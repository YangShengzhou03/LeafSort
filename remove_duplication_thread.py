"""
重复文件检测线程模块

该模块定义了RemoveDuplicationThread类，用于在后台线程中执行重复文件检测任务。
包含文件扫描、哈希计算、重复文件分组等核心功能。
"""

import os
import hashlib
from collections import defaultdict
from PyQt6.QtCore import QThread, pyqtSignal


class RemoveDuplicationThread(QThread):
    """重复文件检测线程类"""
    
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    
    def __init__(self, folders=None, compare_size_only=False):
        """初始化重复文件检测线程
        
        Args:
            folders: 要扫描的文件夹列表
            compare_size_only: 是否仅比较文件大小
        """
        super().__init__()
        self.folders = folders or []
        self.compare_size_only = compare_size_only
        self._stop_flag = False
    
    def run(self):
        """线程执行主函数"""
        try:
            self._scan_duplicates()
        except Exception as e:
            self.progress_updated.emit(0, f"扫描出错: {str(e)}")
    
    def stop(self):
        """停止线程执行"""
        self._stop_flag = True
    
    def _scan_duplicates(self):
        """扫描重复文件"""
        # 获取所有文件
        all_files = self._get_all_files()
        total_files = len(all_files)
        
        if total_files == 0:
            self.progress_updated.emit(100, "没有找到文件")
            self.scan_completed.emit({})
            return
        
        # 按文件大小分组
        self.progress_updated.emit(0, "正在按文件大小分组...")
        size_groups = self._group_by_size(all_files)
        
        # 过滤出可能有重复的文件组
        potential_duplicates = {size: files for size, files in size_groups.items() 
                               if len(files) > 1}
        
        if self.compare_size_only:
            # 如果仅比较大小，直接返回大小相同的文件组
            self.progress_updated.emit(100, "大小比较完成")
            self.scan_completed.emit(potential_duplicates)
            return
        
        # 计算文件哈希值进行精确比较
        duplicate_groups = self._compare_by_hash(potential_duplicates, total_files)
        
        self.progress_updated.emit(100, "重复文件检测完成")
        self.scan_completed.emit(duplicate_groups)
    
    def _get_all_files(self):
        """获取所有要扫描的文件
        
        Returns:
            list: 文件路径列表
        """
        all_files = []
        
        for folder_info in self.folders:
            folder_path = folder_info['path']
            include_sub = folder_info.get('include_sub', True)
            
            if not os.path.exists(folder_path):
                continue
            
            if include_sub:
                # 递归扫描子文件夹
                for root, dirs, files in os.walk(folder_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if os.path.isfile(file_path):
                            all_files.append(file_path)
            else:
                # 仅扫描当前文件夹
                for item in os.listdir(folder_path):
                    file_path = os.path.join(folder_path, item)
                    if os.path.isfile(file_path):
                        all_files.append(file_path)
        
        return all_files
    
    def _group_by_size(self, files):
        """按文件大小分组
        
        Args:
            files: 文件路径列表
            
        Returns:
            dict: 按大小分组的文件字典
        """
        size_groups = defaultdict(list)
        
        for i, file_path in enumerate(files):
            if self._stop_flag:
                return {}
            
            try:
                file_size = os.path.getsize(file_path)
                size_groups[file_size].append(file_path)
            except OSError:
                # 忽略无法访问的文件
                continue
            
            # 更新进度
            progress = int((i + 1) / len(files) * 30)  # 大小分组占30%进度
            self.progress_updated.emit(progress, f"正在分析文件大小... ({i+1}/{len(files)})")
        
        return size_groups
    
    def _compare_by_hash(self, potential_duplicates, total_files):
        """通过哈希值比较文件内容
        
        Args:
            potential_duplicates: 可能重复的文件组
            total_files: 总文件数
            
        Returns:
            dict: 重复文件分组字典
        """
        hash_groups = defaultdict(list)
        processed_files = 0
        
        # 计算需要处理的文件总数
        files_to_process = sum(len(files) for files in potential_duplicates.values())
        
        if files_to_process == 0:
            return {}
        
        for size, files in potential_duplicates.items():
            if self._stop_flag:
                return {}
            
            # 对每个文件计算哈希值
            file_hashes = {}
            
            for file_path in files:
                if self._stop_flag:
                    return {}
                
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    file_hashes[file_hash] = file_hashes.get(file_hash, []) + [file_path]
                except Exception as e:
                    # 忽略计算哈希失败的文件
                    continue
                
                processed_files += 1
                progress = 30 + int((processed_files / files_to_process) * 70)  # 哈希计算占70%进度
                self.progress_updated.emit(progress, f"正在计算文件哈希... ({processed_files}/{files_to_process})")
            
            # 将重复文件添加到结果中
            for file_hash, duplicate_files in file_hashes.items():
                if len(duplicate_files) > 1:
                    group_id = f"{size}_{file_hash[:8]}"
                    hash_groups[group_id] = duplicate_files
        
        return hash_groups
    
    def _calculate_file_hash(self, file_path, chunk_size=8192):
        """计算文件哈希值
        
        Args:
            file_path: 文件路径
            chunk_size: 读取块大小
            
        Returns:
            str: 文件哈希值
        """
        hash_md5 = hashlib.md5()
        
        try:
            with open(file_path, 'rb') as f:
                # 读取文件前几个块来计算哈希（提高性能）
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
                    # 对于大文件，只读取前几个块来快速计算
                    if f.tell() > chunk_size * 4:  # 最多读取32KB
                        break
        except Exception:
            raise
        
        return hash_md5.hexdigest()
    
    def set_folders(self, folders):
        """设置要扫描的文件夹
        
        Args:
            folders: 文件夹信息列表
        """
        self.folders = folders
    
    def set_compare_size_only(self, compare_size_only):
        """设置是否仅比较文件大小
        
        Args:
            compare_size_only: 是否仅比较大小
        """
        self.compare_size_only = compare_size_only