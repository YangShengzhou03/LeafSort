import os

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from Ui_MainWindow import Ui_MainWindow
from update_dialog import check_update
from common import get_resource_path, author


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 初始化空状态管理
        self.empty_widgets = {}
        
        # 初始化窗口
        self._init_window()
        
        # 设置页面
        self._setup_pages()
        
        # 设置快捷键
        self._setup_keyboard_shortcuts()
        
        # 设置拖拽处理
        self._setup_drag_handlers()
        
        # 检查更新
        check_update()
        
        print("MainWindow initialized successfully")
        


    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        # 连接按钮信号与槽函数
        self._connect_buttons()
    


    def _setup_pages(self):
        """设置各个功能页面"""
        try:
            print("[INFO] 开始初始化功能页面")
            
            # 导入必要的模块
            from add_folder import FolderPage
            from smart_arrange import SmartArrangePage
            from remove_duplication import RemoveDuplicationPage
            from write_exif import WriteExifPage
            
            # 尝试导入TextRecognition模块，如果失败则记录错误但继续运行
            try:
                from text_recognition import TextRecognitionPage
                text_recognition_available = True
            except ImportError:
                print("[WARNING] text_recognition.py文件不存在，TextRecognition功能不可用")
                text_recognition_available = False
            
            # 创建功能页面实例
            self.folder_page = FolderPage(parent=self)
            print("[INFO] FolderPage实例创建成功")
            
            self.smart_arrange_page = SmartArrangePage(parent=self)
            print("[INFO] SmartArrangePage实例创建成功")
            
            self.remove_duplication_page = RemoveDuplicationPage(parent=self)
            print("[INFO] RemoveDuplicationPage实例创建成功")
            
            self.write_exif_page = WriteExifPage(parent=self)
            print("[INFO] WriteExifPage实例创建成功")
            
            # 如果TextRecognition模块可用，则创建实例
            if text_recognition_available:
                self.text_recognition_page = TextRecognitionPage(parent=self)
                print("[INFO] TextRecognitionPage实例创建成功")
            else:
                self.text_recognition_page = None
            
            # 将页面添加到stackedWidget
            if hasattr(self, 'stackedWidget'):
                self.stackedWidget.addWidget(self.folder_page)
                self.stackedWidget.addWidget(self.smart_arrange_page)
                self.stackedWidget.addWidget(self.remove_duplication_page)
                self.stackedWidget.addWidget(self.write_exif_page)
                
                if text_recognition_available:
                    self.stackedWidget.addWidget(self.text_recognition_page)
                
                print("[INFO] 所有可用页面已添加到stackedWidget")
            else:
                print("[ERROR] stackedWidget不存在，无法添加页面")
                return
            
            # 初始化各个页面
            self.folder_page.init_page()
            print("[INFO] FolderPage初始化完成")
            
            self.smart_arrange_page.init_page()
            print("[INFO] SmartArrangePage初始化完成")
            
            self.remove_duplication_page.init_page()
            print("[INFO] RemoveDuplicationPage初始化完成")
            
            self.write_exif_page.init_page()
            print("[INFO] WriteExifPage初始化完成")
            
            # 如果TextRecognition模块可用，则初始化页面
            if text_recognition_available:
                self.text_recognition_page.init_page()
                print("[INFO] TextRecognitionPage初始化完成")
            else:
                print("[WARNING] TextRecognition页面不可用")
            
            # 初始显示第一个页面
            self._show_page(0)
            print("[INFO] 初始页面已设置为FolderPage")
            
            print("[INFO] 功能页面初始化完成")
            if not text_recognition_available:
                print("[INFO] 注意: 某些功能页面可能无法使用")
            
        except ImportError as e:
            print(f"[ERROR] 导入模块失败: {str(e)}")
            print("[ERROR] 某些功能页面可能无法使用")
            print(f"Import error setting up pages: {str(e)}")
        except Exception as e:
            print(f"[ERROR] 初始化功能页面时出错: {str(e)}")
            print("[ERROR] 请检查程序配置和依赖")
            print(f"Error setting up pages: {str(e)}")
    
    def _setup_navigation(self):
        """设置导航菜单（仅保留信号连接逻辑）"""
        try:
            # 检查是否有listWidget_navigationMenu
            if not hasattr(self, 'listWidget_navigationMenu'):
                print("[WARNING] listWidget_navigationMenu not found in UI")
                return
            
        except Exception as e:
            print(f"[ERROR] Error setting up navigation: {str(e)}")
    
    def _connect_buttons(self):
        """连接按钮信号与槽 - 保留核心功能"""
        try:
            # 窗口控制按钮（保留必要的功能连接）
            if hasattr(self, 'btnClose'):
                self.btnClose.clicked.connect(self.close)
            if hasattr(self, 'btnMaximize'):
                self.btnMaximize.clicked.connect(self._toggle_maximize)
            if hasattr(self, 'btnMinimize'):
                self.btnMinimize.clicked.connect(self.showMinimized)
            
            if hasattr(self, 'btnGithub'):
                self.btnGithub.clicked.connect(self._feedback)
            if hasattr(self, 'btnSettings'):
                self.btnSettings.clicked.connect(author)
                
            # 连接文件夹选择按钮
            if hasattr(self, 'btnBrowseSource'):
                self.btnBrowseSource.clicked.connect(self._select_source_folder)
            if hasattr(self, 'btnBrowseTarget'):
                self.btnBrowseTarget.clicked.connect(self._select_target_folder)
                
            # 快速工具栏按钮连接
            if hasattr(self, 'pushButton_addFolder'):
                self.pushButton_addFolder.clicked.connect(self._on_add_folder_clicked)
            if hasattr(self, 'pushButton_smartArrange'):
                self.pushButton_smartArrange.clicked.connect(lambda: self._show_page(1))
            if hasattr(self, 'pushButton_removeDuplicate'):
                self.pushButton_removeDuplicate.clicked.connect(lambda: self._show_page(2))
            if hasattr(self, 'pushButton_writeExif'):
                self.pushButton_writeExif.clicked.connect(lambda: self._show_page(3))
            if hasattr(self, 'pushButton_textRecognition'):
                self.pushButton_textRecognition.clicked.connect(lambda: self._show_page(4))
            
            print("[INFO] Button connections setup completed")
        except Exception as e:
            print(f"[WARNING] Failed to connect some buttons: {str(e)}")
            
    def _on_add_folder_clicked(self):
        """添加文件夹按钮点击处理"""
        try:
            # 切换到文件夹页面
            self._show_page(0)
            # 调用文件夹页面的添加文件夹方法
            if hasattr(self, 'folder_page') and hasattr(self.folder_page, '_show_add_folder_dialog'):
                self.folder_page._show_add_folder_dialog()
        except Exception as e:
            print(f"[ERROR] 处理添加文件夹按钮点击时出错: {str(e)}")
            print(f"Error handling add folder click: {str(e)}")

    def _setup_drag_handlers(self):
        """设置窗口拖动处理和文件拖放支持"""
        # 初始化拖拽状态变量
        self._is_dragging = False
        self._drag_start_pos = QtCore.QPoint()
        
        # 启用拖放支持
        self.setAcceptDrops(True)
        
        # 为中央内容区域设置拖放支持
        if hasattr(self, 'centralwidget'):
            self.centralwidget.setAcceptDrops(True)
        
        self.log("INFO", "Drag handlers setup completed")
        
    def dragEnterEvent(self, event):
        """处理拖放进入事件"""
        if event.mimeData().hasUrls():
            import os
            # 检查是否包含文件夹或媒体文件
            for url in event.mimeData().urls():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    event.acceptProposedAction()
                    return
                # 检查是否为支持的媒体文件
                try:
                    from common import detect_media_type
                    result = detect_media_type(path)
                    if result['valid']:
                        event.acceptProposedAction()
                        return
                except Exception as e:
                    self.log("WARNING", f"Error detecting media type: {str(e)}")
        event.ignore()
    
    def dropEvent(self, event):
        """处理拖放释放事件"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            paths = [url.toLocalFile() for url in urls]
            
            # 处理拖放的内容
            self._handle_dropped_items(paths)
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _handle_dropped_items(self, paths):
        """处理拖放的文件或文件夹"""
        folders = []
        files = []
        
        # 分离文件夹和文件
        for path in paths:
            if os.path.isdir(path):
                folders.append(path)
            else:
                files.append(path)
        
        # 显示拖放信息
        message = f"检测到拖放: {len(folders)} 个文件夹, {len(files)} 个文件"
        self.log("INFO", message)
        
        # 默认切换到文件夹页面并添加文件夹
        self._show_page(0)
        
        # 如果有文件夹，添加到文件夹页面
        if folders and hasattr(self, 'folder_page') and hasattr(self.folder_page, '_add_folders'):
            try:
                self.folder_page._add_folders(folders)
                self.log("INFO", "已将拖放的文件夹添加到当前项目")
            except Exception as e:
                self.log("ERROR", f"添加拖放的文件夹时出错: {str(e)}")
        
        # 如果只有文件，可以根据文件类型跳转到相应页面处理
        elif files and not folders:
            # 这里可以根据文件类型实现更多逻辑
            self.log("INFO", "检测到文件拖放，请在相应功能页面中使用")
    
    def _on_mouse_press(self, event):
        """鼠标按下事件处理 - 移除窗口拖动UI相关代码"""
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()
    
    def _on_mouse_move(self, event):
        """鼠标移动事件处理 - 移除窗口拖动UI相关代码"""
        self._is_dragging = False  # 禁用拖动功能
        event.ignore()
    
    def _on_mouse_release(self, event):
        """鼠标释放事件处理 - 移除窗口拖动UI相关代码"""
        self._is_dragging = False
        event.accept()
    
    def _create_empty_widget(self, layout):
        """空状态管理 - 保留接口但简化实现"""
        # 仅创建基本widget用于状态管理，不创建具体UI控件
        empty_widget = QtWidgets.QWidget()
        layout.addWidget(empty_widget)
        empty_widget.hide()
        return empty_widget
    
    def _update_empty_state(self, has_media):
        for widget in self.empty_widgets.values():
            if has_media:
                widget.hide()
            else:
                widget.show()
    
    def _create_quick_toolbar(self):
        """快速工具栏 - 移除UI创建代码，保留功能入口"""
        self.log("INFO", "Quick toolbar functionality skipped (UI controls not created)")
    
    def _setup_keyboard_shortcuts(self):
        """设置全局快捷键"""
        try:
            # 创建快捷键
            self.shortcut_add_folder = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), self)
            self.shortcut_add_folder.activated.connect(self._on_add_folder_clicked)
            
            self.shortcut_batch_add = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+A"), self)
            self.shortcut_batch_add.activated.connect(self._on_add_folder_clicked)
            
            self.shortcut_smart_arrange = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
            self.shortcut_smart_arrange.activated.connect(lambda: self._show_page(1))
            
            self.shortcut_remove_dup = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+D"), self)
            self.shortcut_remove_dup.activated.connect(lambda: self._show_page(2))
            
            self.shortcut_exif = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+E"), self)
            self.shortcut_exif.activated.connect(lambda: self._show_page(3))
            
            self.shortcut_refresh = QtGui.QShortcut(QtGui.QKeySequence("F5"), self)
            self.shortcut_refresh.activated.connect(self._refresh_current_page)
            
            self.shortcut_help = QtGui.QShortcut(QtGui.QKeySequence("F1"), self)
            self.shortcut_help.activated.connect(self._show_help)
            
            # 新增更多快捷键
            self.shortcut_next_page = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Tab"), self)
            self.shortcut_next_page.activated.connect(self._next_page)
            
            self.shortcut_prev_page = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Tab"), self)
            self.shortcut_prev_page.activated.connect(self._prev_page)
            
            self.shortcut_quit = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self)
            self.shortcut_quit.activated.connect(self.close)
            
            self.shortcut_minimize = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+M"), self)
            self.shortcut_minimize.activated.connect(self.showMinimized)
            
            print("Keyboard shortcuts setup completed")
        except Exception as e:
            self.log("ERROR", f"设置快捷键时出错: {str(e)}")
            print(f"Error setting up keyboard shortcuts: {str(e)}")
            import traceback
            traceback.print_exc()

    def _next_page(self):
        """切换到下一页"""
        current_index = self.stackedWidget.currentIndex()
        next_index = (current_index + 1) % self.stackedWidget.count()
        self._show_page(next_index)
        
    def _prev_page(self):
        """切换到上一页"""
        current_index = self.stackedWidget.currentIndex()
        prev_index = (current_index - 1) % self.stackedWidget.count()
        self._show_page(prev_index)
    
    def _show_page(self, page_index):
        """显示指定页面"""
        try:
            # 检查stackedWidget是否存在
            if hasattr(self, 'stackedWidget'):
                stacked_widget = self.stackedWidget
            elif hasattr(self.ui, 'stackedWidget'):
                stacked_widget = self.ui.stackedWidget
            else:
                self.log("ERROR", "stackedWidget不存在")
                return False
            
            # 验证索引是否有效
            if 0 <= page_index < stacked_widget.count():
                stacked_widget.setCurrentIndex(page_index)
                # 更新导航菜单选中状态
                if hasattr(self, 'listNavigationMenu'):  # 使用UI中实际的导航菜单名称
                    self.listNavigationMenu.setCurrentRow(page_index)
                # 记录页面切换
                page_name = stacked_widget.currentWidget().__class__.__name__
                self.log("INFO", f"切换到页面: {page_name}")
                # 刷新当前页面
                self._refresh_current_page()
                return True
            else:
                self.log("ERROR", f"无效的页面索引: {page_index}，有效范围: 0-{stacked_widget.count()-1}")
                # 回退到第一个页面
                if stacked_widget.count() > 0:
                    stacked_widget.setCurrentIndex(0)
                    self.log("INFO", "已回退到第一个页面")
                    # 刷新当前页面
                    self._refresh_current_page()
                    return True
        except Exception as e:
            self.log("ERROR", f"切换页面时出错: {str(e)}")
            print(f"Error showing page: {str(e)}")
        return False
    
    def _refresh_current_page(self):
        """刷新当前页面"""
        try:
            # 获取当前活动页面
            current_widget = None
            if hasattr(self, 'stackedWidget'):
                current_widget = self.stackedWidget.currentWidget()
            elif hasattr(self.ui, 'stackedWidget'):
                current_widget = self.ui.stackedWidget.currentWidget()
            
            if current_widget is not None:
                # 尝试调用页面的refresh方法
                if hasattr(current_widget, 'refresh'):
                    current_widget.refresh()
                    page_name = current_widget.__class__.__name__
                    self.log("INFO", f"已刷新页面: {page_name}")
                elif hasattr(current_widget, 'init_page'):
                    # 作为备选方案，重新初始化页面
                    current_widget.init_page()
                    page_name = current_widget.__class__.__name__
                    self.log("INFO", f"已重新初始化页面: {page_name}")
            else:
                self.log("WARNING", "没有当前活动页面可刷新")
        except Exception as e:
            self.log("ERROR", f"刷新页面时出错: {str(e)}")
            
        # 获取当前索引用于其他逻辑
        current_index = 0
        if hasattr(self, 'stackedWidget_mainContent'):
            current_index = self.stackedWidget_mainContent.currentIndex()
        
        self.log("INFO", "正在刷新当前页面...")
        
        # 根据不同页面执行相应刷新操作
        try:
            if current_index == 0 and hasattr(self, 'folder_page'):
                # 刷新文件夹页面
                if hasattr(self.folder_page, '_refresh_all_folders'):
                    self.folder_page._refresh_all_folders()
                    self.log("INFO", "文件夹页面已刷新")
            elif current_index == 1 and hasattr(self, 'smart_arrange_page'):
                # 刷新智能整理页面
                if hasattr(self.smart_arrange_page, '_refresh_ui'):
                    self.smart_arrange_page._refresh_ui()
                    self.log("INFO", "智能整理页面已刷新")
            elif current_index == 2 and hasattr(self, 'remove_dup_page'):
                # 刷新去重页面
                if hasattr(self.remove_dup_page, '_refresh_ui'):
                    self.remove_dup_page._refresh_ui()
                    self.log("INFO", "去重页面已刷新")
            elif current_index == 3 and hasattr(self, 'write_exif_page'):
                # 刷新EXIF编辑页面
                if hasattr(self.write_exif_page, '_refresh_ui'):
                    self.write_exif_page._refresh_ui()
                    self.log("INFO", "EXIF编辑页面已刷新")
            elif current_index == 4 and hasattr(self, 'text_recog_page'):
                # 刷新文字识别页面
                if hasattr(self.text_recog_page, '_refresh_ui'):
                    self.text_recog_page._refresh_ui()
                    self.log("INFO", "文字识别页面已刷新")
        except Exception as e:
            self.log("ERROR", f"刷新页面时出错: {str(e)}")
            print(f"Error refreshing page: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _show_help(self):
        """显示帮助信息 - 保留核心功能"""
        self.log("INFO", "Showing help information")
        # 保留功能但简化实现
        QtWidgets.QMessageBox.information(self, "帮助", "枫叶相册 - 核心功能正常运行")

    def log(self, level, message):
        """日志记录函数 - 核心逻辑保留"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # 将日志写入文件
        try:
            import os
            log_dir = os.path.join(os.path.expanduser("~"), ".leafview", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "app.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_message + "\n")
        except Exception as log_error:
            print(f"Failed to write log to file: {str(log_error)}")
            
        # 通知用户重要信息
        if level == "ERROR":
            self._show_user_notification("错误", message, "error")
        elif level == "WARNING":
            self._show_user_notification("警告", message, "warning")
        elif level == "INFO":
            if any(keyword in message for keyword in ["完成", "成功", "开始", "停止", "中断"]):
                self._show_user_notification("提示", message, "info")
            
    def _toggle_maximize(self):
        """切换窗口最大化状态 - 简化实现"""
        try:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        except Exception as e:
            self.log("ERROR", f"切换窗口最大化状态时出错: {str(e)}")
        

    def _show_user_notification(self, title, message, level):
        try:
            if level == "error":
                QtWidgets.QMessageBox.critical(self, title, message)
            elif level == "warning":
                QtWidgets.QMessageBox.warning(self, title, message)
            elif level == "info":
                QtWidgets.QMessageBox.information(self, title, message)
                
        except Exception as e:
            print(f"[{level.upper()}] {title}: {message}")
            print(f"Failed to show notification: {str(e)}")

    def _feedback(self):
        QDesktopServices.openUrl(QUrl('https://qun.qq.com/universal-share/share?ac=1&authKey=wjyQkU9iG7wc'
                                      '%2BsIEOWFE6cA0ayLLBdYwpMsKYveyufXSOE5FBe7bb9xxvuNYVsEn&busi_data'
                                      '=eyJncm91cENvZGUiOiIxMDIxNDcxODEzIiwidG9rZW4iOiJDaFYxYVpySU9FUVJr'
                                      'RzkwdUZ2QlFVUTQzZzV2VS83TE9mY0NNREluaUZCR05YcnNjWmpKU2V5Q2FYTllFVlJ'
                                      'MIiwidWluIjoiMzU1ODQ0Njc5In0&data=M7fVC3YlI68T2S2VpmsR20t9s_xJj6HNpF'
                                      '0GGk2ImSQ9iCE8fZomQgrn_ADRZF0Ee4OSY0x6k2tI5P47NlkWug&svctype=4&tempid'
                                      '=h5_group_info'))

    def _select_source_folder(self):
        """选择源文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "选择要处理的文件夹",
            "",
            QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path and hasattr(self, 'inputSourceFolder'):
            self.inputSourceFolder.setText(folder_path)

    def _select_target_folder(self):
        """选择目标文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "选择目标文件夹",
            "",
            QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path and hasattr(self, 'inputTargetFolder'):
            self.inputTargetFolder.setText(folder_path)
