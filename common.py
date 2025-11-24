import json
import os
import sys
import time
import threading
from pathlib import Path

import requests
from filetype import guess
from playwright.sync_api import sync_playwright


class ResourceManager:
    def __init__(self):
        self._base_path = self._get_base_path()
    
    def _get_base_path(self):
        try:
            return Path(sys._MEIPASS)
        except AttributeError:
            # 非打包环境下sys._MEIPASS不存在
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


import threading

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
        
        with self._lock:
            cookies, key = self._load_cached_credentials()
            
            if not (cookies and key):
                cookies, key = self._fetch_credentials()
                if cookies and key:
                    self._save_credentials(cookies, key)
        
        return self._call_geocoding_api(loc, cookies, key)
    
    def _load_cached_credentials(self):
        # 优先使用内存缓存
        import time
        current_time = time.time()
        if self._cached_cookies and self._cached_key and (current_time - self._credentials_last_checked < 300):
            return self._cached_cookies, self._cached_key
            
        if os.path.exists("cookies.json"):
            try:
                with open("cookies.json", "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    cookies = saved.get("cookies")
                    key = saved.get("key")
                    # 更新内存缓存
                    self._cached_cookies = cookies
                    self._cached_key = key
                    self._credentials_last_checked = current_time
                    return cookies, key
            except (json.JSONDecodeError, IOError, PermissionError) as e:
                # 处理JSON解析错误和文件IO错误
                print(f"读取cookies.json失败: {str(e)}")
        return None, None
    
    def _fetch_credentials(self):
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_context().new_page()
                page.goto("https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding")
                page.wait_for_timeout(3000)
                
                target_keys = ['cna', 'passport_login', 'xlly_s', 'HMACCOUNT', 
                              'Hm_lvt_c8ac07c199b1c09a848aaab761f9f909',
                              'Hm_lpvt_c8ac07c199b1c09a848aaab761f9f909', 'tfstk']
                cookies = {c['name']: c['value'] for c in page.context.cookies() 
                          if c['name'] in target_keys}
                
                key = page.get_attribute("#code_origin", "data-jskey")
                browser.close()
                return cookies, key
        except (ImportError, TimeoutError, ConnectionError) as e:
            print(f"获取地理编码凭证失败: {str(e)}")
            return None, None
    
    def _save_credentials(self, cookies, key):
        # 更新内存缓存
        self._cached_cookies = cookies
        self._cached_key = key
        self._credentials_last_checked = time.time()
        
        try:
            with open("cookies.json", "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies, "key": key}, f, ensure_ascii=False)
        except (IOError, PermissionError) as e:
            print(f"保存cookies.json失败: {str(e)}")
    
    def _call_geocoding_api(self, loc, cookies, key):
        if not (cookies and key):
            return "获取地址失败"
        
        try:
            url = self.url_template.format(key=key, loc=loc)
            resp = requests.get(url, headers=self.headers, cookies=cookies, timeout=10)
            resp.raise_for_status()  # 检查HTTP错误
            
            if resp.status_code == 200 and "formatted_address" in resp.text:
                json_str = resp.text[resp.text.index('(') + 1:resp.text.rindex(')')]
                return json.loads(json_str).get("regeocode", {}).get("formatted_address", "")
        except (requests.exceptions.RequestException, json.JSONDecodeError, ValueError) as e:
            print(f"地理编码API调用失败: {str(e)}")
        
        return "获取地址失败"


_resource_manager = ResourceManager()
_media_detector = MediaTypeDetector()
_geocoding_service = GeocodingService()

def get_resource_path(relative_path):
    return _resource_manager.get_resource_path(relative_path)

def detect_media_type(file_path):
    return _media_detector.detect_media_type(file_path)

def get_address_from_coordinates(lat, lon):
    return _geocoding_service.get_address_from_coordinates(lat, lon)

# 兼容性函数，与smart_arrange_thread.py中的get_file_type功能保持一致
def get_file_type(file_path):
    """根据文件扩展名或MIME类型确定文件类型类别"""
    # 如果是Path对象，转换为字符串
    file_path_str = str(file_path)
    file_ext = os.path.splitext(file_path_str)[1].lower()
    
    # 首先尝试使用扩展名快速匹配
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
    
    # 如果扩展名匹配失败且文件存在，尝试使用MIME类型检测
    if os.path.isfile(file_path_str):
        try:
            result = detect_media_type(file_path_str)
            if result['valid']:
                media_type = result['type']
                # 映射MIME类型到类别名称
                mime_to_category = {
                    'image': '图像',
                    'video': '视频',
                    'audio': '音乐'
                }
                if media_type in mime_to_category:
                    return mime_to_category[media_type]
        except (FileNotFoundError, IOError):
            # 如果检测失败，返回'其他'
            pass
    
    return '其他'