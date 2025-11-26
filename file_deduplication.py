import logging

from PyQt6 import QtWidgets, QtCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileDeduplicationManager(QtWidgets.QWidget):
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.scan_thread = None
        self.duplicate_groups = []
        self.parent.duplicateItemsListWidget.addItem("重复文件组 1")
        self.parent.duplicateItemsListWidget.addItem("重复文件组 2")

        duplicate_groups = ["重复文件组 3", "重复文件组 4", "重复文件组 5"]
        self.parent.duplicateItemsListWidget.addItems(duplicate_groups)

        row_count = 5
        col_count = 3
        self.parent.duplicateFilesTableWidget.setRowCount(row_count)
        self.parent.duplicateFilesTableWidget.setColumnCount(col_count)

        # 步骤2：设置表头（列名）
        headers = ["文件路径", "文件大小(KB)", "修改时间"]
        self.parent.duplicateFilesTableWidget.setHorizontalHeaderLabels(headers)
