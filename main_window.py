import os
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import Qt, QPoint
from Ui_MainWindow import Ui_MainWindow
from add_folder import FolderPage
from smart_arrange import SmartArrangeManager
from write_exif import WriteExifManager
from file_deduplication import FileDeduplicationManager
from update_dialog import check_update
from common import get_resource_path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

version = 2.0

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._drag_position = QPoint()
        self.tray_icon = None
        self._setup_ui()
        self._initialize_pages()
        self._connect_signals()
        
        
        try:
            check_update()
        except Exception as e:
            logger.error(f"检查更新时出错: {str(e)}")

    def _initialize_pages(self):
        self.folder_page = FolderPage(self)
        self.smart_arrange_page = SmartArrangeManager(self, self.folder_page)
        self.write_exif_page = WriteExifManager(self, self.folder_page)
        self.deduplication_page = FileDeduplicationManager(self, self.folder_page)

    def _setup_ui(self):
        self.setWindowTitle("枫叶相册")
        icon_path = get_resource_path('resources/img/icon.ico')
        if icon_path:
            self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_system_tray()

    def _setup_system_tray(self):
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
        css_path = get_resource_path('resources/stylesheet/menu.setStyleSheet.css')
        if css_path and os.path.exists(css_path):
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    tray_menu.setStyleSheet(f.read())
            except Exception as e:
                logger.error(f"读取菜单样式表出错: {str(e)}")
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activation)
        self.tray_icon.show()

    def _connect_signals(self):
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self._toggle_maximize)
        self.btnClose.clicked.connect(self._hide_to_tray)
        self.btnGithub.clicked.connect(self._open_github)

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton and
                self.rect().contains(event.pos()) and
                event.pos().y() < 60):
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.MouseButton.LeftButton and
                not self._drag_position.isNull()):
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()

    def _hide_to_tray(self):
        self.hide()
        self.tray_icon.show()

    def _show_window(self):
        self.show()
        self.raise_()

    def _exit_app(self):
        self.tray_icon.hide()
        QtWidgets.QApplication.quit()

    def _handle_tray_activation(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger:
            if self.isHidden():
                self._show_window()
            else:
                self._hide_to_tray()

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
            self.btnMaximize.setIcon(QtGui.QIcon(get_resource_path('resources/img/窗口控制/最大化.svg')))
        else:
            self.showMaximized()
            self.btnMaximize.setIcon(QtGui.QIcon(get_resource_path('resources/img/窗口控制/还原.svg')))

    def closeEvent(self, event):
        event.ignore()
        self._hide_to_tray()

    def _open_github(self):
        url = QtCore.QUrl("https://gitee.com/Yangshengzhou/leaf-view")
        if not QtGui.QDesktopServices.openUrl(url):
            QtWidgets.QMessageBox.information(self, "信息",
                                              "无法打开GitHub页面，请手动访问")