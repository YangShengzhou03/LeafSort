import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif', '.heic', '.heif', '.svg', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.sr2', '.raf', '.dng', '.psd', '.rw2', '.pef', '.nrw']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']

class ResourceManager:
    def __init__(self):
        pass
    
    @staticmethod
    def get_resource_path(relative_path):
        base_path = os.path.dirname(os.path.abspath(__file__))
        
        if relative_path.startswith('_internal/resources/'):
            resource_path = relative_path.replace('_internal/', '', 1)
            path = os.path.join(base_path, resource_path)
            if os.path.exists(path):
                return path
            
            path = os.path.join(os.getcwd(), resource_path)
            if os.path.exists(path):
                return path
        else:
            path = os.path.join(base_path, relative_path)
            if os.path.exists(path):
                return path
            
            path = os.path.join(os.getcwd(), relative_path)
            if os.path.exists(path):
                return path
        
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

_resource_manager = ResourceManager()
_media_detector = MediaTypeDetector()

def get_resource_path(relative_path):
    return _resource_manager.get_resource_path(relative_path)

def detect_media_type(file_path):
    return _media_detector.detect_media_type(file_path)

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