import os
import hashlib
import logging
from PyQt6 import QtCore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FileScanThread(QtCore.QThread):
    """文件扫描线程"""
    
    # 信号定义
    progress_updated = QtCore.pyqtSignal(int, str)  # 进度更新信号
    scan_completed = QtCore.pyqtSignal(list)  # 扫描完成信号
    error_occurred = QtCore.pyqtSignal(str)  # 错误发生信号
    
    def __init__(self, folder_path, filters=None):
        super().__init__()
        self.folder_path = folder_path
        self.filters = filters or []
        self._stop_flag = False
    
    def stop(self):
        """停止扫描"""
        self._stop_flag = True
        logger.info("扫描线程收到停止信号")
    
    def _calculate_md5(self, file_path, block_size=8192):
        """计算文件的MD5值"""
        try:
            md5 = hashlib.md5()
            file_size = os.path.getsize(file_path)
            processed_size = 0
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(block_size), b''):
                    if self._stop_flag:
                        logger.debug("MD5计算已停止")
                        return None
                    md5.update(chunk)
                    processed_size += len(chunk)
                    
                    # 对于大文件，提供更详细的进度信息
                    if file_size > 100 * 1024 * 1024:  # 大于100MB的文件
                        chunk_progress = int(processed_size / file_size * 100)
                        self.progress_updated.emit(-1, f"计算MD5: {file_path} ({chunk_progress}%)")
            
            file_hash = md5.hexdigest()
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
    
    def run(self):
        """运行扫描线程"""
        logger.info(f"开始扫描文件夹: {self.folder_path}")
        if self.filters:
            logger.info(f"使用文件过滤器: {self.filters}")
        
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
            all_files = []
            try:
                file_count = 0
                for root, _, files in os.walk(self.folder_path):
                    if self._stop_flag:
                        logger.info("扫描已停止")
                        self.error_occurred.emit("扫描已停止")
                        return
                    
                    for file in files:
                        # 应用文件过滤器
                        if self.filters and not any(file.lower().endswith(filter.lower()) for filter in self.filters):
                            continue
                        
                        try:
                            file_path = os.path.join(root, file)
                            # 检查文件是否可访问
                            if os.access(file_path, os.R_OK):
                                all_files.append(file_path)
                                file_count += 1
                                # 定期更新进度
                                if file_count % 100 == 0:
                                    self.progress_updated.emit(-1, f"收集文件: 已找到 {file_count} 个文件")
                        except Exception as e:
                            logger.warning(f"无法访问文件 {os.path.join(root, file)}: {str(e)}")
            except PermissionError:
                logger.error(f"无权限访问文件夹: {self.folder_path}")
                self.error_occurred.emit(f"无权限访问文件夹")
                return
            except Exception as e:
                logger.error(f"遍历文件夹时出错: {str(e)}")
                self.error_occurred.emit(f"遍历文件夹时出错: {str(e)}")
                return
            
            logger.info(f"总共找到 {len(all_files)} 个文件")
            
            # 计算MD5值并查找重复
            file_hashes = {}
            total_files = len(all_files)
            skipped_files = 0
            
            for i, file_path in enumerate(all_files):
                if self._stop_flag:
                    logger.info("扫描已停止")
                    self.error_occurred.emit("扫描已停止")
                    return
                
                # 更新进度
                progress = int((i + 1) / total_files * 100)
                self.progress_updated.emit(progress, f"正在扫描: {os.path.basename(file_path)}")
                
                try:
                    file_hash = self._calculate_md5(file_path)
                    if self._stop_flag:
                        logger.info("扫描已停止")
                        self.error_occurred.emit("扫描已停止")
                        return
                    
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
            # 完成扫描
            self.scan_completed.emit(duplicate_groups)
            
        except Exception as e:
            logger.error(f"扫描重复文件时出错: {str(e)}")
            self.error_occurred.emit(f"扫描出错: {str(e)}")

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