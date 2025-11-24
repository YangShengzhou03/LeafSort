from PyQt6 import QtWidgets, QtCore
from PyQt6.QtNetwork import QLocalSocket, QLocalServer
from contextlib import closing
from main_window import MainWindow
import sys
import traceback
import logging

# 配置基础日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

APP_SERVER_NAME = "LeafView_Server"
BRING_TO_FRONT_COMMAND = b'bringToFront'

def handle_exception(exc_type, exc_value, exc_traceback):
    """处理未捕获的异常"""
    if issubclass(exc_type, KeyboardInterrupt):
        return sys.__excepthook__(exc_type, exc_value, exc_traceback)
    
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    logger.error(f"未捕获的异常: {exc_type.__name__}: {exc_value}")
    logger.debug(f"详细错误信息:\n{error_message}")
    
    # 只有在应用程序已初始化时才显示错误对话框
    app = QtWidgets.QApplication.instance()
    if app:
        try:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setWindowTitle("应用程序错误")
            msg.setText("发生意外错误，应用程序可能需要关闭。")
            msg.setInformativeText(f"{exc_type.__name__}: {exc_value}")
            msg.setDetailedText(error_message)
            msg.exec()
        except Exception:
            # 避免在显示错误对话框时再次发生异常
            pass

def main():
    sys.excepthook = handle_exception
    
    # 检查是否已有实例运行
    with closing(QLocalSocket()) as socket:
        try:
            if socket.connectToServer(APP_SERVER_NAME) and socket.waitForConnected(500):
                socket.write(BRING_TO_FRONT_COMMAND)
                socket.waitForBytesWritten(1000)
                logger.info("发现已有实例运行，将其置于前台")
                return 0
        except (QtCore.QObject.QObjectError, ConnectionError):
            # 没有找到已有实例，继续启动新实例
            pass
    
    app = QtWidgets.QApplication(sys.argv)
    app.setApplicationName("LeafView")
    app.setApplicationVersion("1.3")
    
    # 移除可能存在的旧服务器实例并创建新的本地服务器
    QLocalServer.removeServer(APP_SERVER_NAME)
    local_server = None
    try:
        local_server = QLocalServer()
        local_server.listen(APP_SERVER_NAME)
        logger.info("本地服务器启动成功")
    except Exception as e:
        logger.error(f"创建本地服务器失败: {e}")
    
    try:
        window = MainWindow()
        window.move(300, 100)
        window.show()
        
        if local_server:
            def handle_socket_data(socket):
                """处理socket数据，响应前台显示请求"""
                if socket.bytesAvailable() > 0 and socket.readAll().data() == BRING_TO_FRONT_COMMAND:
                    logger.debug("收到前台显示请求")
                    window.activateWindow()
                    window.raise_()
                    window.showNormal()
                socket.deleteLater()
            
            def handle_connection():
                """处理新的socket连接"""
                socket = local_server.nextPendingConnection()
                if socket:
                    socket.readyRead.connect(lambda: handle_socket_data(socket))
            
            local_server.newConnection.connect(handle_connection)
        
        return app.exec()
        
    except Exception as e:
        logger.error(f"应用程序启动失败: {e}")
    try:
        QtWidgets.QMessageBox.critical(None, "致命错误", f"应用程序启动失败: {str(e)}")
    except Exception:
        pass
        return 1
    finally:
        if local_server:
            local_server.close()

if __name__ == '__main__':
    sys.exit(main())