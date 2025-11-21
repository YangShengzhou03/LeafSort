import os
import sys

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices

# 导入智能整理线程类
from smart_arrange_thread import SmartArrangeThread
# 导入文件去重相关类
from remove_duplication_thread import HashWorker, ContrastWorker
# 导入属性写入线程类
from write_exif_thread import WriteExifThread

from Ui_MainWindow import Ui_MainWindow
from update_dialog import check_update
from common import get_resource_path, author


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        
        # 设置全局异常处理
        sys.excepthook = self._handle_global_exception
        
        # 初始化空状态管理
        self.empty_widgets = {}
        
        # 初始化智能整理线程
        self.smart_arrange_thread = None
        # 初始化文件去重相关线程
        self.hash_worker = None
        self.contrast_worker = None
        self.image_hashes = {}
        # 初始化属性写入线程
        self.write_exif_thread = None
        
        # 页面相关初始化 - 添加页面缓存和状态管理
        self.current_page_index = -1
        self.page_cache = {}
        self.last_page_index = -1
        self.page_transitioning = False
        
        try:
            self.setupUi(self)
            
            # 初始化窗口
            self._init_window()
            
            # 设置页面
            self._setup_pages()
            
            # 设置导航（现在已经在_setup_pages中调用，但保留在这里以确保完整性）
            # self._setup_navigation()
            
            # 设置快捷键
            self._setup_keyboard_shortcuts()
            
            # 设置拖拽处理
            self._setup_drag_handlers()
            
            # 检查更新
            check_update()
            
            self.log("INFO", "MainWindow initialized successfully")
            
        except Exception as e:
            self.log("ERROR", f"Failed to initialize MainWindow: {str(e)}")
            # 即使在初始化过程中也尝试显示错误信息
            try:
                QtWidgets.QMessageBox.critical(self, "初始化错误", f"程序启动失败: {str(e)}")
            except:
                print(f"Critical initialization error: {str(e)}")
    
    def _handle_global_exception(self, exc_type, exc_value, exc_traceback):
        """全局异常处理函数"""
        import traceback
        error_message = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        # 记录详细错误到日志
        try:
            # 将日志写入文件
            import os
            log_dir = os.path.join(os.path.expanduser("~"), ".leafview", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "app.log")
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] [ERROR] Unhandled exception: {error_message}\n")
        except:
            pass
        
        # 打印到控制台
        print(f"Unhandled exception: {error_message}")
        
        # 向用户显示友好的错误信息
        user_friendly_message = f"程序遇到问题: {str(exc_value)}"
        try:
            QtWidgets.QMessageBox.critical(
                self, 
                "程序错误", 
                f"{user_friendly_message}\n\n请查看日志文件获取详细信息。",
                QtWidgets.QMessageBox.StandardButton.Ok
            )
        except:
            print(f"Critical error: {user_friendly_message}")
        


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
        """设置导航菜单，连接侧边栏导航与页面切换功能"""
        try:
            # 定义页面映射，方便导航管理
            self.page_map = {
                0: {"name": "媒体导入", "class_name": "FolderPage"},
                1: {"name": "智能整理", "class_name": "SmartArrangePage"},
                2: {"name": "文件去重", "class_name": "RemoveDuplicationPage"},
                3: {"name": "属性写入", "class_name": "WriteExifPage"},
                4: {"name": "文本识别", "class_name": "TextRecognitionPage"}
            }
            
            # 尝试获取导航菜单，优先使用 ui 中的组件
            self.navigation_menu = None
            if hasattr(self.ui, 'listNavigationMenu'):
                self.navigation_menu = self.ui.listNavigationMenu
            elif hasattr(self, 'listNavigationMenu'):
                self.navigation_menu = self.listNavigationMenu
            
            if self.navigation_menu:
                # 清空现有项，避免重复
                self.navigation_menu.clear()
                
                # 添加菜单项
                for i, page_info in self.page_map.items():
                    # 检查页面是否可用（比如TextRecognition可能不可用）
                    if i == 4 and not hasattr(self, 'text_recognition_page'):
                        continue
                    
                    item = QtWidgets.QListWidgetItem(page_info["name"])
                    # 设置样式和提示
                    item.setToolTip(f"切换到{page_info['name']}页面")
                    self.navigation_menu.addItem(item)
                
                # 优化导航菜单性能
                self.navigation_menu.setUniformItemSizes(True)
                self.navigation_menu.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
                
                # 连接项目点击信号
                self.navigation_menu.currentRowChanged.connect(self._on_navigation_item_clicked)
                
                # 初始化导航样式
                self._init_navigation_styles()
                
                self.log("INFO", "侧边栏导航功能已设置完成")
            else:
                self.log("WARNING", "导航菜单组件未在UI中找到")
                # 创建一个备用的导航功能
                self._create_fallback_navigation()
            
        except Exception as e:
            self.log("ERROR", f"设置导航时出错: {str(e)}")
            import traceback
            self.log("ERROR", traceback.format_exc())
    
    def _init_navigation_styles(self):
        """初始化导航菜单样式"""
        try:
            # 设置样式表，使用更现代的设计
            style_sheet = """
            QListWidget {
                background-color: transparent;
                border: none;
                padding: 5px;
                outline: none;
            }
            QListWidget::item {
                padding: 10px 15px;
                border-radius: 6px;
                margin-bottom: 4px;
                color: #555;
                background-color: transparent;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
                font-weight: bold;
            }
            QListWidget::item:hover:not(:selected) {
                background-color: #F5F5F5;
            }
            """
            
            if self.navigation_menu:
                self.navigation_menu.setStyleSheet(style_sheet)
                # 设置默认选中第一个项目
                if self.navigation_menu.count() > 0:
                    self.navigation_menu.setCurrentRow(0)
        except Exception as e:
            self.log("ERROR", f"初始化导航样式时出错: {str(e)}")
            
    def _on_navigation_item_clicked(self, row):
        """处理导航菜单项点击事件"""
        try:
            # 防止重复点击和过渡中点击
            if row >= 0 and row != self.current_page_index and not self.page_transitioning:
                self.log("INFO", f"点击导航菜单项，索引: {row}")
                self._show_page(row)
        except Exception as e:
            self.log("ERROR", f"处理导航点击时出错: {str(e)}")
            import traceback
            self.log("ERROR", traceback.format_exc())
    
    def _update_navigation_style(self, selected_index):
        """更新导航菜单的选中样式 - 现在主要通过样式表控制"""
        try:
            # 由于使用了样式表，这里主要保持导航菜单与当前页面的同步
            if self.navigation_menu and 0 <= selected_index < self.navigation_menu.count():
                # 避免触发信号循环
                try:
                    self.navigation_menu.blockSignals(True)
                    self.navigation_menu.setCurrentRow(selected_index)
                finally:
                    self.navigation_menu.blockSignals(False)
        except Exception as e:
            self.log("ERROR", f"更新导航样式时出错: {str(e)}")
    
    def _create_fallback_navigation(self):
        """创建备用导航功能，当UI组件不可用时"""
        self.log("INFO", "创建备用导航功能")
        # 这里可以实现一个简单的导航功能作为后备方案
        pass
    
    def _connect_buttons(self):
        """连接所有按钮的信号和槽，包括顶部工具栏功能"""
        try:
            # 窗口控制按钮（保留必要的功能连接）
            if hasattr(self, 'btn_close'):
                self.btn_close.clicked.connect(self.close)
            elif hasattr(self, 'btnClose'):
                self.btnClose.clicked.connect(self.close)
            
            if hasattr(self, 'btn_maximize'):
                self.btn_maximize.clicked.connect(self._toggle_maximize)
            elif hasattr(self, 'btnMaximize'):
                self.btnMaximize.clicked.connect(self._toggle_maximize)
                
            if hasattr(self, 'btn_minimize'):
                self.btn_minimize.clicked.connect(self.showMinimized)
            elif hasattr(self, 'btnMinimize'):
                self.btnMinimize.clicked.connect(self.showMinimized)
            
            # GitHub按钮
            if hasattr(self, 'btn_github'):
                self.btn_github.clicked.connect(self._on_github_clicked)
            elif hasattr(self, 'btnGithub'):
                self.btnGithub.clicked.connect(self._on_github_clicked)
            
            # 设置按钮
            if hasattr(self, 'btn_settings'):
                self.btn_settings.clicked.connect(self._on_settings_clicked)
            elif hasattr(self, 'btnSettings'):
                self.btnSettings.clicked.connect(self._on_settings_clicked)
                
            # 连接文件夹选择按钮
            if hasattr(self, 'btnBrowseSource'):
                self.btnBrowseSource.clicked.connect(self._select_source_folder)
            if hasattr(self, 'btnBrowseTarget'):
                self.btnBrowseTarget.clicked.connect(self._select_target_folder)
                
            # 快速工具栏按钮连接
            if hasattr(self, 'btn_addFolder'):
                self.btn_addFolder.clicked.connect(self._on_add_folder_clicked)
            elif hasattr(self, 'pushButton_addFolder'):
                self.pushButton_addFolder.clicked.connect(self._on_add_folder_clicked)
                
            if hasattr(self, 'pushButton_smartArrange'):
                self.pushButton_smartArrange.clicked.connect(lambda: self._show_page(1))
            if hasattr(self, 'pushButton_removeDuplicate'):
                self.pushButton_removeDuplicate.clicked.connect(lambda: self._show_page(2))
            if hasattr(self, 'pushButton_writeExif'):
                self.pushButton_writeExif.clicked.connect(lambda: self._show_page(3))
            if hasattr(self, 'pushButton_textRecognition'):
                self.pushButton_textRecognition.clicked.connect(lambda: self._show_page(4))
                
            # 智能整理相关按钮
            if hasattr(self, 'btnStartArrange'):
                self.btnStartArrange.clicked.connect(self._start_smart_arrange)
            if hasattr(self, 'btnStopArrange'):
                self.btnStopArrange.clicked.connect(self._stop_smart_arrange)
                
            # 文件去重相关按钮
            if hasattr(self, 'btnStartRemoveDuplicate'):
                self.btnStartRemoveDuplicate.clicked.connect(self._start_duplicate_removal)
            if hasattr(self, 'btnStopRemoveDuplicate'):
                self.btnStopRemoveDuplicate.clicked.connect(self._stop_duplicate_removal)
                
            # 属性写入相关按钮
            if hasattr(self, 'btnWriteExif'):
                self.btnWriteExif.clicked.connect(self._start_write_exif)
            if hasattr(self, 'btnStopWriteExif'):
                self.btnStopWriteExif.clicked.connect(self._stop_write_exif)
                
            self.log("INFO", "顶部工具栏按钮已连接")
        except Exception as e:
            self.log("ERROR", f"连接按钮时出错: {str(e)}")
            print(f"[WARNING] Failed to connect some buttons: {str(e)}")
    
    def _on_github_clicked(self):
        """处理GitHub按钮点击事件"""
        try:
            import webbrowser
            webbrowser.open("https://github.com")  # 这里可以替换为实际的GitHub仓库地址
            self.log("INFO", "已打开GitHub页面")
        except Exception as e:
            self.log("ERROR", f"打开GitHub页面时出错: {str(e)}")
    
    def _on_settings_clicked(self):
        """处理设置按钮点击事件"""
        try:
            self.log("INFO", "打开设置对话框")
            # 导入设置对话框类
            from SettingsDialog import SettingsDialog
            
            # 创建并显示设置对话框
            settings_dialog = SettingsDialog(self)
            
            # 连接设置变更信号
            def on_settings_changed(new_settings):
                self.log("INFO", "设置已更新")
                # 这里可以添加根据设置变更更新UI的逻辑
                self._update_ui_based_on_settings(new_settings)
            
            settings_dialog.settings_changed.connect(on_settings_changed)
            
            # 显示对话框
            settings_dialog.exec()
            
        except Exception as e:
            self.log("ERROR", f"打开设置时出错: {str(e)}")
            QtWidgets.QMessageBox.critical(self, "错误", f"打开设置对话框失败: {str(e)}")
    
    def _update_ui_based_on_settings(self, settings):
        """根据设置更新UI"""
        # 更新暗黑模式
        if settings.get("dark_mode", False):
            self._apply_dark_mode()
        else:
            self._apply_light_mode()
        
        # 更新视图模式
        # 这里可以添加其他UI更新逻辑
        pass
    
    def _apply_dark_mode(self):
        """应用暗黑模式样式"""
        # TODO: 实现暗黑模式样式
        pass
    
    def _apply_light_mode(self):
        """应用浅色模式样式"""
        # TODO: 实现浅色模式样式
        pass
            
    def _on_add_folder_clicked(self):
        """处理添加文件夹按钮点击事件，支持媒体文件导入"""
        try:
            # 确保切换到文件夹页面
            self._show_page(0)
            
            # 提供两种选择模式
            option = QtWidgets.QMessageBox.question(
                self, 
                "选择导入模式", 
                "请选择导入模式：\n\n1. 导入文件夹\n2. 导入特定文件",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.Yes
            )
            
            if option == QtWidgets.QMessageBox.Yes:  # 导入文件夹
                folder_path = QtWidgets.QFileDialog.getExistingDirectory(
                    self, 
                    "选择媒体文件夹", 
                    "",
                    QtWidgets.QFileDialog.Option.ShowDirsOnly | QtWidgets.QFileDialog.Option.DontResolveSymlinks
                )
                if folder_path:
                    self.log("INFO", f"选择的文件夹: {folder_path}")
                    self._handle_selected_folder(folder_path)
            else:  # 导入特定文件
                file_paths, _ = QtWidgets.QFileDialog.getOpenFileNames(
                    self,
                    "选择媒体文件",
                    "",
                    "媒体文件 (*.jpg *.jpeg *.png *.gif *.mp4 *.avi *.mov *.bmp *.tiff *.webp);;所有文件 (*)"
                )
                if file_paths:
                    self.log("INFO", f"选择了 {len(file_paths)} 个文件")
                    self._handle_selected_files(file_paths)
        except Exception as e:
            self.log("ERROR", f"选择媒体时出错: {str(e)}")
            self._show_user_notification("错误", f"导入失败: {str(e)}", "error")
    
    def _handle_selected_folder(self, folder_path):
        """处理选择的文件夹，扫描媒体文件并显示预览"""
        try:
            self.log("INFO", f"处理文件夹: {folder_path}")
            
            # 扫描文件夹中的媒体文件
            media_files = self._scan_media_files(folder_path)
            if media_files:
                self.log("INFO", f"找到 {len(media_files)} 个媒体文件")
                # 显示文件预览
                self._display_file_preview(media_files)
                # 更新文件列表
                self._update_file_list(media_files)
            else:
                self.log("WARNING", f"未在文件夹中找到媒体文件: {folder_path}")
                self._show_user_notification("提示", "所选文件夹中未找到支持的媒体文件", "info")
        except Exception as e:
            self.log("ERROR", f"处理文件夹时出错: {str(e)}")
            self._show_user_notification("错误", f"处理文件夹失败: {str(e)}", "error")
    
    def _handle_selected_files(self, file_paths):
        """处理选择的媒体文件，显示预览"""
        try:
            self.log("INFO", f"处理 {len(file_paths)} 个媒体文件")
            # 过滤有效的媒体文件
            valid_files = [f for f in file_paths if self._is_supported_media(f)]
            
            if valid_files:
                self.log("INFO", f"有效媒体文件: {len(valid_files)} 个")
                # 显示文件预览
                self._display_file_preview(valid_files)
                # 更新文件列表
                self._update_file_list(valid_files)
            else:
                self.log("WARNING", "未选择有效的媒体文件")
                self._show_user_notification("提示", "未选择支持的媒体文件", "info")
        except Exception as e:
            self.log("ERROR", f"处理文件时出错: {str(e)}")
            self._show_user_notification("错误", f"处理文件失败: {str(e)}", "error")
    
    def _scan_media_files(self, folder_path):
        """扫描文件夹中的媒体文件"""
        media_files = []
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.bmp', '.tiff', '.webp'}
        
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if any(file.lower().endswith(ext) for ext in supported_extensions):
                        media_files.append(os.path.join(root, file))
        except Exception as e:
            self.log("ERROR", f"扫描媒体文件时出错: {str(e)}")
        
        return media_files
    
    def _is_supported_media(self, file_path):
        """检查文件是否为支持的媒体格式"""
        supported_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.mp4', '.avi', '.mov', '.bmp', '.tiff', '.webp'}
        _, ext = os.path.splitext(file_path.lower())
        return ext in supported_extensions
    
    def _display_file_preview(self, file_paths):
        """显示文件预览"""
        try:
            # 这里可以实现预览逻辑，例如更新预览窗口
            if hasattr(self, 'label_preview'):
                # 显示第一个文件作为预览
                if file_paths:
                    self._update_preview(file_paths[0])
            
            # 更新预览计数
            if hasattr(self, 'label_preview_count'):
                self.label_preview_count.setText(f"预览: 1/{len(file_paths)}")
        except Exception as e:
            self.log("ERROR", f"显示预览时出错: {str(e)}")
    
    def _update_preview(self, file_path):
        """更新预览窗口显示指定文件"""
        try:
            if hasattr(self, 'label_preview'):
                _, ext = os.path.splitext(file_path.lower())
                if ext in {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}:
                    # 显示图片预览
                    pixmap = QtGui.QPixmap(file_path)
                    if not pixmap.isNull():
                        # 缩放图片以适应预览窗口
                        scaled_pixmap = pixmap.scaled(
                            self.label_preview.size(),
                            QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                            QtCore.Qt.TransformationMode.SmoothTransformation
                        )
                        self.label_preview.setPixmap(scaled_pixmap)
                        self.label_preview.setText("")
                    else:
                        self.label_preview.setText("无法预览图片")
                else:
                    # 对于视频文件，可以显示图标或提示
                    self.label_preview.setText(f"视频文件: {os.path.basename(file_path)}")
        except Exception as e:
            self.log("ERROR", f"更新预览时出错: {str(e)}")
    
    def _update_file_list(self, file_paths):
        """更新文件列表显示"""
        try:
            if hasattr(self, 'listWidget_files'):
                self.listWidget_files.clear()
                for file_path in file_paths:
                    item = QtWidgets.QListWidgetItem(os.path.basename(file_path))
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, file_path)  # 存储完整路径
                    self.listWidget_files.addItem(item)
                
                # 连接双击事件以预览文件
                self.listWidget_files.itemDoubleClicked.connect(self._on_file_double_clicked)
        except Exception as e:
            self.log("ERROR", f"更新文件列表时出错: {str(e)}")
    
    def _on_file_double_clicked(self, item):
        """处理文件双击事件，显示预览"""
        try:
            file_path = item.data(QtCore.Qt.ItemDataRole.UserRole)
            if file_path:
                self._update_preview(file_path)
        except Exception as e:
            self.log("ERROR", f"处理文件双击时出错: {str(e)}")

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
        """设置全局快捷键，增强键盘操作体验"""
        try:
            # 创建快捷键字典用于文档和提示
            self._shortcuts = {
                "添加文件夹": {"key": "Ctrl+A", "description": "打开添加文件夹对话框"},
                "批量添加文件夹": {"key": "Ctrl+Shift+A", "description": "打开批量添加文件夹对话框"},
                "智能整理": {"key": "Ctrl+S", "description": "切换到智能整理页面"},
                "查找重复文件": {"key": "Ctrl+D", "description": "切换到去重页面"},
                "EXIF信息查看": {"key": "Ctrl+E", "description": "切换到EXIF信息页面"},
                "刷新": {"key": "F5", "description": "刷新当前页面"},
                "帮助": {"key": "F1", "description": "显示帮助信息"},
                "下一页": {"key": "Ctrl+Tab", "description": "切换到下一个功能页面"},
                "上一页": {"key": "Ctrl+Shift+Tab", "description": "切换到上一个功能页面"},
                "退出": {"key": "Ctrl+Q", "description": "退出应用程序"},
                "最小化": {"key": "Ctrl+M", "description": "最小化窗口"},
                "删除选中项": {"key": "Delete", "description": "删除当前选中的项目"},
                "全选": {"key": "Ctrl+A", "description": "在支持的页面中全选项目"},
                "显示快捷键": {"key": "Ctrl+K", "description": "显示所有可用的快捷键列表"}
            }
            
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
            
            # 页面导航快捷键
            self.shortcut_next_page = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Tab"), self)
            self.shortcut_next_page.activated.connect(self._next_page)
            
            self.shortcut_prev_page = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Shift+Tab"), self)
            self.shortcut_prev_page.activated.connect(self._prev_page)
            
            self.shortcut_quit = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Q"), self)
            self.shortcut_quit.activated.connect(self.close)
            
            self.shortcut_minimize = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+M"), self)
            self.shortcut_minimize.activated.connect(self.showMinimized)
            
            # 新增快捷键
            # 删除选中项快捷键
            self.shortcut_delete = QtGui.QShortcut(QtGui.QKeySequence("Delete"), self)
            self.shortcut_delete.activated.connect(self._on_delete_clicked)
            
            # 显示快捷键列表
            self.shortcut_show_shortcuts = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+K"), self)
            self.shortcut_show_shortcuts.activated.connect(self._show_keyboard_shortcuts)
            
            # 确保窗口支持键盘事件传递
            self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)
            
            self.log("INFO", "键盘快捷键设置完成，支持增强功能")
            print("Keyboard shortcuts setup completed with enhanced support")
        except Exception as e:
            self.log("ERROR", f"设置快捷键时出错: {str(e)}")
            print(f"Error setting up keyboard shortcuts: {str(e)}")
            import traceback
            traceback.print_exc()

    def _next_page(self):
        """切换到下一页"""
        if self.page_transitioning:
            return
            
        current_index = self.stackedWidget.currentIndex()
        next_index = (current_index + 1) % self.stackedWidget.count()
        self._show_page(next_index)
        
    def _prev_page(self):
        """切换到上一页"""
        if self.page_transitioning:
            return
            
        current_index = self.stackedWidget.currentIndex()
        prev_index = (current_index - 1) % self.stackedWidget.count()
        self._show_page(prev_index)
        
    def _light_refresh_current_page(self):
        """轻量级刷新当前页面，用于从缓存恢复时"""
        try:
            # 获取当前活动页面
            current_widget = None
            if hasattr(self, 'stackedWidget'):
                current_widget = self.stackedWidget.currentWidget()
            elif hasattr(self.ui, 'stackedWidget'):
                current_widget = self.ui.stackedWidget.currentWidget()
            
            if current_widget is not None:
                # 尝试调用页面自定义的轻量级刷新方法
                if hasattr(current_widget, 'light_refresh'):
                    current_widget.light_refresh()
                    page_name = current_widget.__class__.__name__
                    self.log("INFO", f"已轻量刷新页面: {page_name}")
                else:
                    # 根据页面类型执行针对性的轻量更新
                    if hasattr(self, 'current_page_index'):
                        if self.current_page_index == 0 and hasattr(self, 'folder_page'):
                            # 媒体导入页面 - 轻量刷新文件夹列表
                            if hasattr(self.folder_page, '_update_folder_stats'):
                                self.folder_page._update_folder_stats()
                        elif self.current_page_index == 1 and hasattr(self, 'smart_arrange_page'):
                            # 智能整理页面 - 刷新状态但不重新扫描
                            pass
            
        except Exception as e:
            self.log("ERROR", f"轻量级刷新页面时出错: {str(e)}")
            # 降级到完整刷新
            self._refresh_current_page()
    
    def _show_page(self, page_index):
        """显示指定页面 - 优化版，支持页面缓存和平滑切换"""
        try:
            # 标记正在过渡
            self.page_transitioning = True
            
            # 检查stackedWidget是否存在
            stacked_widget = None
            if hasattr(self.ui, 'stackedWidget'):
                stacked_widget = self.ui.stackedWidget
            elif hasattr(self, 'stackedWidget'):
                stacked_widget = self.stackedWidget
            else:
                self.log("ERROR", "stackedWidget不存在")
                self.page_transitioning = False
                return False
            
            # 验证索引是否有效
            if 0 <= page_index < stacked_widget.count():
                # 记录上一个页面
                self.last_page_index = self.current_page_index
                self.current_page_index = page_index
                
                # 直接设置当前索引即可，PyQt会自动处理显示/隐藏
                stacked_widget.setCurrentIndex(page_index)
                target_page = stacked_widget.currentWidget()
                
                # 更新导航选中状态
                self._update_navigation_style(page_index)
                
                # 获取页面信息
                page_info = self.page_map.get(page_index, {})
                page_name = page_info.get("name", "未知页面")
                self.log("INFO", f"切换到页面: {page_name} (索引: {page_index})")
                
                # 使用缓存或懒加载优化页面刷新
                if page_index not in self.page_cache or not self.page_cache[page_index]:
                    # 页面首次加载或需要刷新
                    self._refresh_current_page()
                    # 缓存页面状态
                    self.page_cache[page_index] = True
                else:
                    # 从缓存恢复页面时的轻量更新
                    self._light_refresh_current_page()
                
                # 显示简短提示，避免频繁打扰用户
                if self.last_page_index != -1:  # 不是首次加载
                    self._show_user_notification("页面切换", f"已切换到 {page_name}", "info", 1500)
                
                # 允许UI更新
                QtWidgets.QApplication.processEvents()
                
                self.page_transitioning = False
                return True
            else:
                self.log("ERROR", f"无效的页面索引: {page_index}，有效范围: 0-{stacked_widget.count()-1}")
                # 回退到第一个页面
                if stacked_widget.count() > 0:
                    stacked_widget.setCurrentIndex(0)
                    self.current_page_index = 0
                    self.log("INFO", "已回退到第一个页面")
                
                self.page_transitioning = False
                return stacked_widget.count() > 0
        except Exception as e:
            self.log("ERROR", f"切换页面时出错: {str(e)}")
            import traceback
            self.log("ERROR", traceback.format_exc())
            self.page_transitioning = False
            return False
    
    def _refresh_current_page(self):
        """刷新当前页面 - 增强版"""
        try:
            # 显示刷新中的提示
            self._show_user_notification("正在刷新", "页面正在刷新中...", "info", timeout=1000)
            
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
            error_msg = f"刷新页面组件时出错: {str(e)}"
            self.log("ERROR", error_msg)
            
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
                    self._show_user_notification("刷新成功", "文件夹页面已刷新", "success", timeout=2000)
            elif current_index == 1 and hasattr(self, 'smart_arrange_page'):
                # 刷新智能整理页面
                if hasattr(self.smart_arrange_page, '_refresh_ui'):
                    self.smart_arrange_page._refresh_ui()
                    self.log("INFO", "智能整理页面已刷新")
                    self._show_user_notification("刷新成功", "智能整理页面已刷新", "success", timeout=2000)
            elif current_index == 2 and hasattr(self, 'remove_dup_page'):
                # 刷新去重页面
                if hasattr(self.remove_dup_page, '_refresh_ui'):
                    self.remove_dup_page._refresh_ui()
                    self.log("INFO", "去重页面已刷新")
                    self._show_user_notification("刷新成功", "去重页面已刷新", "success", timeout=2000)
            elif current_index == 3 and hasattr(self, 'write_exif_page'):
                # 刷新EXIF编辑页面
                if hasattr(self.write_exif_page, '_refresh_ui'):
                    self.write_exif_page._refresh_ui()
                    self.log("INFO", "EXIF编辑页面已刷新")
                    self._show_user_notification("刷新成功", "EXIF编辑页面已刷新", "success", timeout=2000)
            elif current_index == 4 and hasattr(self, 'text_recog_page'):
                # 刷新文字识别页面
                if hasattr(self.text_recog_page, '_refresh_ui'):
                    self.text_recog_page._refresh_ui()
                    self.log("INFO", "文字识别页面已刷新")
                    self._show_user_notification("刷新成功", "文字识别页面已刷新", "success", timeout=2000)
        except Exception as e:
            error_msg = f"刷新页面时出错: {str(e)}"
            self.log("ERROR", error_msg)
            print(f"Error refreshing page: {str(e)}")
            import traceback
            traceback.print_exc()
            self._show_user_notification("刷新失败", error_msg, "error")
    
    def _show_help(self):
        """显示帮助信息 - 保留核心功能"""
        self.log("INFO", "Showing help information")
        # 保留功能但简化实现
        QtWidgets.QMessageBox.information(self, "帮助", "枫叶相册 - 核心功能正常运行")
        
    def _on_delete_clicked(self):
        """处理删除选中项的快捷键操作"""
        try:
            current_page = self.stackedWidget.currentWidget()
            if hasattr(current_page, 'delete_selected_items'):
                # 如果当前页面有删除选中项的方法
                current_page.delete_selected_items()
            elif hasattr(current_page, 'delete_selected'):
                # 兼容其他命名约定
                current_page.delete_selected()
            elif hasattr(current_page, 'remove_selected'):
                current_page.remove_selected()
            else:
                # 对于不支持直接删除的页面，显示提示
                QtWidgets.QMessageBox.information(
                    self,
                    "提示",
                    "当前页面不支持删除操作或没有选中可删除的项目。",
                    QtWidgets.QMessageBox.StandardButton.Ok
                )
        except Exception as e:
            self.log("ERROR", f"删除操作时出错: {str(e)}")
            QtWidgets.QMessageBox.critical(
                self,
                "错误",
                f"执行删除操作时发生错误: {str(e)}"
            )
            
    def _show_keyboard_shortcuts(self):
        """显示所有可用的快捷键列表"""
        try:
            from PyQt6.QtWidgets import QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QPushButton, QLabel
            from PyQt6.QtCore import Qt
            from PyQt6.QtGui import QFont
            
            dialog = QDialog(self)
            dialog.setWindowTitle("键盘快捷键")
            dialog.resize(500, 400)
            
            layout = QVBoxLayout(dialog)
            
            # 创建表格视图
            table = QTableWidget(len(self._shortcuts), 2)
            table.setHorizontalHeaderLabels(["快捷键", "功能描述"])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            table.verticalHeader().setVisible(False)
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            
            # 填充表格数据
            row = 0
            for action, info in self._shortcuts.items():
                key_item = QTableWidgetItem(f"{info['key']} ({action})")
                desc_item = QTableWidgetItem(info['description'])
                
                # 设置字体和对齐
                key_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                key_item.setFont(QFont("Microsoft YaHei", 10))
                desc_item.setFont(QFont("Microsoft YaHei", 10))
                
                table.setItem(row, 0, key_item)
                table.setItem(row, 1, desc_item)
                row += 1
            
            # 添加关闭按钮
            btn_close = QPushButton("关闭")
            btn_close.clicked.connect(dialog.close)
            
            # 添加说明文本
            label = QLabel("按 Esc 键也可以关闭此对话框")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet("color: #666; font-style: italic;")
            
            # 设置布局
            layout.addWidget(table)
            layout.addWidget(label)
            layout.addWidget(btn_close, 0, Qt.AlignmentFlag.AlignCenter)
            
            # 支持ESC键关闭
            dialog.setWindowFlags(dialog.windowFlags() | Qt.WindowType.WindowCloseButtonHint)
            dialog.exec_()
        except Exception as e:
            self.log("ERROR", f"显示快捷键列表时出错: {str(e)}")
            QtWidgets.QMessageBox.critical(
                self,
                "错误",
                f"显示快捷键列表时发生错误: {str(e)}"
            )
            
    def keyPressEvent(self, event):
        """重写键盘事件处理，支持ESC键关闭对话框"""
        from PyQt6.QtCore import Qt
        from PyQt6.QtWidgets import QApplication
        
        if event.key() == Qt.Key.Key_Escape:
            # 检查是否有活动的模态对话框
            active_window = QApplication.activeModalWidget()
            if active_window:
                active_window.close()
            else:
                # 对于非模态对话框或没有打开对话框的情况，调用基类实现
                super().keyPressEvent(event)
        else:
            # 其他键按正常流程处理
            super().keyPressEvent(event)

    def log(self, level, message):
        """日志记录函数 - 增强版"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 为不同级别日志添加颜色
        if level == "ERROR":
            color = "\033[91m"  # 红色
        elif level == "WARNING":
            color = "\033[93m"  # 黄色
        elif level == "INFO":
            color = "\033[92m"  # 绿色
        else:
            color = "\033[0m"   # 默认
        
        log_message = f"{color}[{timestamp}] [{level}] {message}\033[0m"
        print(log_message)
        
        # 将日志写入文件
        try:
            import os
            log_dir = os.path.join(os.path.expanduser("~"), ".leafview", "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "app.log")
            
            # 写入无颜色的日志到文件
            file_log_message = f"[{timestamp}] [{level}] {message}"
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(file_log_message + "\n")
                
            # 限制日志文件大小（保留最近的5000行）
            self._rotate_logs(log_file)
            
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
                
    def _rotate_logs(self, log_file):
        """日志文件轮转，保留最近的日志记录"""
        try:
            if os.path.exists(log_file) and os.path.getsize(log_file) > 1024 * 1024:  # 1MB
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # 保留最后5000行
                if len(lines) > 5000:
                    with open(log_file, 'w', encoding='utf-8') as f:
                        f.writelines(lines[-5000:])
        except Exception as e:
            print(f"Error rotating logs: {str(e)}")
            
    def _toggle_maximize(self):
        """切换窗口最大化状态"""
        try:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
        except Exception as e:
            self.log("ERROR", f"切换窗口最大化状态时出错: {str(e)}")
        

    def _show_user_notification(self, title, message, level="info", timeout=None):
        """增强版用户通知函数"""
        try:
            if level == "error":
                icon = QtWidgets.QMessageBox.Icon.Critical
                buttons = QtWidgets.QMessageBox.StandardButton.Ok
                msg_box = QtWidgets.QMessageBox(icon, title, message, buttons, self)
            elif level == "warning":
                icon = QtWidgets.QMessageBox.Icon.Warning
                buttons = QtWidgets.QMessageBox.StandardButton.Ok | QtWidgets.QMessageBox.StandardButton.Cancel
                msg_box = QtWidgets.QMessageBox(icon, title, message, buttons, self)
            elif level == "success":
                icon = QtWidgets.QMessageBox.Icon.Information
                buttons = QtWidgets.QMessageBox.StandardButton.Ok
                msg_box = QtWidgets.QMessageBox(icon, title, message, buttons, self)
            else:  # info
                icon = QtWidgets.QMessageBox.Icon.Information
                buttons = QtWidgets.QMessageBox.StandardButton.Ok
                msg_box = QtWidgets.QMessageBox(icon, title, message, buttons, self)
            
            # 设置按钮文本为中文
            for button in msg_box.buttons():
                text = button.text()
                if 'OK' in text:
                    button.setText('确定')
                elif 'Cancel' in text:
                    button.setText('取消')
            
            # 居中显示
            msg_box.setWindowFlag(QtCore.Qt.WindowType.WindowStaysOnTopHint)
            
            # 对于info和success类型，可以设置自动关闭
            if timeout and level in ['info', 'success']:
                # 创建定时器自动关闭消息框
                timer = QtCore.QTimer(self)
                timer.timeout.connect(msg_box.close)
                timer.start(timeout)
            
            return msg_box.exec()
        except Exception as e:
            print(f"Error showing notification: {str(e)}")
            # 回退到简单的打印
            print(f"[{level.upper()}] {title}: {message}")
                
        except Exception as e:
            print(f"[{level.upper()}] {title}: {message}")
            print(f"Failed to show notification: {str(e)}")
    
    def _start_smart_arrange(self):
        """启动智能整理功能"""
        try:
            self.log("INFO", "开始智能整理")
            
            # 获取源文件夹
            source_folder = None
            if hasattr(self, 'inputSourceFolder'):
                source_folder = self.inputSourceFolder.text()
            
            # 获取目标文件夹
            target_folder = None
            if hasattr(self, 'inputTargetFolder'):
                target_folder = self.inputTargetFolder.text()
            
            # 验证文件夹路径
            if not source_folder or not os.path.isdir(source_folder):
                self._show_user_notification("错误", "请选择有效的源文件夹", "error")
                return
            
            # 如果没有指定目标文件夹，使用源文件夹
            if not target_folder:
                target_folder = source_folder
            
            # 创建文件夹信息列表
            folders = [{'path': source_folder, 'include_sub': 1}]  # 假设总是包含子文件夹
            
            # 获取分类和命名结构（这里使用默认值，实际应用中可以从UI获取）
            classification_structure = ["文件类型", "年", "月"]
            file_name_structure = ["年", "月", "日", "原文件名"]
            separator = "-"
            time_derive = "文件创建时间"
            
            # 创建并启动智能整理线程
            self.smart_arrange_thread = SmartArrangeThread(
                parent=self,
                folders=folders,
                classification_structure=classification_structure,
                file_name_structure=file_name_structure,
                destination_root=target_folder,
                separator=separator,
                time_derive=time_derive
            )
            
            # 连接信号
            self.smart_arrange_thread.log_signal.connect(self._on_arrange_log)
            self.smart_arrange_thread.progress_signal.connect(self._on_arrange_progress)
            self.smart_arrange_thread.finished.connect(self._on_arrange_finished)
            
            # 启动线程
            self.smart_arrange_thread.start()
            self.log("INFO", "智能整理线程已启动")
            
            # 更新UI状态
            if hasattr(self, 'btnStartArrange'):
                self.btnStartArrange.setEnabled(False)
            if hasattr(self, 'btnStopArrange'):
                self.btnStopArrange.setEnabled(True)
                
        except Exception as e:
            self.log("ERROR", f"启动智能整理时出错: {str(e)}")
            self._show_user_notification("错误", f"启动失败: {str(e)}", "error")
    
    def _stop_smart_arrange(self):
        """停止智能整理"""
        try:
            if self.smart_arrange_thread and self.smart_arrange_thread.isRunning():
                self.log("INFO", "正在停止智能整理")
                self.smart_arrange_thread.stop()
                # 等待线程结束
                self.smart_arrange_thread.wait(5000)  # 最多等待5秒
                self.log("INFO", "智能整理已停止")
            
            # 更新UI状态
            if hasattr(self, 'btnStartArrange'):
                self.btnStartArrange.setEnabled(True)
            if hasattr(self, 'btnStopArrange'):
                self.btnStopArrange.setEnabled(False)
                
        except Exception as e:
            self.log("ERROR", f"停止智能整理时出错: {str(e)}")
    
    def _on_arrange_log(self, level, message):
        """处理智能整理的日志信息"""
        try:
            self.log(level, f"智能整理: {message}")
            # 如果有日志显示区域，可以在这里更新
            if hasattr(self, 'textBrowser_log'):
                self.textBrowser_log.append(f"[{level}] {message}")
                self.textBrowser_log.verticalScrollBar().setValue(
                    self.textBrowser_log.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"处理整理日志时出错: {str(e)}")
    
    def _on_arrange_progress(self, progress):
        """处理智能整理的进度更新"""
        try:
            # 如果有进度条，可以在这里更新
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(progress)
        except Exception as e:
            print(f"更新进度时出错: {str(e)}")
    
    def _on_arrange_finished(self):
        """处理智能整理完成事件"""
        try:
            self.log("INFO", "智能整理完成")
            self._show_user_notification("成功", "智能整理已完成", "info")
            
            # 更新UI状态
            if hasattr(self, 'btnStartArrange'):
                self.btnStartArrange.setEnabled(True)
            if hasattr(self, 'btnStopArrange'):
                self.btnStopArrange.setEnabled(False)
                
            # 刷新当前页面
            self._refresh_current_page()
            
        except Exception as e:
            self.log("ERROR", f"处理整理完成事件时出错: {str(e)}")
    
    def _start_duplicate_removal(self):
        """启动文件去重功能"""
        try:
            self.log("INFO", "开始文件去重")
            
            # 获取源文件夹
            source_folder = None
            if hasattr(self, 'inputSourceFolder'):
                source_folder = self.inputSourceFolder.text()
            
            # 验证文件夹路径
            if not source_folder or not os.path.isdir(source_folder):
                self._show_user_notification("错误", "请选择有效的源文件夹", "error")
                return
            
            # 扫描文件夹中的图片文件
            image_paths = self._scan_image_files(source_folder)
            if not image_paths:
                self._show_user_notification("提示", "未在文件夹中找到支持的图片文件", "info")
                return
            
            self.log("INFO", f"找到 {len(image_paths)} 个图片文件")
            
            # 更新UI状态
            if hasattr(self, 'btnStartRemoveDuplicate'):
                self.btnStartRemoveDuplicate.setEnabled(False)
            if hasattr(self, 'btnStopRemoveDuplicate'):
                self.btnStopRemoveDuplicate.setEnabled(True)
            
            # 清空之前的哈希数据
            self.image_hashes = {}
            
            # 创建并启动哈希计算线程
            self.hash_worker = HashWorker(image_paths)
            self.hash_worker.hash_completed.connect(self._on_hash_completed)
            self.hash_worker.progress_updated.connect(self._on_hash_progress)
            self.hash_worker.error_occurred.connect(self._on_hash_error)
            self.hash_worker.start()
            
        except Exception as e:
            self.log("ERROR", f"启动文件去重时出错: {str(e)}")
            self._show_user_notification("错误", f"启动失败: {str(e)}", "error")
    
    def _stop_duplicate_removal(self):
        """停止文件去重"""
        try:
            self.log("INFO", "正在停止文件去重")
            
            # 停止对比线程
            if self.contrast_worker and self.contrast_worker.isRunning():
                self.contrast_worker.stop()
                self.contrast_worker.wait(3000)
            
            # 停止哈希线程
            if self.hash_worker and self.hash_worker.isRunning():
                self.hash_worker.stop()
                self.hash_worker.wait(3000)
            
            self.log("INFO", "文件去重已停止")
            
            # 更新UI状态
            if hasattr(self, 'btnStartRemoveDuplicate'):
                self.btnStartRemoveDuplicate.setEnabled(True)
            if hasattr(self, 'btnStopRemoveDuplicate'):
                self.btnStopRemoveDuplicate.setEnabled(False)
                
        except Exception as e:
            self.log("ERROR", f"停止文件去重时出错: {str(e)}")
    
    def _scan_image_files(self, folder_path):
        """扫描文件夹中的图片文件"""
        image_files = []
        supported_extensions = ('.jpg', '.jpeg', '.png', '.bmp', '.gif',
                               '.heic', '.heif', '.webp', '.tif', '.tiff')
        
        try:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(supported_extensions):
                        image_files.append(os.path.join(root, file))
        except Exception as e:
            self.log("ERROR", f"扫描图片文件时出错: {str(e)}")
        
        return image_files
    
    def _on_hash_completed(self, hashes):
        """处理哈希计算完成事件"""
        try:
            self.image_hashes = hashes
            self.log("INFO", f"哈希计算完成，成功计算 {len(hashes)} 个文件的哈希值")
            
            if not hashes:
                self._show_user_notification("提示", "无法计算任何文件的哈希值", "info")
                # 恢复UI状态
                if hasattr(self, 'btnStartRemoveDuplicate'):
                    self.btnStartRemoveDuplicate.setEnabled(True)
                if hasattr(self, 'btnStopRemoveDuplicate'):
                    self.btnStopRemoveDuplicate.setEnabled(False)
                return
            
            # 开始相似度对比
            similarity_threshold = 5  # 相似度阈值，可根据UI设置调整
            self.contrast_worker = ContrastWorker(hashes, similarity_threshold, self)
            self.contrast_worker.progress_signal.connect(self._on_contrast_progress)
            self.contrast_worker.result_signal.connect(self._on_contrast_result)
            self.contrast_worker.finished_signal.connect(self._on_contrast_finished)
            self.contrast_worker.log_signal.connect(self._on_contrast_log)
            self.contrast_worker.start()
            
        except Exception as e:
            self.log("ERROR", f"处理哈希完成事件时出错: {str(e)}")
    
    def _on_hash_progress(self, progress):
        """处理哈希计算进度更新"""
        try:
            # 更新进度条
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(progress)
        except Exception as e:
            print(f"更新哈希进度时出错: {str(e)}")
    
    def _on_hash_error(self, error):
        """处理哈希计算错误"""
        self.log("ERROR", f"哈希计算错误: {error}")
        self._show_user_notification("错误", f"哈希计算失败: {error}", "error")
        
        # 恢复UI状态
        if hasattr(self, 'btnStartRemoveDuplicate'):
            self.btnStartRemoveDuplicate.setEnabled(True)
        if hasattr(self, 'btnStopRemoveDuplicate'):
            self.btnStopRemoveDuplicate.setEnabled(False)
    
    def _on_contrast_progress(self, progress):
        """处理相似度对比进度更新"""
        try:
            # 哈希计算占40%，对比占60%
            if hasattr(self, 'progressBar'):
                adjusted_progress = 40 + int(progress * 0.6)
                self.progressBar.setValue(adjusted_progress)
        except Exception as e:
            print(f"更新对比进度时出错: {str(e)}")
    
    def _on_contrast_result(self, similar_groups):
        """处理相似度对比结果"""
        try:
            self.log("INFO", f"相似度对比完成，找到 {len(similar_groups)} 组相似图片")
            
            # 显示结果
            if similar_groups:
                # 更新结果列表
                if hasattr(self, 'listWidget_duplicates'):
                    self.listWidget_duplicates.clear()
                    for i, group in enumerate(similar_groups):
                        group_title = f"组 {i+1}: {len(group)} 个相似文件"
                        item = QtWidgets.QListWidgetItem(group_title)
                        item.setData(QtCore.Qt.ItemDataRole.UserRole, group)
                        self.listWidget_duplicates.addItem(item)
                
                # 显示详细信息
                message = f"发现 {len(similar_groups)} 组相似图片\n\n"
                for i, group in enumerate(similar_groups):
                    message += f"组 {i+1}:\n"
                    for file_path in group[:3]:  # 只显示前3个文件
                        message += f"  - {os.path.basename(file_path)}\n"
                    if len(group) > 3:
                        message += f"  ... 等 {len(group) - 3} 个文件\n"
                    message += "\n"
                
                self._show_user_notification("去重结果", message, "info")
            else:
                self._show_user_notification("去重结果", "未发现重复图片", "info")
                
        except Exception as e:
            self.log("ERROR", f"处理对比结果时出错: {str(e)}")
    
    def _on_contrast_finished(self):
        """处理对比完成事件"""
        try:
            self.log("INFO", "文件去重完成")
            
            # 更新进度条为100%
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(100)
            
            # 更新UI状态
            if hasattr(self, 'btnStartRemoveDuplicate'):
                self.btnStartRemoveDuplicate.setEnabled(True)
            if hasattr(self, 'btnStopRemoveDuplicate'):
                self.btnStopRemoveDuplicate.setEnabled(False)
                
        except Exception as e:
            self.log("ERROR", f"处理对比完成事件时出错: {str(e)}")
    
    def _on_contrast_log(self, level, message):
        """处理对比过程中的日志信息"""
        try:
            self.log(level, f"文件去重: {message}")
            # 如果有日志显示区域，可以在这里更新
            if hasattr(self, 'textBrowser_log'):
                self.textBrowser_log.append(f"[{level}] {message}")
                self.textBrowser_log.verticalScrollBar().setValue(
                    self.textBrowser_log.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"处理对比日志时出错: {str(e)}")
    
    def _start_write_exif(self):
        """启动属性写入功能"""
        try:
            self.log("INFO", "开始写入EXIF属性")
            
            # 获取文件夹路径和子文件夹选项
            folders_dict = []
            if hasattr(self, 'inputSourceFolder'):
                source_folder = self.inputSourceFolder.text()
                if source_folder and os.path.isdir(source_folder):
                    include_sub = 1 if hasattr(self, 'checkBoxIncludeSubfolders') and self.checkBoxIncludeSubfolders.isChecked() else 0
                    folders_dict.append({'path': source_folder, 'include_sub': include_sub})
            
            if not folders_dict:
                self._show_user_notification("错误", "请选择有效的源文件夹", "error")
                return
            
            # 获取元数据输入
            title = ''
            author = ''
            subject = ''
            rating = ''
            copyright = ''
            position = ''
            shoot_time = ''
            camera_brand = None
            camera_model = None
            lens_brand = None
            lens_model = None
            
            # 从UI控件获取元数据
            if hasattr(self, 'lineEdit_title'):
                title = self.lineEdit_title.text()
            if hasattr(self, 'lineEdit_author'):
                author = self.lineEdit_author.text()
            if hasattr(self, 'lineEdit_subject'):
                subject = self.lineEdit_subject.text()
            if hasattr(self, 'lineEdit_rating'):
                rating = self.lineEdit_rating.text()
            if hasattr(self, 'lineEdit_copyright'):
                copyright = self.lineEdit_copyright.text()
            if hasattr(self, 'lineEdit_position'):
                position = self.lineEdit_position.text()
            if hasattr(self, 'lineEdit_shoot_time'):
                shoot_time = self.lineEdit_shoot_time.text()
            
            # 创建并启动EXIF写入线程
            self.write_exif_thread = WriteExifThread(
                folders_dict=folders_dict,
                title=title,
                author=author,
                subject=subject,
                rating=rating,
                copyright=copyright,
                position=position,
                shoot_time=shoot_time,
                camera_brand=camera_brand,
                camera_model=camera_model,
                lens_brand=lens_brand,
                lens_model=lens_model
            )
            
            # 连接信号
            self.write_exif_thread.progress_updated.connect(self._on_exif_progress_updated)
            self.write_exif_thread.finished_conversion.connect(self._on_exif_finished)
            self.write_exif_thread.log_signal.connect(self._on_exif_log)
            
            # 更新UI状态
            if hasattr(self, 'btnWriteExif'):
                self.btnWriteExif.setEnabled(False)
            if hasattr(self, 'btnStopWriteExif'):
                self.btnStopWriteExif.setEnabled(True)
            
            # 启动线程
            self.write_exif_thread.start()
            
        except Exception as e:
            self.log("ERROR", f"启动EXIF写入时出错: {str(e)}")
            self._show_user_notification("错误", f"启动失败: {str(e)}", "error")
    
    def _stop_write_exif(self):
        """停止属性写入"""
        try:
            self.log("INFO", "正在停止EXIF写入")
            
            if self.write_exif_thread and self.write_exif_thread.isRunning():
                self.write_exif_thread.stop()
                self.write_exif_thread.wait(3000)
            
            self.log("INFO", "EXIF写入已停止")
            
            # 更新UI状态
            if hasattr(self, 'btnWriteExif'):
                self.btnWriteExif.setEnabled(True)
            if hasattr(self, 'btnStopWriteExif'):
                self.btnStopWriteExif.setEnabled(False)
                
        except Exception as e:
            self.log("ERROR", f"停止EXIF写入时出错: {str(e)}")
    
    def _on_exif_progress_updated(self, progress):
        """处理EXIF写入进度更新"""
        try:
            # 更新进度条
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(progress)
        except Exception as e:
            print(f"更新EXIF进度时出错: {str(e)}")
    
    def _on_exif_finished(self):
        """处理EXIF写入完成事件"""
        try:
            self.log("INFO", "EXIF属性写入完成")
            
            # 更新UI状态
            if hasattr(self, 'btnWriteExif'):
                self.btnWriteExif.setEnabled(True)
            if hasattr(self, 'btnStopWriteExif'):
                self.btnStopWriteExif.setEnabled(False)
            
            # 更新进度条
            if hasattr(self, 'progressBar'):
                self.progressBar.setValue(100)
                
            self._show_user_notification("成功", "EXIF属性写入已完成", "info")
            
        except Exception as e:
            self.log("ERROR", f"处理EXIF完成事件时出错: {str(e)}")
    
    def _on_exif_log(self, level, message):
        """处理EXIF写入过程中的日志信息"""
        try:
            self.log(level, f"属性写入: {message}")
            # 更新日志显示区域
            if hasattr(self, 'textBrowser_log'):
                self.textBrowser_log.append(f"[{level}] {message}")
                self.textBrowser_log.verticalScrollBar().setValue(
                    self.textBrowser_log.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"处理EXIF日志时出错: {str(e)}")

    def _feedback(self):
        QDesktopServices.openUrl(QUrl('https://qun.qq.com/universal-share/share?ac=1&authKey=wjyQkU9iG7wc'
                                      '%2BsIEOWFE6cA0ayLLBdYwpMsKYveyufXSOE5FBe7bb9xxvuNYVsEn&busi_data'
                                      '=eyJncm91cENvZGUiOiIxMDIxNDcxODEzIiwidG9rZW4iOiJDaFYxYVpySU9FUVJr'
                                      'RzkwdUZ2QlFVUTQzZzV2VS83TE9mY0NNREluaUZCR05YcnNjWmpKU2V5Q2FYTllFVlJ'
                                      'MIiwidWluIjoiMzU1ODQ0Njc5In0&data=M7fVC3YlI68T2S2VpmsR20t9s_xJj6HNpF'
                                      '0GGk2ImSQ9iCE8fZomQgrn_ADRZF0Ee4OSY0x6k2tI5P47NlkWug&svctype=4&tempid'
                                      '=h5_group_info'))

    def _select_source_folder(self):
        """选择源文件夹并显示文件夹信息"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "选择要处理的文件夹",
            "",
            QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            # 更新源文件夹输入框
            if hasattr(self, 'inputSourceFolder'):
                self.inputSourceFolder.setText(folder_path)
            
            # 调用folder_page来检查和显示文件夹信息
            if hasattr(self, 'folder_page'):
                # 尝试直接使用folder_page的方法来显示文件夹信息
                try:
                    # 收集文件夹统计信息
                    stats = self.folder_page._collect_folder_stats(folder_path)
                    # 显示文件夹信息到textBrowser_import_info
                    self.folder_page._show_folder_info(folder_path, stats)
                    print(f"[INFO] 已显示文件夹 '{folder_path}' 的信息")
                except Exception as e:
                    print(f"[ERROR] 显示文件夹信息时出错: {str(e)}")

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
