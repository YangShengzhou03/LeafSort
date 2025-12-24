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

version = 2.02

class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self._drag_position = QPoint()
        self.tray_icon = None
        self._exit_requested = False
        self._setup_ui()
        self._initialize_pages()
        self._connect_signals()
        
        try:
            check_update()
        except Exception as e:
            logger.error(f"Error checking for updates: {str(e)}")

    def _initialize_pages(self):
        self.folder_page = FolderPage(self)
        self.smart_arrange_page = SmartArrangeManager(self, self.folder_page)
        self.write_exif_page = WriteExifManager(self, self.folder_page)
        self.deduplication_page = FileDeduplicationManager(self, self.folder_page)

    def _setup_ui(self):
        self.setWindowTitle("LeafSort")
        icon_path = get_resource_path('_internal/resources/img/icon.ico')
        if icon_path:
            self.setWindowIcon(QtGui.QIcon(icon_path))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self._setup_system_tray()

    def _setup_system_tray(self):
        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        icon_path = get_resource_path('_internal/resources/img/icon.ico')
        if icon_path:
            self.tray_icon.setIcon(QtGui.QIcon(icon_path))
        self.tray_icon.setToolTip("LeafSort")
        tray_menu = QtWidgets.QMenu()
        action_show = QtGui.QAction("显示窗口", self)
        action_show.triggered.connect(self._show_window)
        action_exit = QtGui.QAction("退出应用", self)
        action_exit.triggered.connect(self._exit_app)
        tray_menu.addAction(action_show)
        tray_menu.addSeparator()
        tray_menu.addAction(action_exit)
        css_path = get_resource_path('_internal/resources/stylesheet/menu.setStyleSheet.css')
        if css_path and os.path.exists(css_path):
            try:
                with open(css_path, 'r', encoding='utf-8') as f:
                    tray_menu.setStyleSheet(f.read())
            except Exception as e:
                logger.error(f"Error reading menu stylesheet: {str(e)}")
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self._handle_tray_activation)
        self.tray_icon.show()

    def _connect_signals(self):
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self._toggle_maximize)
        self.btnClose.clicked.connect(self._hide_to_tray)
        self.btnGithub.clicked.connect(self._open_github)
        self.btnBadge.clicked.connect(self._open_microsoft)

    def mousePressEvent(self, event):
        if (event.button() == Qt.MouseButton.LeftButton and
                self.rect().contains(event.pos()) and
                event.pos().y() < 60):
            self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if (event.buttons() == Qt.MouseButton.LeftButton and
                not self._drag_position.isNull()):
            if self.isMaximized():
                self.showNormal()
                self.btnMaximize.setIcon(QtGui.QIcon(get_resource_path('_internal/resources/img/窗口控制/最大化.svg')))
                screen = QtWidgets.QApplication.primaryScreen().availableGeometry()
                window_rect = self.frameGeometry()
                center_point = screen.center()
                window_rect.moveCenter(center_point)
                self.move(window_rect.topLeft())
                self._drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            self.move(event.globalPosition().toPoint() - self._drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_position = QPoint()

    def _hide_to_tray(self):
        self.hide()
        self.tray_icon.show()
        self.tray_icon.showMessage(
            "LeafSort",
            "应用在后台继续运行",
            QtWidgets.QSystemTrayIcon.MessageIcon.Information,
            3000
        )

    def _show_window(self):
        self.show()
        self.raise_()

    def _exit_app(self):
        self._exit_requested = True
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
            self.btnMaximize.setIcon(QtGui.QIcon(get_resource_path('_internal/resources/img/窗口控制/最大化.svg')))
        else:
            self.showMaximized()
            self.btnMaximize.setIcon(QtGui.QIcon(get_resource_path('_internal/resources/img/窗口控制/还原.svg')))

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.Type.WindowStateChange:
            pass
        super().changeEvent(event)
    
    def closeEvent(self, event):
        if self._exit_requested:
            event.accept()
        else:
            event.ignore()
            self._hide_to_tray()

    def _open_github(self):
        url = QtCore.QUrl("https://gitee.com/Yangshengzhou/leaf-sort")
        if not QtGui.QDesktopServices.openUrl(url):
            QtWidgets.QMessageBox.information(self, "信息",
                                              "无法打开GitHub页面，请手动访问")

    def _open_microsoft(self):
        url = QtCore.QUrl("https://apps.microsoft.com/detail/9p3mkv4xslj8?hl=zh&gl=CN&ocid=pdpshare")
        if not QtGui.QDesktopServices.openUrl(url):
            QtWidgets.QMessageBox.information(self, "信息",
                                              "无法打开Microsoft页面，请手动访问")
