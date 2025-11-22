import json
import os
from datetime import datetime

import requests

from PyQt6 import QtCore
from PyQt6.QtCore import pyqtSlot, QDateTime, pyqtSignal
from PyQt6.QtWidgets import QWidget, QMessageBox
from write_exif_thread import WriteExifThread
from common import get_resource_path
from config_manager import config_manager


class WriteExifPage(QWidget):
    log_signal = pyqtSignal(str, str)   
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.is_running = False
        self.worker = None
        self.folder_page = self.parent.folder_page if hasattr(parent, 'folder_page') else None
        
        # 初始化数据和组件
        self.selected_star = 0
        self.star_buttons = []
        self.camera_lens_mapping = {}
        self.error_messages = []
        self.camera_data = None
        
        # 缓存频繁使用的父组件引用
        self._cached_parent_components = {}
        
        # 初始化界面和连接信号
        self._safe_log("INFO", "属性写入页面初始化")
        self.init_ui()
    
    def _safe_log(self, level, message):
        """安全的日志记录方法，避免属性错误"""
        try:
            if hasattr(self.parent, 'log'):
                self.parent.log(level, message)
        except (AttributeError, TypeError):
            pass  # 静默失败，避免日志功能影响主程序
    
    def _get_parent_component(self, component_name):
        """获取父组件引用，使用缓存优化性能"""
        if component_name not in self._cached_parent_components:
            try:
                # 尝试直接获取组件，避免hasattr检查失败
                component = getattr(self.parent, component_name)
                self._cached_parent_components[component_name] = component
            except AttributeError:
                # 如果组件不存在，记录错误但不缓存None，下次重新尝试
                print(f"警告: 父组件 '{component_name}' 不存在")
                # 不缓存None值，下次重新尝试获取
                return None
        return self._cached_parent_components[component_name]
    
    def init_ui(self):
        """初始化用户界面"""
        # 初始化星级按钮
        self._init_star_buttons()
        
        # 加载相机数据
        self._load_camera_data()
        
        # 设置控件连接
        self.setup_connections()
        
        # 加载配置
        self.load_camera_lens_mapping()
        
        # 初始化相机品牌和型号
        self.init_camera_brand_model()
        
        # 更新按钮状态
        self.update_button_state()
        
        # 设置日期时间
        date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
        if date_time_edit:
            date_time_edit.setDateTime(QDateTime.currentDateTime())
        
        # 加载和保存设置
        self.load_exif_settings()
        self.save_exif_settings()
        
        # 记录欢迎信息
        self._safe_log('INFO', "欢迎使用图像属性写入，不写入项留空即可。文件一旦写入无法还原。")
        
        # 直接向txtWriteEXIFLog组件添加初始欢迎信息
        log_component = self._get_parent_component('txtWriteEXIFLog')
        if log_component:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            welcome_message = f"<span style='color:#8677FD'>[{timestamp}] INFO 欢迎使用图像属性写入功能！</span>"
            welcome_message += f"<br><span style='color:#8677FD'>[{timestamp}] INFO 请选择要写入EXIF信息的图片文件。</span>"
            welcome_message += f"<br><span style='color:#8677FD'>[{timestamp}] INFO 不写入的项留空即可，文件一旦写入无法还原。</span>"
            log_component.setHtml(welcome_message)

    def _init_star_buttons(self):
        """初始化星级评分按钮"""
        self.star_buttons = []
        # 定义按钮名称映射
        button_names = {
            1: 'btnStar1',
            2: 'btnStar2',
            3: 'btnStar3',
            4: 'btnStar4',
            5: 'btnStar5'
        }
        
        # 缓存资源路径
        star_icon_path = get_resource_path('resources/img/page_4/星级_暗.svg')
        
        for i in range(1, 6):
            btn_name = button_names.get(i)
            btn = self._get_parent_component(btn_name)
            if btn:
                btn.setStyleSheet(
                    "QPushButton { "
                    f"image: url({star_icon_path});\n"
                    "border: none; padding: 0; }" "\n"
                    "QPushButton:hover { background-color: transparent; }"
                )
                btn.enterEvent = lambda e, idx=i: self.highlight_stars(idx)
                btn.leaveEvent = lambda e: self.highlight_stars(self.selected_star)
                btn.clicked.connect(lambda _, idx=i: self.set_selected_star(idx))
                self.star_buttons.append(btn)
        
    def load_camera_lens_mapping(self):
        """加载相机镜头映射数据"""
        try:
            data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                    'resources', 'json', 'camera_lens_mapping.json')
            if os.path.exists(data_path):
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.camera_lens_mapping = json.load(f)
            else:
                self.parent.log('WARNING', "相机镜头映射文件不存在，将使用默认镜头信息")
        except Exception as e:
              self.parent.log('WARNING', f"加载相机镜头映射数据失败: {e}")
              self.camera_lens_mapping = {}

    def get_lens_info_for_camera(self, brand, model):
        """获取指定相机品牌和型号的镜头信息"""
        if brand in self.camera_lens_mapping:
            brand_data = self.camera_lens_mapping[brand]
            if model in brand_data:
                return brand_data[model]
        return None

    def _update_camera_brand_model(self):
        """更新相机品牌和型号下拉框"""
        """
        更新相机品牌和型号下拉框的默认状态。
        
        主要功能:
            - 设置日期时间编辑器为当前时间
            - 处理可能的属性访问异常
        
        异常处理:
            - AttributeError: 当组件不存在时
            - TypeError: 当组件类型不匹配时
        """
        try:
            self.parent.dateTimeEdit_shootTime.setDateTime(QtCore.QDateTime.currentDateTime())
        except (AttributeError, TypeError):
            pass
    
    def _on_model_changed(self, index):
        """当相机型号改变时的处理函数"""
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
                self.parent.log("error", f"型号改变事件处理错误: {e}")
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
            self.parent.log('WARNING', f'无法加载相机数据文件 {json_path}: {e}')
            return None
    
    def init_camera_brand_model(self):
        """初始化相机品牌和型号下拉框"""
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
        
        # 使用缓存的组件引用
        camera_brand_combo = self._get_parent_component('cameraBrand')
        if camera_brand_combo:
            try:
                # 填充相机品牌下拉框
                brands = ['不写入'] + list(camera_data.keys())
                camera_brand_combo.addItems(brands)
                camera_brand_combo.currentIndexChanged.connect(self._on_brand_changed)
            except Exception as e:
                self._safe_log("warning", f"初始化相机品牌下拉框失败: {e}")
        else:
            self._safe_log("warning", "未找到相机品牌下拉框")
            
        self.camera_data = camera_data
        
    def _on_brand_changed(self, index):
        """
        根据用户选择的相机品牌，更新相机型号下拉框的内容。
        
        参数:
            index (int): 当前选中的品牌下拉框索引，0 表示“不写入”
        
        逻辑:
            - 如果 index > 0（即选择了具体品牌），则读取该品牌对应的所有型号，
              并在型号下拉框中填充“不写入”及所有可用型号。
            - 如果 index == 0（即“不写入”），则清空型号下拉框。
        
        异常处理:
            - 若无法获取型号下拉框组件，记录警告日志。
            - 其他异常记录错误日志。
        """
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
                self.parent.log("error", f"品牌改变事件处理错误: {e}")
            except (AttributeError, TypeError):
                pass
        


    def setup_connections(self):
        """设置所有控件的信号连接"""
        # 连接日志信号
        try:
            self.log_signal.disconnect(self.handle_log_signal)
        except (TypeError, RuntimeError):
            pass  # 如果没有连接，忽略错误
        self.log_signal.connect(self.handle_log_signal)
        
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
        
        for actual_name, _ in text_fields_mapping.items():
            getattr(self.parent, actual_name).textChanged.connect(self.save_exif_settings)
                
        self.parent.cameraBrand.currentIndexChanged.connect(self.save_exif_settings)
        self.parent.cameraModel.currentIndexChanged.connect(self.save_exif_settings)
            
        # 星级按钮连接已经在init_ui中处理

    def on_combobox_location_changed(self, index):
        """当位置选择下拉框改变时的处理函数"""
        longitude_edit = self._get_parent_component('lineEdit_EXIF_longitude')
        latitude_edit = self._get_parent_component('lineEdit_EXIF_latitude')
        horizontal_frame = self._get_parent_component('horizontalFrame')
        
        if longitude_edit and latitude_edit and horizontal_frame:
            if index == 1:
                longitude_edit.show()
                latitude_edit.show()
                horizontal_frame.hide()
            else:
                longitude_edit.hide()
                latitude_edit.hide()
                horizontal_frame.show()

    def on_combobox_time_changed(self, index):
        """当拍摄时间来源下拉框改变时的处理函数"""
        shoot_time_source = self._get_parent_component('shootTimeSource')
        date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
        
        if shoot_time_source and date_time_edit:
            if shoot_time_source.currentIndex() == 2:
                date_time_edit.show()
            else:
                date_time_edit.hide()

    def update_button_state(self):
        """更新开始/停止按钮的文本状态"""
        # 使用缓存的组件引用
        start_button = self._get_parent_component('btnStartExif')
        if start_button:
            if self.is_running:
                start_button.setText("停止")
            else:
                start_button.setText("开始")

    def toggle_exif_writing(self):
        """切换EXIF写入状态"""
        if self.is_running:
            self.stop_exif_writing()
            self.is_running = False
        else:
            success = self.start_exif_writing()
            if success:
                self.is_running = True
        self.update_button_state()

    def connect_worker_signals(self):
        """连接工作线程的信号"""
        if self.worker:
            self.worker.progress_updated.connect(self.update_progress)
            self.worker.log_signal.connect(self.log)
            self.worker.finished_conversion.connect(self.on_finished)

    @pyqtSlot(int)
    def highlight_stars(self, count):
        """高亮显示星级评分"""
        for i, btn in enumerate(self.star_buttons, 1):
            icon = "星级_亮.svg" if i <= count else "星级_暗.svg"
            btn.setStyleSheet(f"QPushButton {{ image: url({get_resource_path(f'resources/img/page_4/{icon}')}); border: none; padding: 0; }}")

    @pyqtSlot(int)
    def set_selected_star(self, star):
        """设置选中的星级"""
        self.selected_star = star
        self.highlight_stars(star)

    def get_location(self, address):
        """通过地址获取位置坐标"""
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
            self.log("ERROR", f"获取位置失败: {e}")
        return None

    def get_location_by_ip(self):
        """通过IP地址获取位置信息"""
        try:
            response = requests.get('https://ipinfo.io', timeout=5)
            data = response.json()
            if 'loc' in data:
                lat, lon = data['loc'].split(',')
                # No position field in UI, skip setting location text
                return lat, lon
            self.log("ERROR", "无法解析位置信息\n\n"
                         "IP地址定位服务返回的数据格式异常")
            return None
        except Exception as e:
            self.log("ERROR", f"获取位置信息失败: {e}\n\n"
                         "请检查网络连接或稍后重试")
            return None

    def parse_dms_coordinates(self, lat_str, lon_str):
        """解析度分秒格式的坐标"""
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
            return None
                
        except Exception as e:
            self.log("ERROR", f"解析度分秒坐标失败: {e}")
            return None

    def update_position_by_ip(self):
        """通过IP地址更新位置信息"""
        location_info = self.get_location_by_ip()
        if location_info is not None:
            lat, lon = location_info
            # No position field in UI, skip setting location text
        # self.parent.lineEdit_EXIF_Position.setText(f"{lat}, {lon}")
            self.log("WARNING", f"当前纬度={lat}, 经度={lon}，位置已加载，可直接开始。")
        else:
            self.log("ERROR", "获取位置信息失败\n\n"
                         "可能的原因：\n"
                         "• 网络连接异常\n"
                         "• 定位服务暂时不可用\n"
                         "• 防火墙或代理设置阻止了网络请求")

    def start_exif_writing(self):
        """开始EXIF信息写入操作"""
        if not self.folder_page:
            self.log("ERROR", "文件夹页面未初始化\n\n"
                         "请重新启动应用程序或联系技术支持")
            return False
            
        # 使用config_manager获取有效文件夹列表，替代不存在的get_all_folders方法
        folders = config_manager.get_valid_folders()
        if not folders:
            self.log("WARNING", "请先导入一个有效的文件夹\n\n"
                           "点击\"导入文件夹\"按钮添加包含图片的文件夹")
            return False
        
        # 使用缓存的组件引用
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        title_edit = self._get_parent_component('titleLineEdit')
        author_edit = self._get_parent_component('authorLineEdit')
        subject_edit = self._get_parent_component('themeLineEdit')
        copyright_edit = self._get_parent_component('copyrightLineEdit')
        date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
        shoot_time_source = self._get_parent_component('shootTimeSource')
        
        # 优化条件判断：简化组件检查和值获取
        camera_brand = camera_brand_combo.currentText() if camera_brand_combo and camera_brand_combo.currentIndex() > 0 else None
        camera_model = camera_model_combo.currentText() if camera_model_combo and camera_model_combo.currentIndex() > 0 else None
        
        if camera_brand and not camera_model:
            camera_model = self.get_default_model_for_brand(camera_brand)
        
        # 直接获取文本框内容
        title = title_edit.text() if title_edit else ""
        author = author_edit.text() if author_edit else ""
        subject = subject_edit.text() if subject_edit else ""
        copyright_text = copyright_edit.text() if copyright_edit else ""
        
        # 处理拍摄时间
        shoot_time = None
        if shoot_time_source and date_time_edit:
            if shoot_time_source.currentIndex() == 2:
                shoot_time = date_time_edit.dateTime().toString("yyyy:MM:dd HH:mm:ss")
            else:
                shoot_time = shoot_time_source.currentIndex()
        
        params = {
            'folders_dict': folders,
            'title': title,
            'author': author,
            'subject': subject,
            'rating': str(self.selected_star),
            'copyright_text': copyright_text,
            'position': None,
            'shoot_time': shoot_time,
            'camera_brand': camera_brand,
            'camera_model': camera_model,
            'lens_model': self.get_lens_info_for_camera(camera_brand, camera_model)
        }
        
        # Location handling - default to manual coordinates
        location_type = 1  # Default to manual coordinates
        longitude_edit = self._get_parent_component('lineEdit_EXIF_longitude')
        latitude_edit = self._get_parent_component('lineEdit_EXIF_latitude')
        
        # 优化条件判断：简化位置处理逻辑
        if location_type == 1 and longitude_edit and latitude_edit:
            longitude = longitude_edit.text()
            latitude = latitude_edit.text()
            
            if not longitude or not latitude:
                self.log("ERROR", "请输入经纬度信息\n\n"
                         "请在对应的文本框中输入经度和纬度值")
                return False
                
            # 尝试解析十进制坐标
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
                # 尝试解析度分秒坐标
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
        elif location_type == 1:
            self.log("ERROR", "位置输入组件未找到\n\n"
                     "请检查UI组件是否正确初始化")
            return False
        
        self.save_exif_settings()
        
        operation_summary = "操作类型: EXIF信息写入"
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
        """停止EXIF写入操作"""
        if self.worker:
            self.worker.stop()
            self.worker.wait(1000)
            if self.worker.isRunning():
                self.worker.terminate()
            self._safe_log("WARNING", "正在停止EXIF写入操作...")
        self.is_running = False
        self.update_button_state()

    def update_progress(self, value):
        """更新进度条"""
        progress_bar = self._get_parent_component('progressBar_EXIF')
        if progress_bar:
            progress_bar.setValue(value)

    def handle_log_signal(self, level, message):
        # 缓存日志组件引用
        log_component = self._get_parent_component('txtWriteEXIFLog')
        
        # 确保即使没有日志组件，程序也不会崩溃
        if log_component:
            color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD'}
            color = color_map.get(level, '#000000')
            
            # 添加时间戳到日志消息
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            try:
                log_component.append(f'<span style="color:{color}">{formatted_message}</span>')
            except Exception as e:
                print(f"无法写入EXIF日志: {e}")
        else:
            # 如果没有日志组件，打印到控制台
            print(f"[{level}] {message}")
            # 同时尝试使用parent的log方法作为备选
            try:
                self.parent.log(level, message)
            except Exception:
                pass

    def log(self, level, message):
        """记录日志消息"""
        if level == 'ERROR':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.error_messages.append(f"[{timestamp}] [{level}] {message}")
        
        log_message = f"[{level}] {message}"
        try:
            self.log_signal.emit(level, log_message)
        except Exception:
            # 确保即使信号发射失败，程序也不会崩溃
            print(log_message)
            # 尝试使用parent的log方法作为备选
            try:
                self.parent.log(level, message)
            except Exception:
                pass

    def on_finished(self):
        """处理EXIF写入完成事件"""
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
        """加载EXIF设置"""
        try:
            # 使用缓存的组件引用
            title_edit = self._get_parent_component('titleLineEdit')
            author_edit = self._get_parent_component('authorLineEdit')
            subject_edit = self._get_parent_component('themeLineEdit')
            copyright_edit = self._get_parent_component('copyrightLineEdit')
            latitude_edit = self._get_parent_component('lineEdit_EXIF_latitude')
            longitude_edit = self._get_parent_component('lineEdit_EXIF_longitude')
            camera_brand_combo = self._get_parent_component('cameraBrand')
            camera_model_combo = self._get_parent_component('cameraModel')
            shoot_time_source = self._get_parent_component('shootTimeSource')
            
            # 优化条件判断：只有当组件存在且有设置值时才执行
            if title_edit and (title := config_manager.get_setting("exif_title")):
                title_edit.setText(title)
            
            if author_edit and (author := config_manager.get_setting("exif_author")):
                author_edit.setText(author)
            
            if subject_edit and (subject := config_manager.get_setting("exif_subject")):
                subject_edit.setText(subject)
            
            if copyright_edit and (copyright_text := config_manager.get_setting("exif_copyright")):
                copyright_edit.setText(copyright_text)
            
            # No position field in UI, skip loading position setting
            
            if latitude_edit and (latitude := config_manager.get_setting("exif_latitude")):
                latitude_edit.setText(latitude)
            
            if longitude_edit and (longitude := config_manager.get_setting("exif_longitude")):
                longitude_edit.setText(longitude)
            
            # locationComboBox not in UI, skip location_index loading
            
            if camera_brand_combo and (camera_brand := config_manager.get_setting("exif_camera_brand")):
                index = camera_brand_combo.findText(camera_brand)
                if index >= 0:
                    camera_brand_combo.setCurrentIndex(index)
                    self._on_brand_changed(index)
            
            if camera_model_combo and (camera_model := config_manager.get_setting("exif_camera_model")):
                index = camera_model_combo.findText(camera_model)
                if index >= 0:
                    camera_model_combo.setCurrentIndex(index)
            
            if shoot_time_source and (shoot_time_index := config_manager.get_setting("exif_shoot_time_index")):
                shoot_time_source.setCurrentIndex(int(shoot_time_index))
                self.on_combobox_time_changed(int(shoot_time_index))
            
            if star_rating := config_manager.get_setting("exif_star_rating"):
                self.set_selected_star(int(star_rating))
        except Exception as e:
            self._safe_log("WARNING", f"加载EXIF设置时出错: {e}")

    def save_exif_settings(self):
        """保存EXIF设置"""
        try:
            # 使用缓存的组件引用
            title_edit = self._get_parent_component('titleLineEdit')
            author_edit = self._get_parent_component('authorLineEdit')
            subject_edit = self._get_parent_component('themeLineEdit')
            copyright_edit = self._get_parent_component('copyrightLineEdit')
            latitude_edit = self._get_parent_component('lineEdit_EXIF_latitude')
            longitude_edit = self._get_parent_component('lineEdit_EXIF_longitude')
            camera_brand_combo = self._get_parent_component('cameraBrand')
            camera_model_combo = self._get_parent_component('cameraModel')
            shoot_time_source = self._get_parent_component('shootTimeSource')
            date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
            
            # 优化条件判断：只有当组件存在时才保存设置
            if title_edit:
                config_manager.update_setting("exif_title", title_edit.text())
            
            if author_edit:
                config_manager.update_setting("exif_author", author_edit.text())
            
            if subject_edit:
                config_manager.update_setting("exif_subject", subject_edit.text())
            
            if copyright_edit:
                config_manager.update_setting("exif_copyright", copyright_edit.text())
            
            # No position field in UI, skip saving position setting
            
            if latitude_edit:
                config_manager.update_setting("exif_latitude", latitude_edit.text())
            
            if longitude_edit:
                config_manager.update_setting("exif_longitude", longitude_edit.text())
            
            # locationComboBox not in UI, skip saving location_index
            
            if camera_brand_combo:
                config_manager.update_setting("exif_camera_brand", camera_brand_combo.currentText())
            
            if camera_model_combo:
                config_manager.update_setting("exif_camera_model", camera_model_combo.currentText())
            
            if shoot_time_source:
                config_manager.update_setting("exif_shoot_time_index", shoot_time_source.currentIndex())
            
            if date_time_edit:
                config_manager.update_setting("exif_shoot_time", 
                                            date_time_edit.dateTime().toString("yyyy:MM:dd HH:mm:ss"))
            
            config_manager.update_setting("exif_star_rating", self.selected_star)
        except Exception as e:
            self._safe_log("WARNING", f"保存EXIF设置时出错: {e}")
    
    def refresh(self):
        """刷新页面状态"""
        # 优化条件判断：直接设置组件状态，无需异常捕获
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if camera_brand_combo:
            camera_brand_combo.setCurrentIndex(0)
        if camera_model_combo:
            camera_model_combo.setCurrentIndex(0)
            
        try:
            self._safe_log("INFO", "正在刷新EXIF信息写入页面")
            
            # 重置状态
            self._reset_state()
            
            # 获取文件夹页面引用
            self.folder_page = self.parent.folder_page
            self._safe_log("INFO", "已重新获取文件夹页面引用")
                
            # 刷新UI组件状态
            self._update_ui_components()
            
            self._safe_log("INFO", "EXIF信息写入页面刷新完成")
        except Exception as e:
            self._safe_log("ERROR", f"刷新EXIF信息写入页面时出错: {e}")
    
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
            progress_bar = self._get_parent_component('progressBar_EXIF')
            if progress_bar:
                progress_bar.setValue(0)
                
            # 重置按钮状态
            self.is_running = False
            self.update_button_state()
                
        except Exception as e:
            self._safe_log("ERROR", f"重置状态时出错: {e}")
    
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
            self._safe_log("ERROR", f"更新UI组件时出错: {e}")
    