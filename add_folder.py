"""
文件夹页面
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
