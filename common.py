import json
import os
import sys
from pathlib import Path

import requests
from filetype import guess
from playwright.sync_api import sync_playwright


def get_resource_path(relative_path):
    """获取资源文件的绝对路径"""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()

    return str((base_path / relative_path).resolve()).replace('\\', '/')


def detect_media_type(file_path):
    """检测文件的媒体类型并返回详细信息"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"这个文件不存在: {file_path}")

    # 优化媒体类型映射定义，按类别分组
    mime_to_ext = {}
    
    # 常见图片格式
    image_formats = {
        'jpeg': 'jpg', 'png': 'png', 'gif': 'gif', 'tiff': 'tiff',
        'webp': 'webp', 'heic': 'heic', 'avif': 'avif', 'heif': 'heif'
    }
    for format_name, ext in image_formats.items():
        mime_to_ext[f'image/{format_name}'] = (ext, 'image')
    
    # RAW图片格式
    raw_formats = {
        'x-canon-cr2': 'cr2', 'x-canon-cr3': 'cr3', 'x-nikon-nef': 'nef',
        'x-sony-arw': 'arw', 'x-olympus-orf': 'orf', 'x-panasonic-raw': 'raw',
        'x-fuji-raf': 'raf', 'x-adobe-dng': 'dng', 'x-samsung-srw': 'srw',
        'x-pentax-pef': 'pef', 'x-kodak-dcr': 'dcr', 'x-kodak-k25': 'k25',
        'x-kodak-kdc': 'kdc', 'x-minolta-mrw': 'mrw', 'x-sigma-x3f': 'x3f'
    }
    for format_name, ext in raw_formats.items():
        mime_to_ext[f'image/{format_name}'] = (ext, 'image')
    
    # 视频格式
    video_formats = {
        'mp4': 'mp4', 'x-msvideo': 'avi', 'x-matroska': 'mkv',
        'quicktime': 'mov', 'x-ms-wmv': 'wmv', 'mpeg': 'mpeg',
        'webm': 'webm', 'x-flv': 'flv', '3gpp': '3gp', '3gpp2': '3g2',
        'x-m4v': 'm4v', 'x-ms-asf': 'asf', 'x-mng': 'mng',
        'x-sgi-movie': 'movie', 'mp2t': 'ts', 'MP2T': 'ts'
    }
    for format_name, ext in video_formats.items():
        mime_to_ext[f'video/{format_name}'] = (ext, 'video')
    
    # 特殊视频格式
    mime_to_ext['application/vnd.apple.mpegurl'] = ('m3u8', 'video')
    mime_to_ext['application/x-mpegurl'] = ('m3u8', 'video')
    
    # 音频格式
    audio_formats = {
        'mpeg': 'mp3', 'wav': 'wav', 'x-wav': 'wav', 'flac': 'flac',
        'aac': 'aac', 'x-m4a': 'm4a', 'ogg': 'ogg', 'webm': 'webm',
        'amr': 'amr', 'x-ms-wma': 'wma', 'x-aiff': 'aiff', 'x-midi': 'midi'
    }
    for format_name, ext in audio_formats.items():
        mime_to_ext[f'audio/{format_name}'] = (ext, 'audio')
    
    # 其他格式
    mime_to_ext['application/octet-stream'] = ('bin', 'other')

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
    """根据经纬度获取地址信息"""
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
            except Exception:
                pass

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
        except Exception:
            pass
        return None

    cookies, key = get_cookies_key()
    addr = get_address(cookies, key)
    return addr or "获取失败"



