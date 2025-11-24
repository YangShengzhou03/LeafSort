import os
import json
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from common import get_resource_path


class ConfigManager:
    CONFIG_VERSION = "1.0.0"
    MAX_CACHE_ITEMS = 1000
    CACHE_EXPIRATION_DAYS = 30
    
    def __init__(self, config_file: str = "_internal/leafview_config.json", 
                 cache_file: str = "_internal/cache_location.json"):
        self.config_file = Path(get_resource_path(config_file))
        self.cache_file = Path(get_resource_path(cache_file))
        self._lock = threading.RLock()
        self.config = self._load_config()
        self.location_cache = self._load_location_cache()
        self._validate_and_migrate_config()
        with self._lock:
            self._cleanup_expired_cache()
            self._reduce_cache_size(self.MAX_CACHE_ITEMS)
    
    @staticmethod
    def _thread_safe_method(func):
        def wrapper(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return wrapper
    
    def _load_file(self, file_path: Path, default_value: Any) -> Any:
        try:
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 in {file_path}: {str(e)}")
        except IOError as e:
            print(f"文件读取错误 in {file_path}: {str(e)}")
        except PermissionError as e:
            print(f"没有权限访问 {file_path}: {str(e)}")
        except Exception as e:
            print(f"加载文件时发生未知错误 {file_path}: {str(e)}")
        return default_value
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = self._get_default_config()
        config = self._load_file(self.config_file, default_config)
        
        if config is not default_config:
            self._update_config_with_defaults(config, default_config)
        
        return config
    
    def _update_config_with_defaults(self, config: Dict[str, Any], default_config: Dict[str, Any]):
        for key, default_value in default_config.items():
            if key not in config:
                config[key] = default_value
            elif isinstance(default_value, dict) and isinstance(config[key], dict):
                self._update_config_with_defaults(config[key], default_config[key])
    
    @_thread_safe_method
    def _validate_and_migrate_config(self):
        self.config["version"] = self.CONFIG_VERSION
        self.config["last_modified"] = datetime.now().isoformat()
        
        seen_paths = set()
        unique_folders = []
        for folder in self.config["folders"]:
            path = folder.get("path")
            if path and path not in seen_paths:
                seen_paths.add(path)
                unique_folders.append(folder)
        
        if len(unique_folders) != len(self.config["folders"]):
            self.config["folders"] = unique_folders
            self._save_config_no_lock()
    
    def _load_location_cache(self) -> Dict[str, Any]:
        return self._load_file(self.cache_file, {})
    
    def _save_file_no_lock(self, file_path: Path, data: Any) -> bool:
        try:
            self._ensure_directory(file_path.parent)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except PermissionError as e:
            print(f"没有权限写入 {file_path}: {str(e)}")
        except IOError as e:
            print(f"文件写入错误 {file_path}: {str(e)}")
        except json.JSONDecodeError as e:
            print(f"JSON序列化错误: {str(e)}")
        except Exception as e:
            print(f"保存文件时发生未知错误 {file_path}: {str(e)}")
        return False
    
    def _save_config_no_lock(self) -> bool:
        self.config["last_modified"] = datetime.now().isoformat()
        return self._save_file_no_lock(self.config_file, self.config)
    
    @_thread_safe_method
    def save_config(self) -> bool:
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def save_location_cache(self) -> bool:
        return self._save_file_no_lock(self.cache_file, self.location_cache)
    
    def _ensure_directory(self, directory: Path):
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            print(f"没有权限创建目录 {directory}: {str(e)}")
        except OSError as e:
            print(f"创建目录失败 {directory}: {str(e)}")
    
    @_thread_safe_method
    def add_folder(self, folder_path: str, include_sub: bool = True) -> bool:
        folder_path = os.path.normpath(folder_path)
        
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
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
        folder_path = os.path.normpath(folder_path)
        
        for i, folder in enumerate(self.config["folders"]):
            if folder["path"] == folder_path:
                self.config["folders"].pop(i)
                return self._save_config_no_lock()
        
        return False
    
    @_thread_safe_method
    def update_folder_include_sub(self, folder_path: str, include_sub: bool) -> bool:
        folder_path = os.path.normpath(folder_path)
        
        for folder in self.config["folders"]:
            if folder["path"] == folder_path:
                folder["include_sub"] = include_sub
                folder["updated_time"] = datetime.now().isoformat()
                return self._save_config_no_lock()
        
        return False
    
    @_thread_safe_method
    def get_folders(self) -> List[Dict[str, Any]]:
        return [folder.copy() for folder in self.config["folders"]]
    
    @_thread_safe_method
    def get_valid_folders(self) -> List[Dict[str, Any]]:
        return [folder.copy() for folder in self.config["folders"] 
                if os.path.exists(folder["path"]) and os.path.isdir(folder["path"])]
    
    @_thread_safe_method
    def clear_invalid_folders(self) -> int:
        original_count = len(self.config["folders"])
        self.config["folders"] = [folder for folder in self.config["folders"] 
                                  if os.path.exists(folder["path"]) and os.path.isdir(folder["path"])]
        removed_count = original_count - len(self.config["folders"])
        
        if removed_count > 0:
            self._save_config_no_lock()
        
        return removed_count
    
    @_thread_safe_method
    def cache_location(self, latitude: float, longitude: float, address: str) -> bool:
        try:
            key = self._get_cache_key(latitude, longitude)
            self.location_cache[key] = {
                'address': address,
                'timestamp': datetime.now().isoformat(),
                'last_accessed': datetime.now().isoformat()
            }
            
            self._reduce_cache_size(self.MAX_CACHE_ITEMS)
            return self._save_location_cache_no_lock()
        except TypeError as e:
            print(f"缓存位置数据类型错误: {str(e)}")
        except Exception as e:
            print(f"缓存位置时发生未知错误: {str(e)}")
        return False
        
    def _cleanup_expired_cache(self):
        try:
            from datetime import datetime, timedelta
            expiration_date = datetime.now() - timedelta(days=self.CACHE_EXPIRATION_DAYS)
            expired_keys = []
            
            for key, data in self.location_cache.items():
                if isinstance(data, dict) and 'timestamp' in data:
                    try:
                        cache_time = datetime.fromisoformat(data['timestamp'])
                        if cache_time < expiration_date:
                            expired_keys.append(key)
                    except (ValueError, TypeError):
                        expired_keys.append(key)
                else:
                    expired_keys.append(key)
            
            for key in expired_keys:
                del self.location_cache[key]
            
            if expired_keys:
                self._save_location_cache_no_lock()
        except Exception as e:
            print(f"清理过期缓存时出错: {str(e)}")
    
    def _reduce_cache_size(self, max_size):
        try:
            if len(self.location_cache) <= max_size:
                return
            
            from datetime import datetime
            cache_items = []
            
            for key, data in self.location_cache.items():
                if isinstance(data, dict):
                    timestamp = data.get('last_accessed', data.get('timestamp', None))
                    if timestamp:
                        try:
                            cache_time = datetime.fromisoformat(timestamp)
                            cache_items.append((key, cache_time))
                        except (ValueError, TypeError):
                            cache_items.append((key, datetime.now()))
                    else:
                        cache_items.append((key, datetime.now()))
            
            cache_items.sort(key=lambda x: x[1])
            items_to_remove = len(self.location_cache) - max_size
            
            for i in range(items_to_remove):
                if i < len(cache_items):
                    del self.location_cache[cache_items[i][0]]
            
            if items_to_remove > 0:
                self._save_location_cache_no_lock()
        except Exception as e:
            print(f"限制缓存大小时出错: {str(e)}")
    
    def _get_cache_key(self, latitude: float, longitude: float) -> str:
        return f"{latitude:.6f},{longitude:.6f}"
    
    def _update_cache_access_time(self, cached_data: Dict[str, Any]):
        if isinstance(cached_data, dict):
            cached_data['last_accessed'] = datetime.now().isoformat()
    
    def _get_cached_location_no_lock(self, latitude: float, longitude: float) -> Optional[str]:
        cache_key = self._get_cache_key(latitude, longitude)
        cached_data = self.location_cache.get(cache_key)
        
        if cached_data:
            self._update_cache_access_time(cached_data)
            return cached_data["address"]
        
        return None
    
    @_thread_safe_method
    def get_cached_location(self, latitude: float, longitude: float) -> Optional[str]:
        result = self._get_cached_location_no_lock(latitude, longitude)
        if result:
            key = self._get_cache_key(latitude, longitude)
            if key in self.location_cache:
                self._update_cache_access_time(self.location_cache[key])
                threading.Thread(target=self._save_location_cache_no_lock, daemon=True).start()
        return result
    
    @_thread_safe_method
    def get_cached_location_with_tolerance(self, latitude: float, longitude: float, tolerance: float = 0.01) -> Optional[str]:
        exact_match = self._get_cached_location_no_lock(latitude, longitude)
        if exact_match:
            return exact_match
        
        tolerance_squared = tolerance ** 2
        for cache_key, cached_data in self.location_cache.items():
            try:
                cached_lat, cached_lon = map(float, cache_key.split(','))
                distance_squared = ((latitude - cached_lat) ** 2 + (longitude - cached_lon) ** 2)
                if distance_squared <= tolerance_squared:
                    self._update_cache_access_time(cached_data)
                    return cached_data["address"]
            except (ValueError, IndexError):
                continue
        
        return None
    
    @_thread_safe_method
    def clear_folders(self) -> bool:
        self.config["folders"] = []
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def update_setting(self, key: str, value: Any) -> bool:
        if not self._validate_setting(key, value):
            return False
        
        self.config["settings"][key] = value
        return self._save_config_no_lock()
    
    @_thread_safe_method
    def update_settings(self, settings_dict: Dict[str, Any]) -> bool:
        changes_made = False
        for key, value in settings_dict.items():
            if self._validate_setting(key, value):
                if self.config["settings"].get(key) != value:
                    self.config["settings"][key] = value
                    changes_made = True
        
        return self._save_config_no_lock() if changes_made else True
    
    @_thread_safe_method
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.config["settings"].get(key, default)
    
    @_thread_safe_method
    def get_settings(self, keys: List[str] = None) -> Dict[str, Any]:
        if keys:
            return {key: self.config["settings"].get(key) for key in keys}
        
        return self.config["settings"].copy()
    
    @_thread_safe_method
    def reset_settings(self, keys: List[str] = None) -> bool:
        default_config = self._get_default_config()
        changes_made = False
        
        if keys:
            for key in keys:
                if key in default_config["settings"]:
                    self.config["settings"][key] = default_config["settings"][key]
                    changes_made = True
        else:
            self.config["settings"] = default_config["settings"].copy()
            changes_made = True
        
        return self._save_config_no_lock() if changes_made else True
    
    def _validate_setting(self, key: str, value: Any) -> bool:
        validation_rules = {
            "thumbnail_size": lambda v: isinstance(v, int) and 0 < v <= 2000,
            "max_cache_size": lambda v: isinstance(v, int) and v >= 0,
            "default_view": lambda v: isinstance(v, str) and v in ["grid", "list"],
            "map_provider": lambda v: isinstance(v, str) and v in ["gaode", "baidu", "bing", "google"]
        }
        
        if key in ["dark_mode", "auto_update_metadata", "use_gps_cache", "show_thumbnails", "enable_exif_edit", "remember_window_size"]:
            return isinstance(value, bool)
        
        if key in validation_rules:
            return validation_rules[key](value)
        
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
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
        self.location_cache.clear()
        save_result = self.save_location_cache()
        
        cache_dir = os.path.join(self.config_file.parent, 'cache')
        if os.path.exists(cache_dir):
            import shutil
            try:
                shutil.rmtree(cache_dir)
                os.makedirs(cache_dir, exist_ok=True)
            except Exception:
                return False
                
        return save_result


config_manager = ConfigManager()