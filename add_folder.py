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
    
    def _init_tags_selection_ui(self):
        # 初始化标签选择UI
        # 标签数据初始化
        self.available_tags = ["风景", "人像", "动物", "建筑", "美食", "旅行", "夜景", "自然风光", "城市", "街拍"]
        self.selected_tags = []
        
        # 检查UI元素是否存在
        if not hasattr(self.parent, 'frameRenameTags') or not hasattr(self.parent, 'frameRename'):
            print("警告：frameRenameTags或frameRename不存在于UI中")
            return
        
        # 从UI文件中获取已有的frameRenameTags和frameRename
        frame_rename_tags = self.parent.frameRenameTags
        frame_rename = self.parent.frameRename
        
        # 清除现有布局内容
        self._clear_layout(frame_rename_tags.layout())
        self._clear_layout(frame_rename.layout())
        
        # 创建垂直布局
        self.frameRenameTags_layout = QVBoxLayout(frame_rename_tags)
        self.frameRename_layout = QVBoxLayout(frame_rename)
        
        # 创建标签标题
        available_tags_label = QLabel("可用标签")
        available_tags_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
        selected_tags_label = QLabel("已选标签")
        selected_tags_label.setStyleSheet("font-weight: bold; margin-bottom: 8px;")
        
        # 创建滚动区域用于标签展示
        self.available_tags_scroll = QScrollArea()
        self.selected_tags_scroll = QScrollArea()
        
        self.available_tags_scroll.setWidgetResizable(True)
        self.selected_tags_scroll.setWidgetResizable(True)
        
        self.available_tags_widget = QWidget()
        self.selected_tags_widget = QWidget()
        
        # 创建容器布局
        self.available_tags_container = QVBoxLayout(self.available_tags_widget)
        self.selected_tags_container = QVBoxLayout(self.selected_tags_widget)
        
        # 设置水平流式布局以容纳多个标签
        self.available_tags_flow_layout = QHBoxLayout()
        self.available_tags_flow_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.available_tags_flow_layout.setSpacing(8)
        
        self.selected_tags_flow_layout = QHBoxLayout()
        self.selected_tags_flow_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        self.selected_tags_flow_layout.setSpacing(8)
        
        # 添加到容器布局
        self.available_tags_container.addLayout(self.available_tags_flow_layout)
        self.selected_tags_container.addLayout(self.selected_tags_flow_layout)
        
        # 为容器添加拉伸空间，确保标签不会被拉伸
        self.available_tags_container.addStretch(1)
        self.selected_tags_container.addStretch(1)
        
        # 设置滚动区域的widget
        self.available_tags_scroll.setWidget(self.available_tags_widget)
        self.selected_tags_scroll.setWidget(self.selected_tags_widget)
        
        # 添加到主布局
        self.frameRenameTags_layout.addWidget(available_tags_label)
        self.frameRenameTags_layout.addWidget(self.available_tags_scroll)
        
        self.frameRename_layout.addWidget(selected_tags_label)
        self.frameRename_layout.addWidget(self.selected_tags_scroll)
        
        # 初始加载标签
        self._load_tags()
    
    def _load_tags(self):
        # 清除现有标签
        self._clear_layout(self.available_tags_flow_layout)
        self._clear_layout(self.selected_tags_flow_layout)
        
        # 加载可用标签到待选区域
        for tag in self.available_tags:
            tag_button = self._create_tag_button(tag, False)
            self.available_tags_flow_layout.addWidget(tag_button)
        
        # 加载已选标签到已选区域
        for tag in self.selected_tags:
            tag_button = self._create_tag_button(tag, True)
            self.selected_tags_flow_layout.addWidget(tag_button)
    
    def _create_tag_button(self, tag_text, is_selected):
        # 创建标签按钮
        button = QPushButton(tag_text)
        button.setObjectName(f"tag_{tag_text}")
        button.setMinimumSize(80, 32)
        button.setMaximumWidth(120)
        button.setCheckable(True)
        button.setChecked(is_selected)
        button.setCursor(QtCore.Qt.CursorShape.PointingHandCursor)
        
        # 添加属性动画支持
        button.setProperty('is_animated', False)
        
        # 设置样式 - 增强的样式与过渡效果
        if is_selected:
            button.setStyleSheet("""QPushButton {
                background-color: #8b5cf6;
                color: white;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 14px;
                border: 2px solid #8b5cf6;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 8px rgba(139, 92, 246, 0.2);
            }
            QPushButton:hover {
                background-color: #7c3aed;
                border-color: #7c3aed;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
            }
            QPushButton:pressed {
                background-color: #6d28d9;
                border-color: #6d28d9;
                transform: translateY(0);
                box-shadow: 0 1px 4px rgba(139, 92, 246, 0.4);
            }""")
        else:
            button.setStyleSheet("""QPushButton {
                background-color: #f3f4f6;
                color: #4b5563;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 14px;
                border: 2px solid transparent;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
            }
            QPushButton:hover {
                background-color: #e5e7eb;
                border-color: #d1d5db;
                transform: translateY(-1px);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background-color: #d1d5db;
                border-color: #9ca3af;
                transform: translateY(0);
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
            }""")
        
        # 连接点击事件
        button.clicked.connect(lambda checked, btn=button, text=tag_text: self._on_tag_clicked(text, checked, btn))
        
        return button
    
    def _on_tag_clicked(self, tag_text, checked, button):
        # 标签点击事件处理 - 简化实现，直接移动标签
        try:
            # 直接执行标签移动逻辑
            self._move_tag(tag_text, checked, button)
        except Exception as e:
            print(f"处理标签点击事件时出错: {str(e)}")
            # 重新加载标签以恢复一致状态
            self._load_tags()
    

    
    def _move_tag(self, tag_text, checked, button):
        """执行标签移动的实际逻辑"""
        try:
            if checked:
                # 从待选区域移动到已选区域
                if tag_text in self.available_tags:
                    # 从待选列表移除
                    self.available_tags = [tag for tag in self.available_tags if tag != tag_text]
                    # 添加到已选列表
                    if tag_text not in self.selected_tags:
                        self.selected_tags.append(tag_text)
                        # 立即重新加载标签以更新UI
                        self._load_tags()
            else:
                # 从已选区域移动到待选区域
                if tag_text in self.selected_tags:
                    # 从已选列表移除
                    self.selected_tags = [tag for tag in self.selected_tags if tag != tag_text]
                    # 添加到待选列表
                    if tag_text not in self.available_tags:
                        self.available_tags.append(tag_text)
                        # 立即重新加载标签以更新UI
                        self._load_tags()
        except Exception as e:
            print(f"移动标签时出错: {str(e)}")
            # 重新加载标签以恢复一致状态
            self._load_tags()
    

    
    def _save_tags_state(self):
        """保存标签状态，确保数据一致性"""
        try:
            # 验证标签数据的完整性和一致性
            self._validate_tags_data()
            
            # 这里可以实现将标签状态保存到配置或其他存储方式
            # 例如：config_manager.save_tags_state(self.available_tags, self.selected_tags)
            
            # 更新tags_data变量以保持一致性
            self.tags_data = {
                'available_tags': self.available_tags.copy(),
                'selected_tags': self.selected_tags.copy()
            }
            
        except Exception as e:
            print(f"保存标签状态时出错: {str(e)}")
    
    def _validate_tags_data(self):
        """验证标签数据的一致性"""
        # 检查是否有重复标签
        if len(self.available_tags) != len(set(self.available_tags)):
            # 移除重复标签
            self.available_tags = list(set(self.available_tags))
        
        if len(self.selected_tags) != len(set(self.selected_tags)):
            # 移除重复标签
            self.selected_tags = list(set(self.selected_tags))
        
        # 确保没有标签同时存在于两个列表中
        common_tags = set(self.available_tags).intersection(set(self.selected_tags))
        if common_tags:
            # 如果有共同标签，优先保留在selected_tags中
            for tag in common_tags:
                if tag in self.available_tags:
                    self.available_tags.remove(tag)
    
    def get_selected_tags(self):
        """获取已选标签的公共方法"""
        # 返回副本以避免外部修改
        return self.selected_tags.copy()
    
    def _clear_layout(self, layout):
        # 清除布局中的所有控件
        if layout is None:
            return
        
        while layout.count() > 0:
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                nested_layout = item.layout()
                if nested_layout is not None:
                    self._clear_layout(nested_layout)

    def _paths_equal(self, path1, path2):
        try:
            norm_path1 = os.path.normcase(os.path.normpath(path1))
            norm_path2 = os.path.normcase(os.path.normpath(path2))
            
            if os.name == 'nt':
                drive1 = os.path.splitdrive(norm_path1)[0].lower()
                drive2 = os.path.splitdrive(norm_path2)[0].lower()
                path_part1 = norm_path1[len(drive1):]
                path_part2 = norm_path2[len(drive2):]
                return drive1 == drive2 and path_part1 == path_part2
            
            return norm_path1 == norm_path2
        except (TypeError, AttributeError):
            return False
            
    def _check_path_conflicts(self, folder_path):
        """检查路径冲突，返回冲突信息或None"""
        for item in self.folder_items:
            item_path = os.path.normpath(item['path'])
            
            if item['include_sub'] and self._is_subpath(folder_path, item_path):
                return {
                    'type': 1,  # 当前路径是已有路径的子目录
                    'parent_path': item_path,
                    'parent_name': os.path.basename(item_path)
                }
            
            if self._is_subpath(item_path, folder_path) and item['include_sub']:
                return {
                    'type': 2,  # 已有路径是当前路径的子目录
                    'child_path': item_path,
                    'child_name': os.path.basename(item_path)
                }
        return None
        
    def _handle_path_conflict(self, conflict_info, folder_path, folder_name):
        """处理路径冲突，返回是否继续添加"""
        if conflict_info['type'] == 1:
            # 添加智能默认选项，减少用户点击
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("路径冲突")
            msg_box.setText(f"该文件夹是 '{conflict_info['parent_name']}' 的子目录，且 '{conflict_info['parent_name']}'"  
                            f" 包含子文件夹")
            msg_box.setInformativeText("您可以选择以下操作：")
            
            # 添加记住选择的选项
            remember_checkbox = QtWidgets.QCheckBox("记住此选择")
            msg_box.setCheckBox(remember_checkbox)
            
            continue_btn = msg_box.addButton("继续添加", QMessageBox.ButtonRole.ActionRole)
            disable_sub_btn = msg_box.addButton("取消父文件夹的子文件夹选项", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            
            # 设置默认按钮为最常用操作
            msg_box.setDefaultButton(disable_sub_btn)
            msg_box.exec()
            
            # 根据用户选择执行相应操作
            if msg_box.clickedButton() == continue_btn:
                # 记住选择
                if remember_checkbox.isChecked():
                    config_manager.set_last_conflict_resolution("continue")
                return True
            elif msg_box.clickedButton() == disable_sub_btn:
                # 记住选择
                if remember_checkbox.isChecked():
                    config_manager.set_last_conflict_resolution("disable_sub")
                
                # 自动处理父文件夹设置
                for item in self.folder_items:
                    if self._paths_equal(item['path'], conflict_info['parent_path']):
                        item['checkbox'].setChecked(False)
                        config_manager.update_folder_include_sub(item['path'], False)
                        break
                return True
            else:
                return False
        else:
            # 提供一键解决方案
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("路径冲突")
            msg_box.setText(f"'{conflict_info['child_name']}' 是该文件夹的子目录，且 '{conflict_info['child_name']}' 已选择包含子文件夹")
            
            fix_btn = msg_box.addButton("自动修复", QMessageBox.ButtonRole.ActionRole)
            cancel_btn = msg_box.addButton("取消", QMessageBox.ButtonRole.RejectRole)
            
            msg_box.setDefaultButton(fix_btn)
            msg_box.exec()
            
            if msg_box.clickedButton() == fix_btn:
                # 自动修复子文件夹设置
                for item in self.folder_items:
                    if self._paths_equal(item['path'], conflict_info['child_path']):
                        item['checkbox'].setChecked(False)
                        config_manager.update_folder_include_sub(item['path'], False)
                        break
                return True
            return False

    def _is_subpath(self, path, parent_path):
        try:
            path = os.path.normcase(os.path.normpath(path))
            parent_path = os.path.normcase(os.path.normpath(parent_path))
            
            parent_path_with_sep = parent_path
            if not parent_path.endswith(os.sep):
                parent_path_with_sep = parent_path + os.sep
            
            return path == parent_path or path.startswith(parent_path_with_sep)
        except (TypeError, AttributeError, ValueError):
            return False

    def _show_remove_button(self, folder_frame):
        for item in self.parent.gridLayout_6.children():
            if item == folder_frame:
                for child in folder_frame.children():
                    if isinstance(child, QtWidgets.QPushButton) and child.text() == "移除":
                        child.show()
                break

    def _hide_remove_button(self, folder_frame):
        for item in self.parent.gridLayout_6.children():
            if item == folder_frame:
                for child in folder_frame.children():
                    if isinstance(child, QtWidgets.QPushButton) and child.text() == "移除":
                        child.hide()
                break

    def _remove_folder_item(self, folder_frame):
        try:
            for i, item in enumerate(self.folder_items):
                if item['frame'] == folder_frame:
                    try:
                        item['remove_button'].clicked.disconnect()
                        item['checkbox'].stateChanged.disconnect()
                    except TypeError:
                        pass
                    
                    self.parent.welcomeFoldersLayout.removeWidget(folder_frame)
                    folder_frame.deleteLater()
                    
                    folder_path = item['path']
                    
                    self.folder_items.pop(i)
                    
                    try:
                        config_manager.remove_folder(folder_path)
                    except Exception as e:
                        pass
                    break
            
            for i in reversed(range(self.parent.gridLayout_6.count())):
                layout_item = self.parent.gridLayout_6.itemAt(i)
                if layout_item and layout_item.widget():
                    self.parent.gridLayout_6.removeItem(layout_item)
            
            for row, item in enumerate(self.folder_items):
                self.parent.gridLayout_6.addWidget(item['frame'], row, 0)
            
            if len(self.folder_items) == 1:
                self.parent.gridLayout_6.setRowStretch(0, 0)
                self.parent.gridLayout_6.setRowStretch(1, 1)
            elif len(self.folder_items) > 1:
                for i in range(len(self.folder_items)):
                    self.parent.gridLayout_6.setRowStretch(i, 0)
                self.parent.gridLayout_6.setRowStretch(len(self.folder_items), 1)
            
            self.parent._update_empty_state(bool(self.folder_items))
        except Exception as e:
            QMessageBox.warning(
                self, 
                "操作失败", 
                f"移除文件夹时发生错误：{str(e)}"
            )

    def _check_media_files(self, folder_path):
        """检查并收集文件夹中的媒体文件信息"""
        try:
            # 收集文件夹统计信息
            stats = self._collect_folder_stats(folder_path)
            
            # 显示文件夹信息
            self._show_folder_info(folder_path, stats)
            
            # 更新父窗口状态
            if stats['has_media']:
                self.parent._update_empty_state(True)
                
            return stats
        except Exception as e:
            # 发生错误时静默处理，不影响主流程
            return {'has_media': False, 'file_count': 0, 'media_count': 0, 'subfolder_count': 0}
    
    def _collect_folder_stats(self, folder_path):
        """收集文件夹的统计信息"""
        file_count = 0
        media_count = 0
        subfolder_count = 0
        has_media = False
        media_types = Counter()
        
        try:
            # 定义常见媒体文件扩展名
            image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.tiff', '.heic', '.heif', '.bmp', '.ico']
            video_exts = ['.mp4', '.mov', '.avi', '.mkv', '.flv', '.3gp', '.wmv', '.m4v', '.webm']
            audio_exts = ['.mp3', '.flac', '.wav', '.aac', '.ogg', '.wma', '.m4a']
            
            # 遍历文件夹中的所有项
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isfile(item_path):
                    file_count += 1
                    
                    # 检查文件扩展名
                    ext = os.path.splitext(item)[1].lower()
                    
                    if ext in image_exts:
                        has_media = True
                        media_count += 1
                        media_types['图片'] += 1
                    elif ext in video_exts:
                        has_media = True
                        media_count += 1
                        media_types['视频'] += 1
                    elif ext in audio_exts:
                        has_media = True
                        media_count += 1
                        media_types['音频'] += 1
                    else:
                        # 使用detect_media_type进一步检测
                        try:
                            media_info = detect_media_type(item_path)
                            if media_info['valid']:
                                has_media = True
                                media_count += 1
                                media_types['其他媒体'] += 1
                        except Exception:
                            pass
                
                elif os.path.isdir(item_path):
                    subfolder_count += 1
                    
        except Exception:
            # 忽略访问错误
            pass
        
        return {
            'file_count': file_count,
            'media_count': media_count,
            'subfolder_count': subfolder_count,
            'has_media': has_media,
            'media_types': media_types
        }
    
    def _show_folder_info(self, folder_path, stats):
        """显示文件夹信息到UI中的textBrowser_import_info控件"""
        folder_name = os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path
        
        # 构建信息字符串
        info_text = f"文件夹: {folder_name}\n"
        info_text += f"路径: {folder_path}\n\n"
        info_text += f"文件总数: {stats['file_count']}\n"
        info_text += f"媒体文件: {stats['media_count']}\n"
        info_text += f"子文件夹: {stats['subfolder_count']}\n\n"
        
        # 添加媒体类型分布
        if stats['media_types']:
            info_text += "媒体类型分布:\n"
            for media_type, count in stats['media_types'].items():
                info_text += f"  - {media_type}: {count}个\n"
        
        # 尝试使用UI中的textBrowser_import_info控件显示信息
        if hasattr(self.parent, 'textBrowser_import_info'):
            self.parent.textBrowser_import_info.setPlainText(info_text)
        else:
            # 如果控件不存在，使用临时对话框显示信息（兼容性处理）
            msg_box = QtWidgets.QMessageBox(self)
            msg_box.setWindowTitle("文件夹信息")
            msg_box.setText("文件夹扫描完成")
            msg_box.setDetailedText(info_text)
            msg_box.setInformativeText(f"发现 {stats['media_count']} 个媒体文件")
            msg_box.exec()

    def get_all_folders(self):
        return self.folder_items
        
    def _handle_single_file_import(self, file_paths):
        """
        处理单个媒体文件的导入
        """
        if not file_paths:
            return
            
        # 为单个文件创建临时文件夹引用
        import tempfile
        from pathlib import Path
        
        # 获取文件所在的目录
        file_dir = os.path.dirname(file_paths[0])
        folder_name = f"文件集合 - {os.path.basename(file_dir)}"
        
        # 创建文件夹项
        folder_item = self._create_folder_item(file_dir, folder_name)
        if folder_item:
            # 标记为文件模式
            folder_item['is_file_mode'] = True
            folder_item['file_paths'] = file_paths
            
            # 显示导入成功消息
            QMessageBox.information(
                self, 
                "文件导入成功", 
                f"成功导入 {len(file_paths)} 个媒体文件\n\n" + 
                "注意：这些文件将作为其所在目录的引用进行管理。"
            )
        else:
            QMessageBox.warning(
                self, 
                "导入失败", 
                "无法创建文件引用。请检查权限或重试。"
            )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # 提供视觉反馈
            if hasattr(self.parent, 'widgetAddFolder'):
                self.parent.widgetAddFolder.setStyleSheet("background-color: #f0f8ff; border: 2px dashed #4a90e2;")

    def dragLeaveEvent(self, event):
        # 恢复原始样式
        if hasattr(self.parent, 'widgetAddFolder'):
            self.parent.widgetAddFolder.setStyleSheet("")
            
    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        # 恢复原始样式
        if hasattr(self.parent, 'widgetAddFolder'):
            self.parent.widgetAddFolder.setStyleSheet("")
            
        urls = event.mimeData().urls()
        
        folder_paths = []
        file_paths = []
        
        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile()
                if os.path.isdir(path):
                    folder_paths.append(path)
                elif os.path.isfile(path):
                    # 支持单个媒体文件拖拽
                    if detect_media_type(path):
                        file_paths.append(path)
        
        if not folder_paths and not file_paths:
            QMessageBox.information(
                self, 
                "操作提示", 
                "未找到有效的文件夹路径或媒体文件。请确保您拖拽的是本地文件夹或支持的媒体文件。"
            )
            return
            
        # 如果只有文件，特殊处理单个文件导入
        if file_paths and not folder_paths:
            self._handle_single_file_import(file_paths)
        
        total = len(folder_paths)
        added_count = 0
        skipped_count = 0
        error_count = 0
        self._batch_adding = True
        
        # 优化进度对话框显示
        progress_dialog = QProgressDialog(self)
        progress_dialog.setWindowTitle("正在添加文件夹")
        progress_dialog.setLabelText(f"准备处理 {total} 个文件夹...")
        progress_dialog.setRange(0, total)
        progress_dialog.setCancelButtonText("取消")
        progress_dialog.setValue(0)
        progress_dialog.setWindowModality(QtCore.Qt.WindowModality.WindowModal)
        progress_dialog.setMinimumDuration(500)  # 短暂延迟显示，避免闪屏
        progress_dialog.show()
        
        results = {
            'added': [],
            'skipped': [],
            'error': []
        }
        
        for i, folder_path in enumerate(folder_paths):
            if progress_dialog.wasCanceled():
                QMessageBox.information(self, "操作已取消", "文件夹添加操作已被取消。")
                break
            
            folder_name = os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path
            progress_dialog.setLabelText(f"正在处理第 {i+1}/{total} 个文件夹...\n\n当前: {folder_name}")
            progress_dialog.setValue(i)
            
            QtCore.QCoreApplication.processEvents()
            
            try:
                if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
                    skipped_count += 1
                    results['skipped'].append((folder_path, "路径不存在或不是文件夹"))
                    continue
                
                try:
                    os.listdir(folder_path)
                except PermissionError:
                    skipped_count += 1
                    results['skipped'].append((folder_path, "无访问权限"))
                    continue
                
                folder_path = os.path.normpath(folder_path)
                
                has_conflict = False
                conflict_reason = ""
                
                # 优化冲突检测逻辑，提高性能
                has_conflict = False
                conflict_reason = ""
                
                # 先检查是否有完全相同的路径
                if any(self._paths_equal(os.path.normpath(item['path']), folder_path) for item in self.folder_items):
                    has_conflict = True
                    conflict_reason = "已存在相同路径"
                else:
                    # 检查子目录关系
                    for item in self.folder_items:
                        item_path = os.path.normpath(item['path'])
                        
                        if item['include_sub'] and self._is_subpath(folder_path, item_path):
                            has_conflict = True
                            conflict_reason = f"是已添加文件夹 '{os.path.basename(item_path)}' 的子目录且父目录已勾选包含子文件夹"
                            break
                            
                        if self._is_subpath(item_path, folder_path) and item['include_sub']:
                            has_conflict = True
                            conflict_reason = f"包含已添加文件夹 '{os.path.basename(item_path)}' 且子目录已勾选包含子文件夹"
                            break
                
                if has_conflict:
                    skipped_count += 1
                    results['skipped'].append((folder_path, conflict_reason))
                    continue
                
                folder_name = os.path.basename(folder_path) if os.path.basename(folder_path) else folder_path
                folder_item = self._create_folder_item(folder_path, folder_name)
                if folder_item:
                    added_count += 1
                    results['added'].append(folder_path)
                    
                    # 异步检查媒体文件，避免阻塞UI
                    QtCore.QTimer.singleShot(0, lambda path=folder_path: self._check_media_files(path))
                
            except Exception as e:
                error_count += 1
                results['error'].append((folder_path, str(e)))
        
        self._batch_adding = False
        
        progress_dialog.close()
        
        # 优化结果提示，根据添加数量决定提示方式
        if added_count > 0 or skipped_count > 0 or error_count > 0:
            message = ""
            details = []
            
            if added_count > 0:
                message += f"成功添加 {added_count} 个文件夹\n"
                for path in results['added']:
                    details.append(f"  已添加: {os.path.basename(path)} ({path})")
                details.append("")
            
            if skipped_count > 0:
                message += f"跳过 {skipped_count} 个文件夹\n"
                for path, reason in results['skipped']:
                    details.append(f"  {os.path.basename(path)} - {reason}")
                details.append("")
            
            if error_count > 0:
                message += f"{error_count} 个文件夹添加失败\n"
                for path, reason in results['error']:
                    details.append(f"  已跳过: {os.path.basename(path)} - {reason}")
            
            # 对于少量文件夹，直接显示详细信息
            if total <= 5:
                QMessageBox.information(
                    self, 
                    "添加完成", 
                    message + "\n" + "\n".join(details) if details else message
                )
            else:
                # 对于大量文件夹，提供详细信息按钮
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("添加完成")
                msg_box.setText(message)
                
                if details:
                    details_btn = msg_box.addButton("查看详情", QMessageBox.ButtonRole.ActionRole)
                    msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
                    msg_box.setDefaultButton(QMessageBox.StandardButton.Ok)
                    
                    msg_box.exec()
                    
                    if msg_box.clickedButton() == details_btn:
                        details_dialog = QDialog(self)
                        details_dialog.setWindowTitle("添加详情")
                        details_dialog.resize(600, 400)
                        
                        text_browser = QTextEdit()
                        text_browser.setReadOnly(True)
                        text_browser.setPlainText("\n".join(details))
                        
                        close_btn = QPushButton("关闭")
                        close_btn.clicked.connect(details_dialog.close)
                        
                        layout = QVBoxLayout()
                        layout.addWidget(text_browser)
                        layout.addWidget(close_btn, alignment=QtCore.Qt.AlignmentFlag.AlignRight)
                        
                        details_dialog.setLayout(layout)
                        details_dialog.exec()
                else:
                    msg_box.exec()

    def _show_context_menu(self, position):
        """显示右键菜单"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
            QMenu::separator {
                height: 1px;
                background-color: #e0e0e0;
                margin: 4px 0;
            }
        """)
        
        # 添加添加文件夹操作
        add_action = menu.addAction("添加文件夹")
        add_action.triggered.connect(self._open_folder_dialog)
        
        # 添加批量添加文件夹操作
        batch_add_action = menu.addAction("批量添加文件夹")
        batch_add_action.triggered.connect(self._open_multiple_folder_dialog)
        
        if self.folder_items:
            menu.addSeparator()
            
            # 添加菜单项
            select_all_action = menu.addAction("全选")
            select_none_action = menu.addAction("全不选")
            menu.addSeparator()
            
            enable_all_sub_action = menu.addAction("全部包含子文件夹")
            disable_all_sub_action = menu.addAction("全部不包含子文件夹")
            menu.addSeparator()
            
            remove_all_action = menu.addAction("移除所有文件夹")
            refresh_action = menu.addAction("刷新列表")
        else:
            select_all_action = None
            select_none_action = None
            enable_all_sub_action = None
            disable_all_sub_action = None
            remove_all_action = None
            refresh_action = None
        
        # 显示菜单
        action = menu.exec(self.parent.scrollWelcomeContent.mapToGlobal(position))
        
        if action == select_all_action and select_all_action:
            self._select_all_folders(True)
        elif action == select_none_action and select_none_action:
            self._select_all_folders(False)
        elif action == enable_all_sub_action and enable_all_sub_action:
            self._set_all_subfolders(True)
        elif action == disable_all_sub_action and disable_all_sub_action:
            self._set_all_subfolders(False)
        elif action == remove_all_action and remove_all_action:
            self._remove_all_folders()
        elif action == refresh_action and refresh_action:
            self._refresh_folder_list()
            
    def _show_add_folder_dialog(self):
        """显示添加文件夹对话框 - 供MainWindow调用"""
        self._open_folder_dialog()
        
    def _add_folders(self, folders):
        """添加多个文件夹 - 供MainWindow拖放处理调用，并在textBrowser_import_info中显示信息"""
        self._batch_adding = True
        added_count = 0
        
        # 只处理第一个文件夹的信息显示，避免多次覆盖显示
        first_folder_processed = False
        
        for folder_path in folders:
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                self._check_and_add_folder(folder_path)
                added_count += 1
                
                # 处理第一个文件夹时，显示其信息到textBrowser_import_info
                if not first_folder_processed:
                    try:
                        # 收集文件夹统计信息
                        stats = self._collect_folder_stats(folder_path)
                        # 显示文件夹信息到UI
                        self._show_folder_info(folder_path, stats)
                        first_folder_processed = True
                    except Exception as e:
                        print(f"[ERROR] 显示文件夹信息时出错: {str(e)}")
        
        self._batch_adding = False
        
        if added_count > 0:
            self.parent._update_empty_state(True)
            # 如果添加了多个文件夹，可以在textBrowser_import_info底部添加提示
            if added_count > 1 and first_folder_processed and hasattr(self.parent, 'textBrowser_import_info'):
                current_text = self.parent.textBrowser_import_info.toPlainText()
                self.parent.textBrowser_import_info.setPlainText(f"{current_text}\n\n注: 已成功添加共 {added_count} 个文件夹，仅显示第一个文件夹的详细信息。")
            
    def _open_multiple_folder_dialog(self):
        """打开批量选择文件夹对话框"""
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        dialog.setOption(QFileDialog.Option.ShowDirsOnly, True)
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog, True)
        dialog.setWindowTitle("选择多个文件夹")
        
        # 创建选择多个文件夹的按钮
        for view in dialog.findChildren(QtWidgets.QAbstractItemView):
            if isinstance(view, QtWidgets.QTreeView) or isinstance(view, QtWidgets.QListView):
                view.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        
        if dialog.exec():
            selected_folders = dialog.selectedFiles()
            self._add_folders(selected_folders)

    def _select_all_folders(self, select):
        """全选或全不选所有文件夹"""
        for item in self.folder_items:
            item['checkbox'].setChecked(select)

    def _set_all_subfolders(self, include_sub):
        """设置所有文件夹的子文件夹包含状态"""
        for item in self.folder_items:
            item['checkbox'].setChecked(include_sub)
            config_manager.update_folder_include_sub(item['path'], include_sub)

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

    def _refresh_folder_list(self):
        """刷新文件夹列表"""
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
        
        QtWidgets.QMessageBox.information(self, "刷新完成", "文件夹列表已刷新")

    def _show_folder_item_menu(self, position, item_data):
        """显示单个文件夹项的右键菜单"""
        menu = QtWidgets.QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 20px;
                border-radius: 2px;
            }
            QMenu::item:selected {
                background-color: #f0f0f0;
            }
        """)
        
        # 添加菜单项
        open_action = menu.addAction("打开文件夹")
        copy_path_action = menu.addAction("复制路径")
        menu.addSeparator()
        
        toggle_sub_action = menu.addAction("切换子文件夹状态")
        rename_action = menu.addAction("重命名显示")
        menu.addSeparator()
        
        remove_action = menu.addAction("移除文件夹")
        
        # 显示菜单
        action = menu.exec(item_data['frame'].mapToGlobal(position))
        
        if action == open_action:
            self._open_folder_in_explorer(item_data['path'])
        elif action == copy_path_action:
            self._copy_folder_path(item_data['path'])
        elif action == toggle_sub_action:
            self._toggle_folder_sub_status(item_data)
        elif action == rename_action:
            self._rename_folder_display(item_data)
        elif action == remove_action:
            self.remove_folder_item(item_data['frame'])

    def _open_folder_in_explorer(self, folder_path):
        """在资源管理器中打开文件夹"""
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                subprocess.Popen(['explorer', folder_path])
            elif platform.system() == 'Darwin':  # macOS
                subprocess.Popen(['open', folder_path])
            else:  # Linux
                subprocess.Popen(['xdg-open', folder_path])
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "打开失败", f"无法打开文件夹: {str(e)}")

    def _copy_folder_path(self, folder_path):
        """复制文件夹路径到剪贴板"""
        try:
            clipboard = QtWidgets.QApplication.clipboard()
            clipboard.setText(folder_path)
            QtWidgets.QMessageBox.information(self, "复制成功", "文件夹路径已复制到剪贴板")
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, "复制失败", f"无法复制路径: {str(e)}")

    def _toggle_folder_sub_status(self, item_data):
        """切换文件夹的子文件夹包含状态"""
        current_state = item_data['checkbox'].isChecked()
        item_data['checkbox'].setChecked(not current_state)
        config_manager.update_folder_include_sub(item_data['path'], not current_state)

    def _rename_folder_display(self, item_data):
        """重命名文件夹显示名称"""
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, 
            "重命名显示", 
            "输入新的显示名称:",
            text=item_data['name']
        )
        
        if ok and new_name.strip():
            item_data['name_label'].setText(new_name.strip())

    def _load_saved_folders(self):
        saved_folders = config_manager.get_folders()
        loaded_paths = []
        invalid_paths = []
        
        for folder_info in saved_folders:
            folder_path = folder_info["path"]
            folder_path = os.path.normpath(folder_path)
            
            if os.path.exists(folder_path) and os.path.isdir(folder_path):
                has_conflict = False
                for loaded_path in loaded_paths:
                    if self._paths_equal(folder_path, loaded_path):
                        has_conflict = True
                        break
                    
                if not has_conflict:
                    self._create_folder_item(folder_path, os.path.basename(folder_path))
                    loaded_paths.append(folder_path)
            else:
                invalid_paths.append(folder_path)
        
        for invalid_path in invalid_paths:
            config_manager.remove_folder(invalid_path)
            
        if invalid_paths:
            QMessageBox.information(
                self, 
                "文件夹更新", 
                f"检测到 {len(invalid_paths)} 个文件夹路径无效（可能已被移动或删除），\n\n"
                "这些路径已从配置中自动移除。"
            )
        self.parent._update_empty_state(bool(self.folder_items))
