# 标准库导入
import os
from typing import Optional, Tuple, List

# 第三方库导入
from PyQt6 import QtWidgets
from PyQt6.QtCore import pyqtSignal


class FolderPage(QtWidgets.QWidget):
    """
    文件夹选择页面类，负责处理源文件夹和目标文件夹的选择、验证和信息显示。
    
    该类提供了用户界面交互功能，允许用户选择文件夹并进行相关验证，
    包括检查文件夹关系、非空状态，以及显示文件夹详细信息。
    
    信号:
        folders_changed (list): 当源文件夹或目标文件夹选择改变时发出信号，
                              传递当前选择的文件夹列表
    """
    # 定义信号，当文件夹选择改变时触发
    folders_changed = pyqtSignal(list)
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """
        初始化文件夹选择页面。
        
        参数:
            parent: 父窗口部件，通常是主应用窗口或对话框，默认为None
        """
        super().__init__(parent)
        self.parent = parent
        
        # 连接浏览按钮的点击事件到文件夹浏览方法
        # 传递不同的标题和输入控件以区分源文件夹和目标文件夹选择
        self.parent.btnBrowseSource.clicked.connect(
            lambda: self._browse_directory("选择源文件夹", self.parent.inputSourceFolder))
        self.parent.btnBrowseTarget.clicked.connect(
            lambda: self._browse_directory("选择目标文件夹", self.parent.inputTargetFolder))
        
    def _browse_directory(self, title: str, line_edit: QtWidgets.QLineEdit) -> None:
        """
        打开文件夹选择对话框，并处理选择结果。
        
        该方法处理文件夹选择的完整流程，包括：
        1. 显示文件夹选择对话框
        2. 验证文件夹关系（不能相同或存在隶属关系）
        3. 检查目标文件夹是否为空
        4. 更新文件夹信息显示
        5. 更新状态文本
        
        参数:
            title: 对话框标题，用于区分源文件夹和目标文件夹选择
            line_edit: 显示选择路径的行编辑控件
        """
        # 保存原始路径，确保在发生异常时可以恢复
        original_path = line_edit.text()
        
        try:
            # 打开文件夹选择对话框，使用当前路径作为起始位置
            selected_path = QtWidgets.QFileDialog.getExistingDirectory(self, title, original_path or "")
            
            # 如果用户取消选择，则直接返回
            if not selected_path:
                return
                
            # 更新行编辑控件显示选择的路径
            line_edit.setText(selected_path)
            
            # 一次性检查parent属性和必要的控件是否存在
            # 这样可以避免在后续代码中重复调用hasattr方法
            has_parent = self.parent is not None
            has_source_folder = has_parent and hasattr(self.parent, 'inputSourceFolder')
            has_target_folder = has_parent and hasattr(self.parent, 'inputTargetFolder')
            has_import_status = has_parent and hasattr(self.parent, 'importStatus')
            has_text_browser = (hasattr(self, 'textBrowser_import_info') or 
                              (has_parent and hasattr(self.parent, 'textBrowser_import_info')))
            
            # 检查文件夹关系（仅当源文件夹和目标文件夹都存在且非空时）
            if has_source_folder and has_target_folder:
                source_path = self.parent.inputSourceFolder.text().strip()
                target_path = self.parent.inputTargetFolder.text().strip()
                
                if source_path and target_path:
                    try:
                        # 验证两个文件夹之间的关系是否有效
                        if not self._check_folder_relationship(source_path, target_path):
                            # 显示错误消息并恢复原始路径
                            QtWidgets.QMessageBox.warning(
                                self,
                                "文件夹选择错误",
                                "源文件夹和目标文件夹不能相同，也不能存在隶属关系。",
                                QtWidgets.QMessageBox.StandardButton.Ok
                            )
                            line_edit.setText(original_path)
                            return
                    except Exception as e:
                        # 捕获验证过程中可能发生的异常
                        QtWidgets.QMessageBox.warning(
                            self,
                            "验证错误",
                            f"验证文件夹关系时出错：{str(e)}",
                            QtWidgets.QMessageBox.StandardButton.Ok
                        )
                        line_edit.setText(original_path)
                        return
            
            # 目标文件夹非空检查
            if title == "选择目标文件夹":
                try:
                    items = os.listdir(selected_path)
                    if items:
                        QtWidgets.QMessageBox.warning(
                            self,
                            "注意",
                            "目标文件夹不是一个空文件夹。",
                            QtWidgets.QMessageBox.StandardButton.Ok
                        )
                except (OSError, FileNotFoundError) as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "访问错误",
                        f"无法访问目标文件夹：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                except PermissionError as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "权限错误",
                        f"没有权限访问目标文件夹：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                except Exception as e:
                    QtWidgets.QMessageBox.warning(
                        self,
                        "检查错误",
                        f"检查目标文件夹状态时出错：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
            
            # 更新文本浏览器显示文件夹信息（仅源文件夹）
            text_browser = None
            if hasattr(self, 'textBrowser_import_info'):
                text_browser = self.textBrowser_import_info
            elif has_parent and hasattr(self.parent, 'textBrowser_import_info'):
                text_browser = self.parent.textBrowser_import_info
                
            if text_browser and title == "选择源文件夹":
                try:
                    text_browser.setText(self.get_folder_info(selected_path))
                except Exception as e:
                    text_browser.setText(f"获取文件夹信息时出错：{str(e)}")
                    QtWidgets.QMessageBox.warning(
                        self,
                        "信息显示错误",
                        f"无法显示文件夹信息：{str(e)}",
                        QtWidgets.QMessageBox.StandardButton.Ok
                    )
                    
            # 更新状态文本
            if has_import_status:
                try:
                    # 根据不同情况设置不同的状态文本
                    if title == "选择源文件夹":
                        self.parent.importStatus.setText("源文件夹已选择")
                    elif title == "选择目标文件夹":
                        self.parent.importStatus.setText("目标文件夹已选择")
                    
                    # 检查是否两个文件夹都已选择
                    if has_source_folder and has_target_folder:
                        source_path = self.parent.inputSourceFolder.text().strip()
                        target_path = self.parent.inputTargetFolder.text().strip()
                        if source_path and target_path:
                            self.parent.importStatus.setText("文件夹导入完成")
                except Exception as e:
                    # 在状态更新失败时不影响主流程，仅记录错误
                    pass
        
        except Exception as e:
            # 捕获所有其他未预期的异常
            QtWidgets.QMessageBox.critical(
                self,
                "操作失败",
                f"浏览文件夹时发生未知错误：{str(e)}",
                QtWidgets.QMessageBox.StandardButton.Ok
            )
            # 尝试恢复原始状态
            if hasattr(line_edit, 'setText'):
                line_edit.setText(original_path)
    
    def _check_folder_relationship(self, folder1: str, folder2: str) -> bool:
        """
        检查两个文件夹之间的关系，确保它们不是同一个文件夹，也不存在隶属关系。
        
        该方法执行以下验证：
        1. 规范化路径以确保路径分隔符一致
        2. 检查两个路径是否指向同一个文件夹
        3. 检查一个文件夹是否是另一个文件夹的子文件夹
        
        参数:
            folder1: 第一个文件夹路径
            folder2: 第二个文件夹路径
            
        返回:
            bool: 如果文件夹关系有效（不是同一个，也不存在隶属关系），则返回True；否则返回False
        """
        # 快速检查：如果任一路径为空，直接返回True
        if not folder1 or not folder2:
            return True
            
        try:
            # 规范化路径，确保路径分隔符一致，并处理路径大小写
            normalized_folder1 = os.path.normpath(os.path.abspath(folder1)).lower()
            normalized_folder2 = os.path.normpath(os.path.abspath(folder2)).lower()
            
            # 先检查是否为同一文件夹（最常见的情况）
            if normalized_folder1 == normalized_folder2:
                return False
                
            # 安全地检查隶属关系，处理路径分隔符和边界情况
            # 构建规范化的完整路径，并添加路径分隔符以避免前缀误判
            # 例如：C:\folder 和 C:\folders 不应该被误判为隶属关系
            folder1_full = os.path.join(normalized_folder1, '')
            folder2_full = os.path.join(normalized_folder2, '')
            
            # 检查是否存在隶属关系
            if folder1_full.startswith(folder2_full) or folder2_full.startswith(folder1_full):
                return False
                
        except (OSError, ValueError) as e:
            # 路径处理可能出现的异常
            return False
            
        # 所有验证通过，文件夹关系有效
        return True
    
    def get_folder_info(self, folder_path: str) -> str:
        """
        获取文件夹的详细信息，包括路径、文件数量和文件夹数量。
        
        该方法分析指定文件夹的内容，并生成一个格式化的信息字符串，
        包含路径信息、文件和文件夹计数，以及可能的错误提示。
        
        参数:
            folder_path: 要分析的文件夹路径
            
        返回:
            str: 格式化的文件夹信息字符串，包含详细的统计数据和提示信息
        """
        # 初始化信息文本列表，用于构建最终的信息字符串
        info_lines = [
            "=== 待处理的源文件夹信息 ===",
            f"路径：{folder_path}"
        ]
        
        # 初始化计数器和错误跟踪变量
        file_count = 0         # 顶层文件数量
        directory_count = 0    # 顶层文件夹数量
        total_items = 0        # 总项目数量
        error_message = ""
        skipped_items_count = 0
        
        try:
            # 验证路径是否存在且是一个文件夹
            if not os.path.exists(folder_path):
                error_message = "指定的文件夹路径不存在"
            elif not os.path.isdir(folder_path):
                error_message = "指定的路径不是一个文件夹"
            else:
                try:
                    # 获取文件夹中的所有项目
                    items = os.listdir(folder_path)
                    total_items = len(items)
                    
                    # 遍历所有项目，统计文件和文件夹数量
                    for item_name in items:
                        item_full_path = os.path.join(folder_path, item_name)
                        try:
                            if os.path.isfile(item_full_path):
                                file_count += 1
                            elif os.path.isdir(item_full_path):
                                directory_count += 1
                        except (OSError, PermissionError):
                            # 记录无法访问的项目
                            skipped_items_count += 1
                            continue
                        except Exception:
                            # 捕获其他任何单个项目访问异常
                            skipped_items_count += 1
                            continue
                except (OSError, FileNotFoundError) as e:
                    error_message = f"无法访问文件夹内容：{str(e)}"
                except PermissionError as e:
                    error_message = f"没有权限访问文件夹内容：{str(e)}"
                except Exception as e:
                    error_message = f"读取文件夹内容时发生未知错误：{str(e)}"
        except Exception as e:
            error_message = f"验证文件夹时发生错误：{str(e)}"
        
        # 添加错误信息（如果有）
        if error_message:
            info_lines.append(f"\n错误：{error_message}")
        
        # 如果有跳过的项目，添加提示信息
        if skipped_items_count > 0:
            info_lines.append(f"\n注意：跳过了 {skipped_items_count} 个无法访问的项目")
        
        # 添加统计信息和分隔线
        info_lines.extend([
            "",  # 添加空行提高可读性
            "-" * 10 + "注意！会递归遍历处理子文件夹" + "-" * 10,
            "{:<75}".format("顶层内容统计"),
            "{:<25} {:<25} {:<25}".format(
                f"顶层文件数量：{file_count}",
                f"顶层文件夹数量：{directory_count}",
                f"总计：{total_items}"
            ),
            "-" * 75
        ])
        
        # 连接所有行并返回最终的信息字符串
        return '\n'.join(info_lines)
