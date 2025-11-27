import json
import logging
import os
from datetime import datetime
from PyQt6.QtCore import pyqtSignal, QObject, pyqtSlot, QSize
from PyQt6.QtGui import QIcon, QPixmap
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
        self.setup_connections()
        self.init_ui()

    def init_ui(self):
        for i in range(1, 6):
            btn = getattr(self.parent, f'btnStar{i}')
            icon = QIcon()
            icon.addPixmap(QPixmap(get_resource_path('resources/img/page_4/星级_暗.svg')), QIcon.Mode.Normal, QIcon.State.Off)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))
            btn.setStyleSheet("border: none; padding: 0")
            btn.enterEvent = lambda e, idx=i: self.highlight_stars(idx)
            btn.leaveEvent = lambda e: self.highlight_stars(self.selected_star)
            btn.clicked.connect(lambda _, idx=i: self.set_selected_star(idx))
            self.star_buttons.append(btn)

        self.init_camera_brand_model()
        self.load_camera_lens_mapping()

        from PyQt6.QtCore import QDateTime
        self.parent.dateTimeEdit_shootTime.setDateTime(QDateTime.currentDateTime())
        self._on_shoot_time_source_changed(self.parent.shootTimeSource.currentIndex())

        self.update_button_state()
        self.load_exif_settings()

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
        lens_info = {'lens_brand': '', 'lens_model': ''}
        
        if not brand or not model:
            logger.debug(f"品牌或型号为空: brand={brand}, model={model}")
            return lens_info
        
        try:
            if not self.camera_lens_mapping:
                logger.debug("相机镜头映射数据未加载")
                return lens_info
            
            if brand in self.camera_lens_mapping:
                brand_data = self.camera_lens_mapping[brand]
                if isinstance(brand_data, dict):
                    if model in brand_data:
                        lens_info['lens_model'] = brand_data[model]
                        brand_mapping = {
                            'Canon': 'Canon',
                            'Nikon': 'Nikon',
                            'Sony': 'Sony',
                            'Fujifilm': 'Fujifilm',
                            'Leica': 'Leica',
                            'Panasonic': 'Panasonic',
                            'Olympus': 'Olympus',
                            'Pentax': 'Pentax',
                            'Sigma': 'Sigma',
                            'Xiaomi': 'Xiaomi',
                            'Huawei': 'Huawei',
                            'Apple': 'Apple',
                            'Samsung': 'Samsung',
                            'OPPO': 'OPPO',
                            'vivo': 'vivo',
                            'OnePlus': 'OnePlus',
                            'Google': 'Google'
                        }
                        if brand in brand_mapping:
                            lens_info['lens_brand'] = brand_mapping[brand]
                        logger.debug(f"成功匹配镜头信息: 品牌={lens_info['lens_brand']}, 型号={lens_info['lens_model']}")
                    else:
                        logger.debug(f"未找到型号 {model} 对应的镜头信息")
                else:
                    logger.debug(f"品牌 {brand} 的数据格式不正确")
            else:
                logger.debug(f"未找到品牌 {brand} 的镜头映射数据")
        except Exception as e:
            logger.error(f"获取镜头信息失败: {str(e)}")
        
        return lens_info

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
                "Apple": ["iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15", "iPhone 14 Pro Max", "iPhone 14 Pro",
                          "iPhone 14", "iPhone 13 Pro Max", "iPhone 13 Pro"],
                "OnePlus": ["12 Pro", "12", "11 Pro", "11", "10 Pro", "10", "9 Pro", "9"],
                "Xiaomi": ["14 Ultra", "14 Pro", "14", "13 Ultra", "13 Pro", "13", "12S Ultra", "12S Pro"],
                "Huawei": ["P60 Pro", "P60", "Mate 60 Pro", "Mate 60", "P50 Pro", "P50", "Mate 50 Pro", "Mate 50"],
                "OPPO": ["Find X6 Pro", "Find X6", "Find X5 Pro", "Find X5", "Reno10 Pro+", "Reno10 Pro", "Reno10",
                         "Reno9 Pro+"],
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
        self.parent.btnStartExif.clicked.connect(self.toggle_exif_writing)
        
        for i in range(1, 6):
            getattr(self.parent, f'btnStar{i}').clicked.connect(self.save_exif_settings)
        
        self.parent.cameraBrand.currentIndexChanged.connect(self._on_brand_changed)
        # 添加shootTimeSource下拉框变化的连接
        self.parent.shootTimeSource.currentIndexChanged.connect(self._on_shoot_time_source_changed)
        self.log_signal.connect(self._update_log_display)

    def _on_shoot_time_source_changed(self, index):
        """当拍摄时间源下拉框变化时，控制dateTimeEdit_shootTime的显示/隐藏"""
        # 当选择"不写入"(0)或"从文件名"(1)时隐藏dateTimeEdit_shootTime控件
        if index in [0, 1]:
            self.parent.dateTimeEdit_shootTime.setVisible(False)
        else:
            # 当选择"指定时间"(2)时显示dateTimeEdit_shootTime控件
            self.parent.dateTimeEdit_shootTime.setVisible(True)

    def update_button_state(self):
        if self.is_running:
            self.parent.btnStartExif.setText("停止写入EXIF信息")
        else:
            self.parent.btnStartExif.setText("开始写入EXIF信息")

    def toggle_exif_writing(self):
        """切换EXIF写入状态"""
        if not self.folder_page:
            self.log("ERROR", "文件夹页面未初始化\n\n"
                              "请重新启动应用程序或联系技术支持")
            return False

        thread_running = bool(self.worker and self.worker.isRunning())
        if thread_running:
            self.log("INFO", "正在停止操作")
            self.parent.btnStartExif.setText("正在停止...")
            try:
                self.stop_exif_writing()
                self.is_running = False
                return False
            except Exception as e:
                self.log("ERROR", f"停止线程时出错: {str(e)}")
                self.is_running = False
                self.update_button_state()
                return False
        else:
            folders = self.folder_page.get_all_folders() if self.folder_page else []
            if not folders:
                self.log("WARNING", "没有选择文件夹")
                try:
                    QMessageBox.warning(self.parent, "警告", "请先选择要处理的文件夹！")
                except Exception as e:
                    self.log("ERROR", f"显示警告消息失败: {str(e)}")
                return False
            
            if not hasattr(self.folder_page, 'get_target_folder') or not self.folder_page.get_target_folder():
                self.log("WARNING", "未选择有效的目标文件夹")
                try:
                    QMessageBox.warning(self.parent, "警告", "请先选择目标文件夹！")
                except Exception as e:
                    self.log("ERROR", f"显示警告消息失败: {str(e)}")
                return False
            
            success = self.start_exif_writing()
            if success:
                self.is_running = True
            return success

    def connect_worker_signals(self):
        if self.worker:
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.log_signal.connect(self.log)
            self.worker.finished_conversion.connect(self.on_finished)

    @pyqtSlot(int)
    def highlight_stars(self, count):
        for i, btn in enumerate(self.star_buttons, 1):
            icon = QIcon()
            icon_path = '星级_亮.svg' if i <= count else '星级_暗.svg'
            icon.addPixmap(QPixmap(get_resource_path(f'resources/img/page_4/{icon_path}')), QIcon.Mode.Normal, QIcon.State.Off)
            btn.setIcon(icon)
            btn.setIconSize(QSize(20, 20))

    @pyqtSlot(int)
    def set_selected_star(self, star):
        self.selected_star = star
        self.highlight_stars(star)

    def parse_dms_coordinates(self, lat_str, lon_str):
        lat_str = ''.join(char for char in lat_str if ord(char) < 128).strip().replace(' ', '')
        lon_str = ''.join(char for char in lon_str if ord(char) < 128).strip().replace(' ', '')
        
        lat_parts = lat_str.split(';')
        if len(lat_parts) != 3:
            return None

        lon_parts = lon_str.split(';')
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

        target_folder = self.folder_page.get_target_folder() if hasattr(self.folder_page, 'get_target_folder') else None
        if not target_folder:
            self.log("WARNING", "未选择有效的目标文件夹")
            QMessageBox.warning(self.parent, "警告", "请先选择目标文件夹！")
            return False

        folders = self.folder_page.get_all_folders()

        camera_brand = self.parent.cameraBrand.currentText() if self.parent.cameraBrand.currentIndex() > 0 else None
        camera_model = self.parent.cameraModel.currentText() if self.parent.cameraModel.currentIndex() > 0 else None

        if camera_brand and not camera_model:
            camera_model = self.get_default_model_for_brand(camera_brand)

        folders_dict = []
        for folder_path in folders:
            if folder_path and os.path.exists(folder_path) and os.path.isdir(folder_path):
                folders_dict.append({
                    'path': folder_path,
                    'include_sub': True
                })
        
        lens_info = self.get_lens_info_for_camera(camera_brand, camera_model)
        
        if lens_info['lens_brand'] or lens_info['lens_model']:
            self.log("INFO", f"为相机 {camera_brand} {camera_model} 匹配到镜头: {lens_info['lens_brand']} {lens_info['lens_model']}")
        
        shoot_time_source = self.parent.shootTimeSource.currentIndex()
        shoot_time_value = 0
        
        if shoot_time_source == 1:
            shoot_time_value = 1
        elif shoot_time_source == 2:
            shoot_time_value = self.parent.dateTimeEdit_shootTime.dateTime().toString("yyyy:MM:dd HH:mm:ss")
        
        exif_config = {
            'title': self.parent.titleLineEdit.text(),
            'author': self.parent.authorLineEdit.text(),
            'subject': self.parent.themeLineEdit.text(),
            'rating': str(self.selected_star),
            'copyright': self.parent.copyrightLineEdit.text(),
            'position': None,
            'camera_brand': camera_brand,
            'camera_model': camera_model,
            'lens_brand': lens_info.get('lens_brand', ''),
            'lens_model': lens_info.get('lens_model', ''),
            'shoot_time': shoot_time_value
        }

        longitude = self.parent.lineEdit_EXIF_longitude.text().strip()
        latitude = self.parent.lineEdit_EXIF_latitude.text().strip()
        if longitude and latitude:
            def clean_coordinate(text):
                cleaned = ''.join(char for char in text if char.isdigit() or char in ['.', '-'])
                return cleaned
            
            cleaned_longitude = clean_coordinate(longitude)
            cleaned_latitude = clean_coordinate(latitude)
            
            try:
                lon = float(cleaned_longitude)
                lat = float(cleaned_latitude)
                if -180 <= lon <= 180 and -90 <= lat <= 90:
                    exif_config['position'] = f"{lat},{lon}"
                else:
                    self.log("ERROR", "经纬度范围无效\n\n"
                                      f"• 经度 {lon} 应在-180到180之间\n"
                                      f"• 纬度 {lat} 应在-90到90之间\n\n"
                                      "请检查输入的数值是否正确")
                    return False
            except ValueError as e:
                self.log("WARNING", f"尝试转换为浮点数时出错: {str(e)}")
                coords = self.parse_dms_coordinates(latitude, longitude)
                if coords:
                    lat_decimal, lon_decimal = coords
                    if -180 <= lon_decimal <= 180 and -90 <= lat_decimal <= 90:
                        exif_config['position'] = f"{lat_decimal},{lon_decimal}"
                        self.log("INFO", f"成功解析度分秒坐标: 经度={lon_decimal}, 纬度={lat_decimal}")
                    else:
                        self.log("ERROR", "经纬度范围无效\n\n"
                                          "• 经度应在-180到180之间\n"
                                          "• 纬度应在-90到90之间\n\n"
                                          "请检查输入的数值是否正确")
                        return False
                else:
                    self.log("WARNING", f"无法解析经纬度: 经度={longitude}, 纬度={latitude}")
                    self.log("ERROR", "经纬度格式无效!请输入有效的地理坐标，支持十进制格式: 经度116.397128, 纬度39.916527 与 度分秒格式: 经度120;23;53.34, 纬度30;6;51.51")
                    return False

        self.save_exif_settings()

        operation_summary = f"操作类型: EXIF信息写入"
        if exif_config.get('title'):
            operation_summary += f", 标题: {exif_config['title']}"
        if exif_config.get('author'):
            operation_summary += f", 作者: {exif_config['author']}"
        if exif_config.get('copyright'):
            operation_summary += f", 版权: {exif_config['copyright']}"
        if exif_config.get('position'):
            operation_summary += f", 位置: {exif_config['position']}"
        if exif_config.get('rating') != '0':
            operation_summary += f", 评分: {exif_config['rating']}星"

        self.log("WARNING", f"写入摘要: {operation_summary}")

        self.is_running = True
        self.update_button_state()
        
        self.error_messages = []

        self.worker = WriteExifThread(folders_dict, exif_config, target_folder)
        self.connect_worker_signals()
        self.worker.start()
        self.parent.progressBar_EXIF.setValue(0)
        return True

    def stop_exif_writing(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(1000)
            if self.worker.isRunning():
                self.worker.terminate()
            self.log("INFO", "已取消操作")
        self.is_running = False
        self.update_button_state()
        return False

    def update_progress(self, value):
        self.parent.progressBar_EXIF.setValue(value)

    def _update_log_display(self, level, message):
        message_str = str(message)
        color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD', 'DEBUG': '#006400'}
        color = color_map.get(level, '#006400')
            
        try:
            self.parent.txtWriteEXIFLog.append(
                f'<div style="margin: 2px 0; padding: 2px 4px; border-left: 3px solid {color};">'
                f'<span style="color:{color};">{message_str}</span>'
                f'</div>'
            )
            self.parent.txtWriteEXIFLog.verticalScrollBar().setValue(
                self.parent.txtWriteEXIFLog.verticalScrollBar().maximum()
            )
        except AttributeError:
            pass

    def log(self, level, message):
        try:
            if not isinstance(level, str) or not isinstance(message, str):
                raise TypeError("日志级别和消息必须是字符串类型")
            
            valid_levels = {'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'}
            if level not in valid_levels:
                level = 'INFO'
            
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_message = f"[{current_time}] {level}: {message}"
            
            self.log_signal.emit(level, log_message)
            
            if level == 'ERROR':
                logger.error(message)
                self.error_messages.append(log_message)
            elif level == 'WARNING':
                logger.warning(message)
            elif level == 'DEBUG':
                logger.debug(message)
            else:
                logger.info(message)
        except Exception as e:
            try:
                error_msg = f"日志记录失败: {str(e)}"
                logger.error(error_msg)
            except:
                pass

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
                logger.warning(f"无法转换星级评分: {star_rating}")
        
        if shoot_time_source := config_manager.get_setting("exif_shoot_time_source"):
            try:
                self.parent.shootTimeSource.setCurrentIndex(int(shoot_time_source))
            except (ValueError, TypeError):
                logger.warning(f"无法转换拍摄时间来源: {shoot_time_source}")
        
        # 不从配置中读取拍摄时间，始终显示当前时间
        pass

    def save_exif_settings(self):
        try:
            config_manager.update_setting("exif_title", self.parent.titleLineEdit.text())
            config_manager.update_setting("exif_author", self.parent.authorLineEdit.text())
            config_manager.update_setting("exif_subject", self.parent.themeLineEdit.text())
            config_manager.update_setting("exif_copyright", self.parent.copyrightLineEdit.text())

            config_manager.update_setting("exif_latitude", self.parent.lineEdit_EXIF_latitude.text())
            config_manager.update_setting("exif_longitude", self.parent.lineEdit_EXIF_longitude.text())

            config_manager.update_setting("exif_camera_brand", self.parent.cameraBrand.currentText())
            config_manager.update_setting("exif_camera_model", self.parent.cameraModel.currentText())

            config_manager.update_setting("exif_star_rating", self.selected_star)
            
            config_manager.update_setting("exif_shoot_time_source", self.parent.shootTimeSource.currentIndex())
            config_manager.update_setting("exif_shoot_time", self.parent.dateTimeEdit_shootTime.dateTime().toString("yyyy:MM:dd HH:mm:ss"))
        except Exception as e:
            logger.error(f"保存EXIF设置失败: {str(e)}")