import json
import logging
import os
from datetime import datetime

import requests
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, QDateTime
from PyQt6.QtWidgets import QMessageBox

from common import get_resource_path
from config_manager import config_manager
from write_exif_thread import WriteExifThread

logger = logging.getLogger('WriteExifManager')
logger.setLevel(logging.DEBUG)

class WriteExifManager(QObject):
    log_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None, folder_page=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = folder_page
        self.selected_star = 0
        self.worker = None
        self.star_buttons = []
        self.is_running = False
        self.camera_lens_mapping = {}
        self.error_messages = []
        self.camera_data = {}
        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        for i in range(1, 6):
            btn = getattr(self.parent, f'btnStar{i}')
            btn.setStyleSheet(
                "QPushButton { "
                f"image: url({get_resource_path('resources/img/page_4/星级_暗.svg')});\n"
                "border: none; padding: 0; }" "\n"
                "QPushButton:hover { background-color: transparent; }"
            )
            btn.enterEvent = lambda e, idx=i: self.highlight_stars(idx)
            btn.leaveEvent = lambda e: self.highlight_stars(self.selected_star)
            btn.clicked.connect(lambda _, idx=i: self.set_selected_star(idx))
            self.star_buttons.append(btn)
        
        self.init_camera_brand_model()
        
        self.load_camera_lens_mapping()
        
        # 设置信号连接
        self.setup_connections()
        
        self.update_button_state()
        self.load_exif_settings()
        self.save_exif_settings()
        self.log("INFO", "欢迎使用图像属性写入，不写入项留空即可。文件一旦写入无法还原。")
        
    def load_camera_lens_mapping(self):
        data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                'resources', 'json', 'camera_lens_mapping.json')
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.camera_lens_mapping = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.log("WARNING", f"加载相机镜头映射数据失败: {str(e)}")
                self.camera_lens_mapping = {}
        else:
            self.log("WARNING", "相机镜头映射文件不存在，将使用默认镜头信息")
            self.camera_lens_mapping = {}

    def get_lens_info_for_camera(self, brand, model):
        if brand in self.camera_lens_mapping:
            brand_data = self.camera_lens_mapping[brand]
            if model in brand_data:
                return brand_data[model]
        return None

    def get_default_model_for_brand(self, brand):
        if brand in self.camera_data:
            models = self.camera_data[brand]
            if models:
                return models[0]
        return None

    def init_camera_brand_model(self):
        camera_data = self._load_camera_data()

        if not camera_data:
            camera_data = {
                "Apple": ["iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15", "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro Max", "iPhone 13 Pro"],
                "OnePlus": ["12 Pro", "12", "11 Pro", "11", "10 Pro", "10", "9 Pro", "9"],
                "Xiaomi": ["14 Ultra", "14 Pro", "14", "13 Ultra", "13 Pro", "13", "12S Ultra", "12S Pro"],
                "Huawei": ["P60 Pro", "P60", "Mate 60 Pro", "Mate 60", "P50 Pro", "P50", "Mate 50 Pro", "Mate 50"],
                "OPPO": ["Find X6 Pro", "Find X6", "Find X5 Pro", "Find X5", "Reno10 Pro+", "Reno10 Pro", "Reno10", "Reno9 Pro+"],
                "Vivo": ["X100 Pro", "X100", "X90 Pro+", "X90 Pro", "X90", "X80 Pro", "X80", "S18 Pro"]
            }
        for brand in sorted(camera_data.keys()):
            self.parent.cameraBrand.addItem(brand)
        self.camera_data = camera_data
        
    def _load_camera_data(self):
        try:
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'resources', 'json', 'camera_brand_model.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.log("WARNING", f"加载相机品牌型号数据失败: {str(e)}")
        return None
        
    def _on_brand_changed(self, index):
        self.parent.cameraModel.clear()
        if index > 0:
            brand = self.parent.cameraBrand.currentText()
            if brand in self.camera_data:
                for model in sorted(self.camera_data[brand]):
                    self.parent.cameraModel.addItem(model)
        


    def setup_connections(self):
        # 开始按钮连接
        self.parent.btnStartExif.clicked.connect(self.start_exif_writing)
        
        # 星级按钮连接
        for i in range(1, 6):
            getattr(self.parent, f'btnStar{i}').clicked.connect(self.save_exif_settings)
        
        # 相机品牌变化连接
        self.parent.cameraBrand.currentIndexChanged.connect(self._on_brand_changed)

    def update_button_state(self):
        if self.is_running:
            self.parent.btnStartExif.setText("停止写入EXIF信息")
        else:
            self.parent.btnStartExif.setText("开始写入EXIF信息")

    def toggle_exif_writing(self):
        if self.is_running:
            self.stop_exif_writing()
            self.is_running = False
        else:
            success = self.start_exif_writing()
            if success:
                self.is_running = True
        self.update_button_state()

    def connect_worker_signals(self):
        if self.worker:
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.log.connect(self.log)
            self.worker.finished_conversion.connect(self.on_finished)

    @pyqtSlot(int)
    def highlight_stars(self, count):
        for i, btn in enumerate(self.star_buttons, 1):
            icon = "星级_亮.svg" if i <= count else "星级_暗.svg"
            btn.setStyleSheet(f"QPushButton {{ image: url({get_resource_path(f'resources/img/page_4/{icon}')}); border: none; padding: 0; }}")

    @pyqtSlot(int)
    def set_selected_star(self, star):
        self.selected_star = star
        self.highlight_stars(star)

    def parse_dms_coordinates(self, lat_str, lon_str):
        # 移除异常捕获，使用条件检查减少性能开销
        lat_parts = lat_str.strip().replace(' ', '').split(';')
        if len(lat_parts) != 3:
            return None
            
        lon_parts = lon_str.strip().replace(' ', '').split(';')
        if len(lon_parts) != 3:
            return None
            
        try:
            lat_deg = float(lat_parts[0])
            lat_min = float(lat_parts[1])
            lat_sec = float(lat_parts[2])
            
            lon_deg = float(lon_parts[0])
            lon_min = float(lon_parts[1])
            lon_sec = float(lon_parts[2])
            
            lat_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
            lon_decimal = lon_deg + lon_min / 60 + lon_sec / 3600
            
            if -90 <= lat_decimal <= 90 and -180 <= lon_decimal <= 180:
                return lat_decimal, lon_decimal
        except ValueError:
            pass
        return None

    def start_exif_writing(self):
        if not self.folder_page:
            self.log("ERROR", "文件夹页面未初始化\n\n"
                         "请重新启动应用程序或联系技术支持")
            return False
            
        folders = self.folder_page.get_all_folders()
        if not folders:
            self.log("WARNING", "请先导入一个有效的文件夹\n\n"
                           "点击\"导入文件夹\"按钮添加包含图片的文件夹")
            return False
        
        camera_brand = self.parent.cameraBrand.currentText() if self.parent.cameraBrand.currentIndex() > 0 else None
        camera_model = self.parent.cameraModel.currentText() if self.parent.cameraModel.currentIndex() > 0 else None
        
        if camera_brand and not camera_model:
            camera_model = self.get_default_model_for_brand(camera_brand)
        
        params = {
            'folders_dict': folders,
            'title': self.parent.titleLineEdit.text(),
            'author': self.parent.authorLineEdit.text(),
            'subject': self.parent.themeLineEdit.text(),
            'rating': str(self.selected_star),
            'copyright': self.parent.copyrightLineEdit.text(),
            'position': None,
            'cameraBrand': camera_brand,
            'cameraModel': camera_model,
            'lensModel': self.get_lens_info_for_camera(camera_brand, camera_model)
        }
        
        longitude = self.parent.lineEdit_EXIF_longitude.text()
        latitude = self.parent.lineEdit_EXIF_latitude.text()
        if longitude and latitude:
            try:
                lon = float(longitude)
                lat = float(latitude)
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    params['position'] = f"{lat},{lon}"
                else:
                    self.log("ERROR", "经纬度范围无效\n\n"
                                "• 经度应在-180到180之间\n"
                                "• 纬度应在-90到90之间\n\n"
                                "请检查输入的数值是否正确")
                    return False
            except ValueError:
                coords = self.parse_dms_coordinates(latitude, longitude)
                if coords:
                    lat_decimal, lon_decimal = coords
                    if -180 <= lon_decimal <= 180 and -90 <= lat_decimal <= 90:
                        params['position'] = f"{lat_decimal},{lon_decimal}"
                        self.log("INFO", f"成功解析度分秒坐标: 纬度={lat_decimal}, 经度={lon_decimal}")
                    else:
                        self.log("ERROR", "经纬度范围无效\n\n"
                                    "• 经度应在-180到180之间\n"
                                    "• 纬度应在-90到90之间\n\n"
                                    "请检查输入的数值是否正确")
                        return False
                else:
                    self.log("ERROR", "经纬度格式无效\n\n"
                                "请输入有效的数字格式，例如：\n"
                                "• 十进制格式: 经度116.397128, 纬度39.916527\n"
                                "• 度分秒格式: 经度120;23;53.34, 纬度30;6;51.51")
                    return False
            else:
                self.log("ERROR", "请输入经纬度信息\n\n"
                             "请在对应的文本框中输入经度和纬度值")
                return False
        
        self.save_exif_settings()
        
        operation_summary = f"操作类型: EXIF信息写入"
        if params.get('title'):
            operation_summary += f", 标题: {params['title']}"
        if params.get('author'):
            operation_summary += f", 作者: {params['author']}"
        if params.get('position'):
            operation_summary += f", 位置: {params['position']}"
        if params.get('rating') != '0':
            operation_summary += f", 评分: {params['rating']}星"
        
        self.log("INFO", f"摘要: {operation_summary}")
        
        self.error_messages = []
        
        self.worker = WriteExifThread(**params)
        self.connect_worker_signals()
        self.worker.start()
        self.parent.progressBar_EXIF.setValue(0)
        return True

    def stop_exif_writing(self):
        if self.worker:
            self.worker.stop()
            self.worker.wait(1000)
            if self.worker.isRunning():
                self.worker.terminate()
            self.log("WARNING", "正在停止EXIF写入操作...")
        self.is_running = False
        self.update_button_state()

    def update_progress(self, value):
        self.parent.progressBar_EXIF.setValue(value)

    def log(self, level, message):
        c = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'DEBUG': '#008000', 'INFO': '#8677FD'}
        
        if level == 'ERROR':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.error_messages.append(f"[{timestamp}] [{level}] {message}")
        
        try:
            self.parent.txtWriteEXIFLog.append(
                f'<span style="color:{c.get(level, "#000000")}">[{datetime.now().strftime("%H:%M:%S")}] [{level}] {message}</span>')
        except Exception as e:
            print(f"日志更新错误: {e}")

    def on_finished(self):
        self.is_running = False
        self.update_button_state()
        
        if self.error_messages:
            QMessageBox.information(
                self.parent, 
                "操作完成", 
                f"写入操作完成，但是有 {len(self.error_messages)} 个错误！\n\n"
                "您可以在原文件夹中查看更新后的文件。"
            )
        else:
            QMessageBox.information(
                self.parent, 
                "操作完成", 
                "EXIF信息写入操作已完成！\n\n"
                "所有选定的图片文件已成功更新EXIF信息。\n\n"
                "您可以在原文件夹中查看更新后的文件。"
            )

    def load_exif_settings(self):
        # 移除通用异常捕获，减少性能开销
        if title := config_manager.get_setting("exif_title"):
            self.parent.titleLineEdit.setText(title)
        
        if author := config_manager.get_setting("exif_author"):
            self.parent.authorLineEdit.setText(author)
            
        if subject := config_manager.get_setting("exif_subject"):
            self.parent.themeLineEdit.setText(subject)
            
        if copyright := config_manager.get_setting("exif_copyright"):
            self.parent.copyrightLineEdit.setText(copyright)
            
        if latitude := config_manager.get_setting("exif_latitude"):
            self.parent.lineEdit_EXIF_latitude.setText(latitude)
            
        if longitude := config_manager.get_setting("exif_longitude"):
            self.parent.lineEdit_EXIF_longitude.setText(longitude)
        
        if camera_brand := config_manager.get_setting("exif_camera_brand"):
            index = self.parent.cameraBrand.findText(camera_brand)
            if index >= 0:
                self.parent.cameraBrand.setCurrentIndex(index)
                self._on_brand_changed(index)
        
        if camera_model := config_manager.get_setting("exif_camera_model"):
            index = self.parent.cameraModel.findText(camera_model)
            if index >= 0:
                self.parent.cameraModel.setCurrentIndex(index)
        
        if star_rating := config_manager.get_setting("exif_star_rating"):
            try:
                self.set_selected_star(int(star_rating))
            except ValueError:
                pass

    def save_exif_settings(self):
        # 移除通用异常捕获，config_manager内部已处理异常
        config_manager.update_setting("exif_title", self.parent.titleLineEdit.text())
        config_manager.update_setting("exif_author", self.parent.authorLineEdit.text())
        config_manager.update_setting("exif_subject", self.parent.themeLineEdit.text())
        config_manager.update_setting("exif_copyright", self.parent.copyrightLineEdit.text())
        
        config_manager.update_setting("exif_latitude", self.parent.lineEdit_EXIF_latitude.text())
        config_manager.update_setting("exif_longitude", self.parent.lineEdit_EXIF_longitude.text())
        
        config_manager.update_setting("exif_camera_brand", self.parent.cameraBrand.currentText())
        config_manager.update_setting("exif_camera_model", self.parent.cameraModel.currentText())
        
        config_manager.update_setting("exif_star_rating", self.selected_star)
