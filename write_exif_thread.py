import os
import re
import time
import subprocess
import shutil
import tempfile
import logging
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
                raise TypeError("日志级别和消息必须是字符串类型")
            
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
                error_msg = f"日志记录失败: {str(e)}"
                logger.error(error_msg)
            except:
                pass
            
    def __init__(self, folders_dict, exif_config=None, target_folder=None):
        super().__init__()
        self.folders_dict = {item['path']: item['include_sub'] for item in folders_dict}
        self.exif_config = exif_config or {}
        self.target_folder = target_folder or os.path.expanduser("~/Desktop/Processed_Images")
        self.lat, self.lon = None, None
        position = self.exif_config.get('position', '')
        if position and ',' in position:
            try:
                self.lat, self.lon = map(float, position.split(','))
                if not (-90 <= self.lat <= 90) or not (-180 <= self.lon <= 180):
                    self.lat, self.lon = None, None
            except ValueError as e:
                self.log("ERROR", f"解析坐标值失败: {str(e)}")
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
                self.process_image(path)
                success_count += 1
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
        self.log("DEBUG", "="*3+"LeafView © 2025 Yangshengzhou.All Rights Reserved"+"="*3)

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
        
        logger.info("共收集到图像文件")
        return image_paths
    
    def _process_folder_with_subfolders(self, folder_path, image_extensions, image_paths):
        try:
            for root, _, files in os.walk(folder_path):
                if self.isInterruptionRequested():
                    break
                self._process_folder_content(root, files, image_extensions, image_paths)
        except (OSError, IOError) as e:
            error_msg = f"遍历文件夹时出错: {str(e)}"
            logger.error(error_msg)
            self.log("ERROR", error_msg)
    
    def _process_folder_without_subfolders(self, folder_path, image_extensions, image_paths):
        try:
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                self._process_folder_content(folder_path, files, image_extensions, image_paths)
        except PermissionError as e:
            error_msg = f"没有权限访问文件夹 {folder_path}: {str(e)}"
            logger.error(error_msg)
            self.log("ERROR", f"没有权限访问文件夹 {os.path.basename(folder_path)}")
        except (OSError, IOError) as e:
            error_msg = f"列出文件夹 {folder_path} 内容时出错: {str(e)}"
            logger.error(error_msg)
            self.log("ERROR", f"列出文件夹 {os.path.basename(folder_path)} 内容时出错: {str(e)}")
    
    def _process_folder_content(self, root, files, image_extensions, image_paths):
        try:
            image_paths.extend(
                os.path.join(root, file)
                for file in files
                if file.lower().endswith(image_extensions)
            )
        except (OSError, IOError) as e:
            error_msg = f"处理文件夹 {root} 内容时出错: {str(e)}"
            logger.error(error_msg)
            self.log("ERROR", error_msg)

    def process_image(self, image_path):
        try:
            if self.isInterruptionRequested():
                self.log("WARNING", f"处理被取消: {os.path.basename(image_path)}")
                return
            
            if not self._validate_file(image_path):
                return
            
            target_path = self._copy_to_target(image_path)
            if not target_path:
                return
            
            file_ext = os.path.splitext(image_path)[1].lower()
            logger.debug("处理文件: %s, 扩展名: %s", target_path, file_ext)
            
            format_handler = self._get_format_handler(file_ext)
            if format_handler:
                format_handler(target_path)
            else:
                logger.warning("不支持的文件格式: %s", file_ext)
                self.log("WARNING", f"不支持的文件格式: {file_ext}")

        except (IOError, ValueError, TypeError, OSError) as e:
            logger.error("处理文件 %s 时出错: %s", image_path, str(e))
            self._handle_processing_error(image_path, e)
    
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
            error_msg = f"文件不可写: {os.path.basename(image_path)}"
            logger.error("文件不可写: %s", image_path)
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
            logger.warning("加载EXIF数据失败 %s: %s，将创建新的EXIF数据", image_path, str(e))
            return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    def _update_exif_fields(self, exif_dict, image_path):
        if self.isInterruptionRequested():
            return []
            
        updated_fields = []
        
        try:
            self._ensure_exif_sections(exif_dict)
            
            self._update_basic_fields(exif_dict, updated_fields)
            
            self._update_special_fields(exif_dict, image_path, updated_fields)
            
            return self._check_update_result(updated_fields, image_path)
            
        except (IOError, ValueError, OSError) as e:
            error_msg = f"处理EXIF数据时出错 {os.path.basename(image_path)}: {str(e)}"
            logger.error("处理EXIF数据时出错 %s: %s", image_path, str(e))
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
                    logger.error(f"写入基本字段 {config_key} 失败: {str(e)}")
        
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        lens_brand = self.exif_config.get('lens_brand')
        if lens_brand:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = lens_brand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {lens_brand}")
                logger.debug(f"成功写入镜头品牌: {lens_brand}")
            except Exception as e:
                logger.error(f"写入镜头品牌失败: {str(e)}")
        
        lens_model = self.exif_config.get('lens_model')
        if lens_model:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens_model.encode('utf-8')
                updated_fields.append(f"镜头型号: {lens_model}")
                logger.debug(f"成功写入镜头型号: {lens_model}")
            except Exception as e:
                logger.error(f"写入镜头型号失败: {str(e)}")
    
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
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            logger.info("成功写入EXIF数据到 %s", image_path)
            self.log("INFO", f"写入并复制 {os.path.basename(image_path)}")
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
                logger.debug("清理临时文件失败: %s", str(e))
    
    def _load_heic_exif_data(self, heif_file, image, image_path):
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        try:
            try:
                if heif_file.exif:
                    heif_exif = piexif.load(heif_file.exif)
                    exif_dict.update(heif_exif)
            except AttributeError as e:
                logger.debug("HEIF文件缺少exif属性: %s", str(e))
        except (IOError, ValueError) as e:
            logger.debug("加载HEIF EXIF数据失败: %s", str(e))
        
        self._load_pil_exif_data(image, exif_dict)
        
        try:
            if 'exif' in image.info:
                info_exif = piexif.load(image.info['exif'])
                exif_dict.update(info_exif)
        except (KeyError, ValueError, TypeError) as e:
            logger.debug("从image.info加载EXIF失败: %s", str(e))
        
        try:
            with Image.open(image_path) as img:
                try:
                    pil_exif = img.getexif()
                except AttributeError:
                    pil_exif = None
                if pil_exif:
                    self._load_pil_exif_data_to_dict(pil_exif, exif_dict)
        except (IOError, OSError, ValueError) as e:
            logger.debug("再次打开文件加载EXIF失败: %s", str(e))
        
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
            logger.debug("加载PIL EXIF数据失败: %s", str(e))
    
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
                    logger.debug("处理PIL EXIF标签 %s 失败: %s", tag_id, str(e))
    
    def _update_heic_exif_fields(self, exif_dict, image_path):
        """更新HEIF文件的EXIF字段
        
        Args:
            exif_dict: EXIF数据字典
            image_path: 图像文件路径
            
        Returns:
            list: 更新的字段列表
        """
        updated_fields = []
        
        self._update_heic_basic_fields(exif_dict, updated_fields)
        self._update_heic_rating(exif_dict, updated_fields)
        self._update_heic_lens_info(exif_dict, updated_fields)
        self._update_heic_shoot_time(exif_dict, updated_fields, image_path)
        self._update_heic_gps_data(exif_dict, updated_fields)
        
        return updated_fields
    
    def _update_heic_basic_fields(self, exif_dict, updated_fields):
        """更新HEIF文件的基本EXIF字段
        
        Args:
            exif_dict: EXIF数据字典
            updated_fields: 更新字段列表
        """
        # 确保基本EXIF部分存在
        if "0th" not in exif_dict:
            exif_dict["0th"] = {}
        
        # 使用exif_config而不是直接获取属性
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
                    logger.error(f"写入HEIC字段 {config_key} 失败: {str(e)}")
    
    def _update_heic_rating(self, exif_dict, updated_fields):
        rating = self.exif_config.get('rating')
        if rating:
            try:
                # 确保0th部分存在
                if "0th" not in exif_dict:
                    exif_dict["0th"] = {}
                
                # 将评分转换为整数并写入
                rating_value = int(rating)
                exif_dict["0th"][piexif.ImageIFD.Rating] = rating_value
                updated_fields.append(f"评分: {rating}星")
            except (ValueError, TypeError) as e:
                logger.error(f"写入HEIC评分失败: {str(e)}")
    
    def _update_heic_lens_info(self, exif_dict, updated_fields):
        lens_brand = self.exif_config.get('lens_brand')
        lens_model = self.exif_config.get('lens_model')
        
        if not (lens_brand or lens_model):
            return
            
        # 确保Exif部分存在
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        # 写入镜头品牌
        if lens_brand:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = lens_brand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {lens_brand}")
            except Exception as e:
                logger.error(f"写入HEIC镜头品牌失败: {str(e)}")
            
        # 写入镜头型号
        if lens_model:
            try:
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = lens_model.encode('utf-8')
                updated_fields.append(f"镜头型号: {lens_model}")
            except Exception as e:
                logger.error(f"写入HEIC镜头型号失败: {str(e)}")
    
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
                logger.warning("拍摄时间格式无效: %s", shoot_time)
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
    
    def _process_heic_format(self, image_path):
        """处理HEIF格式图像文件"""
        if not PILLOW_HEIF_AVAILABLE:
            self.log("ERROR", f"处理 {os.path.basename(image_path)} 需要 pillow-heif")
            return
        
        try:
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

    def _process_video_format(self, image_path):
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext in ('.mov', '.mp4', '.avi', '.mkv'):
            self._process_video_with_exiftool(image_path)
        else:
            self.log("WARNING", f"不支持的视频格式: {file_ext}")
    
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
        exiftool_path = get_resource_path('resources/exiftool/exiftool.exe')
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
        """向命令中添加时间信息"""
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
        """添加时间相关的字段到命令中"""
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
        """清理临时资源"""
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
        """使用exiftool处理视频文件的EXIF数据"""
        if not os.path.exists(image_path):
            self.log("ERROR", f"文件不存在: {image_path}")
            return False
        
        image_path, original_file_path, temp_file_path, temp_dir = self._handle_non_ascii_path(image_path)
        file_path_normalized = image_path.replace('\\', '/')
        
        try:
            cmd_parts, updated_fields, exiftool_path = self._prepare_exiftool_command(original_file_path)
            cmd_parts.append(file_path_normalized)
            
            result = subprocess.run(cmd_parts, capture_output=True, text=False, shell=False, check=False)
            
            if result.returncode != 0:
                error_msg = result.stderr.decode('utf-8', errors='replace') if result.stderr else "未知错误"
                self.log("ERROR", f"写入EXIF数据失败: {error_msg}")
                return False

            if updated_fields:
                self.log("INFO", f"写入并复制 {os.path.basename(original_file_path)}")
            
            verify_cmd = [exiftool_path, '-CreateDate', '-CreationDate', '-MediaCreateDate', '-DateTimeOriginal', file_path_normalized]
            subprocess.run(verify_cmd, capture_output=True, text=False, shell=False, check=False)
            
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
        """准备RAW文件的EXIF数据
        
        Args:
            image_path: 要处理的文件路径
            
        Returns:
            tuple: (exif_data字典, updated_fields列表)
        """
        exif_data = {}
        updated_fields = []
        
        self._prepare_raw_shoot_time(exif_data, updated_fields, image_path)
        
        self._prepare_raw_basic_fields(exif_data, updated_fields)
        
        self._prepare_raw_gps_data(exif_data, updated_fields)
        
        return exif_data, updated_fields
    
    def _prepare_raw_shoot_time(self, exif_data, updated_fields, image_path):
        """准备RAW文件的拍摄时间数据
        
        Args:
            exif_data: EXIF数据字典
            updated_fields: 更新字段列表
            image_path: 文件路径
        """
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
        """向EXIF数据添加时间相关字段
        
        Args:
            exif_data: EXIF数据字典
            time_str: 时间字符串
        """
        exif_data['DateTimeOriginal'] = time_str
        exif_data['CreateDate'] = time_str
        exif_data['ModifyDate'] = time_str
    
    def _prepare_raw_basic_fields(self, exif_data, updated_fields):
        """准备RAW文件的基本EXIF字段
        
        Args:
            exif_data: EXIF数据字典
            updated_fields: 更新字段列表
        """
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
        """准备RAW文件的GPS数据
        
        Args:
            exif_data: EXIF数据字典
            updated_fields: 更新字段列表
        """
        if self.lat is not None and self.lon is not None:
            exif_data['GPSLatitude'] = self.lat
            exif_data['GPSLongitude'] = self.lon
            updated_fields.append(f"GPS坐标: {self.lat:.6f}, {self.lon:.6f}")
    
    def _execute_exiftool_command(self, exiftool_path, exif_data, image_path, updated_fields):
        """执行exiftool命令更新元数据
        
        Args:
            exiftool_path: exiftool可执行文件路径
            exif_data: 要更新的EXIF数据字典
            image_path: 目标文件路径
            updated_fields: 更新字段列表
        """
        commands = self._build_exiftool_commands(exif_data)
        cmd = [exiftool_path, "-overwrite_original"] + commands + [image_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30, check=False)
            
            if result.returncode == 0:
                if updated_fields:
                    self.log("INFO", f"成功写入 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
                else:
                    self.log("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            else:
                error_msg = result.stderr.decode('utf-8', errors='replace') if result.stderr else "未知错误"
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
        """
        请求停止线程
        """
        self.requestInterruption()
        self.log("INFO", "正在取消操作...")
        if self.isRunning():
            self.wait(1000)

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
        def decimal_to_piexif_dms(decimal):
            degrees = int(abs(decimal))
            minutes_decimal = (abs(decimal) - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            return [(degrees, 1), (minutes, 1), (int(seconds * 100), 100)]
        
        gps_dict = {}
        
        gps_dict[piexif.GPSIFD.GPSLatitude] = decimal_to_piexif_dms(abs(lat))
        gps_dict[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
        
        gps_dict[piexif.GPSIFD.GPSLongitude] = decimal_to_piexif_dms(abs(lon))
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
        """
        从文件名提取日期时间信息
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            datetime: 提取的日期时间对象，失败返回None
        """
        name_without_ext = os.path.splitext(os.path.basename(image_path))[0]
        
        # 基础正则表达式模式集合，确保中文文件名兼容性
        patterns = [
            # 1. 年月日时分秒连续数字格式 (20240629143847)
            r'(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})',
            # 2. 年月日连续，时分秒可选 (20240629_143847 或 20240629)
            r'(\d{4})(\d{2})(\d{2})(?:[-_\.\/\s](\d{2})(\d{2})(\d{2}))?',
            # 3. 通用分隔符的年月日，时分秒可选 (支持各种分隔符：-、_、.、/、空格等)
            r'(\d{4})[-_\.\/\s](\d{1,2})[-_\.\/\s](\d{1,2})(?:[-_\.\/\s](\d{1,2})[-_\.\/\s]?(\d{1,2})[-_\.\/\s]?(\d{1,2}))?',
            # 4. 中文混合格式，处理年_月_日_星期_时分秒 (上海2024_06_29_周六_143847留念2)
            r'(\d{4})[_-](\d{1,2})[_-](\d{1,2}).*?(\d{6})',
            # 5. 中文年月日格式 (2024年6月29日14时38分47秒)
            r'(\d{4})年(\d{1,2})月(\d{1,2})日(?:(\d{1,2})时(\d{1,2})分(\d{1,2})秒)?'
        ]
        
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, name_without_ext)
            if match:
                try:
                    # 获取位置捕获组
                    groups = match.groups()
                    
                    # 提取年月日（所有模式的前三个捕获组）
                    year = int(groups[0])
                    month = int(groups[1])
                    day = int(groups[2])
                    
                    # 增加日期有效性检查
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
                    
                    # 初始化时间为0
                    hour, minute, second = 0, 0, 0
                    
                    # 根据不同模式处理时间信息
                    if i == 0:  # 模式1: 连续数字 (年月日时分秒)
                        if len(groups) >= 6:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 1:  # 模式2: 年月日连续，时分秒可选
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 2:  # 模式3: 通用分隔符
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    elif i == 3:  # 模式4: 中文混合格式，处理连续6位时间
                        if len(groups) >= 4 and groups[3] and len(groups[3]) == 6:
                            full_time = groups[3]
                            hour = int(full_time[0:2])
                            minute = int(full_time[2:4])
                            second = int(full_time[4:6])
                    elif i == 4:  # 模式5: 中文年月日格式
                        if len(groups) >= 6 and groups[3] and groups[4] and groups[5]:
                            hour = int(groups[3])
                            minute = int(groups[4])
                            second = int(groups[5])
                    
                    # 检查时间有效性
                    if 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59:
                        return datetime(year, month, day, hour, minute, second)
                except (ValueError, TypeError, IndexError):
                    continue
        
        return None
