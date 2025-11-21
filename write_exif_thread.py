import os
import re
import time
import subprocess
import shutil
import tempfile
import logging
from concurrent.futures import as_completed, ThreadPoolExecutor
from datetime import datetime, timedelta

import piexif
from PIL import Image, PngImagePlugin
from PyQt6.QtCore import QThread, pyqtSignal

from common import detect_media_type, get_resource_path

# 配置日志记录
logger = logging.getLogger(__name__)


class WriteExifThread(QThread):
    
    progress_updated = pyqtSignal(int)
    finished_conversion = pyqtSignal()
    log_signal = pyqtSignal(str, str)

    def __init__(self, folders_dict, title='', author='', subject='', rating='', copyright='',
                 position='', shoot_time='', camera_brand=None, camera_model=None, lens_brand=None, lens_model=None):
        super().__init__()
        self.folders_dict = {item['path']: item['include_sub'] for item in folders_dict}
        self.title = title
        self.author = author
        self.subject = subject
        self.rating = rating
        self.copyright = copyright
        self.shoot_time = shoot_time
        self.camera_brand = camera_brand
        self.camera_model = camera_model
        self.lens_brand = lens_brand
        self.lens_model = lens_model
        self._stop_requested = False
        self.lat = None
        self.lon = None

        if position and ',' in position:
            try:
                self.lat, self.lon = map(float, position.split(','))
                if not (-90 <= self.lat <= 90) or not (-180 <= self.lon <= 180):
                    self.lat, self.lon = None, None
            except ValueError:
                pass

    def run(self):
        total_files = 0
        success_count = 0
        error_count = 0
        
        image_paths = self._collect_image_paths()
        total_files = len(image_paths)
        
        if not image_paths:
            self.log_signal.emit("WARNING", "没有找到任何可以处理的图像文件\n\n"
                           "请检查：\n"
                           "• 您选择的文件夹路径是否正确\n"
                           "• 文件夹里是否有.jpg、.jpeg、.png、.webp等格式的图片")
            self.finished_conversion.emit()
            return
        
        self.log_signal.emit("WARNING", f"开始处理 {total_files} 张图片")
        self.progress_updated.emit(0)
        
        # 创建任务并处理
        futures = self._create_processing_tasks(image_paths, error_count)
        
        # 执行任务并更新进度
        if futures:
            success_count, error_count = self._execute_futures(futures, success_count, error_count)
        
        # 完成处理，输出总结信息
        self._log_completion_summary(success_count, error_count, total_files)
        self.finished_conversion.emit()
    
    def _create_processing_tasks(self, image_paths, error_count):
        """创建图像处理任务，避免嵌套try-except"""
        futures = {}
        with ThreadPoolExecutor(max_workers=min(4, os.cpu_count() or 1)) as executor:
            for path in image_paths:
                if self._stop_requested:
                    break
                
                # 检查文件大小
                file_size = self._check_file_size(path)
                if file_size > 500 * 1024 * 1024:
                    self.log_signal.emit("ERROR", f"文件 {os.path.basename(path)} 太大了(超过500MB)，暂不支持处理")
                    error_count += 1
                    continue
                
                # 提交任务
                future = self._submit_task(executor, path)
                if future:
                    futures[future] = path
            
            return futures
    
    def _check_file_size(self, file_path):
        """检查文件大小"""
        try:
            return os.path.getsize(file_path)
        except Exception as e:
            self.log_signal.emit("ERROR", f"获取文件大小失败 {os.path.basename(file_path)}: {str(e)}")
            return 0
    
    def _submit_task(self, executor, file_path):
        """提交任务到执行器"""
        try:
            return executor.submit(self.process_image, file_path)
        except Exception as e:
            self.log_signal.emit("ERROR", f"添加文件 {os.path.basename(file_path)} 到任务队列失败: {str(e)}")
            return None
    
    def _execute_futures(self, futures, success_count, error_count):
        """执行所有futures任务并处理结果"""
        try:
            for i, future in enumerate(as_completed(futures), 1):
                if self._stop_requested:
                    self._cancel_all_tasks(futures)
                    break
                
                # 处理单个future结果
                success, error = self._process_future_result(future, futures)
                success_count += success
                error_count += error
                
                # 更新进度
                progress = int((i / len(futures)) * 100)
                self.progress_updated.emit(progress)
        except Exception as e:
            self.log_signal.emit("ERROR", f"任务调度过程中发生错误: {str(e)}")
            error_count += 1
        
        return success_count, error_count
    
    def _cancel_all_tasks(self, futures):
        """取消所有任务"""
        for f in futures:
            f.cancel()
        time.sleep(0.1)
        self.log_signal.emit("DEBUG", "EXIF写入操作已成功中止")
    
    def _process_future_result(self, future, futures):
        """处理单个future的结果"""
        success = 0
        error = 0
        
        try:
            future.result(timeout=30)
            success = 1
        except TimeoutError:
            file_path = futures[future]
            self.log_signal.emit("ERROR", f"处理文件 {os.path.basename(file_path)} 时间太长，已超时")
            error = 1
        except Exception as e:
            file_path = futures[future]
            self.log_signal.emit("ERROR", f"处理文件 {os.path.basename(file_path)} 时出错: {str(e)}")
            error = 1
        
        return success, error
    
    def _log_completion_summary(self, success_count, error_count, total_files):
        """记录完成摘要"""
        self.log_signal.emit("DEBUG", "=" * 40)
        self.log_signal.emit("INFO", f"属性写入完成了，成功写入了 {success_count} 张，失败了 {error_count} 张，共 {total_files}。")
        self.log_signal.emit("DEBUG", "=" * 3 + "LeafView © 2025 Yangshengzhou.All Rights Reserved" + "=" * 3)

    def _collect_image_paths(self):
        image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mov', '.mp4', '.avi', '.mkv', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf')
        image_paths = []
        
        for folder_path, include_sub in self.folders_dict.items():
            # 处理每个文件夹
            self._process_folder(folder_path, include_sub, image_extensions, image_paths)
                
        logger.info(f"共收集到 {len(image_paths)} 个图像文件")
        return image_paths
    
    def _process_folder(self, folder_path, include_sub, image_extensions, image_paths):
        """处理单个文件夹"""
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            logger.warning(f"文件夹不存在: {folder_path}")
            self.log_signal.emit("WARNING", f"文件夹不存在: {folder_path}")
            return
        
        # 根据是否包含子文件夹选择不同的处理方式
        if include_sub == 1:
            self._process_folder_with_subfolders(folder_path, image_extensions, image_paths)
        else:
            self._process_folder_without_subfolders(folder_path, image_extensions, image_paths)
    
    def _process_folder_with_subfolders(self, folder_path, image_extensions, image_paths):
        """处理包含子文件夹的情况"""
        try:
            for root, _, files in os.walk(folder_path):
                self._process_folder_content(root, files, image_extensions, image_paths)
        except Exception as e:
            logger.error(f"遍历文件夹 {folder_path} 时出错: {str(e)}")
            self.log_signal.emit("ERROR", f"遍历文件夹 {folder_path} 时出错: {str(e)}")
    
    def _process_folder_without_subfolders(self, folder_path, image_extensions, image_paths):
        """处理不包含子文件夹的情况"""
        try:
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                self._process_folder_content(folder_path, files, image_extensions, image_paths)
        except PermissionError as e:
            logger.error(f"没有权限访问文件夹 {folder_path}: {str(e)}")
            self.log_signal.emit("ERROR", f"没有权限访问文件夹 {folder_path}")
        except Exception as e:
            logger.error(f"列出文件夹 {folder_path} 内容时出错: {str(e)}")
            self.log_signal.emit("ERROR", f"列出文件夹 {folder_path} 内容时出错: {str(e)}")
    
    def _process_folder_content(self, root, files, image_extensions, image_paths):
        """处理文件夹内容，添加符合条件的图像文件"""
        try:
            image_paths.extend(
                os.path.join(root, file)
                for file in files
                if file.lower().endswith(image_extensions)
            )
        except Exception as e:
            logger.error(f"处理文件夹 {root} 内容时出错: {str(e)}")
            self.log_signal.emit("ERROR", f"处理文件夹 {root} 内容时出错: {str(e)}")

    def process_image(self, image_path):
        try:
            if self._stop_requested:
                self.log_signal.emit("WARNING", f"处理被取消: {os.path.basename(image_path)}")
                return
            
            # 检查文件是否存在
            if not os.path.exists(image_path):
                logger.error(f"文件不存在: {image_path}")
                self.log_signal.emit("ERROR", f"文件不存在: {os.path.basename(image_path)}")
                return
            
            # 检查文件是否可读
            if not os.access(image_path, os.R_OK):
                logger.error(f"文件不可读: {image_path}")
                self.log_signal.emit("ERROR", f"文件不可读: {os.path.basename(image_path)}")
                return
            
            file_ext = os.path.splitext(image_path)[1].lower()
            logger.debug(f"处理文件: {image_path}, 扩展名: {file_ext}")
            
            # 根据文件扩展名处理不同格式
            if file_ext in ('.jpg', '.jpeg', '.webp'):
                self._process_exif_format(image_path)
            elif file_ext == '.png':
                self._process_png_format(image_path)
            elif file_ext in ('.heic', '.heif'):
                self._process_heic_format(image_path)
            elif file_ext in ('.mov', '.mp4', '.avi', '.mkv'):
                self._process_video_format(image_path)
            elif file_ext in ('.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf'):
                self._process_raw_format(image_path)
            else:
                logger.warning(f"不支持的文件格式: {file_ext}")
                self.log_signal.emit("WARNING", f"不支持的文件格式: {file_ext}")

        except Exception as e:
            logger.error(f"处理文件 {image_path} 时出错: {str(e)}")
            self._handle_processing_error(image_path, e)

    def _handle_processing_error(self, image_path, error):
        """处理文件处理过程中的错误"""
        try:
            result = detect_media_type(image_path)
            if not result["valid"]:
                logger.error(f"文件损坏或格式不支持: {image_path}")
                self.log_signal.emit("ERROR", f"{os.path.basename(image_path)} 文件已损坏或格式不支持\n\n"
                                 "请检查文件完整性")
            elif not result["extension_match"]:
                logger.warning(f"扩展名不匹配: {image_path}, 实际格式: {result['extension']}")
                self.log_signal.emit("ERROR", f"{os.path.basename(image_path)} 扩展名不匹配，实际格式为 {result['extension']}\n\n"
                                 "请检查文件格式")
            else:
                logger.error(f"处理文件 {image_path} 时出错: {str(error)}")
                self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(error)}")
        except Exception as e:
            logger.error(f"错误处理过程中出错: {str(e)}")
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(error)}")

    def _process_exif_format(self, image_path):
        # 检查文件是否可写
        if not os.access(image_path, os.W_OK):
            logger.error(f"文件不可写: {image_path}")
            self.log_signal.emit("ERROR", f"文件不可写: {os.path.basename(image_path)}")
            return
        
        # 加载EXIF数据
        exif_dict = self._load_exif_data(image_path)
        if not exif_dict:
            return
        
        # 处理EXIF数据
        updated_fields = self._update_exif_fields(exif_dict, image_path)
        if not updated_fields:
            return
        
        # 写入EXIF数据
        self._save_exif_data(image_path, exif_dict, updated_fields)
    
    def _load_exif_data(self, image_path):
        """加载EXIF数据"""
        try:
            return piexif.load(image_path)
        except Exception as e:
            logger.warning(f"加载EXIF数据失败 {image_path}: {str(e)}，将创建新的EXIF数据")
            return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    def _update_exif_fields(self, exif_dict, image_path):
        """更新EXIF字段"""
        updated_fields = []
        
        try:
            if self.title:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = self.title.encode('utf-8')
                updated_fields.append(f"标题: {self.title}")
            
            if self.author:
                exif_dict["0th"][315] = self.author.encode('utf-8')
                updated_fields.append(f"作者: {self.author}")
            
            if self.subject:
                exif_dict["0th"][piexif.ImageIFD.XPSubject] = self.subject.encode('utf-16le')
                updated_fields.append(f"主题: {self.subject}")
            
            if self.rating:
                exif_dict["0th"][piexif.ImageIFD.Rating] = int(self.rating)
                updated_fields.append(f"评分: {self.rating}星")
            
            if self.copyright:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = self.copyright.encode('utf-8')
                updated_fields.append(f"版权: {self.copyright}")
            
            if self.camera_brand:
                exif_dict["0th"][piexif.ImageIFD.Make] = self.camera_brand.encode('utf-8')
                updated_fields.append(f"相机品牌: {self.camera_brand}")

            if self.camera_model:
                exif_dict["0th"][piexif.ImageIFD.Model] = self.camera_model.encode('utf-8')
                updated_fields.append(f"相机型号: {self.camera_model}")

            if self.lens_brand:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = self.lens_brand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {self.lens_brand}")

            if self.lens_model:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = self.lens_model.encode('utf-8')
                updated_fields.append(f"镜头型号: {self.lens_model}")

            if self.shoot_time != 0:
                self._handle_shoot_time(exif_dict, image_path, updated_fields)
            
            if self.lat is not None and self.lon is not None:
                exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
                updated_fields.append(
                    f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
            
            # 检查是否有更新内容
            if not updated_fields:
                logger.info(f"文件 {image_path} 没有需要更新的内容")
                self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改\n\n"
                                 "可能的原因：\n"
                                 "• 所有EXIF字段均为空")
                return []
            
            return updated_fields
        except Exception as e:
            logger.error(f"处理EXIF数据时出错 {image_path}: {str(e)}")
            self.log_signal.emit("ERROR", f"处理EXIF数据时出错 {os.path.basename(image_path)}: {str(e)}")
            return []
    
    def _save_exif_data(self, image_path, exif_dict, updated_fields):
        """保存EXIF数据"""
        try:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            logger.info(f"成功写入EXIF数据到 {image_path}")
            self.log_signal.emit("INFO", f"写入成功 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
        except Exception as e:
            logger.error(f"写入EXIF数据失败 {image_path}: {str(e)}")
            self.log_signal.emit("ERROR", f"写入EXIF数据失败 {os.path.basename(image_path)}: {str(e)}")

    def _handle_shoot_time(self, exif_dict, image_path, updated_fields):
        """处理拍摄时间逻辑"""
        try:
            if self.shoot_time == 1:
                date_from_filename = self.get_date_from_filename(image_path)
                if date_from_filename:
                    if "Exif" not in exif_dict:
                        exif_dict["Exif"] = {}
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_from_filename.strftime(
                        "%Y:%m:%d %H:%M:%S").encode('utf-8')
                    updated_fields.append(
                        f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')}")
                else:
                    logger.warning(f"无法从文件名提取时间: {image_path}")
                    self.log_signal.emit("WARNING", f"无法从文件名提取时间: {os.path.basename(image_path)}")
            elif self.shoot_time == 2:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
                updated_fields.append(f"拍摄时间: {datetime.now().strftime('%Y:%m:%d %H:%M:%S')}")
            elif self.shoot_time == 3:
                pass
            else:
                try:
                    datetime.strptime(self.shoot_time, "%Y:%m:%d %H:%M:%S")
                    if "Exif" not in exif_dict:
                        exif_dict["Exif"] = {}
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = self.shoot_time.encode('utf-8')
                    updated_fields.append(f"拍摄时间: {self.shoot_time}")
                except ValueError:
                    logger.error(f"拍摄时间格式无效: {self.shoot_time}")
                    self.log_signal.emit("ERROR", f"拍摄时间格式无效: {self.shoot_time}，请使用 YYYY:MM:DD HH:MM:SS 格式")
        except Exception as e:
            logger.error(f"处理拍摄时间时出错: {str(e)}")
            self.log_signal.emit("ERROR", f"处理拍摄时间时出错: {str(e)}")

    def _process_png_format(self, image_path):
        try:
            # 检查文件是否可写
            if not os.access(image_path, os.W_OK):
                logger.error(f"PNG文件不可写: {image_path}")
                self.log_signal.emit("ERROR", f"PNG文件不可写: {os.path.basename(image_path)}")
                return
                
            if self.shoot_time != 0:
                try:
                    with Image.open(image_path) as img:
                        png_info = PngImagePlugin.PngInfo()
                        
                        # 复制现有的文本信息
                        try:
                            if img.text:
                                for key in img.text:
                                    if key.lower() != "creation time":
                                        try:
                                            png_info.add_text(key, img.text[key])
                                        except Exception as e:
                                            logger.warning(f"复制PNG文本信息失败 {key}: {str(e)}")
                        except AttributeError:
                            pass
                        
                        # 添加新的拍摄时间
                        if self.shoot_time == 1:
                            date_from_filename = self.get_date_from_filename(image_path)
                            if date_from_filename:
                                png_info.add_text("Creation Time", str(date_from_filename))
                                self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {date_from_filename}")
                            else:
                                logger.warning(f"无法从文件名提取时间: {image_path}")
                                self.log_signal.emit("WARNING", f"无法从文件名提取时间: {os.path.basename(image_path)}")
                        else:
                            png_info.add_text("Creation Time", self.shoot_time)
                            self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {self.shoot_time}")
                            
                except Exception as e:
                    logger.error(f"处理PNG文件时出错 {image_path}: {str(e)}")
                    self.log_signal.emit("ERROR", f"处理PNG文件 {os.path.basename(image_path)} 时出错: {str(e)}")
            else:
                logger.info(f"PNG文件 {image_path} 没有需要更新的拍摄时间")
                
        except Exception as e:
            logger.error(f"处理PNG格式文件时出错 {image_path}: {str(e)}")
            self.log_signal.emit("ERROR", f"处理PNG格式文件 {os.path.basename(image_path)} 时出错: {str(e)}")

    def _save_png_with_metadata(self, image_path, img, png_info, success_message):
        """保存PNG文件并处理可能的错误"""
        try:
            temp_path = image_path + ".tmp"
            
            # 尝试保存到临时文件
            img.save(temp_path, format="PNG", pnginfo=png_info)
            
            # 检查临时文件是否创建成功
            if not os.path.exists(temp_path):
                raise Exception("临时文件创建失败")
                
            # 尝试替换原文件
            try:
                os.replace(temp_path, image_path)
                logger.info(f"成功写入PNG元数据: {image_path}")
                self.log_signal.emit("INFO", f"成功写入 {os.path.basename(image_path)} 的{success_message}")
            except PermissionError as e:
                logger.error(f"没有权限替换文件 {image_path}: {str(e)}")
                self.log_signal.emit("ERROR", f"没有权限替换文件 {os.path.basename(image_path)}")
                # 清理临时文件
                try:
                    os.remove(temp_path)
                except:
                    pass
            except Exception as e:
                logger.error(f"替换文件失败 {image_path}: {str(e)}")
                self.log_signal.emit("ERROR", f"替换文件失败 {os.path.basename(image_path)}: {str(e)}")
                    
        except Exception as e:
            logger.error(f"保存PNG文件失败 {image_path}: {str(e)}")
            self.log_signal.emit("ERROR", f"保存PNG文件 {os.path.basename(image_path)} 失败: {str(e)}")
        finally:
            # 清理临时文件
            try:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            except Exception as e:
                logger.debug(f"清理临时文件失败: {str(e)}")

    def _process_heic_format(self, image_path):
        try:
            from pillow_heif import open_heif, register_heif_opener
            register_heif_opener()
        except ImportError:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 需要 pillow-heif")
            return
        
        try:
            heif_file = open_heif(image_path)
            
            try:
                image = heif_file.to_pillow()
            except AttributeError:
                image = heif_file.to_pil()
            
            exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
            
            # 尝试加载现有EXIF数据
            try:
                try:
                    if heif_file.exif:
                        heif_exif = piexif.load(heif_file.exif)
                        exif_dict.update(heif_exif)
                except AttributeError:
                    pass
            except Exception as e:
                logger.debug(f"加载HEIF EXIF数据失败: {str(e)}")
            
            try:
                pil_exif = image._getexif()
                if pil_exif:
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
                    
                    # 合并PIL EXIF数据到exif_dict
                    for tag_id, (section, piexif_tag) in tag_mapping.items():
                        if tag_id in pil_exif:
                            try:
                                exif_dict[section][piexif_tag] = pil_exif[tag_id]
                            except Exception as e:
                                logger.debug(f"处理PIL EXIF标签 {tag_id} 失败: {str(e)}")
            except Exception as e:
                logger.debug(f"加载PIL EXIF数据失败: {str(e)}")
            
            # 尝试从image.info加载EXIF数据
            try:
                if 'exif' in image.info:
                    info_exif = piexif.load(image.info['exif'])
                    exif_dict.update(info_exif)

            except Exception as e:
                    pass
            
            try:
                with Image.open(image_path) as img:
                    pil_exif = img._getexif()
                    if pil_exif:
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
                            exif_dict[section][piexif_tag] = pil_exif[tag_id]
            except Exception:
                pass
            
            updated_fields = []
            
            if self.title:
                exif_dict["0th"][piexif.ImageIFD.ImageDescription] = self.title.encode('utf-8')
                updated_fields.append(f"标题: {self.title}")
            
            if self.author:
                exif_dict["0th"][315] = self.author.encode('utf-8')
                updated_fields.append(f"作者: {self.author}")
            
            if self.subject:
                exif_dict["0th"][piexif.ImageIFD.XPSubject] = self.subject.encode('utf-16le')
                updated_fields.append(f"主题: {self.subject}")
            
            if self.rating:
                exif_dict["0th"][piexif.ImageIFD.Rating] = int(self.rating)
                updated_fields.append(f"评分: {self.rating}星")
            
            if self.copyright:
                exif_dict["0th"][piexif.ImageIFD.Copyright] = self.copyright.encode('utf-8')
                updated_fields.append(f"版权: {self.copyright}")
            
            if self.cameraBrand:
                exif_dict["0th"][piexif.ImageIFD.Make] = self.cameraBrand.encode('utf-8')
                updated_fields.append(f"相机品牌: {self.cameraBrand}")
            
            if self.cameraModel:
                exif_dict["0th"][piexif.ImageIFD.Model] = self.cameraModel.encode('utf-8')
                updated_fields.append(f"相机型号: {self.cameraModel}")
            
            if self.lensBrand:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.LensMake] = self.lensBrand.encode('utf-8')
                updated_fields.append(f"镜头品牌: {self.lensBrand}")
            
            if self.lensModel:
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.LensModel] = self.lensModel.encode('utf-8')
                updated_fields.append(f"镜头型号: {self.lensModel}")
            
            if self.shootTime != 0:
                if self.shootTime == 1:
                    date_from_filename = self.get_date_from_filename(image_path)
                    if date_from_filename:
                        if "Exif" not in exif_dict:
                            exif_dict["Exif"] = {}
                        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = date_from_filename.strftime(
                            "%Y:%m:%d %H:%M:%S").encode('utf-8')
                        updated_fields.append(
                            f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')}")
                else:
                    if "Exif" not in exif_dict:
                        exif_dict["Exif"] = {}
                    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = self.shootTime.encode('utf-8')
                    updated_fields.append(f"拍摄时间: {self.shootTime}")
            
            if self.lat is not None and self.lon is not None:
                exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
                updated_fields.append(
                    f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
            
            if updated_fields:
                try:
                    temp_path = image_path + ".tmp"
                    exif_bytes = piexif.dump(exif_dict)
                    image.save(temp_path, format="HEIF", exif=exif_bytes)
                    os.replace(temp_path, image_path)
                    self.log_signal.emit("INFO", f"写入成功 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
                except Exception as e:
                    self.log_signal.emit("ERROR", f"写入EXIF数据失败: {str(e)}")
                    if os.path.exists(temp_path):
                        try:
                            os.remove(temp_path)
                        except:
                            pass
            else:
                self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改\n\n"
                                 "可能的原因：\n"
                                 "• 所有EXIF字段均为空")
                
        except Exception as e:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    def _process_video_format(self, image_path):
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext in ('.mov', '.mp4', '.avi', '.mkv'):
            self._process_video_with_exiftool(image_path)
        else:
            self.log_signal.emit("WARNING", f"不支持的视频格式: {file_ext}")
    
    def _process_video_with_exiftool(self, image_path):
        
        if not os.path.exists(image_path):
            self.log_signal.emit("ERROR", f"文件不存在: {image_path}")
            return
        temp_file_path = None
        original_file_path = image_path
        temp_dir = None
        has_non_ascii = any(ord(char) > 127 for char in image_path)
        
        if has_non_ascii:
            temp_dir = tempfile.mkdtemp(prefix="exiftool_temp_")
            temp_file_path = os.path.join(temp_dir, os.path.basename(image_path))
            shutil.copy2(image_path, temp_file_path)
            image_path = temp_file_path
        
        file_path_normalized = image_path.replace('\\', '/')
        exiftool_path = get_resource_path('resources/exiftool/exiftool.exe')
        cmd_parts = [exiftool_path, "-overwrite_original"]
        updated_fields = []
        
        if self.cameraBrand:
            cmd_parts.append(f'-Make="{self.cameraBrand}"')
            updated_fields.append(f"相机品牌: {self.cameraBrand}")
        
        if self.cameraModel:
            cmd_parts.append(f'-Model="{self.cameraModel}"')
            updated_fields.append(f"相机型号: {self.cameraModel}")
        
        if self.lat is not None and self.lon is not None:
            lat_dms = self.decimal_to_dms(self.lat)
            lon_dms = self.decimal_to_dms(self.lon)
            cmd_parts.append(f'-GPSLatitude="{lat_dms}"')
            cmd_parts.append(f'-GPSLongitude="{lon_dms}"')
            cmd_parts.append('-GPSLatitudeRef=N' if self.lat >= 0 else '-GPSLatitudeRef=S')
            cmd_parts.append('-GPSLongitudeRef=E' if self.lon >= 0 else '-GPSLongitudeRef=W')
            
            cmd_parts.append(f'-GPSCoordinates="{self.lat}, {self.lon}"')
            updated_fields.append(f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
        
        if self.shootTime != 0:
            if self.shootTime == 1:
                date_from_filename = self.get_date_from_filename(original_file_path)
                if date_from_filename:
                    local_time = date_from_filename
                    utc_time = local_time - timedelta(hours=8)
                    actual_write_time = utc_time.strftime("%Y:%m:%d %H:%M:%S")
                    timezone_suffix = "+00:00"
                    cmd_parts.append(f'-CreateDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-CreationDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-MediaCreateDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-DateTimeOriginal={actual_write_time}{timezone_suffix}')
                    updated_fields.append(f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')} (已调整为UTC时间)")
            else:
                try:
                    datetime.strptime(self.shootTime, "%Y:%m:%d %H:%M:%S")
                    local_time = datetime.strptime(self.shootTime, "%Y:%m:%d %H:%M:%S")
                    utc_time = local_time - timedelta(hours=8)
                    actual_write_time = utc_time.strftime("%Y:%m:%d %H:%M:%S")
                    timezone_suffix = "+00:00"
                    cmd_parts.append(f'-CreateDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-CreationDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-MediaCreateDate={actual_write_time}{timezone_suffix}')
                    cmd_parts.append(f'-DateTimeOriginal={actual_write_time}{timezone_suffix}')
                    updated_fields.append(f"拍摄时间: {self.shootTime} (已调整为UTC时间)")
                except ValueError:
                    self.log_signal.emit("ERROR", f"拍摄时间格式无效: {self.shootTime}，请使用 YYYY:MM:DD HH:MM:SS 格式")
        
        try:
            cmd_parts.append(file_path_normalized)
            
            result = subprocess.run(cmd_parts, capture_output=True, text=True, shell=False)
            
            if result.returncode != 0:
                self.log_signal.emit("ERROR", f"写入EXIF数据失败: {result.stderr}")
                return False

            if updated_fields:
                self.log_signal.emit("INFO", f"写入成功 {os.path.basename(original_file_path)}: {'; '.join(updated_fields)}")
            
            verify_cmd = [exiftool_path, '-CreateDate', '-CreationDate', '-MediaCreateDate', '-DateTimeOriginal', file_path_normalized]
            subprocess.run(verify_cmd, capture_output=True, text=True, shell=False)
            
            return True
            
        except Exception as e:
            self.log_signal.emit("ERROR", f"执行exiftool命令时出错: {str(e)}")
            return False
        finally:
            if temp_file_path and os.path.exists(temp_file_path) and original_file_path != image_path:
                try:
                    shutil.copy2(temp_file_path, original_file_path)
                except Exception as e:
                    self.log_signal.emit("ERROR", f"复制文件回原始路径失败: {str(e)}")
            
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    self.log_signal.emit("WARNING", f"无法删除临时文件: {str(e)}")
            
            if temp_dir and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    self.log_signal.emit("WARNING", f"无法删除临时目录: {str(e)}")

    def _process_raw_format(self, image_path):
        if not os.path.exists(image_path):
            self.log_signal.emit("ERROR", f"文件不存在: {os.path.basename(image_path)}")
            return
        
        exiftool_path = os.path.join(os.path.dirname(__file__), "resources", "exiftool", "exiftool.exe")
        
        if not os.path.exists(exiftool_path):
            self.log_signal.emit("ERROR", "exiftool工具不存在，无法处理RAW格式文件")
            return
        
        exif_data = {}
        updated_fields = []
        
        if self.shootTime != 0:
            if self.shootTime == 1:
                date_from_filename = self.get_date_from_filename(image_path)
                if date_from_filename:
                    exif_data['DateTimeOriginal'] = date_from_filename.strftime('%Y:%m:%d %H:%M:%S')
                    exif_data['CreateDate'] = date_from_filename.strftime('%Y:%m:%d %H:%M:%S')
                    exif_data['ModifyDate'] = date_from_filename.strftime('%Y:%m:%d %H:%M:%S')
                    updated_fields.append(f"拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')}")
            else:
                try:
                    datetime.strptime(self.shootTime, "%Y:%m:%d %H:%M:%S")
                    exif_data['DateTimeOriginal'] = self.shootTime
                    exif_data['CreateDate'] = self.shootTime
                    exif_data['ModifyDate'] = self.shootTime
                    updated_fields.append(f"拍摄时间: {self.shootTime}")
                except ValueError:
                    self.log_signal.emit("ERROR", f"拍摄时间格式无效: {self.shootTime}")
        
        if self.title:
            exif_data['ImageDescription'] = self.title
            updated_fields.append(f"标题: {self.title}")
        
        if self.author:
            exif_data['Artist'] = self.author
            updated_fields.append(f"作者: {self.author}")
        
        if self.copyright:
            exif_data['Copyright'] = self.copyright
            updated_fields.append(f"版权: {self.copyright}")
        
        if self.cameraBrand:
            exif_data['Make'] = self.cameraBrand
            updated_fields.append(f"相机品牌: {self.cameraBrand}")
        
        if self.cameraModel:
            exif_data['Model'] = self.cameraModel
            updated_fields.append(f"相机型号: {self.cameraModel}")
        
        if self.lensBrand:
            exif_data['LensMake'] = self.lensBrand
            updated_fields.append(f"镜头品牌: {self.lensBrand}")
        
        if self.lensModel:
            exif_data['LensModel'] = self.lensModel
            updated_fields.append(f"镜头型号: {self.lensModel}")
        
        if self.lat is not None and self.lon is not None:
            exif_data['GPSLatitude'] = self.lat
            exif_data['GPSLongitude'] = self.lon
            updated_fields.append(f"GPS坐标: {self.lat:.6f}, {self.lon:.6f}")
        
        if not exif_data:
            self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            return
        
        commands = []
        for key, value in exif_data.items():
            if isinstance(value, str):
                commands.append(f'-{key}="{value}"')
            else:
                commands.append(f'-{key}={value}')
        
        cmd = [exiftool_path, "-overwrite_original"] + commands + [image_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30)
            
            if result.returncode == 0:
                if updated_fields:
                    self.log_signal.emit("INFO", f"成功写入 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
                else:
                    self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            else:
                error_msg = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "未知错误"
                self.log_signal.emit("ERROR", f"写入 {os.path.basename(image_path)} 失败: {error_msg}")
                
        except subprocess.TimeoutExpired:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 超时")
        except Exception as e:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")

    def stop(self):
        """停止处理线程"""
        self._stop_requested = True
        # 确保线程能够尽快退出
        if self.isRunning():
            self.wait(1000)  # 等待最多1秒让线程完成

    def decimal_to_dms(self, decimal):
        try:
            decimal = abs(decimal)
            
            degrees = int(decimal)
            minutes_decimal = (decimal - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            
            dms_str = f"{degrees} deg {minutes}' {seconds:.2f}\""
            
            return dms_str
        except Exception as e:
            self.log_signal.emit("ERROR", f"坐标转换错误: {str(e)}")
            return str(decimal)



    def _create_gps_data(self, lat, lon):
        def _decimal_to_piexif_dms(decimal):
            degrees = int(abs(decimal))
            minutes_decimal = (abs(decimal) - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            return [(degrees, 1), (minutes, 1), (int(seconds * 100), 100)]
        
        gps_dict = {}
        
        gps_dict[piexif.GPSIFD.GPSLatitude] = _decimal_to_piexif_dms(abs(lat))
        gps_dict[piexif.GPSIFD.GPSLatitudeRef] = b'N' if lat >= 0 else b'S'
        
        gps_dict[piexif.GPSIFD.GPSLongitude] = _decimal_to_piexif_dms(abs(lon))
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
        base_name = os.path.basename(image_path)
        name_without_ext = os.path.splitext(base_name)[0]
        
        date_pattern = r'(?P<year>\d{4})[年\-\.\/\s]?' \
                       r'(?P<month>1[0-2]|0?[1-9])[月\-\.\/\s]?' \
                       r'(?P<day>3[01]|[12]\d|0?[1-9])[日号\-\.\/\s]?' \
                       r'(?:[^0-9]*?)?' \
                       r'(?P<hour>[0-2]?\d)?' \
                       r'(?P<minute>[0-5]?\d)?' \
                       r'(?P<second>[0-5]?\d)?'
        
        match = re.search(date_pattern, name_without_ext)
        if not match:
            time_pattern = r'(?P<year>\d{4})[^\d]*(?P<month>1[0-2]|0?[1-9])[^\d]*(?P<day>3[01]|[12]\d|0?[1-9])[^\d]*(?P<hour>[0-2]?\d)(?P<minute>[0-5]\d)(?P<second>[0-5]\d)'
            match = re.search(time_pattern, name_without_ext)
        
        if match:
            groups = match.groupdict()
            if not all([groups.get('year'), groups.get('month'), groups.get('day')]):
                return None

            date_str_parts = [
                groups['year'],
                groups['month'].rjust(2, '0'),
                groups['day'].rjust(2, '0')
            ]
            
            has_time = False
            if groups.get('hour'):
                date_str_parts.append(groups['hour'].rjust(2, '0'))
                has_time = True
                if groups.get('minute'):
                    date_str_parts.append(groups['minute'].rjust(2, '0'))
                    if groups.get('second'):
                        date_str_parts.append(groups['second'].rjust(2, '0'))
                    elif len(groups.get('minute', '')) == 2 and len(groups.get('hour', '')) == 2:
                        remaining_text = name_without_ext[match.end():]
                        if remaining_text and remaining_text[:2].isdigit():
                            seconds = remaining_text[:2]
                            if 0 <= int(seconds) <= 59:
                                date_str_parts.append(seconds)
                                groups['second'] = seconds
            
            if not has_time:
                time_match = re.search(r'(?P<hour>[0-2]\d)(?P<minute>[0-5]\d)(?P<second>[0-5]\d)', name_without_ext)
                if time_match:
                    groups.update(time_match.groupdict())
                    date_str_parts.append(groups['hour'])
                    date_str_parts.append(groups['minute'])
                    date_str_parts.append(groups['second'])
                    has_time = True

            date_str = ''.join(date_str_parts)
            
            possible_formats = []
            if len(date_str) == 8:
                possible_formats.append("%Y%m%d")
            elif len(date_str) == 12:
                possible_formats.append("%Y%m%d%H%M")
            elif len(date_str) == 14:
                possible_formats.append("%Y%m%d%H%M%S")

            for fmt in possible_formats:
                try:
                    date_obj = datetime.strptime(date_str, fmt)
                    if (1900 <= date_obj.year <= 2100 and
                            1 <= date_obj.month <= 12 and
                            1 <= date_obj.day <= 31):
                        if not has_time:
                            date_obj = date_obj.replace(hour=0, minute=0, second=0)
                        return date_obj
                except ValueError:
                    continue
        return None
