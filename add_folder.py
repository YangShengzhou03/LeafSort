import os
import logging
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal, Qt

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FolderPage(QtWidgets.QWidget):
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        
        if hasattr(self.parent, 'btnBrowseSource') and hasattr(self.parent, 'inputSourceFolder'):
            self.parent.btnBrowseSource.clicked.connect(
                lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
                
        if hasattr(self.parent, 'btnBrowseTarget') and hasattr(self.parent, 'inputTargetFolder'):
            self.parent.btnBrowseTarget.clicked.connect(
                lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
    def _browse_directory(self, title, line_edit):
        original_path = line_edit.text()
        
        try:
            selected_path = QtWidgets.QFileDialog.getExistingDirectory(self, title, original_path or "")
            
            if not selected_path:
                return  
                
            if not self._validate_folder_selection(selected_path, title, original_path, line_edit):
                return
                
            line_edit.setText(selected_path)
            
            if title == "选择源文件夹":
                self._update_folder_info_display(selected_path)
            
            self._update_import_status(title)
                
        except Exception as e:
            logger.error(f"浏览目录时出错: {str(e)}")
            if hasattr(line_edit, 'setText'):
                line_edit.setText(original_path)
    
    def _validate_folder_selection(self, selected_path, title, original_path, line_edit):
        if (hasattr(self.parent, 'inputSourceFolder') and hasattr(self.parent, 'inputTargetFolder')):
            source_path = self.parent.inputSourceFolder.text().strip()
            target_path = self.parent.inputTargetFolder.text().strip()
            
            if title == "选择源文件夹":
                source_path = selected_path
            else:
                target_path = selected_path
            
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
                        return False
                except Exception as e:
                    logger.error(f"检查文件夹关系时出错: {str(e)}")
                    line_edit.setText(original_path)
                    return False
        
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
            except Exception as e:
                logger.warning(f"检查目标文件夹是否为空时出错: {str(e)}")
        
        return True
    
    def _update_folder_info_display(self, folder_path):
        text_browser = None
        if hasattr(self, 'textBrowser_import_info'):
            text_browser = self.textBrowser_import_info
        elif self.parent and hasattr(self.parent, 'textBrowser_import_info'):
            text_browser = self.parent.textBrowser_import_info
            
        if text_browser:
            try:
                text_browser.setText(self.get_folder_info(folder_path))
            except Exception as e:
                logger.error(f"更新文件夹信息显示时出错: {str(e)}")
    
    def _update_import_status(self, title):
        if self.parent and hasattr(self.parent, 'importStatus'):
            try:
                if title == "选择源文件夹":
                    self.parent.importStatus.setText("源文件夹已选择")
                elif title == "选择目标文件夹":
                    self.parent.importStatus.setText("目标文件夹已选择")
                
                if (hasattr(self.parent, 'inputSourceFolder') and 
                    hasattr(self.parent, 'inputTargetFolder')):
                    source_path = self.parent.inputSourceFolder.text().strip()
                    target_path = self.parent.inputTargetFolder.text().strip()
                    if source_path and target_path:
                        self.parent.importStatus.setText("文件夹导入完成")
            except Exception as e:
                logger.error(f"更新导入状态时出错: {str(e)}")
    
    def _check_folder_relationship(self, folder1, folder2):
        if not folder1 or not folder2:
            return True
            
        try:
            normalized_folder1 = os.path.normpath(os.path.abspath(folder1)).lower()
            normalized_folder2 = os.path.normpath(os.path.abspath(folder2)).lower()
            
            if normalized_folder1 == normalized_folder2:
                logger.warning(f"文件夹相同: {normalized_folder1}")
                return False
                
            folder1_full = os.path.join(normalized_folder1, '')
            folder2_full = os.path.join(normalized_folder2, '')
            
            if folder1_full.startswith(folder2_full):
                logger.warning(f"文件夹1包含文件夹2: {folder1_full} -> {folder2_full}")
                return False
                
            if folder2_full.startswith(folder1_full):
                logger.warning(f"文件夹2包含文件夹1: {folder2_full} -> {folder1_full}")
                return False
                
        except Exception as e:
            logger.error(f"检查文件夹关系时出错: {str(e)}")
            return False
            
        return True
    
    def get_all_folders(self):
        try:
            if self.parent and hasattr(self.parent, 'inputSourceFolder'):
                source_path = self.parent.inputSourceFolder.text().strip()
                if source_path and os.path.exists(source_path) and os.path.isdir(source_path):
                    logger.info("获取源文件夹成功")
                    return [source_path]
                elif source_path:
                    logger.warning("源文件夹不存在或不是有效目录")
        except Exception as e:
            logger.error(f"获取源文件夹时出错: {str(e)}")
        return []
            
    def get_target_folder(self):
        try:
            if self.parent and hasattr(self.parent, 'inputTargetFolder'):
                target_path = self.parent.inputTargetFolder.text().strip()
                if target_path and os.path.exists(target_path) and os.path.isdir(target_path):
                    logger.info("获取目标文件夹成功")
                    return target_path
                elif target_path:
                    logger.warning("目标文件夹不存在或不是有效目录")
        except Exception as e:
            logger.error(f"获取目标文件夹时出错: {str(e)}")
        return None
    
    def get_folder_info(self, folder_path):
        info_lines = [
            "=" * 15 + "待处理的源文件夹信息" + "=" * 15,
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
            "-" * 20 + "注意！会递归遍历处理子文件夹" + "-" * 20,
            "顶层内容统计",
            f"顶层文件数量：{file_count}       顶层文件夹数量：{directory_count}       总计：{total_items}",
            "-" * 75,
            " LeafView © 2025 Yangshengzhou.All Rights Reserved "
        ])
        
        return '\n'.join(info_lines)
        
    def _import_folders(self, folders):
        if not folders:
            logger.warning("没有提供要导入的文件夹")
            return
        
        try:
            imported_count = 0
            conflict_count = 0
            
            if not hasattr(self.parent, 'lst_folders'):
                logger.error("父组件没有lst_folders属性")
                return
                
            for folder in folders:
                logger.info(f"尝试导入文件夹: {folder}")
                
                has_conflict = False
                try:
                    for item in self.parent.lst_folders.findItems('', Qt.MatchContains):
                        if not self._check_folder_relationship(folder, item.text()):
                            has_conflict = True
                            conflict_count += 1
                            logger.warning(f"与现有文件夹冲突: {folder} 和 {item.text()}")
                            break
                except Exception as e:
                    logger.error(f"检查文件夹冲突时出错: {str(e)}")
                    continue
                
                target_folder = self.get_target_folder()
                if not has_conflict and target_folder and not self._check_folder_relationship(folder, target_folder):
                    has_conflict = True
                    conflict_count += 1
                    logger.warning(f"与目标文件夹冲突: {folder} 和 {target_folder}")
                
                if not has_conflict and self._is_folder_duplicate(folder):
                    has_conflict = True
                    conflict_count += 1
                    logger.warning(f"文件夹重复: {folder}")
                
                if not has_conflict:
                    self.parent.lst_folders.addItem(folder)
                    imported_count += 1
                    logger.info(f"成功导入文件夹: {folder}")
            
            self._update_status_label(imported_count > 0, 
                                     f"成功导入 {imported_count} 个文件夹" if imported_count > 0 else 
                                     f"未导入文件夹，存在 {conflict_count} 个冲突")
                
        except Exception as e:
            logger.error(f"导入文件夹时出错: {str(e)}")
            self._update_status_label(False, "导入文件夹时出错")
        finally:
            if hasattr(self.parent, 'btn_browse_folder'):
                self.parent.btn_browse_folder.setEnabled(True)
            if hasattr(self.parent, 'btn_import'):
                self.parent.btn_import.setEnabled(True)
            logger.info("文件夹导入操作完成")
            
    def _update_status_label(self, success, message=None):
        if not hasattr(self.parent, 'status_label'):
            logger.error("父组件没有status_label属性")
            return
            
        if success:
            status_text = message if message else "导入成功！"
            self.parent.status_label.setText(status_text)
            self.parent.status_label.setStyleSheet("QLabel { color: green; }")
            logger.info(f"状态更新: {status_text}")
        else:
            status_text = message if message else "导入失败，请检查文件夹路径是否正确或与现有文件夹有冲突"
            self.parent.status_label.setText(status_text)
            self.parent.status_label.setStyleSheet("QLabel { color: red; }")
            logger.warning(f"状态更新: {status_text}")
            
    def _is_folder_duplicate(self, folder):
        if not hasattr(self.parent, 'lst_folders'):
            logger.error("父组件没有lst_folders属性")
            return False
            
        try:
            normalized_folder = os.path.normpath(os.path.abspath(folder)).lower()
            
            for item in self.parent.lst_folders.findItems('', Qt.MatchContains):
                try:
                    normalized_item = os.path.normpath(os.path.abspath(item.text())).lower()
                    if normalized_folder == normalized_item:
                        return True
                except Exception as e:
                    logger.warning(f"检查重复文件夹时出错 (item: {item.text()}): {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"检查重复文件夹时出错 (folder: {folder}): {str(e)}")
        
        return False