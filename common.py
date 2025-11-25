import os
import re
import logging
from PyQt6.QtCore import QUrl, QStandardPaths
from PyQt6.QtWidgets import QMessageBox
import json
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.heic', '.heif', '.svg']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']

class ResourceManager:
    def __init__(self):
        pass
    
    @staticmethod
    def get_resource_path(relative_path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_path, relative_path)
        if os.path.exists(path):
            return path
        
        path = os.path.join(os.getcwd(), relative_path)
        if os.path.exists(path):
            return path
        
        try:
            base_path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(base_path, relative_path)
            if os.path.exists(path):
                return path
        except Exception as e:
            logger.error(f"获取资源路径时出错: {str(e)}")
        
        return None

class MediaTypeDetector:
    def __init__(self):
        pass
    
    @staticmethod
    def is_image(file_path):
        if not file_path:
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in IMAGE_EXTENSIONS
    
    @staticmethod
    def is_video(file_path):
        if not file_path:
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in VIDEO_EXTENSIONS
    
    @staticmethod
    def is_audio(file_path):
        if not file_path:
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in AUDIO_EXTENSIONS
    
    @staticmethod
    def is_media(file_path):
        if not file_path:
            return False
        
        _, ext = os.path.splitext(file_path.lower())
        return ext in IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + AUDIO_EXTENSIONS
    
    def detect_media_type(self, file_path):
        if not os.path.isfile(file_path):
            return {"valid": False, "type": None}
        
        _, ext = os.path.splitext(file_path.lower())
        
        if ext in IMAGE_EXTENSIONS:
            return {"valid": True, "type": "image"}
        elif ext in VIDEO_EXTENSIONS:
            return {"valid": True, "type": "video"}
        elif ext in AUDIO_EXTENSIONS:
            return {"valid": True, "type": "audio"}
        else:
            return {"valid": False, "type": None}

class GeocodingService:
    def __init__(self):
        self.cache_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "geocode_cache.json")
        self.cache = self._load_cache()
        self.api_key = "e7df358a84f7d1879443f48a33e65b87"
        self.api_url = "https://restapi.amap.com/v3/geocode/regeo"
    
    def _load_cache(self):
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"加载地理编码缓存时出错: {str(e)}")
        return {"data": {}, "timestamp": datetime.now().isoformat()}
    
    def _save_cache(self):
        try:
            self.cache["timestamp"] = datetime.now().isoformat()
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存地理编码缓存时出错: {str(e)}")
    
    def _clean_cache(self):
        try:
            cache_time = datetime.fromisoformat(self.cache.get("timestamp", datetime.now().isoformat()))
            if (datetime.now() - cache_time).days > 7:
                self.cache = {"data": {}, "timestamp": datetime.now().isoformat()}
                self._save_cache()
        except Exception as e:
            logger.error(f"清理地理编码缓存时出错: {str(e)}")
    
    def get_address(self, longitude, latitude):
        try:
            cache_key = f"{longitude},{latitude}"
            
            self._clean_cache()
            if cache_key in self.cache["data"]:
                return self.cache["data"][cache_key]
            
            params = {
                "key": self.api_key,
                "location": f"{longitude},{latitude}",
                "extensions": "base",
                "batch": "false"
            }
            
            response = requests.get(self.api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "1":
                    formatted_address = data.get("regeocode", {}).get("formatted_address", "")
                    if formatted_address:
                        self.cache["data"][cache_key] = formatted_address
                        self._save_cache()
                        return formatted_address
            
        except Exception as e:
            logger.error(f"获取地址信息时出错: {str(e)}")
        
        return ""

_resource_manager = ResourceManager()
_media_detector = MediaTypeDetector()

# 工具函数
def get_resource_path(relative_path):
    return _resource_manager.get_resource_path(relative_path)

def detect_media_type(file_path):
    return _media_detector.detect_media_type(file_path)

def is_media_file(file_path):
    return MediaTypeDetector.is_media(file_path)

def get_address_from_coordinates(longitude, latitude):
    service = GeocodingService()
    return service.get_address(longitude, latitude)

def get_common_app_data_path():
    if os.name == 'nt':
        app_data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming')
        return os.path.join(app_data_path, 'LeafView')
    elif os.name == 'posix':
        config_path = os.path.join(os.path.expanduser('~'), '.config')
        return os.path.join(config_path, 'leafview')
    else:
        app_support_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support')
        return os.path.join(app_support_path, 'LeafView')

def get_file_type(file_path):
    file_path_str = str(file_path)
    file_ext = os.path.splitext(file_path_str)[1].lower()
    
    file_type_mapping = {
        '图像': ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.bmp', '.gif', '.svg',
                 '.cr2', '.cr3', '.nef', '.arw', '.orf', '.sr2', '.raf', '.dng',
                 '.tiff', '.tif', '.psd', '.rw2', '.pef', '.nrw'),
        '视频': ('.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.webm'),
        '音乐': ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a'),
        '文档': ('.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx',
                 '.csv', '.html', '.htm', '.xml', '.epub', '.md', '.log'),
        '压缩包': ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.jar')
    }
    
    for file_type, extensions in file_type_mapping.items():
        if file_ext in extensions:
            return file_type
    
    if os.path.isfile(file_path_str):
        try:
            result = detect_media_type(file_path_str)
            if result.get('valid', False):
                media_type = result.get('type')
                mime_to_category = {
                    'image': '图像',
                    'video': '视频',
                    'audio': '音乐'
                }
                if media_type in mime_to_category:
                    return mime_to_category[media_type]
        except (FileNotFoundError, IOError):
            pass
    
    return '其他'
