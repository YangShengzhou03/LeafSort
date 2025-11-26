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
    
    progress_updated = QtCore.pyqtSignal(int, str)
    scan_completed = QtCore.pyqtSignal(list)
    error_occurred = QtCore.pyqtSignal(str)
    file_count_updated = QtCore.pyqtSignal(int)
    
    def __init__(self, folder_path, filters=None):
        super().__init__()
        self.folder_path = folder_path
        self.filters = filters or []
        self._stop_flag = False
        self._file_cache = {}
        self._cache_lock = threading.RLock()
        self._thread_pool = None
        self._max_workers = min(4, os.cpu_count() or 2)
        self._last_progress_time = 0
        self._progress_update_interval = 0.1
    
    def stop(self):
        self._stop_flag = True
    
    def _calculate_md5(self, file_path, block_size=8192*16):
        with self._cache_lock:
            if file_path in self._file_cache:
                file_info = self._file_cache[file_path]
                try:
                    current_stat = os.stat(file_path)
                    if (current_stat.st_size == file_info['size'] and 
                        abs(current_stat.st_mtime - file_info['mtime']) < 0.1):
                        logger.debug(f"从缓存获取MD5: {file_path} -> {file_info['hash']}")
                        return file_info['hash']
                except Exception as e:
                    logger.warning(f"检查文件缓存状态失败: {str(e)}")
        
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            file_mtime = file_stat.st_mtime
            
            if file_size > 2 * 1024 * 1024 * 1024:
                logger.warning(f"文件过大，跳过MD5计算: {file_path} ({file_size} bytes)")
                return None
            
            if file_size == 0:
                empty_hash = "d41d8cd98f00b204e9800998ecf8427e"
                with self._cache_lock:
                    self._file_cache[file_path] = {
                        'hash': empty_hash,
                        'size': file_size,
                        'mtime': file_mtime
                    }
                return empty_hash
            
            if file_size < 5 * 1024 * 1024:
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                    if self._stop_flag:
                        return None
                    file_hash = hashlib.md5(content).hexdigest()
                except MemoryError:
                    logger.warning(f"小文件一次性读取内存不足，回退到分块读取: {file_path}")
                    return self._calculate_md5_chunked(file_path, file_size, file_mtime, block_size)
            else:
                return self._calculate_md5_chunked(file_path, file_size, file_mtime, block_size)
            
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
        except OSError as e:
            if e.errno == 22:
                logger.warning(f"文件名编码问题，跳过文件: {file_path}")
                return None
            else:
                logger.error(f"计算文件{file_path}的MD5值失败: {str(e)}")
                return None
        except Exception as e:
            logger.error(f"计算文件{file_path}的MD5值失败: {str(e)}")
            return None
    
    def _calculate_md5_chunked(self, file_path, file_size, file_mtime, block_size):
        try:
            md5_hash = hashlib.md5()
            with open(file_path, 'rb') as f:
                bytes_read = 0
                while True:
                    if self._stop_flag:
                        return None
                    
                    chunk = f.read(block_size)
                    if not chunk:
                        break
                    
                    md5_hash.update(chunk)
                    bytes_read += len(chunk)
                    
                    if bytes_read % (100 * 1024 * 1024) < block_size:
                        progress = min(100, int((bytes_read / file_size) * 100))
                        self.progress_updated.emit(progress, f"正在计算MD5: {os.path.basename(file_path)}")
            
            file_hash = md5_hash.hexdigest()
            
            with self._cache_lock:
                self._file_cache[file_path] = {
                    'hash': file_hash,
                    'size': file_size,
                    'mtime': file_mtime
                }
            
            return file_hash
        except OSError as e:
            if e.errno == 22:
                logger.warning(f"文件名编码问题，跳过文件: {file_path}")
            else:
                logger.error(f"分块计算文件{file_path}的MD5值失败: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"分块计算文件{file_path}的MD5值失败: {str(e)}")
            return None
    
    def _safe_progress_update(self, progress, status_text):
        current_time = time.time()
        if current_time - self._last_progress_time >= self._progress_update_interval:
            self.progress_updated.emit(progress, status_text)
            self._last_progress_time = current_time
    
    def run(self):
        try:
            logger.info("文件扫描线程开始运行")
            self._stop_flag = False
            
            if isinstance(self.folder_path, str):
                folders = [self.folder_path]
            else:
                folders = self.folder_path
            
            valid_folders = []
            for folder in folders:
                if self._stop_flag:
                    break
                
                if not os.path.exists(folder):
                    logger.warning(f"文件夹不存在: {folder}")
                    self.error_occurred.emit(f"文件夹不存在: {folder}")
                    continue
                
                if not os.path.isdir(folder):
                    logger.warning(f"路径不是文件夹: {folder}")
                    self.error_occurred.emit(f"路径不是文件夹: {folder}")
                    continue
                
                valid_folders.append(folder)
            
            if not valid_folders:
                logger.warning("没有有效的文件夹")
                self.error_occurred.emit("没有有效的文件夹")
                self.scan_completed.emit([])
                return
            
            self._thread_pool = ThreadPoolExecutor(max_workers=self._max_workers)
            
            all_files = []
            total_files = 0
            for folder in valid_folders:
                if self._stop_flag:
                    break
                
                folder_files = self._collect_files(folder)
                all_files.extend(folder_files)
                total_files += len(folder_files)
                
                logger.info(f"文件夹 {folder} 中找到 {len(folder_files)} 个文件")
                self.progress_updated.emit(10, f"已扫描文件夹: {os.path.basename(folder)}")
            
            if not all_files:
                logger.warning("没有找到任何文件")
                self.scan_completed.emit([])
                return
            
            logger.info(f"总共找到 {len(all_files)} 个文件，开始查找重复项")
            self.progress_updated.emit(30, f"开始分析 {len(all_files)} 个文件")
            
            duplicate_groups = self._find_duplicates(all_files)
            
            if self._stop_flag:
                logger.info("扫描被用户中断")
                return
            
            logger.info(f"找到 {len(duplicate_groups)} 组重复文件")
            self.progress_updated.emit(100, "扫描完成")
            self.scan_completed.emit(duplicate_groups)
            
        except Exception as e:
            logger.error(f"扫描线程运行出错: {str(e)}")
            self.error_occurred.emit(f"扫描线程运行出错: {str(e)}")
        finally:
            if hasattr(self, '_thread_pool') and self._thread_pool:
                self._thread_pool.shutdown(wait=False)
            logger.info("文件扫描线程结束运行")
    
    def _collect_files(self, folder):
        files = []
        file_count = 0
        
        try:
            for root, dirs, filenames in os.walk(folder):
                if self._stop_flag:
                    break
                
                dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['System Volume Information', '$RECYCLE.BIN', 'RECYCLER']]
                
                for filename in filenames:
                    if self._stop_flag:
                        break
                    
                    if filename.startswith('.') or filename.startswith('~'):
                        continue
                    
                    file_path = os.path.join(root, filename)
                    
                    if self.filters:
                        file_ext = os.path.splitext(filename)[1].lower()
                        if file_ext not in self.filters:
                            continue
                    
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size == 0:
                            continue
                        if file_size > 10 * 1024 * 1024 * 1024:
                            logger.debug(f"跳过过大文件: {file_path} ({file_size} bytes)")
                            continue
                    except (OSError, IOError, PermissionError) as e:
                        logger.debug(f"无法访问文件: {file_path}, 错误: {str(e)}")
                        continue
                    
                    files.append(file_path)
                    file_count += 1
                    
                    if file_count % 500 == 0:
                        self.progress_updated.emit(5, f"已收集 {file_count} 个文件")
        
        except Exception as e:
            logger.error(f"收集文件时出错: {str(e)}")
        
        logger.info(f"文件夹 {folder} 中收集到 {file_count} 个文件")
        return files
    
    def _find_duplicates(self, all_files):
        file_hashes = {}
        total_files = len(all_files)
        skipped_files = 0
        last_progress_update = 0
        
        size_groups = {}
        for file_path in all_files:
            if self._stop_flag:
                return []
            
            try:
                file_size = os.path.getsize(file_path)
                logger.debug(f"文件: {file_path}, 大小: {file_size} 字节")
                if file_size in size_groups:
                    size_groups[file_size].append(file_path)
                    logger.debug(f"发现相同大小文件组: 大小={file_size}, 文件数={len(size_groups[file_size])}")
                else:
                    size_groups[file_size] = [file_path]
            except Exception as e:
                skipped_files += 1
                logger.warning(f"获取文件大小失败 {file_path}: {str(e)}")
        
        single_files = 0
        potential_duplicates = 0
        for size, files in size_groups.items():
            if len(files) == 1:
                single_files += 1
            else:
                potential_duplicates += len(files)
                logger.info(f"潜在重复组: 大小={size} 字节, 包含文件数={len(files)}")
                for file in files:
                    logger.debug(f"  - {file}")
        logger.info(f"文件大小分析完成: 单文件组={single_files}, 多文件组={len(size_groups)-single_files}, 潜在重复文件={potential_duplicates}")
        
        filtered_files = []
        for size, files in size_groups.items():
            if len(files) > 1:
                filtered_files.extend(files)
        
        logger.info(f"优化后需要计算MD5的文件数: {len(filtered_files)} (总文件数: {total_files})")
        
        total_filtered = len(filtered_files)
        for i, file_path in enumerate(filtered_files):
            if self._stop_flag:
                logger.info("扫描已停止")
                self.error_occurred.emit("扫描已停止")
                return []
            
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
                
                logger.info(f"文件: {file_path}, MD5: {file_hash}")
                
                if file_hash in file_hashes:
                    file_hashes[file_hash].append(file_path)
                else:
                    file_hashes[file_hash] = [file_path]
            except Exception as e:
                skipped_files += 1
                logger.error(f"处理文件{file_path}时出错: {str(e)}")
        
        if skipped_files > 0:
            logger.warning(f"扫描过程中跳过了 {skipped_files} 个文件")
        
        duplicate_groups = [files for files in file_hashes.values() if len(files) > 1]
        
        duplicate_groups.sort(key=len, reverse=True)
        
        logger.info(f"扫描完成，找到 {len(duplicate_groups)} 组重复文件")
        for i, group in enumerate(duplicate_groups):
            logger.info(f"重复组 #{i+1}: 包含 {len(group)} 个文件")
            for file in group:
                try:
                    file_hash = self._calculate_md5(file)
                    logger.info(f"  文件: {file}, MD5: {file_hash}")
                except Exception as e:
                    logger.warning(f"  无法计算文件 {file} 的MD5值: {str(e)}")
                try:
                    file_size = os.path.getsize(file)
                    logger.debug(f"    大小: {file_size} 字节, 修改时间: {os.path.getmtime(file)}")
                except Exception as e:
                    logger.warning(f"获取文件信息失败 {file}: {str(e)}")
        
        if len(duplicate_groups) == 0 and potential_duplicates > 0:
            pass
        
        return duplicate_groups
    
    def stop(self):
        self._stop_flag = True
        logger.info("扫描线程收到停止信号")
        
        if self._thread_pool:
            self._thread_pool.shutdown(wait=False)

class FileDeduplicateThread(QtCore.QThread):
    
    progress_updated = QtCore.pyqtSignal(int, str)
    deduplicate_completed = QtCore.pyqtSignal(int, int)
    error_occurred = QtCore.pyqtSignal(str)
    
    def __init__(self, duplicate_groups, delete_list=None):
        super().__init__()
        self.duplicate_groups = duplicate_groups
        self.delete_list = delete_list or []
        self._stop_flag = False
    
    def stop(self):
        self._stop_flag = True
    
    def run(self):
        logger.info(f"开始执行去重操作，共有 {len(self.delete_list)} 个文件待删除")
        
        try:
            total_deleted = 0
            total_files = 0
            failed_deletions = 0
            
            total_to_process = len(self.delete_list) if self.delete_list else sum(len(group) - 1 for group in self.duplicate_groups)
            
            logger.info(f"总共需要处理 {total_to_process} 个文件")
            
            if self.delete_list:
                for i, file_path in enumerate(self.delete_list):
                    if self._stop_flag:
                        logger.info("去重已停止")
                        self.error_occurred.emit("去重已停止")
                        return
                    
                    try:
                        progress = int((i + 1) / total_to_process * 100)
                        file_name = os.path.basename(file_path)
                        self.progress_updated.emit(progress, f"正在删除: {file_name}")
                        
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
                for group_idx, file_group in enumerate(self.duplicate_groups):
                    for file_idx, file_path in enumerate(file_group):
                        if file_idx == 0:
                            continue
                        
                        if self._stop_flag:
                            logger.info("去重已停止")
                            self.error_occurred.emit("去重已停止")
                            return
                        
                        try:
                            progress = int((total_files / total_to_process) * 100)
                            file_name = os.path.basename(file_path)
                            self.progress_updated.emit(progress, f"正在删除: {file_name}")
                            
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
            
            logger.info(f"去重完成: 成功删除 {total_deleted} 个文件, 失败 {failed_deletions} 个文件, 共处理 {total_files} 个文件")
            
            self.deduplicate_completed.emit(total_deleted, total_files)
            
        except Exception as e:
            logger.error(f"执行文件去重时出错: {str(e)}")
            self.error_occurred.emit(f"去重出错: {str(e)}")