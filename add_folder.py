from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
import os


class FolderPage(QtWidgets.QWidget):
    # 添加信号用于通知主窗口文件夹变化
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_items = []
        self.init_page()
    
    def init_page(self):
        """初始化页面，创建UI组件"""
        # 创建主布局
        main_layout = QtWidgets.QVBoxLayout(self)
        
        # 创建标题标签
        title_label = QtWidgets.QLabel("已添加的文件夹")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        # 创建文件夹列表视图
        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.folder_list)
        
        # 创建按钮布局
        button_layout = QtWidgets.QHBoxLayout()
        
        # 添加文件夹按钮
        self.add_button = QtWidgets.QPushButton("添加文件夹")
        self.add_button.clicked.connect(self.add_folder)
        button_layout.addWidget(self.add_button)
        
        # 移除文件夹按钮
        self.remove_button = QtWidgets.QPushButton("移除选中")
        self.remove_button.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.remove_button)
        
        # 刷新按钮
        self.refresh_button = QtWidgets.QPushButton("刷新列表")
        self.refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
    
    def add_folder(self):
        """打开文件夹选择对话框并添加选择的文件夹"""
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", "", QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path and folder_path not in self.folder_items:
            # 添加文件夹到列表
            self.folder_items.append(folder_path)
            
            # 更新列表视图
            item = QtWidgets.QListWidgetItem(folder_path)
            item.setIcon(QtGui.QIcon.fromTheme("folder"))
            self.folder_list.addItem(item)
            
            # 发送文件夹变化信号
            self.folders_changed.emit(self.folder_items)
    
    def remove_selected(self):
        """移除选中的文件夹"""
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
            
        # 获取要移除的路径
        to_remove = []
        for item in selected_items:
            folder_path = item.text()
            to_remove.append(folder_path)
            
        # 从数据和视图中移除
        for folder_path in to_remove:
            if folder_path in self.folder_items:
                self.folder_items.remove(folder_path)
        
        # 从列表视图中移除选中项
        for item in selected_items:
            self.folder_list.takeItem(self.folder_list.row(item))
        
        # 发送文件夹变化信号
        self.folders_changed.emit(self.folder_items)
    
    def refresh(self):
        """刷新文件夹列表，检查路径有效性"""
        valid_folders = []
        
        # 检查所有文件夹是否仍然存在
        for folder_path in self.folder_items:
            if os.path.isdir(folder_path):
                valid_folders.append(folder_path)
        
        # 更新数据和视图
        self.folder_items = valid_folders
        self.folder_list.clear()
        
        for folder_path in self.folder_items:
            item = QtWidgets.QListWidgetItem(folder_path)
            item.setIcon(QtGui.QIcon.fromTheme("folder"))
            self.folder_list.addItem(item)
        
        # 发送文件夹变化信号
        self.folders_changed.emit(self.folder_items)
    
    def get_all_folders(self):
        """获取所有文件夹"""
        return self.folder_items
    
    def set_folders(self, folders):
        """设置文件夹列表"""
        self.folder_items = folders
        self.refresh()  # 更新视图
