import os
import shutil

import pillow_heif
import send2trash
from PIL import Image
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import pyqtSignal, QRunnable, QObject, Qt, QThreadPool, pyqtSlot
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import QMessageBox, QFileDialog

from remove_duplication_thread import HashWorker, ContrastWorker
from common import get_resource_path


class RemoveDuplicationPage(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.hash_dict = {}
        self.duplicate_groups = []
        self.current_group_index = -1
        self.init_ui()
        self.setup_connections()
    
    def init_page(self):
        # 确保能访问文件夹数据
        if hasattr(self.parent, 'folder_page'):
            self.folder_page = self.parent.folder_page
        else:
            self.folder_page = None
        self.setup_connections()
        self.log("INFO", "文件去重功能已就绪")
    
    def init_ui(self):
        # 设置按钮样式
        if hasattr(self.parent, 'btnStartContrast'):
            self.parent.btnStartContrast.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 4px;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
                QPushButton:disabled {
                    background-color: #cccccc;
                    color: #666666;
                }
            """)
        
        # 设置进度条样式
        if hasattr(self.parent, 'contrastProgressBar'):
            self.parent.contrastProgressBar.setValue(0)
            self.parent.contrastProgressBar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #f0f0f0;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 4px;
                }
            """)
        
        # 初始化图像显示区域
        self._init_image_display()
    
    def _init_image_display(self):
        # 初始化图像A和图像B的显示标签
        for img_name in ['imageA', 'imageB']:
            if hasattr(self.parent, img_name):
                img_label = getattr(self.parent, img_name)
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label.setStyleSheet("""
                    QLabel {
                        border: 1px solid #cccccc;
                        background-color: #f9f9f9;
                    }
                """)
    
    def setup_connections(self):
        # 连接对比按钮信号
        if hasattr(self.parent, 'btnStartContrast'):
            self.parent.btnStartContrast.clicked.connect(self.toggle_contrast)
        
        # 连接导航按钮信号（如果存在）
        for btn_name in ['btnPrevGroup', 'btnNextGroup', 'btnDeleteA', 'btnDeleteB', 'btnKeepBoth']:
            if hasattr(self.parent, btn_name):
                if btn_name == 'btnPrevGroup':
                    getattr(self.parent, btn_name).clicked.connect(self._prev_group)
                elif btn_name == 'btnNextGroup':
                    getattr(self.parent, btn_name).clicked.connect(self._next_group)
                elif btn_name == 'btnDeleteA':
                    getattr(self.parent, btn_name).clicked.connect(lambda: self._delete_image('A'))
                elif btn_name == 'btnDeleteB':
                    getattr(self.parent, btn_name).clicked.connect(lambda: self._delete_image('B'))
                elif btn_name == 'btnKeepBoth':
                    getattr(self.parent, btn_name).clicked.connect(self._keep_both)
    
    def toggle_contrast(self):
        if self.is_running:
            self.stop_contrast()
            self.is_running = False
        else:
            success = self.start_contrast()
            if success:
                self.is_running = True
        self._update_button_state()
    
    def start_contrast(self):
        # 检查是否有文件夹被导入
        if not self.folder_page or not self.folder_page.folder_items:
            QMessageBox.warning(self.parent, "警告", "请先导入文件夹")
            return False
        
        # 获取所有要处理的文件路径
        file_paths = []
        for folder_item in self.folder_page.folder_items:
            folder_path = folder_item['path']
            if os.path.exists(folder_path):
                for root, _, files in os.walk(folder_path):
                    for file in files:
                        # 只处理图片文件
                        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.heic')):
                            file_paths.append(os.path.join(root, file))
        
        if not file_paths:
            QMessageBox.information(self.parent, "提示", "未找到可处理的图片文件")
            return False
        
        # 启动对比线程
        self.worker = HashWorker(file_paths)
        self.connect_worker_signals()
        self.worker.start()
        self.log("INFO", f"开始对比 {len(file_paths)} 个文件")
        
        return True
    
    def connect_worker_signals(self):
        if self.worker:
            self.worker.progress_updated.connect(self._update_progress)
            self.worker.log_signal.connect(self.log)
            self.worker.duplicates_found.connect(self._on_duplicates_found)
            self.worker.finished.connect(self._on_contrast_finished)
    
    def stop_contrast(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log("INFO", "对比已停止")
    
    @pyqtSlot(int)
    def _update_progress(self, value):
        if hasattr(self.parent, 'contrastProgressBar'):
            self.parent.contrastProgressBar.setValue(value)
    
    @pyqtSlot(dict)
    def _on_duplicates_found(self, hash_dict):
        self.hash_dict = hash_dict
        # 构建重复文件组
        self.duplicate_groups = []
        for hash_val, paths in hash_dict.items():
            if len(paths) > 1:
                self.duplicate_groups.append(paths)
    
    @pyqtSlot()
    def _on_contrast_finished(self):
        self.is_running = False
        self._update_button_state()
        
        if not self.duplicate_groups:
            self.log("INFO", "未发现重复文件")
            QMessageBox.information(self.parent, "完成", "未发现重复文件")
        else:
            duplicate_count = sum(len(group) for group in self.duplicate_groups)
            self.log("INFO", f"对比完成，发现 {len(self.duplicate_groups)} 组重复文件，共 {duplicate_count} 个重复文件")
            QMessageBox.information(self.parent, "完成", f"发现 {len(self.duplicate_groups)} 组重复文件，共 {duplicate_count} 个重复文件")
            
            # 显示第一组重复文件
            self.current_group_index = 0
            self._display_current_group()
    
    def _display_current_group(self):
        if 0 <= self.current_group_index < len(self.duplicate_groups):
            group = self.duplicate_groups[self.current_group_index]
            # 显示前两个文件进行对比
            if len(group) >= 1 and hasattr(self.parent, 'imageA'):
                self._display_image(group[0], 'imageA')
            if len(group) >= 2 and hasattr(self.parent, 'imageB'):
                self._display_image(group[1], 'imageB')
            
            # 更新组信息显示（如果有对应的标签）
            if hasattr(self.parent, 'labelCurrentGroup'):
                self.parent.labelCurrentGroup.setText(f"组 {self.current_group_index + 1}/{len(self.duplicate_groups)}")
    
    def _display_image(self, file_path, label_name):
        if hasattr(self.parent, label_name):
            label = getattr(self.parent, label_name)
            try:
                # 根据文件扩展名处理不同的图像格式
                if file_path.lower().endswith('.heic'):
                    heif_file = pillow_heif.read(file_path)
                    image = Image.frombytes(
                        heif_file.mode,
                        heif_file.size,
                        heif_file.data,
                        "raw"
                    )
                else:
                    image = Image.open(file_path)
                
                # 调整图像大小以适应标签
                label_width = label.width() - 20  # 留出边距
                label_height = label.height() - 20
                image.thumbnail((label_width, label_height))
                
                # 转换为QPixmap
                qimage = QImage(image.tobytes(), image.width, image.height, image.width * 3, QImage.Format.Format_RGB888)
                pixmap = QPixmap.fromImage(qimage)
                label.setPixmap(pixmap)
            except Exception as e:
                self.log("ERROR", f"无法显示图像 {file_path}: {str(e)}")
                label.setText(f"无法显示图像\n{os.path.basename(file_path)}")
    
    def _prev_group(self):
        if self.current_group_index > 0:
            self.current_group_index -= 1
            self._display_current_group()
    
    def _next_group(self):
        if self.current_group_index < len(self.duplicate_groups) - 1:
            self.current_group_index += 1
            self._display_current_group()
    
    def _delete_image(self, image_type):
        if not self.duplicate_groups or self.current_group_index < 0:
            return
        
        group = self.duplicate_groups[self.current_group_index]
        index = 0 if image_type == 'A' else 1
        
        if index < len(group):
            file_path = group[index]
            
            # 确认删除
            reply = QMessageBox.question(
                self.parent,
                "确认删除",
                f"确定要删除文件 {os.path.basename(file_path)} 吗？\n此操作无法撤销。",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                try:
                    # 使用send2trash发送到回收站
                    send2trash.send2trash(file_path)
                    self.log("INFO", f"已将文件发送到回收站: {file_path}")
                    
                    # 从组中移除该文件
                    group.pop(index)
                    
                    # 如果组中只剩一个文件，移除该组
                    if len(group) <= 1:
                        self.duplicate_groups.pop(self.current_group_index)
                        if self.duplicate_groups:
                            if self.current_group_index >= len(self.duplicate_groups):
                                self.current_group_index = len(self.duplicate_groups) - 1
                            self._display_current_group()
                        else:
                            self.current_group_index = -1
                            # 清空图像显示
                            for img_name in ['imageA', 'imageB']:
                                if hasattr(self.parent, img_name):
                                    getattr(self.parent, img_name).clear()
                    else:
                        # 重新显示当前组
                        self._display_current_group()
                except Exception as e:
                    self.log("ERROR", f"删除文件失败: {str(e)}")
                    QMessageBox.critical(self.parent, "错误", f"删除文件失败: {str(e)}")
    
    def _keep_both(self):
        # 标记当前组为已处理，移到下一组
        self._next_group()
    
    def _update_button_state(self):
        if hasattr(self.parent, 'btnStartContrast'):
            if self.is_running:
                self.parent.btnStartContrast.setText("停止对比")
                self.parent.btnStartContrast.setEnabled(True)
            else:
                self.parent.btnStartContrast.setText("开始对比")
                self.parent.btnStartContrast.setEnabled(True)
    
    def log(self, level, message):
        # 调用父窗口的日志功能
        if hasattr(self.parent, 'log'):
            self.parent.log(level, message)
        else:
            print(f"[{level}] {message}")
    
    def refresh(self):
        # 刷新页面状态
        self.init_ui()
        # 清空之前的结果
        self.duplicate_groups = []
        self.current_group_index = -1
        # 清空图像显示
        for img_name in ['imageA', 'imageB']:
            if hasattr(self.parent, img_name):
                getattr(self.parent, img_name).clear()
        # 重置进度条
        if hasattr(self.parent, 'contrastProgressBar'):
            self.parent.contrastProgressBar.setValue(0)
        self.log("INFO", "页面已刷新")
