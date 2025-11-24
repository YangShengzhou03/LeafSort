from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from smart_arrange import SmartArrangeManager
from write_exif import WriteExifManager
from common import get_resource_path
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        try:
            super().__init__()
            self.setupUi(self)
            self._drag_position = QPoint()
            self.tray_icon = None
            
            self._initialize_pages()
            self._setup_ui()
            self._connect_signals()
            
            logger.info("主窗口初始化完成")
        except Exception as e:
            logger.error(f"初始化主窗口时出错: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "错误", f"初始化失败: {str(e)}")
        
    def _initialize_pages(self):
        try:
            self.folder_page = FolderPage(self)
            self.smart_arrange_page = SmartArrangeManager(self, self.folder_page)
            self.write_exif_page = WriteExifManager(self)
            logger.info("所有页面组件初始化完成")
        except Exception as e:
            logger.error(f"初始化页面组件时出错: {str(e)}")

    def _setup_ui(self):
        try:
            self.setWindowTitle("枫叶相册")
            
            icon_path = get_resource_path('resources/img/icon.ico')
            if icon_path:
                self.setWindowIcon(QtGui.QIcon(icon_path))
            
            self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
            self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
            
            self._setup_system_tray()
            
            logger.info("窗口UI设置完成")
        except Exception as e:
            logger.error(f"设置窗口UI时出错: {str(e)}")
        
    def _setup_system_tray(self):
        try:
            self.tray_icon = QtWidgets.QSystemTrayIcon(self)
            
            icon_path = get_resource_path('resources/img/icon.ico')
            if icon_path:
                self.tray_icon.setIcon(QtGui.QIcon(icon_path))
            self.tray_icon.setToolTip("枫叶相册")
            
            tray_menu = QtWidgets.QMenu()
            action_show = QtGui.QAction("显示窗口", self)
            action_show.triggered.connect(self._show_window)
            action_exit = QtGui.QAction("退出", self)
            action_exit.triggered.connect(self._exit_app)
            
            tray_menu.addAction(action_show)
            tray_menu.addSeparator()
            tray_menu.addAction(action_exit)
            
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
        try:
            if hasattr(self, 'btnMinimize'):
                self.btnMinimize.clicked.connect(self.showMinimized)
            if hasattr(self, 'btnMaximize'):
                self.btnMaximize.clicked.connect(self._toggle_maximize)
            if hasattr(self, 'btnClose'):
                self.btnClose.clicked.connect(self._hide_to_tray)
            if hasattr(self, 'btnGitHub'):
                self.btnGitHub.clicked.connect(self._open_github)
            
            logger.info("UI信号连接完成")
        except Exception as e:
            logger.error(f"连接UI信号时出错: {str(e)}")
        
    def mousePressEvent(self, event):
        try:
            if (event.button() == Qt.MouseButton.LeftButton and 
                self.rect().contains(event.pos()) and 
                event.pos().y() < 60):
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            logger.error(f"处理鼠标按下事件时出错: {str(e)}")
    
    def mouseMoveEvent(self, event):
        try:
            if (event.buttons() == Qt.MouseButton.LeftButton and 
                not self._drag_position.isNull()):
                self.move(event.globalPosition().toPoint() - self._drag_position)
                event.accept()
        except Exception as e:
            logger.error(f"处理鼠标移动事件时出错: {str(e)}")
    
    def mouseReleaseEvent(self, event):
        try:
            if event.button() == Qt.MouseButton.LeftButton:
                self._drag_position = QPoint()
        except Exception as e:
            logger.error(f"处理鼠标释放事件时出错: {str(e)}")
            
    def _hide_to_tray(self):
        try:
            self.hide()
            if self.tray_icon:
                self.tray_icon.show()
                logger.info("窗口已隐藏到托盘")
        except Exception as e:
            logger.error(f"隐藏窗口到托盘时出错: {str(e)}")
    
    def _show_window(self):
        try:
            self.show()
            self.raise_()
            logger.info("窗口已从托盘显示")
        except Exception as e:
            logger.error(f"显示窗口时出错: {str(e)}")
    
    def _exit_app(self):
        try:
            if self.tray_icon:
                self.tray_icon.hide()
            
            logger.info("应用程序正在退出")
            QtWidgets.QApplication.quit()
        except Exception as e:
            logger.error(f"退出应用程序时出错: {str(e)}")
    
    def _handle_tray_activation(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self._show_window()
            else:
                self._hide_to_tray()
        logger.debug(f"托盘图标激活: {reason}")
    
    def _toggle_maximize(self):
        try:
            if self.isMaximized():
                self.showNormal()
                if hasattr(self, 'btnMaximize') and self.btnMaximize is not None:
                    self.btnMaximize.setIcon(self.style().standardIcon(
                        QtWidgets.QStyle.StandardPixmap.SP_TitleBarMaxButton))
                logger.info("窗口已还原")
            else:
                self.showMaximized()
                if hasattr(self, 'btnMaximize') and self.btnMaximize is not None:
                    self.btnMaximize.setIcon(self.style().standardIcon(
                        QtWidgets.QStyle.StandardPixmap.SP_TitleBarNormalButton))
                logger.info("窗口已最大化")
        except Exception as e:
            logger.error(f"切换窗口最大化状态时出错: {str(e)}")
    
    def closeEvent(self, event):
        try:
            event.ignore()
            self._hide_to_tray()
            logger.info("窗口已隐藏到托盘")
        except Exception as e:
            logger.error(f"处理关闭事件时出错: {str(e)}")
            event.accept()
    
    def _open_github(self):
        try:
            url = QtCore.QUrl("https://github.com/yourusername/LeafView")
            if not QtGui.QDesktopServices.openUrl(url):
                logger.warning("无法打开GitHub页面")
                QtWidgets.QMessageBox.information(self, "信息", 
                                                 "无法打开GitHub页面，请手动访问")
            else:
                logger.info("已打开GitHub页面")
        except Exception as e:
            logger.error(f"打开GitHub页面时出错: {str(e)}")
            QtWidgets.QMessageBox.warning(self, "警告", 
                                         f"打开GitHub页面失败: {str(e)}")