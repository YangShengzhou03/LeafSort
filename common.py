import json
import os
import sys
from pathlib import Path

import requests
from filetype import guess
from playwright.sync_api import sync_playwright


def get_resource_path(relative_path):
    """获取资源文件的绝对路径，支持打包后的应用"""
    try:
        base_path = Path(sys._MEIPASS)
    except Exception:
        base_path = Path(__file__).parent if '__file__' in globals() else Path.cwd()

    return str((base_path / relative_path).resolve()).replace('\\', '/')


def detect_media_type(file_path):
    """检测媒体文件类型和格式"""
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    # 定义MIME类型到文件扩展名的映射
    mime_to_ext = {
        # 常见图片格式
        **{f'image/{fmt}': (ext, 'image') for fmt, ext in {
            'jpeg': 'jpg', 'png': 'png', 'gif': 'gif', 'tiff': 'tiff',
            'webp': 'webp', 'heic': 'heic', 'avif': 'avif', 'heif': 'heif'
        }.items()},
        # RAW相机格式
        **{f'image/{fmt}': (ext, 'image') for fmt, ext in {
            'x-canon-cr2': 'cr2', 'x-canon-cr3': 'cr3', 'x-nikon-nef': 'nef',
            'x-sony-arw': 'arw', 'x-olympus-orf': 'orf', 'x-panasonic-raw': 'raw',
            'x-fuji-raf': 'raf', 'x-adobe-dng': 'dng', 'x-samsung-srw': 'srw',
            'x-pentax-pef': 'pef', 'x-kodak-dcr': 'dcr', 'x-kodak-k25': 'k25',
            'x-kodak-kdc': 'kdc', 'x-minolta-mrw': 'mrw', 'x-sigma-x3f': 'x3f'
        }.items()},
        # 视频格式
        **{f'video/{fmt}': (ext, 'video') for fmt, ext in {
            'mp4': 'mp4', 'x-msvideo': 'avi', 'x-matroska': 'mkv',
            'quicktime': 'mov', 'x-ms-wmv': 'wmv', 'mpeg': 'mpeg',
            'webm': 'webm', 'x-flv': 'flv', '3gpp': '3gp', '3gpp2': '3g2',
            'x-m4v': 'm4v', 'x-ms-asf': 'asf', 'x-mng': 'mng',
            'x-sgi-movie': 'movie', 'mp2t': 'ts', 'MP2T': 'ts'
        }.items()},
        # 特殊格式
        'application/vnd.apple.mpegurl': ('m3u8', 'video'),
        'application/x-mpegurl': ('m3u8', 'video'),
        # 音频格式
        **{f'audio/{fmt}': (ext, 'audio') for fmt, ext in {
            'mpeg': 'mp3', 'wav': 'wav', 'x-wav': 'wav', 'flac': 'flac',
            'aac': 'aac', 'x-m4a': 'm4a', 'ogg': 'ogg', 'webm': 'webm',
            'amr': 'amr', 'x-ms-wma': 'wma', 'x-aiff': 'aiff', 'x-midi': 'midi'
        }.items()},
        'application/octet-stream': ('bin', 'other')
    }

    file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
    
    try:
        kind = guess(file_path)
    except Exception as e:
        raise IOError(f"读取文件错误: {str(e)}")

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
    """根据经纬度坐标获取地址信息"""
    headers = {
        'accept': '*/*', 
        'accept-language': 'zh-CN,zh;q=0.9',
        'referer': 'https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding',
        'user-agent': 'Mozilla/5.0'
    }
    loc = f"{lon},{lat}"
    url_tpl = 'https://developer.amap.com/AMapService/v3/geocode/regeo?key={key}&s=rsv3&language=zh_cn&location={loc}&radius=1000&callback=jsonp_765657_&platform=JS&logversion=2.0&appname=https%3A%2F%2Fdeveloper.amap.com%2Fdemo%2Fjavascript-api%2Fexample%2Fgeocoder%2Fregeocoding&csid=123456&sdkversion=1.4.27'
    
    cookies, key = None, None
    
    # 尝试从缓存文件读取cookies和key
    if os.path.exists("cookies.json"):
        try:
            with open("cookies.json", "r", encoding="utf-8") as f:
                saved = json.load(f)
                cookies, key = saved.get("cookies"), saved.get("key")
        except Exception:
            pass
    
    # 如果没有缓存，使用Playwright获取
    if not (cookies and key):
        target_keys = ['cna', 'passport_login', 'xlly_s', 'HMACCOUNT', 
                      'Hm_lvt_c8ac07c199b1c09a848aaab761f9f909',
                      'Hm_lpvt_c8ac07c199b1c09a848aaab761f9f909', 'tfstk']
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_context().new_page()
                page.goto("https://developer.amap.com/demo/javascript-api/example/geocoder/regeocoding")
                page.wait_for_timeout(3000)
                cookies = {c['name']: c['value'] for c in page.context.cookies() 
                          if c['name'] in target_keys}
                key = page.get_attribute("#code_origin", "data-jskey")
                browser.close()
                
            # 保存到缓存文件
            with open("cookies.json", "w", encoding="utf-8") as f:
                json.dump({"cookies": cookies, "key": key}, f, ensure_ascii=False)
        except Exception:
            pass
    
    # 调用API获取地址信息
    try:
        if cookies and key:
            url = url_tpl.format(key=key, loc=loc)
            resp = requests.get(url, headers=headers, cookies=cookies, timeout=10)
            if resp.status_code == 200 and "formatted_address" in resp.text:
                json_str = resp.text[resp.text.index('(') + 1:resp.text.rindex(')')]
                return json.loads(json_str).get("regeocode", {}).get("formatted_address", "")
    except Exception:
        pass
    
    return "获取地址失败"