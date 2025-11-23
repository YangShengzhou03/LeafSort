"""
文件夹管理页面模块

该模块定义了FolderPage类，用于管理应用程序的文件夹导入和管理功能。
包含文件夹添加、删除、列表显示等核心功能。
"""

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
import os

from config_manager import config_manager

class FolderPage(QtWidgets.QWidget):
    """文件夹管理页面类"""
    
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        """初始化文件夹管理页面
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.parent = parent
        self.init_page()
    
    def init_page(self):
        """初始化页面UI"""
        self._connect_signals()
    
    def _connect_signals(self):
        """连接信号槽"""
        self.ui_manager.add_folder_btn.clicked.connect(self.add_folder)
        self.ui_manager.remove_btn.clicked.connect(self.remove_selected_folders)
        self.ui_manager.clear_btn.clicked.connect(self.clear_all_folders)
