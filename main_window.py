from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from smart_arrange import SmartArrangeManager
from write_exif import WriteExifManager
from common import get_resource_path
import logging
import os

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        """初始化主窗口"""
        try:
            super().__init__()
            self.setupUi(self)
            self._drag_position = QPoint()
            self.tray_icon = None
            
            # 按照依赖顺序初始化各个组件
            self._initialize_pages()
            self._setup_ui()
            self._connect_signals()
            
            logger.info("主窗口初始化完成")
        except Exception as e:
            logger.error(f"初始化主窗口时出错: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "错误", f"初始化失败: {str(e)}")
        
    def _initialize_pages(self):
        """初始化应用程序的各个功能页面"""
        try:
            self.folder_page = FolderPage(self)
            self.smart_arrange_page = SmartArrangeManager(self, self.folder_page)
            self.write_exif_page = WriteExifManager(self)
            logger.info("所有页面组件初始化完成")
        except Exception as e:
            logger.error(f"初始化页面组件时出错: {str(e)}")

    def _setup_ui(self):
        """设置窗口的基本属性和外观"""
        try:
            # 设置窗口标题
            self.setWindowTitle("枫叶相册")
            
            # 设置窗口图标
            icon_path = get_resource_path('resources/img/icon.ico')
            if icon_path:
                self.setWindowIcon(QtGui.QIcon(icon_path))
            
            # 设置窗口样式
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            
            # 设置系统托盘
            self._setup_system_tray()
            
            logger.info("窗口UI设置完成")
        except Exception as e:
            logger.error(f"设置窗口UI时出错: {str(e)}")
        
    def _setup_system_tray(self):
        """设置系统托盘图标和菜单"""
        try:
            self.tray_icon = QtWidgets.QSystemTrayIcon(self)
            
            # 设置图标
            icon_path = get_resource_path('resources/img/icon.ico')
            if icon_path:
                self.tray_icon.setIcon(QtGui.QIcon(icon_path))
            self.tray_icon.setToolTip("枫叶相册")
            
            # 创建菜单
            tray_menu = QtWidgets.QMenu()
            action_show = QtGui.QAction("显示窗口", self)
            action_show.triggered.connect(self._show_window)
            action_exit = QtGui.QAction("退出", self)
            action_exit.triggered.connect(self._exit_app)
            
            tray_menu.addAction(action_show)
            tray_menu.addSeparator()
            tray_menu.addAction(action_exit)
            
            # 应用样式表，使用更合理的文件名
            css_path = get_resource_path('resources/stylesheet/menu_stylesheet.css')
            if css_path and os.path.exists(css_path):
                try:
                    with open(css_path, 'r', encoding='utf-8') as f:
                        tray_menu.setStyleSheet(f.read())
                    logger.info("应用托盘菜单样式")
                except Exception as e:
                    logger.error(f"读取菜单样式表出错: {str(e)}")
            
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.activated.connect(self._handle_tray_activation)
            self.tray_icon.show()
            logger.info("系统托盘已设置")
        except Exception as e:
            logger.error(f"设置系统托盘时出错: {str(e)}")

    def _connect_signals(self):
        """连接UI控件的信号和槽"""
        try:
            # 检查按钮是否存在，避免属性错误
            if hasattr(self, 'btnMinimize'):
                self.btnMinimize.clicked.connect(self.showMinimized)
            if hasattr(self, 'btnMaximize'):
                self.btnMaximize.clicked.connect(self._toggle_maximize)
            if hasattr(self, 'btnClose'):
                self.btnClose.clicked.connect(self._hide_to_tray)
            
            logger.info("UI信号连接完成")
        except Exception as e:
            logger.error(f"连接UI信号时出错: {str(e)}")
        
    def mousePressEvent(self, event):
        """处理鼠标按下事件，用于拖动无框窗口"""
        try:
            # 只在窗口顶部区域允许拖动
            if (event.button() == Qt.MouseButton.LeftButton and 
                self.rect().contains(event.pos()) and 
                event.pos().y() < 60):
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            logger.error(f"处理鼠标按下事件时出错: {str(e)}")
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件，实现窗口拖动"""
        try:
            if (event.buttons() == Qt.MouseButton.LeftButton and 
                not self._drag_position.isNull()):
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
        except Exception as e:
            logger.error(f"处理鼠标移动事件时出错: {str(e)}")
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件，结束窗口拖动"""
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_position = QPoint()
        except Exception as e:
            logger.error(f"处理鼠标释放事件时出错: {str(e)}")
            
    def _hide_to_tray(self):
        """将窗口隐藏到系统托盘"""
        try:
            self.hide()
            if self.tray_icon:
                self.tray_icon.show()
                logger.info("窗口已隐藏到托盘")
        except Exception as e:
            logger.error(f"隐藏窗口到托盘时出错: {str(e)}")
    
    def _show_window(self):
        """从系统托盘显示窗口"""
        try:
            self.show()
            self.raise_()
            logger.info("窗口已从托盘显示")
        except Exception as e:
            logger.error(f"显示窗口时出错: {str(e)}")
    
    def _exit_app(self):
        """完全退出应用程序"""
        try:
            # 隐藏托盘图标
            if self.tray_icon:
                self.tray_icon.hide()
            
            logger.info("应用程序正在退出")
            QtWidgets.QApplication.quit()
        except Exception as e:
            logger.error(f"退出应用程序时出错: {str(e)}")
    
    def _handle_tray_activation(self, reason):
        """处理系统托盘图标激活事件"""
        # 点击托盘图标时切换窗口显示状态
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self._show_window()
            else:
                self._hide_to_tray()
        logger.debug(f"托盘图标激活: {reason}")
    
    def _toggle_maximize(self):
        """切换窗口最大化/还原状态"""
        try:
            if self.isMaximized():
                self.showNormal()
                logger.info("窗口已还原")
            else:
                self.showMaximized()
                logger.info("窗口已最大化")
        except Exception as e:
            logger.error(f"切换窗口最大化状态时出错: {str(e)}")
    
    def closeEvent(self, event):
        """重写关闭事件，隐藏到托盘而不是真正关闭"""
        event.ignore()  # 忽略关闭事件
        self._hide_to_tray()
        logger.info("窗口已隐藏到托盘")