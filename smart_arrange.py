from datetime import datetime
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QInputDialog, QMessageBox, QFileDialog
import os
from pathlib import Path

from smart_arrange_thread import SmartArrangeThread


class SmartArrangePage(QtWidgets.QWidget):
    log_signal = pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        # 从parent获取folder_page引用，确保与MainWindow中的初始化方式一致
        self.folder_page = None
        self.last_selected_button_index = -1
        self.destination_root = None
        
        # 初始化布局变量
        self.available_layout = None
        self.selected_layout = None
        
        # 使用正确的UI组件名称并添加属性检查
        self.tag_buttons = {}
        
        # 映射标签名称到UI组件名称
        button_mapping = {
            '原名': 'btnAddOriginalTag',
            '年份': 'btnAddYearTag',
            '月份': 'btnAddMonthTag',
            '日': 'btnAddDateTag',
            '星期': 'btnDayTag',
            '时间': 'btnAddTimeTag',
            '品牌': 'btnAddMakeTag',
            '型号': 'btnModelTag',
            '位置': 'btnAddressTag',
            '自定义': 'btnCustomizeTag'
        }
        
        # 只添加存在的属性
        for tag_name, attr_name in button_mapping.items():
            try:
                self.tag_buttons[tag_name] = getattr(self.parent, attr_name)
            except AttributeError:
                pass
        
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
        
        # 初始化布局引用
        self._initialize_layouts()
        
        # 添加布局属性检查
        self.available_layout = getattr(self.parent, 'layoutTagsInput', None)
        self.selected_layout = getattr(self.parent, 'layoutRenameContent', None)
        
        self.smart_arrange_thread = None
        self.smart_arrange_settings = []
        
        self.init_page()
        self.set_combo_box_states()
        self.log_signal.connect(self.handle_log_signal)
        self.log("INFO", "欢迎使用智能整理，可以为您整理目录、重命名媒体。请注意，操作一旦执行将无法恢复。")

    def init_page(self):
        # 从parent获取folder_page引用，确保能访问文件夹数据
        try:
            self.folder_page = self.parent.folder_page
            self.log("INFO", "成功获取文件夹页面引用")
        except AttributeError:
            self.log("WARNING", "无法获取文件夹页面引用")
        
        # 确保布局已初始化
        self._initialize_layouts()
        
        self.connect_signals()
        
        for i in range(1, 6):
            try:
                combo_box = getattr(self.parent, f'comboClassificationLevel{i}')
                combo_box.currentIndexChanged.connect(
                    lambda index, level=i: self.handle_combobox_selection(level, index))
            except AttributeError:
                pass
        
        for button in self.tag_buttons.values():
            if button:
                try:
                    button.clicked.connect(lambda checked, b=button: self.move_tag(b))
                except AttributeError:
                    pass
        
        try:
            self.parent.fileOperation.currentIndexChanged.connect(self.handle_operation_change)
        except AttributeError:
            pass
        
        try:
            self.parent.comboBox_separator.currentIndexChanged.connect(self.update_example_label)
        except AttributeError:
            pass
        
        self.log("DEBUG", "欢迎使用图像分类整理，您可在上方构建文件路径与文件名结构。")

    def connect_signals(self):
        # 检查并使用正确的按钮名称
        if hasattr(self.parent, 'btnStartSmartArrange'):
            self.parent.btnStartSmartArrange.clicked.connect(self.toggle_smart_arrange)
        elif hasattr(self.parent, 'toolButton_startSmartArrange'):
            self.parent.toolButton_startSmartArrange.clicked.connect(self.toggle_smart_arrange)
        else:
            self.log("WARNING", "未找到智能整理启动按钮，功能可能无法正常使用")

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

    def toggle_smart_arrange(self):
        """智能整理开关，简化用户交互流程"""
        if self.smart_arrange_thread and self.smart_arrange_thread.isRunning():
            # 停止操作保持不变
            self.smart_arrange_thread.stop()
            # 使用正确的按钮名称并添加属性检查
            if hasattr(self.parent, 'btnStartSmartArrange'):
                self.parent.btnStartSmartArrange.setText("开始整理")
            elif hasattr(self.parent, 'toolButton_startSmartArrange'):
                self.parent.toolButton_startSmartArrange.setText("开始整理")
            try:
                self.parent.progressBar_classification.setValue(0)
            except AttributeError:
                pass
            self._show_operation_status("整理已停止", 2000)
        else:
            folders = self.folder_page.get_all_folders() if self.folder_page else []
            if not folders:
                self.log("WARNING", "请先导入一个包含文件的文件夹。")
                self._show_operation_status("请先添加文件夹", 2500)
                return
                
            # 添加快速模式支持：如果只有一个文件夹且文件数少于100，自动跳过确认
            quick_mode = False
            if len(folders) == 1:
                folder_path = Path(folders[0]['path'])
                if folder_path.exists():
                    try:
                        if not folders[0].get('include_sub', 0):
                            file_count = len([f for f in folder_path.iterdir() if f.is_file()])
                            if file_count > 0 and file_count < 100:
                                quick_mode = True
                                self.log("INFO", f"启用快速模式：单个文件夹且文件数较少({file_count})")
                    except Exception:
                        pass
            
            # 快速模式下跳过确认，直接预检查
            if not quick_mode:
                # 快速确认流程
                if not self._quick_confirm_operation():
                    return
                
            # 智能预检查
            if not self._smart_pre_check(folders):
                return
                
            # 启动整理线程
            self._start_smart_arrange_thread(folders)

    def _quick_confirm_operation(self):
        """快速确认操作，减少用户交互"""
        operation_type = self.parent.fileOperation.currentIndex()
        operation_text = "移动" if operation_type == 0 else "复制"
        
        # 添加记住选择的选项
        try:
            # 直接尝试访问属性，如果不存在会抛出AttributeError
            _ = self._remember_operation
        except AttributeError:
            self._remember_operation = False
        
        # 如果用户选择了记住操作，则跳过确认
        if self._remember_operation:
            self.log("INFO", f"自动确认{operation_text}操作（用户已选择记住此设置）")
            return True
        
        # 获取文件夹信息用于生成准确的确认信息
        folders = self.folder_page.get_all_folders() if self.folder_page else []
        folder_paths = [folder_info['path'] for folder_info in folders]
        
        # 智能生成简洁确认信息
        confirm_message = self._generate_smart_confirmation(operation_type, folder_paths)
        
        # 创建自定义对话框以支持记住选择选项
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"开始{operation_text}整理")
        msg_box.setText(confirm_message)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
        
        # 添加复选框
        remember_checkbox = QtWidgets.QCheckBox("记住此操作，下次不再提示", self)
        msg_box.setCheckBox(remember_checkbox)
        
        reply = msg_box.exec()
        
        # 保存用户的记住选择
        if remember_checkbox.isChecked():
            self._remember_operation = True
            self.log("INFO", "用户已选择记住操作设置")
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log("INFO", "用户取消整理操作")
            return False
        return True
        
    def _smart_pre_check(self, folders):
        """智能预检查，简化检查流程"""
        try:
            # 检查文件夹是否为空
            if not folders:
                self.log("WARNING", "未选择文件夹")
                self._show_operation_status("请先添加文件夹", 2000)
                return False
            
            # 快速检查文件数量
            total_files = 0
            has_valid_folder = False
            
            for folder_info in folders:
                try:
                    folder_path = Path(folder_info['path'])
                    if folder_path.exists():
                        has_valid_folder = True
                        if folder_info.get('include_sub', 0):
                            # 使用生成器表达式优化大文件夹性能
                            for root, _, files in os.walk(folder_path):
                                total_files += len(files)
                                # 如果文件数量过多，不再继续计数以提高性能
                                if total_files > 10000:
                                    break
                        else:
                            # 如果不包含子文件夹，直接列出文件夹中的文件
                            try:
                                files = [f for f in folder_path.iterdir() if f.is_file()]
                                total_files += len(files)
                            except PermissionError:
                                self.log("WARNING", f"无权限访问文件夹: {folder_path}")
                        if total_files > 10000:
                            break
                except Exception:
                    # 忽略文件夹处理中的异常
                    pass
            
            # 简化检查结果处理
            if not has_valid_folder:
                self.log("WARNING", "所有文件夹路径无效")
                self._show_operation_status("文件夹路径无效", 2000)
                return False
                
            if total_files == 0:
                self.log("WARNING", "未检测到文件")
                self._show_operation_status("文件夹中没有文件", 2000)
                return False
            
            # 优化大量文件的处理
            if total_files > 10000:
                self.log("WARNING", f"检测到大量文件({total_files}+)，可能需要较长时间")
                # 对于大量文件，默认跳过详细确认，只显示提示
                self._show_operation_status(f"开始处理大量文件...", 2000)
            
            # 检查目标路径，使用更简洁的错误处理
            if self.parent.lineEdit_destination.text():
                dest_path = Path(self.parent.lineEdit_destination.text())
                try:
                    dest_path.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    self.log("ERROR", f"无法创建目标文件夹: {str(e)}")
                    self._show_operation_status("目标文件夹创建失败", 2500)
                    return False
                    
            return True
            
        except Exception as e:
            self.log("ERROR", f"预检查失败: {str(e)}")
            self._show_operation_status(f"检查失败: {str(e)}", 3000)
            return False
            
    def _start_smart_arrange_thread(self, folders):
        """启动智能整理线程"""
        # 构建分类结构
        classification_structure = [
            getattr(self.parent, f'comboClassificationLevel{i}').currentText()
            for i in range(1, 6)
            if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
               getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
        ]

        # 获取用户选择的标签结构，严格按照用户点击顺序
        file_name_structure = []
        
        # 遍历layout中的所有项目，确保按添加顺序获取（即用户点击顺序）
        for i in range(self.selected_layout.count()):
            widget = self.selected_layout.itemAt(i).widget()
            if isinstance(widget, QtWidgets.QPushButton):
                original_text = widget.property('original_text') or widget.text()
                
                if original_text == '自定义' and widget.property('custom_content') is not None:
                    file_name_structure.append({
                        'tag': original_text,
                        'content': widget.property('custom_content')
                    })
                else:
                    # 使用标签的原始文本而不是显示文本，确保一致性
                    file_name_structure.append({
                        'tag': original_text,
                        'content': None
                    })

        # 记录日志，确认文件名结构顺序
        self.log("INFO", f"文件名结构（按点击顺序）: {file_name_structure}")
        
        separator_text = self.parent.comboBox_separator.currentText()
        separator = self.separator_mapping.get(separator_text, "-")
        
        operation_type = self.parent.fileOperation.currentIndex()
        operation_text = "移动" if operation_type == 0 else "复制"
        
        if not classification_structure and not file_name_structure:
            self.log("WARNING", f"执行{operation_text}操作：将文件夹中的所有文件提取到顶层目录")
        elif not classification_structure:
            self.log("WARNING", f"执行{operation_text}操作：仅重命名文件，不进行分类")
        elif not file_name_structure:
            self.log("WARNING", f"执行{operation_text}操作：仅进行分类，不重命名文件")
        else:
            self.log("WARNING", f"执行{operation_text}操作：进行分类和重命名")
        
        operation_summary = f"操作类型: {operation_text}"
        if classification_structure:
            operation_summary += f", 分类结构: {' → '.join(classification_structure)}"
        if file_name_structure:
            filename_tags = []
            for tag_info in file_name_structure:
                if tag_info['content'] is not None:
                    filename_tags.append(tag_info['content'])
                else:
                    filename_tags.append(tag_info['tag'])
            operation_summary += f", 文件名标签: {'+'.join(filename_tags)}"
        if self.destination_root:
            operation_summary += f", 目标路径: {self.destination_root}"
        
        self.log("INFO", f"摘要: {operation_summary}")
        
        self.smart_arrange_thread = SmartArrangeThread(
            parent=self,
            folders=folders,
            classification_structure=classification_structure or None,
            file_name_structure=file_name_structure or None,
            destination_root=self.destination_root,
            separator=separator,
            time_derive=self.parent.comboBox_timeSource.currentText()
        )
        self.smart_arrange_thread.finished.connect(self.on_thread_finished)
        self.smart_arrange_thread.progress_signal.connect(self.update_progress_bar)
        self.smart_arrange_thread.start()
        # 使用正确的按钮名称并添加属性检查
        try:
            self.parent.btnStartSmartArrange.setText("停止整理")
        except AttributeError:
            try:
                self.parent.toolButton_startSmartArrange.setText("停止整理")
            except AttributeError:
                pass
        self._show_operation_status("开始整理文件...", 1500)

    def on_thread_finished(self):
        """线程结束处理，优化通知机制"""
        # 使用正确的按钮名称并添加属性检查
        try:
            self.parent.btnStartSmartArrange.setText("开始整理")
        except AttributeError:
            try:
                self.parent.toolButton_startSmartArrange.setText("开始整理")
            except AttributeError:
                pass
        
        # 获取线程结果信息
        error_msg = None
        success_count = 0
        fail_count = 0
        
        if self.smart_arrange_thread:
            if hasattr(self.smart_arrange_thread, 'error') and self.smart_arrange_thread.error:
                error_msg = str(self.smart_arrange_thread.error)
            # 获取处理统计信息
            if hasattr(self.smart_arrange_thread, 'stats'):
                stats = self.smart_arrange_thread.stats
                success_count = stats.get('success', 0)
                fail_count = stats.get('fail', 0)
        
        self.smart_arrange_thread = None
        self.update_progress_bar(100)
        
        if error_msg:
            # 错误处理保持不变
            self.log("ERROR", f"整理过程中发生错误: {error_msg}")
            QMessageBox.critical(self, "整理失败", f"操作失败: {error_msg}")
            self._show_operation_status("整理失败", 3000)
        else:
            # 优化成功提示，提供更多信息
            self.log("INFO", "整理完成")
            
            # 生成更详细的成功消息
            success_message = f"文件整理成功！"
            if success_count > 0:
                success_message += f"\n成功处理: {success_count} 个文件"
            if fail_count > 0:
                success_message += f"\n\n注意: 有 {fail_count} 个文件处理失败，请查看日志获取详细信息"
            
            # 为大量文件操作提供简化通知选项
            if success_count > 100:
                # 使用非模态通知，不阻塞用户继续操作
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("整理完成")
                msg_box.setText(success_message)
                msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                msg_box.setIcon(QMessageBox.Icon.Information)
                msg_box.setModal(False)
                msg_box.show()
            else:
                # 小批量操作使用传统消息框
                QMessageBox.information(self, "整理完成", success_message)
                
            self._show_operation_status("整理完成", 2000)

    def handle_combobox_selection(self, level, index):
        """处理下拉框选择事件"""
        self.update_combobox_state(level)

    def _generate_smart_confirmation(self, operation_type, folders):
        """智能生成确认信息，优化用户体验"""
        # 统计文件信息（使用更高效的方式）
        total_files = 0
        processed_folders = 0
        
        for folder in folders:
            if os.path.exists(folder):
                processed_folders += 1
                # 只统计顶层文件以提高速度，避免大量文件时的性能问题
                try:
                    files = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
                    total_files += len(files)
                    # 限制计数以提高性能
                    if total_files > 1000:
                        break
                except PermissionError:
                    pass
        
        operation_text = "移动" if operation_type == 0 else "复制"
        
        # 获取操作摘要
        has_classification = any(getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类" 
                                for i in range(1, 6) if hasattr(self.parent, f'comboClassificationLevel{i}'))
        has_rename = self.selected_layout.count() > 0
        
        # 生成操作类型描述
        action_desc = []
        if has_classification:
            action_desc.append("分类")
        if has_rename:
            action_desc.append("重命名")
        action_text = "和".join(action_desc) if action_desc else "处理"
        
        # 生成更简洁、更明确的确认信息
        if total_files == 0:
            return f"即将{operation_text}文件并进行{action_text}，但当前未检测到文件。请确认继续？"
        elif total_files == 1:
            return f"即将{operation_text}1个文件并进行{action_text}。\n\n确认继续？"
        elif total_files > 1000:
            # 对于大量文件，提供更简洁的信息
            return f"即将{operation_text}大量文件（超过1000个）并进行{action_text}。\n\n此操作可能需要较长时间，确认继续？"
        else:
            # 对于普通数量的文件，提供详细信息
            info_parts = [f"即将{operation_text}{total_files}个文件并进行{action_text}"]
            
            # 添加分类信息
            if has_classification:
                classification_levels = []
                for i in range(1, 6):
                    if hasattr(self.parent, f'comboClassificationLevel{i}'):
                        level_text = getattr(self.parent, f'comboClassificationLevel{i}').currentText()
                        if level_text != "不分类":
                            classification_levels.append(self.get_specific_value(level_text))
                if classification_levels:
                    info_parts.append(f"分类路径: {'/'.join(classification_levels)}")
            
            # 添加重命名信息
            if has_rename:
                tag_count = self.selected_layout.count()
                info_parts.append(f"将添加{tag_count}个标签到文件名")
            
            # 添加目标信息
            if operation_type == 1 and self.destination_root:
                display_path = self.destination_root
                if len(display_path) > 40:
                    display_path = f"{display_path[:20]}...{display_path[-15:]}"
                info_parts.append(f"目标位置: {display_path}")
            
            return "\n".join(info_parts) + "\n\n确认继续？"

    def update_combobox_state(self, level):
        # 检查comboClassificationLevel{level}属性是否存在
        try:
            # 尝试获取属性
            combo_box = getattr(self.parent, f'comboClassificationLevel{level}')
        except AttributeError:
            # 属性不存在时记录日志并返回
            try:
                if hasattr(self.parent, 'log'):
                    self.parent.log.info(f'comboClassificationLevel{level}属性不存在，跳过组合框状态更新')
                elif hasattr(self.parent, 'logger'):
                    self.parent.logger.info(f'comboClassificationLevel{level}属性不存在，跳过组合框状态更新')
            except Exception:
                pass
            return
        
        current_text = getattr(self.parent, f'comboClassificationLevel{level}').currentText()
        
        if current_text == "不分类":
            for i in range(level + 1, 6):
                if hasattr(self.parent, f'comboClassificationLevel{i}'):
                    getattr(self.parent, f'comboClassificationLevel{i}').setEnabled(False)
                    getattr(self.parent, f'comboClassificationLevel{i}').setCurrentIndex(0)
        else:
            if level < 5 and hasattr(self.parent, f'comboClassificationLevel{level + 1}'):
                getattr(self.parent, f'comboClassificationLevel{level + 1}').setEnabled(True)
                self.update_combobox_state(level + 1)
        
        # 安全地收集SmartArrange路径
        SmartArrange_paths = []
        for i in range(1, 6):
            if hasattr(self.parent, f'comboClassificationLevel{i}'):
                combo_box = getattr(self.parent, f'comboClassificationLevel{i}')
                if combo_box.isEnabled() and combo_box.currentText() != "不分类":
                    SmartArrange_paths.append(self.get_specific_value(combo_box.currentText()))
        
        if SmartArrange_paths:
            preview_text = "/".join(SmartArrange_paths)
        else:
            preview_text = "顶层目录（不分类）"
        
        # 使用正确的标签名称
        self.parent.previewRoute.setText(preview_text)
        
        self.SmartArrange_settings = [
            getattr(self.parent, f'comboClassificationLevel{i}').currentText()
            for i in range(1, 6)
            if getattr(self.parent, f'comboClassificationLevel{i}').isEnabled() and
               getattr(self.parent, f'comboClassificationLevel{i}').currentText() != "不分类"
        ]
        
        self.update_operation_display()
    
    def update_operation_display(self):
        # 获取选择的标签数量
        selected_tags_count = self.selected_layout.count()
        
        has_SmartArrange = len(self.SmartArrange_settings) > 0
        
        has_filename = selected_tags_count > 0
        
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
        # 检查comboClassificationLevel1属性是否存在
        try:
            self.parent.comboClassificationLevel1.setEnabled(True)
            # 尝试设置其他级别的组合框状态
            for i in range(2, 6):
                try:
                    combo_box = getattr(self.parent, f'comboClassificationLevel{i}', None)
                    if combo_box:
                        combo_box.setEnabled(False)
                        combo_box.setCurrentIndex(0)
                except Exception:
                    continue
            
            self.update_combobox_state(1)
        except AttributeError:
            # 记录日志，说明组合框不存在
            try:
                if hasattr(self.parent, 'log'):
                    self.parent.log('INFO', 'comboClassificationLevel1属性不存在，跳过组合框状态设置')
                elif hasattr(self.parent, 'logger'):
                    self.parent.logger.info('comboClassificationLevel1属性不存在，跳过组合框状态设置')
            except Exception:
                pass

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
        if any(char in filename for char in invalid_chars):
            return False
        if filename in ('CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9', 'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9'):
            return False
        if filename.endswith('.') or filename.endswith(' '):
            return False
        if len(filename) > 255:
            return False
        return True
    
    def move_tag(self, button):
        # 确保布局存在
        if not self.available_layout or not self.selected_layout:
            self.log("ERROR", "布局组件不存在，无法移动标签")
            return
            
        # 确保按钮是有效的标签按钮
        if button not in self.tag_buttons.values():
            return
        
        # 限制最多选择5个标签
        if self.selected_layout.count() >= 5:
            QMessageBox.information(self, "提示", "最多只能选择5个标签")
            return
        
        # 保存按钮的原始样式
        original_style = button.styleSheet()
        button.setProperty('original_style', original_style)
        
        # 保存按钮的原始文本
        original_text = button.text()
        button.setProperty('original_text', original_text)
        
        # 处理自定义标签
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
                    QMessageBox.warning(
                        self,
                        "文件名无效",
                        f"输入的文件名 '{custom_text}' 不符合Windows命名规范！\n\n"
                        "不允许的字符"
                        "不能使用保留文件名: CON, PRN, AUX, NUL, COM1-9, LPT1-9\n"
                        "不能以点(.)或空格结尾\n"
                        "长度不能超过255个字符\n\n"
                        "请修改后重试。"
                    )
                    return
                
                # 显示简短版本，但保存完整内容
                display_text = custom_text[:3] if len(custom_text) > 3 else custom_text
                button.setText(display_text)
                button.setProperty('custom_content', custom_text)
            else:
                return
        
        try:
            # 从待选区域移除
            self.available_layout.removeWidget(button)
            
            # 添加到已选区域（按点击顺序）
            self.selected_layout.addWidget(button)
            
            # 更改按钮的点击事件处理函数
            try:
                button.clicked.disconnect()
            except TypeError:
                pass  # 如果没有连接的信号，忽略错误
            button.clicked.connect(lambda checked, b=button: self.move_tag_back(b))
            
            # 更新示例和操作显示
            self.update_example_label()
            self.update_operation_display()
            
            # 如果已选满5个标签，禁用剩余的可用标签
            if self.selected_layout.count() >= 5:
                for btn in self.tag_buttons.values():
                    if btn.parent() == self.available_layout:
                        btn.setEnabled(False)
        except Exception as e:
            self.log("ERROR", f"移动标签时出错: {str(e)}")
    
    def _get_weekday(self, date):
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        return weekdays[date.weekday()]
    
    def update_example_label(self):
        now = datetime.now()
        current_separator = self.separator_mapping.get(self.parent.comboBox_separator.currentText(), "-")
        
        example_parts = []
        # 严格按照布局中的顺序获取标签，确保与用户点击顺序一致
        for i in range(self.selected_layout.count()):
            try:
                widget = self.selected_layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QPushButton):
                    # 获取原始标签名（而不是显示的截断文本）
                    original_text = widget.property('original_text') or widget.text()
                    
                    # 处理自定义标签的特殊情况
                    if original_text == '自定义':
                        custom_content = widget.property('custom_content')
                        if custom_content is not None:
                            # 使用完整的自定义内容作为示例，更好地展示实际效果
                            example_parts.append(custom_content)
                        else:
                            example_parts.append("自定义内容")
                    else:
                        # 根据原始标签名获取对应的示例文本
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
                        # 使用get方法避免KeyError，并提供默认值
                        example_parts.append(parts.get(original_text, original_text))
            except Exception as e:
                # 添加错误处理，确保即使出现异常也不会影响整个功能
                self.log("WARNING", f"更新文件名预览时出错: {str(e)}")
        
        # 过滤掉空部分，确保文件名预览不会出现多余的分隔符
        example_parts = [part for part in example_parts if part]
        
        # 使用分隔符连接各部分，生成最终的示例文本
        example_text = current_separator.join(example_parts) if example_parts else "请点击标签以组成文件名"
        
        # 确保预览文本在UI中正确显示
        if hasattr(self.parent, 'label_PreviewName'):
            self.parent.label_PreviewName.setText(example_text)

    @staticmethod
    def _get_weekday(date):
        return ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][date.weekday()]

    def handle_log_signal(self, level, message):
        # 检查并使用正确的日志输出控件
        try:
            color_map = {
                'ERROR': '#FF0000',
                'WARNING': '#FFA500',
                'DEBUG': '#008000',
                'INFO': '#8677FD'
            }
            color = color_map.get(level, '#000000')
            self.parent.smartArrangeLogOutputTextEdit.append(
                f'<span style="color:{color}">{message}</span>')
        except AttributeError:
            try:
                color_map = {
                    'ERROR': '#FF0000',
                    'WARNING': '#FFA500',
                    'DEBUG': '#008000',
                    'INFO': '#8677FD'
                }
                color = color_map.get(level, '#000000')
                self.parent.textEdit_SmartArrange_Log.append(
                    f'<span style="color:{color}">{message}</span>')
            except AttributeError:
                print(f"[{level}] {message}")  # 降级到控制台输出
    
    def _show_operation_status(self, message, duration=1500):
        try:
            # 尝试使用父组件的show_status_message方法
            self.parent.show_status_message(message, duration)
        except AttributeError:
            # 如果父组件没有该方法，记录日志
            self.log("INFO", message)
        except Exception as e:
            # 出错时降级到日志记录
            self.log("WARNING", f"无法显示状态消息: {str(e)}")
    
    def log(self, level, message):
        current_time = datetime.now().strftime('%H:%M:%S')
        formatted_message = f"[{current_time}] [{level}] {message}"
        
        # 直接使用信号发送日志
        try:
            # 发送原始级别和格式化后的消息
            self.log_signal.emit(level, formatted_message)
        except Exception as e:
            # 改进异常处理，提供更详细的错误信息
            print(f"日志发送失败: {str(e)}")
            print(formatted_message)  # 降级到控制台输出

    def move_tag_back(self, button):
        # 确保布局存在
        if not self.available_layout or not self.selected_layout:
            self.log("ERROR", "布局组件不存在，无法移动标签")
            return
            
        try:
            # 从已选区域移除
            self.selected_layout.removeWidget(button)
            
            # 添加回待选区域
            self.available_layout.addWidget(button)
            
            # 恢复原始样式
            if button.property('original_style') is not None:
                # 直接应用样式，不再捕获异常
                button.setStyleSheet(button.property('original_style'))
            
            # 恢复原始文本
            if button.property('original_text') is not None:
                button.setText(button.property('original_text'))
            
            # 清除自定义内容属性
            button.setProperty('custom_content', None)
            
            # 更改按钮的点击事件处理函数
            # 直接连接新的信号处理函数，PyQt会自动断开之前的连接
            button.clicked.connect(lambda checked, b=button: self.move_tag(b))
            
            # 更新示例和操作显示
            self.update_example_label()
            self.update_operation_display()
            
            # 重新启用所有可用标签
            for btn in self.tag_buttons.values():
                if btn.parent() == self.available_layout:
                    btn.setEnabled(True)
        except Exception as e:
            self.log("ERROR", f"将标签移回时出错: {str(e)}")
                
    def _initialize_layouts(self):
        """初始化布局组件引用"""
        # 首先检查是否能直接获取布局
        self.available_layout = getattr(self.parent, 'layoutTagsInput', None)
        self.selected_layout = getattr(self.parent, 'layoutRenameContent', None)
        
        # 如果直接获取失败，尝试通过父框架获取
        try:
            if not self.available_layout and getattr(self.parent, 'frameRenameTags', None):
                frame = getattr(self.parent, 'frameRenameTags')
                # 在frame中查找layout属性
                for attr_name in dir(frame):
                    if attr_name.startswith('_'):
                        continue
                    attr_value = getattr(frame, attr_name)
                    if str(type(attr_value)).find('QHBoxLayout') >= 0:
                        self.available_layout = attr_value
                        self.log("INFO", f"通过frameRenameTags获取布局组件: {attr_name}")
                        break
        except Exception:
            # 忽略获取布局组件时的异常
            pass

        if not self.selected_layout and hasattr(self.parent, 'frameRename'):
            frame = getattr(self.parent, 'frameRename')
            # 在frame中查找layout属性
            for attr_name in dir(frame):
                if attr_name.startswith('_'):
                    continue
                attr_value = getattr(frame, attr_name)
                if str(type(attr_value)).find('QHBoxLayout') >= 0:
                    self.selected_layout = attr_value
                    self.log("INFO", f"通过frameRename获取布局组件: {attr_name}")
                    break
        
        if self.available_layout and self.selected_layout:
            self.log("INFO", "已成功获取布局组件引用")
        else:
            self.log("WARNING", f"无法获取所有布局组件: available={bool(self.available_layout)}, selected={bool(self.selected_layout)}")
    
    def refresh(self):
        """刷新智能整理页面"""
        try:
            self.log("INFO", "正在刷新智能整理页面")
            
            # 重置状态
            self._reset_state()
            
            # 重新检查文件夹页面引用
            try:
                self.folder_page = self.parent.folder_page
                self.log("INFO", "已重新获取文件夹页面引用")
            except AttributeError:
                pass
                
            # 重新初始化布局引用
            self._initialize_layouts()
                
            # 重新获取标签按钮引用
            button_mapping = {
                '原名': 'btnAddOriginalTag',
                '年份': 'btnAddYearTag',
                '月份': 'btnAddMonthTag',
                '日': 'btnAddDateTag',
                '星期': 'btnDayTag',
                '时间': 'btnAddTimeTag',
                '品牌': 'btnAddMakeTag',
                '型号': 'btnModelTag',
                '位置': 'btnAddressTag',
                '自定义': 'btnCustomizeTag'
            }
            
            # 清空并重新填充tag_buttons字典
            self.tag_buttons.clear()
            for tag_name, attr_name in button_mapping.items():
                if hasattr(self.parent, attr_name):
                    button = getattr(self.parent, attr_name)
                    self.tag_buttons[tag_name] = button
                    # 确保按钮与move_tag方法连接
                    if button and hasattr(button, 'clicked'):
                        # 断开现有连接以避免重复连接
                        try:
                            button.clicked.disconnect(self.move_tag)
                        except (TypeError, RuntimeError):
                            pass  # 忽略未连接的错误
                        button.clicked.connect(lambda checked, b=button: self.move_tag(b))
            
            # 重置组合框状态
            self.set_combo_box_states()
            self.log("INFO", "智能整理页面刷新完成")
            
            # 清除所有已选标签并恢复到可用区域
            selected_buttons = []
            for i in range(self.selected_layout.count()):
                widget = self.selected_layout.itemAt(i).widget()
                if isinstance(widget, QtWidgets.QPushButton):
                    selected_buttons.append(widget)
            
            for button in selected_buttons:
                self.move_tag_back(button)
                
            self.log("INFO", "智能整理页面刷新完成")
        except Exception as e:
            self.log("ERROR", f"刷新智能整理页面时出错: {str(e)}")
    
    def _reset_state(self):
        """重置页面状态"""
        try:
            # 停止正在运行的线程
            if hasattr(self, 'smart_arrange_thread') and self.smart_arrange_thread and self.smart_arrange_thread.isRunning():
                self.smart_arrange_thread.stop()
                self.smart_arrange_thread = None
            
            # 重新初始化UI组件引用
            for attr_name in ['btnStartSmartArrange', 'toolButton_startSmartArrange', 'progressBar_classification']:
                try:
                    pass  # 占位，保留结构完整性
                except Exception:
                    pass
                
            # 重置进度条
            if hasattr(self.parent, 'progressBar_classification'):
                self.parent.progressBar_classification.setValue(0)
                
            # 重置操作按钮，使用正确的名称并添加属性检查
            if hasattr(self.parent, 'btnStartSmartArrange'):
                self.parent.btnStartSmartArrange.setText("开始整理")
            elif hasattr(self.parent, 'toolButton_startSmartArrange'):
                self.parent.toolButton_startSmartArrange.setText("开始整理")
                
            # 重置操作类型
            if hasattr(self.parent, 'fileOperation'):
                self.parent.fileOperation.setCurrentIndex(0)
                
            # 重置目标路径
            self.destination_root = None
            
        except Exception as e:
            self.log("ERROR", f"重置状态时出错: {str(e)}")
