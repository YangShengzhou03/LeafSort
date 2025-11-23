"""
重复文件检测与删除页面模块

该模块定义了RemoveDuplicationPage类，用于检测和删除重复文件。
包含文件哈希计算、重复文件分组、预览和删除等功能。
"""

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal
import os
import hashlib
from collections import defaultdict

from remove_duplication_thread import RemoveDuplicationThread


class RemoveDuplicationPage(QtWidgets.QWidget):
    """重复文件检测与删除页面类"""
    
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    deletion_completed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """初始化重复文件检测页面
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.hash_dict = {}