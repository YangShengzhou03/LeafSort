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
    
    CONFIG_VERSION = "1.0.0"
    
    def __init__(self, config_file: str = "_internal/leafview_config.json", 
                 cache_file: str = "_internal/cache_location.json"):
        """初始化配置管理器"""
        self.config_file = Path(get_resource_path(config_file))
        self.cache_file = Path(get_resource_path(cache_file))
        self._lock = threading.RLock()
        self.config = self._load_config()
        self.location_cache = self._load_location_cache()
        self._validate_and_migrate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "version": self.CONFIG_VERSION,
            "folders": [],
            "api_limits": {
                "gaode": {
                    "daily_calls": 0,
                    "last_reset_date": "",
                    "max_daily_calls": 500
                }
            },
            "settings": {},
            "last_modified": datetime.now().isoformat()
        }
        
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 确保所有必需的键存在
                    for key in default_config:
                        if key not in config:
                            config[key] = default_config[key]
                        elif key == "api_limits":

                            for api_name, api_defaults in default_config["api_limits"].items():
                                if api_name not in config["api_limits"]:
                                    config["api_limits"][api_name] = api_defaults
                                else:
                                    for field, default_value in api_defaults.items():
                                        if field not in config["api_limits"][api_name]:
                                            config["api_limits"][api_name][field] = default_value
                    return config
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载配置文件时出错了: {e}")
        
        return default_config
    
    def _validate_and_migrate_config(self):
        """验证配置并进行必要的迁移"""
        with self._lock:
            self.config["version"] = self.CONFIG_VERSION
            
            if "last_modified" not in self.config:
                self.config["last_modified"] = datetime.now().isoformat()
            
            seen_paths = set()
            unique_folders = []
            for folder in self.config["folders"]:
                if folder.get("path") not in seen_paths:
                    seen_paths.add(folder.get("path"))
                    unique_folders.append(folder)
            
            if len(unique_folders) != len(self.config["folders"]):
                self.config["folders"] = unique_folders
                logger.info(f"已清理 {len(seen_paths) - len(unique_folders)} 个重复的文件夹路径")
                self.save_config()
    
    def _load_location_cache(self) -> Dict[str, Any]:
        """加载位置缓存文件"""
        default_cache = {}
        
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.warning(f"加载位置缓存文件时出错了: {e}")
        
        return default_cache
    
    def save_config(self) -> bool:
        """保存配置到文件"""
        with self._lock:
            try:
                self.config["last_modified"] = datetime.now().isoformat()
                
                self.config_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.config, f, ensure_ascii=False, indent=2)
                return True
            except IOError as e:
                logger.error(f"保存配置文件时出错了: {e}")
                return False
    
    def save_location_cache(self) -> bool:
        with self._lock:
            try:
                self.cache_file.parent.mkdir(parents=True, exist_ok=True)
                
                with open(self.cache_file, 'w', encoding='utf-8') as f:
                    json.dump(self.location_cache, f, ensure_ascii=False, indent=2)
                return True
            except IOError as e:
                logger.error(f"保存位置缓存文件时出错了: {e}")
                return False
    
    def add_folder(self, folder_path: str, include_sub: bool = True) -> bool:
        with self._lock:
            folder_path = os.path.normpath(folder_path)
            
            if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                logger.warning(f"尝试添加无效文件夹: {folder_path}")
                return False
            
            for folder in self.config["folders"]:
                if folder["path"] == folder_path:
                    return False
            
            self.config["folders"].append({
                "path": folder_path,
                "include_sub": include_sub,
                "added_time": datetime.now().isoformat()
            })
            
            return self.save_config()
    
    def add_folders(self, folders: List[Dict[str, Any]]) -> int:
        """批量添加文件夹，返回成功添加的数量"""
        with self._lock:
            added_count = 0
            for folder in folders:
                folder_path = os.path.normpath(folder.get("path", ""))
                include_sub = folder.get("include_sub", True)
                
                if folder_path and self.add_folder(folder_path, include_sub):
                    added_count += 1
            return added_count
    
    def remove_folder(self, folder_path: str) -> bool:
        with self._lock:
            folder_path = os.path.normpath(folder_path)
            
            for i, folder in enumerate(self.config["folders"]):
                if folder["path"] == folder_path:
                    self.config["folders"].pop(i)
                    return self.save_config()
            
            return False
    
    def update_folder_include_sub(self, folder_path: str, include_sub: bool) -> bool:
        with self._lock:
            folder_path = os.path.normpath(folder_path)
            
            for folder in self.config["folders"]:
                if folder["path"] == folder_path:
                    folder["include_sub"] = include_sub
                    folder["updated_time"] = datetime.now().isoformat()
                    return self.save_config()
            
            return False
    
    def get_folders(self) -> List[Dict[str, Any]]:
        with self._lock:
            # 返回副本以避免外部修改
            return self.config["folders"].copy()
    
    def get_valid_folders(self) -> List[Dict[str, Any]]:
        with self._lock:
            valid_folders = []
            for folder in self.config["folders"]:
                if os.path.exists(folder["path"]) and os.path.isdir(folder["path"]):
                    valid_folders.append(folder.copy())
            return valid_folders
    
    def clear_invalid_folders(self) -> int:
        with self._lock:
            original_count = len(self.config["folders"])
            valid_folders = []
            for folder in self.config["folders"]:
                if os.path.exists(folder["path"]) and os.path.isdir(folder["path"]):
                    valid_folders.append(folder)
            self.config["folders"] = valid_folders
            removed_count = original_count - len(self.config["folders"])
            
            if removed_count > 0:
                logger.info(f"已移除 {removed_count} 个无效文件夹")
                self.save_config()
            
            return removed_count
    
    def cache_location(self, latitude: float, longitude: float, address: str) -> bool:
        with self._lock:
            cache_key = f"{latitude:.6f},{longitude:.6f}"
            self.location_cache[cache_key] = {
                "address": address,
                "timestamp": datetime.now().timestamp(),
                "last_accessed": datetime.now().timestamp()
            }
            
            # 使用配置中的缓存大小限制
            max_cache_size = self.config.get("cache_settings", {}).get("max_location_cache_size", 50000)
            if len(self.location_cache) > max_cache_size:
                cache_items = list(self.location_cache.items())
                cache_items.sort(key=lambda x: x[1].get("last_accessed", 0), reverse=True)
                self.location_cache = dict(cache_items[:max(10000, max_cache_size // 2)])
                logger.debug(f"位置缓存已清理，当前大小: {len(self.location_cache)}/{max_cache_size}")
            
            return self.save_location_cache()
    
    def get_cached_location(self, latitude: float, longitude: float) -> Optional[str]:
        with self._lock:
            cache_key = f"{latitude:.6f},{longitude:.6f}"
            cached_data = self.location_cache.get(cache_key)
            
            if cached_data:
                # 更新最后访问时间
                cached_data["last_accessed"] = datetime.now().timestamp()
                return cached_data["address"]
            
            return None
    
    def get_cached_location_with_tolerance(self, latitude: float, longitude: float, tolerance: float = 0.01) -> Optional[str]:
        with self._lock:
            exact_match = self.get_cached_location(latitude, longitude)
            if exact_match:
                return exact_match
            
            for cache_key, cached_data in self.location_cache.items():
                try:
                    cached_lat, cached_lon = map(float, cache_key.split(','))
                    distance = ((latitude - cached_lat) ** 2 + (longitude - cached_lon) ** 2) ** 0.5
                    if distance <= tolerance:
                        # 更新最后访问时间
                        cached_data["last_accessed"] = datetime.now().timestamp()
                        return cached_data["address"]
                except (ValueError, IndexError):
                    logger.warning(f"无效的缓存键: {cache_key}")
                    continue
            
            return None
    

    

    
    def clear_folders(self) -> bool:
        with self._lock:
            folder_count = len(self.config["folders"])
            self.config["folders"] = []
            logger.info(f"已清空所有文件夹配置，共删除 {folder_count} 个文件夹")
            return self.save_config()
    

    
    def update_setting(self, key: str, value: Any) -> bool:
        with self._lock:
            # 验证设置值
            if not self._validate_setting(key, value):
                logger.warning(f"设置验证失败: {key} = {value}")
                return False
            
            self.config["settings"][key] = value
            return self.save_config()
    
    def update_settings(self, settings_dict: Dict[str, Any]) -> bool:
        """批量更新设置"""
        with self._lock:
            changes_made = False
            for key, value in settings_dict.items():
                if self._validate_setting(key, value):
                    if self.config["settings"].get(key) != value:
                        self.config["settings"][key] = value
                        logger.info(f"批量设置更新: {key} = {value}")
                        changes_made = True
                else:
                    logger.warning(f"批量设置验证失败: {key} = {value}")
            
            if changes_made:
                return self.save_config()
            return True
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        with self._lock:
            return self.config["settings"].get(key, default)
    
    def get_settings(self, keys: List[str] = None) -> Dict[str, Any]:
        """获取多个设置值"""
        with self._lock:
            if keys:
                # 只返回指定的设置
                return {key: self.config["settings"].get(key) for key in keys}
            else:
                # 返回所有设置的副本（确保包含默认值）
                result = {}
                # 先添加默认设置
                default_config = self._get_default_config()
                result.update(default_config["settings"])
                # 然后更新为当前设置
                result.update(self.config["settings"])
                return result
    
    def reset_settings(self, keys: List[str] = None) -> bool:
        """重置设置到默认值"""
        with self._lock:
            default_config = self._get_default_config()
            changes_made = False
            
            if keys:
                # 重置指定的设置
                for key in keys:
                    if key in default_config["settings"]:
                        self.config["settings"][key] = default_config["settings"][key]
                        changes_made = True
                        logger.info(f"设置已重置: {key} = {default_config['settings'][key]}")
            else:
                # 重置所有设置
                self.config["settings"] = default_config["settings"].copy()
                changes_made = True
                logger.info("所有设置已重置为默认值")
            
            if changes_made:
                return self.save_config()
            return True
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        """验证设置值是否有效"""
        # 类型验证规则
        validation_rules = {
            "thumbnail_size": lambda v: isinstance(v, int) and v > 0 and v <= 2000,
            "max_cache_size": lambda v: isinstance(v, int) and v >= 0,
            "default_view": lambda v: isinstance(v, str) and v in ["grid", "list"],
            "dark_mode": lambda v: isinstance(v, bool),
            "auto_update_metadata": lambda v: isinstance(v, bool),
            "use_gps_cache": lambda v: isinstance(v, bool),
            "map_provider": lambda v: isinstance(v, str) and v in ["gaode", "baidu", "bing", "google"]
        }
        
        if key in validation_rules:
            return validation_rules[key](value)
        
        # 默认允许任何值，但记录未知设置
        logger.debug(f"未知设置键: {key}")
        return True
    

    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置，用于初始化或重置"""
        return {
            "version": self.CONFIG_VERSION,
            "last_modified": datetime.now().isoformat(),
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
                    "last_reset_date": datetime.now().strftime("%Y-%m-%d"),
                    "last_call_time": None
                }
            },
            "cache_settings": {
                "max_location_cache_size": 50000,
                "cache_expiry_days": 30
            }
        }


        
    def clear_cache(self):
        """清除缓存数据"""
        # 清除位置缓存
        self.location_cache.clear()
        self.save_location_cache()  # 修正：应该保存位置缓存而不是配置
        
        # 清除临时文件（如果有）
        cache_dir = os.path.join(self.config_file.parent, 'cache')
        if os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            except Exception as e:
                logger.error(f"清除缓存目录时出错: {e}")
                return False
            
        return True



config_manager = ConfigManager()
