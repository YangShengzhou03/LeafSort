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
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
