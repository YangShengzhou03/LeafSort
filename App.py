import sys
import logging
import traceback
import socket
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QCoreApplication
from main_window import MainWindow

# 配置logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("未处理的异常", exc_info=(exc_type, exc_value, exc_traceback))
    
    app = QtWidgets.QApplication.instance()
    if app:
        try:
            error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setWindowTitle("应用程序错误")
            msg.setText("发生意外错误，应用程序可能需要关闭。")
            msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
            msg.setDetailedText(error_message)
            msg.exec()
        except Exception:
            pass

def main():
    try:
        QCoreApplication.setApplicationName("LeafView")
        QCoreApplication.setApplicationVersion("1.0.0")
        
        # 改进的单实例检测
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', 12345))
        except socket.error:
            logging.info("应用程序已在运行")
            return
        
        app = QApplication(sys.argv)
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"应用启动失败: {str(e)}")
        try:
            QtWidgets.QMessageBox.critical(None, "致命错误", f"应用程序启动失败: {str(e)}")
        except Exception:
            pass
        sys.exit(1)

if __name__ == "__main__":
    sys.excepthook = handle_exception
    main()