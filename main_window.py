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
        self.smart_arrange_page = SmartArrangeManager(self, self.folder_page)
        self.write_exif_page = WriteExifManager(self)
        print("INFO: 已初始化所有页面，SmartArrangeManager已连接到FolderPage")

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
        self.btnMinimize.clicked.connect(self.showMinimized)
        self.btnMaximize.clicked.connect(self._toggle_maximize)
        self.btnClose.clicked.connect(self._hide_to_tray)
        
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
        if self.tray_icon:
            self.tray_icon.show()
    
    def _show_window(self):
        self.show()
        self.raise_()
    
    def _exit_app(self):
        if self.tray_icon:
            self.tray_icon.hide()
        QtWidgets.QApplication.quit()
    
    def _handle_tray_activation(self, reason):
        if reason == QtWidgets.QSystemTrayIcon.ActivationReason.Trigger and self.isHidden():
            self._show_window()
        else:
            self._hide_to_tray()
    
    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    
    def closeEvent(self, event):
        event.ignore()
        self._hide_to_tray()