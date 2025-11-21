from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QProgressDialog, QVBoxLayout, QPushButton, QTextEdit, QDialog, QHBoxLayout, QScrollArea, QLabel
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QPoint
import os
import pathlib
from collections import Counter

from common import get_resource_path, detect_media_type
from config_manager import config_manager


class FolderPage(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_items = []
        self._batch_adding = False
        # 初始化为字典格式，与_save_tags_state方法保持一致
        self.tags_data = {'available_tags': [], 'selected_tags': []}
        self.init_page()
        # 初始化标签选择UI组件
        self._init_tags_selection_ui()
    
    def _setup_drag_drop(self):
        # 添加属性检查以避免错误
        if hasattr(self.parent, 'widgetAddFolder'):
            self.parent.widgetAddFolder.setAcceptDrops(True)
            self.parent.widgetAddFolder.dragEnterEvent = self.dragEnterEvent
            self.parent.widgetAddFolder.dropEvent = self.dropEvent
    
    def _setup_click_behavior(self):
        # 添加属性检查以避免错误
        if hasattr(self.parent, 'widgetAddFolder'):
            self.parent.widgetAddFolder.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
            self.parent.widgetAddFolder.mousePressEvent = self._open_folder_dialog_on_click

    def _setup_context_menu(self):
        """设置右键菜单"""
        # 添加属性检查以避免错误
        if hasattr(self.parent, 'scrollWelcomeContent'):
            self.parent.scrollWelcomeContent.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
            self.parent.scrollWelcomeContent.customContextMenuRequested.connect(self._show_context_menu)

    def init_page(self):
        self._setup_drag_drop()
        self._setup_click_behavior()
        self._setup_context_menu()
        self._connect_buttons()
        # 从配置中加载已保存的文件夹
        self._load_saved_folders()

    def _connect_buttons(self):
        # 添加属性检查以避免错误
        if hasattr(self.parent, 'btnAddFolder'):
            self.parent.btnAddFolder.clicked.connect(self._open_folder_dialog)
    
    def _remove_all_folders(self):
        """移除所有文件夹"""
        if not self.folder_items:
            return
            
        reply = QtWidgets.QMessageBox.question(
            self, 
            "确认移除", 
            f"确定要移除所有 {len(self.folder_items)} 个文件夹吗？",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No
        )
        
        if reply == QtWidgets.QMessageBox.StandardButton.Yes:
            # 复制列表避免修改时出错
            items_copy = self.folder_items.copy()
            for item in items_copy:
                self.remove_folder_item(item['frame'])
    
    def _open_folder_dialog_on_click(self, event):
        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            self._open_folder_dialog()

    def _open_folder_dialog(self):
        # 使用多选对话框，允许用户一次选择多个文件夹
        folder_paths = QFileDialog.getExistingDirectory(self, "选择文件夹", options=QFileDialog.Option.DontUseNativeDialog)
        if folder_paths:
            # 如果只选择了一个文件夹，直接处理
            if ';' not in folder_paths:
                self._check_and_add_folder(folder_paths)
            else:
                # 批量添加多个文件夹
                self._batch_adding = True
                try:
                    # 显示进度对话框
                    progress_dialog = QProgressDialog("正在添加文件夹...", "取消", 0, folder_paths.count(';') + 1, self)
                    progress_dialog.setWindowTitle("批量添加")
                    progress_dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
                    progress_dialog.setValue(0)
                    
                    # 分割路径并逐个处理
                    paths = folder_paths.split(';')
                    for i, path in enumerate(paths):
                        if progress_dialog.wasCanceled():
                            break
                        
                        progress_dialog.setValue(i)
                        self._check_and_add_folder(path)
                        
                        # 允许UI更新
                        QtWidgets.QApplication.processEvents()
                    
                    progress_dialog.setValue(len(paths))
                finally:
                    self._batch_adding = False

    def _check_and_add_folder(self, folder_path):
        try:
            folder_path = os.path.normpath(folder_path)
            folder_name = os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path
            
            # 基本验证 - 统一错误信息收集
            error_messages = []
            
            if not folder_path:
                return
                
            if not os.path.exists(folder_path):
                error_messages.append(f"文件夹路径不存在: {folder_path}")
            elif not os.path.isdir(folder_path):
                error_messages.append(f"选择的路径不是一个文件夹: {folder_path}")
            else:
                try:
                    os.listdir(folder_path)
                except PermissionError:
                    error_messages.append(f"没有足够的权限访问文件夹: {folder_path}")
                except Exception as e:
                    error_messages.append(f"访问文件夹时发生错误: {folder_path}\n错误信息: {str(e)}")
            
            # 检查是否已存在
            for item in self.folder_items:
                if self._paths_equal(item['path'], folder_path):
                    # 在批量添加时静默跳过已存在的文件夹，不再显示对话框
                    if self._batch_adding:
                        return
                    QMessageBox.information(
                        self, 
                        "路径已存在", 
                        f"文件夹 '{folder_name}' 已经添加\n无需重复添加相同的文件夹。"
                    )
                    return
            
            # 路径冲突检查和智能处理
            conflict_info = self._check_path_conflicts(folder_path)
            
            # 如果在批量添加过程中，简化冲突处理逻辑
            if self._batch_adding:
                if conflict_info:
                    # 批量添加时自动处理常见冲突
                    if conflict_info['type'] == 1:
                        # 自动取消父文件夹的子文件夹选项
                        for item in self.folder_items:
                            if self._paths_equal(item['path'], conflict_info['parent_path']):
                                item['checkbox'].setChecked(False)
                                config_manager.update_folder_include_sub(item['path'], False)
                                break
                    # 对于子文件夹冲突，批量添加时直接跳过
                    elif conflict_info['type'] == 2:
                        return
                # 有错误时静默跳过
                if error_messages:
                    return
            else:
                # 非批量添加时显示错误
                if error_messages:
                    QMessageBox.warning(
                        self, 
                        "添加失败", 
                        "\n".join(error_messages)
                    )
                    return
                
                # 非批量添加时进行标准冲突处理
                if conflict_info:
                    if not self._handle_path_conflict(conflict_info, folder_path, folder_name):
                        return
            
            # 创建文件夹项
            self._create_folder_item(folder_path, folder_name)
            
            # 仅在非批量模式下检查媒体文件
            if not self._batch_adding:
                self._check_media_files(folder_path)
            
        except Exception as e:
            # 批量添加时静默捕获错误
            if not self._batch_adding:
                QMessageBox.critical(
                    self, 
                    "添加失败", 
                    f"添加文件夹时发生错误：{str(e)}\n请检查文件夹路径和权限后重试。"
                )

    def _create_folder_item(self, folder_path, folder_name):
        folder_frame = QtWidgets.QFrame(parent=self.parent.scrollWelcomeContent)
        folder_frame.setFixedHeight(48)
        folder_frame.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.ArrowCursor))
        layout = QtWidgets.QHBoxLayout(folder_frame)
        layout.setContentsMargins(8, 0, 8, 0)
        layout.setSpacing(10)

        icon_widget = QtWidgets.QWidget(parent=folder_frame)
        icon_widget.setFixedSize(42, 42)
        icon_widget.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        icon_widget.setStyleSheet(f"image: url({get_resource_path('resources/img/page_0/导入文件夹.svg')}); background-color: transparent;")

        text_layout = QtWidgets.QVBoxLayout()
        text_layout.setSpacing(2)
        text_layout.setContentsMargins(0, 0, 0, 0)

        name_label = QtWidgets.QLabel(folder_name, parent=folder_frame)
        name_label.setMaximumWidth(180)
        name_label.setFont(QtGui.QFont("微软雅黑", 12))
        name_label.setStyleSheet(
            "QLabel {background: transparent; border: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #333; font-weight: 500;}")

        path_label = QtWidgets.QLabel(folder_path, parent=folder_frame)
        path_label.setMaximumWidth(180)
        path_label.setFont(QtGui.QFont("微软雅黑", 9))
        path_label.setStyleSheet(
            "QLabel {background: transparent; border: none; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #666;}")

        text_layout.addWidget(name_label)
        text_layout.addWidget(path_label)

        include_checkbox = QtWidgets.QCheckBox("包含子文件夹", parent=folder_frame)
        include_checkbox.setFont(QtGui.QFont("微软雅黑", 9))
        include_checkbox.setStyleSheet("QCheckBox {spacing: 4px; background: transparent; color: #666;}")
        include_checkbox.stateChanged.connect(lambda state, f=folder_frame: self._update_include_sub(f, state))
        include_checkbox.setChecked(True)

        remove_button = QtWidgets.QPushButton("移除", parent=folder_frame)
        remove_button.setFixedSize(60, 30)
        remove_button.setFont(QtGui.QFont("微软雅黑", 9))
        remove_button.setStyleSheet(
            "QPushButton {background-color: #FF5A5A; color: white; border: none; border-radius: 6px; font-weight: 500;} QPushButton:hover {background-color: #FF3B3B;} QPushButton:pressed {background-color: #E03535;}")
        remove_button.hide()

        folder_frame.enterEvent = lambda e: self._show_remove_button(folder_frame)
        folder_frame.leaveEvent = lambda e: self._hide_remove_button(folder_frame)

        remove_button.clicked.connect(lambda: self._remove_folder_item(folder_frame))

        layout.addWidget(icon_widget)
        layout.addLayout(text_layout)
        layout.addStretch(1)
        layout.addWidget(include_checkbox)
        layout.addWidget(remove_button)

        folder_frame.setStyleSheet(
            "QFrame {background-color: #F5F7FA; border: 1px solid #E0E3E9; border-radius: 8px; margin: 2px;} QFrame:hover {background-color: #EBEFF5; border-color: #C2C9D6;}")

        self.parent.welcomeFoldersLayout.addWidget(folder_frame)
        
        def enter_event(event):
            remove_button.show()
            QtWidgets.QFrame.enterEvent(folder_frame, event)

        def leave_event(event):
            remove_button.hide()
            QtWidgets.QFrame.leaveEvent(folder_frame, event)

        folder_frame.enterEvent = enter_event
        folder_frame.leaveEvent = leave_event

        item_data = {
            'frame': folder_frame,
            'name_label': name_label,
            'path_label': path_label,
            'remove_button': remove_button,
            'path': folder_path,
            'name': folder_name,
            'include_sub': include_checkbox.isChecked(),
            'checkbox': include_checkbox
        }

        self.folder_items.append(item_data)
        self.parent.gridLayout_6.addWidget(folder_frame, 0, 0)

        for i, item in enumerate(self.folder_items[1:], 1):
            self.parent.gridLayout_6.addWidget(item['frame'], i, 0)

        if len(self.folder_items) == 1:
            self.parent.gridLayout_6.setRowStretch(0, 0)
            self.parent.gridLayout_6.setRowStretch(1, 1)
        elif len(self.folder_items) > 1:
            for i in range(len(self.folder_items)):
                self.parent.gridLayout_6.setRowStretch(i, 0)
            self.parent.gridLayout_6.setRowStretch(len(self.folder_items), 1)

        self.parent._update_empty_state(bool(self.folder_items))
        remove_button.clicked.connect(lambda: self.remove_folder_item(folder_frame))
        
        # 为文件夹项添加右键菜单
        folder_frame.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        folder_frame.customContextMenuRequested.connect(
            lambda pos, item_data=item_data: self._show_folder_item_menu(pos, item_data)
        )
        
        config_manager.add_folder(folder_path)

    def _update_include_sub(self, folder_frame, state):
        try:
            for item in self.folder_items:
                if item['frame'] == folder_frame:
                    current_path = os.path.normpath(item['path'])
                    include_sub = state == QtCore.Qt.CheckState.Checked
                    
                    if include_sub:
                        conflict_found = False
                        conflict_type = 0
                        conflict_path = ""
                        
                        for other in self.folder_items:
                            if other['frame'] == folder_frame:
                                continue
                                
                            other_path = os.path.normpath(other['path'])
                            
                            if self._is_subpath(current_path, other_path) and other['include_sub']:
                                conflict_found = True
                                conflict_type = 1
                                conflict_path = other_path
                                break
                                
                            if self._is_subpath(other_path, current_path):
                                conflict_found = True
                                conflict_type = 2
                                conflict_path = other_path
                                break
                        
                        if conflict_found:
                            if hasattr(self, '_batch_adding') and self._batch_adding:
                                item['checkbox'].setChecked(False)
                                return
                            
                            if conflict_type == 1:
                                msg_box = QMessageBox(self)
                                msg_box.setWindowTitle("操作不允许")
                                msg_box.setText(f"操作被阻止！\n\n"
                                "您要勾选的文件夹是其他已勾选包含子文件夹的路径的子目录。")
                                msg_box.setInformativeText(f"• 父路径: {os.path.basename(conflict_path)}\n"
                                f"• 当前路径: {os.path.basename(current_path)}")
                                
                                cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
                                disable_parent_btn = msg_box.addButton("取消父文件夹的子文件夹选项", QMessageBox.ButtonRole.ActionRole)
                                
                                msg_box.setDefaultButton(cancel_btn)
                                msg_box.exec()
                                
                                if msg_box.clickedButton() == disable_parent_btn:
                                    for other_item in self.folder_items:
                                        if self._paths_equal(other_item['path'], conflict_path):
                                            other_item['checkbox'].setChecked(False)
                                            config_manager.update_folder_include_sub(other_item['path'], False)
                                            item['include_sub'] = True
                                            config_manager.update_folder_include_sub(current_path, True)
                                            break
                            else:
                                QMessageBox.warning(
                                    self, 
                                    "操作不允许",
                                    f"操作被阻止！\n\n"
                                    f"您不能勾选此选项，因为该路径包含其他已添加的路径:\n\n"
                                    f"• 子路径: {os.path.basename(conflict_path)}\n"
                                    f"• 当前路径: {os.path.basename(current_path)}\n\n"
                                    "为了避免文件处理冲突，请先移除子路径。"
                                )
                                
                                item['checkbox'].setChecked(False)
                                return
                            
                    item['include_sub'] = include_sub
                    config_manager.update_folder_include_sub(current_path, include_sub)
                    break
        except Exception as e:
            if not (hasattr(self, '_batch_adding') and self._batch_adding):
                QMessageBox.critical(
                    self, 
                    "操作失败", 
                    f"更新文件夹选项时发生错误：{str(e)}\n\n"
                    f"请稍后重试。"
                )

    def remove_folder_item(self, folder_frame):
        self._remove_folder_item(folder_frame)
        
    def refresh(self):
        """刷新文件夹列表"""
        try:
            # 保存当前状态
            current_paths = [item['path'] for item in self.folder_items]
            current_sub_states = {item['path']: item['checkbox'].isChecked() for item in self.folder_items}
            
            # 清除现有项目
            for item in self.folder_items.copy():
                self.remove_folder_item(item['frame'])
            
            # 重新添加文件夹
            for folder_path in current_paths:
                if os.path.exists(folder_path) and os.path.isdir(folder_path):
                    folder_name = os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path
                    self._create_folder_item(folder_path, folder_name)
                    
                    # 恢复子文件夹状态
                    for item in self.folder_items:
                        if item['path'] == folder_path:
                            item['checkbox'].setChecked(current_sub_states.get(folder_path, True))
                            break
            
            self.parent._update_empty_state(bool(self.folder_items))
        except Exception as e:
            print(f"刷新文件夹列表时出错: {str(e)}")
        finally:
            pass