import os
import logging
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from config_manager import config_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FolderPage(QtWidgets.QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent

        
        self._load_saved_folders()
        self._setup_drag_drop()

        self.parent.btnBrowseSource.clicked.connect(
            lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
        self.parent.btnBrowseTarget.clicked.connect(
            lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
        
        self.parent.inputSourceFolder.textChanged.connect(
            lambda: self._save_folder_path("source_folder", self.parent.inputSourceFolder.text()))
        self.parent.inputTargetFolder.textChanged.connect(
            lambda: self._save_folder_path("target_folder", self.parent.inputTargetFolder.text()))
    
    def _setup_drag_drop(self):
        self.parent.frameSourceFolderGroup.setAcceptDrops(True)
        self.parent.frameTargetFolderGroup.setAcceptDrops(True)
        
        def create_drag_drop_handlers(folder_type):
            def dragEnterEvent(event):
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                else:
                    event.ignore()
            
            def dragMoveEvent(event):
                if event.mimeData().hasUrls():
                    event.acceptProposedAction()
                else:
                    event.ignore()
            
            def dropEvent(event):
                urls = event.mimeData().urls()
                if urls:
                    file_path = urls[0].toLocalFile()
                    if os.path.isdir(file_path):
                        title = "选择源文件夹" if folder_type == "source" else "选择目标文件夹"
                        line_edit = self.parent.inputSourceFolder if folder_type == "source" else self.parent.inputTargetFolder
                        
                        if self._validate_folder_selection(file_path, title, line_edit.text(), line_edit):
                            line_edit.setText(file_path)
                            if folder_type == "source":
                                self._update_folder_info_display(file_path)
                            self._update_import_status(title)
                            logger.info(f"通过拖放导入{title}: {file_path}")
                        event.acceptProposedAction()
                    else:
                        QtWidgets.QMessageBox.warning(self, "拖放错误", "请拖放文件夹而不是文件")
                        event.ignore()
                else:
                    event.ignore()
            
            return dragEnterEvent, dragMoveEvent, dropEvent
        
        source_dragEnter, source_dragMove, source_drop = create_drag_drop_handlers("source")
        target_dragEnter, target_dragMove, target_drop = create_drag_drop_handlers("target")
        
        self.parent.frameSourceFolderGroup.dragEnterEvent = source_dragEnter
        self.parent.frameSourceFolderGroup.dragMoveEvent = source_dragMove
        self.parent.frameSourceFolderGroup.dropEvent = source_drop
        self.parent.frameTargetFolderGroup.dragEnterEvent = target_dragEnter
        self.parent.frameTargetFolderGroup.dragMoveEvent = target_dragMove
        self.parent.frameTargetFolderGroup.dropEvent = target_drop
    
    def _load_saved_folders(self):
        try:
            source_folder = config_manager.get_setting("source_folder", "")
            if source_folder and os.path.exists(source_folder):
                self.parent.inputSourceFolder.setText(source_folder)
                logger.info(f"已加载保存的源文件夹: {source_folder}")
                self._update_folder_info_display(source_folder)
            
            target_folder = config_manager.get_setting("target_folder", "")
            if target_folder and os.path.exists(target_folder):
                self.parent.inputTargetFolder.setText(target_folder)
                logger.info(f"已加载保存的目标文件夹: {target_folder}")
                
            self._update_import_status("")
        except Exception as e:
            logger.error(f"加载保存的文件夹路径时出错: {str(e)}")
    
    def _save_folder_path(self, setting_key, folder_path):
        try:
            config_manager.update_setting(setting_key, folder_path)
            logger.info(f"已保存{setting_key}: {folder_path}")
        except Exception as e:
            logger.error(f"保存{setting_key}时出错: {str(e)}")
    
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
            line_edit.setText(original_path)

    def _validate_folder_selection(self, selected_path, title, original_path, line_edit):
        source_path = self.parent.inputSourceFolder.text().strip()
        target_path = self.parent.inputTargetFolder.text().strip()

        if title == "选择源文件夹":
            source_path = selected_path
        else:
            target_path = selected_path

        if source_path and target_path:
            if not self._check_folder_relationship(source_path, target_path):
                QtWidgets.QMessageBox.warning(self, "文件夹选择错误",
                                              "源文件夹和目标文件夹不能相同，也不能存在隶属关系。",
                                              QtWidgets.QMessageBox.StandardButton.Ok)
                line_edit.setText(original_path)
                return False

        if title == "选择目标文件夹":
            try:
                items = os.listdir(selected_path)
                if items:
                    QtWidgets.QMessageBox.warning(self, "请注意，这不是一个空文件夹", "目标文件夹不是空文件夹，但这不影响您继续。",
                                                  QtWidgets.QMessageBox.StandardButton.Ok)
            except Exception as e:
                logger.warning(f"检查目标文件夹是否为空时出错: {str(e)}")

        return True

    def _update_folder_info_display(self, folder_path):
        try:
            self.parent.textBrowser_import_info.setText(self.get_folder_info(folder_path))
        except Exception as e:
            logger.error(f"更新文件夹信息显示时出错: {str(e)}")

    def _update_import_status(self, title):
        try:
            if title == "选择源文件夹":
                self.parent.importStatus.setText("源文件夹已选择")
            elif title == "选择目标文件夹":
                self.parent.importStatus.setText("目标文件夹已选择")

            source_path = self.parent.inputSourceFolder.text().strip()
            target_path = self.parent.inputTargetFolder.text().strip()
            if source_path and target_path:
                self.parent.importStatus.setText("文件夹导入完成")
        except Exception as e:
            logger.error(f"更新导入状态时出错: {str(e)}")

    def _check_folder_relationship(self, folder1, folder2):
        if not folder1 or not folder2:
            return True

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

        return True

    def get_all_folders(self):
        source_path = self.parent.inputSourceFolder.text().strip()
        if source_path and os.path.exists(source_path) and os.path.isdir(source_path):
            return [source_path]
        elif source_path:
            logger.warning("源文件夹不存在或不是有效目录")
        return []

    def get_target_folder(self):
        target_path = self.parent.inputTargetFolder.text().strip()
        if target_path and os.path.exists(target_path) and os.path.isdir(target_path):
            return target_path
        elif target_path:
            logger.warning("目标文件夹不存在或不是有效目录")
        return None

    def get_folder_info(self, folder_path):
        info_lines = ["=" * 15 + "待处理的源文件夹信息" + "=" * 15, f"路径：{folder_path}"]

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

        info_lines.extend(["", "-" * 20 + "注意！会递归遍历处理子文件夹" + "-" * 20, "顶层内容统计",
                           f"顶层文件数量：{file_count}       顶层文件夹数量：{directory_count}       总计：{total_items}",
                           "-" * 75, " LeafSort（轻羽媒体整理） © 2026 Yangshengzhou.All Rights Reserved "])

        return '\n'.join(info_lines)
