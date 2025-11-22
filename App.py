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
    """尝试与现有实例通信并将其置于前台"""
    try:
        with closing(QLocalSocket()) as socket:
            if socket.connectToServer(APP_SERVER_NAME):
                if socket.waitForConnected(500):
                    socket.write(BRING_TO_FRONT_COMMAND)
                    return socket.waitForBytesWritten(1000)
    except (QtCore.QObject.QObjectError, ConnectionError):
        pass
    return False

def setup_local_server():
    """设置本地服务器以支持单实例功能"""
    QLocalServer.removeServer(APP_SERVER_NAME)  # 确保没有旧实例
    try:
        server = QLocalServer()
        return server if server.listen(APP_SERVER_NAME) else None
    except Exception:
        return None

def handle_application_exception(exc_type, exc_value, exc_traceback):
    """自定义异常处理器，显示友好的错误信息"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
        
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    app_instance = QtWidgets.QApplication.instance()
    
    if not app_instance:
        return
        
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
        pass  # 忽略消息框显示错误

def handle_new_connection(server, window_ref):
    """处理新的服务器连接"""
    socket = server.nextPendingConnection()
    if socket:
        socket.readyRead.connect(lambda: handle_socket_data(socket, window_ref))

def handle_socket_data(socket, window_ref):
    """处理来自套接字的数据"""
    try:
        if socket.bytesAvailable() > 0:
            data = socket.readAll().data()
            window = window_ref()
            if data == BRING_TO_FRONT_COMMAND and window:
                window.activateWindow()
                window.raise_()
                window.showNormal()
    finally:
        # 确保即使发生错误也会清理套接字
        if socket:
            socket.deleteLater()

def main():
    """应用程序主函数"""
    sys.excepthook = handle_application_exception
    app = None
    shared_memory = None
    local_server = None
    
    try:
        # 初始化应用程序
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("LeafView")
        app.setApplicationVersion("1.3")
        
        # 单实例检查
        shared_memory = QtCore.QSharedMemory(SHARED_MEMORY_KEY)
        if shared_memory.attach():
            # 尝试激活现有实例
            if bring_existing_to_front():
                return 0
            return 1
        
        # 创建共享内存
        if not shared_memory.create(1):
            QtWidgets.QMessageBox.critical(None, "启动错误", "初始化应用程序失败。可能已有实例在运行。")
            return 1
        
        # 设置本地服务器
        local_server = setup_local_server()
        
        # 创建并显示主窗口
        window = MainWindow()
        window.move(300, 100)
        window.show()
        
        # 连接服务器信号
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
        # 资源清理
        if local_server:
            try:
                local_server.close()
            except Exception:
                pass
        if shared_memory and shared_memory.isAttached():
            try:
                shared_memory.detach()
            except Exception:
                pass


if __name__ == '__main__':
    sys.exit(main())
