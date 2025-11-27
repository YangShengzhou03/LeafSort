import json
import logging
import os
from typing import Dict, Tuple, Optional

import requests
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp', '.tiff', '.heic', '.heif', '.svg']
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv', '.webm', '.m4v', '.3gp']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a']

MAGIC_NUMBERS = {
    # JPG相关魔数
    b'\xff\xd8\xff': ('.jpg', '图像'),
    # PNG相关魔数
    b'\x89\x50\x4E\x47': ('.png', '图像'),
    # GIF相关魔数
    b'GIF8': ('.gif', '图像'),
    b'GIF9': ('.gif', '图像'),
    # BMP相关魔数
    b'BM': ('.bmp', '图像'),
    b'\x42\x4D': ('.bmp', '图像'),
    # 视频相关魔数
    b'RIFF': ('.avi', '视频'),
    b'ftyp': ('.mp4', '视频'),
    b'\x00\x00\x00\x1Cftyp': ('.mp4', '视频'),
    b'\x00\x00\x00\x20ftyp': ('.mp4', '视频'),
    b'\x1A\x45\xDF\xA3': ('.mkv', '视频'),
    b'\x4F\x67\x67\x53': ('.ogv', '视频'),
    # 其他图像格式
    b'WEBP': ('.webp', '图像'),
    b'II*': ('.tiff', '图像'),
    b'MM*': ('.tiff', '图像'),
    # HEIC/HEIF相关魔数 - 这些需要更高的优先级，因为'ftyp'可能匹配到其他文件类型
    b'ftypheic': ('.heic', '图像'),
    b'ftypheix': ('.heic', '图像'),
    b'ftypmif1': ('.heif', '图像'),
    b'ftypmsf1': ('.heif', '图像'),
    # 文档和其他格式
    b'%PDF': ('.pdf', '文档'),
    b'PK\x03\x04': ('.zip', '压缩包'),
    b'Rar!': ('.rar', '压缩包'),
    b'7z\xBC\xAF\x27\x1C': ('.7z', '压缩包'),
    # 音频相关魔数
    b'ID3': ('.mp3', '音乐'),
    b'\x52\x49\x46\x46': ('.wav', '音乐'),
    # SVG相关魔数
    b'<svg': ('.svg', '图像'),
    b'<\?xml': ('.svg', '图像'),
}

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

class FileMagicNumberDetector:
    def __init__(self):
        self.magic_numbers = MAGIC_NUMBERS
    
    def get_file_magic_info(self, file_path: str) -> Optional[Dict[str, str]]:
        try:
            if not os.path.isfile(file_path):
                return None
            
            with open(file_path, 'rb') as f:
                header = f.read(12)
            
            for magic, (ext, file_type) in self.magic_numbers.items():
                if header.startswith(magic):
                    return {
                        'extension': ext,
                        'file_type': file_type,
                        'detected': True
                    }
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text_header = f.read(100).lower()
                    if '<svg' in text_header or '<?xml' in text_header and 'svg' in text_header:
                        return {
                            'extension': '.svg',
                            'file_type': '图像',
                            'detected': True
                        }
            except UnicodeDecodeError:
                pass
            
            return {
                'extension': '',
                'file_type': '未知',
                'detected': False
            }
            
        except Exception as e:
            logger.error(f"检测文件魔数时出错: {str(e)}")
            return None
    
    def verify_file_extension(self, file_path) -> Tuple[bool, Optional[Dict[str, str]]]:
        file_path_str = str(file_path)
        magic_info = self.get_file_magic_info(file_path_str)
        
        if not magic_info or not magic_info['detected']:
            return True, magic_info
        
        _, actual_ext = os.path.splitext(file_path_str.lower())
        expected_ext = magic_info['extension']
        
        # 更宽松的HEIC/HEIF检测，允许实际为JPG的文件使用HEIC扩展名
        if actual_ext in ['.heic', '.heif']:
            # 如果检测为JPG但扩展名为HEIC，也视为有效
            if expected_ext == '.jpg':
                logger.info(f"文件 {os.path.basename(file_path_str)} 扩展名为{actual_ext}但实为JPG，允许使用当前扩展名")
                return True, magic_info
            # HEIC/HEIF之间相互兼容
            return True, magic_info
        
        return actual_ext == expected_ext, magic_info

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
        self.cache_path = os.path.join("_internal", "cache_location.json")
        self.cache = self._load_cache()
        self._ensure_internal_dir()

    def _ensure_internal_dir(self):
        internal_dir = "_internal"
        if not os.path.exists(internal_dir):
            os.makedirs(internal_dir)

    def _load_cache(self):
        try:
            if not os.path.exists(self.cache_path):
                return {}

            if os.path.getsize(self.cache_path) == 0:
                logger.warning(f"缓存文件 {self.cache_path} 为空，删除并重新创建")
                os.remove(self.cache_path)
                return {}

            with open(self.cache_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    logger.warning(f"缓存文件 {self.cache_path} 内容为空，删除并重新创建")
                    os.remove(self.cache_path)
                    return {}

                try:
                    return json.loads(content)
                except json.JSONDecodeError as e:
                    logger.error(f"解析缓存文件失败: {str(e)}，删除损坏的缓存文件")
                    os.remove(self.cache_path)
                    return {}
        except Exception as e:
            logger.error(f"加载缓存时出错: {str(e)}")
            if os.path.exists(self.cache_path):
                try:
                    os.remove(self.cache_path)
                    logger.info(f"已删除损坏的缓存文件: {self.cache_path}")
                except Exception:
                    pass
            return {}

    def _save_cache(self):
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存缓存时出错: {str(e)}")

    def _get_address_from_api(self, latitude, longitude):
        logger.info(f"longitude: {longitude}, latitude: {latitude}")
        headers = {'accept': '*/*', 'accept-language': 'zh-CN,zh;q=0.9',
                   'referer': 'https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding',
                   'user-agent': 'Mozilla/5.0'}
        loc = f"{longitude},{latitude}"
        url_tpl = 'https://developer.amap.com/AMapService/v3/geocode/regeo?key={key}&s=rsv3&language=zh_cn&location={loc}&radius=1000&callback=jsonp_765657_&platform=JS&logversion=2.0&appname=https%3A%2F%2Fdeveloper.amap.com%2Fdemo%2Fjavascript-api%2Fexample%2Fgeocoder%2Fregeocoding&csid=123456&sdkversion=1.4.27'

        def get_cookies_key():
            internal_dir = "_internal"
            cookies_path = os.path.join(internal_dir, "cookies.json")

            # 确保_internal目录存在
            if not os.path.exists(internal_dir):
                os.makedirs(internal_dir)

            if os.path.exists(cookies_path):
                try:
                    with open(cookies_path, "r", encoding="utf-8") as f:
                        saved = json.load(f)
                        if saved.get("cookies") and saved.get("key"):
                            return saved["cookies"], saved["key"]
                except Exception as e:
                    print(f"读取cookies失败: {e}")

            target_keys = ['cna', 'passport_login', 'xlly_s', 'HMACCOUNT',
                           'Hm_lvt_c8ac07c199b1c09a848aaab761f9f909', 'Hm_lpvt_c8ac07c199b1c09a848aaab761f9f909',
                           'tfstk']
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_context().new_page()
                page.goto("https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding")
                page.wait_for_timeout(3000)
                cookies = {c['name']: c['value'] for c in page.context.cookies() if c['name'] in target_keys}
                key = page.get_attribute("#code_origin", "data-jskey")
                browser.close()

            with open(cookies_path, "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies, "key": key}, f, ensure_ascii=False)
            return cookies, key

        def get_address(cookies, key):
            if not cookies or not key:
                return None
            try:
                url = url_tpl.format(key=key, loc=loc)
                resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
                if resp.status_code == 200 and "formatted_address" in resp.text:
                    json_str = resp.text[resp.text.index('(') + 1:resp.text.rindex(')')]
                    return json.loads(json_str).get("regeocode", {}).get("formatted_address", "")
            except Exception as e:
                print(f"请求失败: {e}")
            return None

        cookies, key = get_cookies_key()
        addr = get_address(cookies, key)
        if not addr:
            cookies, key = get_cookies_key()
            addr = get_address(cookies, key)

        return addr or "获取失败"

    def get_address(self, longitude, latitude):
        cache_key = f"{longitude},{latitude}"

        if cache_key in self.cache:
            cached_address = self.cache[cache_key]
            logger.info(f"从缓存获取地址: {cached_address}")
            return cached_address

        logger.info(f"缓存未命中，从API获取地址: {longitude}, {latitude}")
        address = self._get_address_from_api(longitude, latitude)

        if address and address != "获取失败":
            self.cache[cache_key] = address
            self._save_cache()
            logger.info(f"已缓存地址: {address}")

        return address

_resource_manager = ResourceManager()
_media_detector = MediaTypeDetector()
_file_magic_detector = FileMagicNumberDetector()

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

def get_file_magic_info(file_path):
    return _file_magic_detector.get_file_magic_info(file_path)

def verify_file_extension(file_path):
    return _file_magic_detector.verify_file_extension(file_path)

def get_file_type(file_path):
    file_path_str = str(file_path)
    
    magic_info = get_file_magic_info(file_path_str)
    if magic_info and magic_info.get('detected', False):
        return magic_info.get('file_type', '其他')
    
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