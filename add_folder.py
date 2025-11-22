from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt, pyqtSignal
import os


class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_items = []
        self.init_page()
    
    def init_page(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        
        title_label = QtWidgets.QLabel("已添加的文件夹")
        title_font = title_label.font()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title_label.setFont(title_font)
        main_layout.addWidget(title_label)
        
        self.folder_list = QtWidgets.QListWidget()
        self.folder_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        main_layout.addWidget(self.folder_list)
        
        button_layout = QtWidgets.QHBoxLayout()
        
        self.add_button = QtWidgets.QPushButton("添加文件夹")
        self.add_button.clicked.connect(self.add_folder)
        button_layout.addWidget(self.add_button)
        
        self.remove_button = QtWidgets.QPushButton("移除选中")
        self.remove_button.clicked.connect(self.remove_selected)
        button_layout.addWidget(self.remove_button)
        
        self.refresh_button = QtWidgets.QPushButton("刷新列表")
        self.refresh_button.clicked.connect(self.refresh)
        button_layout.addWidget(self.refresh_button)
        
        main_layout.addLayout(button_layout)
    
    def add_folder(self):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(
            self, "选择文件夹", "", QtWidgets.QFileDialog.Option.ShowDirsOnly
        )
        
        if folder_path and folder_path not in self.folder_items:
            self.folder_items.append(folder_path)
            
            item = QtWidgets.QListWidgetItem(folder_path)
            item.setIcon(QtGui.QIcon.fromTheme("folder"))
            self.folder_list.addItem(item)
            
            self.folders_changed.emit(self.folder_items)
    
    def remove_selected(self):
        selected_items = self.folder_list.selectedItems()
        if not selected_items:
            return
            
        to_remove = []
        for item in selected_items:
            folder_path = item.text()
            to_remove.append(folder_path)
            
        for folder_path in to_remove:
            if folder_path in self.folder_items:
                self.folder_items.remove(folder_path)
        
        for item in selected_items:
            self.folder_list.takeItem(self.folder_list.row(item))
        
        self.folders_changed.emit(self.folder_items)
    
    def refresh(self):
        valid_folders = []
        
        for folder_path in self.folder_items:
            if os.path.isdir(folder_path):
                valid_folders.append(folder_path)
        
        self.folder_items = valid_folders
        self.folder_list.clear()
        
        for folder_path in self.folder_items:
            item = QtWidgets.QListWidgetItem(folder_path)
            item.setIcon(QtGui.QIcon.fromTheme("folder"))
            self.folder_list.addItem(item)
        
        self.folders_changed.emit(self.folder_items)
    
    def get_all_folders(self):
        return self.folder_items
    
    def set_folders(self, folders):
        self.folder_items = folders
        self.refresh()
