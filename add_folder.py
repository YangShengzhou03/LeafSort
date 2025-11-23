"""
文件夹页面
"""

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, pyqtSignal
import os

from config_manager import config_manager

class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        
        # 连接浏览文件夹按钮的信号
        self.parent.btnBrowseSource.clicked.connect(lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
        self.parent.btnBrowseTarget.clicked.connect(lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
    def _browse_directory(self, title, line_edit):
        """
        浏览并选择文件夹
        
        Args:
            title: 对话框标题
            line_edit: 用于显示选择路径的QLineEdit
        """
        folder_path = QtWidgets.QFileDialog.getExistingDirectory(self, title, line_edit.text() or "")
        if folder_path:
            line_edit.setText(folder_path)
            # 如果有textBrowser_import_info控件，显示文件夹信息
            if hasattr(self, 'textBrowser_import_info'):
                self.textBrowser_import_info.setText(self.get_folder_info(folder_path))
            elif self.parent and hasattr(self.parent, 'textBrowser_import_info'):
                self.parent.textBrowser_import_info.setText(self.get_folder_info(folder_path))
    
    
    def get_folder_info(self, folder_path):
        """
        获取文件夹的极速信息，完全避免任何递归操作，适用于超大文件夹
        
        Args:
            folder_path: 文件夹路径
            
        Returns:
            包含文件夹信息的字符串
        """
        # 构建信息字符串，使用两列布局
        info = f"=== 待处理的源文件夹信息 ===\n"
        info += f"路径：{folder_path}\n"
        
        # 只获取顶层文件夹信息，完全避免任何递归操作
        top_file_count = 0
        top_folder_count = 0
        try:
            # 只列出顶层内容，不递归
            items = os.listdir(folder_path)
            for item in items:
                item_path = os.path.join(folder_path, item)
                if os.path.isfile(item_path):
                    top_file_count += 1
                elif os.path.isdir(item_path):
                    top_folder_count += 1
        except (OSError, FileNotFoundError, PermissionError) as e:
            pass
        
        # 使用两列布局显示信息
        info += f"\n{'-' * 60}\n"
        info += f"{'顶层内容统计':<60}\n"
        info += f"{'顶层文件数量：' + str(top_file_count):<30} {'顶层文件夹数量：' + str(top_folder_count):<30}\n"
        info += f"{'-' * 60}\n"        
        return info
