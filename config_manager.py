import os
import json
import threading
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import shutil

logger = logging.getLogger(__name__)

def _thread_safe_method(func):
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return func(self, *args, **kwargs)
    return wrapper

class ConfigManager:
    CONFIG_VERSION = "1.1"
    
    def __init__(self):
        self._lock = threading.RLock()
        self.config_file = self._get_config_file_path()
        self._ensure_config_exists()
        self.config = self._load_file()
        self.location_cache = {}
        self.cache_file = self._get_cache_file_path()
        self._load_location_cache()
        self._validate_and_migrate_config()
    
    def _get_config_file_path(self) -> os.PathLike:
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(app_dir, 'config.json')
    
    def _get_cache_file_path(self) -> os.PathLike:
        app_dir = os.path.dirname(os.path.abspath(__file__))
        internal_dir = os.path.join(app_dir, '_internal')
        os.makedirs(internal_dir, exist_ok=True)
        return os.path.join(internal_dir, 'cache_location.json')
    
    def _ensure_config_exists(self) -> None:
        if not os.path.exists(self.config_file):
            default_config = self._get_default_config()
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"创建默认配置文件失败: {str(e)}")
    
    def _load_file(self) -> Dict[str, Any]:
        if not os.path.exists(self.config_file):
            return self._get_default_config()
        
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return self._get_default_config()
    
    def _save_file_no_lock(self) -> bool:
        self.config["last_modified"] = datetime.now().isoformat()
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
    
    def _validate_and_migrate_config(self) -> None:
        default_config = self._get_default_config()
        
        if "version" not in self.config or self.config["version"] != self.CONFIG_VERSION:
            for key, value in default_config.items():
                if key not in self.config:
                    self.config[key] = value.copy() if isinstance(value, dict) else value
            
            for key, value in default_config["settings"].items():
                if key not in self.config["settings"]:
                    self.config["settings"][key] = value
            
            if "api_limits" not in self.config:
                self.config["api_limits"] = default_config["api_limits"]
            elif "gaode" not in self.config["api_limits"]:
                self.config["api_limits"]["gaode"] = default_config["api_limits"]["gaode"]
            else:
                self.config["api_limits"]["gaode"]["max_daily_calls"] = 300
            
            self.config["version"] = self.CONFIG_VERSION
            self._save_file_no_lock()
    
    @_thread_safe_method
    def add_folder(self, folder_path: str) -> bool:
        if folder_path not in self.config["folders"]:
            self.config["folders"].append(folder_path)
            return self._save_config_no_lock()
        return True
    
    @_thread_safe_method
    def remove_folder(self, folder_path: str) -> bool:
        if folder_path in self.config["folders"]:
            self.config["folders"].remove(folder_path)
            return self._save_config_no_lock()
        return True
    
    @_thread_safe_method
    def get_folders(self) -> List[str]:
        return self.config["folders"].copy()
    
    @_thread_safe_method
    def has_folder(self, folder_path: str) -> bool:
        return folder_path in self.config["folders"]
    
    def _save_config_no_lock(self) -> bool:
        return self._save_file_no_lock()
    
    def _load_location_cache(self) -> None:
        if not os.path.exists(self.cache_file):
            return
        
        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                self.location_cache = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"加载位置缓存失败: {str(e)}")
            self.location_cache = {}
    
    def _save_location_cache_no_lock(self) -> bool:
        self._cleanup_expired_cache()
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.location_cache, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"保存位置缓存失败: {str(e)}")
            return False
    
    @_thread_safe_method
    def save_location_cache(self) -> bool:
        return self._save_location_cache_no_lock()
    
    @_thread_safe_method
    def cache_location(self, latitude: float, longitude: float, address: str) -> bool:
        cache_key = f"{latitude},{longitude}"
        current_time = datetime.now().isoformat()
        
        if len(self.location_cache) >= self.config["cache_settings"]["max_location_cache_size"]:
            self._cleanup_expired_cache()
            
            if len(self.location_cache) >= self.config["cache_settings"]["max_location_cache_size"]:
                oldest_key = min(self.location_cache.keys(), key=lambda k: self.location_cache[k]["last_access"])
                del self.location_cache[oldest_key]
        
        self.location_cache[cache_key] = {
            "address": address,
            "last_access": current_time
        }
        
        return self._save_location_cache_no_lock()
    
    def _cleanup_expired_cache(self) -> None:
        expiry_days = self.config["cache_settings"]["cache_expiry_days"]
        # 如果expiry_days为0，表示永不过期，不执行清理
        if expiry_days <= 0:
            return
            
        current_time = datetime.now()
        
        expired_keys = []
        for key, data in self.location_cache.items():
            try:
                last_access = datetime.fromisoformat(data["last_access"])
                days_since_access = (current_time - last_access).days
                
                if days_since_access > expiry_days:
                    expired_keys.append(key)
            except Exception:
                expired_keys.append(key)
        
        for key in expired_keys:
            if key in self.location_cache:
                del self.location_cache[key]
    
    def _update_cache_access_time(self, cache_data: Dict[str, str]) -> None:
        cache_data["last_access"] = datetime.now().isoformat()
    
    def _get_cache_key(self, latitude: float, longitude: float) -> str:
        return f"{latitude},{longitude}"
    
    def _get_cached_location_no_lock(self, latitude: float, longitude: float) -> Optional[str]:
        cache_key = self._get_cache_key(latitude, longitude)
        if cache_key in self.location_cache:
            return self.location_cache[cache_key]["address"]
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
    def get_cached_location_with_tolerance(self, latitude: float, longitude: float, tolerance: float = 0.02) -> Optional[str]:
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
                    threading.Thread(target=self._save_location_cache_no_lock, daemon=True).start()
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
                "window_size": {'width': 942, 'height': 580},
                "location_cache_tolerance": 0.027
            },
            "api_limits": {
                "gaode": {
                    "daily_calls": 0,
                    "max_daily_calls": 100,
                    "last_reset_date": current_time.strftime("%Y-%m-%d"),
                    "last_call_time": None
                }
            },
            "cache_settings": {
                "max_location_cache_size": 500000,
                "cache_expiry_days": 0
            }
        }
    
    @_thread_safe_method
    def _check_and_reset_daily_limit(self) -> None:
        current_date = datetime.now().strftime("%Y-%m-%d")
        if self.config["api_limits"]["gaode"]["last_reset_date"] != current_date:
            self.config["api_limits"]["gaode"]["daily_calls"] = 0
            self.config["api_limits"]["gaode"]["last_reset_date"] = current_date
            self._save_config_no_lock()
    
    @_thread_safe_method
    def can_make_api_call(self) -> bool:
        self._check_and_reset_daily_limit()
        current_calls = self.config["api_limits"]["gaode"]["daily_calls"]
        max_calls = self.config["api_limits"]["gaode"]["max_daily_calls"]
        return current_calls < max_calls
    
    @_thread_safe_method
    def increment_api_call(self) -> None:
        self._check_and_reset_daily_limit()
        self.config["api_limits"]["gaode"]["daily_calls"] += 1
        self.config["api_limits"]["gaode"]["last_call_time"] = datetime.now().isoformat()
        self._save_config_no_lock()
    
    @_thread_safe_method
    def get_remaining_daily_calls(self) -> int:
        self._check_and_reset_daily_limit()
        current_calls = self.config["api_limits"]["gaode"]["daily_calls"]
        max_calls = self.config["api_limits"]["gaode"]["max_daily_calls"]
        return max_calls - current_calls
    
    @_thread_safe_method
    def clear_cache(self):
        self.location_cache.clear()
        save_result = self.save_location_cache()
        
        if os.path.exists(self.cache_file):
            try:
                os.remove(self.cache_file)
            except Exception as e:
                logger.error(f"清理缓存文件时出错: {str(e)}")
                return False
                
        return save_result

config_manager = ConfigManager()
