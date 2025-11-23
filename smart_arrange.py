from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6 import QtWidgets
from smart_arrange_thread import SmartArrangeThread

class SmartArrangeManager(QObject):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.last_selected_button_index = -1
        self.destination_root = None

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
        try:
            self.log_signal.disconnect(self.handle_log_signal)
        except (TypeError, RuntimeError):
            pass
        self.log_signal.connect(self.handle_log_signal)
        
        if hasattr(self.parent, 'btnStartSmartArrange'):
            try:
                self.parent.btnStartSmartArrange.clicked.disconnect(self.toggle_SmartArrange)
            except (TypeError, RuntimeError):
                pass
            
            self.parent.btnStartSmartArrange.clicked.connect(self.toggle_SmartArrange)
            
            if not self.parent.btnStartSmartArrange.isEnabled():
                self.parent.btnStartSmartArrange.setEnabled(True)
                self.log("INFO", "Start arrange button has been enabled")
            
            self.log("INFO", "Button signal connected to toggle_SmartArrange method")
        else:
            self.log("ERROR", "btnStartSmartArrange button not found")

    def update_progress_bar(self, value):
        self.parent.progressBar_classification.setValue(value)

    def toggle_SmartArrange(self):
        self.log("DEBUG", "toggle_SmartArrange方法被调用")
        
        thread_running = self.SmartArrange_thread and self.SmartArrange_thread.isRunning()
        self.log("DEBUG", f"线程运行状态: {thread_running}")
        
        if thread_running:
            self.log("INFO", "User requested to stop smart arrange operation")
            self.parent.btnStartSmartArrange.setText("Stopping...")
            try:
                self.SmartArrange_thread.stop()
                self.log("DEBUG", "Thread stop method called")
                self.log("DEBUG", "Thread stop signal sent")
            except Exception as e:
                self.log("ERROR", f"Error stopping thread: {str(e)}")
                self.parent.btnStartSmartArrange.setText("Start Arrange")
        else:
            self.parent.btnStartSmartArrange.setEnabled(True)
            self.log("DEBUG", "准备启动新的整理任务")
            
            folders = self.folder_page.get_all_folders() if self.folder_page else []
            if not folders:
                self.log("WARNING", "Please import a folder containing files first.")
                return
            
            self.log("DEBUG", f"Retrieved {len(folders)} folders")
            
            if not self.destination_root:
                folder = QFileDialog.getExistingDirectory(self, "Please select destination folder",
                                                          options=QFileDialog.Option.ShowDirsOnly)
                if not folder:
                    self.log("WARNING", "Must select a destination folder to perform arrange operation.")
                    return
                self.destination_root = folder
                display_path = folder + '/'
                if len(display_path) > 20:
                    display_path = f"{display_path[:8]}...{display_path[-6:]}"
                operation_text = "Destination folder: "
                self.parent.copyRoute.setText(f"{operation_text}{display_path}")
            
            if self.SmartArrange_thread:
                try:
                    if self.SmartArrange_thread.isRunning():
                        self.SmartArrange_thread.stop()
                        self.log("DEBUG", "Old thread stopped")
                except Exception as e:
                    self.log("WARNING", f"Error handling old thread: {str(e)}")
                    self.SmartArrange_thread = None

            self.log("DEBUG", "Showing confirmation dialog")
            
            reply = QMessageBox.question(
                self,
                "Ready to start arrangement, confirm?",
                "Important reminder: File arrangement operations cannot be undone once started!\n\n"
                "• Move operation: Files will be moved to new location, original files will be removed\n"
                "• Copy operation: Files will be copied to new location, original files remain intact\n\n"
                "Please make sure to backup important files before starting!\n\n"
                "Are you sure you want to start arrangement?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                self.log("INFO", "You cancelled the arrangement operation")
                return

            self.log("DEBUG", "User confirmed to start arrangement operation")
            
            SmartArrange_structure = [
                getattr(self.parent, f'comboClassificationLevel{i}').currentText()
                for i in range(1, 6)
                if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
                   getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
            ]
            self.log("DEBUG", f"分类结构: {SmartArrange_structure}")

            file_name_parts = []
            try:
                for i in range(self.selected_frame.layout().count()):
                    item = self.selected_frame.layout().itemAt(i)
                    if item and item.widget() and isinstance(item.widget(), QtWidgets.QPushButton):
                        button = item.widget()
                        tag_name = button.text()
                        content = button.property('custom_content') if button.property('original_text') == '自定义' and button.property('custom_content') is not None else None
                        file_name_parts.append({'tag': tag_name, 'content': content})
                self.log("DEBUG", f"文件名结构: {file_name_parts}")
            except Exception as e:
                self.log("ERROR", f"获取文件名结构时出错: {str(e)}")
                file_name_parts = []

            separator_text = self.parent.fileNameSeparator.currentText()
            separator = self.separator_mapping.get(separator_text, "-")
            self.log("DEBUG", f"使用分隔符: '{separator}'")

            operation_type = self.parent.fileOperation.currentIndex()
            operation_text = "Move" if operation_type == 0 else "Copy"
            self.log("DEBUG", f"Operation type: {operation_type} ({operation_text})")

            operation_summary = f"Operation type: {operation_text}"
            if SmartArrange_structure:
                operation_summary += f", Classification structure: {' → '.join(SmartArrange_structure)}"
            if file_name_parts:
                filename_tags = []
                for tag_info in file_name_parts:
                    if tag_info['content'] is not None:
                        filename_tags.append(tag_info['content'])
                    else:
                        filename_tags.append(tag_info['tag'])
                operation_summary += f", Filename tags: {'+'.join(filename_tags)}"
            if self.destination_root:
                operation_summary += f", Destination path: {self.destination_root}"

            self.log("INFO", f"Summary: {operation_summary}")
            
            self.parent.btnStartSmartArrange.setText("停止整理")
            self.parent.btnStartSmartArrange.setEnabled(True)
            
            try:
                self.log("DEBUG", "创建SmartArrangeThread实例")
                self.SmartArrange_thread = SmartArrangeThread(
                    parent=self,
                    folders=folders,
                    classification_structure=SmartArrange_structure,
                    file_name_structure=file_name_parts,
                    destination_root=self.destination_root,
                    separator=separator,
                    time_derive="文件创建时间",
                    operation_type=operation_type
                )
                
                self.log("DEBUG", "连接线程信号")
                try:
                    self.SmartArrange_thread.log_signal.disconnect()
                except (TypeError, RuntimeError):
                    pass
                try:
                    self.SmartArrange_thread.progress_signal.disconnect()
                except (TypeError, RuntimeError):
                    pass
                try:
                    self.SmartArrange_thread.finished.disconnect()
                except (TypeError, RuntimeError):
                    pass
                
                self.SmartArrange_thread.log_signal.connect(self.handle_log_signal)
                self.SmartArrange_thread.progress_signal.connect(self.update_progress_bar)
                self.SmartArrange_thread.finished.connect(self.on_thread_finished)
                
                self.log("DEBUG", "启动智能整理线程")
                self.SmartArrange_thread.start()
                self.log("INFO", "智能整理线程已成功启动")
            except Exception as e:
                self.log("ERROR", f"创建或启动线程时出错: {str(e)}")
                self.parent.btnStartSmartArrange.setText("开始整理")
                self.parent.btnStartSmartArrange.setEnabled(True)
                self.SmartArrange_thread = None

    def on_thread_finished(self):
        self.log("DEBUG", "on_thread_finished方法被调用")
        
        try:
            self.parent.btnStartSmartArrange.setText("开始整理")
            self.parent.btnStartSmartArrange.setEnabled(True)
            self.log("DEBUG", "已重置按钮状态为'开始整理'并启用")
        except Exception as e:
            self.log("ERROR", f"更新按钮状态时出错: {str(e)}")
        
        stopped_status = False
        try:
            if hasattr(self.SmartArrange_thread, 'is_stopped'):
                stopped_status = self.SmartArrange_thread.is_stopped()
                if stopped_status:
                    self.log("INFO", "智能整理操作已停止")
                else:
                    self.log("INFO", "智能整理操作已完成")
            else:
                self.log("INFO", "智能整理操作已完成")
        except Exception as e:
            self.log("WARNING", f"检查线程状态时出错: {str(e)}")
        
        try:
            self.update_progress_bar(0)
            self.log("DEBUG", "已重置进度条")
        except Exception as e:
            self.log("WARNING", f"更新进度条时出错: {str(e)}")
        
        if not stopped_status:
            try:
                QMessageBox.information(self, "操作完成", "文件整理操作已完成！")
                self.log("DEBUG", "已显示完成消息框")
            except Exception as e:
                self.log("WARNING", f"显示完成消息时出错: {str(e)}")
        
        self.log("DEBUG", "清除线程引用")
        self.SmartArrange_thread = None

    def handle_combobox_selection(self, level, index):
        self.update_combobox_state(level)

    def update_combobox_state(self, level):
        current_text = getattr(self.parent, f'comboClassificationLevel{level}').currentText()

        if current_text == "不分类":
            for i in range(level + 1, 6):
                getattr(self.parent, f'comboClassificationLevel{i}').setEnabled(False)
                getattr(self.parent, f'comboClassificationLevel{i}').setCurrentIndex(0)
        else:
            if level < 5:
                getattr(self.parent, f'comboClassificationLevel{level + 1}').setEnabled(True)
                self.update_combobox_state(level + 1)

        SmartArrange_paths = [
            self.get_specific_value(getattr(self.parent, f'comboClassificationLevel{i}').currentText())
            for i in range(1, 6)
            if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
                   getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
        ]

        if SmartArrange_paths:
            preview_text = "/".join(SmartArrange_paths)
        else:
            preview_text = "顶层目录（不分类）"

        self.parent.previewRoute.setText(preview_text)

        self.SmartArrange_settings = [
            getattr(self.parent, f'comboClassificationLevel{i}').currentText()
            for i in range(1, 6)
            if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
                   getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
        ]

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

        operation_mode = "移动" if self.parent.fileOperation.currentIndex() == 0 else "复制"

        move_color = "#FF6B6B"
        copy_color = "#4ECDC4"

        if self.destination_root:
            display_path = str(self.destination_root)
            if len(display_path) > 20:
                display_path = f"{display_path[:8]}...{display_path[-6:]}"
            if operation_mode == "移动":
                self.parent.copyRoute.setText(
                    f'<span style="color:{move_color}">{operation_mode}到: {display_path} ({operation_type})</span>'
                )
            else:
                self.parent.copyRoute.setText(
                    f'<span style="color:{copy_color}">{operation_mode}到: {display_path} ({operation_type})</span>'
                )
        else:
            if operation_mode == "移动":
                self.parent.copyRoute.setText(
                    f'<span style="color:{move_color}">{operation_mode}文件 ({operation_type})</span>'
                )
            else:
                self.parent.copyRoute.setText(
                    f'<span style="color:{copy_color}">{operation_mode}文件 ({operation_type})</span>'
                )

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
        if self.selected_frame.layout().count() >= 5:
            return

        original_style = button.styleSheet()
        button.setProperty('original_style', original_style)

        original_text = button.text()
        button.setProperty('original_text', original_text)

        if original_text == '自定义':
            input_dialog = QInputDialog(self)
            input_dialog.setWindowTitle("自定义标签")
            input_dialog.setLabelText("请输入自定义部分的文件名内容:")
            input_dialog.setTextEchoMode(QtWidgets.QLineEdit.EchoMode.Normal)
            input_dialog.setTextValue("")
            input_dialog.findChild(QtWidgets.QLineEdit).setMaxLength(255)

            ok = input_dialog.exec()
            custom_text = input_dialog.textValue()

            if ok and custom_text:
                if not self.is_valid_windows_filename(custom_text):
                    QMessageBox.warning(self, "文件名无效", f"文件名 '{custom_text}' 不符合Windows命名规范，请修改后重试。")
                    return

                display_text = custom_text[:3] if len(custom_text) > 3 else custom_text
                button.setText(display_text)
                button.setProperty('custom_content', custom_text)
            else:
                return

        self.available_frame.layout().removeWidget(button)
        button.hide()

        self.selected_frame.layout().addWidget(button)
        button.show()

        button.clicked.disconnect()
        button.clicked.connect(lambda checked, b=button: self.move_tag_back(b))

        self.update_example_label()

        self.update_operation_display()

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
        if hasattr(self.parent, 'txtSmartArrangeLog'):
            color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD'}
            color = color_map.get(level, '#006400')
            
            # 添加时间戳到日志消息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            try:
                self.parent.txtSmartArrangeLog.append(f'<span style="color:{color}">{formatted_message}</span>')
            except Exception as e:
                print(f"无法写入日志: {e}")
        else:
            print(f"[{level}] {message}")

    def log(self, level, message):
        log_message = f"[{level}] {message}"
        try:
            self.log_signal.emit(level, log_message)
        except Exception:
            print(log_message)
            pass

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