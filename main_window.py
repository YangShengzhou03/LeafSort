from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint

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
        # 初始化各功能页面
        for page_name, page in self.pages.items():
            try:
                page.init_page()
            except Exception as e:
                print(f"初始化{page_name}页面失败: {str(e)}")
        
        # 设置导航菜单的初始状态
        self.listNavigationMenu.setCurrentRow(0)
        
    def _connect_signals(self):
        """连接信号槽"""
        # 设置按钮点击事件
        try:
            # 设置按钮连接
            self.btnSettings.clicked.connect(self._show_settings)
            
            # 窗口控制按钮连接
            try:
                self.btnMinimize.clicked.connect(self.showMinimized)
                self.btnMaximize.clicked.connect(self._toggle_maximize)
                self.btnClose.clicked.connect(self.close)
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
            
    def log(self, level, message):
        """日志记录功能"""
        # 实现日志记录功能，将日志显示在UI上
        timestamp = QtCore.QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        log_message = f"[{timestamp}] [{level}] {message}\n"
        
        # 根据当前活动页面显示在对应的日志组件中
        try:
            current_index = self.stackedWidget.currentIndex()
            
            # 定义页面索引到可能的日志组件名称的映射
            log_components = {
                0: ['textBrowser_import_info'],
                1: ['smartArrangeLogOutputTextEdit'],
                2: ['textBrowser_duplication_log', 'textBrowser_duplication', 'textBrowser_log_duplication'],
                3: ['textBrowser_EXIF_log', 'textBrowser_exif', 'textBrowser_log_exif']
            }
            
            # 尝试使用映射中的组件
            if current_index in log_components:
                for component_name in log_components[current_index]:
                    try:
                        getattr(self, component_name).append(log_message)
                        break
                    except (AttributeError, TypeError):
                        pass
        except Exception as e:
            print(f"写入日志到UI失败: {str(e)}")
            
        print(log_message)