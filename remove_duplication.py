"""
重复文件检测与删除页面模块

该模块定义了RemoveDuplicationPage类，用于检测和删除重复文件。
包含文件哈希计算、重复文件分组、预览和删除等功能。
"""

from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, pyqtSignal
import os
import hashlib
from collections import defaultdict

from remove_duplication_thread import RemoveDuplicationThread


class RemoveDuplicationPage(QtWidgets.QWidget):
    """重复文件检测与删除页面类"""
    
    progress_updated = pyqtSignal(int, str)
    scan_completed = pyqtSignal(dict)
    deletion_completed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        """初始化重复文件检测页面
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.hash_dict = {}
        self.duplicate_groups = []
        self.current_group_index = -1
        
        self.init_page()
    
    def init_page(self):
        """初始化页面UI"""
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 控制区域
        self._add_controls(main_layout)
        
        # 进度显示区域
        self._add_progress_area(main_layout)
        
        # 重复文件列表区域
        self._add_duplicate_list(main_layout)
        
        # 操作按钮区域
        self._add_action_buttons(main_layout)
    
    def _add_controls(self, main_layout):
        """添加控制区域"""
        control_layout = QtWidgets.QHBoxLayout()
        
        # 开始扫描按钮
        self.scan_btn = QtWidgets.QPushButton("开始扫描")
        self.scan_btn.clicked.connect(self.start_scan)
        control_layout.addWidget(self.scan_btn)
        
        # 停止扫描按钮
        self.stop_btn = QtWidgets.QPushButton("停止扫描")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        control_layout.addWidget(self.stop_btn)
        
        # 扫描选项
        self.size_checkbox = QtWidgets.QCheckBox("仅比较文件大小")
        self.size_checkbox.setChecked(False)
        control_layout.addWidget(self.size_checkbox)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
    
    def _add_progress_area(self, main_layout):
        """添加进度显示区域"""
        # 进度标签
        self.progress_label = QtWidgets.QLabel("准备扫描...")
        main_layout.addWidget(self.progress_label)
        
        # 进度条
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
    
    def _add_duplicate_list(self, main_layout):
        """添加重复文件列表区域"""
        # 重复文件列表标签
        duplicate_label = QtWidgets.QLabel("检测到的重复文件:")
        main_layout.addWidget(duplicate_label)
        
        # 重复文件列表
        self.duplicate_list = QtWidgets.QListWidget()
        self.duplicate_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.duplicate_list)
    
    def _add_action_buttons(self, main_layout):
        """添加操作按钮区域"""
        button_layout = QtWidgets.QHBoxLayout()
        
        # 预览按钮
        self.preview_btn = QtWidgets.QPushButton("预览选中")
        self.preview_btn.clicked.connect(self.preview_selected)
        self.preview_btn.setEnabled(False)
        button_layout.addWidget(self.preview_btn)
        
        # 删除按钮
        self.delete_btn = QtWidgets.QPushButton("删除选中")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)
        
        # 保留一个按钮
        self.keep_one_btn = QtWidgets.QPushButton("每组保留一个")
        self.keep_one_btn.clicked.connect(self.keep_one_per_group)
        self.keep_one_btn.setEnabled(False)
        button_layout.addWidget(self.keep_one_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def start_scan(self):
        """开始扫描重复文件"""
        if self.is_running:
            return
        
        self.is_running = True
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 创建并启动工作线程
        self.worker = RemoveDuplicationThread()
        self.worker.progress_updated.connect(self._on_progress_updated)
        self.worker.scan_completed.connect(self._on_scan_completed)
        self.worker.start()
    
    def stop_scan(self):
        """停止扫描"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait()
        
        self._reset_scan_state()
    
    def _on_progress_updated(self, progress, message):
        """处理进度更新信号
        
        Args:
            progress: 进度值
            message: 进度消息
        """
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
    
    def _on_scan_completed(self, duplicate_groups):
        """处理扫描完成信号
        
        Args:
            duplicate_groups: 重复文件分组字典
        """
        self.duplicate_groups = duplicate_groups
        self._display_duplicate_groups()
        self._reset_scan_state()
        
        # 启用操作按钮
        self.preview_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        self.keep_one_btn.setEnabled(True)
    
    def _display_duplicate_groups(self):
        """显示重复文件分组"""
        self.duplicate_list.clear()
        
        for group_id, files in self.duplicate_groups.items():
            if len(files) > 1:  # 只有重复文件才显示
                group_item = QtWidgets.QListWidgetItem()
                group_item.setText(f"重复组 {group_id}: {len(files)} 个文件")
                group_item.setData(Qt.ItemDataRole.UserRole, files)
                self.duplicate_list.addItem(group_item)
    
    def _reset_scan_state(self):
        """重置扫描状态"""
        self.is_running = False
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("扫描完成")
    
    def preview_selected(self):
        """预览选中的重复文件"""
        selected_items = self.duplicate_list.selectedItems()
        if not selected_items:
            self._show_message("提示", "请先选择要预览的重复组")
            return
        
        # 实现文件预览逻辑
        for item in selected_items:
            files = item.data(Qt.ItemDataRole.UserRole)
            self._preview_files(files)
    
    def delete_selected(self):
        """删除选中的重复文件"""
        selected_items = self.duplicate_list.selectedItems()
        if not selected_items:
            self._show_message("提示", "请先选择要删除的重复组")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(selected_items)} 个重复组吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            deleted_count = 0
            for item in selected_items:
                files = item.data(Qt.ItemDataRole.UserRole)
                deleted_count += self._delete_files(files)
            
            self.deletion_completed.emit(deleted_count)
            self._show_message("删除完成", f"已删除 {deleted_count} 个重复文件")
            self._display_duplicate_groups()  # 刷新显示
    
    def keep_one_per_group(self):
        """每组保留一个文件"""
        if not self.duplicate_groups:
            self._show_message("提示", "没有检测到重复文件")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认操作",
            "确定要每组保留一个文件吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            kept_count = 0
            deleted_count = 0
            
            for group_id, files in self.duplicate_groups.items():
                if len(files) > 1:
                    # 保留第一个文件，删除其余文件
                    kept_file = files[0]
                    files_to_delete = files[1:]
                    
                    deleted_count += self._delete_files(files_to_delete)
                    kept_count += 1
            
            self.deletion_completed.emit(deleted_count)
            self._show_message("操作完成", f"已保留 {kept_count} 个文件，删除 {deleted_count} 个重复文件")
            self._display_duplicate_groups()  # 刷新显示
    
    def _preview_files(self, files):
        """预览文件列表
        
        Args:
            files: 文件路径列表
        """
        # 实现文件预览逻辑
        preview_dialog = QtWidgets.QDialog(self)
        preview_dialog.setWindowTitle("文件预览")
        
        layout = QtWidgets.QVBoxLayout(preview_dialog)
        list_widget = QtWidgets.QListWidget()
        
        for file_path in files:
            item = QtWidgets.QListWidgetItem(file_path)
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        preview_dialog.exec()
    
    def _delete_files(self, files):
        """删除文件列表
        
        Args:
            files: 文件路径列表
            
        Returns:
            int: 成功删除的文件数量
        """
        deleted_count = 0
        for file_path in files:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    deleted_count += 1
            except Exception as e:
                print(f"删除文件失败 {file_path}: {e}")
        
        return deleted_count
    
    def _show_message(self, title, message):
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
        """
        QtWidgets.QMessageBox.information(self, title, message)