import os

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog

from common import get_resource_path
from config_manager import config_manager


class FolderPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_items = []
    
    def refresh(self):
        """刷新文件夹列表"""
        # 简单实现：清空现有列表
        self.folder_items.clear()
        
    def get_all_folders(self):
        """获取所有文件夹"""
        return self.folder_items
