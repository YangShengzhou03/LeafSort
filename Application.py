import sys
import logging
import traceback
import socket
import os
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtGui import QFontDatabase, QFont
from main_window import MainWindow
from common import get_resource_path

CUSTOM_FONT_FAMILY = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)


def load_custom_font():
    global CUSTOM_FONT_FAMILY
    font_path = get_resource_path("resources/fonts/Microsoft YaHei UI Light.ttf")
    if font_path and os.path.exists(font_path):
        font_id = QFontDatabase.addApplicationFont(font_path)
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            if families:
                CUSTOM_FONT_FAMILY = families[0]
                logging.info(f"Loaded custom font: {CUSTOM_FONT_FAMILY}")
                return True
    logging.warning("Failed to load custom font, using system default")
    return False


def apply_app_font(app):
    global CUSTOM_FONT_FAMILY
    if CUSTOM_FONT_FAMILY:
        font = QFont(CUSTOM_FONT_FAMILY, 10)
        app.setFont(font)


def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))
    app = QApplication.instance()
    if app:
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(f"Error: {exc_type.__name__}: {exc_value}")
        print(error_message)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText("An unexpected error occurred. The application may need to close.")
        msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
        msg.setDetailedText(error_message)
        msg.exec()


def main():
    try:
        QCoreApplication.setApplicationName("LeafSort（轻羽媒体整理）")
        QCoreApplication.setApplicationVersion("2.0.2")
        global lock_socket
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            lock_socket.bind(('127.0.0.1', 12345))
            lock_socket.listen(1)
        except socket.error:
            logging.info("Application already running")
            QMessageBox.warning(None, "提示", "程序已在运行中")
            return
        app = QApplication(sys.argv)
        load_custom_font()
        apply_app_font(app)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"Failed to start application: {str(e)}")
        print(f"Start error: {str(e)}")
        traceback.print_exc()
        QMessageBox.critical(None, "致命错误", f"应用程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    sys.excepthook = handle_exception
    main()
