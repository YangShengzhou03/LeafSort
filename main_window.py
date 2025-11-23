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
        获取文件夹的详细信息，包括大小、文件数、子文件夹数、文件类型统计等
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            包含文件夹信息的字符串
        """
        import os
        from datetime import datetime
        
        # 初始化计数器
        total_size = 0
        file_count = 0
        subfolder_count = 0
        # 文件类型统计
        file_types = {}
        # 最近修改时间
        latest_modified = None
        earliest_modified = None
        # 大型文件跟踪（超过100MB的文件）
        large_files = []
        
        try:
            # 获取文件夹基本信息
            folder_stats = os.stat(folder_path)
            folder_creation_time = datetime.fromtimestamp(folder_stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')
            folder_modified_time = datetime.fromtimestamp(folder_stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            
            # 遍历文件夹及其子文件夹
            for root, dirs, files in os.walk(folder_path):
                # 计算子文件夹数量
                if root != folder_path:
                    subfolder_count += len(dirs)
                
                # 计算文件数量和总大小，统计文件类型
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        # 获取文件大小
                        file_size = os.path.getsize(file_path)
                        total_size += file_size
                        file_count += 1
                        
                        # 跟踪大型文件（>100MB）
                        if file_size > 100 * 1024 * 1024:
                            large_files.append((file, file_size))
                        
                        # 统计文件类型
                        _, ext = os.path.splitext(file)
                        ext = ext.lower() or '(无扩展名)'
                        file_types[ext] = file_types.get(ext, 0) + 1
                        
                        # 更新修改时间统计
                        file_mtime = os.path.getmtime(file_path)
                        if latest_modified is None or file_mtime > latest_modified:
                            latest_modified = file_mtime
                        if earliest_modified is None or file_mtime < earliest_modified:
                            earliest_modified = file_mtime
                    except (OSError, FileNotFoundError, PermissionError):
                        # 忽略无法访问的文件
                        continue
            
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
            
            # 构建信息字符串
            info = f"=== 文件夹详细信息 ===\n"
            info += f"路径：{folder_path}\n"
            info += f"创建时间：{folder_creation_time}\n"
            info += f"修改时间：{folder_modified_time}\n"
            info += f"\n--- 空间统计 ---\n"
            info += f"总大小：{format_size(total_size)}\n"
            info += f"平均文件大小：{format_size(total_size / file_count if file_count > 0 else 0)}\n"
            info += f"\n--- 文件统计 ---\n"
            info += f"文件总数：{file_count}\n"
            info += f"子文件夹总数：{subfolder_count}\n"
            
            # 添加文件时间范围信息
            if latest_modified is not None:
                latest_str = datetime.fromtimestamp(latest_modified).strftime('%Y-%m-%d %H:%M:%S')
                earliest_str = datetime.fromtimestamp(earliest_modified).strftime('%Y-%m-%d %H:%M:%S')
                info += f"\n--- 时间范围 ---\n"
                info += f"最早修改：{earliest_str}\n"
                info += f"最近修改：{latest_str}\n"
            
            # 添加文件类型统计，只显示数量最多的前10种类型
            if file_types:
                info += f"\n--- 文件类型统计 (前10种) ---\n"
                sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:10]
                for ext, count in sorted_types:
                    percentage = (count / file_count * 100) if file_count > 0 else 0
                    info += f"{ext}: {count} 个 ({percentage:.1f}%)\n"
                
                # 如果有更多类型，显示总数
                if len(file_types) > 10:
                    info += f"... 还有 {len(file_types) - 10} 种其他文件类型\n"
            
            # 添加大型文件信息
            if large_files:
                info += f"\n--- 大型文件 (>100MB) ---\n"
                # 最多显示5个最大的文件
                large_files.sort(key=lambda x: x[1], reverse=True)
                for file, size in large_files[:5]:
                    info += f"{file}: {format_size(size)}\n"
                if len(large_files) > 5:
                    info += f"... 还有 {len(large_files) - 5} 个大型文件\n"
            
            return info
        except Exception as e:
            return f"获取文件夹信息失败：{str(e)}"
    
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