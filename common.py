import json
import os
import sys
import time
import threading
from pathlib import Path
import logging

import requests
from filetype import guess
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceManager:
    def __init__(self):
        self._base_path = self._get_base_path()
    
    def _get_base_path(self):
        try:
            return Path(sys._MEIPASS)
        except AttributeError:
            return Path(__file__).parent if '__file__' in globals() else Path.cwd()
    
    def get_resource_path(self, relative_path):
        return str((self._base_path / relative_path).resolve()).replace('\\', '/')


class MediaTypeDetector:
    def __init__(self):
        self.mime_to_ext = self._build_mime_mapping()
    
    def _build_mime_mapping(self):
        return {
            **{f'image/{fmt}': (ext, 'image') for fmt, ext in {
                'jpeg': 'jpg', 'png': 'png', 'gif': 'gif', 'tiff': 'tiff',
                'webp': 'webp', 'heic': 'heic', 'avif': 'avif', 'heif': 'heif'
            }.items()},
            **{f'image/{fmt}': (ext, 'image') for fmt, ext in {
                'x-canon-cr2': 'cr2', 'x-canon-cr3': 'cr3', 'x-nikon-nef': 'nef',
                'x-sony-arw': 'arw', 'x-olympus-orf': 'orf', 'x-panasonic-raw': 'raw',
                'x-fuji-raf': 'raf', 'x-adobe-dng': 'dng', 'x-samsung-srw': 'srw',
                'x-pentax-pef': 'pef', 'x-kodak-dcr': 'dcr', 'x-kodak-k25': 'k25',
                'x-kodak-kdc': 'kdc', 'x-minolta-mrw': 'mrw', 'x-sigma-x3f': 'x3f'
            }.items()},
            **{f'video/{fmt}': (ext, 'video') for fmt, ext in {
                'mp4': 'mp4', 'x-msvideo': 'avi', 'x-matroska': 'mkv',
                'quicktime': 'mov', 'x-ms-wmv': 'wmv', 'mpeg': 'mpeg',
                'webm': 'webm', 'x-flv': 'flv', '3gpp': '3gp', '3gpp2': '3g2',
                'x-m4v': 'm4v', 'x-ms-asf': 'asf', 'x-mng': 'mng',
                'x-sgi-movie': 'movie', 'mp2t': 'ts', 'MP2T': 'ts'
            }.items()},
            'application/vnd.apple.mpegurl': ('m3u8', 'video'),
            'application/x-mpegurl': ('m3u8', 'video'),
            **{f'audio/{fmt}': (ext, 'audio') for fmt, ext in {
                'mpeg': 'mp3', 'wav': 'wav', 'x-wav': 'wav', 'flac': 'flac',
                'aac': 'aac', 'x-m4a': 'm4a', 'ogg': 'ogg', 'webm': 'webm',
                'amr': 'amr', 'x-ms-wma': 'wma', 'x-aiff': 'aiff', 'x-midi': 'midi'
            }.items()},
            'application/octet-stream': ('bin', 'other')
        }
    
    def detect_media_type(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        
        try:
            kind = guess(file_path)
        except (IOError, PermissionError, OSError) as e:
            raise IOError(f"读取文件错误: {str(e)}")

        if not kind:
            return self._create_invalid_result()

        mime = kind.mime
        result = self._create_base_result(mime)

        if result['valid']:
            ext, media_type = self.mime_to_ext[mime]
            result.update({
                'extension': ext,
                'type': media_type,
                'extension_match': (ext == file_ext)
            })

        return result
    
    def _create_invalid_result(self):
        return {
            'valid': False,
            'type': None,
            'mime': None,
            'extension': None,
            'extension_match': False
        }
    
    def _create_base_result(self, mime):
        return {
            'valid': mime in self.mime_to_ext,
            'mime': mime,
            'extension': None,
            'type': None,
            'extension_match': False
        }


class GeocodingService:
    def __init__(self):
        self.headers = {
            'accept': '*/*', 
            'accept-language': 'zh-CN,zh;q=0.9',
            'referer': 'https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding',
            'user-agent': 'Mozilla/5.0'
        }
        self.url_template = 'https://developer.amap.com/AMapService/v3/geocode/regeo?key={key}&s=rsv3&language=zh_cn&location={loc}&radius=1000&callback=jsonp_765657_&platform=JS&logversion=2.0&appname=https%3A%2F%2Fdeveloper.amap.com%2Fdemo%2Fjavascript-api%2Fexample%2Fgeocoder%2Fregeocoding&csid=123456&sdkversion=1.4.27'
        self._lock = threading.Lock()
        self._cached_cookies = None
        self._cached_key = None
        self._credentials_last_checked = 0
    
    def get_address_from_coordinates(self, lat, lon):
        loc = f"{lon},{lat}"
        logger.info(f"开始转换坐标到地址: 纬度={lat}, 经度={lon}")
        
        with self._lock:
            cookies, key = self._load_cached_credentials()
            
            if not (cookies and key):
                logger.info("没有找到缓存的凭证，需要获取新凭证")
                cookies, key = self._fetch_credentials()
                if cookies and key:
                    self._save_credentials(cookies, key)
        
        address = self._call_geocoding_api(loc, cookies, key)
        logger.info(f"坐标转换完成: 纬度={lat}, 经度={lon}, 地址={address}")
        return address
    
    def _load_cached_credentials(self):
        current_time = time.time()
        if self._cached_cookies and self._cached_key and (current_time - self._credentials_last_checked < 300):
            return self._cached_cookies, self._cached_key
            
        if os.path.exists("cookies.json"):
            try:
                with open("cookies.json", "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cookies = saved.get("cookies")
                    key = saved.get("key")
                    self._cached_cookies = cookies
                    self._cached_key = key
                    self._credentials_last_checked = current_time
                    return cookies, key
            except (json.JSONDecodeError, IOError, PermissionError) as e:
                logger.error(f"读取cookies.json失败: {str(e)}")
        return None, None
    
    def _fetch_credentials(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_context().new_page()
                try:
                    page.goto("https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding")
                    page.wait_for_timeout(3000)
                    
                    target_keys = ['cna', 'passport_login', 'xlly_s', 'HMACCOUNT', 
                                  'Hm_lvt_c8ac07c199b1c09a848aaab761f9f909',
                                  'Hm_lpvt_c8ac07c199b1c09a848aaab761f9f909', 'tfstk']
                    cookies = {c['name']: c['value'] for c in page.context.cookies() 
                              if c['name'] in target_keys}
                    
                    key = page.get_attribute("#code_origin", "data-jskey")
                    return cookies, key
                finally:
                    if browser.is_connected():
                        browser.close()
        except (ImportError, TimeoutError, ConnectionError) as e:
            logger.error(f"获取地理编码凭证失败: {str(e)}")
            return None, None
    
    def _save_credentials(self, cookies, key):
        self._cached_cookies = cookies
        self._cached_key = key
        self._credentials_last_checked = time.time()
        
        try:
            with open("cookies.json", "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies, "key": key}, f, ensure_ascii=False)
        except (IOError, PermissionError) as e:
            logger.error(f"保存cookies.json失败: {str(e)}")
    
    def _call_geocoding_api(self, loc, cookies, key):
        if not (cookies and key):
            logger.warning("缺少地理编码凭证")
            return "未知位置"
        
        try:
            url = self.url_template.format(key=key, loc=loc)
            logger.info(f"向高德地图API发送网络请求, 位置坐标: {loc}")
            with requests.get(url, headers=self.headers, cookies=cookies, timeout=10) as resp:
                resp.raise_for_status()
                
                if resp.status_code == 200 and "formatted_address" in resp.text:
                    try:
                        json_str = resp.text[resp.text.index('(') + 1:resp.text.rindex(')')]
                        result = json.loads(json_str).get("regeocode", {}).get("formatted_address", "")
                        return result if result else "未知位置"
                    except (ValueError, json.JSONDecodeError) as parse_error:
                        logger.error(f"解析地理编码响应失败: {str(parse_error)}")
        except requests.exceptions.RequestException as e:
            logger.error(f"地理编码API调用失败: {str(e)}")
        
        return "未知位置"


_resource_manager = ResourceManager()
_media_detector = MediaTypeDetector()
_geocoding_service = GeocodingService()

def get_resource_path(relative_path):
    return _resource_manager.get_resource_path(relative_path)

def detect_media_type(file_path):
    return _media_detector.detect_media_type(file_path)

def get_address_from_coordinates(lat, lon):
    return _geocoding_service.get_address_from_coordinates(lat, lon)

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
            if result['valid']:
                media_type = result['type']
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