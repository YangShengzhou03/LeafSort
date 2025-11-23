"""
文件夹管理页面模块

该模块定义了FolderPage类，用于管理应用程序的文件夹导入和管理功能。
包含文件夹添加、删除、列表显示等核心功能。
"""

from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
import os

from config_manager import config_manager


class FolderPage(QtWidgets.QWidget):
    """文件夹管理页面类"""
    
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        """初始化文件夹管理页面
        
        Args:
            parent: 父组件
        """
        super().__init__(parent)
        self.parent = parent
        self.folders = []
        
        self.init_page()
        self.load_folders()
    
    def init_page(self):
        """初始化页面UI"""
        # 主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 添加文件夹按钮区域
        self._add_folder_controls(main_layout)
        
        # 文件夹列表区域
        self._add_folder_list(main_layout)
        
        # 操作按钮区域
        self._add_action_buttons(main_layout)
    
    def _add_folder_controls(self, main_layout):
        """添加文件夹控制区域"""
        control_layout = QtWidgets.QHBoxLayout()
        
        # 添加文件夹按钮
        self.add_folder_btn = QtWidgets.QPushButton("添加文件夹")
        self.add_folder_btn.clicked.connect(self.add_folder)
        control_layout.addWidget(self.add_folder_btn)
        
        # 包含子文件夹复选框
        self.include_sub_checkbox = QtWidgets.QCheckBox("包含子文件夹")
        self.include_sub_checkbox.setChecked(True)
        control_layout.addWidget(self.include_sub_checkbox)
        
        control_layout.addStretch()
        main_layout.addLayout(control_layout)
    
    def _add_folder_list(self, main_layout):
        """添加文件夹列表区域"""
        # 文件夹列表标签
        folder_label = QtWidgets.QLabel("已导入的文件夹:")
        main_layout.addWidget(folder_label)
        
        # 文件夹列表
        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.folder_list)
    
    def _add_action_buttons(self, main_layout):
        """添加操作按钮区域"""
        button_layout = QtWidgets.QHBoxLayout()
        
        # 移除选中文件夹按钮
        self.remove_btn = QtWidgets.QPushButton("移除选中")
        self.remove_btn.clicked.connect(self.remove_selected_folders)
        button_layout.addWidget(self.remove_btn)
        
        # 清空所有文件夹按钮
        self.clear_btn = QtWidgets.QPushButton("清空所有")
        self.clear_btn.clicked.connect(self.clear_all_folders)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def add_folder(self):
        """添加文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, 
            "选择文件夹",
            options=QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path:
            include_sub = self.include_sub_checkbox.isChecked()
            success = config_manager.add_folder(folder_path, include_sub)
            
            if success:
                self.load_folders()
                self.folders_changed.emit(self.folders)
                self._show_message("添加成功", f"文件夹 '{os.path.basename(folder_path)}' 已成功添加")
            else:
                self._show_message("添加失败", "文件夹添加失败，请检查路径是否有效")
    
    def remove_selected_folders(self):
        """移除选中的文件夹"""
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            self._show_message("提示", "请先选择要移除的文件夹")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认移除",
            f"确定要移除选中的 {len(selected_items)} 个文件夹吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            removed_count = 0
            for item in selected_items:
                folder_path = item.data(Qt.ItemDataRole.UserRole)
                if config_manager.remove_folder(folder_path):
                    removed_count += 1
            
            if removed_count > 0:
                self.load_folders()
                self.folders_changed.emit(self.folders)
                self._show_message("移除成功", f"已成功移除 {removed_count} 个文件夹")
    
    def clear_all_folders(self):
        """清空所有文件夹"""
        if not self.folders:
            self._show_message("提示", "当前没有导入任何文件夹")
            return
        
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有文件夹吗？此操作不可撤销。",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            if config_manager.clear_folders():
                self.load_folders()
                self.folders_changed.emit(self.folders)
                self._show_message("清空成功", "所有文件夹已成功清空")
    
    def load_folders(self):
        """加载文件夹列表"""
        self.folders = config_manager.get_valid_folders()
        self.folder_list.clear()
        
        for folder in self.folders:
            folder_path = folder['path']
            include_sub = folder.get('include_sub', True)
            
            item = QtWidgets.QListWidgetItem()
            item.setText(f"{folder_path} {'(包含子文件夹)' if include_sub else '(不包含子文件夹)'}")
            item.setData(Qt.ItemDataRole.UserRole, folder_path)
            self.folder_list.addItem(item)
    
    def get_all_folders(self):
        """获取所有文件夹
        
        Returns:
            list: 文件夹信息列表
        """
        return self.folders
    
    def get_valid_folders(self):
        """获取有效文件夹
        
        Returns:
            list: 有效文件夹信息列表
        """
        return [folder for folder in self.folders 
                if os.path.exists(folder['path']) and os.path.isdir(folder['path'])]
    
    def _show_message(self, title, message):
        """显示消息对话框
        
        Args:
            title: 对话框标题
            message: 消息内容
        """
        QtWidgets.QMessageBox.information(self, title, message)