from PyQt6.QtCore import QObject


class RemoveDuplicationPage(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.hash_dict = {}
        self.duplicate_groups = []
        self.current_group_index = -1