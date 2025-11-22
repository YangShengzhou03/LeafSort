import json
import os
import sys
from pathlib import Path

import requests
from filetype import guess
from playwright.sync_api import sync_playwright


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径
    同时支持开发环境和打包后的环境
    
    Args:
        relative_path: 相对于项目根目录的路径
        
    Returns:
        str: 资源文件的绝对路径
    """
    try:
        # 打包后的环境
        base_path = Path(sys._MEIPASS)
    except Exception:
        # 开发环境
        base_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()

    # 规范化路径，使用正斜杠
    return str((base_path / relative_path).resolve()).replace('\\', '/')


def detect_media_type(file_path):
    """
    检测媒体文件类型
    
    Args:
        file_path: 文件路径
        
    Returns:
        dict: 包含文件类型信息的字典
        
    Raises:
        FileNotFoundError: 文件不存在时抛出
    """
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"这个文件不存在: {file_path}")

    mime_to_ext = {
        'image/jpeg': ('jpg', 'image'),
        'image/png': ('png', 'image'),
        'image/gif': ('gif', 'image'),
        'image/tiff': ('tiff', 'image'),
        'image/webp': ('webp', 'image'),
        'image/heic': ('heic', 'image'),
        'image/avif': ('avif', 'image'),
        'image/heif': ('heif', 'image'),
        
        'image/x-canon-cr2': ('cr2', 'image'),
        'image/x-canon-cr3': ('cr3', 'image'),
        'image/x-nikon-nef': ('nef', 'image'),
        'image/x-sony-arw': ('arw', 'image'),
        'image/x-olympus-orf': ('orf', 'image'),
        'image/x-panasonic-raw': ('raw', 'image'),
        'image/x-fuji-raf': ('raf', 'image'),
        'image/x-adobe-dng': ('dng', 'image'),
        'image/x-samsung-srw': ('srw', 'image'),
        'image/x-pentax-pef': ('pef', 'image'),
        'image/x-kodak-dcr': ('dcr', 'image'),
        'image/x-kodak-k25': ('k25', 'image'),
        'image/x-kodak-kdc': ('kdc', 'image'),
        'image/x-minolta-mrw': ('mrw', 'image'),
        'image/x-sigma-x3f': ('x3f', 'image'),
        
        'video/mp4': ('mp4', 'video'),
        'video/x-msvideo': ('avi', 'video'),
        'video/x-matroska': ('mkv', 'video'),
        'video/quicktime': ('mov', 'video'),
        'video/x-ms-wmv': ('wmv', 'video'),
        'video/mpeg': ('mpeg', 'video'),
        'video/webm': ('webm', 'video'),
        'video/x-flv': ('flv', 'video'),
        'video/3gpp': ('3gp', 'video'),
        'video/3gpp2': ('3g2', 'video'),
        'video/x-m4v': ('m4v', 'video'),
        'video/x-ms-asf': ('asf', 'video'),
        'video/x-mng': ('mng', 'video'),
        'video/x-sgi-movie': ('movie', 'video'),
        'application/vnd.apple.mpegurl': ('m3u8', 'video'),
        'application/x-mpegurl': ('m3u8', 'video'),
        'video/mp2t': ('ts', 'video'),
        'video/MP2T': ('ts', 'video'),
        
        'audio/mpeg': ('mp3', 'audio'),
        'audio/wav': ('wav', 'audio'),
        'audio/x-wav': ('wav', 'audio'),
        'audio/flac': ('flac', 'audio'),
        'audio/aac': ('aac', 'audio'),
        'audio/x-m4a': ('m4a', 'audio'),
        'audio/ogg': ('ogg', 'audio'),
        'audio/webm': ('webm', 'audio'),
        'audio/amr': ('amr', 'audio'),
        'audio/x-ms-wma': ('wma', 'audio'),
        'audio/x-aiff': ('aiff', 'audio'),
        'audio/x-midi': ('midi', 'audio'),
        
        'application/octet-stream': ('bin', 'other'),
    }

    file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    
    try:
        kind = guess(file_path)
    except Exception as e:
        raise IOError(f"读文件时出错了: {str(e)}")

    if not kind:
        return {
            'valid': False,
            'type': None,
            'mime': None,
            'extension': None,
            'extension_match': False
        }

    mime = kind.mime
    result = {
        'valid': mime in mime_to_ext,
        'mime': mime,
        'extension': None,
        'type': None,
        'extension_match': False
    }

    if result['valid']:
        ext, media_type = mime_to_ext[mime]
        result.update({
            'extension': ext,
            'type': media_type,
            'extension_match': (ext == file_ext)
        })

    return result


def get_address_from_coordinates(lat, lon):
    headers = {'accept': '*/*', 'accept-language': 'zh-CN,zh;q=0.9',
               'referer': 'https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding',
               'user-agent': 'Mozilla/5.0'}
    loc = f"{lon},{lat}"
    url_tpl = 'https://developer.amap.com/AMapService/v3/geocode/regeo?key={key}&s=rsv3&language=zh_cn&location={loc}&radius=1000&callback=jsonp_765657_&platform=JS&logversion=2.0&appname=https%3A%2F%2Fdeveloper.amap.com%2Fdemo%2Fjavascript-api%2Fexample%2Fgeocoder%2Fregeocoding&csid=123456&sdkversion=1.4.27'

    def get_cookies_key():
        if os.path.exists("cookies.json"):
            try:
                with open("cookies.json", "r", encoding="utf-8") as f:
                    saved = json.load(f)
                    if saved.get("cookies") and saved.get("key"):
                        return saved["cookies"], saved["key"]
            except Exception as e:
                print(f"读取cookies失败: {e}")

        target_keys = ['cna', 'passport_login', 'xlly_s', 'HMACCOUNT', 'Hm_lvt_c8ac07c199b1c09a848aaab761f9f909',
                       'Hm_lpvt_c8ac07c199b1c09a848aaab761f9f909', 'tfstk']
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_context().new_page()
            page.goto("https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding")
            page.wait_for_timeout(3000)
            cookies = {c['name']: c['value'] for c in page.context.cookies() if c['name'] in target_keys}
            key = page.get_attribute("#code_origin", "data-jskey")
            browser.close()

        with open("cookies.json", "w", encoding="utf-8") as f:
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


if __name__ == "__main__":
    print(f"坐标 (39.9087, 116.3975) 对应的地址是：{get_address_from_coordinates(39.9087, 116.3975)}")
