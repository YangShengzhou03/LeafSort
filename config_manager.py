import os
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from common import get_resource_path

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器类，负责应用程序配置的加载、保存和管理"""
    
    CONFIG_VERSION = "1.0.0"
    
    def __init__(self, config_file: str = "_internal/leafview_config.json", 
                 cache_file: str = "_internal/cache_location.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
            cache_file: 缓存文件路径
        """
        self.config_file = Path(get_resource_path(config_file))
        self.cache_file = Path(get_resource_path(cache_file))
        self._lock = threading.RLock()
        self.config = self._load_config()
        self.location_cache = self._load_location_cache()
        self._validate_and_migrate_config()
    
    def _thread_safe_method(func):
        """线程安全方法装饰器"""
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，如果不存在则返回默认配置"""
        default_config = self._get_default_config()
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._update_config_with_defaults(config, default_config)
                    return config
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载配置文件失败: {e}")
        
        return default_config
    
    def _update_config_with_defaults(self, config: Dict[str, Any], default_config: Dict[str, Any]):
        """使用默认值更新配置"""
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(config[key], dict):
                self._update_config_with_defaults(config[key], default_config[key])
    
    @_thread_safe_method
    def _validate_and_migrate_config(self):
        """验证和迁移配置"""
        self.config["version"] = self.CONFIG_VERSION
        self.config["last_modified"] = datetime.now().isoformat()
        
        # 清理重复文件夹路径
        seen_paths = set()
        unique_folders = []
        for folder in self.config["folders"]:
            path = folder.get("path")
            if path and path not in seen_paths:
                seen_paths.add(path)
                unique_folders.append(folder)
        
        if len(unique_folders) != len(self.config["folders"]):
            duplicate_count = len(self.config["folders"]) - len(unique_folders)
            self.config["folders"] = unique_folders
            logger.info(f"清理了 {duplicate_count} 个重复文件夹路径")
            self._save_config_no_lock()
    
    def _load_location_cache(self) -> Dict[str, Any]:
        """加载位置缓存文件"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载位置缓存文件失败: {e}")
        
        return {}
    
    def _save_config_no_lock(self) -> bool:
        """无锁保存配置"""
        try:
            self.config["last_modified"] = datetime.now().isoformat()
            self._ensure_directory(self.config_file.parent)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
    
    @_thread_safe_method
    def save_config(self) -> bool:
        """保存配置"""
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def save_location_cache(self) -> bool:
        """保存位置缓存"""
        try:
            self._ensure_directory(self.cache_file.parent)
            
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.location_cache, f, ensure_ascii=False, indent=2)
            return True
        except IOError as e:
            logger.error(f"保存位置缓存文件失败: {e}")
            return False
    
    def _ensure_directory(self, directory: Path):
        """确保目录存在"""
        directory.mkdir(parents=True, exist_ok=True)
    
    @_thread_safe_method
    def add_folder(self, folder_path: str, include_sub: bool = True) -> bool:
        """添加文件夹到配置"""
        folder_path = os.path.normpath(folder_path)
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            logger.warning(f"尝试添加无效文件夹: {folder_path}")
            return False
        
        if any(folder["path"] == folder_path for folder in self.config["folders"]):
            return False
        
        self.config["folders"].append({
            "path": folder_path,
            "include_sub": include_sub,
            "added_time": datetime.now().isoformat()
        })
        
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def add_folders(self, folders: List[Dict[str, Any]]) -> int:
        """批量添加文件夹"""
        added_count = 0
        for folder in folders:
            folder_path = os.path.normpath(folder.get("path", ""))
            include_sub = folder.get("include_sub", True)
            
            if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
                if not any(f["path"] == folder_path for f in self.config["folders"]):
                    self.config["folders"].append({
                        "path": folder_path,
                        "include_sub": include_sub,
                        "added_time": datetime.now().isoformat()
                    })
                    added_count += 1
        
        if added_count > 0:
            self._save_config_no_lock()
        return added_count
    
    @_thread_safe_method
    def remove_folder(self, folder_path: str) -> bool:
        """移除文件夹"""
        folder_path = os.path.normpath(folder_path)
        
        for i, folder in enumerate(self.config["folders"]):
            if folder["path"] == folder_path:
                self.config["folders"].pop(i)
                return self._save_config_no_lock()
        
        return False
    
    @_thread_safe_method
    def update_folder_include_sub(self, folder_path: str, include_sub: bool) -> bool:
        """更新文件夹包含子文件夹设置"""
        folder_path = os.path.normpath(folder_path)
        
        for folder in self.config["folders"]:
            if folder["path"] == folder_path:
                folder["include_sub"] = include_sub
                folder["updated_time"] = datetime.now().isoformat()
                return self._save_config_no_lock()
        
        return False
    
    @_thread_safe_method
    def get_folders(self) -> List[Dict[str, Any]]:
        """获取所有文件夹"""
        return [folder.copy() for folder in self.config["folders"]]
    
    @_thread_safe_method
    def get_valid_folders(self) -> List[Dict[str, Any]]:
        """获取有效文件夹"""
        return [folder.copy() for folder in self.config["folders"] 
                if os.path.exists(folder["path"]) and os.path.isdir(folder["path"])]
    
    @_thread_safe_method
    def clear_invalid_folders(self) -> int:
        """清理无效文件夹"""
        original_count = len(self.config["folders"])
        self.config["folders"] = [folder for folder in self.config["folders"] 
                                  if os.path.exists(folder["path"]) and os.path.isdir(folder["path"])]
        removed_count = original_count - len(self.config["folders"])
        
        if removed_count > 0:
            logger.info(f"清理了 {removed_count} 个无效文件夹")
            self._save_config_no_lock()
        
        return removed_count
    
    @_thread_safe_method
    def cache_location(self, latitude: float, longitude: float, address: str) -> bool:
        """缓存位置信息"""
        cache_key = f"{latitude:.6f},{longitude:.6f}"
        self.location_cache[cache_key] = {
            "address": address,
            "timestamp": datetime.now().timestamp(),
            "last_accessed": datetime.now().timestamp()
        }
        
        max_cache_size = self.config.get("cache_settings", {}).get("max_location_cache_size", 50000)
        if len(self.location_cache) > max_cache_size:
            cache_items = list(self.location_cache.items())
            cache_items.sort(key=lambda x: x[1].get("last_accessed", 0), reverse=True)
            self.location_cache = dict(cache_items[:max(10000, max_cache_size // 2)])
            logger.debug(f"位置缓存已清理，当前大小: {len(self.location_cache)}/{max_cache_size}")
        
        return self.save_location_cache()
    
    @_thread_safe_method
    def get_cached_location(self, latitude: float, longitude: float) -> Optional[str]:
        """获取缓存的位置信息"""
        cache_key = f"{latitude:.6f},{longitude:.6f}"
        cached_data = self.location_cache.get(cache_key)
        
        if cached_data:
            cached_data["last_accessed"] = datetime.now().timestamp()
            return cached_data["address"]
        
        return None
    
    @_thread_safe_method
    def get_cached_location_with_tolerance(self, latitude: float, longitude: float, tolerance: float = 0.01) -> Optional[str]:
        """获取缓存的位置信息（带容差）"""
        exact_match = self._get_cached_location_no_lock(latitude, longitude)
        if exact_match:
            return exact_match
        
        for cache_key, cached_data in self.location_cache.items():
            try:
                cached_lat, cached_lon = map(float, cache_key.split(','))
                distance = ((latitude - cached_lat) ** 2 + (longitude - cached_lon) ** 2) ** 0.5
                if distance <= tolerance:
                    cached_data["last_accessed"] = datetime.now().timestamp()
                    return cached_data["address"]
            except (ValueError, IndexError):
                logger.warning(f"无效的缓存键: {cache_key}")
                continue
        
        return None
    
    def _get_cached_location_no_lock(self, latitude: float, longitude: float) -> Optional[str]:
        """无锁获取缓存位置信息"""
        cache_key = f"{latitude:.6f},{longitude:.6f}"
        cached_data = self.location_cache.get(cache_key)
        
        if cached_data:
            cached_data["last_accessed"] = datetime.now().timestamp()
            return cached_data["address"]
        
        return None
    
    @_thread_safe_method
    def clear_folders(self) -> bool:
        """清空所有文件夹"""
        folder_count = len(self.config["folders"])
        self.config["folders"] = []
        logger.info(f"清空所有文件夹配置，删除了 {folder_count} 个文件夹")
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def update_setting(self, key: str, value: Any) -> bool:
        """更新单个设置"""
        if not self._validate_setting(key, value):
            logger.warning(f"设置验证失败: {key} = {value}")
            return False
        
        self.config["settings"][key] = value
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def update_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """批量更新设置"""
        changes_made = False
        for key, value in settings_dict.items():
            if self._validate_setting(key, value):
                if self.config["settings"].get(key) != value:
                    self.config["settings"][key] = value
                    logger.info(f"批量设置更新: {key} = {value}")
                    changes_made = True
            else:
                logger.warning(f"批量设置验证失败: {key} = {value}")
        
        return self._save_config_no_lock() if changes_made else True
    
    @_thread_safe_method
    def get_setting(self, key: str, default: Any = None) -> Any:
        """获取单个设置"""
        return self.config["settings"].get(key, default)
    
    @_thread_safe_method
    def get_settings(self, keys: List[str] = None) -> Dict[str, Any]:
        """获取多个设置"""
        if keys:
            return {key: self.config["settings"].get(key) for key in keys}
        else:
            default_config = self._get_default_config()
            result = default_config["settings"].copy()
            result.update(self.config["settings"])
            return result
    
    @_thread_safe_method
    def reset_settings(self, keys: List[str] = None) -> bool:
        """重置设置"""
        default_config = self._get_default_config()
        changes_made = False
        
        if keys:
            for key in keys:
                if key in default_config["settings"]:
                    self.config["settings"][key] = default_config["settings"][key]
                    changes_made = True
                    logger.info(f"设置重置: {key} = {default_config['settings'][key]}")
        else:
            self.config["settings"] = default_config["settings"].copy()
            changes_made = True
            logger.info("所有设置已重置为默认值")
        
        return self._save_config_no_lock() if changes_made else True
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """验证设置值"""
        validation_rules = {
            "thumbnail_size": lambda v: isinstance(v, int) and 0 < v <= 2000,
            "max_cache_size": lambda v: isinstance(v, int) and v >= 0,
            "default_view": lambda v: isinstance(v, str) and v in ["grid", "list"],
            "dark_mode": lambda v: isinstance(v, bool),
            "auto_update_metadata": lambda v: isinstance(v, bool),
            "use_gps_cache": lambda v: isinstance(v, bool),
            "map_provider": lambda v: isinstance(v, str) and v in ["gaode", "baidu", "bing", "google"]
        }
        
        if key in validation_rules:
            return validation_rules[key](value)
        
        logger.debug(f"未知设置键: {key}")
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        current_time = datetime.now()
        return {
            "version": self.CONFIG_VERSION,
            "last_modified": current_time.isoformat(),
            "folders": [],
            "settings": {
                "thumbnail_size": 200,
                "max_cache_size": 10000,
                "default_view": "grid",
                "dark_mode": False,
                "auto_update_metadata": True,
                "use_gps_cache": True,
                "map_provider": "gaode",
                "show_thumbnails": True,
                "enable_exif_edit": True,
                "remember_window_size": True,
                "max_threads": 4,
                "memory_limit_mb": 2048,
                "amap_api_key": '0db079da53e08cbb62b52a42f657b994',
                "last_opened_folder": '',
                "window_position": {'x': 100, 'y': 100},
                "window_size": {'width': 942, 'height': 580}
            },
            "api_limits": {
                "gaode": {
                    "daily_calls": 0,
                    "max_daily_calls": 500,
                    "last_reset_date": current_time.strftime("%Y-%m-%d"),
                    "last_call_time": None
                }
            },
            "cache_settings": {
                "max_location_cache_size": 50000,
                "cache_expiry_days": 30
            }
        }
    
    @_thread_safe_method
    def clear_cache(self):
        """清空缓存"""
        self.location_cache.clear()
        save_result = self.save_location_cache()
        
        cache_dir = os.path.join(self.config_file.parent, 'cache')
        if os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"清理缓存目录失败: {e}")
                return False
                
        return save_result


config_manager = ConfigManager()