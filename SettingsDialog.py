from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit, QHBoxLayout, QGroupBox, QGridLayout, QComboBox, QMessageBox
from PyQt6 import QtGui
from common import get_resource_path
from config_manager import config_manager

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('resources/img/icon.ico')))
        self.resize(600, 400)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        self._add_general_settings(main_layout)
        self._add_cache_settings(main_layout)
        self._add_buttons(main_layout)
    
    def _add_general_settings(self, main_layout):
        general_group = QGroupBox("通用设置")
        general_layout = QGridLayout()
        
        general_layout.addWidget(QLabel("最大工作线程数:"), 0, 0)
        self.thread_combo = QComboBox()
        for i in range(1, 9):
            self.thread_combo.addItem(str(i))
        general_layout.addWidget(self.thread_combo, 0, 1)
        
        general_layout.addWidget(QLabel("内存使用限制 (MB):"), 1, 0)
        self.memory_limit = QLineEdit()
        general_layout.addWidget(self.memory_limit, 1, 1)
        
        general_group.setLayout(general_layout)
        main_layout.addWidget(general_group)
    def _add_cache_settings(self, main_layout):
        cache_group = QGroupBox("缓存设置")
        cache_layout = QVBoxLayout()
        
        self.clear_cache_button = QPushButton("清除缓存数据")
        self.clear_cache_button.clicked.connect(self.clear_cache)
        cache_layout.addWidget(self.clear_cache_button)
        
        cache_group.setLayout(cache_layout)
        main_layout.addWidget(cache_group)
    
    def _add_buttons(self, main_layout):
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_settings)
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        
        main_layout.addStretch()
        main_layout.addLayout(button_layout)
    
    def load_settings(self):
        try:
            settings = config_manager.get_settings()
            
            thread_count = settings.get('max_threads', 4)
            if 1 <= thread_count <= 8:
                self.thread_combo.setCurrentText(str(thread_count))
            
            memory_limit = settings.get('memory_limit_mb', 2048)
            self.memory_limit.setText(str(memory_limit))
            
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def save_settings(self):
        try:
            settings = {
                'max_threads': int(self.thread_combo.currentText()),
                'memory_limit_mb': int(self.memory_limit.text()) if self.memory_limit.text() else 2048
            }
            
            config_manager.save_settings(settings)
            QMessageBox.information(self, "保存成功", "设置已成功保存！")
            self.accept()
            
        except ValueError:
            QMessageBox.warning(self, "输入错误", "请确保输入的数值正确！")
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存设置时出错: {e}")
    
    def clear_cache(self):
        reply = QMessageBox.question(
            self, "清除缓存", 
            "确定要清除所有缓存数据吗？这将删除所有临时文件和缓存记录。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                config_manager.clear_cache()
                QMessageBox.information(self, "清除成功", "缓存数据已成功清除！")
            except Exception as e:
                QMessageBox.warning(self, "清除失败", f"清除缓存时出错: {e}")