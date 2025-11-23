import os
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal


class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.parent.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
        self.parent.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
    def _browse_directory(self, title, line_edit):
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, title, line_edit.text() or "")
        if not folder_path:
            return
            
        line_edit.setText(folder_path)
        
        if hasattr(self, 'textBrowser_import_info'):
            text_browser = self.textBrowser_import_info
        elif self.parent and hasattr(self.parent, 'textBrowser_import_info'):
            text_browser = self.parent.textBrowser_import_info
        else:
            text_browser = None
            
        if text_browser:
            text_browser.setText(self.get_folder_info(folder_path))
            
        if not self.parent or not hasattr(self.parent, 'importStatus'):
            return
            
        if title == "选择源文件夹":
            self.parent.importStatus.setText("源文件夹已选择")
        elif title == "选择目标文件夹":
            self.parent.importStatus.setText("目标文件夹已选择")
            
        if hasattr(self.parent, 'inputSourceFolder') and hasattr(self.parent, 'inputTargetFolder'):
            if self.parent.inputSourceFolder.text().strip() and self.parent.inputTargetFolder.text().strip():
                self.parent.importStatus.setText("文件夹导入完成")
    
    def get_folder_info(self, folder_path):
        info = f"=== 待处理的源文件夹信息 ===\n"
        info += f"路径：{folder_path}\n"
        
        top_file_count = 0
        top_folder_count = 0
        try:
            items = os.listdir(folder_path)
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    top_file_count += 1
                elif os.path.isdir(item_path):
                    top_folder_count += 1
        except (OSError, FileNotFoundError, PermissionError):
            pass
        
        info += f"\n{'-' * 10}注意！会递归遍历处理子文件夹{'-' * 10}\n"
        info += f"{'顶层内容统计':<60}\n"
        info += f"{'顶层文件数量：' + str(top_file_count):<30} {'顶层文件夹数量：' + str(top_folder_count):<30}\n"
        info += f"{'-' * 60}\n"        
        return info
