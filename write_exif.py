import json
import json
import re
from datetime import datetime

from PyQt6.QtCore import pyqtSignal, QObject
from PyQt6.QtWidgets import QMessageBox

from common import get_resource_path
from config_manager import config_manager
from write_exif_thread import WriteExifThread


class WriteExifManager(QObject):
    log_signal = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.folder_page = None
        self.worker = None
        self.is_running = False
        self.selected_star = 0
        self.error_messages = []
        self.log_signal.connect(self.handle_log_signal)
        self.init_ui()
        self._setup_connections()
        self._safe_log("INFO", "EXIF信息写入页面初始化完成")

    def init_ui(self):
        self._init_star_buttons()
        self.init_camera_brand_model()
        self.load_exif_settings()

    def _safe_log(self, level, message):
        try:
            self.log(level, message)
        except Exception as e:
            print(f"日志记录失败: {e}")

    def _get_parent_component(self, name):
        try:
            return getattr(self.parent, name, None)
        except Exception:
            return None

    def _init_star_buttons(self):
        self.star_buttons = []
        for i in range(1, 6):
            button = self._get_parent_component(f'star{i}Button')
            if button:
                button.clicked.connect(lambda checked, star=i: self.set_selected_star(star))
                self.star_buttons.append(button)
        self.highlight_stars(0)

    def highlight_stars(self, count):
        """高亮显示指定数量的星级按钮"""
        star_on = get_resource_path("assets/star_on.png")
        star_off = get_resource_path("assets/star_off.png")
        
        for i, button in enumerate(self.star_buttons, 1):
            if i <= count:
                button.setIcon(QPixmap(star_on))
            else:
                button.setIcon(QPixmap(star_off))

    def set_selected_star(self, star):
        """设置选中的星级"""
        self.selected_star = star
        self.highlight_stars(star)
        self._safe_log("INFO", f"已选择 {star} 星评分")

    def load_camera_lens_mapping(self):
        """加载相机镜头映射数据"""
        mapping_file = get_resource_path("assets/camera_lens_mapping.json")
        try:
            with open(mapping_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self._safe_log("ERROR", f"加载相机镜头映射文件失败: {e}")
            return {}

    def init_camera_brand_model(self):
        """初始化相机品牌和型号下拉框"""
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if not camera_brand_combo or not camera_model_combo:
            return
            
        camera_brand_combo.clear()
        camera_model_combo.clear()
        
        camera_data = self.load_camera_lens_mapping()
        
        # 添加默认选项
        camera_brand_combo.addItem("选择品牌")
        camera_model_combo.addItem("选择型号")
        
        # 填充品牌数据
        for brand in sorted(camera_data.keys()):
            camera_brand_combo.addItem(brand)

    def _on_brand_changed(self, index):
        """处理相机品牌变更事件"""
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if not camera_brand_combo or not camera_model_combo:
            return
            
        camera_model_combo.clear()
        camera_model_combo.addItem("选择型号")
        
        if index <= 0:
            return
            
        selected_brand = camera_brand_combo.currentText()
        camera_data = self.load_camera_lens_mapping()
        
        if selected_brand in camera_data:
            for model in sorted(camera_data[selected_brand].keys()):
                camera_model_combo.addItem(model)

    def _on_model_changed(self, index):
        """处理相机型号变更事件"""
        if index <= 0:
            return
            
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if not camera_brand_combo or not camera_model_combo:
            return
            
        selected_brand = camera_brand_combo.currentText()
        selected_model = camera_model_combo.currentText()
        
        self._safe_log("INFO", f"已选择相机: {selected_brand} {selected_model}")

    def get_lens_info_for_camera(self, brand, model):
        """根据相机品牌和型号获取镜头信息
        
        Args:
            brand: 相机品牌
            model: 相机型号
            
        Returns:
            镜头型号信息，如果未找到则返回空字符串
        """
        if not brand or not model:
            return ""
            
        camera_data = self.load_camera_lens_mapping()
        return camera_data.get(brand, {}).get(model, "")

    def parse_dms_coordinates(self, latitude_str, longitude_str):
        """解析度分秒格式的坐标
        
        Args:
            latitude_str: 纬度字符串
            longitude_str: 经度字符串
            
        Returns:
            转换后的十进制坐标元组 (纬度, 经度)，解析失败返回None
        """
        def parse_dms(dms_str):
            """解析度分秒字符串为十进制数值"""
            try:
                parts = re.split(r'[;\s,]+', dms_str.strip())
                if len(parts) == 3:
                    degrees = float(parts[0])
                    minutes = float(parts[1])
                    seconds = float(parts[2])
                    return degrees + minutes/60 + seconds/3600
            except (ValueError, IndexError):
                pass
            return None
        
        lat_decimal = parse_dms(latitude_str)
        lon_decimal = parse_dms(longitude_str)
        
        if lat_decimal is not None and lon_decimal is not None:
            return lat_decimal, lon_decimal
        return None



    def _setup_connections(self):
        """设置信号连接
        
        连接界面控件的事件信号到对应的处理函数。
        """
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if camera_brand_combo:
            camera_brand_combo.currentIndexChanged.connect(self._on_brand_changed)
        if camera_model_combo:
            camera_model_combo.currentIndexChanged.connect(self._on_model_changed)

    def on_combobox_time_changed(self, index):
        """处理拍摄时间来源变更事件
        
        Args:
            index: 选中的时间来源索引
        """
        date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
        if date_time_edit:
            date_time_edit.setEnabled(index == 0)

    def update_button_state(self):
        """更新按钮状态
        
        根据当前操作状态启用或禁用相关按钮。
        """
        start_button = self._get_parent_component('btnStartWriteEXIF')
        stop_button = self._get_parent_component('btnStopWriteEXIF')
        
        if start_button and stop_button:
            start_button.setEnabled(not self.is_running)
            stop_button.setEnabled(self.is_running)

    def connect_worker_signals(self):
        """连接工作线程信号
        
        连接EXIF写入线程的信号到对应的处理函数。
        """
        if self.worker:
            self.worker.progress_signal.connect(self.update_progress)
            self.worker.log_signal.connect(self.handle_log_signal)
            self.worker.finished.connect(self.on_finished)

    def start_exif_writing(self):
        """开始EXIF信息写入操作
        
        Returns:
            操作是否成功启动
        """
        if self.is_running:
            self._safe_log("WARNING", "EXIF写入操作正在进行中")
            return False
            
        if not self.folder_page:
            self._safe_log("ERROR", "文件夹页面未初始化")
            return False
            
        selected_files = self.folder_page.get_selected_files()
        if not selected_files:
            self._safe_log("ERROR", "请先选择要处理的文件")
            return False

        # 收集EXIF参数
        params = self._collect_exif_params()
        if not params:
            return False
            
        params['files'] = selected_files
        
        self.save_exif_settings()
        self._log_operation_summary(params)
        
        self.error_messages = []
        self.worker = WriteExifThread(**params)
        self.connect_worker_signals()
        self.worker.start()
        self.parent.progressBar_EXIF.setValue(0)
        self.is_running = True
        self.update_button_state()
        return True

    def _collect_exif_params(self):
        """收集EXIF参数
        
        Returns:
            EXIF参数字典，收集失败返回None
        """
        # 获取基本EXIF信息
        title_edit = self._get_parent_component('titleLineEdit')
        author_edit = self._get_parent_component('authorLineEdit')
        subject_edit = self._get_parent_component('themeLineEdit')
        copyright_edit = self._get_parent_component('copyrightLineEdit')
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        shoot_time_source = self._get_parent_component('shootTimeSource')
        date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
        
        params = {
            'title': title_edit.text() if title_edit else "",
            'author': author_edit.text() if author_edit else "",
            'subject': subject_edit.text() if subject_edit else "",
            'rating': str(self.selected_star),
            'copyright_text': copyright_edit.text() if copyright_edit else "",
            'position': None,
            'shoot_time': None,
            'camera_brand': camera_brand_combo.currentText() if camera_brand_combo else "",
            'camera_model': camera_model_combo.currentText() if camera_model_combo else "",
            'lens_model': self.get_lens_info_for_camera(
                camera_brand_combo.currentText() if camera_brand_combo else "",
                camera_model_combo.currentText() if camera_model_combo else ""
            )
        }
        
        # 处理拍摄时间
        if shoot_time_source and shoot_time_source.currentIndex() == 0 and date_time_edit:
            params['shoot_time'] = date_time_edit.dateTime().toString("yyyy:MM:dd HH:mm:ss")
        
        # 处理位置信息
        if not self._handle_location_info(params):
            return None
            
        return params

    def _handle_location_info(self, params):
        """处理位置信息
        
        Args:
            params: EXIF参数字典
            
        Returns:
            位置信息处理是否成功
        """
        longitude_edit = self._get_parent_component('lineEdit_EXIF_longitude')
        latitude_edit = self._get_parent_component('lineEdit_EXIF_latitude')
        
        if not longitude_edit or not latitude_edit:
            self.log("ERROR", "位置输入组件未找到")
            return False
            
        longitude = longitude_edit.text()
        latitude = latitude_edit.text()
        
        if not longitude or not latitude:
            self.log("ERROR", "请输入经纬度信息")
            return False
            
        # 尝试解析十进制坐标
        try:
            lon = float(longitude)
            lat = float(latitude)
            if -180 <= lon <= 180 and -90 <= lat <= 90:
                params['position'] = f"{lat},{lon}"
                return True
            else:
                self.log("ERROR", "经纬度范围无效")
                return False
        except ValueError:
            # 尝试解析度分秒坐标
            coords = self.parse_dms_coordinates(latitude, longitude)
            if coords:
                lat_decimal, lon_decimal = coords
                if -180 <= lon_decimal <= 180 and -90 <= lat_decimal <= 90:
                    params['position'] = f"{lat_decimal},{lon_decimal}"
                    self.log("INFO", f"成功解析度分秒坐标: 纬度={lat_decimal}, 经度={lon_decimal}")
                    return True
                else:
                    self.log("ERROR", "经纬度范围无效")
                    return False
            else:
                self.log("ERROR", "经纬度格式无效")
                return False

    def _log_operation_summary(self, params):
        """记录操作摘要
        
        Args:
            params: EXIF参数字典
        """
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
        """更新进度条
        
        Args:
            value: 进度值 (0-100)
        """
        progress_bar = self._get_parent_component('progressBar_EXIF')
        if progress_bar:
            progress_bar.setValue(value)

    def handle_log_signal(self, level, message):
        """处理日志信号
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        log_component = self._get_parent_component('txtWriteEXIFLog')
        
        if log_component:
            color_map = {'ERROR': '#FF0000', 'WARNING': '#FFA500', 'INFO': '#8677FD'}
            color = color_map.get(level, '#006400')
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            formatted_message = f"[{timestamp}] {message}"
            
            try:
                log_component.append(f'<span style="color:{color}">{formatted_message}</span>')
            except Exception as e:
                print(f"无法写入EXIF日志: {e}")
        else:
            print(f"[{level}] {message}")
            try:
                self.parent.log(level, message)
            except Exception as e:
                print(f"无法将日志传递给父组件: {e}")

    def log(self, level, message):
        """记录日志消息
        
        Args:
            level: 日志级别
            message: 日志消息
        """
        if level == 'ERROR':
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.error_messages.append(f"[{timestamp}] [{level}] {message}")
        
        log_message = f"[{level}] {message}"
        try:
            self.log_signal.emit(level, log_message)
        except Exception as e:
            print(f"无法发出日志信号: {e}")
            print(log_message)

    def on_finished(self):
        """处理EXIF写入完成事件"""
        self.is_running = False
        self.update_button_state()
        
        if self.error_messages:
            QMessageBox.information(
                self.parent, 
                "操作完成", 
                f"写入操作完成，但是有 {len(self.error_messages)} 个错误！"
            )
        else:
            QMessageBox.information(
                self.parent, 
                "操作完成", 
                "EXIF信息写入操作已完成！"
            )

    def load_exif_settings(self):
        """加载EXIF设置"""
        try:
            components = {
                'titleLineEdit': "exif_title",
                'authorLineEdit': "exif_author", 
                'themeLineEdit': "exif_subject",
                'copyrightLineEdit': "exif_copyright",
                'lineEdit_EXIF_latitude': "exif_latitude",
                'lineEdit_EXIF_longitude': "exif_longitude",
                'cameraBrand': "exif_camera_brand",
                'cameraModel': "exif_camera_model",
                'shootTimeSource': "exif_shoot_time_index"
            }
            
            for comp_name, setting_name in components.items():
                component = self._get_parent_component(comp_name)
                if component and (value := config_manager.get_setting(setting_name)):
                    if comp_name in ['cameraBrand', 'cameraModel']:
                        index = component.findText(value)
                        if index >= 0:
                            component.setCurrentIndex(index)
                            if comp_name == 'cameraBrand':
                                self._on_brand_changed(index)
                    elif comp_name == 'shootTimeSource':
                        component.setCurrentIndex(int(value))
                        self.on_combobox_time_changed(int(value))
                    else:
                        component.setText(value)
            
            if star_rating := config_manager.get_setting("exif_star_rating"):
                self.set_selected_star(int(star_rating))
        except Exception as e:
            self._safe_log("WARNING", f"加载EXIF设置时出错: {e}")

    def save_exif_settings(self):
        """保存EXIF设置"""
        try:
            components = {
                'titleLineEdit': "exif_title",
                'authorLineEdit': "exif_author",
                'themeLineEdit': "exif_subject", 
                'copyrightLineEdit': "exif_copyright",
                'lineEdit_EXIF_latitude': "exif_latitude",
                'lineEdit_EXIF_longitude': "exif_longitude",
                'cameraBrand': "exif_camera_brand",
                'cameraModel': "exif_camera_model",
                'shootTimeSource': "exif_shoot_time_index"
            }
            
            for comp_name, setting_name in components.items():
                component = self._get_parent_component(comp_name)
                if component:
                    if comp_name in ['cameraBrand', 'cameraModel']:
                        config_manager.update_setting(setting_name, component.currentText())
                    elif comp_name == 'shootTimeSource':
                        config_manager.update_setting(setting_name, component.currentIndex())
                    else:
                        config_manager.update_setting(setting_name, component.text())
            
            date_time_edit = self._get_parent_component('dateTimeEdit_shootTime')
            if date_time_edit:
                config_manager.update_setting("exif_shoot_time", 
                                            date_time_edit.dateTime().toString("yyyy:MM:dd HH:mm:ss"))
            
            config_manager.update_setting("exif_star_rating", self.selected_star)
        except Exception as e:
            self._safe_log("WARNING", f"保存EXIF设置时出错: {e}")
    
    def refresh(self):
        """刷新页面状态"""
        camera_brand_combo = self._get_parent_component('cameraBrand')
        camera_model_combo = self._get_parent_component('cameraModel')
        
        if camera_brand_combo:
            camera_brand_combo.setCurrentIndex(0)
        if camera_model_combo:
            camera_model_combo.setCurrentIndex(0)
            
        try:
            self._safe_log("INFO", "正在刷新EXIF信息写入页面")
            self._reset_state()
            self.folder_page = self.parent.folder_page
            self._safe_log("INFO", "已重新获取文件夹页面引用")
            self._update_ui_components()
            self._safe_log("INFO", "EXIF信息写入页面刷新完成")
        except Exception as e:
            self._safe_log("ERROR", f"刷新EXIF信息写入页面时出错: {e}")
    
    def _reset_state(self):
        """重置页面状态"""
        try:
            self.selected_star = 0
            
            if self.worker:
                self.worker.stop()
                self.worker = None
                
            progress_bar = self._get_parent_component('progressBar_EXIF')
            if progress_bar:
                progress_bar.setValue(0)
                
            self.is_running = False
            self.update_button_state()
        except Exception as e:
            self._safe_log("ERROR", f"重置状态时出错: {e}")
    
    def _update_ui_components(self):
        """更新UI组件状态"""
        try:
            self.highlight_stars(0)
            self.init_camera_brand_model()
            self.load_exif_settings()
        except Exception as e:
            self._safe_log("ERROR", f"更新UI组件时出错: {e}")

