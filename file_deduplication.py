import os
import hashlib
import logging
from PyQt6 import QtWidgets, QtCore, QtGui
from common import get_resource_path
from file_deduplication_thread import FileScanThread, FileDeduplicateThread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileDeduplicationManager(QtWidgets.QWidget):
    """文件去重管理器"""

    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    deduplicate_completed = QtCore.pyqtSignal(int, int)  # 去重完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.scan_thread = None
        self.deduplicate_thread = None
        self.duplicate_groups = []
        
        # 初始化UI元素引用
        self._init_ui_references()
        
        # 连接信号和槽
        self._connect_signals()
        
        # 初始化表格
        self._init_table()
    
    def _init_ui_references(self):
        """初始化UI元素引用"""
        # 确保所有需要的UI元素都被引用
        self.folder_path_edit = getattr(self.parent, 'folderPathEdit', None)
        self.duplicate_table = getattr(self.parent, 'duplicateTable', None)
        self.progress_bar = getattr(self.parent, 'progressBar', None)
        self.status_label = getattr(self.parent, 'statusLabel', None)
        self.stats_label = getattr(self.parent, 'statsLabel', None)
        self.scan_btn = getattr(self.parent, 'btnStartScan', None)
        self.stop_scan_btn = getattr(self.parent, 'btnStopScan', None)
        self.filter_input = getattr(self.parent, 'filterInput', None)
        
        # 如果找不到某些UI元素，记录警告
        missing_elements = []
        for attr in ['folder_path_edit', 'duplicate_table', 'progress_bar', 'status_label', 'stats_label', 
                     'scan_btn', 'stop_scan_btn', 'filter_input']:
            if not getattr(self, attr):
                missing_elements.append(attr)
        
        if missing_elements:
            logger.warning(f"未找到以下UI元素: {missing_elements}")
    
    def _init_table(self):
        """初始化表格"""
        if self.duplicate_table:
            # 设置表格列
            self.duplicate_table.setColumnCount(3)
            self.duplicate_table.setHorizontalHeaderLabels(["文件路径", "文件大小", "删除"])
            
            # 设置表格属性
            header = self.duplicate_table.horizontalHeader()
            header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
            
            # 启用排序
            self.duplicate_table.setSortingEnabled(True)
    
    def _connect_signals(self):
        """连接信号和槽"""
        # 连接扫描按钮
        if self.scan_btn:
            self.scan_btn.clicked.connect(self._start_scan)
        
        # 连接停止扫描按钮
        if self.stop_scan_btn:
            self.stop_scan_btn.clicked.connect(self._stop_scan)
        
        # 连接浏览文件夹按钮
        if hasattr(self.parent, 'btnBrowseFolder'):
            self.parent.btnBrowseFolder.clicked.connect(self._browse_folder)
        
        # 连接去重按钮
        if hasattr(self.parent, 'btnStartDeduplication'):
            self.parent.btnStartDeduplication.clicked.connect(self._on_deduplication_clicked)
    
    def _on_deduplication_clicked(self):
        """去重按钮点击事件处理"""
        logger.info('执行去重按钮点击事件')
        self._start_deduplication()
    
    def _browse_folder(self):
        """浏览选择文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", 
            self.folder_path_edit and self.folder_path_edit.text() or ""
        )
        if folder_path:
            if self.folder_path_edit:
                self.folder_path_edit.setText(folder_path)
            logger.info(f"已选择文件夹: {folder_path}")
    
    def _set_ui_enabled(self, scanning=False, deduplicating=False):
        """设置UI元素的启用状态"""
        # 扫描相关按钮状态
        if self.scan_btn:
            self.scan_btn.setEnabled(not scanning and not deduplicating)
        
        if self.stop_scan_btn:
            self.stop_scan_btn.setEnabled(scanning)
        
        # 去重按钮状态
        if hasattr(self.parent, 'btnStartDeduplication'):
            self.parent.btnStartDeduplication.setEnabled(
                not scanning and not deduplicating and bool(self.duplicate_groups)
            )
        
        # 浏览文件夹按钮状态
        if hasattr(self.parent, 'btnBrowseFolder'):
            self.parent.btnBrowseFolder.setEnabled(not scanning and not deduplicating)
        
        # 文件路径输入框状态
        if self.folder_path_edit:
            self.folder_path_edit.setEnabled(not scanning and not deduplicating)
        
        # 过滤器输入框状态
        if self.filter_input:
            self.filter_input.setEnabled(not scanning and not deduplicating)
    
    def _start_scan(self):
        """开始扫描重复文件"""
        if not self.folder_path_edit or not self.folder_path_edit.text() or not os.path.exists(self.folder_path_edit.text()):
            QtWidgets.QMessageBox.warning(self, "警告", "请选择有效的文件夹路径")
            logger.warning("无效的文件夹路径")
            return
        
        folder_path = self.folder_path_edit.text()
        logger.info(f"开始扫描文件夹: {folder_path}")
        
        # 清空之前的结果
        self.duplicate_groups = []
        if self.duplicate_table:
            self.duplicate_table.setRowCount(0)
        
        # 更新UI状态
        self._set_ui_enabled(scanning=True)
        
        # 设置进度条和状态标签
        if self.progress_bar:
            self.progress_bar.setValue(0)
        if self.status_label:
            self.status_label.setText("开始扫描...")
        if self.stats_label:
            self.stats_label.setText("准备扫描...")
        
        # 获取文件过滤器
        filters = []
        if self.filter_input and self.filter_input.text():
            filters = [f.strip() for f in self.filter_input.text().split(",")]
        logger.info(f"使用文件过滤器: {filters if filters else '无'}")
        
        # 启动扫描线程
        self.scan_thread = FileScanThread(folder_path, filters)
        self.scan_thread.progress_updated.connect(self.on_progress_updated)
        self.scan_thread.scan_completed.connect(self.on_scan_completed)
        self.scan_thread.error_occurred.connect(self.on_error_occurred)
        self.scan_thread.finished.connect(self._on_scan_thread_finished)
        self.scan_thread.start()
    
    def _stop_scan(self):
        """停止扫描"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            if hasattr(self, 'status_label'):
                self.status_label.setText("正在停止扫描...")
            logger.info("停止扫描")
    
    def _on_scan_thread_finished(self):
        """扫描线程完成后的处理"""
        # 重置UI状态
        self._set_ui_enabled(scanning=False)
        logger.info("扫描线程已完成")
    
    def _start_deduplication(self):
        """开始执行去重"""
        if not self.duplicate_groups:
            logger.warning("没有重复文件组，无法执行去重")
            return
        
        # 确认对话框
        reply = QtWidgets.QMessageBox.question(
            self, "确认去重", 
            "确定要删除选中的重复文件吗？此操作不可恢复。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            logger.info("用户取消了去重操作")
            return
        
        # 收集要删除的文件列表
        delete_list = []
        if self.duplicate_table:
            for row in range(self.duplicate_table.rowCount()):
                file_path = self.duplicate_table.item(row, 0).text()
                # 获取复选框
                checkbox_widget = self.duplicate_table.cellWidget(row, 2)
                if checkbox_widget:
                    # 尝试从布局中获取复选框
                    for i in range(checkbox_widget.layout().count()):
                        item = checkbox_widget.layout().itemAt(i)
                        if item and isinstance(item.widget(), QtWidgets.QCheckBox):
                            checkbox = item.widget()
                            if checkbox and checkbox.isChecked():
                                delete_list.append(file_path)
                                break
        
        if not delete_list:
            QtWidgets.QMessageBox.information(self, "提示", "请选择要删除的重复文件")
            return
        
        logger.info(f"开始去重操作，将删除 {len(delete_list)} 个文件")
        
        # 更新UI状态
        self._set_ui_enabled(deduplicating=True)
        
        # 设置进度条和状态标签
        if self.progress_bar:
            self.progress_bar.setValue(0)
        if self.status_label:
            self.status_label.setText("开始去重...")
        
        # 启动去重线程
        self.deduplicate_thread = FileDeduplicateThread(self.duplicate_groups, delete_list)
        self.deduplicate_thread.progress_updated.connect(self.on_progress_updated)
        self.deduplicate_thread.deduplicate_completed.connect(self.on_deduplicate_completed)
        self.deduplicate_thread.error_occurred.connect(self.on_error_occurred)
        self.deduplicate_thread.finished.connect(self._on_deduplicate_thread_finished)
        self.deduplicate_thread.start()
    
    def _on_deduplicate_thread_finished(self):
        """去重线程完成后的处理"""
        # 重置UI状态
        self._set_ui_enabled(deduplicating=False)
        logger.info("去重线程已完成")
    
    def _format_file_size(self, size_bytes):
        """格式化文件大小为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def _update_scan_results(self, duplicate_groups):
        """更新扫描结果显示"""
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        total_groups = len(duplicate_groups)
        
        logger.info(f"扫描完成，找到 {total_groups} 组重复文件，共 {total_duplicates} 个重复文件")
        
        # 计算节省的空间
        total_saved_space = 0
        for group in duplicate_groups:
            if group:
                # 获取第一个文件的大小（保留的文件）
                try:
                    base_size = os.path.getsize(group[0])
                    # 累加其他重复文件的大小（节省的空间）
                    for file_path in group[1:]:
                        total_saved_space += os.path.getsize(file_path)
                except Exception as e:
                    logger.error(f"计算文件大小时出错: {str(e)}")
        
        # 更新统计信息
        if total_groups > 0:
            if self.stats_label:
                saved_space_str = self._format_file_size(total_saved_space)
                self.stats_label.setText(
                    f"找到 {total_groups} 组重复文件，共 {total_duplicates} 个重复文件，可节省 {saved_space_str}"
                )
            
            # 填充表格
            if self.duplicate_table:
                self.duplicate_table.setRowCount(0)  # 清空表格
                row = 0
                for group_idx, group in enumerate(duplicate_groups):
                    for i, file_path in enumerate(group):
                        try:
                            file_size = os.path.getsize(file_path)
                            
                            self.duplicate_table.insertRow(row)
                            
                            # 文件路径
                            path_item = QtWidgets.QTableWidgetItem(file_path)
                            if i == 0:
                                path_item.setForeground(QtGui.QBrush(QtGui.QColor("green")))
                            self.duplicate_table.setItem(row, 0, path_item)
                            
                            # 文件大小
                            size_str = self._format_file_size(file_size)
                            self.duplicate_table.setItem(row, 1, QtWidgets.QTableWidgetItem(size_str))
                            
                            # 添加复选框（默认保留每组的第一个文件）
                            checkbox = QtWidgets.QCheckBox()
                            if i > 0:  # 不是每组的第一个文件默认选中删除
                                checkbox.setChecked(True)
                            checkbox.setEnabled(i > 0)  # 禁用每组第一个文件的复选框
                            
                            checkbox_widget = QtWidgets.QWidget()
                            checkbox_layout = QtWidgets.QHBoxLayout(checkbox_widget)
                            checkbox_layout.addWidget(checkbox)
                            checkbox_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                            checkbox_layout.setContentsMargins(0, 0, 0, 0)
                            
                            self.duplicate_table.setCellWidget(row, 2, checkbox_widget)
                            
                            # 为每组添加分隔线
                            if i == 0 and group_idx > 0:
                                # 添加分隔线行
                                self.duplicate_table.insertRow(row)
                                separator_item = QtWidgets.QTableWidgetItem(f"--- 第 {group_idx + 1} 组重复文件 ---")
                                separator_item.setForeground(QtGui.QBrush(QtGui.QColor("gray")))
                                separator_item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)  # 不可编辑
                                self.duplicate_table.setItem(row, 0, separator_item)
                                self.duplicate_table.setSpan(row, 0, 1, 3)  # 合并单元格
                                row += 1
                            
                            row += 1
                        except Exception as e:
                            logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
        else:
            if self.stats_label:
                self.stats_label.setText("没有找到重复文件")
        
        # 更新状态标签
        if self.status_label:
            self.status_label.setText("扫描完成")
        
        # 更新UI状态
        self._set_ui_enabled(scanning=False)

    def on_progress_updated(self, progress, status_text):
        """进度更新槽函数"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(progress)
        if hasattr(self, 'status_label'):
            self.status_label.setText(status_text)
        logger.debug(f"进度更新: {progress}% - {status_text}")
    
    def on_scan_completed(self, duplicate_groups):
        """扫描完成槽函数"""
        # 保存扫描结果
        self.duplicate_groups = duplicate_groups
        self._update_scan_results(duplicate_groups)
    
    def on_deduplicate_completed(self, deleted_count, total_count):
        """去重完成槽函数"""
        if self.status_label:
            self.status_label.setText(f"去重完成: 成功删除 {deleted_count}/{total_count} 个重复文件")
        if self.progress_bar:
            self.progress_bar.setValue(100)
        
        logger.info(f"去重完成: 成功删除 {deleted_count}/{total_count} 个重复文件")
        
        # 重新扫描以更新结果
        if deleted_count > 0 and self.folder_path_edit and os.path.exists(self.folder_path_edit.text()):
            self._start_scan()
        else:
            # 更新UI状态
            self._set_ui_enabled(deduplicating=False)
            
            # 显示结果消息
            QtWidgets.QMessageBox.information(
                self, "去重完成",
                f"成功删除 {deleted_count} 个重复文件\n共处理 {total_count} 个文件"
            )
    
    def on_error_occurred(self, error_message):
        """错误发生槽函数"""
        if self.status_label:
            self.status_label.setText("操作出错")
        
        # 重置UI状态
        self._set_ui_enabled(scanning=False, deduplicating=False)
        
        logger.error(f"发生错误: {error_message}")
        QtWidgets.QMessageBox.critical(self, "错误", error_message)