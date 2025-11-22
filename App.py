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
            socket.connectToServer(APP_SERVER_NAME)
            if socket.waitForConnected(500):
                socket.write(BRING_TO_FRONT_COMMAND)
                if socket.waitForBytesWritten(1000):
                    return True
    except Exception:
        pass
    return False

def setup_local_server():
    try:
        server = QLocalServer()
        QLocalServer.removeServer(APP_SERVER_NAME)
        return server if server.listen(APP_SERVER_NAME) else None
    except Exception:
        return None

def handle_application_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    app_instance = QtWidgets.QApplication.instance()
    if app_instance:
        try:
            user_error_msg = f"{exc_type.__name__}: {str(exc_value)}"
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setWindowTitle("应用程序错误")
            msg.setText("发生未预期的错误。应用程序可能需要关闭。")
            msg.setInformativeText(user_error_msg)
            msg.setDetailedText(error_message)
            msg.exec()
        except Exception:
            pass

def handle_new_connection(server, window_ref):
    try:
        socket = server.nextPendingConnection()
        if socket:
            socket.readyRead.connect(lambda: handle_socket_data(socket, window_ref))
    except Exception:
        pass

def handle_socket_data(socket, window_ref):
    try:
        data = socket.readAll().data()
        window = window_ref()
        if data == BRING_TO_FRONT_COMMAND and window:
            window.activateWindow()
            window.raise_()
            window.showNormal()
    except Exception:
        pass
    finally:
        try:
            socket.deleteLater()
        except Exception:
            pass

def main():
    sys.excepthook = handle_application_exception
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("LeafView")
        app.setApplicationVersion("1.3")
        
        shared_memory = QtCore.QSharedMemory(SHARED_MEMORY_KEY)
        if shared_memory.attach():
            if bring_existing_to_front():
                sys.exit(0)
            sys.exit(1)
        
        if not shared_memory.create(1):
            QtWidgets.QMessageBox.critical(None, "启动错误", "初始化应用程序失败。可能已有实例在运行。")
            sys.exit(1)
        
        local_server = setup_local_server()
        window = MainWindow()
        window.move(300, 100)
        window.show()
        
        if local_server:
            local_server.newConnection.connect(lambda: handle_new_connection(local_server, lambda: window))
        
        return app.exec()
    except Exception as e:
        error_msg = f"应用程序启动失败: {str(e)}"
        try:
            QtWidgets.QMessageBox.critical(None, "致命错误", error_msg)
        except Exception:
            pass
        return 1
    finally:
        if 'local_server' in locals():
            try:
                local_server.close()
            except Exception:
                pass
        if 'shared_memory' in locals() and shared_memory.isAttached():
            try:
                shared_memory.detach()
            except Exception:
                pass


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
