from PyQt6 import QtWidgets


class FolderPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_items = []
    
    def init_page(self):
        """初始化页面"""
        # 页面初始化逻辑
        pass
    
    def refresh(self):
        """刷新文件夹列表"""
        # 简单实现：清空现有列表
        self.folder_items.clear()
        
    def get_all_folders(self):
        """获取所有文件夹"""
        return self.folder_items
