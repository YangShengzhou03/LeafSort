import logging
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timedelta

import piexif
from PIL import Image, PngImagePlugin
from PyQt6.QtCore import QThread, pyqtSignal

from common import get_resource_path

logger = logging.getLogger(__name__)

try:
    from pillow_heif import open_heif, register_heif_opener
    PILLOW_HEIF_AVAILABLE = True
    register_heif_opener()
except ImportError:
    PILLOW_HEIF_AVAILABLE = False

class WriteExifThread(QThread):
    progress_updated = pyqtSignal(int)
    finished_conversion = pyqtSignal()
    log_signal = pyqtSignal(str, str)

    def log(self, level, message):
        try:
            if not isinstance(level, str) or not isinstance(message, str):
                raise TypeError("Log level and message must be string types")
            
            valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
            if level not in valid_levels:
                level = 'INFO'
            
            if level == 'ERROR':
                logger.error(message)
            elif level == 'WARNING':
                logger.warning(message)
            elif level == 'DEBUG':
                logger.debug(message)
            else:
                logger.info(message)
                
            self.log_signal.emit(level, message)
        except Exception as e:
            try:
                error_msg = f"Failed to record log: {str(e)}"
                logger.error(error_msg)
            except:
                pass
    
    def _decode_subprocess_output(self, output_data):
        if not output_data:
            return ""
        
        encodings = ['utf-8', 'gbk', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                return output_data.decode(encoding, errors='replace')
            except (UnicodeDecodeError, AttributeError):
                continue
        
        return ""
            
    def __init__(self, folders_dict, exif_config=None, target_folder=None):
        super().__init__()
        self.folders_dict = {item['path']: item['include_sub'] for item in folders_dict}
        self.exif_config = exif_config or {}
        self.target_folder = target_folder or os.path.expanduser("~/Desktop/Processed_Images")
        self.lat, self.lon = None, None
        
        self._requires_exiftool_lens_update = False
        self._exiftool_lens_data = {}
        
        position = self.exif_config.get('position', '')
        if position and ',' in position:
            try:
                self.lat, self.lon = map(float, position.split(','))
                if not (-90 <= self.lat <= 90) or not (-180 <= self.lon <= 180):
                    self.lat, self.lon = None, None
            except ValueError as e:
                self.log("ERROR", f"Failed to parse coordinate values: {str(e)}")
                self.lat, self.lon = None, None

    def run(self):
        image_paths = self._collect_image_paths()
        total_files = len(image_paths)
        
        if not image_paths:
            self.log("WARNING", "没有找到任何可以处理的图像文件\n\n"
                           "请检查：\n"
                           "• 您选择的文件夹路径是否正确\n"
                           "• 文件夹里是否有.jpg、.jpeg、.png、.webp等格式的图片")
            self.finished_conversion.emit()
            return
        
        self.log("DEBUG", f"{'=' * 10} 待处理总文件数： {total_files} {'=' * 10}")
        self.progress_updated.emit(0)
        
        success_count, error_count = self._process_all_images(image_paths)
        
        self._log_completion_summary(success_count, error_count, total_files)
        self.finished_conversion.emit()
    
    def _process_all_images(self, image_paths):
        success_count = 0
        error_count = 0
        
        valid_paths = []
        for path in image_paths:
            if self.isInterruptionRequested():
                break
                
            try:
                file_size = os.path.getsize(path)
                if file_size > 500 * 1024 * 1024:
                    self.log("ERROR", f"文件 {os.path.basename(path)} 太大了(超过500MB)，暂不支持处理")
                    error_count += 1
                    continue
            except (IOError, OSError) as e:
                self.log("ERROR", f"获取文件大小失败 {os.path.basename(path)}: {str(e)}")
                error_count += 1
                continue
                
            valid_paths.append(path)
        
        total_valid = len(valid_paths)
        if total_valid == 0:
            return success_count, error_count
        
        processed_count = 0
        
        for path in valid_paths:
            if self.isInterruptionRequested():
                break
                
            try:
                result = self.process_image(path)
                if result == 'success':
                    success_count += 1
                elif result == 'skipped':
                    error_count += 1
                elif result == 'failed':
                    error_count += 1
            except (IOError, ValueError, TypeError, TimeoutError) as e:
                self.log("ERROR", f"处理文件 {os.path.basename(path)} 时出错: {str(e)}")
                error_count += 1
            
            processed_count += 1
            progress = int((processed_count / total_valid) * 100)
            self.progress_updated.emit(progress)
        
        return success_count, error_count
    
    def _log_completion_summary(self, success_count, error_count, total_files):
        self.log("DEBUG", "="*40)
        self.log("DEBUG", f"文件写入完成：成功写入了 {success_count} 张，失败了 {error_count} 张，共 {total_files}。")
        self.log("DEBUG", "="*3+"LeafSort（轻羽媒体整理） © 2025 Yangshengzhou.All Rights Reserved"+"="*3)

    def _collect_image_paths(self):
        image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mov', '.mp4', '.avi', '.mkv')
        raw_extensions = ('.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf')
        all_extensions = image_extensions + raw_extensions
        
        image_paths = []
        
        for folder_path, include_sub in self.folders_dict.items():
            if os.path.isdir(folder_path):
                if include_sub:
                    for root, _, files in os.walk(folder_path):
                        if self.isInterruptionRequested():
                            break
                        image_paths.extend([os.path.join(root, f) for f in files 
                                          if os.path.splitext(f)[1].lower() in all_extensions])
                else:
                    try:
                        files = [f for f in os.listdir(folder_path) 
                                if os.path.isfile(os.path.join(folder_path, f)) 
                                and os.path.splitext(f)[1].lower() in all_extensions]
                        image_paths.extend([os.path.join(folder_path, f) for f in files])
                    except (IOError, OSError) as e:
                        self.log("ERROR", f"读取文件夹失败: {str(e)}")
        
        return image_paths
    
    def process_image(self, image_path):
        try:
            if self.isInterruptionRequested():
                self.log("WARNING", f"处理被取消: {os.path.basename(image_path)}")
                return 'failed'
            
            if not self._validate_file(image_path):
                return 'failed'
            
            target_path = self._copy_to_target(image_path)
            if not target_path:
                return 'failed'
            
            file_ext = os.path.splitext(image_path)[1].lower()

            
            format_handler = self._get_format_handler(file_ext)
            if format_handler:
                format_handler_result = format_handler(target_path)
                if format_handler_result == 'skipped':
                    return 'skipped'
                elif format_handler_result == 'failed':
                    return 'failed'
                else:
                    return 'success'
            else:
                logger.warning("不支持的文件格式: %s", file_ext)
                self.log("WARNING", f"不支持的文件格式: {file_ext}")
                return 'skipped'

        except (IOError, ValueError, TypeError, OSError) as e:
            logger.error("处理文件 %s 时出错: %s", image_path, str(e))
            self._handle_processing_error(image_path, e)
            return 'failed'
    
    def _validate_file(self, image_path):
        if not os.path.exists(image_path):
            logger.error("文件不存在: %s", image_path)
            self.log("ERROR", f"文件不存在: {os.path.basename(image_path)}")
            return False
        
        if not os.access(image_path, os.R_OK):
            logger.error("文件不可读: %s", image_path)
            self.log("ERROR", f"文件不可读: {os.path.basename(image_path)}")
            return False
            
        return True
        
    def _get_format_handler(self, file_ext):
        handlers = {
            ('.jpg', '.jpeg', '.webp'): self._process_exif_format,
            ('.png',): self._process_png_format,
            ('.heic', '.heif'): self._process_heic_format,
            ('.mov', '.mp4', '.avi', '.mkv'): self._process_video_format,
            ('.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf'): self._process_raw_format
        }
        
        for extensions, handler in handlers.items():
            if file_ext in extensions:
                return handler
                
        return None

    def _handle_processing_error(self, image_path, error):
        error_msg = f"处理 {os.path.basename(image_path)} 时出错: {str(error)}"
        logger.error("处理文件 %s 时出错: %s", image_path, str(error))
        self.log("ERROR", error_msg)
    
    def _get_target_path(self, source_path):
        for root_folder, include_sub in self.folders_dict.items():
            if source_path.startswith(root_folder):
                relative_path = os.path.relpath(source_path, root_folder)
                target_path = os.path.join(self.target_folder, relative_path)
                return target_path
        
        return os.path.join(self.target_folder, os.path.basename(source_path))
    
    def _copy_to_target(self, source_path):
        try:
            target_path = self._get_target_path(source_path)
            target_dir = os.path.dirname(target_path)
            
            if not os.path.exists(target_dir):
                os.makedirs(target_dir)
            
            shutil.copy2(source_path, target_path)
            return target_path
            
        except (IOError, OSError, shutil.Error) as e:
            self.log("ERROR", f"复制文件失败 {os.path.basename(source_path)}: {str(e)}")
            return None

    def _process_exif_format(self, image_path):
        if self.isInterruptionRequested():
            return
            
        if not os.access(image_path, os.W_OK):
            error_msg = f"File not writable: {os.path.basename(image_path)}"
            logger.error("File not writable: %s", image_path)
            self.log("ERROR", error_msg)
            return
        
        exif_dict = self._load_exif_data(image_path)
        if not exif_dict:
            return
        
        updated_fields = self._update_exif_fields(exif_dict, image_path)
        if not updated_fields:
            return
        
        self._save_exif_data(image_path, exif_dict, updated_fields)
    
    def _load_exif_data(self, image_path):
        try:
            if self.isInterruptionRequested():
                return None
            return piexif.load(image_path)
        except (IOError, OSError, ValueError, TypeError) as e:
            logger.warning("Failed to load EXIF data %s: %s, will create new EXIF data", image_path, str(e))
            return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    def _update_exif_fields(self, exif_dict, image_path):
        if self.isInterruptionRequested():
            return []
            
        updated_fields = []
        
        try:
            self._ensure_exif_sections(exif_dict)
            
            if not self._check_exif_support(image_path):
                logger.warning("EXIF check failed, attempting to continue processing")
            
            self._requires_exiftool_lens_update = False
            self._exiftool_lens_data = {}
            
            self._update_basic_fields(exif_dict, updated_fields)
            
            self._update_special_fields(exif_dict, image_path, updated_fields)
            
            return self._check_update_result(updated_fields, image_path)
            
        except (IOError, ValueError, OSError) as e:
            error_msg = f"Error processing EXIF data {os.path.basename(image_path)}: {str(e)}"
            logger.error("Error processing EXIF data %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", error_msg)
            return []
    
    def _ensure_exif_sections(self, exif_dict):
        if "0th" not in exif_dict:
            exif_dict["0th"] = {}
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        if "GPS" not in exif_dict:
            exif_dict["GPS"] = {}
    
    def _update_basic_fields(self, exif_dict, updated_fields):
        basic_mappings = [
            ("title", "0th", piexif.ImageIFD.ImageDescription, "title", "标题: {}", "utf-8"),
            ("author", "0th", 315, "author", "作者: {}", "utf-8"),
            ("subject", "0th", piexif.ImageIFD.XPSubject, "subject", "主题: {}", "utf-16le"),
            ("rating", "0th", piexif.ImageIFD.Rating, "rating", "评分: {}星", None, int),
            ("copyright", "0th", piexif.ImageIFD.Copyright, "copyright", "版权: {}", "utf-8"),
            ("camera_brand", "0th", piexif.ImageIFD.Make, "camera_brand", "相机品牌: {}", "utf-8"),
            ("camera_model", "0th", piexif.ImageIFD.Model, "camera_model", "相机型号: {}", "utf-8")
        ]
        
        for _, section, tag, config_key, format_str, encoding, *transform in basic_mappings:
            value = self.exif_config.get(config_key)
            if value:
                try:
                    processed_value = transform[0](value) if transform else value
                    if encoding and isinstance(processed_value, str):
                        processed_value = processed_value.encode(encoding)
                    
                    exif_dict[section][tag] = processed_value
                    updated_fields.append(format_str.format(value))
                except Exception as e:
                    logger.error(f"Failed to write basic field {config_key}: {str(e)}")
        
        self._update_lens_information(exif_dict, updated_fields)
    
    def _update_lens_information(self, exif_dict, updated_fields):
        lens_brand = self.exif_config.get('lens_brand')
        lens_model = self.exif_config.get('lens_model')
        
        if not lens_brand and not lens_model:
            return
        
        try:
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}
            
            if lens_brand:
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = lens_brand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {lens_brand}")
            
            if lens_model:
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens_model.encode('utf-8')
                updated_fields.append(f"镜头型号: {lens_model}")
            
            self._requires_exiftool_lens_update = True
            self._exiftool_lens_data = {
                'lens_brand': lens_brand,
                'lens_model': lens_model
            }
            
        except Exception as e:
            logger.error(f"Failed to write basic lens information: {str(e)}")
            self.log("ERROR", f"Failed to write lens information: {str(e)}")
    
    def _check_exif_support(self, image_path):
        try:
            exiftool_path = get_resource_path('_internal/resources\\exiftool\\exiftool.exe')
            if not os.path.exists(exiftool_path):
                logger.warning("ExifTool path not found, skipping EXIF check")
                return True
            
            check_cmd = [exiftool_path, '-all', '-s', image_path]
            result = subprocess.run(check_cmd, capture_output=True, text=False, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                stdout_str = self._decode_subprocess_output(result.stdout)
                if stdout_str:
                    exif_count = len([line for line in stdout_str.split('\n') 
                                    if line.strip() and not line.startswith('=')])
                    
                    if exif_count == 0:
                        logger.info("File has no EXIF data, will initialize basic information")
                        return self._initialize_basic_exif(image_path)
                    return True
            else:
                stderr_str = self._decode_subprocess_output(result.stderr)
                logger.warning(f"Unable to read EXIF information: {stderr_str}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("EXIF check timeout")
            return True
        except Exception as e:
            logger.error(f"Error checking EXIF support: {str(e)}")
            return True
    
    def _initialize_basic_exif(self, image_path):
        try:
            exiftool_path = get_resource_path('_internal/resources\\exiftool\\exiftool.exe')
            if not os.path.exists(exiftool_path):
                logger.warning("ExifTool not found, cannot initialize EXIF")
                return False
            
            init_cmd = [
                exiftool_path,
                '-DateTimeOriginal=2023:01:01 12:00:00',
                '-Model=LeafSort Processed',
                '-Make=LeafSort',
                '-overwrite_original',
                image_path
            ]
            
            result = subprocess.run(init_cmd, capture_output=True, text=False, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                logger.info("Basic EXIF information initialized successfully")
                return True
            else:
                stderr_str = self._decode_subprocess_output(result.stderr)
                logger.error(f"EXIF initialization failed: {stderr_str}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing basic EXIF: {str(e)}")
            return False
    
    def _write_lens_info_with_exiftool(self, image_path):
        """使用ExifTool写入完整的镜头信息以确保Windows属性显示"""
        if not (self._exiftool_lens_data.get('lens_brand') or self._exiftool_lens_data.get('lens_model')):
            return True
        
        try:
            exiftool_path = get_resource_path('_internal/resources\\exiftool\\exiftool.exe')
            if not os.path.exists(exiftool_path):
                logger.warning("ExifTool 路径不存在，跳过ExifTool镜头信息写入")
                return False
            
            lens_brand = self._exiftool_lens_data.get('lens_brand', '')
            lens_model = self._exiftool_lens_data.get('lens_model', '')
            
            cmd = [
                exiftool_path,
                f'-LensManufacturer={lens_brand}',
                f'-LensModel={lens_model}',
                f'-LensMake={lens_brand}',
                f'-LensSpecification="{lens_brand} {lens_model}"',
                '-overwrite_original',
                image_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                logger.info("使用ExifTool写入镜头信息成功: %s %s", lens_brand, lens_model)
                return True
            else:
                stderr_str = self._decode_subprocess_output(result.stderr)
                logger.warning("使用ExifTool写入镜头信息失败: %s", stderr_str)
                self.log("WARNING", f"ExifTool写入镜头信息失败: {stderr_str}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("ExifTool写入镜头信息超时")
            return False
        except Exception as e:
            logger.error("使用ExifTool写入镜头信息时出错: %s", str(e))
            self.log("ERROR", f"ExifTool写入镜头信息时出错: {str(e)}")
            return False

    def _update_special_fields(self, exif_dict, image_path, updated_fields):
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time != 0:
            self._handle_shoot_time(exif_dict, image_path, updated_fields, shoot_time)
        
        if self.lat is not None and self.lon is not None:
            exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
            updated_fields.append(
                f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
    
    def _check_update_result(self, updated_fields, image_path):
        if not updated_fields:
            logger.info("文件 %s 没有需要更新的内容", image_path)
            self.log("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改\n\n可能的原因：\n• 所有EXIF字段均为空")
            return []
        return updated_fields
    
    def _save_exif_data(self, image_path, exif_dict, updated_fields):
        try:
            self._clean_exif_for_heic(exif_dict)
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            self.log("INFO", f"写入并复制 {os.path.basename(image_path)}")
            
            if hasattr(self, '_requires_exiftool_lens_update') and self._requires_exiftool_lens_update:
                success = self._write_lens_info_with_exiftool(image_path)
                if success:
                    updated_fields.append("镜头信息(ExifTool)")
                else:
                    self.log("WARNING", "使用ExifTool写入镜头信息失败")
            
        except (IOError, ValueError, OSError) as e:
            logger.error("写入EXIF数据失败 %s: %s", image_path, str(e))
            self.log("ERROR", f"写入EXIF数据失败 {os.path.basename(image_path)}: {str(e)}")

    def _handle_shoot_time(self, exif_dict, image_path, updated_fields, shoot_time):
        if shoot_time == 1:
            date_from_filename = self.get_date_from_filename(image_path)
            if date_from_filename:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_from_filename.strftime(
                    "%Y:%m:%d %H:%M:%S").encode('utf-8')
                updated_fields.append(
                    f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')}")
            else:
                logger.warning("无法从文件名提取时间: %s", image_path)
                self.log("WARNING", f"无法从文件名提取时间: {os.path.basename(image_path)}")
        elif shoot_time == 2:
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
            updated_fields.append(f"拍摄时间: {datetime.now().strftime('%Y:%m:%d %H:%M:%S')}")
        elif shoot_time == 3:
            logger.warning("拍摄时间选项3未实现: %s", shoot_time)
            self.log("WARNING", "拍摄时间选项3未实现")
        else:
            try:
                datetime.strptime(shoot_time, "%Y:%m:%d %H:%M:%S")
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = shoot_time.encode('utf-8')
                updated_fields.append(f"拍摄时间: {shoot_time}")
            except ValueError:
                logger.error("拍摄时间格式无效: %s", shoot_time)
                self.log("ERROR", f"拍摄时间格式无效: {shoot_time}，请使用 YYYY:MM:DD HH:MM:SS 格式")

    def _process_png_format(self, image_path):
        if not self._check_png_writable(image_path):
            return
            
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time != 0:
            self._process_png_shoot_time(image_path, shoot_time)
        else:
            logger.info("PNG文件 %s 没有需要更新的拍摄时间", image_path)
            
    def _check_png_writable(self, image_path):
        if not os.access(image_path, os.W_OK):
            logger.error("PNG文件不可写: %s", image_path)
            self.log("ERROR", f"PNG文件不可写: {os.path.basename(image_path)}")
            return False
        return True
    
    def _process_png_shoot_time(self, image_path):
        try:
            with Image.open(image_path) as img:
                png_info = PngImagePlugin.PngInfo()
                self._copy_existing_png_text(img, png_info)
                self._add_png_creation_time(image_path, img, png_info)
        except (IOError, OSError, ValueError, TypeError) as e:
            logger.error("处理PNG文件时出错 %s: %s", image_path, str(e))
            self.log("ERROR", f"处理PNG文件 {os.path.basename(image_path)} 时出错: {str(e)}")
    
    def _copy_existing_png_text(self, img, png_info):
        try:
            if img.text:
                for key in img.text:
                    if key.lower() != "creation time":
                        try:
                            png_info.add_text(key, img.text[key])
                        except (KeyError, ValueError, TypeError) as e:
                            logger.warning("复制PNG文本信息失败 %s: %s", key, str(e))
        except AttributeError as e:
            self.log("WARNING", f"复制PNG文本数据时出错: {str(e)}")
    
    def _add_png_creation_time(self, image_path, img, png_info):
        shoot_time = self.exif_config.get('shoot_time', None)
        if shoot_time == 1:
            date_from_filename = self.get_date_from_filename(image_path)
            if date_from_filename:
                png_info.add_text("Creation Time", str(date_from_filename))
                self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {str(date_from_filename)}")
            else:
                logger.warning("无法从文件名提取时间: %s", image_path)
                self.log("WARNING", f"无法从文件名提取时间: {os.path.basename(image_path)}")
        elif shoot_time:
            png_info.add_text("Creation Time", shoot_time)
            self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {shoot_time}")

    def _save_png_with_metadata(self, image_path, img, png_info, success_message):
        temp_path = image_path + ".tmp"
        
        try:
            img.save(temp_path, format="PNG", pnginfo=png_info)
            
            if not os.path.exists(temp_path):
                raise IOError("临时文件创建失败")
                
            os.replace(temp_path, image_path)
            logger.info("成功写入PNG元数据: %s", image_path)
            self.log("INFO", f"成功写入 {os.path.basename(image_path)} 的{success_message}")
            
        except PermissionError as e:
            logger.error("没有权限替换文件 %s: %s", image_path, str(e))
            self.log("ERROR", f"没有权限替换文件 {os.path.basename(image_path)}")
            self._cleanup_temp_file(temp_path)
            
        except (IOError, ValueError, OSError) as e:
            logger.error("保存PNG文件失败 %s: %s", image_path, str(e))
            self.log("ERROR", f"保存PNG文件 {os.path.basename(image_path)} 失败: {str(e)}")
            self._cleanup_temp_file(temp_path)

    def _cleanup_temp_file(self, temp_path):
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError as e:
                pass
    
    def _load_heic_exif_data(self, heif_file, image, image_path):
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        try:
            try:
                if heif_file.exif:
                    heif_exif = piexif.load(heif_file.exif)
                    exif_dict.update(heif_exif)
            except AttributeError as e:
                pass
        
        except (IOError, ValueError) as e:
            pass
        
        self._load_pil_exif_data(image, exif_dict)
        
        try:
            if 'exif' in image.info:
                info_exif = piexif.load(image.info['exif'])
                exif_dict.update(info_exif)
        except (KeyError, ValueError, TypeError) as e:
            pass
        
        try:
            with Image.open(image_path) as img:
                try:
                    pil_exif = img.getexif()
                except AttributeError:
                    pil_exif = None
                if pil_exif:
                    self._load_pil_exif_data_to_dict(pil_exif, exif_dict)
        except (IOError, OSError, ValueError) as e:
            pass
        
        return exif_dict
    
    def _load_pil_exif_data(self, image, exif_dict):
        try:
            try:
                pil_exif = image.getexif()
            except AttributeError:
                pil_exif = None
            if pil_exif:
                self._load_pil_exif_data_to_dict(pil_exif, exif_dict)
        except (IOError, OSError, ValueError, TypeError) as e:
            pass
    
    def _load_pil_exif_data_to_dict(self, pil_exif, exif_dict):
        tag_mapping = {
            270: ("0th", piexif.ImageIFD.ImageDescription),
            271: ("0th", piexif.ImageIFD.Make),
            272: ("0th", piexif.ImageIFD.Model),
            315: ("0th", 315),
            36867: ("Exif", piexif.ExifIFD.DateTimeOriginal),
            37378: ("Exif", piexif.ExifIFD.FNumber),
            37386: ("Exif", piexif.ExifIFD.FocalLength),
            42035: ("Exif", piexif.ExifIFD.LensMake),
            41988: ("Exif", piexif.ExifIFD.LensModel),
            42034: ("Exif", piexif.ExifIFD.LensSpecification),
        }
        
        for tag_id, (section, piexif_tag) in tag_mapping.items():
            if tag_id in pil_exif:
                try:
                    exif_dict[section][piexif_tag] = pil_exif[tag_id]
                except (KeyError, ValueError, TypeError) as e:
                    pass
        
    def _update_heic_exif_fields(self, exif_dict, image_path):

        updated_fields = []
        
        self._update_heic_basic_fields(exif_dict, updated_fields)
        self._update_heic_rating(exif_dict, updated_fields)
        self._update_heic_lens_info(exif_dict, updated_fields)
        self._update_heic_shoot_time(exif_dict, updated_fields, image_path)
        self._update_heic_gps_data(exif_dict, updated_fields)
        
        return updated_fields
    
    def _update_heic_basic_fields(self, exif_dict, updated_fields):

        if "0th" not in exif_dict:
            exif_dict["0th"] = {}
        
        field_mappings = [
            ('title', piexif.ImageIFD.ImageDescription, "标题: {}", 'utf-8'),
            ('author', 315, "作者: {}", 'utf-8'),
            ('subject', piexif.ImageIFD.XPSubject, "主题: {}", 'utf-16le'),
            ('copyright', piexif.ImageIFD.Copyright, "版权: {}", 'utf-8'),
            ('camera_brand', piexif.ImageIFD.Make, "相机品牌: {}", 'utf-8'),
            ('camera_model', piexif.ImageIFD.Model, "相机型号: {}", 'utf-8'),
        ]
        
        for config_key, ifd_key, format_str, encoding in field_mappings:
            value = self.exif_config.get(config_key)
            if value:
                try:
                    exif_dict["0th"][ifd_key] = value.encode(encoding)
                    updated_fields.append(format_str.format(value))
                except Exception as e:
                    self.log("ERROR", f"写入HEIC字段 {config_key} 失败: {str(e)}")
    
    def _update_heic_rating(self, exif_dict, updated_fields):
        rating = self.exif_config.get('rating')
        if rating:
            try:
                if "0th" not in exif_dict:
                    exif_dict["0th"] = {}
                
                rating_value = int(rating)
                exif_dict["0th"][piexif.ImageIFD.Rating] = rating_value
                updated_fields.append(f"评分: {rating}星")
            except (ValueError, TypeError) as e:
                self.log("ERROR", f"写入HEIC评分失败: {str(e)}")
    
    def _update_heic_lens_info(self, exif_dict, updated_fields):
        lens_brand = self.exif_config.get('lens_brand')
        lens_model = self.exif_config.get('lens_model')
        
        if not (lens_brand or lens_model):
            return
            
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        if lens_brand:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = lens_brand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {lens_brand}")
            except Exception as e:
                self.log("ERROR", f"写入HEIC镜头品牌失败: {str(e)}")
            
        if lens_model:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens_model.encode('utf-8')
                updated_fields.append(f"镜头型号: {lens_model}")
            except Exception as e:
                self.log("ERROR", f"写入HEIC镜头型号失败: {str(e)}")
    
    def _update_heic_shoot_time(self, exif_dict, updated_fields, image_path):
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time == 0:
            return
        
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        if shoot_time == 1:
            date_from_filename = self.get_date_from_filename(image_path)
            if date_from_filename:
                time_str = date_from_filename.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = time_str.encode('utf-8')
                updated_fields.append(f"文件名识别拍摄时间: {time_str}")
        else:
            if isinstance(shoot_time, str):
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = shoot_time.encode('utf-8')
                updated_fields.append(f"拍摄时间: {shoot_time}")
            else:
                self.log("WARNING", f"拍摄时间格式无效: {shoot_time}")
    
    def _update_heic_gps_data(self, exif_dict, updated_fields):
        if self.lat is not None and self.lon is not None:
            exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
            
            lat_dir = 'N' if self.lat >= 0 else 'S'
            lon_dir = 'E' if self.lon >= 0 else 'W'
            updated_fields.append(
                f"GPS坐标: {abs(self.lat):.6f}°{lat_dir}, {abs(self.lon):.6f}°{lon_dir}")
    
    def _save_heic_data(self, image, image_path, exif_dict, updated_fields):
        temp_path = image_path + ".tmp"
        try:
            self._clean_exif_for_heic(exif_dict)
            exif_bytes = piexif.dump(exif_dict)
            image.save(temp_path, format="HEIF", exif=exif_bytes)
            os.replace(temp_path, image_path)
            self.log("INFO", f"写入并复制 {os.path.basename(image_path)}")
        except (IOError, ValueError, OSError) as e:
            self.log("ERROR", f"写入EXIF数据失败: {str(e)}")
        finally:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

    def _clean_exif_for_heic(self, exif_dict):
        if not exif_dict:
            return
        
        valid_sections = ["0th", "Exif", "GPS", "1st", "thumbnail"]
        
        for section in list(exif_dict.keys()):
            if section not in valid_sections:
                exif_dict.pop(section, None)
                continue
                
            if isinstance(exif_dict[section], dict):
                for tag, value in list(exif_dict[section].items()):
                    if not self._is_valid_exif_tag(section, tag, value):
                        exif_dict[section].pop(tag, None)
                        
    def _is_valid_exif_tag(self, section, tag, value):
        try:
            if section == "0th":
                known_tags = [
                    piexif.ImageIFD.ImageDescription, piexif.ImageIFD.Make, piexif.ImageIFD.Model,
                    piexif.ImageIFD.DateTime, piexif.ImageIFD.Artist, piexif.ImageIFD.Copyright,
                    piexif.ImageIFD.XPTitle, piexif.ImageIFD.XPComment, piexif.ImageIFD.XPAuthor,
                    piexif.ImageIFD.XPKeywords, piexif.ImageIFD.XPSubject, piexif.ImageIFD.Rating,
                    315, 270, 271, 272, 306, 33432, 40093, 40094, 40095, 40096, 40097, 40098
                ]
            elif section == "Exif":
                known_tags = [
                    piexif.ExifIFD.DateTimeOriginal, piexif.ExifIFD.DateTimeDigitized,
                    piexif.ExifIFD.FNumber, piexif.ExifIFD.ExposureTime, piexif.ExifIFD.Flash,
                    piexif.ExifIFD.FocalLength, piexif.ExifIFD.ISOSpeedRatings, piexif.ExifIFD.PixelXDimension,
                    piexif.ExifIFD.PixelYDimension, piexif.ExifIFD.UserComment, piexif.ExifIFD.LensMake,
                    piexif.ExifIFD.LensModel, piexif.ExifIFD.LensSpecification, piexif.ExifIFD.BodySerialNumber,
                    piexif.ExifIFD.LensSerialNumber, piexif.ExifIFD.ShutterSpeedValue, piexif.ExifIFD.ApertureValue,
                    piexif.ExifIFD.BrightnessValue, piexif.ExifIFD.ExposureBiasValue, piexif.ExifIFD.MaxApertureValue,
                    piexif.ExifIFD.SubjectDistance, piexif.ExifIFD.MeteringMode, piexif.ExifIFD.LightSource,
                    piexif.ExifIFD.FlashEnergy, piexif.ExifIFD.SubjectArea, piexif.ExifIFD.ExposureMode,
                    piexif.ExifIFD.WhiteBalance, piexif.ExifIFD.DigitalZoomRatio, piexif.ExifIFD.FocalLengthIn35mmFilm,
                    piexif.ExifIFD.SceneCaptureType, piexif.ExifIFD.GainControl, piexif.ExifIFD.Contrast,
                    piexif.ExifIFD.Saturation, piexif.ExifIFD.Sharpness, piexif.ExifIFD.DeviceSettingDescription,
                    piexif.ExifIFD.SubjectDistanceRange, piexif.ExifIFD.ImageUniqueID,
                    36867, 36868, 37377, 37378, 37379, 37380, 37381, 37382, 37383, 37384, 37385, 37386, 37387, 37388, 37389, 37390, 37391, 37392, 37393, 37394, 37395, 37396, 37397, 41483, 41484, 41486, 41487, 41488, 41492, 41493, 41494, 41985, 41986, 41987, 41988, 41989, 41990, 41991, 41992, 41993, 41994, 41995, 41996, 42016, 42017, 42032, 42033, 42034, 42035, 42036, 42037, 42080, 42081, 42082, 42083, 42085, 42086, 42087, 42088, 42089, 42090, 42091, 42092, 42093, 42094, 42095, 42096, 42097, 42098, 42099
                ]
            elif section == "GPS":
                known_tags = [
                    piexif.GPSIFD.GPSVersionID, piexif.GPSIFD.GPSLatitudeRef, piexif.GPSIFD.GPSLatitude,
                    piexif.GPSIFD.GPSLongitudeRef, piexif.GPSIFD.GPSLongitude, piexif.GPSIFD.GPSAltitudeRef,
                    piexif.GPSIFD.GPSAltitude, piexif.GPSIFD.GPSTimeStamp, piexif.GPSIFD.GPSSatellites,
                    piexif.GPSIFD.GPSStatus, piexif.GPSIFD.GPSMeasureMode, piexif.GPSIFD.GPSDOP,
                    piexif.GPSIFD.GPSSpeedRef, piexif.GPSIFD.GPSSpeed, piexif.GPSIFD.GPSTrackRef,
                    piexif.GPSIFD.GPSTrack, piexif.GPSIFD.GPSImgDirectionRef, piexif.GPSIFD.GPSImgDirection,
                    piexif.GPSIFD.GPSMapDatum, piexif.GPSIFD.GPSDestLatitudeRef, piexif.GPSIFD.GPSDestLatitude,
                    piexif.GPSIFD.GPSDestLongitudeRef, piexif.GPSIFD.GPSDestLongitude, piexif.GPSIFD.GPSDestBearingRef,
                    piexif.GPSIFD.GPSDestBearing, piexif.GPSIFD.GPSDestDistanceRef, piexif.GPSIFD.GPSDestDistance,
                    piexif.GPSIFD.GPSProcessingMethod, piexif.GPSIFD.GPSAreaInformation, piexif.GPSIFD.GPSDateStamp,
                    piexif.GPSIFD.GPSDifferential, piexif.GPSIFD.GPSHPositioningError,
                    0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31
                ]
            else:
                return False
                
            if tag not in known_tags:
                return False
                
            if value is None or value == "":
                return False
                
            return True
            
        except (AttributeError, KeyError, TypeError):
            return False
    
    def _process_heic_format(self, image_path):
        if not PILLOW_HEIF_AVAILABLE:
            self.log("ERROR", f"处理 {os.path.basename(image_path)} 需要 pillow-heif")
            return
        
        try:
            if not self._validate_heic_file(image_path):
                self.log("WARNING", f"文件 {os.path.basename(image_path)} 不是有效的HEIC格式，跳过处理")
                return
                
            register_heif_opener()
            heif_file = open_heif(image_path)
            
            if hasattr(heif_file, 'to_pillow'):
                image = heif_file.to_pillow()
            else:
                image = Image.open(image_path)
            
            exif_dict = self._load_heic_exif_data(heif_file, image, image_path)
            
            updated_fields = self._update_heic_exif_fields(exif_dict, image_path)
            
            if updated_fields:
                self._save_heic_data(image, image_path, exif_dict, updated_fields)
            else:
                self.log("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改\n\n")
                
        except (IOError, OSError, ValueError, TypeError, ImportError) as e:
            self.log("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    def _validate_heic_file(self, image_path):
        try:
            with open(image_path, 'rb') as f:
                header = f.read(12)
                
            if len(header) < 12:
                return False
                
            if header[:4] != b'ftyp':
                return False
                
            valid_brand_types = [
                b'mif1', b'mif2', b'mif3', b'heic', b'heix', b'hevc', 
                b'hevx', b'hev1', b'hev2', b'hev3', b'hev4', b'hev5', b'hev6',
                b'hev7', b'hev8', b'hev9', b'hev1', b'hev2', b'hev3', b'hev4', b'hev5'
            ]
            
            brand = header[4:8]
            if brand in valid_brand_types:
                return True
                
            version_brand = header[8:12]
            if version_brand[1:4] in [b'heic', b'heix', b'hevc']:
                return True
                
            return False
            
        except (IOError, OSError):
            return False

    def _process_video_format(self, image_path):
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext == '.avi':
            if self._is_riff_avi(image_path):
                self.log("WARNING", f"文件 {os.path.basename(image_path)} 是RIFF格式的AVI文件，"
                                   "不支持EXIF信息写入。")
                return 'skipped'
            else:
                self.log("INFO", f"正在处理非RIFF格式的AVI文件: {os.path.basename(image_path)}")
        
        if file_ext in ('.mov', '.mp4', '.avi', '.mkv'):
            result = self._process_video_with_exiftool(image_path)
            return 'success' if result else 'failed'
        else:
            self.log("WARNING", f"不支持的视频格式: {file_ext}")
            return 'skipped'
    
    def _handle_non_ascii_path(self, image_path):
        temp_file_path = None
        temp_dir = None
        original_file_path = image_path
        
        has_non_ascii = any(ord(char) > 127 for char in image_path)
        
        if has_non_ascii:
            temp_dir = tempfile.mkdtemp(prefix="exiftool_temp_")
            temp_file_path = os.path.join(temp_dir, os.path.basename(image_path))
            shutil.copy2(image_path, temp_file_path)
            image_path = temp_file_path
        
        return image_path, original_file_path, temp_file_path, temp_dir
    
    def _prepare_exiftool_command(self, original_file_path):
        exiftool_path = get_resource_path('_internal/resources/exiftool/exiftool.exe')
        cmd_parts = [exiftool_path, "-overwrite_original"]
        updated_fields = []
        
        camera_brand = self.exif_config.get('camera_brand')
        camera_model = self.exif_config.get('camera_model')
        shoot_time = self.exif_config.get('shoot_time', 0)
        
        if camera_brand:
            cmd_parts.append(f'-Make="{camera_brand}"')
            updated_fields.append(f"相机品牌: {camera_brand}")
        
        if camera_model:
            cmd_parts.append(f'-Model="{camera_model}"')
            updated_fields.append(f"相机型号: {camera_model}")
        
        if self.lat is not None and self.lon is not None:
            self._add_gps_to_command(cmd_parts, updated_fields)
        
        if shoot_time != 0:
            self._add_time_to_command(cmd_parts, updated_fields, original_file_path, shoot_time)
        
        return cmd_parts, updated_fields, exiftool_path
    
    def _add_gps_to_command(self, cmd_parts, updated_fields):
        lat_dms = self.decimal_to_dms(self.lat)
        lon_dms = self.decimal_to_dms(self.lon)
        cmd_parts.append(f'-GPSLatitude="{lat_dms}"')
        cmd_parts.append(f'-GPSLongitude="{lon_dms}"')
        cmd_parts.append('-GPSLatitudeRef=N' if self.lat >= 0 else '-GPSLatitudeRef=S')
        cmd_parts.append('-GPSLongitudeRef=E' if self.lon >= 0 else '-GPSLongitudeRef=W')
        cmd_parts.append(f'-GPSCoordinates="{self.lat}, {self.lon}"')
        updated_fields.append(f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
    
    def _add_time_to_command(self, cmd_parts, updated_fields, original_file_path, shoot_time):

        if shoot_time == 1:
            date_from_filename = self.get_date_from_filename(original_file_path)
            if date_from_filename:
                self._add_time_fields(cmd_parts, date_from_filename)
                updated_fields.append(f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')} (已调整为UTC时间)")
            else:
                self.log("WARNING", f"无法从文件名提取时间: {os.path.basename(original_file_path)}")
        else:
            try:
                datetime.strptime(shoot_time, "%Y:%m:%d %H:%M:%S")
                local_time = datetime.strptime(shoot_time, "%Y:%m:%d %H:%M:%S")
                self._add_time_fields(cmd_parts, local_time)
                updated_fields.append(f"拍摄时间: {shoot_time} (已调整为UTC时间)")
            except (ValueError, TypeError):
                self.log("ERROR", f"拍摄时间格式无效: {shoot_time}，请使用 YYYY:MM:DD HH:MM:SS 格式")
    
    def _add_time_fields(self, cmd_parts, datetime_obj):

        local_time = datetime_obj
        utc_time = local_time - timedelta(hours=8)
        actual_write_time = utc_time.strftime("%Y:%m:%d %H:%M:%S")
        timezone_suffix = "+00:00"
        cmd_parts.extend([
            f'-CreateDate={actual_write_time}{timezone_suffix}',
            f'-CreationDate={actual_write_time}{timezone_suffix}',
            f'-MediaCreateDate={actual_write_time}{timezone_suffix}',
            f'-DateTimeOriginal={actual_write_time}{timezone_suffix}'
        ])
    
    def _cleanup_temp_resources(self, temp_file_path, temp_dir, original_file_path, current_path):

        if temp_file_path and os.path.exists(temp_file_path) and original_file_path != current_path:
            try:
                shutil.copy2(temp_file_path, original_file_path)
            except (IOError, OSError) as e:
                self.log("ERROR", f"复制文件回原始路径失败: {str(e)}")
        
        self._cleanup_temp_file(temp_file_path)
        
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except OSError as e:
                self.log("WARNING", f"无法删除临时目录: {str(e)}")
    
    def _process_video_with_exiftool(self, image_path):

        if not os.path.exists(image_path):
            self.log("ERROR", f"文件不存在: {image_path}")
            return False
        
        image_path, original_file_path, temp_file_path, temp_dir = self._handle_non_ascii_path(image_path)
        file_path_normalized = image_path.replace('\\', '/')
        
        try:
            cmd_parts, updated_fields, exiftool_path = self._prepare_exiftool_command(original_file_path)
            cmd_parts.append(file_path_normalized)
            
            result = subprocess.run(cmd_parts, capture_output=True, text=False, shell=False, check=False, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode != 0:
                error_msg = self._decode_subprocess_output(result.stderr) if result.stderr else "未知错误"
                
                if "Can't currently write RIFF AVI files" in error_msg or "RIFF AVI files" in error_msg:
                    self.log("WARNING", f"文件 {os.path.basename(original_file_path)} 是RIFF格式的AVI文件，"
                                       "不支持EXIF信息写入。")
                    return False
                
                if "FileName encoding must be specified" in error_msg:
                    self.log("WARNING", f"文件名包含非ASCII字符，建议重命名文件后重试: {os.path.basename(original_file_path)}")
                    return False
                
                self.log("ERROR", f"写入EXIF数据失败: {error_msg}")
                return False

            if updated_fields:
                self.log("INFO", f"写入并复制 {os.path.basename(original_file_path)}")
            
            verify_cmd = [exiftool_path, '-CreateDate', '-CreationDate', '-MediaCreateDate', '-DateTimeOriginal', file_path_normalized]
            subprocess.run(verify_cmd, capture_output=True, text=False, shell=False, check=False, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            return True
            
        except (IOError, ValueError, OSError, subprocess.SubprocessError) as e:
            self.log("ERROR", f"执行exiftool命令时出错: {str(e)}")
            return False
        finally:
            self._cleanup_temp_resources(temp_file_path, temp_dir, original_file_path, image_path)

    def _process_raw_format(self, image_path):
        exiftool_path = self._validate_raw_processing(image_path)
        if not exiftool_path:
            return
        
        exif_data, updated_fields = self._prepare_raw_exif_data(image_path)
        if not exif_data:
            self.log("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            return
        
        self._execute_exiftool_command(exiftool_path, exif_data, image_path, updated_fields)
    
    def _validate_raw_processing(self, image_path):
        if not os.path.exists(image_path):
            self.log.emit("ERROR", f"文件不存在: {os.path.basename(image_path)}")
            return None
        
        exiftool_path = os.path.join(os.path.dirname(__file__), "resources", "exiftool", "exiftool.exe")
        if not os.path.exists(exiftool_path):
            self.log.emit("ERROR", "exiftool工具不存在，无法处理RAW格式文件")
            return None
        
        return exiftool_path
    
    def _prepare_raw_exif_data(self, image_path):
        exif_data = {}
        updated_fields = []
        
        self._prepare_raw_shoot_time(exif_data, updated_fields, image_path)
        self._prepare_raw_basic_fields(exif_data, updated_fields)
        self._prepare_raw_gps_data(exif_data, updated_fields)
        
        return exif_data, updated_fields
    
    def _prepare_raw_shoot_time(self, exif_data, updated_fields, image_path):
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time != 0:
            if shoot_time == 1:
                date_from_filename = self.get_date_from_filename(image_path)
                if date_from_filename:
                    time_str = date_from_filename.strftime('%Y:%m:%d %H:%M:%S')
                    self._add_time_fields_to_data(exif_data, time_str)
                    updated_fields.append(f"拍摄时间: {time_str}")
            else:
                try:
                    datetime.strptime(shoot_time, "%Y:%m:%d %H:%M:%S")
                    self._add_time_fields_to_data(exif_data, shoot_time)
                    updated_fields.append(f"拍摄时间: {shoot_time}")
                except ValueError:
                    self.log.emit("ERROR", f"拍摄时间格式无效: {shoot_time}")
    
    def _add_time_fields_to_data(self, exif_data, time_str):

        exif_data['DateTimeOriginal'] = time_str
        exif_data['CreateDate'] = time_str
        exif_data['ModifyDate'] = time_str
    
    def _prepare_raw_basic_fields(self, exif_data, updated_fields):

        field_mappings = [
            ('title', 'ImageDescription', '标题: {}'),
            ('author', 'Artist', '作者: {}'),
            ('copyright', 'Copyright', '版权: {}'),
            ('camera_brand', 'Make', '相机品牌: {}'),
            ('camera_model', 'Model', '相机型号: {}'),
            ('lens_brand', 'LensMake', '镜头品牌: {}'),
            ('lens_model', 'LensModel', '镜头型号: {}')
        ]
        
        for config_key, exif_key, format_str in field_mappings:
            attr_value = self.exif_config.get(config_key)
            if attr_value:
                exif_data[exif_key] = attr_value
                updated_fields.append(format_str.format(attr_value))
    
    def _prepare_raw_gps_data(self, exif_data, updated_fields):

        if self.lat is not None and self.lon is not None:
            exif_data['GPSLatitude'] = self.lat
            exif_data['GPSLongitude'] = self.lon
            updated_fields.append(f"GPS坐标: {self.lat:.6f}, {self.lon:.6f}")
    
    def _execute_exiftool_command(self, exiftool_path, exif_data, image_path, updated_fields):

        commands = self._build_exiftool_commands(exif_data)
        cmd = [exiftool_path, "-overwrite_original"] + commands + [image_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30, check=False, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode == 0:
                if updated_fields:
                    self.log("INFO", f"成功写入 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
                else:
                    self.log("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            else:
                error_msg = self._decode_subprocess_output(result.stderr) if result.stderr else "未知错误"
                self.log("ERROR", f"写入 {os.path.basename(image_path)} 失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            self.log("ERROR", f"处理 {os.path.basename(image_path)} 超时")
        except (subprocess.SubprocessError, IOError, OSError) as e:
            self.log("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")
    
    def _build_exiftool_commands(self, exif_data):
        commands = []
        for key, value in exif_data.items():
            if isinstance(value, str):
                commands.append(f'-{key}="{value}"')
            else:
                commands.append(f'-{key}={value}')
        return commands

    def stop(self):

        self.requestInterruption()
        self.log("WARNING", "正在取消写入EXIF数据操作...")
        if self.isRunning():
            self.wait(1000)

    def _is_riff_avi(self, file_path):
        try:
            with open(file_path, 'rb') as f:
                header = f.read(12)
                if len(header) < 12:
                    return False
                
                if header[:4] == b'RIFF' and header[8:12] == b'AVI ':
                    return True
                
                if header[:4] == b'RIFF' and header[8:12] != b'AVI ':
                    riff_type = header[8:]
                    return any(marker in riff_type for marker in [b'AVIX', b'AVI '])
                
                return False
                
        except (IOError, OSError) as e:
            self.log("DEBUG", f"检测AVI格式时出错 {os.path.basename(file_path)}: {str(e)}")
            return False

    def decimal_to_dms(self, decimal):
        try:
            decimal = abs(decimal)
            
            degrees = int(decimal)
            minutes_decimal = (decimal - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            
            dms_str = f"{degrees} deg {minutes}' {seconds:.2f}\""
            
            return dms_str
        except (ValueError, TypeError, ZeroDivisionError) as e:
            self.log("ERROR", f"坐标转换错误: {str(e)}")
            return str(decimal)

    def _create_gps_data(self, lat, lon):
        gps_dict = {}
        
        lat_deg = int(abs(lat))
        lat_min_decimal = (abs(lat) - lat_deg) * 60
        lat_min = int(lat_min_decimal)
        lat_sec = int((lat_min_decimal - lat_min) * 100)
        gps_dict[piexif.GPSIFD.GPSLatitude] = [(lat_deg, 1), (lat_min, 1), (lat_sec, 100)]
        gps_dict[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
        
        lon_deg = int(abs(lon))
        lon_min_decimal = (abs(lon) - lon_deg) * 60
        lon_min = int(lon_min_decimal)
        lon_sec = int((lon_min_decimal - lon_min) * 100)
        gps_dict[piexif.GPSIFD.GPSLongitude] = [(lon_deg, 1), (lon_min, 1), (lon_sec, 100)]
        gps_dict[piexif.GPSIFD.GPSLongitudeRef] = b'E' if lon >= 0 else b'W'
        
        current_time = datetime.now()
        gps_dict[piexif.GPSIFD.GPSDateStamp] = current_time.strftime("%Y:%m:%d")
        gps_dict[piexif.GPSIFD.GPSTimeStamp] = [
            (current_time.hour, 1),
            (current_time.minute, 1),
            (current_time.second, 1)
        ]
        
        gps_dict[piexif.GPSIFD.GPSProcessingMethod] = b'GPS'
        
        return gps_dict

    def get_date_from_filename(self, image_path):

        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        
        patterns = [
            r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})',
            r'(\d{4})(\d{2})(\d{2})(?:[-_\.\/\s=](\d{2})(\d{2})(\d{2}))?',
            r'(\d{4})[-_=](\d{1,2})[-_=](\d{1,2}).*?[-_\s](\d{6})',
            r'(\d{4})[-_=](\d{1,2})[-_=](\d{1,2}).*?(\d{6})',
            r'(\d{4})[-_\.\/\s=](\d{1,2})[-_\.\/\s=](\d{1,2})(?:[-_\.\/\s=](\d{1,2})[-_\.\/\s=]?(\d{1,2})[-_\.\/\s=]?(\d{1,2}))?',
            r'(\d{4})年(\d{1,2})月(\d{1,2})日(?:(\d{1,2})时(\d{1,2})分(\d{1,2})秒)?'
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, name_without_ext)
            if match:
                try:
                    groups = match.groups()
                    
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                    
                    if not (1900 <= year <= 2100 and 1 <= month <= 12):
                        continue
                    if month in [4, 6, 9, 11] and day > 30:
                        continue
                    if month == 2:
                        is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
                        if day > (29 if is_leap else 28):
                            continue
                    elif day > 31:
                        continue
                    
                    hour, minute, second = 0, 0, 0
                    
                    if i == 0:
                        if len(groups) >= 6:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 1:
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 2 or i == 3:
                        if len(groups) >= 4 and groups[3] and len(groups[3]) == 6:
                            full_time = groups[3]
                            hour = int(full_time[0:2])
                            minute = int(full_time[2:4])
                            second = int(full_time[4:6])
                    elif i == 4:
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 5:
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    
                    if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                        return datetime(year, month, day, hour, minute, second)
                except (ValueError, TypeError, IndexError):
                    continue
        
        return None
