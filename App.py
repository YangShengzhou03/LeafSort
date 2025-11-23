from PyQt6 import QtWidgets, QtCore
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from contextlib import closing
from main_window import MainWindow
import sys
import traceback

APP_SERVER_NAME = "LeafView_Server"
BRING_TO_FRONT_COMMAND = b'bringToFront'

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    
    app = QtWidgets.QApplication.instance()
    if app:
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setWindowTitle("应用程序错误")
        msg.setText("发生意外错误，应用程序可能需要关闭。")
        msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
        msg.setDetailedText(error_message)
        msg.exec()

def main():
    sys.excepthook = handle_exception
    
    with closing(QLocalSocket()) as socket:
        try:
            if socket.connectToServer(APP_SERVER_NAME) and socket.waitForConnected(500):
                socket.write(BRING_TO_FRONT_COMMAND)
                socket.waitForBytesWritten(1000)
                return 0
        except (QtCore.QObject.QObjectError, ConnectionError):
            pass
    
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("LeafView")
    app.setApplicationVersion("1.3")
    
    QLocalServer.removeServer(APP_SERVER_NAME)
    local_server = None
    try:
        local_server = QLocalServer()
        local_server.listen(APP_SERVER_NAME)
    except Exception:
        pass
    
    try:
        window = MainWindow()
        window.move(300, 100)
        window.show()
        
        if local_server:
            def handle_socket_data(socket):
                if socket.bytesAvailable() > 0 and socket.readAll().data() == BRING_TO_FRONT_COMMAND:
                    window.activateWindow()
                    window.raise_()
                    window.showNormal()
                socket.deleteLater()
            
            def handle_connection():
                if socket := local_server.nextPendingConnection():
                    socket.readyRead.connect(lambda: handle_socket_data(socket))
            
            local_server.newConnection.connect(handle_connection)
        
        return app.exec()
        
    except Exception as e:
        error_msg = f"应用程序启动失败: {e}"
        try:
            QtWidgets.QMessageBox.critical(None, "致命错误", error_msg)
        except Exception:
            pass
        return 1
    finally:
        if local_server:
            local_server.close()

if __name__ == '__main__':
    sys.exit(main())