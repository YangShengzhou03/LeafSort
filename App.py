from PyQt6 import QtWidgets, QtCore
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from contextlib import closing
from main_window import MainWindow
import sys
import traceback

APP_SERVER_NAME = "LeafView_Server"
BRING_TO_FRONT_COMMAND = b'bringToFront'

class ApplicationManager:
    """应用程序管理器，负责单例控制和进程间通信"""
    
    def __init__(self):
        self.app = None
        self.local_server = None
        self.shared_memory = None
        
    def setup_exception_handler(self):
        """设置全局异常处理器"""
        sys.excepthook = self._handle_exception
    
    def _handle_exception(self, exc_type, exc_value, exc_traceback):
        """处理应用程序异常"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        if self.app:
            try:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
                msg.setWindowTitle("应用程序错误")
                msg.setText("发生意外错误，应用程序可能需要关闭。")
                msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
                msg.setDetailedText(error_message)
                msg.exec()
            except Exception:
                pass
    
    def check_existing_instance(self):
        """检查是否已有实例运行"""
        try:
            with closing(QLocalSocket()) as socket:
                if socket.connectToServer(APP_SERVER_NAME) and socket.waitForConnected(500):
                    socket.write(BRING_TO_FRONT_COMMAND)
                    return socket.waitForBytesWritten(1000)
        except (QtCore.QObject.QObjectError, ConnectionError):
            pass
        return False
    
    def setup_local_server(self):
        """设置本地服务器用于进程间通信"""
        QLocalServer.removeServer(APP_SERVER_NAME)
        try:
            server = QLocalServer()
            return server if server.listen(APP_SERVER_NAME) else None
        except Exception:
            return None
    
    def handle_socket_data(self, socket, window):
        """处理来自其他实例的Socket数据"""
        try:
            if socket.bytesAvailable() > 0 and socket.readAll().data() == BRING_TO_FRONT_COMMAND:
                if window:
                    window.activateWindow()
                    window.raise_()
                    window.showNormal()
        finally:
            socket.deleteLater()
    
    def cleanup(self):
        """清理资源"""
        if self.local_server:
            self.local_server.close()
        if self.shared_memory and self.shared_memory.isAttached():
            self.shared_memory.detach()
    
    def run(self):
        """运行应用程序"""
        self.setup_exception_handler()
        
        # 检查是否已有实例运行
        if self.check_existing_instance():
            return 0
        
        try:
            self.app = QtWidgets.QApplication(sys.argv)
            self.app.setApplicationName("LeafView")
            self.app.setApplicationVersion("1.3")
            
            # 设置本地服务器
            self.local_server = self.setup_local_server()
            
            # 创建主窗口
            window = MainWindow()
            window.move(300, 100)
            window.show()
            
            # 设置Socket连接处理
            if self.local_server:
                def handle_connection():
                    socket = self.local_server.nextPendingConnection()
                    if socket:
                        socket.readyRead.connect(lambda: self.handle_socket_data(socket, window))
                self.local_server.newConnection.connect(handle_connection)
            
            return self.app.exec()
            
        except Exception as e:
            error_msg = f"应用程序启动失败: {e}"
            try:
                QtWidgets.QMessageBox.critical(None, "致命错误", error_msg)
            except Exception:
                pass
            return 1
        finally:
            self.cleanup()

def main():
    """应用程序主入口点"""
    app_manager = ApplicationManager()
    return app_manager.run()

if __name__ == '__main__':
    sys.exit(main())