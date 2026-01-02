import logging

import requests
from PyQt6 import QtCore, QtGui
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog

from UI_UpdateDialog import Ui_UpdateDialog
from common import get_resource_path

logger = logging.getLogger(__name__)

class UpdateDialog(QDialog):
    def __init__(self, url, title, content, version="", necessary=False):
        super().__init__()
        self.ui = Ui_UpdateDialog()
        self.ui.setupUi(self)
        self.url = url
        self.setWindowTitle("轻羽媒体整理通知 - 更新提示")
        self.setWindowIcon(QtGui.QIcon(get_resource_path('_internal/resources/img/icon.ico')))
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.ui.lblTitle.setText(title)
        self.ui.lblContent.setText(content)
        
        
        self.ui.btnDownload.clicked.connect(self.download_update)
        self.ui.btnCancel.clicked.connect(self.close)
    
    def download_update(self):
        QDesktopServices.openUrl(QUrl(self.url))
        self.close()
    
    def closeEvent(self, event):
        
        super().closeEvent(event)

def check_update():
    url = 'https://gitee.com/Yangshengzhou/yang-shengzhou/raw/master/LeafSort/versionInfo'
    current_version = 2.02
    logger.info(f"当前应用版本: {current_version}")
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        content = response.text.strip()
        info_dict = {}
        for line in content.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info_dict[key.strip()] = value.strip()
        
        if not all(key in info_dict for key in ['Latest Version', 'Download Link', 'Description']):
            raise ValueError("Invalid update information format")
        
        latest_version_str = info_dict['Latest Version']
        download_link = info_dict['Download Link']
        description = info_dict['Description']
        
        try:
            latest_version = float(latest_version_str)
        except ValueError:
            raise ValueError("Invalid version number format")
        
        if latest_version > current_version:
            version_text = f"LeafSort v{latest_version_str}"
            dialog = UpdateDialog(download_link, f"发现新版本 {version_text}", description, version_text, False)
            dialog.exec()

    except requests.exceptions.RequestException as e:
        logger.info(f"网络错误，无法检查更新: {str(e)}")
    except Exception as e:
        logger.error(f"检查更新时出错: {str(e)}")
