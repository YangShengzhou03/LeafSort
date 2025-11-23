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