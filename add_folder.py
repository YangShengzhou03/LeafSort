import os
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal

class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.parent.btnBrowseSource.clicked.connect(
            lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
        self.parent.btnBrowseTarget.clicked.connect(
            lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
    def _browse_directory(self, title, line_edit):
        original_path = line_edit.text()
        
        try:
            selected_path = QtWidgets.QFileDialog.getExistingDirectory(self, title, original_path or "")
            
            if not selected_path:
                return
                
            line_edit.setText(selected_path)
            
            has_parent = self.parent is not None
            has_source_folder = has_parent and hasattr(self.parent, 'inputSourceFolder')
            has_target_folder = has_parent and hasattr(self.parent, 'inputTargetFolder')
            has_import_status = has_parent and hasattr(self.parent, 'importStatus')
            
            if has_source_folder and has_target_folder:
                source_path = self.parent.inputSourceFolder.text().strip()
                target_path = self.parent.inputTargetFolder.text().strip()
                
                if source_path and target_path:
                    try:
                        if not self._check_folder_relationship(source_path, target_path):
                            QtWidgets.QMessageBox.warning(
                                self,
                                "文件夹选择错误",
                                "源文件夹和目标文件夹不能相同，也不能存在隶属关系。",
                                QtWidgets.QMessageBox.StandardButton.Ok
                            )
                            line_edit.setText(original_path)
                            return
                    except Exception:
                        line_edit.setText(original_path)
                        return
            
            if title == "选择目标文件夹":
                try:
                    items = os.listdir(selected_path)
                    if items:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "注意",
                            "目标文件夹不是一个空文件夹。",
                            QtWidgets.QMessageBox.StandardButton.Ok
                        )
                except Exception:
                    pass
            
            text_browser = None
            if hasattr(self, 'textBrowser_import_info'):
                text_browser = self.textBrowser_import_info
            elif has_parent and hasattr(self.parent, 'textBrowser_import_info'):
                text_browser = self.parent.textBrowser_import_info
                
            if text_browser and title == "选择源文件夹":
                try:
                    text_browser.setText(self.get_folder_info(selected_path))
                except Exception:
                    pass
                    
            if has_import_status:
                try:
                    if title == "选择源文件夹":
                        self.parent.importStatus.setText("源文件夹已选择")
                    elif title == "选择目标文件夹":
                        self.parent.importStatus.setText("目标文件夹已选择")
                    
                    if has_source_folder and has_target_folder:
                        source_path = self.parent.inputSourceFolder.text().strip()
                        target_path = self.parent.inputTargetFolder.text().strip()
                        if source_path and target_path:
                            self.parent.importStatus.setText("文件夹导入完成")
                except Exception:
                    pass
        
        except Exception:
            if hasattr(line_edit, 'setText'):
                line_edit.setText(original_path)
    
    def _check_folder_relationship(self, folder1, folder2):
        if not folder1 or not folder2:
            return True
            
        try:
            normalized_folder1 = os.path.normpath(os.path.abspath(folder1)).lower()
            normalized_folder2 = os.path.normpath(os.path.abspath(folder2)).lower()
            
            if normalized_folder1 == normalized_folder2:
                return False
                
            folder1_full = os.path.join(normalized_folder1, '')
            folder2_full = os.path.join(normalized_folder2, '')
            
            if folder1_full.startswith(folder2_full) or folder2_full.startswith(folder1_full):
                return False
                
        except Exception:
            return False
            
        return True
    
    def get_all_folders(self):
        try:
            if self.parent and hasattr(self.parent, 'inputSourceFolder'):
                source_path = self.parent.inputSourceFolder.text().strip()
                if source_path and os.path.exists(source_path) and os.path.isdir(source_path):
                    return [source_path]
        except Exception:
            pass
        return []
            
    def get_target_folder(self):
        try:
            if self.parent and hasattr(self.parent, 'inputTargetFolder'):
                target_path = self.parent.inputTargetFolder.text().strip()
                if target_path and os.path.exists(target_path) and os.path.isdir(target_path):
                    return target_path
        except Exception:
            pass
        return None
    
    def get_folder_info(self, folder_path):
        info_lines = [
            "=== 待处理的源文件夹信息 ===",
            f"路径：{folder_path}"
        ]
        
        file_count = 0
        directory_count = 0
        total_items = 0
        skipped_items_count = 0
        
        try:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                try:
                    items = os.listdir(folder_path)
                    total_items = len(items)
                    
                    for item_name in items:
                        item_full_path = os.path.join(folder_path, item_name)
                        try:
                            if os.path.isfile(item_full_path):
                                file_count += 1
                            elif os.path.isdir(item_full_path):
                                directory_count += 1
                        except Exception:
                            skipped_items_count += 1
                            continue
                except Exception:
                    pass
        except Exception:
            pass
        
        if skipped_items_count > 0:
            info_lines.append(f"\n注意：跳过了 {skipped_items_count} 个无法访问的项目")
        
        info_lines.extend([
            "",
            "-" * 10 + "注意！会递归遍历处理子文件夹" + "-" * 10,
            "顶层内容统计                               ",
            f"顶层文件数量：{file_count}       顶层文件夹数量：{directory_count}       总计：{total_items}",
            "-" * 75
        ])
        
        return '\n'.join(info_lines)