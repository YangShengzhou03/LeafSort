import logging
import os

from PyQt6 import QtWidgets, QtCore

from file_deduplication_thread import FileScanThread, FileDeduplicateThread

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileDeduplicationManager(QtWidgets.QWidget):
    progress_updated = QtCore.pyqtSignal(int, str)
    scan_completed = QtCore.pyqtSignal(list)
    error_occurred = QtCore.pyqtSignal(str)
    
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
        self.parent.duplicateItemsListWidget.clear()
        
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        self.parent.duplicateFilesTableWidget.setColumnCount(3)
        headers = ["选择", "文件名", "文件路径"]
        self.parent.duplicateFilesTableWidget.setHorizontalHeaderLabels(headers)
        
        header = self.parent.duplicateFilesTableWidget.horizontalHeader()
        
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        
        self.parent.duplicateFilesTableWidget.setColumnWidth(0, 65)
        
        self.parent.duplicateFilesTableWidget.setColumnWidth(1, 250)
        
        self.parent.duplicateFilesTableWidget.setAlternatingRowColors(True)
        self.parent.duplicateFilesTableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self.parent.duplicateFilesTableWidget.setSortingEnabled(True)
        
        self.parent.contrastProgressBar.setValue(0)
    
    def _connect_signals(self):
        self.parent.btnStartDeduplication.clicked.connect(self.start_scan)
        self.parent.btnRandomSelect.clicked.connect(self.random_select)
        self.parent.btnMoveToRecycleBin.clicked.connect(self.move_to_recycle_bin)
        
        self.parent.duplicateItemsListWidget.currentRowChanged.connect(self.on_group_selected)
        
        self.parent.duplicateFilesTableWidget.cellChanged.connect(self.on_file_selection_changed)
    
    def start_scan(self):
        if not self.folder_page:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "系统错误：folder_page未初始化")
            return
        
        folders = self.folder_page.get_all_folders()
        if not folders:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先选择要扫描的文件夹")
            return
        
        self.duplicate_groups = []
        self.current_group_index = -1
        self.selected_files.clear()
        self.parent.duplicateItemsListWidget.clear()
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        self.parent.contrastProgressBar.setValue(0)
        
        self.parent.btnStartDeduplication.setEnabled(False)
        self.parent.btnStartDeduplication.setText("扫描中...")
        
        self.scan_thread = FileScanThread(folders, self.filters)
        self.scan_thread.progress_updated.connect(self.on_scan_progress)
        self.scan_thread.scan_completed.connect(self.on_scan_completed)
        self.scan_thread.error_occurred.connect(self.on_scan_error)
        self.scan_thread.start()
        
        logger.info(f"开始扫描文件夹: {folders}")
    
    def on_scan_progress(self, progress, status_text):
        self.parent.contrastProgressBar.setValue(progress)
    
    def on_scan_completed(self, duplicate_groups):
        self.duplicate_groups = duplicate_groups
        
        self.parent.duplicateItemsListWidget.clear()
        for i, group in enumerate(duplicate_groups):
            item = QtWidgets.QListWidgetItem(f"重复文件组 {i+1} ({len(group)}个文件)")
            self.parent.duplicateItemsListWidget.addItem(item)
        
        self.parent.btnStartDeduplication.setEnabled(True)
        self.parent.btnStartDeduplication.setText("开始查重")
        self.parent.contrastProgressBar.setValue(100)
        
        if duplicate_groups:
            QtWidgets.QMessageBox.information(self.parent, "扫描完成", 
                                            f"找到 {len(duplicate_groups)} 组重复文件")
            
            self.parent.duplicateItemsListWidget.setCurrentRow(0)
            self.on_group_selected(0)
            logger.info("自动选择第一个重复文件组")
        else:
            QtWidgets.QMessageBox.information(self.parent, "扫描完成", "未找到重复文件")
        
        logger.info(f"扫描完成，找到 {len(duplicate_groups)} 组重复文件")
    
    def on_scan_error(self, error_message):
        self.parent.btnStartDeduplication.setEnabled(True)
        self.parent.btnStartDeduplication.setText("开始查重")
        QtWidgets.QMessageBox.critical(self.parent, "扫描错误", error_message)
        logger.error(f"扫描错误: {error_message}")
    
    def on_group_selected(self, row):
        if row < 0 or row >= len(self.duplicate_groups):
            return
        
        self.current_group_index = row
        self._display_group_files(self.duplicate_groups[row])
    
    def _display_group_files(self, file_group):
        self.parent.duplicateFilesTableWidget.setRowCount(0)
        
        for i, file_path in enumerate(file_group):
            self.parent.duplicateFilesTableWidget.insertRow(i)
            
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(file_path in self.selected_files)
            checkbox.stateChanged.connect(lambda state, path=file_path: self._on_checkbox_changed(state, path))
            checkbox_widget = QtWidgets.QWidget()
            layout = QtWidgets.QHBoxLayout(checkbox_widget)
            layout.addWidget(checkbox)
            layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.setContentsMargins(5, 3, 5, 3)
            self.parent.duplicateFilesTableWidget.setCellWidget(i, 0, checkbox_widget)
            
            file_name = os.path.basename(file_path)
            self.parent.duplicateFilesTableWidget.setItem(i, 1, QtWidgets.QTableWidgetItem(file_name))
            
            path_item = QtWidgets.QTableWidgetItem(file_path)
            path_item.setToolTip(file_path)
            self.parent.duplicateFilesTableWidget.setItem(i, 2, path_item)
    
    def _on_checkbox_changed(self, state, file_path):
        if state == QtCore.Qt.CheckState.Checked.value:
            self.selected_files.add(file_path)
        else:
            self.selected_files.discard(file_path)
        
        self._update_selection_status()
    
    def _update_selection_status(self):
        logger.info(f"已选择 {len(self.selected_files)} 个文件待删除")
        
        if hasattr(self.parent, 'statusBar'):
            try:
                status_bar = self.parent.statusBar()
                if status_bar:
                    status_bar.showMessage(f"已选择 {len(self.selected_files)} 个文件待删除")
            except Exception as e:
                logger.debug(f"无法更新状态栏: {e}")
    
    def on_file_selection_changed(self, row, column):
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
        if not self.duplicate_groups:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先扫描重复文件")
            return
        
        self.selected_files.clear()
        selected_count = 0
        
        for group in self.duplicate_groups:
            if len(group) > 1:
                import random
                keep_file = random.choice(group)
                
                for file_path in group:
                    if file_path != keep_file:
                        self.selected_files.add(file_path)
                        selected_count += 1
        
        if self.current_group_index >= 0:
            self._display_group_files(self.duplicate_groups[self.current_group_index])
        
        QtWidgets.QMessageBox.information(self.parent, "随机选择", 
                                        f"已随机保留每组中一个文件，共选择 {selected_count} 个重复文件")
    
    def move_to_recycle_bin(self):
        if not self.selected_files:
            QtWidgets.QMessageBox.warning(self.parent, "警告", "请先选择要删除的文件")
            return
        
        reply = QtWidgets.QMessageBox.question(self.parent, "确认删除", 
                                             f"确定要将 {len(self.selected_files)} 个文件移动到回收站吗？",
                                             QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No)
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            self.deduplicate_thread = FileDeduplicateThread(self.duplicate_groups, list(self.selected_files))
            self.deduplicate_thread.progress_updated.connect(self.on_deduplicate_progress)
            self.deduplicate_thread.deduplicate_completed.connect(self.on_deduplicate_completed)
            self.deduplicate_thread.error_occurred.connect(self.on_deduplicate_error)
            self.deduplicate_thread.start()
            
            logger.info(f"开始删除 {len(self.selected_files)} 个重复文件")
    
    def on_deduplicate_progress(self, progress, status_text):
        self.parent.contrastProgressBar.setValue(progress)
    
    def on_deduplicate_completed(self, deleted_count, total_count):
        QtWidgets.QMessageBox.information(self.parent, "去重完成", 
                                        f"成功删除 {deleted_count} 个重复文件")
        
        self.start_scan()
    
    def on_deduplicate_error(self, error_message):
        QtWidgets.QMessageBox.critical(self.parent, "去重错误", error_message)
        logger.error(f"去重错误: {error_message}")
    
    def stop_scan(self):
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.stop()
            self.scan_thread.wait()
        
        if self.deduplicate_thread and self.deduplicate_thread.isRunning():
            self.deduplicate_thread.stop()
            self.deduplicate_thread.wait()