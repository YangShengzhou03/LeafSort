from PyQt6.QtWidgets import QWidget


class RemoveDuplicationPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.hash_dict = {}
        self.duplicate_groups = []
        self.current_group_index = -1
    
    def init_page(self):
        """初始化页面"""
        # 页面初始化逻辑
        pass