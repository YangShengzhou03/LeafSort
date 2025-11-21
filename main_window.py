from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QMainWindow, QDialog, QMenu, QInputDialog, QMessageBox
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QPixmap, QImage, QIcon, QFont
import os
import sys
from Ui_MainWindow import Ui_MainWindow
from SettingsDialog import SettingsDialog
from common import get_resource_path
from add_folder import FolderPage
from smart_arrange import SmartArrangePage
from remove_duplication import RemoveDuplicationPage
from write_exif import WriteExifPage


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # 页面相关初始化
        self.current_page_index = -1
        self.page_cache = {}
        self.setupUi(self)
            
            # 初始化窗口
        self._init_window()
        
        # 初始化功能页面
        self.folder_page = FolderPage(self)
        self.smart_arrange_page = SmartArrangePage(self)
        self.remove_duplication_page = RemoveDuplicationPage(self)
        self.write_exif_page = WriteExifPage(self)
        
        # 保存各功能页面引用
        self.pages = {
            'folder': self.folder_page,
            'smart_arrange': self.smart_arrange_page,
            'remove_duplication': self.remove_duplication_page,
            'write_exif': self.write_exif_page
        }
        
        # 连接信号槽
        self._connect_signals()
        
        # 初始化UI
        self.init_ui()

    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def init_ui(self):
        # 初始化各功能页面，安全地调用init_page方法
        for page_name, page in self.pages.items():
            if hasattr(page, 'init_page'):
                try:
                    page.init_page()
                except Exception as e:
                    print(f"初始化{page_name}页面失败: {str(e)}")
            else:
                print(f"{page_name}页面没有init_page方法，跳过初始化")
        
        # 设置导航菜单的初始状态
        self.listNavigationMenu.setCurrentRow(0)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 设置按钮点击事件
        try:
            # 导航菜单连接
            self.listNavigationMenu.currentRowChanged.connect(self._on_navigation_changed)
            
            # 设置按钮连接
            self.btnSettings.clicked.connect(self._show_settings)
            
            # 窗口控制按钮连接
            try:
                self.toolButton_Minimize.clicked.connect(self.showMinimized)
                self.toolButton_Maximize.clicked.connect(self._toggle_maximize)
                self.toolButton_Close.clicked.connect(self.close)
            except Exception as e:
                print(f"连接窗口控制按钮信号失败: {str(e)}")
                
            # 为拖动窗口做准备
            self.mousePressEvent = self._on_mouse_press
            self.mouseMoveEvent = self._on_mouse_move
            self.mouseReleaseEvent = self._on_mouse_release
            self._drag_position = QPoint()
            
        except Exception as e:
            print(f"连接信号失败: {str(e)}")
            
    def _on_navigation_changed(self, index):
        # 根据导航菜单选择切换页面
        self.stackedWidget.setCurrentIndex(index)
        # 切换到对应页面时重新初始化
        if index == 0:  # 添加文件夹页面
            self.folder_page.refresh()
        elif index == 1:  # 智能整理页面
            self.smart_arrange_page.refresh()
        elif index == 2:  # 文件去重页面
            self.remove_duplication_page.refresh()
        elif index == 3:  # 属性写入页面
            self.write_exif_page.refresh()
            
    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            print(f"打开设置对话框失败: {str(e)}")
            QtWidgets.QMessageBox.warning(self, "错误", f"打开设置对话框时出错: {str(e)}")
    
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def _on_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查点击位置是否在标题栏区域
            if self.rect().contains(event.pos()) and event.pos().y() < 60:  # 假设标题栏高度为60
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def _on_mouse_move(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and hasattr(self, '_drag_position') and self._drag_position:
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def _on_mouse_release(self, event):
        self._drag_position = QPoint()
            
    def log(self, level, message):
        """日志记录功能"""
        # 实现日志记录功能，将日志显示在UI上
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        # 根据当前活动页面显示在对应的日志组件中
        try:
            current_index = self.stackedWidget.currentIndex()
            if current_index == 0 and hasattr(self, 'textBrowser_import_info'):
                self.textBrowser_import_info.append(log_message)
            elif current_index == 1 and hasattr(self, 'smartArrangeLogOutputTextEdit'):
                self.smartArrangeLogOutputTextEdit.append(log_message)
            elif current_index == 2 and hasattr(self, 'textBrowser_duplication_log'):
                self.textBrowser_duplication_log.append(log_message)
            elif current_index == 3 and hasattr(self, 'textBrowser_EXIF_log'):
                self.textBrowser_EXIF_log.append(log_message)
        except Exception as e:
            print(f"写入日志到UI失败: {str(e)}")
            
        print(log_message)