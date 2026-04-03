import logging
import os
import sys
from datetime import datetime
from typing import Dict, Optional

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.tif', '.heic', '.heif', '.svg', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.sr2', '.raf', '.dng', '.psd', '.rw2', '.pef', '.nrw']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']
DOCUMENT_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', '.ppt', '.pptx', '.csv', '.html', '.htm', '.xml', '.epub', '.md', '.log']
ARCHIVE_EXTENSIONS = ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso', '.jar']

RAW_EXTENSIONS = ['.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf', '.sr2', '.rw2', '.pef', '.nrw']

EXIF_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']
EXIF_VIDEO_EXTENSIONS = ['.mov', '.mp4', '.avi', '.mkv']

LOG_COLOR_MAP: Dict[str, str] = {
    'ERROR': '#FF0000',
    'WARNING': '#FFA500',
    'INFO': '#8677FD',
    'DEBUG': '#006400'
}

def get_current_time_str() -> str:
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def format_log_html(level: str, message: str) -> str:
    color = LOG_COLOR_MAP.get(level, '#006400')
    return f'<div style="margin: 2px 0; padding: 2px 4px; border-left: 3px solid {color};"><span style="color:{color};">{message}</span></div>'

class ResourceManager:
    @staticmethod
    def get_resource_path(relative_path: str) -> Optional[str]:
        if relative_path.startswith('_internal/resources/'):
            relative_path = relative_path.replace('_internal/resources/', 'resources/', 1)
        
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            internal_dir = os.path.join(exe_dir, '_internal')
            
            path = os.path.join(internal_dir, relative_path)
            if os.path.exists(path):
                return path
            
            path = os.path.join(exe_dir, relative_path)
            if os.path.exists(path):
                return path
            
            if hasattr(sys, '_MEIPASS'):
                path = os.path.join(sys._MEIPASS, relative_path)
                if os.path.exists(path):
                    return path
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
            path = os.path.join(base_path, relative_path)
            if os.path.exists(path):
                return path
            
            path = os.path.join(os.getcwd(), relative_path)
            if os.path.exists(path):
                return path
        
        return None

_resource_manager = ResourceManager()

def get_resource_path(relative_path: str) -> Optional[str]:
    return _resource_manager.get_resource_path(relative_path)

def get_file_type(file_path: str) -> str:
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