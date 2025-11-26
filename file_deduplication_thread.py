import os
import hashlib
import logging
from PyQt6 import QtCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileScanThread(QtCore.QThread):
    """文件扫描线程"""
    
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, folder_path, filters=None):
        super().__init__()
        self.folder_path = folder_path
        self.filters = filters or []
        self._stop_flag = False
    
    def stop(self):
        """停止扫描"""
        self._stop_flag = True
    
    def _calculate_md5(self, file_path, block_size=8192):
        """计算文件的MD5值"""
        md5 = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(block_size), b''):
                if self._stop_flag:
                    return None
                md5.update(chunk)
        return md5.hexdigest()
    
    def run(self):
        """运行扫描线程"""
        try:
            # 获取所有文件
            all_files = []
            for root, _, files in os.walk(self.folder_path):
                if self._stop_flag:
                    self.error_occurred.emit("扫描已停止")
                    return
                
                for file in files:
                    # 应用文件过滤器
                    if self.filters and not any(file.lower().endswith(filter.lower()) for filter in self.filters):
                        continue
                    
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            
            # 计算MD5值并查找重复
            file_hashes = {}
            total_files = len(all_files)
            
            for i, file_path in enumerate(all_files):
                if self._stop_flag:
                    self.error_occurred.emit("扫描已停止")
                    return
                
                # 更新进度
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress, f"正在扫描: {file_path}")
                
                try:
                    file_hash = self._calculate_md5(file_path)
                    if self._stop_flag or file_hash is None:
                        self.error_occurred.emit("扫描已停止")
                        return
                    
                    if file_hash in file_hashes:
                        file_hashes[file_hash].append(file_path)
                    else:
                        file_hashes[file_hash] = [file_path]
                except Exception as e:
                    logger.error(f"计算文件{file_path}的MD5值失败: {str(e)}")
            
            # 过滤出重复的文件组
            duplicate_groups = [files for files in file_hashes.values() if len(files) > 1]
            
            # 完成扫描
            self.scan_completed.emit(duplicate_groups)
            
        except Exception as e:
            logger.error(f"扫描重复文件时出错: {str(e)}")
            self.error_occurred.emit(f"扫描出错: {str(e)}")

class FileDeduplicateThread(QtCore.QThread):
    """文件去重线程"""
    
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    deduplicate_completed = QtCore.pyqtSignal(int, int)  # 去重完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, duplicate_groups, delete_list=None):
        super().__init__()
        self.duplicate_groups = duplicate_groups
        self.delete_list = delete_list or []
        self._stop_flag = False
    
    def stop(self):
        """停止去重"""
        self._stop_flag = True
    
    def run(self):
        """运行去重线程"""
        try:
            total_deleted = 0
            total_files = 0
            
            # 计算需要处理的文件总数
            total_to_process = sum(len(group) - 1 for group in self.duplicate_groups)
            
            for group_idx, file_group in enumerate(self.duplicate_groups):
                for file_idx, file_path in enumerate(file_group):
                    # 跳过每组的第一个文件（保留）
                    if file_idx == 0:
                        continue
                    
                    # 检查是否应该删除
                    should_delete = True
                    if self.delete_list and file_path not in self.delete_list:
                        should_delete = False
                    
                    if should_delete:
                        try:
                            if self._stop_flag:
                                self.error_occurred.emit("去重已停止")
                                return
                            
                            os.remove(file_path)
                            total_deleted += 1
                            logger.info(f"已删除重复文件: {file_path}")
                        except Exception as e:
                            logger.error(f"删除文件{file_path}失败: {str(e)}")
                    
                    total_files += 1
                    
                    # 更新进度
                    if total_to_process > 0:
                        progress = int((total_files / total_to_process) * 100)
                        self.progress_updated.emit(progress, f"正在删除: {file_path}")
            
            # 完成去重
            self.deduplicate_completed.emit(total_deleted, total_files)
            
        except Exception as e:
            logger.error(f"执行文件去重时出错: {str(e)}")
            self.error_occurred.emit(f"去重出错: {str(e)}")