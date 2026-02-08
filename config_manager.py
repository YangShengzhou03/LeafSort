import json
import logging
import os
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional

def get_app_data_path():
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        app_data_path = os.path.join(local_app_data, 'LeafSort')
        os.makedirs(app_data_path, exist_ok=True)
        return app_data_path
    
    return os.path.dirname(os.path.abspath(__file__))

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
        self.app_data_path = get_app_data_path()
        self.internal_dir = os.path.join(self.app_data_path, '_internal')
        os.makedirs(self.internal_dir, exist_ok=True)
        
        self.config_file = os.path.join(self.internal_dir, 'config.json')
        self._ensure_config_exists()
        self.config = self._load_file()
        self._validate_and_migrate_config()
    
    def _ensure_config_exists(self) -> None:

        os.makedirs(self.internal_dir, exist_ok=True)
        

        if not os.path.exists(self.config_file):
            default_config = self._get_default_config()
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=4, ensure_ascii=False)
                logger.info(f"创建默认配置文件: {self.config_file}")
            except Exception as e:
                logger.error(f"创建默认配置文件失败: {str(e)}")
    
    def _load_file(self) -> Dict[str, Any]:
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
            
            self.config["version"] = self.CONFIG_VERSION
            self._save_file_no_lock()
    
    @_thread_safe_method
    def add_folder(self, folder_path: str) -> bool:
        if folder_path not in self.config["folders"]:
            self.config["folders"].append(folder_path)
            return self._save_file_no_lock()
        return True
    
    @_thread_safe_method
    def remove_folder(self, folder_path: str) -> bool:
        if folder_path in self.config["folders"]:
            self.config["folders"].remove(folder_path)
            return self._save_file_no_lock()
        return True
    
    @_thread_safe_method
    def get_folders(self) -> List[str]:
        return self.config["folders"].copy()
    
    @_thread_safe_method
    def has_folder(self, folder_path: str) -> bool:
        return folder_path in self.config["folders"]

    @_thread_safe_method
    def clear_folders(self) -> bool:
        self.config["folders"] = []
        return self._save_file_no_lock()
    
    @_thread_safe_method
    def update_setting(self, key: str, value: Any) -> bool:
        if not self._validate_setting(key, value):
            return False
        
        self.config["settings"][key] = value
        return self._save_file_no_lock()
    
    
    @_thread_safe_method
    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.config["settings"].get(key, default)
    
    @_thread_safe_method
    def get_settings(self, keys: List[str] = None) -> Dict[str, Any]:
        if keys:
            return {key: self.config["settings"].get(key) for key in keys}
        
        return self.config["settings"].copy()

    @_thread_safe_method
    def _validate_setting(self, key: str, value: Any) -> bool:
        if key in ["source_folder", "target_folder"]:
            return isinstance(value, str)
        
        return True
    
    def _get_default_config(self) -> Dict[str, Any]:
        current_time = datetime.now()
        return {
            "version": self.CONFIG_VERSION,
            "last_modified": current_time.isoformat(),
            "folders": [],
            "settings": {
                "source_folder": '',
                "target_folder": ''
            }
        }

config_manager = ConfigManager()