import datetime
import json
import os
import subprocess
import logging
from pathlib import Path
import threading

import exifread
import pillow_heif
from PIL import Image
from PyQt6 import QtCore

from common import get_resource_path
from config_manager import config_manager

logger = logging.getLogger(__name__)

IMAGE_EXTENSIONS = (
    '.jpg', '.jpeg', '.png', '.heic', '.tiff', '.tif', '.bmp', '.webp', '.gif', '.svg', 
    '.psd', '.arw', '.cr2', '.cr3', '.nef', '.orf', '.sr2', '.raf', '.dng', '.rw2', 
    '.pef', '.nrw', '.kdc', '.mos', '.iiq', '.fff', '.x3f', '.3fr', '.mef', '.mrw', 
    '.erf', '.raw', '.rwz', '.ari', '.jxr', '.hdp', '.wdp', '.ico', '.exr', '.tga',
    '.pbm', '.pgm', '.ppm', '.pnm', '.hdr', '.avif', '.jxl'
)

VIDEO_EXTENSIONS = (
    '.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.m4v', '.3gp', '.mpeg', '.mpg',
    '.mts', '.mxf', '.webm', '.ogv', '.livp', '.ts', '.m2ts', '.divx', '.f4v', '.vob',
    '.rm', '.rmvb', '.asf', '.swf', '.m4p', '.m4b', '.m4r', '.3g2', '.3gp2', '.ogm',
    '.ogx', '.qt', '.yuv', '.dat', '.m1v', '.m2v', '.m4u', '.mpv', '.nsv', '.svi',
    '.wtv', '.amv', '.drc', '.gifv', '.mng', '.mxf', '.roq', '.y4m'
)

AUDIO_EXTENSIONS = (
    '.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma', '.m4a', '.aiff', '.aif', '.aifc',
    '.ape', '.alac', '.ac3', '.amr', '.au', '.cda', '.dts', '.mka', '.mpc', '.opus',
    '.ra', '.rm', '.tta', '.voc', '.wv', '.8svx', '.aax', '.act', '.awb', '.dss',
    '.dvf', '.gsm', '.iklax', '.ivs', '.m4p', '.mmf', '.msv', '.nmf', '.nsf', '.oga',
    '.spx', '.vox', '.wma', '.wpl', '.xm'
)

DOCUMENT_EXTENSIONS = (
    '.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt', '.xls', '.xlsx', '.ppt', '.pptx',
    '.odp', '.ods', '.csv', '.html', '.htm', '.xml', '.epub', '.mobi', '.azw', '.azw3',
    '.fb2', '.lit', '.lrf', '.pdb', '.prc', '.rb', '.tcr', '.pdb', '.oxps', '.xps',
    '.pages', '.numbers', '.key', '.md', '.tex', '.log', '.wpd', '.wps', '.abw',
    '.zabw', '.123', '.602', '.hwp', '.lwp', '.mw', '.nb', '.nbp', '.odm', '.sxw',
    '.uot', '.vor', '.wpt', '.wri', '.xmind'
)

ARCHIVE_EXTENSIONS = (
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.lz', '.lzma', '.lzo',
    '.z', '.Z', '.tgz', '.tbz2', '.txz', '.tlz', '.tlzma', '.tlzo', '.tz', '.tZ',
    '.cab', '.deb', '.rpm', '.jar', '.war', '.ear', '.sar', '.cpio', '.iso', '.img',
    '.dmg', '.hfs', '.hfsx', '.udf', '.xar', '.zoo', '.arc', '.arj', '.lha', '.lzh',
    '.pak', '.pk3', '.pk4', '.vpk', '.wim', '.swm', '.esd', '.msu', '.msp', '.msi',
    '.appx', '.appxbundle', '.xap', '.snap', '.flatpak', '.appimage', '.r0', '.r1',
    '.r2', '.r3', '.s7z', '.ace', '.cpt', '.dd', '.dgc', '.gca', '.ha', '.ice',
    '.ipg', '.kgb', '.lbr', '.lqr', '.lzx', '.pak', '.paq6', '.paq7', '.paq8',
    '.pea', '.pf', '.pim', '.pit', '.qda', '.rk', '.sda', '.sea', '.sit', '.sitx',
    '.sqx', '.tar.z', '.uc2', '.uca', '.uha', '.ea', '.yz', '.zap', '.zipx', '.zoo',
    '.zpaq', '.zz'
)

SUPPORTED_EXTENSIONS = IMAGE_EXTENSIONS + VIDEO_EXTENSIONS + AUDIO_EXTENSIONS + DOCUMENT_EXTENSIONS + ARCHIVE_EXTENSIONS

FILE_TYPE_CATEGORIES = {
    '图像': IMAGE_EXTENSIONS,
    '视频': VIDEO_EXTENSIONS,
    '音乐': AUDIO_EXTENSIONS,
    '文档': DOCUMENT_EXTENSIONS,
    '压缩包': ARCHIVE_EXTENSIONS,
    '其他': ()
}

def get_file_type(file_path):
    ext = file_path.suffix.lower()
    for file_type, extensions in FILE_TYPE_CATEGORIES.items():
        if ext in extensions:
            return file_type
    return '其他'

class SmartArrangeThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, folders=None, classification_structure=None, file_name_structure=None,
                 destination_root=None, separator="-", time_derive="文件创建时间"):
        super().__init__(parent)
        self.parent = parent
        self.folders = folders or []
        self.classification_structure = classification_structure
        self.file_name_structure = file_name_structure
        self.destination_root = destination_root
        self.separator = separator
        self.time_derive = time_derive
        self._is_running = True
        self._stop_flag = False
        self._stop_lock = threading.Lock()
        self.total_files = 0
        self.processed_files = 0
        self.processed_lock = threading.Lock()
        self.log_signal = parent.log_signal if parent else None
        self.files_to_rename = []
        self.files_lock = threading.Lock()
        # 初始化地理数据属性
        self.city_data = {}
        self.province_data = {}

    def calculate_total_files(self):
        try:
            self.total_files = 0
            for folder_info in self.folders:
                folder_path = Path(folder_info['path'])
                if not self._validate_folder_path(folder_path):
                    continue
                    
                if folder_info.get('include_sub', 0):
                    self._count_files_recursive(folder_path)
                else:
                    self._count_files_direct(folder_path)
                    
        except Exception as e:
            self.log("ERROR", f"计算文件数量失败: {str(e)}")
            self.total_files = 0

    def load_geographic_data(self):
        try:
            with open(get_resource_path('resources/json/City_Reverse_Geocode.json'), 'r', encoding='utf-8') as f:
                self.city_data = json.load(f)
            with open(get_resource_path('resources/json/Province_Reverse_Geocode.json'), 'r', encoding='utf-8') as f:
                self.province_data = json.load(f)
        except Exception:
            self.city_data, self.province_data = {'features': []}, {'features': []}

    def run(self):
        try:
            self.load_geographic_data()
            self.calculate_total_files()
            
            success_count = 0
            fail_count = 0
            self.processed_files = 0

            for folder_info in self.folders:
                if self._stop_flag:
                    self.log("WARNING", "您已经取消了整理文件的操作")
                    break
                    
                # 增强的目标文件夹验证
                if not self._validate_destination_folder(folder_info):
                    continue
                    
                try:
                    if not self.classification_structure and not self.file_name_structure:
                        self.organize_without_classification(folder_info['path'])
                    else:
                        self.process_folder_with_classification(folder_info)
                    success_count += 1
                except (OSError, IOError) as e:
                    self.log("ERROR", f"文件操作失败 {folder_info['path']}: {str(e)}")
                    fail_count += 1
                except Exception as e:
                    self.log("ERROR", f"处理文件夹失败 {folder_info['path']}: {str(e)}")
                    fail_count += 1
            
            if not self._stop_flag:
                try:
                    self.process_renaming()
                    success_count = len(self.files_to_rename) - fail_count
                except (OSError, IOError) as e:
                    self.log("ERROR", f"重命名文件失败: {str(e)}")
                    fail_count += 1
                except Exception as e:
                    self.log("ERROR", f"重命名过程出错: {str(e)}")
                    fail_count += 1
                
                if not self.destination_root:
                    try:
                        self.delete_empty_folders()
                    except Exception as e:
                        self.log("WARNING", f"删除空文件夹时出错了: {str(e)}")

                self.log("DEBUG", "="*40)
                self.log("DEBUG", f"文件整理完成了，成功处理了 {success_count} 个文件，失败了 {fail_count} 个文件")
                self.log("DEBUG", "="*3+"LeafView © 2025 Yangshengzhou.All Rights Reserved"+"="*3)
                self.progress_signal.emit(100)
            else:
                self.log("WARNING", "您已经取消了整理文件的操作")
                
        except Exception as e:
            self.log("ERROR", f"整理文件时遇到了严重问题: {str(e)}")

    def process_folder_with_classification(self, folder_info):
        folder_path = Path(folder_info['path'])
        
        if folder_info.get('include_sub', 0):
            for root, _, files in os.walk(folder_path):
                # 批量处理，每批处理100个文件
                batch_size = 100
                for i in range(0, len(files), batch_size):
                    if self.is_stopped():
                        self.log("WARNING", "您已经取消了当前文件夹的处理")
                        return
                    
                    batch_files = files[i:i + batch_size]
                    for file in batch_files:
                        if self.is_stopped():
                            self.log("WARNING", "您已经取消了当前文件夹的处理")
                            return
                        full_file_path = Path(root) / file
                        if self.destination_root:
                            self.process_single_file(full_file_path)
                        else:
                            self.process_single_file(full_file_path, base_folder=folder_path)
                        
                        with self.processed_lock:
                            self.processed_files += 1
                        
                        if self.total_files > 0:
                            percent_complete = int((self.processed_files / self.total_files) * 80)
                            self.progress_signal.emit(percent_complete)
                    
                    # 批次之间短暂休息，减少CPU占用
                    time.sleep(0.01)
        else:
            # 获取文件列表，分批处理
            try:
                all_files = [f for f in os.listdir(folder_path) if (folder_path / f).is_file()]
                batch_size = 100
                
                for i in range(0, len(all_files), batch_size):
                    if self.is_stopped():
                        self.log("WARNING", "文件夹处理被用户中断")
                        return
                    
                    batch_files = all_files[i:i + batch_size]
                    for file in batch_files:
                        if self.is_stopped():
                            self.log("WARNING", "文件夹处理被用户中断")
                            return
                        full_file_path = folder_path / file
                        # 如果有目标根路径（复制操作），则不传递base_folder参数
                        if self.destination_root:
                            self.process_single_file(full_file_path)
                        else:
                            self.process_single_file(full_file_path)
                        
                        with self.processed_lock:
                            self.processed_files += 1
                        
                        if self.total_files > 0:
                            percent_complete = int((self.processed_files / self.total_files) * 80)
                            self.progress_signal.emit(percent_complete)
                    
                    # 批次之间短暂休息，减少CPU占用
                    time.sleep(0.01)
                    
            except Exception as e:
                self.log("ERROR", f"处理文件夹时出错: {str(e)}")

    def process_renaming(self):
        # 初始化统计变量
        total_rename_files = len(self.files_to_rename)
        renamed_files = 0
        failed_files = 0
        skipped_files = 0
        
        self.log("INFO", f"开始处理 {total_rename_files} 个文件")
        
        for idx, file_info in enumerate(self.files_to_rename):
            if self._stop_flag:
                self.log("WARNING", "文件重命名操作被用户中断")
                break
            
            old_path = Path(file_info['old_path'])
            new_path = Path(file_info['new_path'])
            
            # 验证源文件是否存在
            if not old_path.exists():
                self.log("WARNING", f"源文件不存在，跳过: {old_path}")
                skipped_files += 1
                continue
            
            try:
                # 增强的目录创建，增加错误处理
                try:
                    new_path.parent.mkdir(parents=True, exist_ok=True)
                    # 验证目录是否真的创建成功
                    if not new_path.parent.exists():
                        raise OSError(f"无法创建目标目录: {new_path.parent}")
                    # 验证目录是否可写
                    if not os.access(new_path.parent, os.W_OK):
                        raise PermissionError(f"没有写入权限: {new_path.parent}")
                except (OSError, PermissionError) as e:
                    self.log("ERROR", f"创建目录失败 {new_path.parent}: {str(e)}")
                    failed_files += 1
                    continue
                
                # 改进的文件冲突检测
                base_name = new_path.stem
                ext = new_path.suffix
                counter = 1
                unique_path = new_path
                
                # 使用更智能的文件名冲突解决
                while unique_path.exists():
                    # 检查是否是同一个文件（硬链接或相同内容）
                    if old_path.resolve() == unique_path.resolve():
                        self.log("INFO", f"源文件和目标文件相同，跳过: {old_path}")
                        skipped_files += 1
                        unique_path = None
                        break
                    
                    # 生成新的唯一文件名
                    unique_path = new_path.parent / f"{base_name}_{counter}{ext}"
                    counter += 1
                    
                    # 防止无限循环
                    if counter > 1000:
                        self.log("ERROR", f"无法找到唯一文件名，跳过: {old_path}")
                        unique_path = None
                        failed_files += 1
                        break
                
                if unique_path is None:
                    continue
                
                # 执行文件操作，增加更多错误处理
                try:
                    if self.destination_root:
                        import shutil
                        # 复制文件时保留元数据
                        shutil.copy2(old_path, unique_path)
                        self.log("INFO", f"复制文件成功: {old_path.name} -> {unique_path.name}")
                    else:
                        if old_path.parent == unique_path.parent:
                            # 同一目录下重命名
                            old_path.rename(unique_path)
                            self.log("DEBUG", f"重命名文件成功: {old_path.name} -> {unique_path.name}")
                        else:
                            # 跨目录移动
                            import shutil
                            # 先尝试直接移动
                            try:
                                shutil.move(old_path, unique_path)
                            except (OSError, PermissionError):
                                # 如果移动失败，尝试复制后删除
                                self.log("WARNING", f"直接移动失败，尝试复制后删除: {old_path}")
                                shutil.copy2(old_path, unique_path)
                                old_path.unlink()
                            self.log("INFO", f"移动文件成功: {old_path.name} -> {unique_path}")
                    
                    renamed_files += 1
                    
                    # 更新进度条，提供更平滑的进度更新
                    if total_rename_files > 0:
                        rename_progress = int((renamed_files / total_rename_files) * 20)
                        total_progress = 80 + rename_progress
                        self.progress_signal.emit(min(total_progress, 99))
                    
                except (OSError, PermissionError, IOError) as e:
                    self.log("ERROR", f"文件操作失败 {old_path} -> {unique_path}: {str(e)}")
                    failed_files += 1
            
            except Exception as e:
                self.log("ERROR", f"处理文件时发生未预期错误 {old_path}: {str(e)}")
                failed_files += 1
            
            # 定期更新进度，即使文件处理失败
            if idx % 10 == 0 or idx == total_rename_files - 1:
                self.progress_signal.emit(min(80 + int((idx + 1) / total_rename_files * 20), 99))
        
        # 最终进度更新
        self.progress_signal.emit(99)
        
        # 输出统计信息
        self.log("INFO", f"文件整理完成 - 成功: {renamed_files}, 失败: {failed_files}, 跳过: {skipped_files}")

    def organize_without_classification(self, folder_path):
        folder_path = Path(folder_path)
        
        self.log("DEBUG", f"开始处理文件夹: {folder_path}")
        
        file_count = 0
        for root, _, files in os.walk(folder_path):
            if self._stop_flag:
                self.log("WARNING", "文件提取操作被用户中断")
                break
            
            for file in files:
                if self._stop_flag:
                    self.log("WARNING", "您已经取消了文件提取操作")
                    break
                
                file_path = Path(root) / file
                
                if self.destination_root:
                    target_path = Path(self.destination_root) / file_path.name
                else:
                    target_path = folder_path / file_path.name
                
                if file_path != target_path:
                    try:
                        import shutil
                        if self.destination_root:
                            shutil.copy2(file_path, target_path)
                            self.log("INFO", f"复制文件: {file_path} -> {target_path}")
                        else:
                            shutil.move(file_path, target_path)
                            self.log("INFO", f"移动文件: {file_path} -> {target_path}")
                        
                        file_count += 1
                        
                        self.processed_files += 1
                        if self.total_files > 0:
                            percent_complete = int((self.processed_files / self.total_files) * 80)
                            self.progress_signal.emit(percent_complete)
                    except Exception as e:
                        self.log("ERROR", f"处理文件 {file_path} 时出错: {str(e)}")
        
        operation_type = "复制" if self.destination_root else "移动"
        self.log("INFO", f"处理完成，共{operation_type} {file_count} 个文件")

    def delete_empty_folders(self):
        deleted_count = 0
        processed_folders = set()
        
        source_folders = [Path(folder_info['path']).resolve() for folder_info in self.folders]
        
        for folder_info in self.folders:
            folder_path = Path(folder_info['path'])
            processed_folders.add(folder_path.resolve())
            
            if folder_info.get('include_sub', 0):
                for root, _, _ in os.walk(folder_path):
                    processed_folders.add(Path(root).resolve())
        
        for folder in processed_folders:
            if self._stop_flag:
                self.log("WARNING", "您已经取消了空文件夹删除操作")
                break
            
            if folder.exists() and folder.is_dir():
                try:
                    deleted_in_this_folder = self._recursive_delete_empty_folders(folder, source_folders)
                    deleted_count += deleted_in_this_folder
                except Exception as e:
                    self.log("ERROR", f"删除文件夹 {folder} 时出错: {str(e)}")
        
        self.log("WARNING", f"已为您删除了 {deleted_count} 个空文件夹")
    
    def stop(self):
        """停止线程操作"""
        with self._stop_lock:
            self._stop_flag = True
        self.log("INFO", "正在停止智能整理操作...")
    
    def is_stopped(self):
        """线程安全的停止状态检查"""
        with self._stop_lock:
            return self._stop_flag

    def _validate_folder_path(self, folder_path):
        """验证文件夹路径的有效性"""
        if not folder_path.exists():
            self.log("WARNING", f"文件夹不存在: {folder_path}")
            return False
            
        if not folder_path.is_dir():
            self.log("WARNING", f"路径不是文件夹: {folder_path}")
            return False
            
        # 检查读取权限
        try:
            folder_path.iterdir()
            return True
        except PermissionError:
            self.log("ERROR", f"没有权限访问文件夹: {folder_path}")
            return False
        except Exception as e:
            self.log("ERROR", f"文件夹验证失败: {str(e)}")
            return False

    def _validate_destination_folder(self, folder_info):
        """验证目标文件夹配置"""
        if not self.destination_root:
            return True
            
        try:
            destination_path = Path(self.destination_root).resolve()
            folder_path = Path(folder_info['path']).resolve()
            
            # 检查目标文件夹是否是源文件夹的子文件夹
            if len(destination_path.parts) > len(folder_path.parts) and destination_path.parts[:len(folder_path.parts)] == folder_path.parts:
                self.log("ERROR", "目标文件夹不能是要整理的文件夹的子文件夹，这样会导致重复处理！")
                return False
                
            # 检查目标文件夹是否存在，不存在则创建
            if not destination_path.exists():
                destination_path.mkdir(parents=True, exist_ok=True)
                self.log("INFO", f"创建目标文件夹: {destination_path}")
                
            return True
            
        except Exception as e:
            self.log("ERROR", f"目标文件夹验证失败: {str(e)}")
            return False

    def _count_files_recursive(self, folder_path):
        """递归统计文件数量"""
        try:
            for root, _, files in os.walk(folder_path):
                if self._stop_flag:
                    break
                try:
                    self.total_files += len(files)
                except Exception as e:
                    logger.error(f"统计文件数量失败 {root}: {str(e)}")
                    self.log("WARNING", f"部分文件统计失败: {str(e)}")
        except Exception as e:
            logger.error(f"递归遍历文件夹失败 {folder_path}: {str(e)}")
            self.log("ERROR", f"文件夹遍历失败: {str(e)}")

    def _count_files_direct(self, folder_path):
        """直接统计文件夹内文件数量"""
        try:
            files = os.listdir(folder_path)
            self.total_files += len([f for f in files if (folder_path / f).is_file()])
        except PermissionError:
            logger.error(f"没有权限访问文件夹: {folder_path}")
            self.log("ERROR", f"没有权限访问文件夹: {folder_path}")
        except Exception as e:
            logger.error(f"列出文件夹内容失败 {folder_path}: {str(e)}")
            self.log("ERROR", f"读取文件夹失败: {str(e)}")

    def _recursive_delete_empty_folders(self, folder_path, source_folders):
        deleted_count = 0
        
        if not folder_path.exists() or not folder_path.is_dir():
            return deleted_count
        
        if self._is_protected_folder(folder_path, source_folders):
            return deleted_count
            
        try:
            for item in folder_path.iterdir():
                if item.is_dir():
                    deleted_count += self._recursive_delete_empty_folders(item, source_folders)
            
            if not any(folder_path.iterdir()):
                if folder_path != folder_path.resolve().anchor:
                    try:
                        folder_path.rmdir()
                        deleted_count += 1
                    except Exception as e:
                        self.log("WARNING", f"无法删除文件夹 {folder_path}: {str(e)}")
                         
        except PermissionError:
            self.log("WARNING", f"权限不足，无法访问文件夹: {folder_path}")
        except Exception as e:
            self.log("ERROR", f"处理文件夹 {folder_path} 时出错: {str(e)}")
        
        return deleted_count
        
    def _is_protected_folder(self, folder_path, source_folders):
        if folder_path in source_folders:
            return True
            
        windows_system_dirs = [
            Path(os.environ.get('WINDIR', 'C:\Windows')),
            Path(os.environ.get('SYSTEMROOT', 'C:\Windows')),
            Path(os.environ.get('ProgramFiles', 'C:\Program Files')),
            Path(os.environ.get('ProgramFiles(x86)', 'C:\Program Files (x86)')),
            Path(os.path.expanduser('~')),
            Path('C:\\')
        ]
        
        folder_path = folder_path.resolve()
        for system_dir in windows_system_dirs:
            if system_dir and folder_path.is_relative_to(system_dir):
                return True
                
        return False

    def log(self, level, message):
        # 简化日志记录
        log_message = f"[{level}] {message}"
        self.log_signal.emit(level, log_message, "#000000")
        
        # 仅记录关键错误
        if level == "ERROR":
            logger.error(message)
    
    def get_exif_data(self, file_path):
        exif_data = {}
        file_path_obj = Path(file_path)
        suffix = file_path_obj.suffix.lower()
        
        # 文件大小检查，避免处理过大的文件
        try:
            file_size = file_path_obj.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB限制
                exif_data['DateTime'] = datetime.datetime.fromtimestamp(file_path_obj.stat().st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                return exif_data
        except Exception:
            pass
        
        # 获取文件系统时间
        try:
            create_time = datetime.datetime.fromtimestamp(file_path_obj.stat().st_ctime)
            modify_time = datetime.datetime.fromtimestamp(file_path_obj.stat().st_mtime)
        except Exception:
            current_time = datetime.datetime.now()
            create_time = modify_time = current_time
        
        date_taken = None
        
        try:
            if suffix in ('.jpg', '.jpeg', '.tiff', '.tif'):
                date_taken = self._process_image_exif(file_path_obj, exif_data)
                if not date_taken:
                    date_taken = self._try_alternative_exif_extraction(file_path_obj, exif_data)
            elif suffix == '.heic':
                date_taken = self._process_heic_exif(file_path_obj, exif_data)
            elif suffix == '.png':
                date_taken = self._process_png_exif(file_path_obj)
            elif suffix in ('.mov', '.qt'):
                date_taken = self._process_mov_exif(file_path_obj, exif_data)
            elif suffix in ('.mp4', '.m4v'):
                date_taken = self._process_mp4_exif(file_path_obj, exif_data)
            elif suffix.lower() in ('.arw', '.cr2', '.cr3', '.nef', '.orf', '.sr2', '.raf', '.dng', '.rw2', 
                                  '.pef', '.nrw', '.kdc', '.mos', '.iiq', '.fff', '.x3f', '.3fr', '.mef', 
                                  '.mrw', '.erf', '.raw', '.rwz', '.ari'):
                # 处理RAW格式
                try:
                    metadata = self._get_video_metadata(file_path, timeout=20)
                    if metadata and 'DateTime' in metadata:
                        try:
                            date_str = metadata['DateTime']
                            date_taken = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            for key, value in metadata.items():
                                if key not in exif_data:
                                    exif_data[key] = value
                        except (ValueError, TypeError):
                            pass
                    
                    if not date_taken:
                        date_taken = self._process_raw_exif(file_path_obj, exif_data)
                except Exception:
                    pass
            elif suffix in VIDEO_EXTENSIONS:
                # 处理其他视频格式
                try:
                    metadata = self._get_video_metadata(file_path, timeout=15)
                    if metadata and 'DateTime' in metadata:
                        try:
                            date_str = metadata['DateTime']
                            date_taken = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            for key, value in metadata.items():
                                if key not in exif_data:
                                    exif_data[key] = value
                        except (ValueError, TypeError):
                            pass
                except Exception:
                    pass
            elif suffix in AUDIO_EXTENSIONS:
                # 处理音频文件
                try:
                    metadata = self._get_video_metadata(file_path, timeout=10)
                    if metadata and 'DateTime' in metadata:
                        try:
                            date_str = metadata['DateTime']
                            date_taken = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                            for key, value in metadata.items():
                                if key not in exif_data:
                                    exif_data[key] = value
                        except (ValueError, TypeError):
                            pass
                except Exception:
                    pass

            # 确定最终的日期时间
            final_datetime = self._determine_best_datetime(date_taken, create_time, modify_time)
            exif_data['DateTime'] = final_datetime
                
        except Exception:
            # 出错时使用修改时间
            exif_data['DateTime'] = modify_time.strftime('%Y-%m-%d %H:%M:%S')
        
        # 添加基本文件信息
        exif_data['file_extension'] = suffix
        try:
            exif_data['file_size'] = file_path_obj.stat().st_size
        except:
            pass
            
        return exif_data
        
    def _try_alternative_exif_extraction(self, file_path_obj, exif_data):
        try:
            from PIL import Image, ExifTags
            with Image.open(file_path_obj) as img:
                try:
                    exif = img._getexif()
                    if exif:
                        exif_translated = {}
                        for tag, value in exif.items():
                            tag_name = ExifTags.TAGS.get(tag, tag)
                            exif_translated[tag_name] = value
                        
                        if 'DateTime' in exif_translated:
                            try:
                                date_taken = datetime.datetime.strptime(exif_translated['DateTime'], '%Y:%m:%d %H:%M:%S')
                                if 'Make' in exif_translated:
                                    exif_data['camera'] = exif_translated['Make']
                                if 'Model' in exif_translated:
                                    exif_data['model'] = exif_translated['Model']
                                return date_taken
                            except ValueError:
                                pass
                except (ValueError, TypeError, KeyError):
                    pass
        except (OSError, ValueError, TypeError):
            pass
        
        return None

    def _process_image_exif(self, file_path, exif_data):
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            date_taken = self.parse_exif_datetime(tags)
            self._extract_gps_and_camera_info(tags, exif_data)
            return date_taken
        except Exception:
            return None

    def _process_raw_exif(self, file_path, exif_data):
        # 文件大小检查
        try:
            file_size = os.path.getsize(file_path)
            if file_size > 200 * 1024 * 1024:  # 200MB限制
                return None
        except (OSError, FileNotFoundError):
            pass
        
        # 构建exiftool路径
        exiftool_path = os.path.join(os.path.dirname(__file__), "resources", "exiftool", "exiftool.exe")
        
        if not os.path.exists(exiftool_path):
            return None
        
        try:
            # 使用exiftool读取EXIF信息
            cmd = [exiftool_path, file_path]
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=15, check=False)
            
            if result.returncode != 0:
                return None
            
            exif_data_str = result.stdout.decode('utf-8', errors='ignore')
            
            # 解析拍摄时间
            date_taken = self._parse_raw_datetime(exif_data_str)
            
            # 提取相机和GPS信息
            self._extract_raw_metadata(exif_data_str, exif_data)
            
            return date_taken
                
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    def _parse_raw_datetime(self, exif_data_str):
        """从RAW格式的EXIF数据中解析拍摄时间"""
        date_patterns = [
            'Date/Time Original',
            'Create Date', 
            'Modify Date',
            'DateTimeOriginal',
            'Creation Date'
        ]
        
        for line in exif_data_str.split('\n'):
            for pattern in date_patterns:
                if pattern in line:
                    try:
                        date_str = line.split(':', 1)[1].strip()
                        date_taken = self.parse_datetime(date_str)
                        if date_taken:
                            return date_taken
                    except (ValueError, IndexError):
                        continue
        return None
    
    def _extract_raw_metadata(self, exif_data_str, exif_data):
        """从RAW格式的EXIF数据中提取相机和GPS信息"""
        # 提取相机信息
        for line in exif_data_str.split('\n'):
            if 'Make' in line and ':' in line:
                try:
                    make_value = line.split(':', 1)[1].strip()
                    exif_data['Make'] = make_value
                except (ValueError, IndexError):
                    pass
            elif 'Model' in line and ':' in line:
                try:
                    model_value = line.split(':', 1)[1].strip()
                    exif_data['Model'] = model_value
                except (ValueError, IndexError):
                    pass
            elif 'Lens Model' in line and ':' in line:
                try:
                    lens_model = line.split(':', 1)[1].strip()
                    exif_data['LensModel'] = lens_model
                except (ValueError, IndexError):
                    pass
        
        # 提取GPS信息
        gps_lat = None
        gps_lon = None
        for line in exif_data_str.split('\n'):
            if 'GPS Latitude' in line and ':' in line:
                try:
                    lat_str = line.split(':', 1)[1].strip()
                    gps_lat = self._parse_dms_coordinate(lat_str)
                except (ValueError, IndexError):
                    pass
            elif 'GPS Longitude' in line and ':' in line:
                try:
                    lon_str = line.split(':', 1)[1].strip()
                    gps_lon = self._parse_dms_coordinate(lon_str)
                except (ValueError, IndexError):
                    pass
        
        if gps_lat is not None and gps_lon is not None:
            exif_data['GPS GPSLatitude'] = gps_lat
            exif_data['GPS GPSLongitude'] = gps_lon

    def _process_heic_exif(self, file_path, exif_data):
        heif_file = pillow_heif.read_heif(file_path)
        exif_raw = heif_file.info.get('exif', b'')
        if exif_raw.startswith(b'Exif\x00\x00'):
            exif_raw = exif_raw[6:]
        if exif_raw:
            tags = exifread.process_file(io.BytesIO(exif_raw), details=False)
            date_taken = self.parse_exif_datetime(tags)
            self._extract_gps_and_camera_info(tags, exif_data)
            return date_taken
        return None

    def _process_png_exif(self, file_path):
        try:
            with Image.open(file_path) as img:
                creation_time = img.info.get('Creation Time')
                if creation_time:
                    return self.parse_datetime(creation_time)
        except Exception:
            pass
        return None

    def _process_mp4_exif(self, file_path, exif_data):
        video_metadata = self._get_video_metadata(file_path)
        if not video_metadata:
            return None
            
        date_taken = None
        date_keys = [
            'Create Date', 'Creation Date', 'Media Create Date', 'Date/Time Original',
            'Track Create Date', 'Creation Date (Windows)', 'Modify Date'
        ]
        
        for key in date_keys:
            if key in video_metadata:
                date_str = video_metadata[key]
                if '+' in date_str or '-' in date_str[-5:]:
                    date_taken = self.parse_datetime(date_str)
                else:
                    try:
                        dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        utc_dt = dt.replace(tzinfo=datetime.timezone.utc)
                        date_taken = utc_dt.astimezone().replace(tzinfo=None)
                    except ValueError:
                        date_taken = self.parse_datetime(date_str)
                if date_taken:
                    break
        
        make_keys = [
            'Make', 'Camera Make', 'Manufacturer', 'Camera Manufacturer'
        ]
        
        for key in make_keys:
            if key in video_metadata:
                make_value = video_metadata[key]
                if make_value:
                    # Remove quotes from camera brand name
                    if isinstance(make_value, str):
                        make_value = make_value.strip().strip('"\'')
                    exif_data['Make'] = make_value
                break
        
        model_keys = [
            'Model', 'Camera Model', 'Device Model', 'Product Name'
        ]
        
        for key in model_keys:
            if key in video_metadata:
                model_value = video_metadata[key]
                if model_value:
                    # Remove quotes from camera model name
                    if isinstance(model_value, str):
                        model_value = model_value.strip().strip('"\'')
                    exif_data['Model'] = model_value
                break
        
        gps_found = False
        for key, value in video_metadata.items():
            if 'gps' in key.lower() or 'location' in key.lower():
                gps_found = True
                if 'Coordinates' in key or 'Position' in key:
                    lat, lon = self._parse_combined_coordinates(value)
                    if lat is not None and lon is not None:
                        exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
                elif 'Latitude' in key:
                    lat = self._parse_dms_coordinate(value)
                    if lat is not None:
                        exif_data['GPS GPSLatitude'] = lat
                elif 'Longitude' in key:
                    lon = self._parse_dms_coordinate(value)
                    if lon is not None:
                        exif_data['GPS GPSLongitude'] = lon
        
        if gps_found and ('GPS GPSLatitude' not in exif_data or 'GPS GPSLongitude' not in exif_data):
            lat = exif_data.get('GPS GPSLatitude')
            lon = exif_data.get('GPS GPSLongitude')
        return date_taken

    def _process_mov_exif(self, file_path, exif_data):
        video_metadata = self._get_video_metadata(file_path)
        if not video_metadata:
            return None
            
        date_taken = None
        
        date_keys = [
            'Create Date', 'Creation Date', 'DateTimeOriginal',
            'Media Create Date', 'Date/Time Original', 'Date/Time Created'
        ]
        
        for key in date_keys:
            if key in video_metadata:
                date_str = video_metadata[key]
                if '+' in date_str or '-' in date_str[-5:]:
                    date_taken = self.parse_datetime(date_str)
                else:
                    try:
                        dt = datetime.datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                        utc_dt = dt.replace(tzinfo=datetime.timezone.utc)
                        date_taken = utc_dt.astimezone().replace(tzinfo=None)
                    except ValueError:
                        date_taken = self.parse_datetime(date_str)
                
                if date_taken:
                    break
        
        make_keys = [
            'Make', 'Camera Make', 'Manufacturer', 'Camera Manufacturer'
        ]
        
        for key in make_keys:
            if key in video_metadata:
                make_value = video_metadata[key]
                if make_value:
                    # Remove quotes from camera brand name
                    if isinstance(make_value, str):
                        make_value = make_value.strip().strip('"\'')
                    exif_data['Make'] = make_value
                    if not date_taken:
                        date_taken = make_value
                break
        
        model_keys = [
            'Model', 'Camera Model', 'Device Model', 'Product Name'
        ]
        
        for key in model_keys:
            if key in video_metadata:
                model_value = video_metadata[key]
                if model_value:
                    exif_data['Model'] = model_value
                break
        
        gps_found = False
        for key, value in video_metadata.items():
            if 'gps' in key.lower() or 'location' in key.lower():
                gps_found = True
                if 'Coordinates' in key or 'Position' in key:
                    lat, lon = self._parse_combined_coordinates(value)
                    if lat is not None and lon is not None:
                        exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
                elif 'Latitude' in key:
                    lat = self._parse_dms_coordinate(value)
                    if lat is not None:
                        exif_data['GPS GPSLatitude'] = lat
                elif 'Longitude' in key:
                    lon = self._parse_dms_coordinate(value)
                    if lon is not None:
                        exif_data['GPS GPSLongitude'] = lon
        
        if gps_found and ('GPS GPSLatitude' not in exif_data or 'GPS GPSLongitude' not in exif_data):
            lat = exif_data.get('GPS GPSLatitude')
            lon = exif_data.get('GPS GPSLongitude')
            if lat is not None and lon is not None:
                self.log("DEBUG", f"GPS坐标: 纬度={lat}, 经度={lon}")
        return date_taken

    def _determine_best_datetime(self, date_taken, create_time, modify_time):
        if self.time_derive == "拍摄日期":
            return date_taken.strftime('%Y-%m-%d %H:%M:%S') if date_taken else None
        elif self.time_derive == "创建时间":
            return create_time.strftime('%Y-%m-%d %H:%M:%S')
        elif self.time_derive == "修改时间":
            return modify_time.strftime('%Y-%m-%d %H:%M:%S')
        else:
            times = [t for t in [date_taken, create_time, modify_time] if t is not None]
            earliest_time = min(times) if times else modify_time
            return earliest_time.strftime('%Y-%m-%d %H:%M:%S')

    def _extract_gps_and_camera_info(self, tags, exif_data):
        lat_ref = str(tags.get('GPS GPSLatitudeRef', '')).strip()
        lon_ref = str(tags.get('GPS GPSLongitudeRef', '')).strip()
        
        gps_lat = tags.get('GPS GPSLatitude')
        gps_lon = tags.get('GPS GPSLongitude')
        
        if gps_lat and gps_lon:
            # 检查GPS数据是否已经是浮点数格式
            if isinstance(gps_lat, (int, float)) and isinstance(gps_lon, (int, float)):
                # 如果是浮点数格式，直接使用
                lat = gps_lat
                lon = gps_lon
            else:
                try:
                    # 尝试作为度分秒数据转换
                    lat = self.convert_to_degrees(gps_lat)
                    lon = self.convert_to_degrees(gps_lon)
                except (AttributeError, TypeError, ValueError):
                    # 如果转换失败，尝试转换为浮点数
                    try:
                        lat = float(gps_lat)
                        lon = float(gps_lon)
                    except (ValueError, TypeError):
                        lat = None
                        lon = None
            
            if lat is not None and lon is not None:
                # 应用方向参考
                if lat_ref and lat_ref.lower() == 's':
                    lat = -abs(lat)
                elif lat_ref and lat_ref.lower() == 'n':
                    lat = abs(lat)
                    
                if lon_ref and lon_ref.lower() == 'w':
                    lon = -abs(lon)
                elif lon_ref and lon_ref.lower() == 'e':
                    lon = abs(lon)
                
                exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
        
        make = str(tags.get('Image Make', '')).strip()
        model = str(tags.get('Image Model', '')).strip()
        
        # Remove quotes from camera brand and model names
        if isinstance(make, str):
            make = make.strip().strip('"\'')
        if isinstance(model, str):
            model = model.strip().strip('"\'')
        
        exif_data.update({
            'Make': make or None,
            'Model': model or None
        })

    def _get_video_metadata(self, file_path, timeout=15):
        try:
            # 文件大小检查
            try:
                file_size = os.path.getsize(file_path)
                if file_size > 500 * 1024 * 1024:  # 500MB限制
                    self.log("DEBUG", f"视频文件过大，跳过: {file_path} ({file_size / 1024 / 1024:.1f}MB)")
                    return None
            except (OSError, FileNotFoundError):
                pass
                
            file_path_normalized = str(file_path).replace('\\', '/')
            cmd = f"{get_resource_path('resources/exiftool/exiftool.exe')} -fast \"{file_path_normalized}\""

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                shell=True
            )

            metadata = {}
            for line in result.stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    metadata[key.strip()] = value.strip()

            return metadata

        except subprocess.TimeoutExpired:
            self.log("DEBUG", f"读取视频文件 {file_path} 的EXIF数据超时")
            return None
        except Exception as e:
            self.log("DEBUG", f"读取视频文件 {file_path} 的EXIF数据时出错: {str(e)}")
            return None

    def parse_exif_datetime(self, tags):
        try:
            datetime_str = str(tags.get('EXIF DateTimeOriginal', ''))
            if datetime_str and datetime_str != 'None':
                if '+' in datetime_str or '-' in datetime_str[-5:]:
                    try:
                        dt = datetime.datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S%z')
                        if dt.tzinfo is not None:
                            dt = dt.astimezone()
                            return dt.replace(tzinfo=None)
                    except ValueError:
                        pass
                
                return datetime.datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
            
            datetime_str = str(tags.get('Image DateTime', ''))
            if datetime_str and datetime_str != 'None':
                if '+' in datetime_str or '-' in datetime_str[-5:]:
                    try:
                        dt = datetime.datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S%z')
                        if dt.tzinfo is not None:
                            dt = dt.astimezone()
                            return dt.replace(tzinfo=None)
                    except ValueError:
                        pass
                
                return datetime.datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                
        except (ValueError, TypeError):
            pass
            
        return None

    def parse_datetime(self, datetime_str):
        if not datetime_str:
            return None
            
        try:
            formats_with_timezone = [
                '%Y:%m:%d %H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S%z',
                '%Y/%m/%d %H:%M:%S%z',
            ]
            
            formats_without_timezone = [
                '%Y:%m:%d %H:%M:%S',
                '%Y-%m-%d %H:%M:%S', 
                '%Y/%m/%d %H:%M:%S',
                '%Y%m%d%H%M%S',
                '%Y-%m-%d',
                '%Y/%m/%d',
                '%Y%m%d'
            ]
            
            for fmt in formats_with_timezone:
                try:
                    dt = datetime.datetime.strptime(datetime_str, fmt)
                    if dt.tzinfo is not None:
                        dt = dt.astimezone()
                        return dt.replace(tzinfo=None)
                    return dt
                except ValueError:
                    continue
            
            for fmt in formats_without_timezone:
                try:
                    dt = datetime.datetime.strptime(datetime_str, fmt)
                    if 'mov' in fmt.lower() or fmt in ['%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S']:
                        import time
                        utc_dt = dt.replace(tzinfo=datetime.timezone.utc)
                        local_dt = utc_dt.astimezone()
                        return local_dt.replace(tzinfo=None)
                    
                    return dt
                except ValueError:
                    continue
        except (ValueError, TypeError):
            pass
            
        return None

    def parse_gps_coordinates(self, gps_info):
        """解析GPS坐标信息
        
        从GPS信息字典中提取并解析经纬度坐标。支持多种GPS坐标格式，
        优先尝试从'GPS Coordinates'和'GPS Position'字段解析，
        失败时回退到分别解析'GPS Latitude'和'GPS Longitude'。
        
        Args:
            gps_info: 包含GPS信息的字典
            
        Returns:
            tuple: (纬度, 经度)，解析失败时返回(None, None)
        """
        if not gps_info:
            return None, None
            
        for key in ['GPS Coordinates', 'GPS Position']:
            if key in gps_info:
                coords_str = gps_info[key]
                lat, lon = self._parse_combined_coordinates(coords_str)
                if lat is not None and lon is not None:
                    return lat, lon
        
        lat = self._parse_dms_coordinate(gps_info.get('GPS Latitude', ''))
        lon = self._parse_dms_coordinate(gps_info.get('GPS Longitude', ''))
        
        return lat, lon
    
    def _parse_combined_coordinates(self, coords_str):
        try:
            parts = coords_str.split(',')
            if len(parts) == 2:
                lat_str = parts[0].strip()
                lon_str = parts[1].strip()
                
                lat = self._parse_dms_coordinate(lat_str)
                lon = self._parse_dms_coordinate(lon_str)
                
                return lat, lon
        except (ValueError, TypeError, KeyError):
            pass
            
        return None, None
    
    def _parse_dms_coordinate(self, coord_str):
        if not coord_str:
            return None
            
        try:
            direction = None
            for dir_char in ['N', 'S', 'E', 'W']:
                if dir_char in coord_str:
                    direction = dir_char
                    break
            
            clean_str = coord_str
            for char in ['N', 'S', 'E', 'W']:
                clean_str = clean_str.replace(char, '')
            
            clean_str = clean_str.replace('deg', '°').replace('°', ' ').replace("'", ' ').replace('"', ' ')
            
            parts = [p for p in clean_str.split() if p.strip()]
            degrees = minutes = seconds = 0.0
            
            if len(parts) >= 1:
                degrees = float(parts[0])
            if len(parts) >= 2:
                minutes = float(parts[1])
            if len(parts) >= 3:
                seconds = float(parts[2])
            
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            
            if direction in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except (OSError, ValueError, TypeError):
            return None

    def get_city_and_province(self, lat, lon):
        """根据经纬度坐标获取省份和城市信息。
        
        Args:
            lat: 纬度坐标，可以是浮点数、整数或字符串格式
            lon: 经度坐标，可以是浮点数、整数或字符串格式
            
        Returns:
            tuple: 包含省份和城市的元组，格式为(province, city)
                  如果无法确定位置，返回("未知省份", "未知城市")
        """
        try:
            # 检查 province_data 和 city_data 是否存在
            _ = self.province_data
            _ = self.city_data
        except AttributeError:
            return "未知省份", "未知城市"

        def is_point_in_polygon(x, y, polygon):
            if not isinstance(polygon, (list, tuple)) or len(polygon) < 3:
                return False
            
            n = len(polygon)
            inside = False
            
            p1x, p1y = polygon[0]
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            
            return inside

        def query_location(longitude, latitude, data):
            for feature in data['features']:
                name, coordinates = feature['properties']['name'], feature['geometry']['coordinates']
                polygons = [polygon for multi_polygon in coordinates for polygon in
                            ([multi_polygon] if isinstance(multi_polygon[0][0], (float, int)) else multi_polygon)]
                
                for polygon in polygons:
                    if is_point_in_polygon(longitude, latitude, polygon):
                        return name

            return None

        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            lat_deg = lat
            lon_deg = lon
        else:
            lat_deg = self.convert_to_degrees(lat)
            lon_deg = self.convert_to_degrees(lon)
        
        if lat_deg and lon_deg:
            province = query_location(lon_deg, lat_deg, self.province_data)
            city = query_location(lon_deg, lat_deg, self.city_data)

            return (
                province if province else "未知省份",
                city if city else "未知城市"
            )
        else:
            return "未知省份", "未知城市"

    @staticmethod
    def convert_to_degrees(value):
        if not value:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass

        try:
            if len(value.values) >= 3:
                d = float(value.values[0].num) / float(value.values[0].den)
                m = float(value.values[1].num) / float(value.values[1].den)
                s = float(value.values[2].num) / float(value.values[2].den)
                result = d + (m / 60.0) + (s / 3600.0)
                return result
        except (ValueError, TypeError, AttributeError):
            pass

        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def build_new_file_name(self, file_path, file_time, original_name, exif_data=None):
        """构建新的文件名
        
        Args:
            file_path: 文件路径
            file_time: 文件时间
            original_name: 原始文件名
            exif_data: 可选，EXIF数据
            
        Returns:
            新的文件名
        """
        if not self.file_name_structure:
            return original_name
        
        if exif_data is None:
            exif_data = self.get_exif_data(file_path)
        
        parts = []
        # 准备文件上下文信息
        file_context = {
            'file_path': file_path,
            'file_time': file_time,
            'original_name': original_name,
            'exif_data': exif_data
        }
        
        # 严格按照用户点击tag的顺序构建文件名
        for tag in self.file_name_structure:
            # 调用get_file_name_part获取每个标签对应的值
            file_part = self.get_file_name_part(tag, file_context)
            # 只添加非空的部分
            if file_part:
                parts.append(file_part)
        
        # 确保文件名不为空
        if not parts:
            return original_name
        
        # 用指定的分隔符连接各部分
        return self.separator.join(parts)
        
    def process_single_file(self, file_path, base_folder=None):
        """处理单个文件的分类和重命名
        
        Args:
            file_path: 文件路径
            base_folder: 可选，基础文件夹
            
        Returns:
            处理后的信息或None
        """
        try:
            if self.is_stopped():
                return
                
            # 文件大小检查，避免处理过大的文件
            file_size = file_path.stat().st_size
            if file_size > 500 * 1024 * 1024:  # 500MB限制
                self.log("WARNING", f"跳过过大的文件: {file_path.name} ({file_size / 1024 / 1024:.1f}MB)")
                return
                
            exif_data = self.get_exif_data(file_path)
            
            # 解析文件时间 - 简化格式解析逻辑
            file_time = None
            if exif_data.get('DateTime'):
                # 使用更高效的方式尝试解析日期时间
                # 首先尝试调用专门的解析方法，如果存在的话
                if hasattr(self, 'parse_datetime'):
                    file_time = self.parse_datetime(str(exif_data['DateTime']))
                
                # 如果专门的方法不存在或失败，回退到尝试多种格式
                if file_time is None:
                    date_formats = [
                        '%Y-%m-%d %H:%M:%S',
                        '%Y:%m:%d %H:%M:%S',
                        '%Y-%m-%dT%H:%M:%S',
                        '%Y:%m:%dT%H:%M:%S'
                    ]
                    
                    # 优先尝试最常见的格式，减少循环次数
                    for fmt in date_formats:
                        try:
                            file_time = datetime.datetime.strptime(str(exif_data['DateTime']), fmt)
                            break
                        except ValueError:
                            continue
                
                if file_time is None:
                    self.log("WARNING", f"无法解析文件时间格式: {exif_data['DateTime']} 对于文件 {file_path.name}")
                    
            # 如果EXIF时间解析失败，使用文件系统时间
            if file_time is None:
                try:
                    # 简化文件时间获取逻辑
                    timestamp = file_path.stat().st_ctime if self.time_derive == "文件创建时间" else file_path.stat().st_mtime
                    file_time = datetime.datetime.fromtimestamp(timestamp)
                    self.log("DEBUG", f"使用文件系统时间: {file_time} 对于文件 {file_path.name}")
                except (OSError, IOError) as e:
                    self.log("ERROR", f"获取文件系统时间失败 {file_path.name}: {str(e)}")

            # 设置目标根目录
            if self.destination_root:
                base_folder = self.destination_root
            
            # 构建目标路径和新文件名
            target_path = self.build_target_path(file_path, exif_data, file_time, base_folder)
            original_name = file_path.stem
            new_file_name = self.build_new_file_name(file_path, file_time, original_name, exif_data)
            new_file_name_with_ext = f"{new_file_name}{file_path.suffix}"
            full_target_path = target_path / new_file_name_with_ext
            
            # 简化文件操作判断逻辑
            needs_operation = file_path.name != new_file_name_with_ext or file_path.parent != target_path
            
            if needs_operation:
                with self.files_lock:
                    self.files_to_rename.append({
                        'old_path': str(file_path),
                        'new_path': str(full_target_path)
                    })
            
            # 线程安全地更新处理计数
            with self.processed_lock:
                self.processed_files += 1
                
        except (OSError, IOError, ValueError, TypeError) as e:
            self.log("ERROR", f"处理文件 {file_path} 时出错: {str(e)}")

    def get_file_name_part(self, tag_info, file_context):
        """根据标签获取文件名部分
        
        Args:
            tag_info: 标签或标签字典
            file_context: 包含文件信息的字典，包含'file_path'、'file_time'、'original_name'、'exif_data'等键
            
        Returns:
            文件名部分字符串
        """
        # 处理标签字典情况
        if isinstance(tag_info, dict):
            return self._process_tag_dict(tag_info)
        
        # 确保exif_data可用
        if 'exif_data' not in file_context or file_context['exif_data'] is None:
            file_context['exif_data'] = self.get_exif_data(file_context['file_path'])
        
        # 使用字典映射代替多个if语句
        tag_processors = {
            "原文件名": lambda ctx: ctx['original_name'],
            "年份": lambda ctx: str(ctx['file_time'].year) if ctx['file_time'] else "",
            "月份": lambda ctx: f"{ctx['file_time'].month:02d}" if ctx['file_time'] else "",
            "日": lambda ctx: f"{ctx['file_time'].day:02d}" if ctx['file_time'] else "",
            "星期": lambda ctx: self._get_weekday_name(ctx['file_time']) if ctx['file_time'] else "",
            "时间": lambda ctx: ctx['file_time'].strftime('%H%M%S') if ctx['file_time'] else "",
            "品牌": lambda ctx: self._get_device_info(ctx['exif_data'], 'Make', '未知品牌'),
            "型号": lambda ctx: self._get_device_info(ctx['exif_data'], 'Model', '未知型号'),
            "位置": lambda ctx: self._get_location_name(ctx),
            "自定义": lambda ctx: "自定义"
        }
        
        # 获取对应的处理器并执行
        processor = tag_processors.get(tag_info)
        return processor(file_context) if processor else ""
    
    def _process_tag_dict(self, tag_dict):
        """处理标签字典格式"""
        if tag_dict.get('tag') == "自定义" or tag_dict.get('content') is not None:
            return tag_dict.get('content', "")
        return tag_dict.get('tag', "")
    
    def _get_weekday_name(self, file_time):
        """获取星期名称"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[file_time.weekday()]
    
    def _get_device_info(self, exif_data, key, default):
        """获取设备信息"""
        value = exif_data.get(key, default)
        if isinstance(value, str):
            value = value.strip().strip('"\'')
        return str(value) if value is not None else default
    
    def _get_location_name(self, file_context):
        """获取位置名称"""
        exif_data = file_context['exif_data']
        if not exif_data.get('GPS GPSLatitude') or not exif_data.get('GPS GPSLongitude'):
            return "未知位置"
        
        try:
            lat = float(exif_data['GPS GPSLatitude'])
            lon = float(exif_data['GPS GPSLongitude'])
            
            # 尝试从缓存获取
            cached_address = config_manager.get_cached_location_with_tolerance(lat, lon, 0.045)
            if cached_address and cached_address != "未知位置":
                return cached_address
            
            # 尝试获取地址信息
            address = self._get_address_from_coordinates(lat, lon)
            if address and address != "未知位置":
                config_manager.cache_location(lat, lon, address)
                return address
            
            # 获取省份城市信息
            province, city = self.get_city_and_province(exif_data['GPS GPSLatitude'], exif_data['GPS GPSLongitude'])
            return f"{province}{city}" if city != "未知城市" else province
        except (ValueError, TypeError):
            return "未知位置"

    def build_target_path(self, file_path, exif_data, file_time, base_folder):
        """构建目标路径并确保目录存在，增强了错误处理和权限检查"""
        if not self.classification_structure:
            return file_path.parent
        
        # 确定基础目标路径
        if base_folder:
            target_path = self._safe_path_resolve(base_folder)
        elif self.destination_root:
            target_path = self._safe_path_resolve(self.destination_root)
        else:
            target_path = file_path.parent
        
        # 验证基础路径的有效性
        if not self._validate_folder_path(target_path):
            self.log("ERROR", f"无效的目标路径: {target_path}")
            return file_path.parent
        
        # 构建分类路径
        target_path = self._build_classification_path(target_path, exif_data, file_time, file_path)
        
        # 添加文件类型文件夹
        target_path = self._add_file_type_folder(target_path, file_path)
        
        # 检查路径长度限制（Windows默认260字符限制）
        if self._check_path_length_limit(target_path):
            self.log("WARNING", f"路径长度可能超过系统限制: {target_path}")
            # 尝试简化路径
            target_path = self._simplify_path_if_needed(target_path)
        
        # 尝试创建目录结构
        success = self._create_directory_structure(target_path)
        if not success:
            return file_path.parent
        
        return target_path
        
    def _build_classification_path(self, target_path, exif_data, file_time, file_path):
        """构建分类路径，处理每个分类级别"""
        for level in self.classification_structure:
            # 使用函数处理以避免嵌套异常
            folder_name = self._get_safe_folder_name(level, exif_data, file_time, file_path)
            if folder_name:
                target_path = target_path / folder_name
        return target_path
    
    def _get_safe_folder_name(self, level, exif_data, file_time, file_path):
        """获取安全的文件夹名称"""
        try:
            folder_name = self.get_folder_name(level, exif_data, file_time, file_path)
            if folder_name:
                # 清理文件夹名称，移除或替换非法字符
                safe_folder_name = self._sanitize_folder_name(folder_name)
                if safe_folder_name:
                    return safe_folder_name
                # 移除else子句
                self.log("WARNING", f"无效的文件夹名称: {folder_name}，跳过该级别")
        except (ValueError, TypeError, OSError) as e:
            self.log("WARNING", f"处理分类级别 '{level}' 时出错: {str(e)}，跳过该级别")
        return None
    
    def _add_file_type_folder(self, target_path, file_path):
        """添加文件类型文件夹"""
        try:
            file_type = get_file_type(file_path)
            if file_type:
                safe_file_type = self._sanitize_folder_name(file_type)
                return target_path / safe_file_type
        except (ValueError, TypeError) as e:
            self.log("WARNING", f"获取文件类型时出错: {str(e)}")
        return target_path
    
    def _create_directory_structure(self, target_path):
        """创建目录结构并处理可能的错误"""
        try:
            self._ensure_directory_exists(target_path)
            return True
        except (OSError, PermissionError) as e:
            self.log("ERROR", f"创建目标目录失败: {target_path}，错误: {str(e)}")
            return False
    
    def _safe_path_resolve(self, path_str):
        """安全地解析路径，避免路径遍历攻击"""
        try:
            # 使用Path对象解析路径
            path = Path(path_str).resolve()
            # 确保是绝对路径
            if not path.is_absolute():
                self.log("WARNING", f"路径不是绝对路径，将使用当前工作目录: {path_str}")
                path = Path.cwd() / path_str
                path = path.resolve()
            return path
        except (OSError, ValueError, TypeError) as e:
            self.log("ERROR", f"解析路径失败: {path_str}，错误: {str(e)}")
            # 返回当前工作目录作为备选
            return Path.cwd()
    
    def _sanitize_folder_name(self, folder_name):
        """清理文件夹名称，移除或替换非法字符"""
        try:
            # 替换Windows文件系统中的非法字符
            illegal_chars = '<>:"/\\|?*'
            safe_name = folder_name
            for char in illegal_chars:
                safe_name = safe_name.replace(char, '_')
            
            # 移除控制字符
            safe_name = ''.join(char for char in safe_name if ord(char) > 31)
            
            # 处理空字符串或仅包含空格的情况
            safe_name = safe_name.strip()
            if not safe_name:
                safe_name = "未知"
            
            # 处理过长的文件夹名称（Windows限制为255个字符）
            if len(safe_name) > 255:
                safe_name = safe_name[:252] + "..."
            
            return safe_name
        except (TypeError, ValueError):
            return "未知"
    
    def _check_path_length_limit(self, path):
        """检查路径长度是否接近系统限制"""
        try:
            # Windows通常有260字符的限制，我们设置240作为预警值
            path_str = str(path)
            return len(path_str) > 240
        except (TypeError, ValueError):
            return False
    
    def _simplify_path_if_needed(self, path):
        """在需要时简化路径"""
        try:
            # 这里可以根据需要实现更复杂的路径简化逻辑
            # 目前只是返回父目录作为简单的备选方案
            if len(path.parts) > 2:
                # 保留最后两个部分，其他用父目录替换
                return path.parent.parent / path.name
            return path
        except (OSError, TypeError, AttributeError):
            return path
    
    def _ensure_directory_exists(self, directory_path):
        """确保目录存在，如果不存在则创建，并处理权限问题"""
        try:
            if not directory_path.exists():
                # 使用parents=True确保所有父目录都被创建
                directory_path.mkdir(parents=True, exist_ok=True)
                self.log("DEBUG", f"成功创建目录: {directory_path}")
            
            # 验证目录是否可以写入
            if not self._can_write_to_directory(directory_path):
                raise PermissionError(f"没有写入权限: {directory_path}")
            
            return True
        except PermissionError as e:
            self.log("ERROR", f"权限错误: {str(e)}")
            raise
        except Exception as e:
            self.log("ERROR", f"创建目录失败: {directory_path}，错误: {str(e)}")
            raise
    
    def _can_write_to_directory(self, directory_path):
        """检查是否有写入目录的权限"""
        try:
            # 尝试创建一个临时文件来验证写权限
            test_file = directory_path / f".permission_test_{int(time.time())}"
            test_file.touch()
            test_file.unlink()
            return True
        except (PermissionError, IOError):
            return False

    def get_folder_name(self, level, exif_data, file_time, file_path):
        """根据分类级别获取文件夹名称
        
        Args:
            level: 分类级别（如"年份"、"月份"、"拍摄设备"等）
            exif_data: EXIF数据字典
            file_time: 文件时间对象
            file_path: 文件路径
            
        Returns:
            str: 文件夹名称，如果为"不分类"则返回None
        """
        # 处理特殊情况：不分类
        if level == "不分类":
            return None
            
        # 使用字典映射处理不同级别的文件夹名称生成
        folder_name_map = {
            "年份": lambda: str(file_time.year) if file_time else "未知",
            "月份": lambda: f"{file_time.month:02d}" if file_time else "未知",
            "日期": lambda: f"{file_time.day:02d}" if file_time else "未知",
            "星期": lambda: self._get_weekday_name(file_time) if file_time else "未知",
            "拍摄设备": lambda: self._get_device_make(exif_data),
            "相机型号": lambda: self._get_device_model(exif_data),
            "拍摄省份": lambda: self._get_geographic_location(exif_data, 'province'),
            "拍摄城市": lambda: self._get_geographic_location(exif_data, 'city'),
            "文件类型": lambda: get_file_type(file_path)
        }
        
        # 获取对应的处理函数并执行，如不存在则返回"未知"
        folder_name_func = folder_name_map.get(level)
        return folder_name_func() if folder_name_func else "未知"
        
    def _get_weekday_name(self, file_time):
        """获取星期名称"""
        weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
        return weekdays[file_time.weekday()]
        
    def _get_device_make(self, exif_data):
        """获取设备制造商"""
        if exif_data.get('Make'):
            make = exif_data['Make']
            if isinstance(make, str):
                make = make.strip().strip('"\'')
            return make
        return "未知设备"
        
    def _get_device_model(self, exif_data):
        """获取相机型号"""
        if exif_data.get('Model'):
            model = exif_data['Model']
            if isinstance(model, str):
                model = model.strip().strip('"\'')
            return model
        return "未知设备"
        
    def _get_geographic_location(self, exif_data, location_type):
        """根据GPS信息获取地理位置"""
        if exif_data.get('GPS GPSLatitude') and exif_data.get('GPS GPSLongitude'):
            province, city = self.get_city_and_province(
                exif_data['GPS GPSLatitude'], exif_data['GPS GPSLongitude']
            )
            return province if location_type == 'province' else city
        return "未知省份" if location_type == 'province' else "未知城市"
    
    def _get_address_from_coordinates(self, _lat, _lon):
        """根据坐标获取地址信息"""
        try:
            # 避免import-outside-toplevel警告，这里不导入requests
            # 如果需要实际实现地址解析，可以使用现有的地理编码功能
            return "未知位置"
        except (ValueError, TypeError, KeyError):
            return "未知位置"
