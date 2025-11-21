import os
import json
import logging
from datetime import datetime
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QTabWidget, QWidget, QCheckBox, QComboBox, QSpinBox,
                            QGroupBox, QGridLayout, QListWidget, QListWidgetItem,
                            QMessageBox, QFrame, QLineEdit, QDoubleSpinBox, QSplitter)
from PyQt6.QtCore import Qt, pyqtSignal
from config_manager import config_manager

# 设置日志记录
logger = logging.getLogger(__name__)

# 常用操作预设配置
PRESET_CONFIGS = {
    "默认配置": {
        "thumbnail_size": 200,
        "max_cache_size": 10000,
        "default_view": "grid",
        "dark_mode": False,
        "auto_update_metadata": True,
        "use_gps_cache": True,
        "map_provider": "gaode",
        "show_thumbnails": True,
        "enable_exif_edit": True,
        "remember_window_size": True
    },
    "性能优先": {
        "thumbnail_size": 150,
        "max_cache_size": 5000,
        "default_view": "list",
        "dark_mode": False,
        "auto_update_metadata": False,
        "use_gps_cache": True,
        "map_provider": "gaode",
        "show_thumbnails": True,
        "enable_exif_edit": False,
        "remember_window_size": True
    },
    "高清体验": {
        "thumbnail_size": 300,
        "max_cache_size": 20000,
        "default_view": "grid",
        "dark_mode": True,
        "auto_update_metadata": True,
        "use_gps_cache": True,
        "map_provider": "gaode",
        "show_thumbnails": True,
        "enable_exif_edit": True,
        "remember_window_size": True
    },
    "省电模式": {
        "thumbnail_size": 100,
        "max_cache_size": 2000,
        "default_view": "list",
        "dark_mode": False,
        "auto_update_metadata": False,
        "use_gps_cache": False,
        "map_provider": "gaode",
        "show_thumbnails": False,
        "enable_exif_edit": False,
        "remember_window_size": False
    }
}

class SettingsDialog(QDialog):
    