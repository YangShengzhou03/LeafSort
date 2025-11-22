from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
import os


class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        