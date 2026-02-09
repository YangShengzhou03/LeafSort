import json
import os
import threading
import shutil
import io
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from PyQt6 import QtCore
from PIL import Image
import exifread
import pillow_heif
from common import get_resource_path, get_file_type
from config_manager import config_manager, logger

class SmartArrangeThread(QtCore.QThread):
    log_signal = QtCore.pyqtSignal(str, str)
    progress_signal = QtCore.pyqtSignal(int)

    def __init__(self, parent=None, folders: Optional[List[Dict[str, Any]]] = None, 
                 classification_structure: Optional[Dict[str, Any]] = None, 
                 file_name_structure: Optional[List[str]] = None,
                 destination_root: Optional[str] = None, separator: str = "-", 
                 time_derive: str = "文件创建时间", operation_type: int = 0):
        if folders is not None and not isinstance(folders, list):
            raise TypeError("folders参数必须是列表类型")
        
        super().__init__(parent)
        self._lock = threading.RLock()
        self.parent = parent
        self.folders = folders or []
        self.classification_structure = classification_structure or []
        self.file_name_structure = file_name_structure or []
        self.destination_root = destination_root
        self.separator = separator if separator else "-"
        self.time_derive = time_derive if time_derive else "文件创建时间"
        self.operation_type = operation_type
        self._stop_flag = False
        self.total_files = 0
        self.processed_files = 0
        self.success_count = 0
        self.fail_count = 0
        self.city_data = {'features': []}
        self.province_data = {'features': []}
        self.log_signal = parent.log_signal if parent and hasattr(parent, 'log_signal') else self.log_signal
        
        self.load_geographic_data()

    def calculate_total_files(self) -> int:
        try:
            with self._lock:
                self.total_files = 0
            
            if not self.folders:
                self.log("INFO", "没有指定要处理的文件夹")
                return 0
            
            for folder_info in self.folders:
                if self._stop_flag:
                    self.log("INFO", "文件计数操作被用户取消")
                    break
                
                try:
                    if not isinstance(folder_info, dict):
                        self.log("WARNING", "文件夹信息格式不正确，跳过")
                        continue
                    
                    if 'path' not in folder_info:
                        self.log("WARNING", "文件夹信息中缺少path字段")
                        continue
                    
                    folder_path = Path(folder_info['path'])
                    
                    if not folder_path.exists() or not folder_path.is_dir():
                        self.log("WARNING", f"路径不存在或不是目录: {folder_path}")
                        continue
                    
                    include_sub = bool(folder_info.get('include_sub', 0))
                    
                    if include_sub:
                        for root, _, files in os.walk(folder_path):
                            if self._stop_flag:
                                break
                            
                            with self._lock:
                                self.total_files += len(files)
                    else:
                        try:
                            items = list(folder_path.iterdir())
                            file_count = sum(1 for item in items if item.is_file())
                            
                            with self._lock:
                                self.total_files += file_count
                        except PermissionError:
                            self.log("ERROR", f"权限不足，无法读取文件夹: {folder_path}")
                        except Exception as e:
                            self.log("ERROR", f"读取文件夹内容时出错: {str(e)}")
                except KeyError as e:
                    self.log("ERROR", f"文件夹信息中缺少必要字段: {str(e)}")
                except Exception as e:
                    self.log("ERROR", f"处理文件夹时出错: {str(e)}")
            
            return self.total_files
        except Exception as e:
            self.log("ERROR", f"总文件计数过程中发生严重错误: {str(e)}")
            return 0

    def load_geographic_data(self):
        try:
            city_file_path = get_resource_path('_internal/resources/json/City_Reverse_Geocode.json')
            if os.path.exists(city_file_path):
                with open(city_file_path, 'r', encoding='utf-8') as f:
                    self.city_data = json.load(f)
            else:
                self.log("WARNING", f"城市地理数据文件不存在: {city_file_path}")
                
            province_file_path = get_resource_path('_internal/resources/json/Province_Reverse_Geocode.json')
            if os.path.exists(province_file_path):
                with open(province_file_path, 'r', encoding='utf-8') as f:
                    self.province_data = json.load(f)
            else:
                self.log("WARNING", f"省份地理数据文件不存在: {province_file_path}")
                
        except json.JSONDecodeError as e:
            self.log("ERROR", f"解析地理数据JSON失败: {str(e)}")
        except Exception as e:
            self.log("ERROR", f"加载地理数据时出错: {str(e)}")

    def run(self):
        try:
            self.load_geographic_data()
            self.calculate_total_files()
            
            self.processed_files = 0

            for folder_info in self.folders:
                if self._stop_flag:
                    break
                if self.destination_root:
                    destination_path = Path(self.destination_root).resolve()
                    folder_path = Path(folder_info['path']).resolve()
                    if len(destination_path.parts) > len(folder_path.parts) and destination_path.parts[:len(folder_path.parts)] == folder_path.parts:
                        self.log("ERROR", "目标文件夹不能是要整理的文件夹的子文件夹，这样会导致重复处理！")
                        break
                try:
                    if not self.classification_structure and not self.file_name_structure:
                        self.organize_without_classification(folder_info['path'])
                    else:
                        self.process_folder_with_classification(folder_info)
                except Exception as e:
                    self.log("ERROR", f"处理文件夹 {folder_info['path']} 时出错了: {str(e)}")
            
            if not self._stop_flag:
                if not self.destination_root:
                    try:
                        self.delete_empty_folders()
                    except Exception as e:
                        self.log("WARNING", f"删除空文件夹时出错了: {str(e)}")

                self.progress_signal.emit(100)
                
                self.log("DEBUG", "="*40)
                self.log("DEBUG", f"文件整理完成：成功处理 {self.success_count} 个文件，失败 {self.fail_count} 个文件")
                self.log("DEBUG", "="*3+"LeafSort © 2025 Yangshengzhou.All Rights Reserved"+"="*3)

            else:
                self.log("WARNING", "您已经取消了整理文件的操作")
                
        except Exception as e:
            self.log("ERROR", f"整理文件时遇到了严重问题: {str(e)}")

    def process_folder_with_classification(self, folder_info):
        folder_path = Path(folder_info['path'])
        
        if folder_info.get('include_sub', 0):
            for root, _, files in os.walk(folder_path):
                for file in files:
                    if self._stop_flag:
                        self.log("WARNING", "您已经取消了当前文件夹的处理")
                        return
                    full_file_path = Path(root) / file
                    if self.destination_root:
                        self.process_single_file(full_file_path)
                    else:
                        self.process_single_file(full_file_path, base_folder=folder_path)
                    self.processed_files += 1
                    if self.total_files > 0:
                        percent_complete = int((self.processed_files / self.total_files) * 100)
                        self.progress_signal.emit(min(percent_complete, 99))
        else:
            for file in os.listdir(folder_path):
                if self._stop_flag:
                    self.log("WARNING", "文件夹处理被用户中断")
                    return
                full_file_path = folder_path / file
                if full_file_path.is_file():
                    if self.destination_root:
                        self.process_single_file(full_file_path)
                    else:
                        self.process_single_file(full_file_path)
                    self.processed_files += 1
                    if self.total_files > 0:
                        percent_complete = int((self.processed_files / self.total_files) * 100)
                        self.progress_signal.emit(min(percent_complete, 99))


    def _truncate_filename(self, filename, max_length=50):
        if len(filename) <= max_length:
            return filename
        return filename[:max_length - 3] + "..."

    def organize_without_classification(self, folder_path):
        folder_path = Path(folder_path)
        
        for root, dirs, files in os.walk(folder_path):
            if self._stop_flag:
                self.log("WARNING", "文件提取操作被用户中断")
                break
            
            for file in files:
                if self._stop_flag:
                    self.log("WARNING", "您已经取消了文件提取操作")
                    break
                
                file_path = Path(root) / file
                
                if self.destination_root:
                    target_path = Path(self.destination_root) / file_path.name
                else:
                    target_path = folder_path / file_path.name
                
                if file_path != target_path:
                    try:
                        if self.destination_root:
                            shutil.copy2(file_path, target_path)
                        else:
                            shutil.move(file_path, target_path)
                        
                        self.success_count += 1
                        
                        self.processed_files += 1
                        if self.total_files > 0:
                            percent_complete = int((self.processed_files / self.total_files) * 100)
                            self.progress_signal.emit(min(percent_complete, 99))
                    except Exception as e:
                        filename = os.path.basename(file_path)
                        self.log("ERROR", f"处理文件时出错: {filename}, 错误: {str(e)}")
                        self.fail_count += 1

    def delete_empty_folders(self):
        deleted_count = 0
        processed_folders = set()
        
        source_folders = [Path(folder_info['path']).resolve() for folder_info in self.folders]
        
        for folder_info in self.folders:
            folder_path = Path(folder_info['path'])
            processed_folders.add(folder_path.resolve())
            
            if folder_info.get('include_sub', 0):
                for root, dirs, files in os.walk(folder_path):
                    processed_folders.add(Path(root).resolve())
        
        for folder in processed_folders:
            if self._stop_flag:
                self.log("WARNING", "您已经取消了空文件夹删除操作")
                break
            
            if folder.exists() and folder.is_dir():
                try:
                    deleted_in_this_folder = self._recursive_delete_empty_folders(folder, source_folders)
                    deleted_count += deleted_in_this_folder
                except Exception as e:
                    self.log("ERROR", f"删除文件夹 {folder} 时出错: {str(e)}")
        
        self.log("WARNING", f"已为您删除了 {deleted_count} 个空文件夹")
    
    def stop(self):
        self._stop_flag = True

    def _recursive_delete_empty_folders(self, folder_path, source_folders):
        deleted_count = 0
        
        if not folder_path.exists() or not folder_path.is_dir():
            return deleted_count
        
        if self._is_protected_folder(folder_path, source_folders):
            return deleted_count
            
        try:
            for item in folder_path.iterdir():
                if item.is_dir():
                    deleted_count += self._recursive_delete_empty_folders(item, source_folders)
            
            if not any(folder_path.iterdir()):
                if folder_path != folder_path.resolve().anchor:
                    try:
                        folder_path.rmdir()
                        deleted_count += 1
                    except Exception as e:
                        self.log("WARNING", f"无法删除文件夹 {folder_path}: {str(e)}")
                         
        except PermissionError:
            self.log("WARNING", f"权限不足，无法访问文件夹: {folder_path}")
        except Exception as e:
            self.log("ERROR", f"处理文件夹 {folder_path} 时出错: {str(e)}")
        
        return deleted_count
        
    def _is_protected_folder(self, folder_path, source_folders):
        if folder_path in source_folders:
            return True
            
        windows_system_dirs = []
        
        windir = os.environ.get('WINDIR', '')
        if windir:
            windows_system_dirs.append(Path(windir))
            
        systemroot = os.environ.get('SYSTEMROOT', '')
        if systemroot:
            windows_system_dirs.append(Path(systemroot))
            
        programfiles = os.environ.get('ProgramFiles', '')
        if programfiles:
            windows_system_dirs.append(Path(programfiles))
            
        programfiles_x86 = os.environ.get('ProgramFiles(x86)', '')
        if programfiles_x86:
            windows_system_dirs.append(Path(programfiles_x86))
            
        home_dir = Path.home()
        if home_dir:
            windows_system_dirs.append(home_dir)
            
        if Path('C:/').exists():
            windows_system_dirs.append(Path('C:/'))
            
        folder_path = folder_path.resolve()
        for system_dir in windows_system_dirs:
            if system_dir and folder_path.is_relative_to(system_dir):
                return True
            continue
                
        return False

    def log(self, level: str, message: str) -> None:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_message = f"[{current_time}] {level}: {message}"
        if hasattr(self, 'log_signal'):
            self.log_signal.emit(level, log_message)
    
    def get_exif_data(self, file_path):
        if self._stop_flag:
            return {}
        
        exif_data = {}
        file_path_obj = Path(file_path)
        
        suffix = str(file_path_obj.suffix).lower()
        create_time = datetime.fromtimestamp(file_path_obj.stat().st_ctime)
        modify_time = datetime.fromtimestamp(file_path_obj.stat().st_mtime)
        
        date_taken = None
        
        try:
            if suffix == '.heic':
                date_taken = self._process_heic_exif(file_path_obj, exif_data)
            elif suffix in ('.jpg', '.jpeg', '.tiff', '.tif'):
                date_taken = self._process_image_exif(file_path_obj, exif_data)
                if not date_taken:
                    self.log("ERROR", f"{file_path.name} - 无法从EXIF读取拍摄时间")
            elif suffix == '.png':
                date_taken = self._process_png_exif(file_path_obj)
            elif suffix == '.mov':
                date_taken = self._process_mov_exif(file_path_obj, exif_data)
            elif suffix == '.mp4':
                date_taken = self._process_mp4_exif(file_path_obj, exif_data)
            elif suffix in ('.arw', '.cr2', '.cr3', '.dng', '.nef', '.orf', '.raf', '.sr2', '.tif', '.tiff', '.rw2', '.pef', '.nrw'):
                date_taken = self._process_raw_exif(file_path_obj, exif_data)
            else:
                self.log("ERROR", f"不支持的文件类型或无EXIF数据: {suffix}")

            time_info = []
            if date_taken:
                time_info.append(f"拍摄时间: {date_taken}")
            time_info.append(f"创建时间: {create_time}")
            time_info.append(f"修改时间: {modify_time}")
            
            final_datetime = self._determine_best_datetime(date_taken, create_time, modify_time)
            exif_data['DateTime'] = final_datetime
                
        except Exception as e:
            exif_data['DateTime'] = create_time.strftime('%Y-%m-%d %H:%M:%S')
        return exif_data

    def _process_image_exif(self, file_path, exif_data):
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            date_taken = self.parse_exif_datetime(tags)
            
            self._extract_gps_and_camera_info(tags, exif_data)
              
            return date_taken
        except Exception as e:
            self.log("ERROR", f"{file_path.name} - 处理EXIF数据时出错: {str(e)}")
            return None

    def _process_raw_exif(self, file_path, exif_data):
        if self._stop_flag:
            return None
        
        if not os.path.exists(file_path):
            return None
        
        exiftool_path = os.path.join(os.path.dirname(__file__), "resources", "exiftool", "exiftool.exe")
        
        if not os.path.exists(exiftool_path):
            return None
        
        try:
            cmd = [exiftool_path, file_path]
            result = subprocess.run(cmd, capture_output=True, text=False, timeout=30, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            
            if result.returncode != 0:
                return None
            
            exif_data_str = result.stdout.decode('utf-8', errors='ignore')
            
            date_taken = self._parse_raw_datetime(exif_data_str)
            
            self._extract_raw_metadata(exif_data_str, exif_data)
            
            return date_taken
                
        except (subprocess.TimeoutExpired, Exception):
            return None
    
    def _parse_raw_datetime(self, exif_data_str):
        date_patterns = [
            'Date/Time Original',
            'Create Date', 
            'Modify Date',
            'DateTimeOriginal',
            'Creation Date',
            'DateTime',
            'Date Taken',
            'GPS Date/Time',
            'DateTimeCreated',
            'DateTimeDigitized',
            'Digital Creation Date',
            'Timestamp'
        ]
        
        found_dates = []
        
        for line in exif_data_str.split('\n'):
            for pattern in date_patterns:
                if pattern in line and ':' in line:
                    try:
                        date_str = line.split(':', 1)[1].strip()
                        date_taken = self.parse_datetime(date_str)
                        if date_taken:
                            if pattern in ['Date/Time Original', 'DateTimeOriginal']:
                                return date_taken
                            found_dates.append((date_taken, pattern))
                    except (ValueError, IndexError):
                        continue
        
        if found_dates:
            for date, pattern in found_dates:
                if 'Create' in pattern:
                    return date
            return found_dates[0][0]
        
        return None
    
    def _extract_raw_metadata(self, exif_data_str, exif_data):
    
        for line in exif_data_str.split('\n'):
            if 'Make' in line and ':' in line and not 'Lens Make' in line and not 'GPS Make' in line:
                try:
                    make_value = line.split(':', 1)[1].strip()
                    exif_data['Make'] = make_value
                except (ValueError, IndexError):
                    pass
            elif 'Camera Model' in line and ':' in line or 'Model' in line and ':' in line and not 'Lens Model' in line and not 'GPS Model' in line:
                try:
                    model_value = line.split(':', 1)[1].strip()
                    exif_data['Model'] = model_value
                except (ValueError, IndexError):
                    pass
            elif 'Lens Model' in line and ':' in line:
                try:
                    lens_model = line.split(':', 1)[1].strip()
                    exif_data['LensModel'] = lens_model
                except (ValueError, IndexError):
                    pass
        
        gps_lat = None
        gps_lon = None
        for line in exif_data_str.split('\n'):
            if 'GPS Latitude' in line and ':' in line:
                try:
                    lat_str = line.split(':', 1)[1].strip()
                    gps_lat = self._parse_dms_coordinate(lat_str)
                except (ValueError, IndexError):
                    pass
            elif 'GPS Longitude' in line and ':' in line:
                try:
                    lon_str = line.split(':', 1)[1].strip()
                    gps_lon = self._parse_dms_coordinate(lon_str)
                except (ValueError, IndexError):
                    pass
        
        if gps_lat and gps_lon:
            exif_data['GPS GPSLatitude'] = gps_lat
            exif_data['GPS GPSLongitude'] = gps_lon

    def _process_heic_exif(self, file_path, exif_data):
        try:
            heif_file = pillow_heif.read_heif(file_path)
            exif_raw = heif_file.info.get('exif', b'')
            if exif_raw.startswith(b'Exif\x00\x00'):
                exif_raw = exif_raw[6:]
            if exif_raw:
                tags = exifread.process_file(io.BytesIO(exif_raw), details=False)
                date_taken = self.parse_exif_datetime(tags)
                self._extract_gps_and_camera_info(tags, exif_data)
                return date_taken
            else:
    
                return None
        except Exception as e:
            
            if "No 'ftyp' box" in str(e):
                self.log("ERROR", f"{file_path.name}文件扩展名异常，可能不是真正的HEIC文件")
            else:
                self.log("DEBUG", f"处理HEIC文件EXIF时出错: {str(e)}")
            return None

    def _process_png_exif(self, file_path):
        with Image.open(file_path) as img:
            creation_time = img.info.get('Creation Time')
            if creation_time:
                return self.parse_datetime(creation_time)
        return None

    def _process_mp4_exif(self, file_path, exif_data):
        video_metadata = self._get_video_metadata(file_path)
        
        if not video_metadata:
            return None
            
        date_taken = None
        date_keys = [
            'DateTimeOriginal', 'Date/Time Original', 'Date Time Original',
            'CreateDate', 'Create Date', 'Creation Date', 
            'TrackCreateDate', 'Track Create Date', 'MediaCreateDate', 'Media Create Date',
            'ModifyDate', 'Modify Date',
            'FileModifyDate', 'FileModify Date', 'File Modify Date', 'Creation Date (Windows)'
        ]
        
        selected_time_field = None
        for key in date_keys:
            if key in video_metadata:
                date_str = video_metadata[key]
                
                if date_str == '0000:00:00 00:00:00' or not date_str or date_str.strip() == '':
                    continue
                
                try:
                    if '+' in date_str or '-' in str(date_str)[-5:]:
                        date_taken = self.parse_datetime(date_str)
                        if date_taken:
                            selected_time_field = key
                            break
                    else:
                        try:
                            dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            if 'Create' in key or 'Media' in key:
                                date_taken = dt + timedelta(hours=8)
                            else:
                                date_taken = dt
                            selected_time_field = key
                            break
                        except ValueError:
                            date_taken = self.parse_datetime(date_str)
                            if date_taken:
                                selected_time_field = key
                                break
                except Exception:
                    continue
        
        make_keys = [
            'Make', 'Camera Make', 'Manufacturer', 'Camera Manufacturer',
            'AndroidMake',
            'CompressorVersion', 'CanonFirmwareVersion', 'CameraType'
        ]
        
        for key in make_keys:
            if key in video_metadata:
                make_value = video_metadata[key]
                if make_value:
                    if isinstance(make_value, str):
                        make_value = make_value.strip().strip('"\'')
                        if key == 'CompressorVersion' and 'Canon' in make_value:
                            make_value = 'Canon'
                        elif key == 'CanonFirmwareVersion':
                            make_value = 'Canon'
                        elif key == 'CameraType' and 'Canon' in make_value:
                            make_value = 'Canon'
                    exif_data['Make'] = make_value
                break
        
        if 'Make' not in exif_data:
            app_info = self._detect_app_from_metadata(video_metadata)
            if app_info:
                exif_data['Make'] = app_info
        
        model_keys = [
            'Model', 'Camera Model', 'Device Model', 'Product Name',
            'AndroidModel',
            'CanonImageType', 'CanonModelID', 'LensType'
        ]
        
        for key in model_keys:
            if key in video_metadata:
                model_value = video_metadata[key]
                if model_value:
                    if isinstance(model_value, str):
                        model_value = model_value.strip().strip('"\'')
                        if key == 'CanonImageType':
                            if ':' in model_value:
                                model_value = model_value.split(':')[1].strip()
                        elif key == 'CanonModelID':
                            model_mapping = {
                                '1042': 'Canon EOS M50',
                            }
                            model_value = model_mapping.get(model_value, f'Canon Camera {model_value}')
                        elif key == 'LensType':
                            if model_value != '0':
                                model_value = f'Canon Lens {model_value}'
                    exif_data['Model'] = model_value
                break
        
        if 'Model' not in exif_data:
            device_info = self._detect_device_from_metadata(video_metadata)
            if device_info:
                exif_data['Model'] = device_info
        
        gps_found = False
        
        for key, value in video_metadata.items():
            if 'gps' in key.lower() or 'location' in key.lower():
                gps_found = True
                
                if 'Coordinates' in key or 'Position' in key:
                    lat, lon = self._parse_combined_coordinates(value)
                    if lat is not None and lon is not None:
                        exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
                elif 'Latitude' in key:
                    lat = self._parse_dms_coordinate(value)
                    if lat is not None:
                        exif_data['GPS GPSLatitude'] = lat
                elif 'Longitude' in key:
                    lon = self._parse_dms_coordinate(value)
                    if lon is not None:
                        exif_data['GPS GPSLongitude'] = lon
        
        return date_taken

    def _process_mov_exif(self, file_path, exif_data):
        video_metadata = self._get_video_metadata(file_path)
        if not video_metadata:
            self.log("ERROR", f"MOV文件 {file_path.name} 无法获取元数据")
            return None
            
        date_taken = None
        
        date_keys = [
            'Create Date', 'Creation Date', 'DateTime Original',
            'Media Create Date', 'Track Create Date', 
            'Date/Time Original', 'Date Time Original',
            'Creation Time', 'Created', 'Creation Date (Windows)',
            'Modify Date', 'Last Modified Date'
        ]
        
        for key in date_keys:
            if key in video_metadata:
                date_str = video_metadata[key].strip().strip('"\'')
                
                if date_str:
                    if '+' in date_str or '-' in date_str[-5:]:
                        date_taken = self.parse_datetime(date_str)
                    else:
                        try:
                            dt = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
                            date_taken = dt.replace(tzinfo=None)
                        except ValueError:
                            try:
                                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                                date_taken = dt
                            except ValueError:
                                try:
                                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                                    date_taken = dt
                                except ValueError:
                                    date_taken = self.parse_datetime(date_str)
                
                if date_taken:
                    break
        
        make_keys = [
            'Make', 'Camera Make', 'Manufacturer', 'Camera Manufacturer',
            'Producer', 'Software', 'Application'
        ]
        
        for key in make_keys:
            if key in video_metadata:
                make_value = video_metadata[key].strip().strip('"\'')
                if make_value and make_value.lower() not in ['', 'none', 'null', 'unknown']:
                    exif_data['Make'] = make_value
                    break
        
        model_keys = [
            'Model', 'Camera Model', 'Device Model', 'Product Name',
            'Model Name', 'Camera Model Name', 'Product Model'
        ]
        
        for key in model_keys:
            if key in video_metadata:
                model_value = video_metadata[key].strip().strip('"\'')
                if model_value and model_value.lower() not in ['', 'none', 'null', 'unknown']:
                    exif_data['Model'] = model_value
                    break
        
        gps_found = False
        for key, value in video_metadata.items():
            if 'gps' in key.lower() or 'location' in key.lower() or 'position' in key.lower():
                gps_found = True
                
                if 'Coordinates' in key or 'Position' in key:
                    lat, lon = self._parse_combined_coordinates(value)
                    if lat is not None and lon is not None:
                        exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
                elif 'Latitude' in key:
                    lat = self._parse_dms_coordinate(value)
                    if lat is not None:
                        exif_data['GPS GPSLatitude'] = lat
                elif 'Longitude' in key:
                    lon = self._parse_dms_coordinate(value)
                    if lon is not None:
                        exif_data['GPS GPSLongitude'] = lon
            
        return date_taken

    def _determine_best_datetime(self, date_taken, create_time, modify_time):
        if self.time_derive == "拍摄日期":
            if date_taken:
                return date_taken.strftime('%Y-%m-%d %H:%M:%S')
                
        elif self.time_derive == "创建时间":
            if create_time:
                return create_time.strftime('%Y-%m-%d %H:%M:%S')
                
        elif self.time_derive == "修改时间":
            if modify_time:
                return modify_time.strftime('%Y-%m-%d %H:%M:%S')
                
        if self.time_derive == "最早时间" or self.time_derive not in ["拍摄日期", "创建时间", "修改时间"]:
            times = [t for t in [date_taken, create_time, modify_time] if t is not None]
            if times:
                selected_time = min(times)
                return selected_time.strftime('%Y-%m-%d %H:%M:%S')
            
        available_times = [t for t in [date_taken, create_time, modify_time] if t is not None]
        if available_times:
            fallback_time = available_times[0]
            return fallback_time.strftime('%Y-%m-%d %H:%M:%S')
            
        try:
            return modify_time.strftime('%Y-%m-%d %H:%M:%S') if modify_time else ""
        except:
            return ""

    def _extract_gps_and_camera_info(self, tags, exif_data):
        lat_ref = str(tags.get('GPS GPSLatitudeRef', '')).strip()
        lon_ref = str(tags.get('GPS GPSLongitudeRef', '')).strip()
        
        gps_lat = tags.get('GPS GPSLatitude')
        gps_lon = tags.get('GPS GPSLongitude')
        
        if gps_lat and gps_lon:
            if isinstance(gps_lat, (int, float)) and isinstance(gps_lon, (int, float)):
                lat = gps_lat
                lon = gps_lon
            elif hasattr(gps_lat, 'values') and hasattr(gps_lon, 'values'):
                lat = self.convert_to_degrees(gps_lat)
                lon = self.convert_to_degrees(gps_lon)
            else:
                try:
                    lat = float(gps_lat)
                    lon = float(gps_lon)
                except (ValueError, TypeError):
                    lat = None
                    lon = None
            
            if lat is not None and lon is not None:
                if lat_ref and lat_ref.lower() == 's':
                    lat = -abs(lat)
                elif lat_ref and lat_ref.lower() == 'n':
                    lat = abs(lat)
                    
                if lon_ref and lon_ref.lower() == 'w':
                    lon = -abs(lon)
                elif lon_ref and lon_ref.lower() == 'e':
                    lon = abs(lon)
                
                exif_data.update({'GPS GPSLatitude': lat, 'GPS GPSLongitude': lon})
        
        make = str(tags.get('Image Make', '')).strip()
        model = str(tags.get('Image Model', '')).strip()
        
        if isinstance(make, str):
            make = make.strip().strip('"\'')
        if isinstance(model, str):
            model = model.strip().strip('"\'')
        
        exif_data.update({
            'Make': make or None,
            'Model': model or None
        })

    def _get_video_metadata(self, file_path, timeout=30):
        if self._stop_flag:
            return None
        
        try:
            if not os.path.exists(file_path):
                return None
                
            exiftool_path = get_resource_path('_internal/resources/exiftool/exiftool.exe')
            if not exiftool_path:
                exiftool_path = os.path.join(os.path.dirname(__file__), 'resources', 'exiftool', 'exiftool.exe')
            
            if not exiftool_path or not os.path.exists(exiftool_path):
                return None
                
            file_path_normalized = str(file_path).replace('\\', '/')
            
            metadata = {}
            cmd = [exiftool_path, "-s", "-n", file_path_normalized]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=timeout,
                shell=False,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            if result.returncode != 0:
                cmd = [exiftool_path, file_path_normalized]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=timeout,
                    shell=False,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                if result.returncode != 0:
                    return None

            if not result.stdout:
                return None

            try:
                stdout_text = result.stdout.decode('utf-8', errors='ignore')
            except Exception as e:
                return None
            
            lines_processed = 0
            for line in stdout_text.split('\n'):
                line = line.strip()
                if not line or line.startswith('=') or 'ExifTool' in line:
                    continue
                    
                if ':' in line:
                    colon_index = line.find(':')
                    key = line[:colon_index].strip()
                    value = line[colon_index+1:].strip()
                    
                    if not key or not value or value.lower() in ['', 'none', 'null']:
                        continue
                    
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    
                    metadata[key] = value
                    lines_processed += 1
                    
                    if lines_processed > 100:
                        break
            
            if not metadata and stdout_text.strip():
                for line in stdout_text.split('\n'):
                    line = line.strip()
                    if ':' in line and not line.startswith('='):
                        parts = line.split(':', 1)
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            if key and value:
                                if value.startswith('"') and value.endswith('"'):
                                    value = value[1:-1]
                                metadata[key] = value
            
            return metadata if metadata else None

        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            pass
        return None

    def _detect_app_from_metadata(self, metadata):
        app_fields = [
            'Encoder', 'Software', 'Tool', 'Application',
            'Producer', 'CreationTool', 'Generator'
        ]
        
        for field in app_fields:
            if field in metadata:
                value = metadata[field]
                if value:

                    if 'bytevehwavc' in value.lower():
                        return 'ByteDance'
                    elif 'douyin' in value.lower() or 'tiktok' in value.lower():
                        return 'ByteDance'
                    elif 'instagram' in value.lower():
                        return 'Instagram'
                    elif 'wechat' in value.lower() or 'weixin' in value.lower():
                        return 'WeChat'
                    elif 'snapchat' in value.lower():
                        return 'Snapchat'
                    elif 'videoeditor' in value.lower():
                        return 'VideoEditor'
                    else:
                        return value.strip().strip('"\'')
        
                if 'LvMetaInfo' in metadata:
                    try:
                        import json
                        info_str = metadata['LvMetaInfo']
                        if isinstance(info_str, str) and info_str.startswith('{"'):
                            info_data = json.loads(info_str)
                            if 'source_type' in info_data:
                                source_type = info_data['source_type']
                                if 'douyin' in source_type:
                                    return 'ByteDance'
                    except:
                        pass
        
        return None

    def _detect_device_from_metadata(self, metadata):
        device_fields = [
            'Model', 'Device Model', 'Product Name', 'Product',
            'Hardware', 'Platform', 'System'
        ]
        
        for field in device_fields:
            if field in metadata:
                value = metadata[field]
                if value and value not in ['', 'unknown', 'none']:
                    return value.strip().strip('"\'')
        

        if 'LvMetaInfo' in metadata:
            try:
                import json
                info_str = metadata['LvMetaInfo']
                if isinstance(info_str, str) and info_str.startswith('{"'):
                    info_data = json.loads(info_str)
                    if 'data' in info_data:
                        data = info_data['data']
                        if 'os' in data:
                            os_info = data['os']
                            if os_info == 'android':
                                return 'Android Device'
                            elif os_info == 'ios':
                                return 'iOS Device'
                            else:
                                return f"{os_info.title()} Device"
            except:
                pass
        
        return None

    def parse_exif_datetime(self, tags):
        try:
            time_tags_priority = [
                'EXIF DateTimeOriginal',
                'Image DateTime',
                'EXIF DateTimeDigitized',
                'EXIF DateTime',
                'DateTimeOriginal',
                'DateTimeDigitized',
                'DateTime',
                'GPS GPSDate',
                'GPS GPSTimeStamp',
                'GPS GPSDateTime'
            ]
            
            for tag_name in time_tags_priority:
                if tag_name in tags:
                    datetime_str = str(tags[tag_name])
                    if datetime_str and datetime_str != 'None':
                        parsed_dt = self.parse_datetime(datetime_str)
                        if parsed_dt:
                            return parsed_dt
            
            case_insensitive_tags = {str(tag).lower(): str(tag) for tag in tags}
            important_time_keywords = ['datetimeoriginal', 'datetime', 'date', 'time']
            
            for lower_tag, original_tag in case_insensitive_tags.items():
                if any(keyword in lower_tag for keyword in important_time_keywords):
                    if original_tag not in time_tags_priority:
                        datetime_str = str(tags[original_tag])
                        if datetime_str and datetime_str != 'None':
                            parsed_dt = self.parse_datetime(datetime_str)
                            if parsed_dt:
                                return parsed_dt
            
            for tag in tags:
                tag_name = str(tag)
                if tag_name not in time_tags_priority:
                    datetime_str = str(tags[tag])
                    if datetime_str and datetime_str != 'None':
                        if any(char.isdigit() for char in datetime_str) and ('/' in datetime_str or '-' in datetime_str or ':' in datetime_str):
                            parsed_dt = self.parse_datetime(datetime_str)
                            if parsed_dt:
                                return parsed_dt
            
        except Exception as e:
            self.log("ERROR", f"解析EXIF时间时出错: {str(e)}")
            
        return None

    def parse_datetime(self, datetime_str):
        if not datetime_str:
            return None
            
        datetime_str = str(datetime_str).strip()
        
        if datetime_str and (datetime_str.startswith('0x') or datetime_str.startswith('b"') or datetime_str.startswith('b\'')):
            try:
                if datetime_str.startswith('0x'):
                    datetime_str = bytes.fromhex(datetime_str[2:]).decode('utf-8', errors='ignore').strip()
                elif datetime_str.startswith('b"') or datetime_str.startswith('b\''):
                    datetime_str = datetime_str[2:-1].strip()
            except Exception as e:
                return None
        
        formats_with_timezone = [
            '%Y:%m:%d %H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S%z',
            '%Y/%m/%d %H:%M:%S%z',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y/%m/%dT%H:%M:%S%z',
            '%Y-%m-%d %H:%M:%S.%f%z',
            '%Y:%m:%d %H:%M:%S.%f%z',
            '%Y-%m-%dT%H:%M:%S.%f%z',
        ]
        

        formats_without_timezone = [
            '%Y:%m:%d %H:%M:%S',
            '%Y:%m:%d',
            '%Y-%m-%d %H:%M:%S', 
            '%Y/%m/%d %H:%M:%S',
            '%Y%m%d%H%M%S',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y/%m/%dT%H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%Y.%m.%d %H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%Y:%m:%d %H:%M',
            '%m/%d/%Y %H:%M',
            '%d/%m/%Y %H:%M',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y:%m:%d %H:%M:%S.%f',
            '%Y-%m-%dT%H:%M:%S.%f',
        ]
        
        for fmt in formats_with_timezone:
            try:
                dt = datetime.strptime(datetime_str, fmt)
                if dt.tzinfo is not None:
                    dt = dt.astimezone()
                    result = dt.replace(tzinfo=None)
                    return result
                result = dt
                return result
            except ValueError:
                continue
        
        for fmt in formats_without_timezone:
            try:
                dt = datetime.strptime(datetime_str, fmt)
                return dt
            except ValueError:
                continue
        
        try:
            cleaned_str = ''.join(c for c in datetime_str if c.isdigit() or c in ':-/.T ')
            if cleaned_str != datetime_str:
                for fmt in formats_without_timezone + formats_with_timezone:
                    try:
                        dt = datetime.strptime(cleaned_str, fmt)
                        return dt
                    except ValueError:
                        continue
        except Exception as e:
            pass
        
        return None

    def parse_gps_coordinates(self, gps_info):
        if not gps_info:
            return None, None
            
        for key in ['GPS Coordinates', 'GPS Position']:
            if key in gps_info:
                coords_str = gps_info[key]
                lat, lon = self._parse_combined_coordinates(coords_str)
                if lat is not None and lon is not None:
                    return lat, lon
        
        lat = self._parse_dms_coordinate(gps_info.get('GPS Latitude', ''))
        lon = self._parse_dms_coordinate(gps_info.get('GPS Longitude', ''))
        
        return lat, lon
    
    def _parse_combined_coordinates(self, coords_str):
        try:

            if ',' in coords_str:
                parts = coords_str.split(',')
                if len(parts) == 2:
                    lat_str = parts[0].strip()
                    lon_str = parts[1].strip()
                    
                    lat = self._parse_dms_coordinate(lat_str)
                    lon = self._parse_dms_coordinate(lon_str)
                    
                    return lat, lon
            

            elif ' ' in coords_str:
                parts = coords_str.split()
                if len(parts) == 2:
                    lat_str = parts[0].strip()
                    lon_str = parts[1].strip()
                    
                    lat = self._parse_dms_coordinate(lat_str)
                    lon = self._parse_dms_coordinate(lon_str)
                    
                    return lat, lon
        except Exception:
            pass
            
        return None, None
    
    def _parse_dms_coordinate(self, coord_str):
        if not coord_str:
            return None
            
        try:
            coord_str = str(coord_str).strip()
            
            direction = None
            for dir_char in ['N', 'S', 'E', 'W']:
                if dir_char in coord_str:
                    direction = dir_char
                    break
            
            clean_str = coord_str
            for char in ['N', 'S', 'E', 'W', 'deg', '°', "'", '"']:
                clean_str = clean_str.replace(char, '')
            
            clean_str = clean_str.strip()
            

            try:
                decimal = float(clean_str)
                if direction in ['S', 'W']:
                    decimal = -decimal
                return decimal
            except ValueError:
                pass
            

            parts = [p for p in clean_str.split() if p.strip()]
            degrees = minutes = seconds = 0.0
            
            if len(parts) >= 1:
                degrees = float(parts[0])
            if len(parts) >= 2:
                minutes = float(parts[1])
            if len(parts) >= 3:
                seconds = float(parts[2])
            
            decimal = degrees + minutes / 60.0 + seconds / 3600.0
            
            if direction in ['S', 'W']:
                decimal = -decimal
                
            return decimal
            
        except Exception as e:
            return None

    def get_city_and_province(self, lat, lon):
        if not hasattr(self, 'province_data') or not hasattr(self, 'city_data'):
            return "未知省份", "未知城市"

        def is_point_in_polygon(x, y, polygon):
            if not isinstance(polygon, (list, tuple)) or len(polygon) < 3:
                return False
            
            n = len(polygon)
            inside = False
            
            p1x, p1y = polygon[0]
            for i in range(n + 1):
                p2x, p2y = polygon[i % n]
                if y > min(p1y, p2y):
                    if y <= max(p1y, p2y):
                        if x <= max(p1x, p2x):
                            if p1y != p2y:
                                xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                            if p1x == p2x or x <= xinters:
                                inside = not inside
                p1x, p1y = p2x, p2y
            
            return inside

        def query_location(longitude, latitude, data):
            for i, feature in enumerate(data['features']):
                name, coordinates = feature['properties']['name'], feature['geometry']['coordinates']
                polygons = [polygon for multi_polygon in coordinates for polygon in
                            ([multi_polygon] if isinstance(multi_polygon[0][0], (float, int)) else multi_polygon)]
                
                for j, polygon in enumerate(polygons):
                    if is_point_in_polygon(longitude, latitude, polygon):
                        return name

            return None

        if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            lat_deg = lat
            lon_deg = lon
        else:
            lat_deg = self.convert_to_degrees(lat)
            lon_deg = self.convert_to_degrees(lon)
        
        if lat_deg and lon_deg:
            province = query_location(lon_deg, lat_deg, self.province_data)
            city = query_location(lon_deg, lat_deg, self.city_data)

            return (
                province if province else "未知省份",
                city if city else "未知城市"
            )
        else:
            return "未知省份", "未知城市"

    @staticmethod
    def convert_to_degrees(value):
        if not value:
            return None

        if isinstance(value, (int, float)):
            return float(value)

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass

        try:
            if hasattr(value, 'values') and len(value.values) >= 3:
                d = float(value.values[0].num) / float(value.values[0].den)
                m = float(value.values[1].num) / float(value.values[1].den)
                s = float(value.values[2].num) / float(value.values[2].den)
                result = d + (m / 60.0) + (s / 3600.0)
                return result
        except Exception:
            pass

        try:
            return float(value)
        except Exception:
            return None

    def build_new_file_name(self, file_path, file_time, original_name, exif_data=None):
        if not self.file_name_structure:
            return original_name
        
        if exif_data is None:
            exif_data = self.get_exif_data(file_path)
        
        parts = []
        for tag in self.file_name_structure:
            parts.append(self.get_file_name_part(tag, file_path, file_time, original_name, exif_data))
        
        file_name = self.separator.join(parts)
        
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            file_name = file_name.replace(char, '_')
            
        return file_name
        
    def process_single_file(self, file_path, base_folder=None):
        try:
            file_path_str = str(file_path)
            exif_data = self.get_exif_data(file_path)
            
            file_time = None
            if exif_data.get('DateTime'):
                try:
                    file_time = datetime.strptime(exif_data['DateTime'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    self.log("WARNING", f"无法解析文件时间: {file_path}")

            target_base = self.destination_root
            
            target_path = self.build_target_path(file_path, exif_data, file_time, target_base)
            
            original_name = file_path.stem
            new_file_name = self.build_new_file_name(file_path, file_time, original_name, exif_data)
            
            new_file_name_with_ext = f"{new_file_name}{file_path.suffix}"
            
            full_target_path = target_path / new_file_name_with_ext
            
            full_target_path.parent.mkdir(parents=True, exist_ok=True)
            
            base_name = full_target_path.stem
            ext = full_target_path.suffix
            counter = 1
            unique_path = full_target_path
            
            while unique_path.exists():
                unique_path = full_target_path.parent / f"{base_name}_{counter}{ext}"
                counter += 1
            
            try:
                old_name = os.path.basename(file_path)
                new_name = os.path.basename(unique_path)
                truncated_old_name = self._truncate_filename(old_name)
                truncated_new_name = self._truncate_filename(new_name)
                
                if self.operation_type == 0 or not self.destination_root:
                    shutil.copy2(file_path, unique_path)
                else:
                    shutil.move(file_path, unique_path)
                
                self.success_count += 1
                
            except Exception as e:
                filename = os.path.basename(file_path)
                self.log("ERROR", f"处理文件时出错: {filename}, 错误: {str(e)}")
                self.fail_count += 1
            
        except Exception as e:
            self.log("ERROR", f"处理文件 {file_path} 时出错: {str(e)}")
            self.fail_count += 1

    def get_file_name_part(self, tag, file_path, file_time, original_name, exif_data=None):
        if isinstance(tag, dict) and 'tag' in tag and 'content' in tag:
            tag_name = tag['tag']
            if tag_name == "自定义":
                return tag['content']  
            else:
                if tag['content'] is not None:
                    return tag['content']
                else:
                    tag = tag_name
        
        if exif_data is None:
            exif_data = self.get_exif_data(file_path)
        
        if tag == "原名":
            return original_name
        elif tag == "年份" and file_time:
            return str(file_time.year)
        elif tag == "月份" and file_time:
            return f"{file_time.month:02d}"
        elif tag == "日" and file_time:
            return f"{file_time.day:02d}"
        elif tag == "星期" and file_time:
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            return weekdays[file_time.weekday()]
        elif tag == "时间" and file_time:
            return file_time.strftime('%H%M%S')
        elif tag == "品牌":
            brand = exif_data.get('Make', '未知品牌')
            if isinstance(brand, str):
                brand = brand.strip().strip('"\'')
            return str(brand) if brand is not None else '未知品牌'
        elif tag == "型号":
            model = exif_data.get('Model', '未知型号')
            if isinstance(model, str):
                model = model.strip().strip('"\'')
            return str(model) if model is not None else '未知型号'
        elif tag == "位置":
            if exif_data.get('GPS GPSLatitude') and exif_data.get('GPS GPSLongitude'):
                lat = float(exif_data['GPS GPSLatitude'])
                lon = float(exif_data['GPS GPSLongitude'])
                
                province, city = self.get_city_and_province(lat, lon)
                local_location = f"{province}{city}" if city != "未知城市" else province
                
                return local_location
            return "未知位置"
        elif tag == "自定义":
            return "自定义"
        else:
            return ""

    def build_target_path(self, file_path, exif_data, file_time, target_base):
        if not self.classification_structure:
            if target_base:
                return Path(target_base)
            else:
                return file_path.parent / "整理结果"
        
        if target_base:
            target_path = Path(target_base)
        else:
            target_path = file_path.parent / "整理结果"
        
        original_path = target_path
        
        for level in self.classification_structure:
            folder_name = self.get_folder_name(level, exif_data, file_time, file_path)
            if folder_name:
                target_path = target_path / folder_name
        
        
        file_type = get_file_type(str(file_path))
        target_path = target_path / file_type
        
        return target_path

    def get_folder_name(self, level, exif_data, file_time, file_path):
        if level == "不分类":
            return None
        elif level == "年份" and file_time:
            return str(file_time.year)
        elif level == "月份" and file_time:
            return f"{file_time.month:02d}"
        elif level == "日期" and file_time:
            return f"{file_time.day:02d}"
        elif level == "星期" and file_time:
            weekdays = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"]
            return weekdays[file_time.weekday()]
        
        elif level in ["拍摄设备"]:
            if exif_data.get('Make'):
                make = exif_data['Make']
                if isinstance(make, str):
                    make = make.strip().strip('"\'')
                return make
            else:
                return "未知设备"
        elif level == "相机型号":
            if exif_data.get('Model'):
                model = exif_data['Model']
                if isinstance(model, str):
                    model = model.strip().strip('"\'')
                return model
            else:
                return "未知设备"
        
        elif level == "拍摄省份":
            if exif_data.get('GPS GPSLatitude') and exif_data.get('GPS GPSLongitude'):
                province, _ = self.get_city_and_province(
                    exif_data['GPS GPSLatitude'], exif_data['GPS GPSLongitude']
                )
                return province
            else:
                return "未知省份"
        elif level == "拍摄城市":
            if exif_data.get('GPS GPSLatitude') and exif_data.get('GPS GPSLongitude'):
                _, city = self.get_city_and_province(
                    exif_data['GPS GPSLatitude'], exif_data['GPS GPSLongitude']
                )
                return city
            else:
                return "未知城市"
        
        elif level == "文件类型":
            return get_file_type(file_path)
        elif level == "按扩展名":
            file_ext = os.path.splitext(str(file_path))[1].strip('.').upper()
            return file_ext
        
        else:
            return "未知"
