import sys
import logging
import traceback
import socket
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QCoreApplication
from main_window import MainWindow

logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',handlers=[logging.FileHandler("app.log"), logging.StreamHandler()])
logger = logging.getLogger(__name__)

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
        QCoreApplication.setApplicationName("LeafView")
        QCoreApplication.setApplicationVersion("1.0.0")
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', 12345))
        except socket.error:
            logging.info("Application already running")
            return
        app = QApplication(sys.argv)
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
