from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from SettingsDialog import SettingsDialog
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from common import get_resource_path
from remove_duplication import RemoveDuplicationPage
from smart_arrange import SmartArrangePage
from write_exif import WriteExifPage


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # 页面相关初始化
        self.current_page_index = -1
        self.page_cache = {}
        
        # 初始化系统托盘
        self._init_system_tray()
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
        

    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 设置按钮连接
        try:
            # 设置按钮连接
            self.btnSettings.clicked.connect(self._show_settings)
            
            # 窗口控制按钮连接
            try:
                self.btnMinimize.clicked.connect(self.showMinimized)
                self.btnMaximize.clicked.connect(self._toggle_maximize)
                self.btnClose.clicked.connect(self.hide_to_tray)
            except Exception as e:
                print(f"连接窗口控制按钮信号失败: {str(e)}")
                
            # 为拖动窗口做准备
            self.mousePressEvent = self._on_mouse_press
            self.mouseMoveEvent = self._on_mouse_move
            self.mouseReleaseEvent = self._on_mouse_release
            self._drag_position = QPoint()
            
        except Exception as e:
            print(f"连接信号失败: {str(e)}")
            
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
            
    def _init_system_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.tray_icon.setToolTip("枫叶相册")
        
        # 创建托盘菜单
        self._create_tray_menu()
        
        # 设置点击托盘图标显示/隐藏主窗口
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
    def _create_tray_menu(self):
        """创建托盘菜单"""
        # 创建菜单
        self.tray_menu = QMenu()
        
        # 创建显示动作
        self.action_show = QAction("显示窗口", self)
        self.action_show.triggered.connect(self._show_window)
        
        # 创建退出动作
        self.action_exit = QAction("退出", self)
        self.action_exit.triggered.connect(self._exit_application)
        
        # 添加动作到菜单
        self.tray_menu.addAction(self.action_show)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.action_exit)
        
        # 设置托盘菜单
        self.tray_icon.setContextMenu(self.tray_menu)
        
    def _show_window(self):
        """显示主窗口"""
        self.show()
        self.raise_()
        
    def _exit_application(self):
        """退出应用程序"""
        # 先隐藏托盘图标
        self.tray_icon.hide()
        # 然后退出应用
        QtWidgets.QApplication.quit()
        
    def _tray_icon_activated(self, reason):
        """托盘图标被激活时的处理"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self.show()
                self.raise_()
            else:
                self.hide()
                
    def hide_to_tray(self):
        """隐藏到系统托盘"""
        self.hide()
        self.tray_icon.show()
        
    def closeEvent(self, event):
        """重写关闭事件，最小化到托盘而不是退出"""
        event.ignore()
        self.hide_to_tray()
    
    def _on_mouse_press(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查点击位置是否在标题栏区域
            if self.rect().contains(event.pos()) and event.pos().y() < 60:  # 假设标题栏高度为60
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
    
    def _on_mouse_move(self, event):
        try:
            if event.buttons() == Qt.MouseButton.LeftButton and self._drag_position:
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
        except AttributeError:
            pass
    
    def _on_mouse_release(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_position = QPoint()
        except AttributeError:
            pass