from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from smart_arrange import SmartArrangeManager
from write_exif import WriteExifManager
from common import get_resource_path

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        self.setupUi(self)
        
        self._drag_position = QPoint()
        self.tray_icon = None
        
        self._initialize_pages()
        
        self._setup_ui()
        self._connect_signals()
        
    def _initialize_pages(self):
        self.folder_page = FolderPage(self)
        self.smart_arrange_page = SmartArrangeManager(self)
        self.write_exif_page = WriteExifManager(self)

    def _setup_ui(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self._setup_system_tray()
        
    def _setup_system_tray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.tray_icon.setToolTip("枫叶相册")
        
        tray_menu = QtWidgets.QMenu()
        action_show = QtGui.QAction("显示窗口", self)
        action_show.triggered.connect(self._show_window)
        action_exit = QtGui.QAction("退出", self)
        action_exit.triggered.connect(self._exit_app)
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_exit)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activation)

    def _connect_signals(self):
        self.btnSettings.clicked.connect(self._show_settings)
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self._toggle_maximize)
        self.btnClose.clicked.connect(self._hide_to_tray)
        
        self.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.inputSourceFolder))
        self.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.inputTargetFolder))
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()) and event.pos().y() < 60:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()
            
    def _hide_to_tray(self):
        self.hide()
        self.tray_icon and self.tray_icon.show()
            
    def _show_settings(self):
        pass
    
    def _get_folder_info(self, folder_path):
        """
        获取文件夹的极速信息，完全避免任何递归操作，适用于超大文件夹
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            包含文件夹信息的字符串
        """
        import os
        
        # 格式化文件大小
        def format_size(size_bytes):
            """将字节大小格式化为人类可读的格式"""
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        
        # 构建信息字符串，使用两列布局
        info = f"{'='*10} 待处理的源文件夹信息 {'='*10}\n"
        info += f"路径：{folder_path}\n"
        
        # 只获取顶层文件夹信息，完全避免任何递归操作
        top_file_count = 0
        top_folder_count = 0
        try:
            # 只列出顶层内容，不递归
            items = os.listdir(folder_path)
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    top_file_count += 1
                elif os.path.isdir(item_path):
                    top_folder_count += 1
        except (OSError, FileNotFoundError, PermissionError) as e:
            pass
        
        # 使用两列布局显示信息
        info += f"{'-' * 60}\n"
        info += f"{'顶层内容统计':<60}\n"
        info += f"{'顶层文件数量：' + str(top_file_count):<30} {'顶层文件夹数量：' + str(top_folder_count):<30}\n"
        info += f"{'-' * 60}\n"
        return info
    
    def _browse_directory(self, dialog_title, target_widget):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, dialog_title, "", QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            target_widget.setText(folder_path)
            # 如果是源文件夹，则显示文件夹信息
            if target_widget == self.inputSourceFolder:
                folder_info = self._get_folder_info(folder_path)
                self.textBrowser_import_info.setText(folder_info)
    
    def _show_window(self):
        self.show()
        self.raise_()
    
    def _exit_app(self):
        self.tray_icon.hide()
        QtWidgets.QApplication.quit()
    
    def _handle_tray_activation(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger and self.isHidden():
            self._show_window()
        else:
            self._hide_to_tray()
    
    def _toggle_maximize(self):
        self.showNormal() if self.isMaximized() else self.showMaximized()
    
    def closeEvent(self, event):
        event.ignore()
        self._hide_to_tray()