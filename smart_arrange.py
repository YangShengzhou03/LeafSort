"""
智能整理页面模块

该模块定义了SmartArrangePage类，用于实现文件的智能整理和重命名功能。
包含分类结构设置、文件名标签管理、文件操作（移动/复制）等核心功能。
"""

from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QFileDialog
from smart_arrange_thread import SmartArrangeThread


class SmartArrangePage(QtWidgets.QWidget):
    """智能整理页面类"""
    
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None, folder_page=None):
        """初始化智能整理页面
        
        Args:
            parent: 父组件
            folder_page: 文件夹页面实例
        """
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.last_selected_button_index = -1
        self.destination_root = None

        # 标签按钮映射
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

        # 分隔符映射
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
        self.log("INFO", "Welcome to Smart Arrange, you can organize directories and rename media. Please note that operations cannot be undone once executed.")

    def init_page(self):
        """初始化页面UI和信号连接"""
        self.connect_signals()

        # 连接分类级别组合框信号
        for i in range(1, 6):
            getattr(self.parent, f'comboClassificationLevel{i}').currentIndexChanged.connect(
                lambda index, level=i: self.handle_combobox_selection(level, index))

        # 连接标签按钮信号
        for button in self.tag_buttons.values():
            button.clicked.connect(lambda checked, b=button: self.move_tag(b))

    def connect_signals(self):
        """连接信号和槽函数"""
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
        """更新进度条
        
        Args:
            value: 进度值 (0-100)
        """
        self.parent.progressBar_classification.setValue(value)

    def toggle_SmartArrange(self):
        """切换智能整理操作（开始/停止）"""
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
            self._start_smart_arrange()

    def _start_smart_arrange(self):
        """开始智能整理操作"""
        self.parent.btnStartSmartArrange.setEnabled(True)
        self.log("DEBUG", "准备启动新的整理任务")
        
        # 检查文件夹
        folders = self.folder_page.get_all_folders() if self.folder_page else []
        if not folders:
            self.log("WARNING", "Please import a folder containing files first.")
            return
        
        self.log("DEBUG", f"Retrieved {len(folders)} folders")
        
        # 选择目标文件夹
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
        
        # 清理旧线程
        if self.SmartArrange_thread:
            try:
                if self.SmartArrange_thread.isRunning():
                    self.SmartArrange_thread.stop()
                    self.log("DEBUG", "Old thread stopped")
            except Exception as e:
                self.log("WARNING", f"Error handling old thread: {str(e)}")
                self.SmartArrange_thread = None

        self.log("DEBUG", "Showing confirmation dialog")
        
        # 确认对话框
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
        
        # 获取分类结构
        SmartArrange_structure = [
            getattr(self.parent, f'comboClassificationLevel{i}').currentText()
            for i in range(1, 6)
            if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
               getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
        ]
        self.log("DEBUG", f"分类结构: {SmartArrange_structure}")

        # 获取文件名结构
        file_name_parts = self._get_filename_structure()
        
        # 获取分隔符
        separator_text = self.parent.fileNameSeparator.currentText()
        separator = self.separator_mapping.get(separator_text, "-")
        self.log("DEBUG", f"使用分隔符: '{separator}'")

        # 获取操作类型
        operation_type = self.parent.fileOperation.currentIndex()
        operation_text = "Move" if operation_type == 0 else "Copy"
        self.log("DEBUG", f"Operation type: {operation_type} ({operation_text})")

        # 生成操作摘要
        operation_summary = self._generate_operation_summary(
            operation_text, SmartArrange_structure, file_name_parts
        )
        self.log("INFO", f"Summary: {operation_summary}")
        
        # 启动整理线程
        self._start_arrange_thread(folders, SmartArrange_structure, file_name_parts, 
                                 separator, operation_type)

    def _get_filename_structure(self):
        """获取文件名结构
        
        Returns:
            list: 文件名标签结构列表
        """
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
        
        return file_name_parts

    def _generate_operation_summary(self, operation_text, structure, file_name_parts):
        """生成操作摘要
        
        Args:
            operation_text: 操作类型文本
            structure: 分类结构列表
            file_name_parts: 文件名标签结构
            
        Returns:
            str: 操作摘要
        """
        operation_summary = f"Operation type: {operation_text}"
        
        if structure:
            operation_summary += f", Classification structure: {' → '.join(structure)}"
        
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
        
        return operation_summary

    def _start_arrange_thread(self, folders, structure, file_name_parts, separator, operation_type):
        """启动整理线程
        
        Args:
            folders: 文件夹列表
            structure: 分类结构
            file_name_parts: 文件名标签结构
            separator: 分隔符
            operation_type: 操作类型
        """
        self.SmartArrange_thread = SmartArrangeThread(
            folders=folders,
            destination_root=self.destination_root,
            classification_structure=structure,
            file_name_parts=file_name_parts,
            separator=separator,
            operation_type=operation_type
        )
        
        self.SmartArrange_thread.progress_updated.connect(self.update_progress_bar)
        self.SmartArrange_thread.log_signal.connect(self.handle_log_signal)
        self.SmartArrange_thread.finished.connect(self._on_arrange_finished)
        
        self.parent.btnStartSmartArrange.setText("Stop Arrange")
        self.SmartArrange_thread.start()
        self.log("INFO", "Smart arrange operation started")

    def _on_arrange_finished(self):
        """整理操作完成处理"""
        self.parent.btnStartSmartArrange.setText("Start Arrange")
        self.log("INFO", "Smart arrange operation completed")

    def handle_log_signal(self, level, message):
        """处理日志信号
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        self.log(level, message)

    def log(self, level, message):
        """记录日志
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] [{level}] {message}"
        print(formatted_message)
        
        # 发送日志信号
        self.log_signal.emit(level, message)

    def handle_combobox_selection(self, level, index):
        """处理组合框选择
        
        Args:
            level: 分类级别
            index: 选择索引
        """
        # 实现组合框选择处理逻辑
        pass

    def move_tag(self, button):
        """移动标签
        
        Args:
            button: 按钮实例
        """
        # 实现标签移动逻辑
        pass

    def set_combo_box_states(self):
        """设置组合框状态"""
        # 实现组合框状态设置逻辑
        pass