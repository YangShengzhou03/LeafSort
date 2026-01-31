# LeafSort —— 轻羽媒体整理

<div align="center">

[![GitHub stars](https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/stargazers)&nbsp;[![GitHub forks](https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/network/members)&nbsp;[![GitHub issues](https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=for-the-badge&logo=github)](https://github.com/YangShengzhou03/LeafSort/issues)&nbsp;[![GitHub license](https://img.shields.io/github/license/YangShengzhou03/LeafSort?style=for-the-badge)](https://github.com/YangShengzhou03/LeafSort/blob/main/LICENSE)&nbsp;[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python)](https://www.python.org/)&nbsp;[![PyQt6](https://img.shields.io/badge/PyQt6-6.5.0+-41CD52?style=for-the-badge&logo=qt)](https://www.riverbankcomputing.com/software/pyqt/)

<a href="https://apps.microsoft.com/detail/9p3mkv4xslj8?referrer=appbadge&mode=direct">
 <img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>

<div align="center">
  <h3>一个现代化的媒体文件管理工具，专注于高效管理和智能整理</h3>
  <p>支持多种图像格式的快速浏览和管理，提供基于时间、地点、设备、类型的自动分类和整理</p>
</div>

[快速开始](#快速开始) • [功能特性](#功能特性) • [技术架构](#技术架构) • [使用指南](#使用指南)

</div>

## 项目简介

LeafSort（轻羽媒体整理）是一个基于 Python 的图像管理工具，专注于高效管理、智能整理和批量处理各种图像文件。软件支持快速浏览和管理多种图像格式，提供基于拍摄时间、GPS 位置、拍摄设备、文件类型等多个维度的自动分类和整理功能，支持基于 MD5 哈希算法的文件去重，支持查看和编辑 EXIF 元数据，以及批量重命名和地理编码操作。

本软件采用三层架构设计，包括用户界面层、业务逻辑层和数据处理层。用户界面层基于 PyQt6 构建现代化 GUI 界面，业务逻辑层处理核心业务逻辑和功能实现，数据处理层负责文件操作、元数据处理和配置管理。通过现代化的技术架构和人性化的交互设计，为用户提供便捷、高效、安全的媒体文件管理服务。

软件的设计理念是简单、高效、智能。简单体现在用户界面简洁明了，操作流程清晰易懂，用户无需复杂的学习成本即可快速上手。高效体现在文件处理速度快，支持多线程并发处理，能够快速处理大量文件。智能体现在自动识别图像元数据，智能分类和整理，减少人工操作。

软件的技术架构采用模块化设计，将系统划分为多个独立的功能模块，每个模块负责特定的功能。这种架构设计使得系统具有良好的可扩展性和可维护性，可以方便地添加新功能或修改现有功能。软件还采用缓存机制，提高系统响应速度，优化用户体验。

软件致力于为摄影爱好者和专业摄影师提供一个免费、高效的媒体文件管理工具，帮助用户快速整理和管理大量的照片和视频文件，提高工作效率。软件支持多种图像格式，包括 JPEG、PNG、WebP、HEIC、HEIF 等主流格式，能够快速加载和显示大量图像文件。

## 功能特性

### 图像管理

支持快速浏览和管理多种图像格式，包括 JPEG、PNG、WebP、HEIC、HEIF 等主流格式，能够快速加载和显示大量图像文件。支持缩略图预览，快速定位目标文件，支持文件选择、复制、移动、删除等基本操作。

![媒体导入](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/media_import.png)

### 智能整理

提供智能整理功能，可以基于图像拍摄时间、GPS 位置、拍摄设备、文件类型等多个维度自动分类和整理文件。用户可以自定义分类规则和文件命名规则。软件自动读取图像 EXIF 元数据，构建目标路径和文件名，执行文件复制或移动操作。

![智能整理](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/smart_organize.png)

支持按时间维度分类，包括年、年-月、年-月-日、年-月-日-时-分-秒等多种格式。支持按地理位置分类，包括省、市、区等不同层级。支持按设备类型分类，包括相机品牌、型号等。支持按文件类型分类，包括图像、视频、音频、文档等不同类型。

### 文件去重

基于 MD5 哈希算法高精度识别完全相同的文件。支持两阶段过滤机制：第一阶段按文件大小分组，快速排除非重复文件；第二阶段仅对相同大小的文件计算 MD5，显著减少计算量。使用线程池并发计算 MD5，支持缓存已计算的哈希值，提高处理效率。

支持批量去重，可以扫描整个文件夹或指定文件夹，自动识别重复文件。支持手动选择保留的文件，或让软件随机选择。支持预览重复文件，查看文件详情，确保删除正确的文件。

### EXIF 编辑

支持查看和修改图像 EXIF 元数据信息，包括标题、作者、评级、相机品牌、型号、镜头信息等。软件内置相机品牌型号数据库和镜头型号数据库，可以自动匹配镜头信息。支持 JPEG、PNG、WebP 等多种格式的 EXIF 读写，对于复杂格式使用 exiftool 作为备用方案。

![EXIF 编辑](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/attribute_write.png)

支持批量编辑 EXIF，可以一次性修改多个文件的 EXIF 信息。支持自定义字段，包括标题、作者、关键词、描述等。支持评级系统，可以为文件设置 1-5 星评级。支持查看完整的 EXIF 信息，包括拍摄参数、GPS 位置、相机设置等。

### 地理编码

自动使用高德地图 API 将 GPS 坐标转换为地址信息。软件缓存地理编码结果，避免重复调用 API，支持批量处理相同位置的文件，提高处理效率。如果 API 调用失败，使用离线地理数据作为备用方案。

支持反向地理编码，将经纬度坐标转换为省、市、区等地址信息。支持批量处理，可以一次性处理多个文件的 GPS 信息。支持自定义地址格式，包括省、市、区、街道等不同层级。

### 多格式支持

除了图像格式，还支持管理和处理视频、音频、文档、压缩包等其他文件类型。支持文件类型检测，自动识别文件类型。支持文件扩展名过滤，可以按文件类型筛选文件。

## 快速开始

### 环境要求

#### 开发环境
- **Python**: 3.11+ 
- **PyQt6**: 6.5.0+ (GUI 框架)
- **Pillow**: 11.3.0+ (图像处理)
- **opencv-python**: 4.8.0+ (计算机视觉)
- **scikit-image**: 0.24.0+ (图像处理)
- **numpy**: 1.24.0+ (数值计算)
- **piexif**: 1.1.3+ (EXIF 处理)
- **exifread**: 3.0.0+ (EXIF 读取)
- **pillow-heif**: 0.16.0+ (HEIC/HEIF 支持)
- **requests**: 2.31.0+ (HTTP 请求)
- **playwright**: 1.40.0+ (浏览器自动化)

#### 生产环境
- **操作系统**: Windows 10/11
- **内存**: 4GB+ RAM
- **存储**: 2GB+ 可用空间

### 环境配置说明

#### Python 环境配置
Python 3.11+ 是软件开发的基础环境，PyQt6 6.5.0+ 框架要求 Python 3.11 或更高版本。安装 Python 3.11 后，需要配置 PATH 环境变量，将 Python 的 Scripts 目录添加到 PATH 中。可以通过运行 `python --version` 命令验证 Python 是否正确安装。

#### PyQt6 环境配置
PyQt6 6.5.0+ 是软件开发的基础 GUI 框架，用于构建现代化的用户界面。安装 PyQt6 后，可以通过运行 `pip list` 命令检查 PyQt6 是否正确安装。PyQt6 支持 Windows、macOS、Linux 等多个平台。

#### 依赖库配置
项目依赖多个第三方库，包括图像处理库（Pillow、opencv-python、scikit-image）、EXIF 处理库（piexif、exifread）、HTTP 请求库（requests）、浏览器自动化库（playwright）等。安装依赖库后，可以通过运行 `pip list` 命令检查所有依赖库是否正确安装。

## 安装部署

### 1. 克隆项目
```bash
git clone https://github.com/YangShengzhou03/LeafSort.git
cd LeafSort
```

克隆项目后，项目目录包含多个 Python 源文件、资源文件、配置文件等。主要文件包括 App.py（应用入口）、main_window.py（主窗口）、smart_arrange.py（智能整理）、write_exif.py（EXIF 编辑）、file_deduplication.py（文件去重）等。

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate
```

创建虚拟环境可以隔离项目依赖，避免与其他项目的依赖冲突。激活虚拟环境后，命令行提示符会显示虚拟环境名称，表示当前已进入虚拟环境。

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

requirements.txt 文件列出了项目依赖的所有第三方库及其版本要求。运行该命令会自动下载并安装所有依赖库。安装完成后，可以通过运行 `pip list` 命令检查所有依赖库是否正确安装。

### 4. 安装 Playwright 浏览器
```bash
playwright install chromium
```

Playwright 用于浏览器自动化，需要安装 Chromium 浏览器。运行该命令会自动下载并安装 Chromium 浏览器及其依赖。安装完成后，Playwright 可以自动启动 Chromium 浏览器并执行自动化操作。

### 5. 运行应用
```bash
python App.py
```

运行该命令会启动应用程序，显示主窗口。应用程序会自动检查更新，如果有新版本，会提示用户下载和安装。应用程序支持单实例运行，如果已经有一个实例在运行，新的实例会自动退出。

## 使用指南

### 文件夹管理

启动软件后，首先需要设置源文件夹和目标文件夹。点击"添加文件夹"按钮，选择包含要整理图像的文件夹作为源文件夹，选择整理后的图像存储位置作为目标文件夹。软件会显示文件夹的基本信息，包括文件数量和总大小。

### 智能整理

在智能整理页面，可以配置分类规则和文件命名规则。支持按时间维度分类，包括年、年-月、年-月-日、年-月-日-时-分-秒等格式。支持按地理位置分类，包括省、市、区等不同层级。支持按设备类型分类，包括相机品牌、型号等。支持按文件类型分类，包括图像、视频、音频、文档等不同类型。

配置完成后，点击"开始整理"按钮，软件会自动遍历文件夹，读取图像 EXIF 元数据，构建目标路径和文件名，执行文件复制或移动操作。整理过程中，软件会显示进度信息，包括已处理文件数、总文件数、处理速度等。

### EXIF 编辑

在 EXIF 编辑页面，可以为图像添加或修改 EXIF 元数据。支持设置标题、作者、评级、相机品牌、型号、镜头信息等。软件内置相机品牌型号数据库和镜头型号数据库，选择相机品牌和型号后，会自动匹配镜头信息。

配置完成后，点击"开始写入"按钮，软件会遍历文件夹，更新图像 EXIF 数据。写入过程中，软件会显示进度信息，包括已处理文件数、总文件数、处理速度等。

### 文件去重

在文件去重页面，可以查找和删除重复文件。点击"开始去重"按钮，软件会扫描文件夹，计算文件 MD5 哈希值，查找完全相同的文件。去重完成后，会显示重复文件列表。用户可以手动选择要保留的文件，或让软件随机选择。

选择完成后，点击"开始删除"按钮，软件会删除选中的重复文件。删除过程中，软件会显示进度信息，包括已删除文件数、总文件数、删除速度等。

### 地理编码

软件自动将图像 GPS 坐标转换为地址信息。使用高德地图 API 进行反向地理编码，支持缓存地理编码结果，避免重复调用 API。如果 API 调用失败，使用离线地理数据作为备用方案。

## 技术架构

### 系统架构图
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   用户界面层     │    │   业务逻辑层     │    │   数据处理层     │
│                 │    │                 │    │                 │
│  PyQt6 6.5.0    │◄──►│  Python 3.11+   │◄──►│  文件系统       │
│  Qt Designer    │    │  多线程处理     │    │  EXIF 数据      │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                        │                        │
         │                        │                        │
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   图形界面       │    │   核心功能       │    │   外部服务       │
│                 │    │                 │    │                 │
│  主窗口         │    │  智能整理       │    │  高德地图 API    │
│  文件夹管理     │    │  EXIF 编辑      │    │  Playwright      │
│  进度显示       │    │  文件去重       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 技术栈详情

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| PyQt6 | 6.5.0+ | GUI 框架 |
| Pillow | 11.3.0+ | 图像处理 |
| opencv-python | 4.8.0+ | 计算机视觉 |
| scikit-image | 0.24.0+ | 图像处理 |
| numpy | 1.24.0+ | 数值计算 |
| piexif | 1.1.3+ | EXIF 处理 |
| exifread | 3.0.0+ | EXIF 读取 |
| pillow-heif | 0.16.0+ | HEIC/HEIF 支持 |
| requests | 2.31.0+ | HTTP 请求 |
| playwright | 1.40.0+ | 浏览器自动化 |

### 项目结构

```
LeafSort/
├── App.py                          # 应用入口
├── main_window.py                  # 主窗口实现
├── Ui_MainWindow.py                # UI 界面文件（自动生成）
├── Ui_MainWindow.ui                # Qt Designer 界面文件
├── add_folder.py                   # 文件夹管理功能
├── smart_arrange.py                # 智能整理服务管理器
├── smart_arrange_thread.py         # 智能整理工作线程
├── write_exif.py                   # EXIF 编辑管理器
├── write_exif_thread.py            # EXIF 写入工作线程
├── file_deduplication.py           # 文件去重管理器
├── file_deduplication_thread.py    # 文件去重工作线程
├── common.py                       # 通用函数和工具类
├── config_manager.py               # 配置管理器（线程安全）
├── update_dialog.py                # 更新检查对话框
├── UI_UpdateDialog.py              # 更新对话框 UI（自动生成）
├── UI_UpdateDialog.ui              # Qt Designer 界面文件
├── requirements.txt                # Python 依赖列表
├── App.spec                        # PyInstaller 打包配置
├── README.md                       # 项目文档（中文）
├── README_EN.md                    # 项目文档（英文）
├── license.txt                     # 许可证文本
├── .gitignore                      # Git 忽略文件配置
├── License/                        # 数字签名相关文件
│   ├── Y.cer                       # 证书文件
│   ├── Y.pfx                       # 私钥文件
│   ├── Y.pvk                       # 私钥容器
│   ├── Y.spc                       # 软件发布者证书
│   ├── cert2spc.exe                # 证书转换工具
│   └── certmgr.exe                 # 证书管理工具
└── resources/                      # 资源文件
    ├── cv2_date/                   # OpenCV 相关文件
    │   └── haarcascade_frontalface_alt2.xml  # 人脸检测模型
    ├── exiftool/                   # EXIF 工具
    │   ├── exiftool.exe            # EXIF 工具可执行文件
    │   ├── exiftool(-k).exe        # EXIF 工具（保持窗口）
    │   └── exiftool_files/         # EXIF 工具依赖文件
    ├── img/                        # 图像资源
    │   ├── activity/               # 活动相关图标
    │   ├── list/                   # 列表图标
    │   ├── page_0/                 # 页面 0 图标
    │   ├── page_1/                 # 页面 1 图标
    │   ├── page_2/                 # 页面 2 图标
    │   ├── page_3/                 # 页面 3 图标
    │   ├── page_4/                 # 页面 4 图标
    │   ├── 头标/                   # 会员徽章
    │   ├── 窗口控制/               # 窗口控制图标
    │   ├── icon.ico                # 应用图标
    │   └── setup.ico               # 安装图标
    ├── json/                       # JSON 数据文件
    │   ├── City_Reverse_Geocode.json         # 城市地理编码数据
    │   ├── Province_Reverse_Geocode.json     # 省份地理编码数据
    │   ├── camera_brand_model.json           # 相机品牌型号数据库
    │   ├── camera_lens_mapping.json          # 相机镜头映射数据库
    │   └── lens_model.json                  # 镜头型号数据库
    └── stylesheet/                 # 样式表文件
        └── menu.setStyleSheet.css  # 菜单样式表
```

### 核心模块说明

- **App.py**: 应用入口，负责初始化 QApplication、创建主窗口实例、设置全局异常处理和单实例检测
- **main_window.py**: 主窗口控制器，管理所有功能页面，处理窗口事件，管理系统托盘图标
- **add_folder.py**: 文件夹管理页面，管理源文件夹和目标文件夹选择，验证文件夹路径有效性
- **smart_arrange.py**: 智能整理业务逻辑管理器，管理智能整理 UI 交互，收集用户配置
- **smart_arrange_thread.py**: 智能整理工作线程，在独立线程中执行整理任务，避免阻塞 UI
- **write_exif.py**: EXIF 编辑业务逻辑管理器，管理 EXIF 编辑 UI 交互，收集用户配置
- **write_exif_thread.py**: EXIF 写入工作线程，在独立线程中执行 EXIF 写入任务
- **file_deduplication.py**: 文件去重业务逻辑管理器，管理文件去重 UI 交互
- **file_deduplication_thread.py**: 文件去重工作线程，扫描文件并计算 MD5，删除重复文件
- **common.py**: 通用工具库，提供资源路径管理、文件类型检测、媒体类型检测、地理编码服务等功能
- **config_manager.py**: 配置管理器，线程安全的配置读写操作，管理地理编码缓存和 API 调用限流
- **update_dialog.py**: 更新检查对话框，检查 GitHub 上的最新版本

### 线程模型

软件使用 Qt 信号槽机制进行线程通信。主线程处理所有 UI 交互和响应，工作线程执行耗时的文件操作任务。所有工作线程继承自 QThread，支持随时停止操作，保持 UI 响应性。

## 开发指南

### 代码规范

类名使用 PascalCase 命名规范，如 SmartArrangeManager。函数名使用小写字母加下划线，如 get_exif_data。变量名使用小写字母加下划线，如 file_path。常量使用大写字母加下划线，如 IMAGE_EXTENSIONS。私有方法使用单下划线前缀，如 _process_file。

### 错误处理

使用 try-except 捕获异常，记录详细的错误信息，并向用户显示友好的错误消息。当关键操作失败时，提供恢复建议。对于文件操作错误：如果文件不存在，跳过并记录；如果权限不足，记录错误并继续处理其他文件；如果文件损坏，记录错误并跳过。对于 EXIF 读取错误：如果不支持格式，使用文件系统时间；如果数据损坏，记录警告并使用默认值；如果字段缺失，使用空值或默认值。对于网络请求错误：如果 API 调用失败，使用缓存数据；如果 Cookie 过期，重新获取 Cookie；如果超时，重试 3 次后放弃。

### 性能优化

软件使用缓存机制提高性能，包括缩略图缓存、元数据缓存、地理编码缓存、文件哈希缓存。使用线程池并发计算 MD5，同时处理多个文件，最大线程数限制为 CPU 核心数。分块读取大文件，避免一次性加载，及时释放未使用的资源，限制缓存大小防止内存溢出。在文件去重时，先按大小分组，跳过空文件和超大文件，跳过系统文件夹和隐藏文件。

## 许可证

本项目采用 MIT 许可证，详见 license.txt 文件。

## 联系方式

GitHub: https://github.com/YangShengzhou03/LeafSort
Microsoft Store: https://apps.microsoft.com/detail/9p3mkv4xslj8
