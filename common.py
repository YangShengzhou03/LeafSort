import logging
import os

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif', '.heic', '.heif', '.svg', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.sr2', '.raf', '.dng', '.psd', '.rw2', '.pef', '.nrw']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.html', '.htm', '.xml', '.epub', '.md', '.log']
ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.jar']

class ResourceManager:
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

_resource_manager = ResourceManager()

def get_resource_path(relative_path):
    return _resource_manager.get_resource_path(relative_path)

def detect_media_type(file_path):
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

def get_file_type(file_path):
    file_path_str = str(file_path)
    file_ext = os.path.splitext(file_path_str)[1].lower()
    
    if file_ext in IMAGE_EXTENSIONS:
        return '图像'
    elif file_ext in VIDEO_EXTENSIONS:
        return '视频'
    elif file_ext in AUDIO_EXTENSIONS:
        return '音乐'
    elif file_ext in DOCUMENT_EXTENSIONS:
        return '文档'
    elif file_ext in ARCHIVE_EXTENSIONS:
        return '压缩包'
    
    return '其他'