#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
write_exif_thread.py

功能：处理图片EXIF信息写入的线程模块
用于在后台线程中批量更新图片的EXIF元数据，支持多种图片格式，包括JPEG、PNG和HEIC。
"""

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

# 尝试导入pillow-heif，用于处理HEIC格式
try:
    from pillow_heif import open_heif, register_heif_opener
    PILLOW_HEIF_AVAILABLE = True
except ImportError:
    PILLOW_HEIF_AVAILABLE = False

# 配置日志记录
logger = logging.getLogger(__name__)


class WriteExifThread(QThread):
    """
    EXIF信息写入线程类
    
    用于在后台线程中批量处理图片的EXIF信息更新，避免阻塞主线程。
    支持更新标题、作者、版权、位置、拍摄时间等多种EXIF元数据。
    """
    
    progress_updated = pyqtSignal(int)
    finished_conversion = pyqtSignal()
    log_signal = pyqtSignal(str, str)

    def __init__(self, folders_dict, exif_config=None):
        """
        初始化EXIF写入线程
        
        Args:
            folders_dict: 包含要处理的文件夹路径及其子文件夹包含选项的字典
            exif_config: 包含EXIF配置信息的字典，可选键值包括：
                title: 图片标题
                author: 作者信息
                subject: 主题信息
                rating: 评分
                copyright_text: 版权信息
                position: 位置信息(格式: "纬度,经度")
                shoot_time: 拍摄时间
                camera_brand: 相机品牌
                camera_model: 相机型号
                lens_brand: 镜头品牌
                lens_model: 镜头型号
        """
        super().__init__()
        # 基础属性
        self.folders_dict = {item['path']: item['include_sub'] for item in folders_dict}
        self._stop_requested = False
        
        # 使用配置字典存储EXIF相关信息
        self.exif_config = exif_config or {}
        
        # 解析位置信息
        self.lat, self.lon = None, None
        position = self.exif_config.get('position', '')
        if position and ',' in position:
            try:
                self.lat, self.lon = map(float, position.split(','))
                if not (-90 <= self.lat <= 90) or not (-180 <= self.lon <= 180):
                    self.lat, self.lon = None, None
            except ValueError:
                pass

    def run(self):
        """线程主函数，执行EXIF写入任务的核心流程
        
        该方法负责收集图像路径、创建处理任务、执行任务并更新进度，
        最终输出处理结果摘要。
        """
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
        except (IOError, OSError, ValueError, TypeError) as e:
            self.log_signal.emit("ERROR", f"获取文件大小失败 {os.path.basename(file_path)}: {str(e)}")
            return 0
    
    def _submit_task(self, executor, file_path):
        """提交任务到执行器
        
        Args:
            executor: ThreadPoolExecutor实例
            file_path: 要处理的文件路径
            
        Returns:
            Future对象或None（如果提交失败）
        """
        try:
            return executor.submit(self.process_image, file_path)
        except (IOError, OSError, ValueError, TypeError) as e:
            self.log_signal.emit("ERROR", f"添加文件 {os.path.basename(file_path)} 到任务队列失败: {str(e)}")
            return None
    
    def _execute_futures(self, futures, success_count, error_count):
        """执行所有futures任务并处理结果
        
        Args:
            futures: Future对象字典
            success_count: 成功计数
            error_count: 错误计数
            
        Returns:
            tuple: (success_count, error_count) 更新后的计数
        """
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
        except (IOError, OSError, ValueError, TypeError) as e:
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
        """处理单个future的结果
        
        Args:
            future: Future对象
            futures: Future对象字典，用于获取文件路径
            
        Returns:
            tuple: (success, error) 成功和错误计数
        """
        success = 0
        error = 0
        
        try:
            future.result(timeout=30)
            success = 1
        except TimeoutError:
            file_path = futures[future]
            self.log_signal.emit("ERROR", f"处理文件 {os.path.basename(file_path)} 时间太长，已超时")
            error = 1
        except (IOError, ValueError, TypeError) as e:
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
        """收集所有需要处理的图像文件路径
        
        根据配置的文件夹字典，收集所有支持格式的图像和视频文件路径。
        
        Returns:
            list: 包含所有符合条件的文件路径的列表
        """
        image_extensions = ('.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif', '.mov', '.mp4', '.avi', '.mkv', '.cr2', '.cr3', '.nef', '.arw', '.orf', '.dng', '.raf')
        image_paths = []
        
        for folder_path, include_sub in self.folders_dict.items():
            # 处理每个文件夹
            self._process_folder(folder_path, include_sub, image_extensions, image_paths)
                
        logger.info("共收集到 %d 个图像文件", len(image_paths))
        return image_paths
    
    def _process_folder(self, folder_path, include_sub, image_extensions, image_paths):
        """处理单个文件夹
        
        Args:
            folder_path: 文件夹路径
            include_sub: 是否包含子文件夹（1为包含，0为不包含）
            image_extensions: 支持的图像扩展名元组
            image_paths: 存储图像路径的列表
        """
        # 检查文件夹是否存在
        if not os.path.exists(folder_path):
            logger.warning("文件夹不存在: %s", folder_path)
            self.log_signal.emit("WARNING", "文件夹不存在: %s", folder_path)
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
        except (OSError, IOError) as e:
            logger.error("遍历文件夹 %s 时出错: %s", folder_path, str(e))
            self.log_signal.emit("ERROR", "遍历文件夹 %s 时出错: %s", folder_path, str(e))
    
    def _process_folder_without_subfolders(self, folder_path, image_extensions, image_paths):
        """处理不包含子文件夹的情况"""
        try:
            if os.path.isdir(folder_path):
                files = os.listdir(folder_path)
                self._process_folder_content(folder_path, files, image_extensions, image_paths)
        except PermissionError as e:
            logger.error("没有权限访问文件夹 %s: %s", folder_path, str(e))
            self.log_signal.emit("ERROR", "没有权限访问文件夹 %s", folder_path)
        except (OSError, IOError) as e:
            logger.error("列出文件夹 %s 内容时出错: %s", folder_path, str(e))
            self.log_signal.emit("ERROR", "列出文件夹 %s 内容时出错: %s", folder_path, str(e))
    
    def _process_folder_content(self, root, files, image_extensions, image_paths):
        """处理文件夹内容，添加符合条件的图像文件
        
        Args:
            root: 文件夹根路径
            files: 文件列表
            image_extensions: 支持的图像扩展名元组
            image_paths: 存储图像路径的列表
        """
        try:
            image_paths.extend(
                os.path.join(root, file)
                for file in files
                if file.lower().endswith(image_extensions)
            )
        except (OSError, IOError) as e:
            logger.error("处理文件夹 %s 内容时出错: %s", root, str(e))
            self.log_signal.emit("ERROR", "处理文件夹 %s 内容时出错: %s", root, str(e))

    def process_image(self, image_path):
        """处理单个图像文件，根据文件格式调用相应的处理方法
        
        Args:
            image_path: 要处理的图像文件路径
        """
        try:
            if self._stop_requested:
                self.log_signal.emit("WARNING", f"处理被取消: {os.path.basename(image_path)}")
                return
            
            # 检查文件基本信息
            if not self._validate_file(image_path):
                return
            
            file_ext = os.path.splitext(image_path)[1].lower()
            logger.debug("处理文件: %s, 扩展名: %s", image_path, file_ext)
            
            # 使用字典映射文件扩展名到处理方法，降低分支复杂度
            format_handler = self._get_format_handler(file_ext)
            if format_handler:
                format_handler(image_path)
            else:
                logger.warning("不支持的文件格式: %s", file_ext)
                self.log_signal.emit("WARNING", "不支持的文件格式: %s", file_ext)

        except (IOError, ValueError, TypeError, OSError) as e:
            logger.error("处理文件 %s 时出错: %s", image_path, str(e))
            self._handle_processing_error(image_path, e)
    
    def _validate_file(self, image_path):
        """验证文件是否存在且可读
        
        Args:
            image_path: 要验证的文件路径
            
        Returns:
            bool: 文件有效返回True，否则返回False
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            logger.error("文件不存在: %s", image_path)
            self.log_signal.emit("ERROR", "文件不存在: %s", os.path.basename(image_path))
            return False
        
        # 检查文件是否可读
        if not os.access(image_path, os.R_OK):
            logger.error("文件不可读: %s", image_path)
            self.log_signal.emit("ERROR", "文件不可读: %s", os.path.basename(image_path))
            return False
            
        return True
        
    def _get_format_handler(self, file_ext):
        """获取文件格式对应的处理方法
        
        Args:
            file_ext: 文件扩展名
            
        Returns:
            function: 对应的处理方法或None
        """
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
        """处理文件处理过程中的错误
        
        Args:
            image_path: 图像文件路径
            error: 异常对象
        """
        try:
            result = detect_media_type(image_path)
            if not result["valid"]:
                logger.error("文件损坏或格式不支持: %s", image_path)
                self.log_signal.emit("ERROR", "%s 文件已损坏或格式不支持\n\n请检查文件完整性", os.path.basename(image_path))
            elif not result["extension_match"]:
                logger.warning("扩展名不匹配: %s, 实际格式: %s", image_path, result['extension'])
                self.log_signal.emit("ERROR", "%s 扩展名不匹配，实际格式为 %s\n\n请检查文件格式", os.path.basename(image_path), result['extension'])
            else:
                logger.error("处理文件 %s 时出错: %s", image_path, str(error))
                self.log_signal.emit("ERROR", "处理 %s 时出错: %s", os.path.basename(image_path), str(error))
        except (IOError, OSError) as e:
            logger.error("错误处理过程中出错: %s", str(e))
            self.log_signal.emit("ERROR", "处理 %s 时出错: %s", os.path.basename(image_path), str(error))

    def _process_exif_format(self, image_path):
        """处理支持EXIF格式的图像文件（JPG、JPEG、WebP）
        
        加载现有EXIF数据，更新指定字段，然后将修改后的数据写回文件。
        
        Args:
            image_path: 要处理的图像文件路径
        """
        # 检查文件是否可写
        if not os.access(image_path, os.W_OK):
            logger.error("文件不可写: %s", image_path)
            self.log_signal.emit("ERROR", "文件不可写: %s", os.path.basename(image_path))
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
        except (IOError, OSError, ValueError, TypeError) as e:
            logger.warning("加载EXIF数据失败 %s: %s，将创建新的EXIF数据", image_path, str(e))
            return {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
    
    def _update_exif_fields(self, exif_dict, image_path):
        """更新EXIF字段"""
        updated_fields = []
        
        try:
            # 确保所有需要的section存在
            self._ensure_exif_sections(exif_dict)
            
            # 更新基本EXIF字段
            self._update_basic_fields(exif_dict, updated_fields)
            
            # 更新特殊字段
            self._update_special_fields(exif_dict, image_path, updated_fields)
            
            # 检查是否有更新内容
            return self._check_update_result(updated_fields, image_path)
            
        except (IOError, ValueError, OSError) as e:
            logger.error("处理EXIF数据时出错 %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", "处理EXIF数据时出错 %s: %s", os.path.basename(image_path), str(e))
            return []
    
    def _ensure_exif_sections(self, exif_dict):
        """确保所有需要的EXIF section存在"""
        if "0th" not in exif_dict:
            exif_dict["0th"] = {}
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        if "GPS" not in exif_dict:
            exif_dict["GPS"] = {}
    
    def _update_basic_fields(self, exif_dict, updated_fields):
        """更新基本EXIF字段"""
        # 使用元组列表定义字段映射，每个元组包含(字段名, section, tag, 配置键, 格式化信息)
        field_mappings = [
            ("title", "0th", piexif.ImageIFD.ImageDescription, "title", "标题: {}", "utf-8"),
            ("author", "0th", 315, "author", "作者: {}", "utf-8"),
            ("subject", "0th", piexif.ImageIFD.XPSubject, "subject", "主题: {}", "utf-16le"),
            ("rating", "0th", piexif.ImageIFD.Rating, "rating", "评分: {}星", None, int),
            ("copyright", "0th", piexif.ImageIFD.Copyright, "copyright_text", "版权: {}", "utf-8"),
            ("camera_brand", "0th", piexif.ImageIFD.Make, "camera_brand", "相机品牌: {}", "utf-8"),
            ("camera_model", "0th", piexif.ImageIFD.Model, "camera_model", "相机型号: {}", "utf-8"),
            ("lens_brand", "Exif", piexif.ExifIFD.LensMake, "lens_brand", "镜头品牌: {}", "utf-8"),
            ("lens_model", "Exif", piexif.ExifIFD.LensModel, "lens_model", "镜头型号: {}", "utf-8")
        ]
        
        # 批量更新字段
        for _, section, tag, config_key, format_str, encoding, *transform in field_mappings:
            value = self.exif_config.get(config_key)
            if value:
                # 应用转换函数（如果有）
                processed_value = transform[0](value) if transform else value
                # 应用编码（如果需要）
                if encoding and isinstance(processed_value, str):
                    processed_value = processed_value.encode(encoding)
                
                exif_dict[section][tag] = processed_value
                updated_fields.append(format_str.format(value))
    
    def _update_special_fields(self, exif_dict, image_path, updated_fields):
        """更新特殊字段（拍摄时间和GPS坐标）"""
        # 处理拍摄时间
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time != 0:
            self._handle_shoot_time(exif_dict, image_path, updated_fields, shoot_time)
        
        # 处理GPS坐标
        if self.lat is not None and self.lon is not None:
            exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
            updated_fields.append(
                f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
    
    def _check_update_result(self, updated_fields, image_path):
        """检查更新结果并返回适当的值"""
        if not updated_fields:
            logger.info("文件 %s 没有需要更新的内容", image_path)
            self.log_signal.emit("WARNING", "未对 %s 进行任何更改\n\n可能的原因：\n• 所有EXIF字段均为空", os.path.basename(image_path))
            return []
        return updated_fields
    
    def _save_exif_data(self, image_path, exif_dict, updated_fields):
        """保存EXIF数据"""
        try:
            exif_bytes = piexif.dump(exif_dict)
            piexif.insert(exif_bytes, image_path)
            logger.info("成功写入EXIF数据到 %s", image_path)
            self.log_signal.emit("INFO", "写入成功 %s: %s", os.path.basename(image_path), "; ".join(updated_fields))
        except (IOError, ValueError, OSError) as e:
            logger.error("写入EXIF数据失败 %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", "写入EXIF数据失败 %s: %s", os.path.basename(image_path), str(e))

    def _handle_shoot_time(self, exif_dict, image_path, updated_fields, shoot_time):
        """处理拍摄时间逻辑"""
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
                self.log_signal.emit("WARNING", "无法从文件名提取时间: %s", os.path.basename(image_path))
        elif shoot_time == 2:
            if "Exif" not in exif_dict:
                exif_dict["Exif"] = {}
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = datetime.now().strftime("%Y:%m:%d %H:%M:%S").encode('utf-8')
            updated_fields.append(f"拍摄时间: {datetime.now().strftime('%Y:%m:%d %H:%M:%S')}")
        elif shoot_time == 3:
            pass
        else:
            try:
                datetime.strptime(shoot_time, "%Y:%m:%d %H:%M:%S")
                if "Exif" not in exif_dict:
                    exif_dict["Exif"] = {}
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = shoot_time.encode('utf-8')
                updated_fields.append(f"拍摄时间: {shoot_time}")
            except ValueError:
                logger.error("拍摄时间格式无效: %s", shoot_time)
                self.log_signal.emit("ERROR", "拍摄时间格式无效: %s，请使用 YYYY:MM:DD HH:MM:SS 格式", shoot_time)

    def _process_png_format(self, image_path):
        """处理PNG格式文件的EXIF信息"""
        if not self._check_png_writable(image_path):
            return
            
        shoot_time = self.exif_config.get('shoot_time', 0)
        if shoot_time != 0:
            self._process_png_shoot_time(image_path, shoot_time)
        else:
            logger.info("PNG文件 %s 没有需要更新的拍摄时间", image_path)
            
    def _check_png_writable(self, image_path):
        """检查PNG文件是否可写"""
        if not os.access(image_path, os.W_OK):
            logger.error("PNG文件不可写: %s", image_path)
            self.log_signal.emit("ERROR", "PNG文件不可写: %s", os.path.basename(image_path))
            return False
        return True
    
    def _process_png_shoot_time(self, image_path):
        """处理PNG文件的拍摄时间"""
        try:
            with Image.open(image_path) as img:
                png_info = PngImagePlugin.PngInfo()
                self._copy_existing_png_text(img, png_info)
                self._add_png_creation_time(image_path, img, png_info)
        except (IOError, OSError, ValueError, TypeError) as e:
            logger.error("处理PNG文件时出错 %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", "处理PNG文件 %s 时出错: %s", os.path.basename(image_path), str(e))
    
    def _copy_existing_png_text(self, img, png_info):
        """复制现有的PNG文本信息"""
        try:
            if img.text:
                for key in img.text:
                    if key.lower() != "creation time":
                        try:
                            png_info.add_text(key, img.text[key])
                        except (KeyError, ValueError, TypeError) as e:
                            logger.warning("复制PNG文本信息失败 %s: %s", key, str(e))
        except AttributeError:
            pass
    
    def _add_png_creation_time(self, image_path, img, png_info):
        """添加PNG文件的创建时间"""
        shoot_time = self.exif_config.get('shoot_time', None)
        if shoot_time == 1:
            date_from_filename = self.get_date_from_filename(image_path)
            if date_from_filename:
                png_info.add_text("Creation Time", str(date_from_filename))
                self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {str(date_from_filename)}")
            else:
                logger.warning("无法从文件名提取时间: %s", image_path)
                self.log_signal.emit("WARNING", "无法从文件名提取时间: %s", os.path.basename(image_path))
        elif shoot_time:
            png_info.add_text("Creation Time", shoot_time)
            self._save_png_with_metadata(image_path, img, png_info, f"拍摄时间 {shoot_time}")

    def _save_png_with_metadata(self, image_path, img, png_info, success_message):
        """保存PNG文件并处理可能的错误"""
        temp_path = image_path + ".tmp"
        
        try:
            # 保存到临时文件
            img.save(temp_path, format="PNG", pnginfo=png_info)
            
            # 检查临时文件是否创建成功
            if not os.path.exists(temp_path):
                raise IOError("临时文件创建失败")
                
            # 替换原文件
            os.replace(temp_path, image_path)
            logger.info("成功写入PNG元数据: %s", image_path)
            self.log_signal.emit("INFO", "成功写入 %s 的%s", os.path.basename(image_path), success_message)
            
        except PermissionError as e:
            logger.error("没有权限替换文件 %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", "没有权限替换文件 %s", os.path.basename(image_path))
            # 确保清理临时文件
            self._cleanup_temp_file(temp_path)
            
        except (IOError, ValueError, OSError) as e:
            logger.error("保存PNG文件失败 %s: %s", image_path, str(e))
            self.log_signal.emit("ERROR", "保存PNG文件 %s 失败: %s", os.path.basename(image_path), str(e))
            # 确保清理临时文件
            self._cleanup_temp_file(temp_path)

    def _cleanup_temp_file(self, temp_path):
        """安全清理临时文件"""
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError as e:
                logger.debug("清理临时文件失败: %s", str(e))
    
    def _load_heic_exif_data(self, heif_file, image, image_path):
        """加载HEIF文件的现有EXIF数据"""
        exif_dict = {"0th": {}, "Exif": {}, "GPS": {}, "1st": {}, "thumbnail": None}
        
        # 从heif_file加载EXIF
        try:
            try:
                if heif_file.exif:
                    heif_exif = piexif.load(heif_file.exif)
                    exif_dict.update(heif_exif)
            except AttributeError:
                pass
        except (IOError, ValueError) as e:
            logger.debug("加载HEIF EXIF数据失败: %s", str(e))
        
        # 从PIL加载EXIF
        self._load_pil_exif_data(image, exif_dict)
        
        # 从image.info加载EXIF
        try:
            if 'exif' in image.info:
                info_exif = piexif.load(image.info['exif'])
                exif_dict.update(info_exif)
        except (KeyError, ValueError, TypeError):
            pass
        
        # 尝试再次打开文件加载EXIF（作为备选方案）
        try:
            with Image.open(image_path) as img:
                # 使用公共API获取EXIF数据
                try:
                    pil_exif = img.getexif()
                except AttributeError:
                    # 兼容旧版本PIL
                    pil_exif = None
                if pil_exif:
                    self._load_pil_exif_data_to_dict(pil_exif, exif_dict)
        except (IOError, OSError, ValueError):
            pass
        
        return exif_dict
    
    def _load_pil_exif_data(self, image, exif_dict):
        """从PIL图像加载EXIF数据到字典"""
        try:
            # 使用公共API获取EXIF数据
            try:
                pil_exif = image.getexif()
            except AttributeError:
                # 兼容旧版本PIL
                pil_exif = None
            if pil_exif:
                self._load_pil_exif_data_to_dict(pil_exif, exif_dict)
        except (IOError, OSError, ValueError, TypeError) as e:
            logger.debug("加载PIL EXIF数据失败: %s", str(e))
    
    def _load_pil_exif_data_to_dict(self, pil_exif, exif_dict):
        """将PIL EXIF数据映射到piexif字典格式"""
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
        
        # 更新各类EXIF字段
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
        # 基本字段映射
        field_mappings = [
            ('title', "0th", piexif.ImageIFD.ImageDescription, "标题: {}", 'utf-8'),
            ('author', "0th", 315, "作者: {}", 'utf-8'),
            ('subject', "0th", piexif.ImageIFD.XPSubject, "主题: {}", 'utf-16le'),
            ('copyright', "0th", piexif.ImageIFD.Copyright, "版权: {}", 'utf-8'),
            ('camera_brand', "0th", piexif.ImageIFD.Make, "相机品牌: {}", 'utf-8'),
            ('camera_model', "0th", piexif.ImageIFD.Model, "相机型号: {}", 'utf-8'),
        ]
        
        for attr_name, section, tag, format_str, encoding in field_mappings:
            attr_value = getattr(self, attr_name, None)
            if attr_value:
                exif_dict[section][tag] = attr_value.encode(encoding)
                updated_fields.append(format_str.format(attr_value))
    
    def _update_heic_rating(self, exif_dict, updated_fields):
        """更新HEIF文件的评分信息
        
        Args:
            exif_dict: EXIF数据字典
            updated_fields: 更新字段列表
        """
        if self.rating:
            exif_dict["0th"][piexif.ImageIFD.Rating] = int(self.rating)
            updated_fields.append(f"评分: {self.rating}星")
    
    def _update_heic_lens_info(self, exif_dict, updated_fields):
        """更新HEIF文件的镜头信息
        
        Args:
            exif_dict: EXIF数据字典
            updated_fields: 更新字段列表
        """
        # 检查是否需要更新镜头信息
        if not (self.lens_brand or self.lens_model):
            return
        
        # 确保Exif部分存在
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        # 更新镜头品牌
        if self.lens_brand:
            exif_dict["Exif"][piexif.ExifIFD.LensMake] = self.lens_brand.encode('utf-8')
            updated_fields.append(f"镜头品牌: {self.lens_brand}")
        
        # 更新镜头型号
        if self.lens_model:
            exif_dict["Exif"][piexif.ExifIFD.LensModel] = self.lens_model.encode('utf-8')
            updated_fields.append(f"镜头型号: {self.lens_model}")
    
    def _update_heic_shoot_time(self, exif_dict, updated_fields, image_path):
        """更新HEIF文件的拍摄时间
        
        Args:
            exif_dict: EXIF数据字典
            updated_fields: 更新字段列表
            image_path: 图像文件路径
        """
        # 使用正确的属性名shoot_time（与__init__一致）
        if self.shoot_time == 0:
            return
        
        # 确保Exif部分存在
        if "Exif" not in exif_dict:
            exif_dict["Exif"] = {}
        
        # 从文件名提取拍摄时间
        if self.shoot_time == 1:
            date_from_filename = self.get_date_from_filename(image_path)
            if date_from_filename:
                time_str = date_from_filename.strftime("%Y:%m:%d %H:%M:%S")
                exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = time_str.encode('utf-8')
                updated_fields.append(f"文件名识别拍摄时间: {time_str}")
        # 使用自定义拍摄时间
        else:
            exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = self.shoot_time.encode('utf-8')
            updated_fields.append(f"拍摄时间: {self.shoot_time}")
    
    def _update_heic_gps_data(self, exif_dict, updated_fields):
        """更新HEIF文件的GPS数据
        
        Args:
            exif_dict: EXIF数据字典
            updated_fields: 更新字段列表
        """
        if self.lat is not None and self.lon is not None:
            exif_dict["GPS"] = self._create_gps_data(self.lat, self.lon)
            
            # 格式化GPS坐标显示
            lat_dir = 'N' if self.lat >= 0 else 'S'
            lon_dir = 'E' if self.lon >= 0 else 'W'
            updated_fields.append(
                f"GPS坐标: {abs(self.lat):.6f}°{lat_dir}, {abs(self.lon):.6f}°{lon_dir}")
    
    def _save_heic_data(self, image, image_path, exif_dict, updated_fields):
        """保存HEIF文件和更新后的EXIF数据"""
        temp_path = image_path + ".tmp"
        try:
            exif_bytes = piexif.dump(exif_dict)
            image.save(temp_path, format="HEIF", exif=exif_bytes)
            os.replace(temp_path, image_path)
            self.log_signal.emit("INFO", f"写入成功 {os.path.basename(image_path)}: {'; '.join(updated_fields)}")
        except (IOError, ValueError, OSError) as e:
            self.log_signal.emit("ERROR", f"写入EXIF数据失败: {str(e)}")
        finally:
            # 确保清理临时文件
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
    
    def _process_heic_format(self, image_path):
        """处理HEIF格式图像文件"""
        if not PILLOW_HEIF_AVAILABLE:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 需要 pillow-heif")
            return
        
        try:
            register_heif_opener()
            heif_file = open_heif(image_path)
            
            # 处理不同版本的pillow-heif API
            if hasattr(heif_file, 'to_pillow'):
                image = heif_file.to_pillow()
            else:
                # 兼容旧版本API，使用Image.open替代直接调用to_pil
                image = Image.open(image_path)
            
            # 加载现有EXIF数据
            exif_dict = self._load_heic_exif_data(heif_file, image, image_path)
            
            # 更新EXIF字段
            updated_fields = self._update_heic_exif_fields(exif_dict, image_path)
            
            # 保存更改
            if updated_fields:
                self._save_heic_data(image, image_path, exif_dict, updated_fields)
            else:
                self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改\n\n"
                                 "可能的原因：\n"
                                 "• 所有EXIF字段均为空")
                
        except (IOError, OSError, ValueError, TypeError, ImportError) as e:
            self.log_signal.emit("ERROR", "处理 %s 时出错: %s", os.path.basename(image_path), str(e))

    def _process_video_format(self, image_path):
        """处理视频文件格式（MOV、MP4、AVI、MKV）
        
        根据文件扩展名调用对应的处理方法。
        
        Args:
            image_path: 要处理的视频文件路径
        """
        file_ext = os.path.splitext(image_path)[1].lower()
        
        if file_ext in ('.mov', '.mp4', '.avi', '.mkv'):
            self._process_video_with_exiftool(image_path)
        else:
            self.log_signal.emit("WARNING", f"不支持的视频格式: {file_ext}")
    
    def _handle_non_ascii_path(self, image_path):
        """处理非ASCII路径，创建临时文件进行处理"""
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
        """准备exiftool命令和参数"""
        exiftool_path = get_resource_path('resources/exiftool/exiftool.exe')
        cmd_parts = [exiftool_path, "-overwrite_original"]
        updated_fields = []
        
        # 添加相机信息
        if self.cameraBrand:
            cmd_parts.append(f'-Make="{self.cameraBrand}"')
            updated_fields.append(f"相机品牌: {self.cameraBrand}")
        
        if self.cameraModel:
            cmd_parts.append(f'-Model="{self.cameraModel}"')
            updated_fields.append(f"相机型号: {self.cameraModel}")
        
        # 添加GPS信息
        if self.lat is not None and self.lon is not None:
            self._add_gps_to_command(cmd_parts, updated_fields)
        
        # 添加时间信息
        if self.shootTime != 0:
            self._add_time_to_command(cmd_parts, updated_fields, original_file_path)
        
        return cmd_parts, updated_fields, exiftool_path
    
    def _add_gps_to_command(self, cmd_parts, updated_fields):
        """向命令中添加GPS信息"""
        lat_dms = self.decimal_to_dms(self.lat)
        lon_dms = self.decimal_to_dms(self.lon)
        cmd_parts.append(f'-GPSLatitude="{lat_dms}"')
        cmd_parts.append(f'-GPSLongitude="{lon_dms}"')
        cmd_parts.append('-GPSLatitudeRef=N' if self.lat >= 0 else '-GPSLatitudeRef=S')
        cmd_parts.append('-GPSLongitudeRef=E' if self.lon >= 0 else '-GPSLongitudeRef=W')
        cmd_parts.append(f'-GPSCoordinates="{self.lat}, {self.lon}"')
        updated_fields.append(f"GPS坐标: {abs(self.lat):.6f}°{'N' if self.lat >= 0 else 'S'}, {abs(self.lon):.6f}°{'E' if self.lon >= 0 else 'W'}")
    
    def _add_time_to_command(self, cmd_parts, updated_fields, original_file_path):
        """向命令中添加时间信息"""
        if self.shootTime == 1:
            date_from_filename = self.get_date_from_filename(original_file_path)
            if date_from_filename:
                self._add_time_fields(cmd_parts, date_from_filename)
                updated_fields.append(f"文件名识别拍摄时间: {date_from_filename.strftime('%Y:%m:%d %H:%M:%S')} (已调整为UTC时间)")
            else:
                self.log_signal.emit("WARNING", f"无法从文件名提取时间: {os.path.basename(original_file_path)}")
        else:
            try:
                datetime.strptime(self.shootTime, "%Y:%m:%d %H:%M:%S")
                local_time = datetime.strptime(self.shootTime, "%Y:%m:%d %H:%M:%S")
                self._add_time_fields(cmd_parts, local_time)
                updated_fields.append(f"拍摄时间: {self.shootTime} (已调整为UTC时间)")
            except ValueError:
                self.log_signal.emit("ERROR", f"拍摄时间格式无效: {self.shootTime}，请使用 YYYY:MM:DD HH:MM:SS 格式")
    
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
        # 复制文件回原始路径
        if temp_file_path and os.path.exists(temp_file_path) and original_file_path != current_path:
            try:
                shutil.copy2(temp_file_path, original_file_path)
            except (IOError, OSError) as e:
                self.log_signal.emit("ERROR", f"复制文件回原始路径失败: {str(e)}")
        
        # 删除临时文件
        self._cleanup_temp_file(temp_file_path)
        
        # 删除临时目录
        if temp_dir and os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
            except OSError as e:
                self.log_signal.emit("WARNING", f"无法删除临时目录: {str(e)}")
    
    def _process_video_with_exiftool(self, image_path):
        """使用exiftool处理视频文件的EXIF数据"""
        if not os.path.exists(image_path):
            self.log_signal.emit("ERROR", f"文件不存在: {image_path}")
            return False
        
        # 处理非ASCII路径
        image_path, original_file_path, temp_file_path, temp_dir = self._handle_non_ascii_path(image_path)
        file_path_normalized = image_path.replace('\\', '/')
        
        try:
            # 准备命令和参数
            cmd_parts, updated_fields, exiftool_path = self._prepare_exiftool_command(original_file_path)
            cmd_parts.append(file_path_normalized)
            
            # 执行exiftool命令
            result = subprocess.run(cmd_parts, capture_output=True, text=True, shell=False, check=False)
            
            if result.returncode != 0:
                self.log_signal.emit("ERROR", f"写入EXIF数据失败: {result.stderr}")
                return False

            if updated_fields:
                self.log_signal.emit("INFO", f"写入成功 {os.path.basename(original_file_path)}: {'; '.join(updated_fields)}")
            
            # 验证写入
            verify_cmd = [exiftool_path, '-CreateDate', '-CreationDate', '-MediaCreateDate', '-DateTimeOriginal', file_path_normalized]
            subprocess.run(verify_cmd, capture_output=True, text=True, shell=False, check=False)
            
            return True
            
        except (IOError, ValueError, OSError, subprocess.SubprocessError) as e:
            self.log_signal.emit("ERROR", f"执行exiftool命令时出错: {str(e)}")
            return False
        finally:
            # 清理临时资源
            self._cleanup_temp_resources(temp_file_path, temp_dir, original_file_path, image_path)

    def _process_raw_format(self, image_path):
        """处理RAW格式图像文件
        
        使用exiftool处理RAW格式文件，更新拍摄时间、标题、作者、版权等元数据。
        
        Args:
            image_path: 要处理的RAW格式文件路径
        """
        # 验证必要条件
        exiftool_path = self._validate_raw_processing(image_path)
        if not exiftool_path:
            return
        
        # 准备EXIF数据
        exif_data, updated_fields = self._prepare_raw_exif_data(image_path)
        if not exif_data:
            self.log_signal.emit("WARNING", f"未对 {os.path.basename(image_path)} 进行任何更改")
            return
        
        # 构建并执行exiftool命令
        self._execute_exiftool_command(exiftool_path, exif_data, image_path, updated_fields)
    
    def _validate_raw_processing(self, image_path):
        """验证RAW处理的必要条件
        
        Args:
            image_path: 要处理的文件路径
            
        Returns:
            str: exiftool路径或None（如果验证失败）
        """
        # 检查文件是否存在
        if not os.path.exists(image_path):
            self.log_signal.emit("ERROR", f"文件不存在: {os.path.basename(image_path)}")
            return None
        
        # 获取并检查exiftool路径
        exiftool_path = os.path.join(os.path.dirname(__file__), "resources", "exiftool", "exiftool.exe")
        if not os.path.exists(exiftool_path):
            self.log_signal.emit("ERROR", "exiftool工具不存在，无法处理RAW格式文件")
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
        
        # 处理拍摄时间 - 注意使用正确的属性名
        self._prepare_raw_shoot_time(exif_data, updated_fields, image_path)
        
        # 处理其他基本字段
        self._prepare_raw_basic_fields(exif_data, updated_fields)
        
        # 处理GPS坐标
        self._prepare_raw_gps_data(exif_data, updated_fields)
        
        return exif_data, updated_fields
    
    def _prepare_raw_shoot_time(self, exif_data, updated_fields, image_path):
        """准备RAW文件的拍摄时间数据
        
        Args:
            exif_data: EXIF数据字典
            updated_fields: 更新字段列表
            image_path: 文件路径
        """
        # 注意使用实例变量名时保持一致（与__init__中定义的一致）
        if self.shoot_time != 0:
            if self.shoot_time == 1:
                date_from_filename = self.get_date_from_filename(image_path)
                if date_from_filename:
                    time_str = date_from_filename.strftime('%Y:%m:%d %H:%M:%S')
                    self._add_time_fields_to_data(exif_data, time_str)
                    updated_fields.append(f"拍摄时间: {time_str}")
            else:
                try:
                    # 验证时间格式
                    datetime.strptime(self.shoot_time, "%Y:%m:%d %H:%M:%S")
                    self._add_time_fields_to_data(exif_data, self.shoot_time)
                    updated_fields.append(f"拍摄时间: {self.shoot_time}")
                except ValueError:
                    self.log_signal.emit("ERROR", f"拍摄时间格式无效: {self.shoot_time}")
    
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
        # 字段映射定义
        field_mappings = [
            ('title', 'ImageDescription', '标题: {}'),
            ('author', 'Artist', '作者: {}'),
            ('copyright', 'Copyright', '版权: {}'),
            ('camera_brand', 'Make', '相机品牌: {}'),
            ('camera_model', 'Model', '相机型号: {}'),
            ('lens_brand', 'LensMake', '镜头品牌: {}'),
            ('lens_model', 'LensModel', '镜头型号: {}')
        ]
        
        # 批量处理基本字段
        for attr_name, exif_key, format_str in field_mappings:
            attr_value = getattr(self, attr_name, None)
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
        # 构建命令参数
        commands = self._build_exiftool_commands(exif_data)
        cmd = [exiftool_path, "-overwrite_original"] + commands + [image_path]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30, check=False)
            
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
        except (subprocess.SubprocessError, IOError, OSError) as e:
            self.log_signal.emit("ERROR", f"处理 {os.path.basename(image_path)} 时出错: {str(e)}")
    
    def _build_exiftool_commands(self, exif_data):
        """构建exiftool命令参数
        
        Args:
            exif_data: EXIF数据字典
            
        Returns:
            list: 命令参数字符串列表
        """
        commands = []
        for key, value in exif_data.items():
            if isinstance(value, str):
                commands.append(f'-{key}="{value}"')
            else:
                commands.append(f'-{key}={value}')
        return commands

    def stop(self):
        """停止处理线程
        
        设置停止标志并等待线程安全退出，最多等待1秒
        """
        self._stop_requested = True
        # 确保线程能够尽快退出
        if self.isRunning():
            self.wait(1000)  # 等待最多1秒让线程完成

    def decimal_to_dms(self, decimal):
        """将十进制坐标转换为度分秒格式"""
        try:
            decimal = abs(decimal)
            
            degrees = int(decimal)
            minutes_decimal = (decimal - degrees) * 60
            minutes = int(minutes_decimal)
            seconds = (minutes_decimal - minutes) * 60
            
            dms_str = f"{degrees} deg {minutes}' {seconds:.2f}\""
            
            return dms_str
        except (ValueError, TypeError, ZeroDivisionError) as e:
            self.log_signal.emit("ERROR", "坐标转换错误: %s", str(e))
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
        """从文件名中提取日期信息
        
        Args:
            image_path: 图像文件路径
            
        Returns:
            datetime: 提取的日期时间对象，失败返回None
        """
        # 提取文件名部分
        name_without_ext = self._get_filename_without_extension(image_path)
        
        # 尝试匹配日期模式
        match = self._find_date_pattern_match(name_without_ext)
        if not match:
            return None
        
        # 提取日期组件
        groups = match.groupdict()
        if not self._has_required_date_components(groups):
            return None
        
        # 构建日期字符串
        date_str_parts, has_time = self._build_date_str_parts(groups, name_without_ext, match)
        
        # 处理缺少时间部分的情况
        if not has_time:
            date_str_parts, has_time = self._try_extract_missing_time(date_str_parts, name_without_ext, groups)
        
        # 生成日期字符串
        date_str = ''.join(date_str_parts)
        
        # 解析日期时间
        return self._parse_date_string(date_str, has_time)
    
    def _get_filename_without_extension(self, image_path):
        """获取不包含扩展名的文件名
        
        Args:
            image_path: 文件路径
            
        Returns:
            str: 不包含扩展名的文件名
        """
        base_name = os.path.basename(image_path)
        return os.path.splitext(base_name)[0]
    
    def _find_date_pattern_match(self, name_without_ext):
        """尝试使用多个模式匹配日期
        
        Args:
            name_without_ext: 不包含扩展名的文件名
            
        Returns:
            re.Match: 匹配对象或None
        """
        # 主要日期模式
        date_pattern = r'(?P<year>\d{4})[年\-\.\/\s]?' \
                      r'(?P<month>1[0-2]|0?[1-9])[月\-\.\/\s]?' \
                      r'(?P<day>3[01]|[12]\d|0?[1-9])[日号\-\.\/\s]?' \
                      r'(?:[^0-9]*?)?' \
                      r'(?P<hour>[0-2]?\d)?' \
                      r'(?P<minute>[0-5]?\d)?' \
                      r'(?P<second>[0-5]?\d)?'
        
        match = re.search(date_pattern, name_without_ext)
        if not match:
            # 备选时间模式
            time_pattern = r'(?P<year>\d{4})[^\d]*(?P<month>1[0-2]|0?[1-9])[^\d]*(?P<day>3[01]|[12]\d|0?[1-9])[^\d]*(?P<hour>[0-2]?\d)(?P<minute>[0-5]\d)(?P<second>[0-5]\d)'
            match = re.search(time_pattern, name_without_ext)
        
        return match
    
    def _has_required_date_components(self, groups):
        """检查是否包含必要的日期组件
        
        Args:
            groups: 正则表达式匹配组字典
            
        Returns:
            bool: 是否包含必要组件
        """
        return all([groups.get('year'), groups.get('month'), groups.get('day')])
    
    def _build_date_str_parts(self, groups, name_without_ext, match):
        """构建日期字符串部分
        
        Args:
            groups: 正则表达式匹配组字典
            name_without_ext: 不包含扩展名的文件名
            match: 匹配对象
            
        Returns:
            tuple: (日期字符串部分列表, 是否包含时间)
        """
        date_str_parts = [
            groups['year'],
            groups['month'].rjust(2, '0'),
            groups['day'].rjust(2, '0')
        ]
        
        has_time = False
        if groups.get('hour'):
            date_str_parts.append(groups['hour'].rjust(2, '0'))
            has_time = True
            self._add_time_components(date_str_parts, groups, name_without_ext, match)
        
        return date_str_parts, has_time
    
    def _add_time_components(self, date_str_parts, groups, name_without_ext, match):
        """添加时间组件到日期字符串部分
        
        Args:
            date_str_parts: 日期字符串部分列表
            groups: 正则表达式匹配组字典
            name_without_ext: 不包含扩展名的文件名
            match: 匹配对象
        """
        if groups.get('minute'):
            date_str_parts.append(groups['minute'].rjust(2, '0'))
            
            if groups.get('second'):
                date_str_parts.append(groups['second'].rjust(2, '0'))
            elif len(groups.get('minute', '')) == 2 and len(groups.get('hour', '')) == 2:
                # 尝试从剩余文本中提取秒数
                self._try_extract_seconds(date_str_parts, groups, name_without_ext, match)
    
    def _try_extract_seconds(self, date_str_parts, groups, name_without_ext, match):
        """尝试从剩余文本中提取秒数
        
        Args:
            date_str_parts: 日期字符串部分列表
            groups: 正则表达式匹配组字典
            name_without_ext: 不包含扩展名的文件名
            match: 匹配对象
        """
        remaining_text = name_without_ext[match.end():]
        if remaining_text and remaining_text[:2].isdigit():
            seconds = remaining_text[:2]
            if 0 <= int(seconds) <= 59:
                date_str_parts.append(seconds)
                groups['second'] = seconds
    
    def _try_extract_missing_time(self, date_str_parts, name_without_ext, groups):
        """尝试从文件名中提取缺失的时间信息
        
        Args:
            date_str_parts: 日期字符串部分列表
            name_without_ext: 不包含扩展名的文件名
            groups: 正则表达式匹配组字典
            
        Returns:
            tuple: (更新后的日期字符串部分列表, 是否包含时间)
        """
        time_match = re.search(r'(?P<hour>[0-2]\d)(?P<minute>[0-5]\d)(?P<second>[0-5]\d)', name_without_ext)
        if time_match:
            groups.update(time_match.groupdict())
            date_str_parts.append(groups['hour'])
            date_str_parts.append(groups['minute'])
            date_str_parts.append(groups['second'])
            return date_str_parts, True
        
        return date_str_parts, False
    
    def _parse_date_string(self, date_str, has_time):
        """解析日期字符串为datetime对象
        
        Args:
            date_str: 日期字符串
            has_time: 是否包含时间
            
        Returns:
            datetime: 解析后的日期时间对象或None
        """
        # 确定可能的格式
        format_map = {
            8: "%Y%m%d",
            12: "%Y%m%d%H%M",
            14: "%Y%m%d%H%M%S"
        }
        
        fmt = format_map.get(len(date_str))
        if not fmt:
            return None
        
        # 尝试解析并验证日期
        try:
            date_obj = datetime.strptime(date_str, fmt)
            if self._is_valid_date(date_obj):
                if not has_time:
                    date_obj = date_obj.replace(hour=0, minute=0, second=0)
                return date_obj
        except ValueError:
            pass
        
        return None
    
    def _is_valid_date(self, date_obj):
        """验证日期是否有效
        
        Args:
            date_obj: datetime对象
            
        Returns:
            bool: 日期是否有效
        """
        return (1900 <= date_obj.year <= 2100 and
                1 <= date_obj.month <= 12 and
                1 <= date_obj.day <= 31)
