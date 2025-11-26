import os
import hashlib
import logging
from PyQt6 import QtCore
import time
from concurrent.futures import ThreadPoolExecutor
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileScanThread(QtCore.QThread):
    """文件扫描线程"""
    
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    file_count_updated = QtCore.pyqtSignal(int)  # 文件计数更新信号
    
    def __init__(self, folder_path, filters=None):
        super().__init__()
        self.folder_path = folder_path
        self.filters = filters or []
        self._stop_flag = False
        self._file_cache = {}  # 文件缓存，避免重复计算
        self._cache_lock = threading.RLock()  # 缓存锁
        self._thread_pool = None  # 线程池用于并行计算MD5
        self._max_workers = min(4, os.cpu_count() or 2)  # 根据CPU核心数设置最大工作线程数
        self._last_progress_time = 0  # 上次进度更新时间，避免过于频繁的更新
        self._progress_update_interval = 0.1  # 进度更新间隔（秒）
    
    def stop(self):
        """停止扫描"""
        self._stop_flag = True
        logger.info("扫描线程收到停止信号")
    
    def _calculate_md5(self, file_path, block_size=8192*8):  # 增加块大小以提高性能
        """计算文件的MD5值"""
        # 检查缓存
        with self._cache_lock:
            if file_path in self._file_cache:
                file_info = self._file_cache[file_path]
                # 检查文件是否被修改（通过大小和修改时间）
                try:
                    current_stat = os.stat(file_path)
                    if (current_stat.st_size == file_info['size'] and 
                        abs(current_stat.st_mtime - file_info['mtime']) < 0.1):
                        logger.debug(f"从缓存获取MD5: {file_path} -> {file_info['hash']}")
                        return file_info['hash']
                except Exception as e:
                    logger.warning(f"检查文件缓存状态失败: {str(e)}")
        
        try:
            # 获取文件信息用于缓存
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_mtime = file_stat.st_mtime
            
            # 对于空文件，直接返回固定值
            if file_size == 0:
                empty_hash = "d41d8cd98f00b204e9800998ecf8427e"  # 空文件的MD5
                with self._cache_lock:
                    self._file_cache[file_path] = {
                        'hash': empty_hash,
                        'size': file_size,
                        'mtime': file_mtime
                    }
                return empty_hash
            
            # 对于小文件，直接读取整个文件
            if file_size < 10 * 1024 * 1024:  # 小于10MB的文件
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    if self._stop_flag:
                        return None
                    file_hash = hashlib.md5(content).hexdigest()
                except MemoryError:
                    # 如果内存不足，回退到分块读取
                    logger.warning(f"小文件一次性读取内存不足，回退到分块读取: {file_path}")
                    return self._calculate_md5_chunked(file_path, file_size, file_mtime, block_size)
            else:
                # 大文件分块读取
                return self._calculate_md5_chunked(file_path, file_size, file_mtime, block_size)
            
            # 更新缓存
            with self._cache_lock:
                self._file_cache[file_path] = {
                    'hash': file_hash,
                    'size': file_size,
                    'mtime': file_mtime
                }
            
            logger.debug(f"计算文件MD5成功: {file_path} -> {file_hash}")
            return file_hash
        except FileNotFoundError:
            logger.error(f"文件不存在: {file_path}")
            return None
        except PermissionError:
            logger.error(f"无权限访问文件: {file_path}")
            return None
        except Exception as e:
            logger.error(f"计算文件{file_path}的MD5值失败: {str(e)}")
            return None
    
    def _calculate_md5_chunked(self, file_path, file_size, file_mtime, block_size):
        """分块计算文件的MD5值"""
        md5 = hashlib.md5()
        processed_size = 0
        last_progress_update = 0
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(block_size), b''):
                    if self._stop_flag:
                        logger.debug("MD5计算已停止")
                        return None
                    md5.update(chunk)
                    processed_size += len(chunk)
                    
                    # 对于大文件，提供更详细的进度信息，但限制更新频率
                    if file_size > 100 * 1024 * 1024:  # 大于100MB的文件
                        current_time = time.time()
                        if current_time - last_progress_update > self._progress_update_interval:
                            chunk_progress = int(processed_size / file_size * 100)
                            self._safe_progress_update(-1, f"计算MD5: {os.path.basename(file_path)} ({chunk_progress}%)")
                            last_progress_update = current_time
            
            file_hash = md5.hexdigest()
            
            # 更新缓存
            with self._cache_lock:
                self._file_cache[file_path] = {
                    'hash': file_hash,
                    'size': file_size,
                    'mtime': file_mtime
                }
            
            return file_hash
        except Exception as e:
            logger.error(f"分块计算文件{file_path}的MD5值失败: {str(e)}")
            return None
    
    def _safe_progress_update(self, progress, status_text):
        """安全地更新进度，避免过于频繁的UI更新"""
        current_time = time.time()
        if current_time - self._last_progress_time >= self._progress_update_interval:
            self.progress_updated.emit(progress, status_text)
            self._last_progress_time = current_time
    
    def run(self):
        """运行扫描线程"""
        logger.info(f"开始扫描文件夹: {self.folder_path}")
        if self.filters:
            logger.info(f"使用文件过滤器: {self.filters}")
        
        # 初始化线程池
        self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
        
        try:
            # 验证文件夹路径
            if not os.path.exists(self.folder_path):
                error_msg = f"文件夹不存在: {self.folder_path}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            if not os.path.isdir(self.folder_path):
                error_msg = f"路径不是文件夹: {self.folder_path}"
                logger.error(error_msg)
                self.error_occurred.emit(error_msg)
                return
            
            # 获取所有文件
            all_files = self._collect_files()
            if self._stop_flag:
                return
            
            total_files = len(all_files)
            logger.info(f"总共找到 {total_files} 个文件")
            
            # 如果文件数量为0，直接返回
            if total_files == 0:
                self.scan_completed.emit([])
                return
            
            # 计算MD5值并查找重复
            duplicate_groups = self._find_duplicates(all_files)
            
            if self._stop_flag:
                return
            
            # 完成扫描
            self.scan_completed.emit(duplicate_groups)
            
        except Exception as e:
            logger.error(f"扫描重复文件时出错: {str(e)}")
            self.error_occurred.emit(f"扫描出错: {str(e)}")
        finally:
            # 清理线程池
            if self._thread_pool:
                self._thread_pool.shutdown(wait=False)
    
    def _collect_files(self):
        """收集所有符合条件的文件"""
        all_files = []
        file_count = 0
        last_progress_update = 0
        
        # 预处理过滤器，提高匹配效率
        processed_filters = []
        for filter in self.filters:
            if not filter.startswith('.'):
                filter = '.' + filter
            processed_filters.append(filter.lower())
        
        try:
            for root, _, files in os.walk(self.folder_path):
                if self._stop_flag:
                    logger.info("扫描已停止")
                    self.error_occurred.emit("扫描已停止")
                    return []
                
                for file in files:
                    # 应用文件过滤器
                    if processed_filters:
                        file_lower = file.lower()
                        if not any(file_lower.endswith(filter) for filter in processed_filters):
                            continue
                    
                    try:
                        file_path = os.path.join(root, file)
                        # 检查文件是否可访问
                        if os.access(file_path, os.R_OK):
                            all_files.append(file_path)
                            file_count += 1
                            # 定期更新进度，但限制更新频率
                            current_time = time.time()
                            if current_time - last_progress_update > self._progress_update_interval:
                                self._safe_progress_update(-1, f"收集文件: 已找到 {file_count} 个文件")
                                last_progress_update = current_time
                    except Exception as e:
                        logger.warning(f"无法访问文件 {os.path.join(root, file)}: {str(e)}")
        except PermissionError:
            logger.error(f"无权限访问文件夹: {self.folder_path}")
            self.error_occurred.emit(f"无权限访问文件夹")
            return []
        except Exception as e:
            logger.error(f"遍历文件夹时出错: {str(e)}")
            self.error_occurred.emit(f"遍历文件夹时出错: {str(e)}")
            return []
        
        # 发送最终文件计数
        self.file_count_updated.emit(file_count)
        return all_files
    
    def _find_duplicates(self, all_files):
        """查找重复文件"""
        file_hashes = {}
        total_files = len(all_files)
        skipped_files = 0
        last_progress_update = 0
        
        # 首先按文件大小分组，减少MD5计算次数
        size_groups = {}
        for file_path in all_files:
            if self._stop_flag:
                return []
            
            try:
                file_size = os.path.getsize(file_path)
                if file_size in size_groups:
                    size_groups[file_size].append(file_path)
                else:
                    size_groups[file_size] = [file_path]
            except Exception as e:
                skipped_files += 1
                logger.warning(f"获取文件大小失败 {file_path}: {str(e)}")
        
        # 只对有多个文件的大小组计算MD5
        filtered_files = []
        for size, files in size_groups.items():
            if len(files) > 1:
                filtered_files.extend(files)
        
        logger.info(f"优化后需要计算MD5的文件数: {len(filtered_files)} (总文件数: {total_files})")
        
        # 计算MD5值
        total_filtered = len(filtered_files)
        for i, file_path in enumerate(filtered_files):
            if self._stop_flag:
                logger.info("扫描已停止")
                self.error_occurred.emit("扫描已停止")
                return []
            
            # 更新进度，但限制更新频率
            current_time = time.time()
            if current_time - last_progress_update > self._progress_update_interval:
                progress = int((i + 1) / total_filtered * 100)
                self._safe_progress_update(progress, f"正在扫描: {os.path.basename(file_path)} ({i+1}/{total_filtered})")
                last_progress_update = current_time
            
            try:
                file_hash = self._calculate_md5(file_path)
                if self._stop_flag:
                    return []
                
                if file_hash is None:
                    skipped_files += 1
                    logger.warning(f"跳过文件: {file_path}")
                    continue
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(file_path)
                else:
                    file_hashes[file_hash] = [file_path]
            except Exception as e:
                skipped_files += 1
                logger.error(f"处理文件{file_path}时出错: {str(e)}")
        
        if skipped_files > 0:
            logger.warning(f"扫描过程中跳过了 {skipped_files} 个文件")
        
        # 过滤出重复的文件组
        duplicate_groups = [files for files in file_hashes.values() if len(files) > 1]
        
        # 按文件数量降序排序（优先显示重复文件最多的组）
        duplicate_groups.sort(key=len, reverse=True)
        
        logger.info(f"扫描完成，找到 {len(duplicate_groups)} 组重复文件")
        return duplicate_groups
    
    def stop(self):
        """停止扫描"""
        self._stop_flag = True
        logger.info("扫描线程收到停止信号")
        
        # 清理线程池
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)

class FileDeduplicateThread(QtCore.QThread):
    """文件去重线程"""
    
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    deduplicate_completed = QtCore.pyqtSignal(int, int)  # 去重完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, duplicate_groups, delete_list=None):
        super().__init__()
        self.duplicate_groups = duplicate_groups
        self.delete_list = delete_list or []
        self._stop_flag = False
    
    def stop(self):
        """停止去重"""
        self._stop_flag = True
        logger.info("去重线程收到停止信号")
    
    def run(self):
        """运行去重线程"""
        logger.info(f"开始执行去重操作，共有 {len(self.delete_list)} 个文件待删除")
        
        try:
            total_deleted = 0
            total_files = 0
            failed_deletions = 0
            
            # 计算需要处理的文件总数
            total_to_process = len(self.delete_list) if self.delete_list else sum(len(group) - 1 for group in self.duplicate_groups)
            
            logger.info(f"总共需要处理 {total_to_process} 个文件")
            
            if self.delete_list:
                # 使用明确的删除列表
                for i, file_path in enumerate(self.delete_list):
                    if self._stop_flag:
                        logger.info("去重已停止")
                        self.error_occurred.emit("去重已停止")
                        return
                    
                    try:
                        # 更新进度
                        progress = int((i + 1) / total_to_process * 100)
                        file_name = os.path.basename(file_path)
                        self.progress_updated.emit(progress, f"正在删除: {file_name}")
                        
                        # 检查文件是否存在
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            total_deleted += 1
                            logger.info(f"已删除重复文件: {file_path}")
                        else:
                            logger.warning(f"文件不存在: {file_path}")
                            failed_deletions += 1
                        
                        total_files += 1
                        
                    except PermissionError:
                        failed_deletions += 1
                        logger.error(f"无权限删除文件: {file_path}")
                    except Exception as e:
                        failed_deletions += 1
                        logger.error(f"删除文件{file_path}失败: {str(e)}")
            else:
                # 使用重复组进行去重
                for group_idx, file_group in enumerate(self.duplicate_groups):
                    for file_idx, file_path in enumerate(file_group):
                        # 跳过每组的第一个文件（保留）
                        if file_idx == 0:
                            continue
                        
                        if self._stop_flag:
                            logger.info("去重已停止")
                            self.error_occurred.emit("去重已停止")
                            return
                        
                        try:
                            # 更新进度
                            progress = int((total_files / total_to_process) * 100)
                            file_name = os.path.basename(file_path)
                            self.progress_updated.emit(progress, f"正在删除: {file_name}")
                            
                            # 检查文件是否存在
                            if os.path.exists(file_path):
                                os.remove(file_path)
                                total_deleted += 1
                                logger.info(f"已删除重复文件: {file_path}")
                            else:
                                logger.warning(f"文件不存在: {file_path}")
                                failed_deletions += 1
                            
                        except PermissionError:
                            failed_deletions += 1
                            logger.error(f"无权限删除文件: {file_path}")
                        except Exception as e:
                            failed_deletions += 1
                            logger.error(f"删除文件{file_path}失败: {str(e)}")
                        
                        total_files += 1
            
            # 记录去重统计信息
            logger.info(f"去重完成: 成功删除 {total_deleted} 个文件, 失败 {failed_deletions} 个文件, 共处理 {total_files} 个文件")
            
            # 完成去重
            self.deduplicate_completed.emit(total_deleted, total_files)
            
        except Exception as e:
            logger.error(f"执行文件去重时出错: {str(e)}")
            self.error_occurred.emit(f"去重出错: {str(e)}")