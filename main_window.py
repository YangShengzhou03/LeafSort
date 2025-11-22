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
    """枫叶相册主窗口类"""
    
    def __init__(self):
        """初始化主窗口"""
        super().__init__()
        
        # 初始化变量
        self.current_page_index = -1
        self.page_cache = {}
        self._drag_position = QPoint()
        
        # 初始化UI和组件
        self.setupUi(self)
        self._init_window()
        self._init_system_tray()
        
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
        """初始化窗口属性"""
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
    def _connect_signals(self):
        """连接UI元素的信号槽"""
        # 窗口控制按钮
        self.btnSettings.clicked.connect(self._show_settings)
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self._toggle_maximize)
        self.btnClose.clicked.connect(self.hide_to_tray)
        
        # 文件浏览按钮
        self.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.inputSourceFolder))
        self.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.inputTargetFolder))
        
        # 窗口拖动事件
        self.mousePressEvent = self._on_mouse_press
        self.mouseMoveEvent = self._on_mouse_move
        self.mouseReleaseEvent = self._on_mouse_release
            
    def _show_settings(self):
        """显示设置对话框"""
        try:
            dialog = SettingsDialog(self)
            dialog.exec()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "错误", f"打开设置对话框时出错: {str(e)}")
    
    def _toggle_maximize(self):
        """切换窗口最大化/正常状态"""
        self.showNormal() if self.isMaximized() else self.showMaximized()
            
    def _init_system_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.tray_icon.setToolTip("枫叶相册")
        self._create_tray_menu()
        self.tray_icon.activated.connect(self._tray_icon_activated)
        
    def _create_tray_menu(self):
        """创建托盘菜单"""
        self.tray_menu = QMenu()
        
        # 创建并添加菜单动作
        self.action_show = QAction("显示窗口", self)
        self.action_show.triggered.connect(self._show_window)
        
        self.action_exit = QAction("退出", self)
        self.action_exit.triggered.connect(self._exit_application)
        
        self.tray_menu.addAction(self.action_show)
        self.tray_menu.addSeparator()
        self.tray_menu.addAction(self.action_exit)
        
        self.tray_icon.setContextMenu(self.tray_menu)
        
    def _show_window(self):
        """从托盘显示窗口"""
        self.show()
        self.raise_()
        
    def _exit_application(self):
        """退出应用程序"""
        self.tray_icon.hide()
        QtWidgets.QApplication.quit()
        
    def _tray_icon_activated(self, reason):
        """处理托盘图标激活事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self._show_window() if self.isHidden() else self.hide()
                
    def hide_to_tray(self):
        """隐藏窗口到系统托盘"""
        self.hide()
        self.tray_icon.show()
        
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        event.ignore()
        self.hide_to_tray()
    
    def _on_mouse_press(self, event):
        """处理鼠标按下事件，实现窗口拖动"""
        if event.button() == Qt.MouseButton.LeftButton and self.rect().contains(event.pos()) and event.pos().y() < 60:
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def _on_mouse_move(self, event):
        """处理鼠标移动事件，实现窗口拖动"""
        if event.buttons() == Qt.MouseButton.LeftButton and not self._drag_position.isNull():
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()
    
    def _on_mouse_release(self, event):
        """处理鼠标释放事件，结束窗口拖动"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()
    
    def _browse_directory(self, dialog_title, target_widget):
        """通用目录浏览函数"""
        try:
            folder_path = QtWidgets.QFileDialog.getExistingDirectory(
                self, dialog_title, "", QtWidgets.QFileDialog.Option.ShowDirsOnly
            )
            
            if folder_path:
                target_widget.setText(folder_path)
                self.log("INFO", f"已选择{dialog_title.replace('选择', '')}: {folder_path}")
        except Exception as e:
            self.log("ERROR", f"打开{dialog_title}对话框失败: {str(e)}")
    
    def log(self, level, message):
        """记录日志消息到当前页面的日志组件"""
        # 格式化日志消息
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        # 简化日志组件查找逻辑
        log_components = {
            0: 'textBrowser_import_info',  # 导入信息显示组件
            1: 'txtSmartArrangeLog',  # 智能整理日志组件
            2: 'textBrowser_ThumbnailGenLog',  # 缩略图生成日志框
            3: 'txtWriteEXIFLog'  # EXIF写入日志组件
        }
        
        try:
            # 添加调试信息
            current_index = self.stackedWidget.currentIndex()
            component_name = log_components.get(current_index)
            
            # 调试输出
            print(f"[调试] 当前页面索引: {current_index}, 目标日志组件: {component_name}")
            
            if component_name:
                # 检查组件是否存在
                if hasattr(self, component_name):
                    log_widget = getattr(self, component_name)
                    if log_widget and hasattr(log_widget, 'append'):
                        print(f"[调试] 成功访问日志组件: {component_name}")
                        log_widget.append(log_message)
                    else:
                        print(f"[调试] 组件存在但缺少append方法: {component_name}")
                else:
                    print(f"[调试] 组件不存在: {component_name}")
                    # 尝试在所有可能的日志组件中查找
                    for name, widget_name in log_components.items():
                        if hasattr(self, widget_name):
                            print(f"[调试] 发现可用的日志组件: {widget_name}")
        except Exception as e:
            print(f"[调试] 日志处理异常: {str(e)}")
            pass  # 静默失败，避免日志功能影响主程序运行