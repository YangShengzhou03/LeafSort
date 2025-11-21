import os
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time
import hashlib

import numpy as np
import pillow_heif
from PIL import Image
from PyQt6 import QtCore
from PyQt6.QtCore import QThread, pyqtSignal


class HashWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_signal = pyqtSignal(str, str)
    duplicates_found = pyqtSignal(dict)
    
    def __init__(self, file_paths):
        super().__init__()
        self.file_paths = file_paths
        self.running = True
        self.hash_dict = {}
    
    def stop(self):
        self.running = False
    
    def run(self):
        try:
            self._compute_hashes()
        except Exception as e:
            self.log_signal.emit("ERROR", f"计算哈希值时出错: {str(e)}")
    
    def _compute_hashes(self):
        total_files = len(self.file_paths)
        processed_files = 0
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            # 提交所有任务
            future_to_file = {executor.submit(self._compute_file_hash, file_path): file_path 
                            for file_path in self.file_paths}
            
            # 处理完成的任务
            for future in as_completed(future_to_file):
                if not self.running:
                    executor.shutdown(wait=False)
                    break
                
                try:
                    file_path, file_hash = future.result()
                    if file_hash:
                        if file_hash not in self.hash_dict:
                            self.hash_dict[file_hash] = []
                        self.hash_dict[file_hash].append(file_path)
                    
                    processed_files += 1
                    progress = int((processed_files / total_files) * 100)
                    self.progress_updated.emit(progress)
                    
                    if processed_files % 100 == 0:
                        self.log_signal.emit("INFO", f"已处理 {processed_files}/{total_files} 个文件")
                    
                except Exception as e:
                    file_path = future_to_file[future]
                    self.log_signal.emit("WARNING", f"处理文件失败 {file_path}: {str(e)}")
        
        if self.running:
            self.duplicates_found.emit(self.hash_dict)
            self.log_signal.emit("INFO", "哈希计算完成")
    
    def _compute_file_hash(self, file_path):
        try:
            # 使用文件内容计算哈希值
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # 读取文件的前10MB或整个文件（取较小值）
                # 对于大文件，这样可以提高性能
                size = min(os.path.getsize(file_path), 10 * 1024 * 1024)
                data = f.read(size)
                hasher.update(data)
            return file_path, hasher.hexdigest()
        except Exception as e:
            self.log_signal.emit("WARNING", f"计算文件哈希失败 {file_path}: {str(e)}")
            return file_path, None


class ContrastWorker(QThread):
    progress_updated = pyqtSignal(int)
    log_signal = pyqtSignal(str, str)
    contrast_result = pyqtSignal(list)
    
    def __init__(self, file_groups):
        super().__init__()
        self.file_groups = file_groups
        self.running = True
    
    def stop(self):
        self.running = False
    
    def run(self):
        try:
            results = []
            total_groups = len(self.file_groups)
            
            for i, group in enumerate(self.file_groups):
                if not self.running:
                    break
                
                # 对每组文件进行详细对比
                if len(group) > 1:
                    # 这里可以实现更复杂的图像对比逻辑
                    # 例如像素级对比、直方图对比等
                    results.append(group)
                
                progress = int(((i + 1) / total_groups) * 100)
                self.progress_updated.emit(progress)
            
            if self.running:
                self.contrast_result.emit(results)
                self.log_signal.emit("INFO", f"对比完成，找到 {len(results)} 组相似文件")
        
        except Exception as e:
            self.log_signal.emit("ERROR", f"图像对比时出错: {str(e)}")
    
    def _compare_images(self, file1, file2):
        """
        比较两个图像文件的相似度
        返回一个相似度分数（0-100）
        """
        try:
            # 这里可以实现更复杂的对比逻辑
            # 目前简单返回100表示相似
            return 100
        except Exception as e:
            self.log_signal.emit("WARNING", f"比较图像失败 {file1}, {file2}: {str(e)}")
            return 0
