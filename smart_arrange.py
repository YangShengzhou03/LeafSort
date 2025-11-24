from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QMessageBox, QInputDialog
from smart_arrange_thread import SmartArrangeThread

class SmartArrangeManager(QObject):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.last_selected_button_index = -1
        self.destination_root = None
        self.selected_folders = []

        self.tag_buttons = {
            '原名': self.parent.btnAddOriginalTag,
            '年份': self.parent.btnAddYearTag,
            '月份': self.parent.btnAddMonthTag,
            '日': self.parent.btnAddDateTag,
            '星期': self.parent.btnDayTag,
            '时间': self.parent.btnAddTimeTag,
            '品牌': self.parent.btnAddMakeTag,
            '型号': self.parent.btnModelTag,
            '位置': self.parent.btnAddressTag,
            '自定义': self.parent.btnCustomizeTag
        }

        self.separator_mapping = {
            "-": "-",
            "无": "",
            "空格": " ",
            "_": "_",
            ".": ".",
            ",": ",",
            "|": "|",
            "~": "~"
        }

        self.available_frame = self.parent.frameRenameTags
        self.selected_frame = self.parent.frameRename

        self.SmartArrange_thread = None
        self.SmartArrange_settings = []

        self.init_page()
        self.set_combo_box_states()

    def init_page(self):
        self.connect_signals()

        for i in range(1, 6):
            getattr(self.parent, f'comboClassificationLevel{i}').currentIndexChanged.connect(
                lambda index, level=i: self.handle_combobox_selection(level, index))

        for button in self.tag_buttons.values():
            button.clicked.connect(lambda checked, b=button: self.move_tag(b))

    def connect_signals(self):
        # 确保log_signal正确初始化和连接
        if not hasattr(self, 'log_signal'):
            from PyQt6.QtCore import pyqtSignal
            self.log_signal = pyqtSignal(str, str)
        
        # 连接fileOperation下拉列表的信号
        if hasattr(self.parent, 'fileOperation'):
            try:
                self.parent.fileOperation.currentIndexChanged.disconnect(self.update_operation_display)
            except (TypeError, RuntimeError):
                pass
            self.parent.fileOperation.currentIndexChanged.connect(self.update_operation_display)
        
        try:
            self.log_signal.disconnect(self.handle_log_signal)
        except (TypeError, RuntimeError) as e:
            self.log("DEBUG", f"断开log_signal信号连接失败: {str(e)}")
        self.log_signal.connect(self.handle_log_signal)
        
        if hasattr(self.parent, 'btnStartSmartArrange'):
            try:
                self.parent.btnStartSmartArrange.clicked.disconnect()
            except (TypeError, RuntimeError) as e:
                pass
            
            self.parent.btnStartSmartArrange.clicked.connect(self.toggle_SmartArrange)
            
            if not self.parent.btnStartSmartArrange.isEnabled():
                self.parent.btnStartSmartArrange.setEnabled(True)
                self.log("INFO", "开始整理按钮已启用")
        else:
            self.log("ERROR", "btnStartSmartArrange button not found")

    def update_progress_bar(self, value):
        self.parent.classificationProgressBar.setValue(value)

    def toggle_SmartArrange(self):
        self.log("DEBUG", "toggle_SmartArrange")
        thread_running = bool(self.SmartArrange_thread and self.SmartArrange_thread.isRunning())
        self.log("DEBUG", f"thread_running: {thread_running}")
        if thread_running:
            self.log("INFO", "停止操作")
            self.parent.btnStartSmartArrange.setText("Stopping...")
            try:
                self.SmartArrange_thread.stop()
                self.log("DEBUG", "停止操作")
            except Exception as e:
                self.log("ERROR", f"{str(e)}")
                self.parent.btnStartSmartArrange.setText("Start Arrange")
        else:
            self.parent.btnStartSmartArrange.setEnabled(True)
            self.log("DEBUG", "start")
            
            self.selected_folders = self.folder_page.get_all_folders() if self.folder_page else []
            if not self.selected_folders:
                self.log("WARNING", "未选择文件夹")
                try:
                    QtWidgets.QMessageBox.warning(self.parent, "警告", "请先选择要整理的文件夹！")
                except Exception as e:
                    self.log("ERROR", f"显示警告消息失败: {e}")
                return
            
            self.log("DEBUG", f"folders: {len(self.selected_folders)}")
            
            if not self.destination_root:
                # 首先尝试从folder_page获取已选择的目标文件夹
                self.log("INFO", "尝试从folder_page获取目标文件夹")
                import os
                if self.folder_page and hasattr(self.folder_page, 'get_target_folder'):
                    self.log("INFO", "folder_page存在且有get_target_folder方法")
                    target_folder = self.folder_page.get_target_folder()
                    self.log("INFO", f"从folder_page获取的目标文件夹: {target_folder}")
                    if target_folder:
                        # 验证目标文件夹路径
                        destination = target_folder
                        # 验证是否有写入权限
                        if not os.access(destination, os.W_OK):
                            from PyQt6.QtWidgets import QMessageBox
                            QMessageBox.critical(self.parent, "错误", "目标文件夹没有写入权限！")
                            return
                        
                        self.destination_root = destination
                        display_path = destination + '/'
                        if len(display_path) > 20:
                            display_path = f"{display_path[:8]}...{display_path[-6:]}"
                        operation_text = "目标路径: "
                        self.parent.copyRoute.setText(f"{operation_text}{display_path}")
                    else:
                        # 如果folder_page中没有选择目标文件夹，则弹出选择对话框
                        import os
                        from PyQt6.QtWidgets import QFileDialog
                        folder = QFileDialog.getExistingDirectory(self.parent, "Select folder",
                                                                  options=QFileDialog.Option.ShowDirsOnly)
                        if not folder:
                            self.log("WARNING", "No destination")
                            return
                        
                        # 验证目标文件夹路径
                        destination = folder
                        if not os.path.exists(destination):
                            # 询问是否创建目标文件夹
                            from PyQt6.QtWidgets import QMessageBox
                            reply = QMessageBox.question(
                                self.parent,
                                "确认", 
                                f"目标文件夹不存在，是否创建？\n{destination}",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                            )
                            if reply == QMessageBox.StandardButton.Yes:
                                try:
                                    os.makedirs(destination, exist_ok=True)
                                except Exception as e:
                                    QMessageBox.critical(self.parent, "错误", f"创建目标文件夹失败：{str(e)}")
                                    return
                            else:
                                return
                        
                        # 验证是否有写入权限
                        if not os.access(destination, os.W_OK):
                            from PyQt6.QtWidgets import QMessageBox
                            QMessageBox.critical(self.parent, "错误", "目标文件夹没有写入权限！")
                            return
                        
                        self.destination_root = folder
                        display_path = folder + '/'
                        if len(display_path) > 20:
                            display_path = f"{display_path[:8]}...{display_path[-6:]}"
                        operation_text = "Destination: "
                        self.parent.copyRoute.setText(f"{operation_text}{display_path}")
                else:
                    # 如果没有folder_page或缺少get_target_folder方法，则弹出选择对话框
                    import os
                    from PyQt6.QtWidgets import QFileDialog
                    folder = QFileDialog.getExistingDirectory(self.parent, "Select folder",
                                                              options=QFileDialog.Option.ShowDirsOnly)
                    if not folder:
                        self.log("WARNING", "No destination")
                        return
                    
                    # 验证目标文件夹路径
                    destination = folder
                    if not os.path.exists(destination):
                        # 询问是否创建目标文件夹
                        from PyQt6.QtWidgets import QMessageBox
                        reply = QMessageBox.question(
                            self.parent,
                            "确认", 
                            f"目标文件夹不存在，是否创建？\n{destination}",
                            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                        )
                        if reply == QMessageBox.StandardButton.Yes:
                            try:
                                os.makedirs(destination, exist_ok=True)
                            except Exception as e:
                                QMessageBox.critical(self.parent, "错误", f"创建目标文件夹失败：{str(e)}")
                                return
                        else:
                            return
                    
                    # 验证是否有写入权限
                    if not os.access(destination, os.W_OK):
                        from PyQt6.QtWidgets import QMessageBox
                        QMessageBox.critical(self.parent, "错误", "目标文件夹没有写入权限！")
                        return
                    
                    self.destination_root = folder
                    display_path = folder + '/'
                    if len(display_path) > 20:
                        display_path = f"{display_path[:8]}...{display_path[-6:]}"
                    operation_text = "Destination: "
                    self.parent.copyRoute.setText(f"{operation_text}{display_path}")
            
            if self.SmartArrange_thread:
                try:
                    if self.SmartArrange_thread.isRunning():
                        self.SmartArrange_thread.stop()
                except Exception as e:
                    self.log("WARNING", f"{str(e)}")
                    self.SmartArrange_thread = None

            self.log("DEBUG", "confirm")
            
            # 添加局部导入以确保QMessageBox在这个作用域中可用
            from PyQt6.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self.parent,
                "确认操作?",
                "操作无法撤销!\n\n"
                "• 移动: 文件移动后，原始文件将被删除\n"
                "• 复制: 文件复制后，原始文件保留\n\n"
                "请备份重要文件!\n\n"
                "确定继续?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                self.log("INFO", "已取消")
                return

            self.log("DEBUG", "confirmed")
            
            # 确保selected_folders是列表格式，修复string indices错误
            if isinstance(self.selected_folders, str):
                self.selected_folders = [{'path': self.selected_folders, 'include_sub': 1}]
            elif not all(isinstance(f, dict) and 'path' in f for f in self.selected_folders):
                # 如果不是正确格式的字典列表，则尝试转换
                corrected_folders = []
                for folder in self.selected_folders:
                    if isinstance(folder, str):
                        corrected_folders.append({'path': folder, 'include_sub': 1})
                    elif isinstance(folder, dict) and 'path' in folder:
                        # 始终包含子文件夹，设为1
                        folder['include_sub'] = 1
                        corrected_folders.append(folder)
                self.selected_folders = corrected_folders
            else:
                # 确保所有文件夹字典都包含include_sub且值为1（始终包含子文件夹）
                for folder in self.selected_folders:
                    if isinstance(folder, dict) and 'path' in folder:
                        folder['include_sub'] = 1
            
            SmartArrange_structure = [
                getattr(self.parent, f'comboClassificationLevel{i}').currentText()
                for i in range(1, 6)
                if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
                   getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
            ]

            file_name_parts = []
            try:
                for i in range(self.selected_frame.layout().count()):
                    item = self.selected_frame.layout().itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), QtWidgets.QPushButton):
                        button = item.widget()
                        tag_name = button.text()
                        content = button.property('custom_content') if button.property('original_text') == '自定义' and button.property('custom_content') is not None else None
                        file_name_parts.append({'tag': tag_name, 'content': content})
            except Exception as e:
                self.log("ERROR", f"{str(e)}")
                file_name_parts = []

            separator_text = self.parent.fileNameSeparator.currentText()
            separator = self.separator_mapping.get(separator_text, "-")

            operation_type = self.parent.fileOperation.currentIndex()
            
            self.parent.btnStartSmartArrange.setText("停止整理")
            
            try:
                self.SmartArrange_thread = SmartArrangeThread(
                    parent=self,
                    folders=self.selected_folders,
                    classification_structure=SmartArrange_structure,
                    file_name_structure=file_name_parts,
                    destination_root=self.destination_root,
                    separator=separator,
                    time_derive="文件创建时间",
                    operation_type=operation_type
                )
                
                # 统一处理信号断开连接
                signals_to_disconnect = [
                    ('log_signal', self.handle_log_signal),
                    ('progress_signal', self.update_progress_bar),
                    ('finished', self.on_thread_finished)
                ]
                
                for signal_name, slot in signals_to_disconnect:
                    try:
                        signal = getattr(self.SmartArrange_thread, signal_name)
                        signal.disconnect(slot)
                    except (TypeError, RuntimeError) as e:
                        self.log("DEBUG", f"断开{signal_name}连接失败: {str(e)}")
                
                # 连接信号到对应的槽函数
                self.SmartArrange_thread.log_signal.connect(self.handle_log_signal)
                self.SmartArrange_thread.progress_signal.connect(self.update_progress_bar)
                self.SmartArrange_thread.finished.connect(self.on_thread_finished)
                
                self.SmartArrange_thread.start()
            except Exception as e:
                self.log("ERROR", f"{str(e)}")
                self.parent.btnStartSmartArrange.setText("开始整理")
                self.parent.btnStartSmartArrange.setEnabled(True)
                self.SmartArrange_thread = None

    def on_thread_finished(self):
        # 封装异常处理的辅助方法
        def safe_operation(operation, error_level="ERROR", message_prefix=""):
            try:
                return operation()
            except Exception as e:
                self.log(error_level, f"{message_prefix}{str(e)}")
                return None
        
        # 恢复按钮状态
        safe_operation(lambda: setattr(self.parent.btnStartSmartArrange, "setText", "开始整理")(), 
                      error_level="ERROR")
        safe_operation(lambda: setattr(self.parent.btnStartSmartArrange, "setEnabled", True)(), 
                      error_level="ERROR")
        
        # 检查是否被停止
        stopped_status = False
        if hasattr(self.SmartArrange_thread, 'is_stopped'):
            stopped_status = safe_operation(lambda: self.SmartArrange_thread.is_stopped(), 
                                           error_level="WARNING", 
                                           message_prefix="获取线程停止状态失败: ") or False
        
        # 重置进度条
        safe_operation(lambda: self.update_progress_bar(0), 
                      error_level="WARNING", 
                      message_prefix="重置进度条失败: ")
        
        # 如果不是被停止，则显示完成消息
        if not stopped_status:
            safe_operation(lambda: QMessageBox.information(self.parent, "完成", "操作已完成！"), 
                          error_level="WARNING", 
                          message_prefix="显示完成消息失败: ")
        
        # 清理线程引用
        self.SmartArrange_thread = None

    def handle_combobox_selection(self, level, index):
        self.update_combobox_state(level)

    def update_combobox_state(self, level):
        # 获取当前级别的combo box
        current_combo = getattr(self.parent, f'comboClassificationLevel{level}')
        current_text = current_combo.currentText()

        # 处理不分类的情况
        if current_text == "不分类":
            for i in range(level + 1, 6):
                combo = getattr(self.parent, f'comboClassificationLevel{i}')
                combo.setEnabled(False)
                combo.setCurrentIndex(0)
        else:
            # 启用下一级并递归更新
            if level < 5:
                next_combo = getattr(self.parent, f'comboClassificationLevel{level + 1}')
                next_combo.setEnabled(True)
                self.update_combobox_state(level + 1)

        # 收集有效的分类路径和设置
        SmartArrange_paths = []
        self.SmartArrange_settings = []
        
        for i in range(1, 6):
            combo = getattr(self.parent, f'comboClassificationLevel{i}')
            # 只处理启用且非"不分类"的选项
            if combo.isEnabled() and combo.currentText() != "不分类":
                text = combo.currentText()
                SmartArrange_paths.append(self.get_specific_value(text))
                self.SmartArrange_settings.append(text)

        # 更新预览路径
        if SmartArrange_paths:
            preview_text = "/".join(SmartArrange_paths)
        else:
            preview_text = "顶层目录（不分类）"
        
        self.parent.previewRoute.setText(preview_text)
        # 更新操作显示
        self.update_operation_display()

    def update_operation_display(self):
        has_SmartArrange = len(self.SmartArrange_settings) > 0
        has_filename = self.selected_frame.layout().count() > 0

        if has_SmartArrange and has_filename:
            operation_type = "分类并重命名"
        elif has_SmartArrange and not has_filename:
            operation_type = "仅分类"
        elif not has_SmartArrange and has_filename:
            operation_type = "仅重命名"
        else:
            operation_type = "提取到顶层目录"

        operation_mode = "复制" if self.parent.fileOperation.currentIndex() == 0 else "移动"

        if self.destination_root:
            display_path = str(self.destination_root)
            if len(display_path) > 20:
                display_path = f"{display_path[:8]}...{display_path[-6:]}"
            self.parent.copyRoute.setText(f"{operation_mode}到: {display_path} ({operation_type})")
        else:
            self.parent.copyRoute.setText(f"{operation_mode}文件 ({operation_type})")

    def set_combo_box_states(self):
        self.parent.comboClassificationLevel1.setEnabled(True)
        for i in range(2, 6):
            combo_box = getattr(self.parent, f'comboClassificationLevel{i}')
            combo_box.setEnabled(False)
            combo_box.setCurrentIndex(0)

        self.update_combobox_state(1)

    def get_specific_value(self, text):
        now = datetime.now()
        return {
            "年份": str(now.year),
            "月份": str(now.month),
            "拍摄设备": "小米",
            "相机型号": "EOS 5D Mark IV",
            "拍摄省份": "江西",
            "拍摄城市": "南昌"
        }.get(text, text)

    def is_valid_windows_filename(self, filename):
        invalid_chars = '<>:"/\\|?*'
        reserved_names = {'CON', 'PRN', 'AUX', 'NUL'}
        reserved_names.update({f'COM{i}' for i in range(1, 10)})
        reserved_names.update({f'LPT{i}' for i in range(1, 10)})
        
        return (not any(char in filename for char in invalid_chars) and
                filename not in reserved_names and
                not filename.endswith(('.', ' ')) and
                len(filename) <= 255)

    def move_tag(self, button):
        # 检查已选标签数量限制
        if self.selected_frame.layout().count() >= 5:
            return

        # 保存原始属性
        button.setProperty('original_style', button.styleSheet())
        button.setProperty('original_text', button.text())

        # 处理自定义标签
        if button.text() == '自定义':
            # 创建并配置输入对话框
            input_dialog = QInputDialog(self.parent)
            input_dialog.setWindowTitle("自定义标签")
            input_dialog.setLabelText("请输入自定义部分的文件名内容:")
            input_dialog.setTextEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            input_dialog.setTextValue("")
            
            # 设置最大长度限制
            line_edit = input_dialog.findChild(QtWidgets.QLineEdit)
            if line_edit:
                line_edit.setMaxLength(255)

            # 显示对话框并处理结果
            if input_dialog.exec() and input_dialog.textValue():
                custom_text = input_dialog.textValue()
                
                # 验证文件名
                if not self.is_valid_windows_filename(custom_text):
                    QMessageBox.warning(self.parent, "文件名无效", 
                                      f"文件名 '{custom_text}' 不符合Windows命名规范，请修改后重试。")
                    return

                # 设置显示文本和自定义内容
                display_text = custom_text[:3] if len(custom_text) > 3 else custom_text
                button.setText(display_text)
                button.setProperty('custom_content', custom_text)
            else:
                return  # 用户取消操作

        # 移动按钮从可用区域到已选区域
        self.available_frame.layout().removeWidget(button)
        self.selected_frame.layout().addWidget(button)
        button.hide()
        button.show()

        # 更新按钮连接的槽函数
        button.clicked.disconnect()
        button.clicked.connect(lambda checked, b=button: self.move_tag_back(b))

        # 更新UI显示
        self.update_example_label()
        self.update_operation_display()

        # 当已选满5个标签时，禁用剩余可用标签
        if self.selected_frame.layout().count() >= 5:
            for btn in self.tag_buttons.values():
                if btn.parent() == self.available_frame:
                    btn.setEnabled(False)

    def update_example_label(self):
        now = datetime.now()
        selected_buttons = [self.selected_frame.layout().itemAt(i).widget() for i in range(self.selected_frame.layout().count())
                            if isinstance(self.selected_frame.layout().itemAt(i).widget(), QtWidgets.QPushButton)]
        current_separator = self.separator_mapping.get(self.parent.fileNameSeparator.currentText(), "")

        example_parts = []
        for button in selected_buttons:
            button_text = button.text()
            if button.property('original_text') == '自定义' and button.property('custom_content') is not None:
                custom_content = button.property('custom_content')
                example_parts.append(custom_content[:3] if len(custom_content) > 3 else custom_content)
            else:
                parts = {
                    "原名": "IMG_1234",
                    "年份": f"{now.year}",
                    "月份": f"{now.month:02d}",
                    "日": f"{now.day:02d}",
                    "星期": f"{self._get_weekday(now)}",
                    "时间": f"{now.strftime('%H%M%S')}",
                    "品牌": "佳能",
                    "型号": "EOS 5D Mark IV",
                    "位置": "浙大"
                }
                example_parts.append(parts.get(button_text, button_text))

        example_text = current_separator.join(example_parts) if example_parts else "请点击标签以组成文件名"
        self.parent.previewName.setText(example_text)

    @staticmethod
    def _get_weekday(date):
        return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]

    def handle_log_signal(self, level, message):
        """处理日志信号"""
        # 过滤英文日志，只保留包含中文的日志
        message_str = str(message)
        if not any('\u4e00' <= char <= '\u9fff' for char in message_str):
            return
            
        log_component = self.parent.txtSmartArrangeLog if hasattr(self.parent, 'txtSmartArrangeLog') else None
        
        # 格式化消息 - 检查是否已包含时间戳
        if "[" in message_str and "]" in message_str and len(message_str) > 20:
            final_message = message_str
        else:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            final_message = f"[{timestamp}] {level}: {message_str}"
        
        # 定义日志颜色映射
        color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD', 'DEBUG': '#006400'}
        color = color_map.get(level, '#006400')
            
        # 显示日志
        if log_component:
            try:
                # 添加HTML样式以增强可读性
                log_component.append(
                    f'<div style="margin: 2px 0; padding: 2px 4px; border-left: 3px solid {color};">'  \
                    f'<span style="color:{color};">{final_message}</span>'  \
                    f'</div>'
                )
            except Exception as e:
                print(f"无法写入整理日志: {e}")
        else:
            # 控制台输出
            print(final_message)
            # 尝试调用父组件的log方法
            if hasattr(self.parent, 'log'):
                try:
                    self.parent.log(level, message_str)
                except Exception as e:
                    print(f"调用父组件log方法失败: {str(e)}")

    def log(self, level, message):
        try:
            self.log_signal.emit(level, message)
        except Exception:
            print(message)

    def move_tag_back(self, button):
        self.selected_frame.layout().removeWidget(button)
        self.available_frame.layout().addWidget(button)
        button.show()

        if button.property('original_style') is not None:
            button.setStyleSheet(button.property('original_style'))

        if button.property('original_text') is not None:
            button.setText(button.property('original_text'))

        button.clicked.disconnect()
        button.clicked.connect(lambda checked, b=button: self.move_tag(b))

        self.update_example_label()
        self.update_operation_display()

        for btn in self.tag_buttons.values():
            btn.setEnabled(True)