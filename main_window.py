from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
from PyQt6.QtGui import QAction

from SettingsDialog import SettingsDialog
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from smart_arrange import SmartArrangePage
from remove_duplication import RemoveDuplicationPage
from write_exif import WriteExifPage
from common import get_resource_path

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """主窗口类，负责应用程序的主要界面和功能协调"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        self.setupUi(self)
        
        # 窗口拖拽变量
        self._drag_position = QPoint()
        self.tray_icon = None
        
        # 初始化页面
        self._initialize_pages()
        
        self._setup_ui()
        self._connect_signals()
        
    def _initialize_pages(self):
        """初始化各个功能页面"""
        # 简化页面初始化，只传递必要的parent参数
        self.folder_page = FolderPage(self)
        self.smart_arrange_page = SmartArrangePage(self)
        self.remove_duplication_page = RemoveDuplicationPage(self)
        self.write_exif_page = WriteExifPage(self)

    def _setup_ui(self):
        """设置UI"""
        # 设置窗口属性
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置系统托盘
        self._setup_system_tray()
        
    def _setup_system_tray(self):
        """设置系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.tray_icon.setToolTip("枫叶相册")
        
        # 创建托盘菜单
        tray_menu = QMenu()
        action_show = QAction("显示窗口", self)
        action_show.triggered.connect(lambda: (self.show(), self.raise_()))
        action_exit = QAction("退出", self)
        action_exit.triggered.connect(lambda: (self.tray_icon.hide(), QtWidgets.QApplication.quit()))
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_exit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(lambda reason: (self.show(), self.raise_()) if reason == QSystemTrayIcon.ActivationReason.Trigger and self.isHidden() else self._hide_to_tray())

    def _connect_signals(self):
        """连接信号和槽函数"""
        # 窗口控制按钮
        self.btnSettings.clicked.connect(self._show_settings)
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(lambda: self.showNormal() if self.isMaximized() else self.showMaximized())
        self.btnClose.clicked.connect(self._hide_to_tray)
        
        # 文件夹浏览按钮
        self.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.inputSourceFolder))
        self.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.inputTargetFolder))
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()) and event.pos().y() < 60:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()
            
    def _hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        self.hide()
        if self.tray_icon:
            self.tray_icon.show()
            
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
        self._hide_to_tray()