import sys

from PyQt6 import QtWidgets, QtCore, QtGui

from Ui_MainWindow import Ui_MainWindow
from common import get_resource_path
from SettingsDialog import SettingsDialog


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # 页面相关初始化
        self.current_page_index = -1
        self.page_cache = {}
        self.setupUi(self)
            
            # 初始化窗口
        self._init_window()
        
        # 连接信号槽
        self._connect_signals()

    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 设置按钮点击事件
        try:
            self.btnSettings.clicked.connect(self._show_settings)
        except Exception as e:
            print(f"连接设置按钮信号失败: {str(e)}")
            
    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"打开设置对话框失败: {str(e)}")
            QtWidgets.QMessageBox.warning(self, "错误", f"打开设置对话框时出错: {str(e)}")
            
    def log(self, level, message):
        """日志记录功能"""
        print(f"[{level}] {message}")
        # 可以在这里添加更多的日志处理逻辑，如写入文件等