from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QFileDialog

class SmartArrangePage(QtWidgets.QWidget):
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
        self.log("INFO", "欢迎使用智能整理，可以为您整理目录、重命名媒体。请注意，操作一旦执行将无法恢复。")

    def init_page(self):
        self.connect_signals()

        for i in range(1, 6):
            getattr(self.parent, f'comboClassificationLevel{i}').currentIndexChanged.connect(
                lambda index, level=i: self.handle_combobox_selection(level, index))

        for button in self.tag_buttons.values():
            button.clicked.connect(lambda checked, b=button: self.move_tag(b))

        self.parent.fileOperation.currentIndexChanged.connect(self.handle_operation_change)
        self.parent.fileNameSeparator.currentIndexChanged.connect(self.update_example_label)

    def connect_signals(self):
        self.parent.btnStartSmartArrange.clicked.connect(self.toggle_SmartArrange)

    def update_progress_bar(self, value):
        self.parent.progressBar_classification.setValue(value)

    def handle_operation_change(self, index):
        if index == 1:
            folder = QFileDialog.getExistingDirectory(self, "选择复制目标文件夹",
                                                      options=QFileDialog.Option.ShowDirsOnly)
            if folder:
                self.destination_root = folder
                display_path = folder + '/'
                if len(display_path) > 20:
                    display_path = f"{display_path[:8]}...{display_path[-6:]}"
                operation_text = "复制到: "
                self.parent.copyRoute.setText(f"{operation_text}{display_path}")
            else:
                self.parent.fileOperation.setCurrentIndex(0)
                self.destination_root = None
                self.parent.copyRoute.setText("移动文件（默认操作）")
        else:
            self.destination_root = None
            operation_text = "移动文件"
            self.parent.copyRoute.setText(f"{operation_text}")

        self.update_operation_display()

    def toggle_SmartArrange(self):
        if self.SmartArrange_thread and self.SmartArrange_thread.isRunning():
            self.SmartArrange_thread.stop()
            self.parent.btnStartSmartArrange.setText("开始整理")
            self.parent.progressBar_classification.setValue(0)
        else:
            folders = self.folder_page.get_all_folders() if self.folder_page else []
            if not folders:
                self.log("WARNING", "请先导入一个包含文件的文件夹。")
                return
            
            # 确保必须选择目标文件夹
            if not self.destination_root:
                folder = QFileDialog.getExistingDirectory(self, "请选择目标文件夹",
                                                          options=QFileDialog.Option.ShowDirsOnly)
                if not folder:
                    self.log("WARNING", "必须选择目标文件夹才能进行整理操作。")
                    return
                self.destination_root = folder
                display_path = folder + '/'
                if len(display_path) > 20:
                    display_path = f"{display_path[:8]}...{display_path[-6:]}"
                operation_text = "目标文件夹: "
                self.parent.copyRoute.setText(f"{operation_text}{display_path}")

            reply = QMessageBox.question(
                self,
                "即将开始整理，确定吗？",
                "重要提醒：整理文件的操作一旦开始就没办法恢复了！\n\n"
                "• 移动操作：文件会被搬到新位置，原来的地方就没有了\n"
                "• 复制操作：文件会在新位置创建一份，原目录文件原封不动\n\n"
                "答应我，一定要先备份好重要文件再开始！\n\n"
                "确定要开始整理吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )

            if reply != QMessageBox.StandardButton.Yes:
                self.log("INFO", "您取消了整理操作")
                return

            SmartArrange_structure = [
                getattr(self.parent, f'comboClassificationLevel{i}').currentText()
                for i in range(1, 6)
                if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
                   getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
            ]

            # 使用布局管理器的count方法而不是QFrame的count方法
            file_name_structure = [self.selected_frame.layout().itemAt(i).widget().text()
                                   for i in range(self.selected_frame.layout().count())
                                   if isinstance(self.selected_frame.layout().itemAt(i).widget(), QtWidgets.QPushButton)]

            separator_text = self.parent.fileNameSeparator.currentText()
            separator = self.separator_mapping.get(separator_text, "-")

            operation_type = self.parent.fileOperation.currentIndex()
            operation_text = "移动" if operation_type == 0 else "复制"

            # 操作类型已在后续摘要中记录，简化此处逻辑

            file_name_parts = []
            # 使用布局管理器的count方法而不是QFrame的count方法
            for i in range(self.selected_frame.layout().count()):
                button = self.selected_frame.layout().itemAt(i).widget()
                if isinstance(button, QtWidgets.QPushButton):
                    tag_name = button.text()
                    content = button.property('custom_content') if button.property('original_text') == '自定义' and button.property('custom_content') is not None else None
                    file_name_parts.append({'tag': tag_name, 'content': content})

            operation_summary = f"操作类型: {operation_text}"
            if SmartArrange_structure:
                operation_summary += f", 分类结构: {' → '.join(SmartArrange_structure)}"
            if file_name_parts:
                filename_tags = []
                for tag_info in file_name_parts:
                    if tag_info['content'] is not None:
                        filename_tags.append(tag_info['content'])
                    else:
                        filename_tags.append(tag_info['tag'])
                operation_summary += f", 文件名标签: {'+'.join(filename_tags)}"
            if self.destination_root:
                operation_summary += f", 目标路径: {self.destination_root}"

            self.log("INFO", f"摘要: {operation_summary}")
            self.parent.btnStartSmartArrange.setText("停止整理")

    def on_thread_finished(self):
        self.parent.btnStartSmartArrange.setText("开始整理")
        self.SmartArrange_thread = None
        self.update_progress_bar(100)
        QMessageBox.information(self, "操作完成", "文件整理操作已完成！")

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

        # 使用布局管理器的count方法而不是QFrame的count方法
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
        # 简化的文件名验证
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

        # 使用布局管理器移除控件
        self.available_frame.layout().removeWidget(button)
        button.hide()  # 确保控件被隐藏

        # 使用布局管理器添加控件
        self.selected_frame.layout().addWidget(button)
        button.show()  # 确保控件可见

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
        if hasattr(self.parent, 'textEdit_SmartArrange_Log'):
            color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD'}
            color = color_map.get(level, '#000000')
            self.parent.textEdit_SmartArrange_Log.append(f'<span style="color:{color}">{message}</span>')

    def log(self, level, message):
        # 移除时间戳以简化日志
        self.log_signal.emit(level, f"[{level}] {message}")

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
