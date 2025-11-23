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


class WindowManager:
    """窗口管理器，负责窗口控制和系统托盘功能"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self._drag_position = QPoint()
        self.tray_icon = None
        
    def setup_window(self):
        """设置窗口属性"""
        self.main_window.setWindowTitle("枫叶相册")
        self.main_window.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.main_window.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.main_window.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
    
    def setup_system_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self.main_window)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.tray_icon.setToolTip("枫叶相册")
        self._create_tray_menu()
        self.tray_icon.activated.connect(self._tray_icon_activated)
    
    def _create_tray_menu(self):
        """创建托盘菜单"""
        tray_menu = QMenu()
        
        action_show = QAction("显示窗口", self.main_window)
        action_show.triggered.connect(self._show_window)
        
        action_exit = QAction("退出", self.main_window)
        action_exit.triggered.connect(self._exit_application)
        
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_exit)
        
        self.tray_icon.setContextMenu(tray_menu)
    
    def _show_window(self):
        """显示主窗口"""
        self.main_window.show()
        self.main_window.raise_()
    
    def _exit_application(self):
        """退出应用程序"""
        if self.tray_icon:
            self.tray_icon.hide()
        QtWidgets.QApplication.quit()
    
    def _tray_icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window() if self.main_window.isHidden() else self.hide_to_tray()
    
    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        self.main_window.hide()
        if self.tray_icon:
            self.tray_icon.show()
    
    def handle_mouse_press(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.main_window.rect().contains(event.pos()) and event.pos().y() < 60:
            self._drag_position = event.globalPosition().toPoint() - self.main_window.frameGeometry().topLeft()
            event.accept()
    
    def handle_mouse_move(self, event):
        """处理鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_position.isNull():
            self.main_window.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def handle_mouse_release(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()
    
    def toggle_maximize(self):
        """切换窗口最大化/正常状态"""
        self.main_window.showNormal() if self.main_window.isMaximized() else self.main_window.showMaximized()

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """主窗口类，负责应用程序的主要界面和功能协调"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.setupUi(self)
        
        # 初始化管理器
        self.window_manager = WindowManager(self)
        
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        """设置UI"""
        self.window_manager.setup_window()
        self.window_manager.setup_system_tray()

    def _connect_signals(self):
        """连接信号和槽函数"""
        # 窗口控制按钮
        self.btnSettings.clicked.connect(self._show_settings)
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self.window_manager.toggle_maximize)
        self.btnClose.clicked.connect(self.window_manager.hide_to_tray)
        
        # 文件夹浏览按钮
        self.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.inputSourceFolder))
        self.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.inputTargetFolder))
        
        # 窗口拖拽事件
        self.mousePressEvent = self.window_manager.handle_mouse_press
        self.mouseMoveEvent = self.window_manager.handle_mouse_move
        self.mouseReleaseEvent = self.window_manager.handle_mouse_release
            
    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", f"打开设置对话框失败: {e}")
    
    def _browse_directory(self, dialog_title, target_widget):
        """浏览文件夹并设置到目标控件"""
        try:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(
                self, dialog_title, "", QtWidgets.QFileDialog.Option.ShowDirsOnly
            )
            
            if folder_path:
                target_widget.setText(folder_path)
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", f"打开{dialog_title}对话框失败: {e}")
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        event.ignore()
        self.window_manager.hide_to_tray()