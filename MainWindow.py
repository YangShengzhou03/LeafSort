from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

from AddFolder import FolderPage
from SmartArrange import SmartArrange
from RemoveDuplication import Contrast
from WriteExif import WriteExif
from TextRecognition import TextRecognition
from Ui_MainWindow import Ui_MainWindow
from UpdateDialog import check_update
from common import get_resource_path, author


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
        # 初始化空状态管理
        self.empty_widgets = {}
        
        # 初始化UI组件
        self._init_window()
        
        # 设置页面
        self._setup_pages()
        
        # 设置导航
        self._setup_navigation()
        
        # 设置快捷键
        self._setup_keyboard_shortcuts()
        
        # 设置拖拽处理
        self._setup_drag_handlers()
        
        # 创建快速工具栏
        self._create_quick_toolbar()
        
        # 检查更新
        check_update()
        
        print("MainWindow initialized successfully")
        


    def _init_window(self):
        self.setWindowTitle("枫叶相册")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 设置窗口的渲染提示以提升整体抗锯齿效果
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_StyledBackground, True)
        
        self._connect_buttons()
        
        self.scrollAreaSidebar.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeading | 
            QtCore.Qt.AlignmentFlag.AlignLeft | 
            QtCore.Qt.AlignmentFlag.AlignTop
        )
    


    def _setup_pages(self):
        """初始化所有功能页面"""
        try:
            # 检查是否有stackedWidget_mainContent
            if not hasattr(self, 'stackedWidget_mainContent'):
                print("Warning: stackedWidget_mainContent not found in UI")
                return
            
            # 清除现有页面（如果有）
            while self.stackedWidget_mainContent.count() > 0:
                widget = self.stackedWidget_mainContent.widget(0)
                self.stackedWidget_mainContent.removeWidget(widget)
                widget.deleteLater()
            
            # 创建各个功能页面
            print("Creating application pages...")
            
            # 文件夹页面
            self.folder_page = FolderPage(self)
            self.stackedWidget_mainContent.addWidget(self.folder_page)
            
            # 智能整理页面
            self.smart_arrange_page = SmartArrange(self)
            self.stackedWidget_mainContent.addWidget(self.smart_arrange_page)
            
            # 去重对比页面
            self.remove_dup_page = Contrast(self)
            self.stackedWidget_mainContent.addWidget(self.remove_dup_page)
            
            # EXIF编辑页面
            self.write_exif_page = WriteExif(self)
            self.stackedWidget_mainContent.addWidget(self.write_exif_page)
            
            # 文字识别页面
            self.text_recog_page = TextRecognition(self)
            self.stackedWidget_mainContent.addWidget(self.text_recog_page)
            
            print(f"Created {self.stackedWidget_mainContent.count()} pages successfully")
            
        except Exception as e:
            print(f"Error setting up pages: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _setup_navigation(self):
        """设置导航菜单"""
        try:
            # 检查是否有listWidget_navigationMenu
            if not hasattr(self, 'listWidget_navigationMenu'):
                print("Warning: listWidget_navigationMenu not found in UI")
                return
            
            # 清除现有导航项
            self.listWidget_navigationMenu.clear()
            
            # 添加导航项
            nav_items = [
                ("文件夹管理", "resources/img/list/文件夹.svg"),
                ("智能整理", "resources/img/list/智能整理.svg"),
                ("去重对比", "resources/img/list/去重对比.svg"),
                ("EXIF编辑", "resources/img/list/EXIF编辑.svg"),
                ("文字识别", "resources/img/list/文字识别.svg")
            ]
            
            for i, (text, icon_path) in enumerate(nav_items):
                item = QtWidgets.QListWidgetItem(text)
                try:
                    icon = QtGui.QIcon(get_resource_path(icon_path))
                    item.setIcon(icon)
                except Exception as e:
                    print(f"Error loading icon for {text}: {str(e)}")
                
                # 设置样式
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignVCenter | QtCore.Qt.AlignmentFlag.AlignLeft)
                self.listWidget_navigationMenu.addItem(item)
            
            # 连接导航信号
            self.listWidget_navigationMenu.currentRowChanged.connect(self._show_page)
            
            # 默认选中第一个页面
            self.listWidget_navigationMenu.setCurrentRow(0)
            
        except Exception as e:
            print(f"Error setting up navigation: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _connect_buttons(self):
        """连接按钮信号与槽函数"""
        try:
            # 窗口控制按钮
            self.btnClose.clicked.connect(self.close)
            self.btnMaximize.clicked.connect(self._toggle_maximize)
            self.btnMinimize.clicked.connect(self.showMinimized)
            
            self.btnGithub.clicked.connect(self.feedback)
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
                
            print("Button connections setup completed")
        except Exception as e:
            self.log("ERROR", f"连接按钮时出错: {str(e)}")
            print(f"Error connecting buttons: {str(e)}")
            import traceback
            traceback.print_exc()
            
    def _on_add_folder_clicked(self):
        """添加文件夹按钮点击处理"""
        try:
            # 切换到文件夹页面
            self._show_page(0)
            # 调用文件夹页面的添加文件夹方法
            if hasattr(self, 'folder_page') and hasattr(self.folder_page, '_show_add_folder_dialog'):
                self.folder_page._show_add_folder_dialog()
        except Exception as e:
            self.log("ERROR", f"处理添加文件夹按钮点击时出错: {str(e)}")
            print(f"Error handling add folder click: {str(e)}")

    def _setup_drag_handlers(self):
        """设置窗口拖动处理和文件拖放支持"""
        # 设置窗口拖动
        self.frameAppHeaderBar.mousePressEvent = self._on_mouse_press
        self.frameAppHeaderBar.mouseMoveEvent = self._on_mouse_move
        self.frameAppHeaderBar.mouseReleaseEvent = self._on_mouse_release
        
        self._is_dragging = False
        self._drag_start_pos = QtCore.QPoint()
        
        # 启用拖放支持
        self.setAcceptDrops(True)
        
        # 为中央内容区域设置拖放支持
        if hasattr(self, 'centralwidget'):
            self.centralwidget.setAcceptDrops(True)
        
        print("Drag handlers setup completed")
        
    def dragEnterEvent(self, event):
        """处理拖放进入事件"""
        if event.mimeData().hasUrls():
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
                except:
                    pass
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
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._is_dragging = True
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        event.accept()
    
    def _on_mouse_move(self, event):
        if self._is_dragging and event.buttons() & QtCore.Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)
        event.accept()
    
    def _on_mouse_release(self, event):
        self._is_dragging = False
        event.accept()
    
    def _create_empty_widget(self, layout):
        empty_widget = QtWidgets.QWidget()
        empty_layout = QtWidgets.QVBoxLayout(empty_widget)
        empty_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        
        icon_label = QtWidgets.QLabel()
        icon = QtGui.QIcon(get_resource_path('resources/img/page_0/空状态.svg'))
        icon_label.setPixmap(icon.pixmap(128, 128))
        empty_layout.addWidget(icon_label, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        text_label = QtWidgets.QLabel("暂无媒体文件")
        text_label.setStyleSheet("font-size: 16px; color: #666666;")
        text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(text_label, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        desc_label = QtWidgets.QLabel("请点击上方按钮添加媒体文件夹")
        desc_label.setStyleSheet("font-size: 12px; color: #999999;")
        desc_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        empty_layout.addWidget(desc_label, 0, QtCore.Qt.AlignmentFlag.AlignCenter)
        
        empty_widget.hide()
        
        layout.addWidget(empty_widget)
        
        return empty_widget
    
    def _update_empty_state(self, has_media):
        for widget in self.empty_widgets.values():
            if has_media:
                widget.hide()
            else:
                widget.show()
    
    def _create_quick_toolbar(self):
        """创建快速操作工具栏 - 新增功能"""
        # 在左侧导航区域添加快速工具栏
        quick_toolbar = QtWidgets.QFrame(parent=self.sidebarFrame)
        quick_toolbar.setObjectName("quick_toolbar")
        quick_toolbar.setStyleSheet("""
            QFrame#quick_toolbar {
                background-color: rgba(255, 255, 255, 0.8);
                border-radius: 8px;
                margin: 8px 4px;
                padding: 4px;
            }
            
            QPushButton {
                background-color: #6c5ce7;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                margin: 2px;
                min-width: 80px;
            }
            
            QPushButton:hover {
                background-color: #5a4bc7;
            }
            
            QPushButton:pressed {
                background-color: #4a3ba7;
            }
        """)
        
        toolbar_layout = QtWidgets.QVBoxLayout(quick_toolbar)
        toolbar_layout.setContentsMargins(6, 6, 6, 6)
        toolbar_layout.setSpacing(4)
        
        # 添加快速操作按钮
        self.btn_quick_add = QtWidgets.QPushButton("📁 添加文件夹")
        self.btn_quick_add.clicked.connect(lambda: self._show_page(0))
        toolbar_layout.addWidget(self.btn_quick_add)
        
        self.btn_quick_batch = QtWidgets.QPushButton("📂 批量添加")
        self.btn_quick_batch.clicked.connect(lambda: self._show_page(0))
        toolbar_layout.addWidget(self.btn_quick_batch)
        
        toolbar_layout.addSpacing(8)
        
        self.btn_quick_smart = QtWidgets.QPushButton("🤖 智能整理")
        self.btn_quick_smart.clicked.connect(lambda: self._show_page(1))
        toolbar_layout.addWidget(self.btn_quick_smart)
        
        self.btn_quick_remove_dup = QtWidgets.QPushButton("🗑️ 去重")
        self.btn_quick_remove_dup.clicked.connect(lambda: self._show_page(2))
        toolbar_layout.addWidget(self.btn_quick_remove_dup)
        
        toolbar_layout.addSpacing(8)
        
        self.btn_quick_exif = QtWidgets.QPushButton("📝 编辑信息")
        self.btn_quick_exif.clicked.connect(lambda: self._show_page(3))
        toolbar_layout.addWidget(self.btn_quick_exif)
        
        # 添加到左侧布局（在logo下方，导航菜单上方）
        self.sidebarLayout.insertWidget(1, quick_toolbar)
    
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
        current_index = self.stackedWidget_mainContent.currentIndex()
        next_index = (current_index + 1) % self.stackedWidget_mainContent.count()
        self._show_page(next_index)
        
    def _prev_page(self):
        """切换到上一页"""
        current_index = self.stackedWidget_mainContent.currentIndex()
        prev_index = (current_index - 1) % self.stackedWidget_mainContent.count()
        self._show_page(prev_index)
    
    def _show_page(self, page_index):
        """显示指定页面"""
        try:
            if hasattr(self, 'stackedWidget_mainContent'):
                # 验证索引有效性
                if 0 <= page_index < self.stackedWidget_mainContent.count():
                    self.stackedWidget_mainContent.setCurrentIndex(page_index)
                    # 更新导航菜单选中状态
                    self.listWidget_navigationMenu.setCurrentRow(page_index)
                    self.log("INFO", f"切换到页面: {page_index}")
                    # 刷新当前页面
                    self._refresh_current_page()
                    return True
                else:
                    self.log("ERROR", f"无效的页面索引: {page_index}")
            else:
                self.log("ERROR", "stackedWidget_mainContent 不存在")
        except Exception as e:
            self.log("ERROR", f"切换页面时出错: {str(e)}")
            print(f"Error showing page: {str(e)}")
        return False
    
    def _refresh_current_page(self):
        """刷新当前页面"""
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
        """显示帮助信息 - 新增功能"""
        help_text = """
        <h3>枫叶相册 - 快捷键帮助</h3>
        <p><b>页面切换：</b></p>
        <ul>
        <li>Ctrl+A - 添加文件夹页面</li>
        <li>Ctrl+S - 智能整理页面</li>
        <li>Ctrl+D - 去重页面</li>
        <li>Ctrl+E - 编辑信息页面</li>
        </ul>
        <p><b>通用操作：</b></p>
        <ul>
        <li>F5 - 刷新当前页面</li>
        <li>F1 - 显示帮助</li>
        <li>拖拽文件夹 - 快速添加</li>
        </ul>
        <p><b>窗口控制：</b></p>
        <ul>
        <li>双击标题栏 - 最大化/还原</li>
        <li>拖拽标题栏 - 移动窗口</li>
        </ul>
        """
        
        QtWidgets.QMessageBox.information(self, "快捷键帮助", help_text)

    def _toggle_maximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def log(self, level, message):
        """记录日志"""
        try:
            # 使用QTime获取当前时间，保持原有行为
            current_time = QtCore.QTime.currentTime().toString("HH:mm:ss")
            log_message = f"[{current_time}] [{level}] {message}"
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
                # 如果写入日志文件失败，至少在控制台打印
                print(f"Failed to write log to file: {str(log_error)}")
            
            # 通知用户重要信息
            if level == "ERROR":
                self._show_user_notification("错误", message, "error")
            elif level == "WARNING":
                self._show_user_notification("警告", message, "warning")
            elif level == "INFO":
                if any(keyword in message for keyword in ["完成", "成功", "开始", "停止", "中断"]):
                    self._show_user_notification("提示", message, "info")
        except Exception as e:
            # 日志记录本身的错误不应影响程序运行
            print(f"Error in log function: {str(e)}")
            
    def _toggle_maximize(self):
        """切换窗口最大化状态"""
        try:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        except Exception as e:
            self.log("ERROR", f"切换窗口最大化状态时出错: {str(e)}")
            print(f"Error toggling maximize: {str(e)}")
        

    def _show_user_notification(self, title, message, level):
        try:
            from PyQt6.QtWidgets import QMessageBox
            
            if level == "error":
                QMessageBox.critical(self, title, message)
            elif level == "warning":
                QMessageBox.warning(self, title, message)
            elif level == "info":
                QMessageBox.information(self, title, message)
                
        except ImportError:
            print(f"[{level.upper()}] {title}: {message}")

    def feedback(self):
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
