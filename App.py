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
    """Try to bring existing instance to front with better error handling"""
    try:
        with closing(QLocalSocket()) as socket:
            print(f"Attempting to connect to existing server: {APP_SERVER_NAME}")
            socket.connectToServer(APP_SERVER_NAME)
            if socket.waitForConnected(500):
                print("Connected to existing server, sending bring to front command")
                socket.write(BRING_TO_FRONT_COMMAND)
                if socket.waitForBytesWritten(1000):
                    print("Command sent successfully")
                    return True
                else:
                    print("Failed to write bytes to socket")
            else:
                print(f"Failed to connect to server: {socket.errorString()}")
    except Exception as e:
        print(f"Error in bring_existing_to_front: {str(e)}")
    return False


def setup_local_server():
    """Setup local server with better error handling"""
    try:
        server = QLocalServer()
        print(f"Setting up local server: {APP_SERVER_NAME}")
        
        # Remove server if it already exists (cleanup from previous run)
        QLocalServer.removeServer(APP_SERVER_NAME)
        
        if server.listen(APP_SERVER_NAME):
            print(f"Local server started successfully on {APP_SERVER_NAME}")
            return server
        else:
            print(f"Failed to start local server: {server.errorString()}")
            return None
    except Exception as e:
        print(f"Exception when setting up local server: {str(e)}")
        return None


def handle_application_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    # Log the exception
    error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Unhandled exception: {error_message}")
    
    # Try to show error to user if possible
    try:
        if QtWidgets.QApplication.instance():
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setWindowTitle("Application Error")
            msg.setText("An unexpected error occurred. The application will close.")
            msg.setDetailedText(error_message)
            msg.exec()
    except:
        pass


def main():
    """Main application entry point with improved error handling"""
    shared_memory = None
    local_server = None
    window = None
    
    try:
        # Set global exception handler
        sys.excepthook = handle_application_exception
        
        # Create application instance
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("LeafView")
        app.setApplicationVersion("1.3")
        
        # Try to detect existing instance
        try:
            shared_memory = QtCore.QSharedMemory(SHARED_MEMORY_KEY)
            if shared_memory.attach():
                if bring_existing_to_front():
                    print("Another instance already running, bringing it to front.")
                    sys.exit(0)
                else:
                    print("Failed to bring existing instance to front.")
                    sys.exit(1)
            
            if not shared_memory.create(1):
                QtWidgets.QMessageBox.critical(None, "启动错误", 
                    "初始化应用程序失败。可能已有实例在运行。")
                sys.exit(1)
        except Exception as e:
            print(f"Error in single instance check: {str(e)}")
            # Continue anyway
            pass
        
        # Setup local server for inter-process communication
        local_server = setup_local_server()
        if not local_server:
            print("Warning: Failed to setup local server for IPC")
        
        def handle_new_connection():
            try:
                socket = local_server.nextPendingConnection()
                if socket:
                    socket.readyRead.connect(lambda: handle_socket_data(socket))
            except Exception as e:
                print(f"Error handling new connection: {str(e)}")
        
        def handle_socket_data(socket):
            try:
                data = socket.readAll().data()
                if data == BRING_TO_FRONT_COMMAND and window:
                    window.activateWindow()
                    window.raise_()
                    window.showNormal()
                    print("Window brought to front via IPC")
            except Exception as e:
                print(f"Error handling socket data: {str(e)}")
            finally:
                try:
                    socket.deleteLater()
                except Exception as e:
                    print(f"Error cleaning up socket: {str(e)}")
        
        if local_server:
            local_server.newConnection.connect(handle_new_connection)
        
        # Create and show main window
        print("Creating main window...")
        window = MainWindow()
        window.move(300, 100)
        window.show()
        print("Main window created and shown")
        
        # Show warning message
        try:
            window.log("WARNING", "文件整理、重命名和属性写入等操作一旦执行无法恢复，操作前请务必备份好原数据。")
        except Exception as e:
            print(f"Error showing warning message: {str(e)}")
        
        # Start event loop
        exit_code = app.exec()
        
        return exit_code
        
    except Exception as e:
        error_msg = f"应用程序启动失败: {str(e)}"
        print(f"Fatal error: {error_msg}")
        try:
            print(error_msg)
            QtWidgets.QMessageBox.critical(None, "致命错误", error_msg)
        except:
            print("Failed to show error message dialog")
        return 1
    finally:
        # Cleanup resources
        print("Cleaning up resources...")
        
        # Cleanup socket server
        if local_server:
            try:
                local_server.close()
            except Exception as e:
                print(f"Error closing local server: {str(e)}")
        
        # Cleanup shared memory
        if shared_memory and shared_memory.isAttached():
            try:
                shared_memory.detach()
                print("Shared memory detached")
            except Exception as e:
                print(f"Error detaching shared memory: {str(e)}")
        
        print("Application shutdown complete")


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
