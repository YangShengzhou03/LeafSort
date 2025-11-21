import sys

from PyQt6 import QtWidgets, QtCore, QtGui

from Ui_MainWindow import Ui_MainWindow
from common import get_resource_path


# 导入智能整理线程类
# 导入文件去重相关类
# 导入属性写入线程类


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()

        
        # 初始化空状态管理
        self.empty_widgets = {}
        
        # 初始化智能整理线程
        self.smart_arrange_thread = None
        # 初始化文件去重相关线程
        self.hash_worker = None
        self.contrast_worker = None
        self.image_hashes = {}
        # 初始化属性写入线程
        self.write_exif_thread = None
        
        # 页面相关初始化 - 添加页面缓存和状态管理
        self.current_page_index = -1
        self.page_cache = {}
        self.last_page_index = -1
        self.page_transitioning = False
        self.setupUi(self)
            
            # 初始化窗口
        self._init_window()

    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)