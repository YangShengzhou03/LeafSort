import json
import os
import requests
from datetime import datetime
from PyQt6.QtCore import pyqtSlot, QDateTime
from PyQt6.QtWidgets import QWidget, QMessageBox
from write_exif_thread import WriteExifThread
from common import get_resource_path
from config_manager import config_manager


class WriteExifPage(QWidget):    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        try:
            self.parent.log("info", "属性写入页面初始化")
        except (AttributeError, TypeError):
            pass
        self.folder_page = self.parent.folder_page

        self.selected_star = 0
        self.star_buttons = []
        self.camera_lens_mapping = {}
        self.error_messages = []
        self.init_ui()
        self.setup_connections()
        
    def init_page(self):
        """初始化页面组件和数据"""
        try:
            self.parent.log("info", "初始化属性写入页面")
        except (AttributeError, TypeError):
            pass
        self.folder_page = self.parent.folder_page
        self.setup_connections()
        self.load_camera_lens_mapping()

    def init_ui(self):
        self.star_buttons = []
        # 定义按钮名称映射
        button_names = {
            1: 'starButton1',
            2: 'ratingStar2Button',
            3: 'ratingStar3Button',
            4: 'ratingStar4Button',
            5: 'ratingStar5Button'
        }
        
        for i in range(1, 6):
            btn_name = button_names.get(i)
            btn = getattr(self.parent, btn_name)
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
        
        self.update_button_state()
        self.parent.dateTimeEdit_shootTime.setDateTime(QDateTime.currentDateTime())
        self.load_exif_settings()
        self.save_exif_settings()
        self.parent.log('INFO', "欢迎使用图像属性写入，不写入项留空即可。文件一旦写入无法还原。")
        
    def load_camera_lens_mapping(self):
        try:
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'resources', 'json', 'camera_lens_mapping.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.camera_lens_mapping = json.load(f)
            else:
                self.parent.log('WARNING', "相机镜头映射文件不存在，将使用默认镜头信息")
        except Exception as e:
              self.parent.log('WARNING', f"加载相机镜头映射数据失败: {str(e)}")
              self.camera_lens_mapping = {}

    def get_lens_info_for_camera(self, brand, model):
        if brand in self.camera_lens_mapping:
            brand_data = self.camera_lens_mapping[brand]
            if model in brand_data:
                return brand_data[model]
        return None

    def _update_camera_brand_model(self):
        """更新相机品牌和型号下拉框"""
        try:
            self.dateTimeEdit_shootTime.setDateTime(QtCore.QDateTime.currentDateTime())
        except (AttributeError, TypeError):
            pass
    
    def _on_model_changed(self, index):
        try:
            if index > 0:
                # 通过父窗口获取当前选择的品牌和型号
                brand = self.parent.cameraBrand.currentText()
                # 尝试获取相机型号下拉框的当前文本
                try:
                    camera_model_combo = getattr(self.parent, 'cameraModel', None)
                    if camera_model_combo:
                        model = camera_model_combo.currentText()
                        self.get_lens_info_for_camera(brand, model)
                except (AttributeError, TypeError):
                    pass
            
            self.update_button_state()
            # 确保通过父窗口访问日期时间编辑器
            try:
                self.parent.dateTimeEdit_shootTime.setDateTime(QDateTime.currentDateTime())
                self.parent.dateTimeEdit_shootTime.hide()
            except (AttributeError, TypeError):
                pass
        except Exception as e:
            try:
                self.parent.log("error", f"型号改变事件处理错误: {str(e)}")
            except (AttributeError, TypeError):
                pass

    def _load_camera_data(self):
        """从JSON文件加载相机品牌和型号数据"""
        import json
        import os
        
        json_path = os.path.join('resources', 'json', 'camera_brand_model.json')
        try:
            # 读取相机品牌和型号数据
            try:
                self.parent.log("debug", "加载相机品牌型号数据")
            except (AttributeError, TypeError):
                pass
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            # 如果文件不存在或解析错误，记录警告并返回None
            self.parent.log('WARNING', f'无法加载相机数据文件 {json_path}: {str(e)}')
            return None
    
    def init_camera_brand_model(self):
        camera_data = self._load_camera_data()

        if not camera_data:
            camera_data = {
                "Apple": ["iPhone 15 Pro Max", "iPhone 15 Pro", "iPhone 15", "iPhone 14 Pro Max", "iPhone 14 Pro", "iPhone 14", "iPhone 13 Pro Max", "iPhone 13 Pro"],
                "Samsung": ["Galaxy S24 Ultra", "Galaxy S24+", "Galaxy S24", "Galaxy S23 Ultra", "Galaxy S23+", "Galaxy S23", "Galaxy Z Fold5", "Galaxy Z Flip5"],
                "Google": ["Pixel 8 Pro", "Pixel 8", "Pixel 7 Pro", "Pixel 7", "Pixel 6 Pro", "Pixel 6", "Pixel 5"],
                "OnePlus": ["12 Pro", "12", "11 Pro", "11", "10 Pro", "10", "9 Pro", "9"],
                "Xiaomi": ["14 Ultra", "14 Pro", "14", "13 Ultra", "13 Pro", "13", "12S Ultra", "12S Pro"],
                "Huawei": ["P60 Pro", "P60", "Mate 60 Pro", "Mate 60", "P50 Pro", "P50", "Mate 50 Pro", "Mate 50"],
                "OPPO": ["Find X6 Pro", "Find X6", "Find X5 Pro", "Find X5", "Reno10 Pro+", "Reno10 Pro", "Reno10", "Reno9 Pro+"],
                "Vivo": ["X100 Pro", "X100", "X90 Pro+", "X90 Pro", "X90", "X80 Pro", "X80", "S18 Pro"]
            }
        
        try:
            # 填充相机品牌下拉框
            brands = ['不写入'] + list(camera_data.keys())
            self.parent.cameraBrand.addItems(brands)
            self.parent.cameraBrand.currentIndexChanged.connect(self._on_brand_changed)
        except (AttributeError, TypeError):
            try:
                self.parent.log("warning", "未找到相机品牌或型号下拉框")
            except (AttributeError, TypeError):
                pass
        self.camera_data = camera_data
        # 通过父窗口访问正确的组件名称
        try:
            # 确保已经正确设置了相机品牌下拉框的连接
            pass  # 连接已经在上面的try块中设置
        except (AttributeError, TypeError):
            try:
                self.parent.log("warning", "无法设置相机品牌/型号下拉框连接")
            except (AttributeError, TypeError):
                pass
        
    def _on_brand_changed(self, index):
        """当相机品牌改变时，更新型号下拉框"""
        try:
            # 尝试获取相机型号下拉框并更新
            # 注意：从UI定义看，可能需要找到正确的相机型号下拉框名称
            # 这里我们假设UI中有一个名为cameraModel的组件
            try:
                camera_model_combo = getattr(self.parent, 'cameraModel', None)
                if camera_model_combo:
                    camera_model_combo.clear()
                    if index > 0:
                        brand = self.parent.cameraBrand.currentText()
                        models = ['不写入'] + self.camera_data.get(brand, [])
                        camera_model_combo.addItems(models)
            except (AttributeError, TypeError):
                try:
                    self.parent.log("warning", "无法更新相机型号下拉框")
                except (AttributeError, TypeError):
                    pass
        except Exception as e:
            try:
                self.parent.log("error", f"品牌改变事件处理错误: {str(e)}")
            except (AttributeError, TypeError):
                pass
        


    def setup_connections(self):
        # 直接连接控件
        self.parent.btnStartExif.clicked.connect(self.toggle_exif_writing)
            
        # 为位置更新按钮添加连接（如果存在）
        # 注意：在UI文件中没有找到pushButton_Position的直接对应组件
        
        self.parent.shootTimeSource.currentIndexChanged.connect(self.on_combobox_time_changed)
            
        # 为所有文本框连接添加hasattr检查
        # 使用正确的组件名称
        text_fields_mapping = {
            'authorLineEdit': 'lineEdit_EXIF_Author',
            'themeLineEdit': 'lineEdit_EXIF_Theme',
            'copyrightLineEdit': 'lineEdit_EXIF_Copyright',
            'lineEdit_EXIF_latitude': 'lineEdit_EXIF_latitude',
            'lineEdit_EXIF_longitude': 'lineEdit_EXIF_longitude'
        }
        
        for actual_name, old_name in text_fields_mapping.items():
            getattr(self.parent, actual_name).textChanged.connect(self.save_exif_settings)
                
        self.parent.cameraBrand.currentIndexChanged.connect(self.save_exif_settings)
        self.parent.cameraModel.currentIndexChanged.connect(self.save_exif_settings)
            
        # 星级按钮连接已经在init_ui中处理

    def on_combobox_location_changed(self, index):
            if index == 1:
                self.parent.lineEdit_EXIF_longitude.show()
                self.parent.lineEdit_EXIF_latitude.show()
                self.parent.horizontalFrame.hide()
            else:
                self.parent.lineEdit_EXIF_longitude.hide()
                self.parent.lineEdit_EXIF_latitude.hide()
                self.parent.horizontalFrame.show()

    def on_combobox_time_changed(self, index):
        if self.parent.shootTimeSource.currentIndex() == 2:
            self.parent.dateTimeEdit_shootTime.show()
        else:
            self.parent.dateTimeEdit_shootTime.hide()

    def update_button_state(self):
        # 直接使用parent中的btnStartExif
        if self.is_running:
            self.parent.btnStartExif.setText("停止")
        else:
            self.parent.btnStartExif.setText("开始")

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
            self.worker.log_signal.connect(self.log)
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

    def get_location(self, address):
        try:
            url = "https://restapi.amap.com/v3/geocode/geo"
            amap_key = '0db079da53e08cbb62b52a42f657b994'
            
            params = {
                'address': address, 
                'key': amap_key, 
                'output': 'JSON',
                'city': '全国'
            }
            
            self.log("INFO", f"正在请求高德地图API，地址: {address}")
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            self.log("INFO", f"高德地图API返回数据: {data}")
            
            if data.get('status') == '1' and int(data.get('count', 0)) > 0:
                location = data['geocodes'][0]['location'].split(',')
                self.log("INFO", f"成功获取位置坐标: 纬度={location[1]}, 经度={location[0]}")
                return location
            else:
                error_info = data.get('info', '未知错误')
                error_code = data.get('infocode', '未知错误码')
                self.log("ERROR", f"高德地图API返回错误: {error_info} (错误码: {error_code})")
                
                if len(address) > 10:
                    simplified_address = address[:10]
                    self.log("INFO", f"尝试使用简化地址再次请求: {simplified_address}")
                    params['address'] = simplified_address
                    response = requests.get(url, params=params, timeout=5)
                    response.raise_for_status()
                    data = response.json()
                    
                    if data.get('status') == '1' and int(data.get('count', 0)) > 0:
                        location = data['geocodes'][0]['location'].split(',')
                        self.log("INFO", f"使用简化地址成功获取位置坐标: 纬度={location[1]}, 经度={location[0]}")
                        return location
        except Exception as e:
            self.log("ERROR", f"获取位置失败: {str(e)}")
        return None

    def get_location_by_ip(self):
        try:
            response = requests.get('https://ipinfo.io', timeout=5)
            data = response.json()
            if 'loc' in data:
                lat, lon = data['loc'].split(',')
                location = f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country', '')}"
                self.parent.lineEdit_EXIF_Position.setText(location)
                return lat, lon
            else:
                self.log("ERROR", "无法解析位置信息\n\n"
                             "IP地址定位服务返回的数据格式异常")
                return None
        except Exception as e:
            self.log("ERROR", f"获取位置信息失败: {str(e)}\n\n"
                         "请检查网络连接或稍后重试")
            return None

    def parse_dms_coordinates(self, lat_str, lon_str):
        try:
            lat_parts = lat_str.strip().replace(' ', '').split(';')
            if len(lat_parts) != 3:
                return None
                
            lat_deg = float(lat_parts[0])
            lat_min = float(lat_parts[1])
            lat_sec = float(lat_parts[2])
            
            lon_parts = lon_str.strip().replace(' ', '').split(';')
            if len(lon_parts) != 3:
                return None
                
            lon_deg = float(lon_parts[0])
            lon_min = float(lon_parts[1])
            lon_sec = float(lon_parts[2])
            
            lat_decimal = lat_deg + lat_min / 60 + lat_sec / 3600
            lon_decimal = lon_deg + lon_min / 60 + lon_sec / 3600
            
            if -90 <= lat_decimal <= 90 and -180 <= lon_decimal <= 180:
                return lat_decimal, lon_decimal
            else:
                return None
                
        except Exception as e:
            self.log("ERROR", f"解析度分秒坐标失败: {str(e)}")
            return None

    def update_position_by_ip(self):
        location_info = self.get_location_by_ip()
        if location_info is not None:
            lat, lon = location_info
            self.parent.lineEdit_EXIF_Position.setText(f"{lat}, {lon}")
            self.log("WARNING", f"当前纬度={lat}, 经度={lon}，位置已加载，可直接开始。")
        else:
            self.log("ERROR", "获取位置信息失败\n\n"
                         "可能的原因：\n"
                         "• 网络连接异常\n"
                         "• 定位服务暂时不可用\n"
                         "• 防火墙或代理设置阻止了网络请求")

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
        
        # 直接获取文本框内容
        title = self.parent.titleLineEdit.text()
        author = self.parent.authorLineEdit.text()
        subject = self.parent.themeLineEdit.text()
        copyright = self.parent.copyrightLineEdit.text()
        
        params = {
            'folders_dict': folders,
            'title': title,
            'author': author,
            'subject': subject,
            'rating': str(self.selected_star),
            'copyright': copyright,
            'position': None,
            'shootTime': self.parent.dateTimeEdit_shootTime.dateTime().toString(
                "yyyy:MM:dd HH:mm:ss")
            if self.parent.shootTimeSource.currentIndex() == 2
            else self.parent.shootTimeSource.currentIndex(),
            'cameraBrand': camera_brand,
            'cameraModel': camera_model,
            'lensModel': self.get_lens_info_for_camera(camera_brand, camera_model)
        }
        
        location_type = self.parent.locationComboBox.currentIndex()
        if location_type == 0:
            address = self.parent.lineEdit_EXIF_Position.text()
            if address:
                import re
                coord_pattern = r'^\s*(-?\d+\.?\d*)\s*,\s*(-?\d+\.?\d*)\s*$'
                coord_match = re.match(coord_pattern, address)
                
                if coord_match:
                    lat, lon = coord_match.groups()
                    try:
                        lat_float = float(lat)
                        lon_float = float(lon)
                        if -90 <= lat_float <= 90 and -180 <= lon_float <= 180:
                            params['position'] = f"{lat_float},{lon_float}"
                        else:
                            self.log("ERROR", "坐标范围无效\n\n"
                                     "• 经度应在-180到180之间\n"
                                     "• 纬度应在-90到90之间")
                            return False
                    except ValueError:
                        self.log("ERROR", "坐标格式无效\n\n"
                                 "请输入有效的数字格式")
                        return False
                else:
                    dms_pattern = r'纬度\s*([0-9;.\s]+)\s*经度\s*([0-9;.\s]+)'
                    dms_match = re.match(dms_pattern, address)
                    
                    if not dms_match:
                        dms_pattern = r'([0-9;.\s]+)\s*,\s*([0-9;.\s]+)'
                        dms_match = re.match(dms_pattern, address)
                    
                    if dms_match:
                        lat_str, lon_str = dms_match.groups()
                        coords = self.parse_dms_coordinates(lat_str, lon_str)
                        if coords:
                            lat_decimal, lon_decimal = coords
                            params['position'] = f"{lat_decimal},{lon_decimal}"
                            self.log("INFO", f"成功解析度分秒坐标: 纬度={lat_decimal}, 经度={lon_decimal}")
                        else:
                            self.log("ERROR", "度分秒坐标格式无效\n\n"
                                     "请确保格式为：纬度30;6;51.50999999999474 经度120;23;53.3499999999766317")
                            return False
                    else:
                        if coords := self.get_location(address):
                            params['position'] = ','.join(coords)
                        else:
                            self.log("ERROR", f"无法找到地址'{address}'对应的地理坐标\n\n"
                                       "请检查：\n"
                                       "• 地址拼写是否正确\n"
                                       "• 是否包含详细的门牌号或地标\n"
                                       "• 高德地图API密钥是否有效")
                            return False
        elif location_type == 1:
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
        
        camera_brand = self.parent.brandComboBox.currentText() if self.parent.brandComboBox.currentIndex() > 0 else None
        camera_model = self.parent.modelComboBox.currentText() if self.parent.modelComboBox.currentIndex() > 0 else None
        
        if camera_brand and not camera_model:
            camera_model = self.get_default_model_for_brand(camera_brand)
        
        params = {
            'folders_dict': folders,
            'title': self.parent.lineEdit_EXIF_Title.text(),
            'author': self.parent.lineEdit_EXIF_Author.text(),
            'subject': self.parent.lineEdit_EXIF_Theme.text(),
            'rating': str(self.selected_star),
            'copyright': self.parent.lineEdit_EXIF_Copyright.text(),
            'position': None,
            'shootTime': self.parent.dateTimeEdit_shootTime.dateTime().toString(
                "yyyy:MM:dd HH:mm:ss")
            if self.parent.shootTimeComboBox.currentIndex() == 2
            else self.parent.shootTimeComboBox.currentIndex(),
            'cameraBrand': camera_brand,
            'cameraModel': camera_model,
            'lensModel': self.get_lens_info_for_camera(camera_brand, camera_model)
        }
        
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
        if level == 'ERROR':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.error_messages.append(f"[{timestamp}] [{level}] {message}")
        
        # 直接使用parent的log方法
        self.parent.log(level, message)

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
        try:
            # 直接使用控件
            if title := config_manager.get_setting("exif_title"):
                self.parent.titleLineEdit.setText(title)
            
            if author := config_manager.get_setting("exif_author"):
                self.parent.authorLineEdit.setText(author)
            
            if subject := config_manager.get_setting("exif_subject"):
                self.parent.themeLineEdit.setText(subject)
            
            if copyright := config_manager.get_setting("exif_copyright"):
                self.parent.copyrightLineEdit.setText(copyright)
            
            # 使用lineEdit_EXIF_Position
            if position := config_manager.get_setting("exif_position"):
                self.parent.lineEdit_EXIF_Position.setText(position)
            
            if latitude := config_manager.get_setting("exif_latitude"):
                self.parent.lineEdit_EXIF_latitude.setText(latitude)
            
            if longitude := config_manager.get_setting("exif_longitude"):
                self.parent.lineEdit_EXIF_longitude.setText(longitude)
            
            if location_index := config_manager.get_setting("exif_location_index"):
                self.parent.locationComboBox.setCurrentIndex(int(location_index))
                self.on_combobox_location_changed(int(location_index))
            
            if camera_brand := config_manager.get_setting("exif_camera_brand"):
                index = self.parent.brandComboBox.findText(camera_brand)
                if index >= 0:
                    self.parent.brandComboBox.setCurrentIndex(index)
                    self._on_brand_changed(index)
            
            if camera_model := config_manager.get_setting("exif_camera_model"):
                index = self.parent.modelComboBox.findText(camera_model)
                if index >= 0:
                    self.parent.modelComboBox.setCurrentIndex(index)
            
            if shoot_time_index := config_manager.get_setting("exif_shoot_time_index"):
                self.parent.shootTimeSource.setCurrentIndex(int(shoot_time_index))
                self.on_combobox_time_changed(int(shoot_time_index))
            
            if star_rating := config_manager.get_setting("exif_star_rating"):
                self.set_selected_star(int(star_rating))
        except Exception as e:
            self.log("WARNING", f"加载EXIF设置时出错: {str(e)}")

    def save_exif_settings(self):
        try:
            # 直接使用控件
            config_manager.update_setting("exif_title", self.parent.titleLineEdit.text())
            
            config_manager.update_setting("exif_author", self.parent.authorLineEdit.text())
            
            config_manager.update_setting("exif_subject", self.parent.themeLineEdit.text())
            
            config_manager.update_setting("exif_copyright", self.parent.copyrightLineEdit.text())
            
            # 使用lineEdit_EXIF_Position
            config_manager.update_setting("exif_position", self.parent.lineEdit_EXIF_Position.text())
            
            config_manager.update_setting("exif_latitude", self.parent.lineEdit_EXIF_latitude.text())
            
            config_manager.update_setting("exif_longitude", self.parent.lineEdit_EXIF_longitude.text())
            
            config_manager.update_setting("exif_location_index", self.parent.locationComboBox.currentIndex())
            
            config_manager.update_setting("exif_camera_brand", self.parent.brandComboBox.currentText())
            
            config_manager.update_setting("exif_camera_model", self.parent.modelComboBox.currentText())
            
            config_manager.update_setting("exif_shoot_time_index", self.parent.shootTimeSource.currentIndex())
            
            config_manager.update_setting("exif_shoot_time", 
                                        self.parent.dateTimeEdit_shootTime.dateTime().toString("yyyy:MM:dd HH:mm:ss"))
            
            config_manager.update_setting("exif_star_rating", self.selected_star)
        except Exception as e:
            self.log("WARNING", f"保存EXIF设置时出错: {str(e)}")
    
    def refresh(self):
        """刷新页面状态"""
        try:
            self.brandComboBox.setCurrentIndex(0)
            self.modelComboBox.setCurrentIndex(0)
        except (AttributeError, TypeError):
            pass
        try:
            self.log("INFO", "正在刷新EXIF信息写入页面")
            
            # 重置状态
            self._reset_state()
            
            # 获取文件夹页面引用
            self.folder_page = self.parent.folder_page
            self.log("INFO", "已重新获取文件夹页面引用")
                
            # 刷新UI组件状态
            self._update_ui_components()
            
            self.log("INFO", "EXIF信息写入页面刷新完成")
        except Exception as e:
            self.log("ERROR", f"刷新EXIF信息写入页面时出错: {str(e)}")
    
    def _reset_state(self):
        """重置页面状态"""
        try:
            # 重置星级选择
            self.selected_star = 0
            
            # 停止正在运行的工作线程
            if self.worker:
                self.worker.stop()
                self.worker = None
                
            # 重置进度条
            self.parent.progressBar_EXIF.setValue(0)
                
            # 重置按钮状态
            self.is_running = False
            self.update_button_state()
                
        except Exception as e:
            self.log("ERROR", f"重置状态时出错: {str(e)}")
    
    def _update_ui_components(self):
        """更新UI组件状态"""
        try:
            # 重置星级按钮状态
            self.highlight_stars(0)
            
            # 刷新相机品牌和型号数据
            self.init_camera_brand_model()
            
            # 重新加载设置
            self.load_exif_settings()
                
        except Exception as e:
            self.log("ERROR", f"更新UI组件时出错: {str(e)}")