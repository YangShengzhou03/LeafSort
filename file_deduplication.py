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

    # 信号定义 - 这些信号现在主要用于向后兼容和内部使用
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
        def on_deduplication_clicked():
            logger.info('执行去重按钮点击事件')
            self._start_deduplication()
        
        self.parent.btnStartDeduplication.clicked.connect(on_deduplication_clicked)
    
    def _browse_folder(self):
        """浏览选择文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", 
            getattr(self, 'folder_path_edit', None) and self.folder_path_edit.text() or ""
        )
        if folder_path:
            if hasattr(self, 'folder_path_edit'):
                self.folder_path_edit.setText(folder_path)
            logger.info(f"已选择文件夹: {folder_path}")
    
    def _start_scan(self):
        """开始扫描重复文件"""
        if not hasattr(self, 'folder_path_edit') or not self.folder_path_edit.text() or not os.path.exists(self.folder_path_edit.text()):
            QtWidgets.QMessageBox.warning(self, "警告", "请选择有效的文件夹路径")
            logger.warning("无效的文件夹路径")
            return
        
        folder_path = self.folder_path_edit.text()
        logger.info(f"开始扫描文件夹: {folder_path}")
        # 清空之前的结果
        self.duplicate_groups = []
        if hasattr(self, 'duplicate_table'):
            self.duplicate_table.setRowCount(0)
        if hasattr(self, 'btnStartDeduplication'):
            self.btnStartDeduplication.setEnabled(False)
        
        # 更新UI状态
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(False)
        if hasattr(self, 'stop_scan_btn'):
            self.stop_scan_btn.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(0)
        if hasattr(self, 'status_label'):
            self.status_label.setText("开始扫描...")
        
        # 启动扫描线程
        filters = []
        if hasattr(self, 'filter_input') and self.filter_input.text():
            filters = [f.strip() for f in self.filter_input.text().split(",")]
        logger.info(f"使用文件过滤器: {filters if filters else '无'}")
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
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(True)
        if hasattr(self, 'stop_scan_btn'):
            self.stop_scan_btn.setEnabled(False)
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
        if hasattr(self, 'duplicate_table'):
            for row in range(self.duplicate_table.rowCount()):
                file_path = self.duplicate_table.item(row, 0).text()
                checkbox = self.duplicate_table.cellWidget(row, 2)
                if checkbox and checkbox.isChecked():
                    delete_list.append(file_path)
        
        logger.info(f"开始去重操作，将删除 {len(delete_list)} 个文件")
        # 更新UI状态
        if hasattr(self, 'btnStartDeduplication'):
            self.btnStartDeduplication.setEnabled(False)
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(False)
        
        # 启动去重线程
        self.deduplicate_thread = FileDeduplicateThread(self.duplicate_groups, delete_list)
        self.deduplicate_thread.progress_updated.connect(self.on_progress_updated)
        self.deduplicate_thread.deduplicate_completed.connect(self.on_deduplicate_completed)
        self.deduplicate_thread.error_occurred.connect(self.on_error_occurred)
        self.deduplicate_thread.finished.connect(self._on_deduplicate_thread_finished)
        self.deduplicate_thread.start()
    
    def _on_deduplicate_thread_finished(self):
        """去重线程完成后的处理"""
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(True)
        logger.info("去重线程已完成")

    def _update_scan_results(self, duplicate_groups):
        """更新扫描结果显示"""
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        total_groups = len(duplicate_groups)
        
        logger.info(f"扫描完成，找到 {total_groups} 组重复文件，共 {total_duplicates} 个重复文件")
        # 更新统计信息
        if total_groups > 0:
            if hasattr(self, 'stats_label'):
                self.stats_label.setText(
                    f"找到 {total_groups} 组重复文件，共 {total_duplicates} 个重复文件"
                )
            if hasattr(self, 'btnStartDeduplication'):
                self.btnStartDeduplication.setEnabled(True)
            
            # 填充表格
            if hasattr(self, 'duplicate_table'):
                row = 0
                for group in duplicate_groups:
                    for i, file_path in enumerate(group):
                        file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                        
                        self.duplicate_table.insertRow(row)
                        self.duplicate_table.setItem(row, 0, QtWidgets.QTableWidgetItem(file_path))
                        self.duplicate_table.setItem(row, 1, QtWidgets.QTableWidgetItem(f"{file_size:.2f} MB"))
                        
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
                        
                        # 为保留的文件添加标记
                        if i == 0:
                            self.duplicate_table.item(row, 0).setForeground(QtGui.QBrush(QtGui.QColor("green")))
                        
                        row += 1
        else:
            if hasattr(self, 'stats_label'):
                self.stats_label.setText("没有找到重复文件")
        
        # 恢复UI状态
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(True)
        if hasattr(self, 'stop_scan_btn'):
            self.stop_scan_btn.setEnabled(False)
        if hasattr(self, 'status_label'):
            self.status_label.setText("扫描完成")

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
        if hasattr(self, 'status_label'):
            self.status_label.setText(f"去重完成: 成功删除 {deleted_count}/{total_count} 个重复文件")
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(True)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(100)
        
        logger.info(f"去重完成: 成功删除 {deleted_count}/{total_count} 个重复文件")
        # 显示结果消息
        QtWidgets.QMessageBox.information(
            self, "去重完成",
            f"成功删除 {deleted_count} 个重复文件\n共处理 {total_count} 个文件"
        )
    
    def on_error_occurred(self, error_message):
        """错误发生槽函数"""
        if hasattr(self, 'status_label'):
            self.status_label.setText("扫描出错")
        if hasattr(self, 'scan_btn'):
            self.scan_btn.setEnabled(True)
        if hasattr(self, 'stop_scan_btn'):
            self.stop_scan_btn.setEnabled(False)
        
        logger.error(f"发生错误: {error_message}")
        QtWidgets.QMessageBox.critical(self, "错误", error_message)