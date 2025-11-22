from PyQt6 import QtWidgets, QtCore
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from contextlib import closing
from main_window import MainWindow
import sys
import traceback

APP_SERVER_NAME = "LeafView_Server"
SHARED_MEMORY_KEY = "LeafView_SharedMemory"
BRING_TO_FRONT_COMMAND = b'bringToFront'

def bring_existing_to_front():
    try:
        with closing(QLocalSocket()) as socket:
            if socket.connectToServer(APP_SERVER_NAME) and socket.waitForConnected(500):
                socket.write(BRING_TO_FRONT_COMMAND)
                return socket.waitForBytesWritten(1000)
    except (QtCore.QObject.QObjectError, ConnectionError):
        pass
    return False

def setup_local_server():
    QLocalServer.removeServer(APP_SERVER_NAME)
    try:
        server = QLocalServer()
        return server if server.listen(APP_SERVER_NAME) else None
    except Exception:
        return None

def handle_application_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    app_instance = QtWidgets.QApplication.instance()
    
    if not app_instance:
        return
        
    try:
        user_error_msg = f"{exc_type.__name__}: {exc_value}"
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setWindowTitle("应用程序错误")
        msg.setText("发生未预期的错误。应用程序可能需要关闭。")
        msg.setInformativeText(user_error_msg)
        msg.setDetailedText(error_message)
        msg.exec()
    except Exception:
        pass

def handle_socket_data(socket, window_ref):
    try:
        if socket.bytesAvailable() > 0 and socket.readAll().data() == BRING_TO_FRONT_COMMAND:
            window = window_ref()
            if window:
                window.activateWindow()
                window.raise_()
                window.showNormal()
    finally:
        socket.deleteLater()

def main():
    sys.excepthook = handle_application_exception
    local_server = None
    shared_memory = None
    
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("LeafView")
        app.setApplicationVersion("1.3")
        
        shared_memory = QtCore.QSharedMemory(SHARED_MEMORY_KEY)
        if shared_memory.attach():
            return 0 if bring_existing_to_front() else 1
        
        if not shared_memory.create(1):
            QtWidgets.QMessageBox.critical(None, "启动错误", "初始化应用程序失败。可能已有实例在运行。")
            return 1
        
        local_server = setup_local_server()
        window = MainWindow()
        window.move(300, 100)
        window.show()
        
        if local_server:
            def handle_connection():
                socket = local_server.nextPendingConnection()
                if socket:
                    socket.readyRead.connect(lambda s=socket: handle_socket_data(s, lambda: window))
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
        try:
            if local_server:
                local_server.close()
            if shared_memory and shared_memory.isAttached():
                shared_memory.detach()
        except Exception:
            pass


if __name__ == '__main__':
    sys.exit(main())
