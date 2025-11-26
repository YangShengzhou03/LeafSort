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
        self._setup_ui()
    
    def _setup_ui(self):
        """设置UI界面"""
        self.layout = QtWidgets.QVBoxLayout(self)
        
        # 标题
        title_label = QtWidgets.QLabel("文件去重")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #333;")
        self.layout.addWidget(title_label)
        
        # 文件夹选择
        folder_layout = QtWidgets.QHBoxLayout()
        self.folder_path_edit = QtWidgets.QLineEdit()
        self.folder_path_edit.setReadOnly(True)
        self.folder_path_edit.setPlaceholderText("请选择要扫描的文件夹")
        browse_btn = QtWidgets.QPushButton("浏览...")
        browse_btn.clicked.connect(self._browse_folder)
        
        folder_layout.addWidget(self.folder_path_edit)
        folder_layout.addWidget(browse_btn)
        self.layout.addLayout(folder_layout)
        
        # 文件类型过滤
        filter_layout = QtWidgets.QHBoxLayout()
        filter_label = QtWidgets.QLabel("文件类型过滤:")
        self.filter_input = QtWidgets.QLineEdit()
        self.filter_input.setPlaceholderText("例如: .jpg,.png,.gif")
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_input)
        self.layout.addLayout(filter_layout)
        
        # 扫描按钮
        self.scan_btn = QtWidgets.QPushButton("开始扫描")
        self.scan_btn.clicked.connect(self._start_scan)
        self.stop_scan_btn = QtWidgets.QPushButton("停止扫描")
        self.stop_scan_btn.clicked.connect(self._stop_scan)
        self.stop_scan_btn.setEnabled(False)
        
        btn_layout = QtWidgets.QHBoxLayout()
        btn_layout.addWidget(self.scan_btn)
        btn_layout.addWidget(self.stop_scan_btn)
        self.layout.addLayout(btn_layout)
        
        # 进度条
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setValue(0)
        self.layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QtWidgets.QLabel("就绪")
        self.layout.addWidget(self.status_label)
        
        # 结果显示
        result_group = QtWidgets.QGroupBox("扫描结果")
        result_layout = QtWidgets.QVBoxLayout(result_group)
        
        # 统计信息
        self.stats_label = QtWidgets.QLabel("未扫描")
        result_layout.addWidget(self.stats_label)
        
        # 去重按钮
        self.deduplicate_btn = QtWidgets.QPushButton("执行去重")
        self.deduplicate_btn.clicked.connect(self._start_deduplication)
        self.deduplicate_btn.setEnabled(False)
        result_layout.addWidget(self.deduplicate_btn)
        
        # 重复文件列表
        self.duplicate_table = QtWidgets.QTableWidget()
        self.duplicate_table.setColumnCount(3)
        self.duplicate_table.setHorizontalHeaderLabels(["文件路径", "文件大小", "保留/删除"])
        self.duplicate_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        result_layout.addWidget(self.duplicate_table)
        
        self.layout.addWidget(result_group)
        
        # 底部填充
        self.layout.addStretch()
    
    def _browse_folder(self):
        """浏览选择文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", 
            self.folder_path_edit.text() or ""
        )
        if folder_path:
            self.folder_path_edit.setText(folder_path)
    
    def _start_scan(self):
        """开始扫描重复文件"""
        folder_path = self.folder_path_edit.text()
        if not folder_path or not os.path.exists(folder_path):
            QtWidgets.QMessageBox.warning(self, "警告", "请选择有效的文件夹路径")
            return
        
        # 清空之前的结果
        self.duplicate_groups = []
        self.duplicate_table.setRowCount(0)
        self.deduplicate_btn.setEnabled(False)
        
        # 更新UI状态
        self.scan_btn.setEnabled(False)
        self.stop_scan_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("开始扫描...")
        
        # 启动扫描线程
        filters = [f.strip() for f in self.filter_input.text().split(",")] if self.filter_input.text() else []
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
            self.status_label.setText("正在停止扫描...")
    
    def _on_scan_thread_finished(self):
        """扫描线程完成后的处理"""
        self.scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
    

    
    def _start_deduplication(self):
        """开始执行去重"""
        if not self.duplicate_groups:
            return
        
        # 确认对话框
        reply = QtWidgets.QMessageBox.question(
            self, "确认去重", 
            "确定要删除选中的重复文件吗？此操作不可恢复。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        
        # 收集要删除的文件列表
        delete_list = []
        for row in range(self.duplicate_table.rowCount()):
            file_path = self.duplicate_table.item(row, 0).text()
            checkbox = self.duplicate_table.cellWidget(row, 2)
            if checkbox and checkbox.isChecked():
                delete_list.append(file_path)
        
        # 更新UI状态
        self.deduplicate_btn.setEnabled(False)
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
        self.scan_btn.setEnabled(True)

    def _update_scan_results(self, duplicate_groups):
        """更新扫描结果显示"""
        total_duplicates = sum(len(group) - 1 for group in duplicate_groups)
        total_groups = len(duplicate_groups)
        
        # 更新统计信息
        if total_groups > 0:
            self.stats_label.setText(
                f"找到 {total_groups} 组重复文件，共 {total_duplicates} 个重复文件"
            )
            self.deduplicate_btn.setEnabled(True)
            
            # 填充表格
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
            self.stats_label.setText("没有找到重复文件")
        
        # 恢复UI状态
        self.scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        self.status_label.setText("扫描完成")

    def on_progress_updated(self, progress, status_text):
        """进度更新槽函数"""
        self.progress_bar.setValue(progress)
        self.status_label.setText(status_text)
    
    def on_scan_completed(self, duplicate_groups):
        """扫描完成槽函数"""
        # 保存扫描结果
        self.duplicate_groups = duplicate_groups
        self._update_scan_results(duplicate_groups)
    
    def on_deduplicate_completed(self, deleted_count, total_count):
        """去重完成槽函数"""
        self.status_label.setText(f"去重完成: 成功删除 {deleted_count}/{total_count} 个重复文件")
        self.scan_btn.setEnabled(True)
        self.progress_bar.setValue(100)
        
        # 显示结果消息
        QtWidgets.QMessageBox.information(
            self, "去重完成",
            f"成功删除 {deleted_count} 个重复文件\n共处理 {total_count} 个文件"
        )
    
    def on_error_occurred(self, error_message):
        """错误发生槽函数"""
        self.status_label.setText("扫描出错")
        self.scan_btn.setEnabled(True)
        self.stop_scan_btn.setEnabled(False)
        
        QtWidgets.QMessageBox.critical(self, "错误", error_message)