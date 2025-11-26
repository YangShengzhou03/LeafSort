import logging
import os
from datetime import datetime

from PyQt6 import QtWidgets, QtCore, QtGui
from file_deduplication_thread import FileScanThread, FileDeduplicateThread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileDeduplicationManager(QtWidgets.QWidget):
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.scan_thread = None
        self.deduplicate_thread = None
        self.duplicate_groups = []
        self.current_group_index = -1
        self.selected_files = set()
        self.filters = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """初始化UI设置"""
        # 初始化重复文件列表
        self.parent.duplicateItemsListWidget.clear()
        
        # 设置表格
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        self.parent.duplicateFilesTableWidget.setColumnCount(4)
        headers = ["选择", "文件路径", "文件大小", "修改时间"]
        self.parent.duplicateFilesTableWidget.setHorizontalHeaderLabels(headers)
        
        # 设置列宽
        self.parent.duplicateFilesTableWidget.setColumnWidth(0, 60)  # 选择列
        self.parent.duplicateFilesTableWidget.setColumnWidth(1, 400)  # 文件路径
        self.parent.duplicateFilesTableWidget.setColumnWidth(2, 100)  # 文件大小
        self.parent.duplicateFilesTableWidget.setColumnWidth(3, 150)  # 修改时间
        
        # 设置进度条初始值
        self.parent.contrastProgressBar.setValue(0)
    
    def _connect_signals(self):
        """连接信号和槽函数"""
        # 按钮点击事件
        self.parent.btnStartDeduplication.clicked.connect(self.start_scan)
        self.parent.btnRandomSelect.clicked.connect(self.random_select)
        self.parent.btnMoveToRecycleBin.clicked.connect(self.move_to_recycle_bin)
        
        # 列表选择事件
        self.parent.duplicateItemsListWidget.currentRowChanged.connect(self.on_group_selected)
        
        # 表格选择事件
        self.parent.duplicateFilesTableWidget.cellChanged.connect(self.on_file_selection_changed)
    
    def start_scan(self):
        """开始扫描重复文件"""
        if not self.folder_page:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "系统错误：folder_page未初始化")
            return
        
        folders = self.folder_page.get_all_folders()
        if not folders:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先选择要扫描的文件夹")
            return
        
        # 重置状态
        self.duplicate_groups = []
        self.current_group_index = -1
        self.selected_files.clear()
        self.parent.duplicateItemsListWidget.clear()
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        self.parent.contrastProgressBar.setValue(0)
        
        # 更新按钮状态
        self.parent.btnStartDeduplication.setEnabled(False)
        self.parent.btnStartDeduplication.setText("扫描中...")
        
        # 创建并启动扫描线程
        self.scan_thread = FileScanThread(folders, self.filters)
        self.scan_thread.progress_updated.connect(self.on_scan_progress)
        self.scan_thread.scan_completed.connect(self.on_scan_completed)
        self.scan_thread.error_occurred.connect(self.on_scan_error)
        self.scan_thread.start()
        
        logger.info(f"开始扫描文件夹: {folders}")
    
    def on_scan_progress(self, progress, status_text):
        """处理扫描进度更新"""
        self.parent.contrastProgressBar.setValue(progress)
        # 可以在这里更新状态文本
    
    def on_scan_completed(self, duplicate_groups):
        """处理扫描完成"""
        self.duplicate_groups = duplicate_groups
        
        # 更新重复文件组列表
        self.parent.duplicateItemsListWidget.clear()
        for i, group in enumerate(duplicate_groups):
            item = QtWidgets.QListWidgetItem(f"重复文件组 {i+1} ({len(group)}个文件)")
            self.parent.duplicateItemsListWidget.addItem(item)
        
        # 更新按钮状态
        self.parent.btnStartDeduplication.setEnabled(True)
        self.parent.btnStartDeduplication.setText("开始查重")
        self.parent.contrastProgressBar.setValue(100)
        
        # 显示扫描结果
        if duplicate_groups:
            QtWidgets.QMessageBox.information(self.parent, "扫描完成", 
                                            f"找到 {len(duplicate_groups)} 组重复文件")
        else:
            QtWidgets.QMessageBox.information(self.parent, "扫描完成", "未找到重复文件")
        
        logger.info(f"扫描完成，找到 {len(duplicate_groups)} 组重复文件")
    
    def on_scan_error(self, error_message):
        """处理扫描错误"""
        self.parent.btnStartDeduplication.setEnabled(True)
        self.parent.btnStartDeduplication.setText("开始查重")
        QtWidgets.QMessageBox.critical(self.parent, "扫描错误", error_message)
        logger.error(f"扫描错误: {error_message}")
    
    def on_group_selected(self, row):
        """处理重复文件组选择"""
        if row < 0 or row >= len(self.duplicate_groups):
            return
        
        self.current_group_index = row
        self._display_group_files(self.duplicate_groups[row])
    
    def _display_group_files(self, file_group):
        """显示指定文件组的文件信息"""
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        
        for i, file_path in enumerate(file_group):
            self.parent.duplicateFilesTableWidget.insertRow(i)
            
            # 选择复选框
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(file_path in self.selected_files)
            checkbox_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(0, 0, 0, 0)
            self.parent.duplicateFilesTableWidget.setCellWidget(i, 0, checkbox_widget)
            
            # 文件路径
            self.parent.duplicateFilesTableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(file_path))
            
            # 文件大小
            try:
                size_bytes = os.path.getsize(file_path)
                size_str = self._format_file_size(size_bytes)
                self.parent.duplicateFilesTableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem(size_str))
            except:
                self.parent.duplicateFilesTableWidget.setItem(i, 2, QtWidgets.QTableWidgetItem("未知"))
            
            # 修改时间
            try:
                mtime = os.path.getmtime(file_path)
                time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')
                self.parent.duplicateFilesTableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem(time_str))
            except:
                self.parent.duplicateFilesTableWidget.setItem(i, 3, QtWidgets.QTableWidgetItem("未知"))
    
    def _format_file_size(self, size_bytes):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def on_file_selection_changed(self, row, column):
        """处理文件选择变化"""
        if column != 0 or self.current_group_index < 0:
            return
        
        file_group = self.duplicate_groups[self.current_group_index]
        if row < len(file_group):
            file_path = file_group[row]
            checkbox_widget = self.parent.duplicateFilesTableWidget.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QtWidgets.QCheckBox)
            
            if checkbox.isChecked():
                self.selected_files.add(file_path)
            else:
                self.selected_files.discard(file_path)
    
    def random_select(self):
        """随机选择重复文件"""
        if not self.duplicate_groups:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先扫描重复文件")
            return
        
        self.selected_files.clear()
        
        for group in self.duplicate_groups:
            if len(group) > 1:
                # 保留第一个文件，随机选择要删除的文件
                import random
                files_to_delete = group[1:]
                if files_to_delete:
                    selected_file = random.choice(files_to_delete)
                    self.selected_files.add(selected_file)
        
        # 更新表格显示
        if self.current_group_index >= 0:
            self._display_group_files(self.duplicate_groups[self.current_group_index])
        
        QtWidgets.QMessageBox.information(self.parent, "随机选择", 
                                        f"已随机选择 {len(self.selected_files)} 个文件待删除")
    
    def move_to_recycle_bin(self):
        """将选中的文件移动到回收站"""
        if not self.selected_files:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先选择要删除的文件")
            return
        
        reply = QtWidgets.QMessageBox.question(self.parent, "确认删除", 
                                             f"确定要将 {len(self.selected_files)} 个文件移动到回收站吗？",
                                             QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # 创建并启动去重线程
            self.deduplicate_thread = FileDeduplicateThread(self.duplicate_groups, list(self.selected_files))
            self.deduplicate_thread.progress_updated.connect(self.on_deduplicate_progress)
            self.deduplicate_thread.deduplicate_completed.connect(self.on_deduplicate_completed)
            self.deduplicate_thread.error_occurred.connect(self.on_deduplicate_error)
            self.deduplicate_thread.start()
            
            logger.info(f"开始删除 {len(self.selected_files)} 个重复文件")
    
    def on_deduplicate_progress(self, progress, status_text):
        """处理去重进度更新"""
        self.parent.contrastProgressBar.setValue(progress)
    
    def on_deduplicate_completed(self, deleted_count, total_count):
        """处理去重完成"""
        QtWidgets.QMessageBox.information(self.parent, "去重完成", 
                                        f"成功删除 {deleted_count} 个重复文件")
        
        # 重新扫描以更新文件列表
        self.start_scan()
    
    def on_deduplicate_error(self, error_message):
        """处理去重错误"""
        QtWidgets.QMessageBox.critical(self.parent, "去重错误", error_message)
        logger.error(f"去重错误: {error_message}")
    
    def stop_scan(self):
        """停止扫描"""
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        
        if self.deduplicate_thread and self.deduplicate_thread.isRunning():
            self.deduplicate_thread.stop()
            self.deduplicate_thread.wait()
