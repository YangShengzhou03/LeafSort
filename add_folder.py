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
            has_text_browser = (hasattr(self, 'textBrowser_import_info') or 
                              (has_parent and hasattr(self.parent, 'textBrowser_import_info')))
            
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
                    except Exception as e:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "验证错误",
                            f"验证文件夹关系时出错：{str(e)}",
                            QtWidgets.QMessageBox.StandardButton.Ok
                        )
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
                except (OSError, FileNotFoundError) as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "访问错误",
                        f"无法访问目标文件夹：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                except PermissionError as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "权限错误",
                        f"没有权限访问目标文件夹：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "检查错误",
                        f"检查目标文件夹状态时出错：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
            
            text_browser = None
            if hasattr(self, 'textBrowser_import_info'):
                text_browser = self.textBrowser_import_info
            elif has_parent and hasattr(self.parent, 'textBrowser_import_info'):
                text_browser = self.parent.textBrowser_import_info
                
            if text_browser and title == "选择源文件夹":
                try:
                    text_browser.setText(self.get_folder_info(selected_path))
                except Exception as e:
                    text_browser.setText(f"获取文件夹信息时出错：{str(e)}")
                    QtWidgets.QMessageBox.warning(
                        self,
                        "信息显示错误",
                        f"无法显示文件夹信息：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                    
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
        
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "操作失败",
                f"浏览文件夹时发生未知错误：{str(e)}",
                QtWidgets.QMessageBox.StandardButton.Ok
            )
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
                
        except (OSError, ValueError):
            return False
            
        return True
    
    def get_all_folders(self):
        try:
            if self.parent and hasattr(self.parent, 'inputSourceFolder'):
                source_path = self.parent.inputSourceFolder.text().strip()
                if source_path and os.path.exists(source_path) and os.path.isdir(source_path):
                    return [source_path]
            return []
        except Exception:
            return []
            
    def get_target_folder(self):
        try:
            if self.parent and hasattr(self.parent, 'inputTargetFolder'):
                target_path = self.parent.inputTargetFolder.text().strip()
                if target_path and os.path.exists(target_path) and os.path.isdir(target_path):
                    return target_path
            return None
        except Exception:
            return None
    
    def get_folder_info(self, folder_path):
        info_lines = [
            "=== 待处理的源文件夹信息 ===",
            f"路径：{folder_path}"
        ]
        
        file_count = 0
        directory_count = 0
        total_items = 0
        error_message = ""
        skipped_items_count = 0
        
        try:
            if not os.path.exists(folder_path):
                error_message = "指定的文件夹路径不存在"
            elif not os.path.isdir(folder_path):
                error_message = "指定的路径不是一个文件夹"
            else:
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
                        except (OSError, PermissionError):
                            skipped_items_count += 1
                            continue
                        except Exception:
                            skipped_items_count += 1
                            continue
                except (OSError, FileNotFoundError) as e:
                    error_message = f"无法访问文件夹内容：{str(e)}"
                except PermissionError as e:
                    error_message = f"没有权限访问文件夹内容：{str(e)}"
                except Exception as e:
                    error_message = f"读取文件夹内容时发生未知错误：{str(e)}"
        except Exception as e:
            error_message = f"验证文件夹时发生错误：{str(e)}"
        
        if error_message:
            info_lines.append(f"\n错误：{error_message}")
        
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
