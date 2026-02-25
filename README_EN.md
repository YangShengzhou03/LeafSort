# LeafSort 轻羽媒体整理 - 图片管理，智能整理、文件去重、EXIF编辑和批量处理

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

LeafSort（轻羽媒体整理）是一个基于 Python 的图像管理工具，专注于高效管理、智能整理和批量处理各种图像文件。软件支持快速浏览和管理多种图像格式，提供基于拍摄时间、GPS 位置、拍摄设备、文件类型等多个维度的自动分类和整理功能，支持基于 MD5 哈希算法的文件去重，支持查看和编辑 EXIF 元数据，以及地理编码操作。

本软件采用三层架构设计，包括用户界面层、业务逻辑层和数据处理层。用户界面层基于 PyQt6 构建现代化 GUI 界面，业务逻辑层处理核心业务逻辑和功能实现，数据处理层负责文件操作、元数据处理和配置管理。通过现代化的技术架构和人性化的交互设计，为用户提供便捷、高效、安全的媒体文件管理服务。

软件的设计理念是简单、高效、智能。简单体现在用户界面简洁明了，操作流程清晰易懂，用户无需复杂的学习成本即可快速上手。高效体现在文件处理速度快，支持多线程并发处理，能够快速处理大量文件。智能体现在自动识别图像元数据，智能分类和整理，减少人工操作。

软件的技术架构采用模块化设计，将系统划分为多个独立的功能模块，每个模块负责特定的功能。这种架构设计使得系统具有良好的可扩展性和可维护性，可以方便地添加新功能或修改现有功能。

软件致力于为摄影爱好者和专业摄影师提供一个免费、高效的媒体文件管理工具，帮助用户快速整理和管理大量的照片和视频文件，提高工作效率。软件支持多种图像格式，包括 JPEG、PNG、WebP、HEIC、HEIF 等主流格式，能够快速加载和显示大量图像文件。

## 功能特性

### 图像管理

支持快速浏览和管理多种图像格式，包括 JPEG、PNG、WebP、HEIC、HEIF 等主流格式，能够快速加载和显示大量图像文件。

![媒体导入](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/media_import.png)

### 智能整理

提供智能整理功能，可以基于图像拍摄时间、GPS 位置、拍摄设备、文件类型等多个维度自动分类和整理文件。用户可以自定义分类规则和文件命名规则。软件自动读取图像 EXIF 元数据，构建目标路径和文件名，执行文件复制或移动操作。

![智能整理](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/smart_organize.png)

支持按时间维度分类，包括年、年-月、年-月-日、年-月-日-时-分-秒等多种格式。支持按地理位置分类，包括省、市、区等不同层级。支持按设备类型分类，包括相机品牌、型号等。支持按文件类型分类，包括图像、视频、音频、文档等不同类型。

### 文件去重

基于 MD5 哈希算法高精度识别完全相同的文件。支持两阶段过滤机制：第一阶段按文件大小分组，快速排除非重复文件；第二阶段仅对相同大小的文件计算 MD5，显著减少计算量。使用线程池并发计算 MD5，支持缓存已计算的哈希值，提高处理效率。
![文件去重](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/file_deduplication.png)
支持批量去重，可以扫描整个文件夹或指定文件夹，自动识别重复文件。支持手动选择保留的文件，或让软件随机选择。支持预览重复文件，查看文件详情，确保删除正确的文件。

### EXIF 编辑

支持查看和修改图像 EXIF 元数据信息，包括标题、作者、评级、相机品牌、型号、镜头信息等。软件内置相机品牌型号数据库和镜头型号数据库，可以自动匹配镜头信息。支持 JPEG、PNG、WebP 等多种格式的 EXIF 读写，对于复杂格式使用 exiftool 作为备用方案。

![EXIF 编辑](https://gitee.com/Yangshengzhou/leaf-sort/raw/master/assets/attribute_write.png)

支持批量编辑 EXIF，可以一次性修改多个文件的 EXIF 信息。支持自定义字段，包括标题、作者、关键词、描述等。支持评级系统，可以为文件设置 1-5 星评级。支持查看完整的 EXIF 信息，包括拍摄参数、GPS 位置、相机设置等。

### 地理编码

使用离线地理数据将 GPS 坐标转换为地址信息。支持批量处理相同位置的文件，提高处理效率。

支持反向地理编码，将经纬度坐标转换为省、市、区等地址信息。支持批量处理，可以一次性处理多个文件的 GPS 信息。支持自定义地址格式，包括省、市、区、街道等不同层级。

### 多格式支持

除了图像格式，还支持管理和处理视频、音频、文档、压缩包等其他文件类型。支持文件类型检测，自动识别文件类型。支持文件扩展名过滤，可以按文件类型筛选文件。

## 快速开始

### 环境要求

#### 开发环境
- **Python**: 3.11+ 
- **PyQt6**: 6.5.0+ (GUI 框架)
- **Pillow**: 11.3.0+ (图像处理)
- **piexif**: 1.1.3+ (EXIF 处理)
- **exifread**: 3.0.0+ (EXIF 读取)
- **pillow-heif**: 0.16.0+ (HEIC/HEIF 支持)
- **requests**: 2.31.0+ (HTTP 请求)

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
项目依赖多个第三方库，包括图像处理库（Pillow）、EXIF 处理库（piexif、exifread）、HTTP 请求库（requests）等。安装依赖库后，可以通过运行 `pip list` 命令检查所有依赖库是否正确安装。

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

### 4. 运行应用
```bash
python App.py
```

运行该命令会启动应用程序，显示主窗口。应用程序会自动检查更新，如果有新版本，会提示用户下载和安装。应用程序支持单实例运行，如果已经有一个实例在运行，新的实例会自动退出。

## 使用指南

### 文件夹管理

启动软件后，首先需要设置源文件夹和目标文件夹。点击"浏览"按钮，选择包含要整理图像的文件夹作为源文件夹，选择整理后的图像存储位置作为目标文件夹。软件会显示文件夹的基本信息，包括文件数量。

### 智能整理

在智能整理页面，可以配置分类规则和文件命名规则。支持按时间维度分类，包括年、年-月、年-月-日、年-月-日-时-分-秒等格式。支持按地理位置分类，包括省、市、区等不同层级。支持按设备类型分类，包括相机品牌、型号等。支持按文件类型分类，包括图像、视频、音频、文档等不同类型。

配置完成后，点击"开始整理"按钮，软件会自动遍历文件夹，读取图像 EXIF 元数据，构建目标路径和文件名，执行文件复制或移动操作。整理过程中，软件会显示进度信息，包括已处理文件数、总文件数、处理速度等。

### EXIF 编辑

在 EXIF 编辑页面，可以为图像添加或修改 EXIF 元数据。支持设置标题、作者、评级、相机品牌、型号、镜头信息等。软件内置相机品牌型号数据库和镜头型号数据库，选择相机品牌和型号后，会自动匹配镜头信息。

配置完成后，点击"开始写入"按钮，软件会遍历文件夹，更新图像 EXIF 数据。写入过程中，软件会显示进度信息，包括已处理文件数、总文件数、处理速度等。

### 文件去重

在文件去重页面，可以查找和删除重复文件。点击"开始查重"按钮，软件会扫描文件夹，计算文件 MD5 哈希值，查找完全相同的文件。去重完成后，会显示重复文件列表。用户可以手动选择保留的文件，或让软件随机选择。

选择完成后，点击"移动到回收站"按钮，软件会将选中的重复文件移动到回收站。移动过程中，软件会显示进度信息，包括已移动文件数、总文件数、移动速度等。

### 地理编码

软件自动将图像 GPS 坐标转换为地址信息。使用离线地理数据进行反向地理编码。

支持反向地理编码，将经纬度坐标转换为省、市、区等地址信息。支持批量处理，可以一次性处理多个文件的 GPS 信息。支持自定义地址格式，包括省、市、区、街道等不同层级。

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
│  主窗口         │    │  智能整理       │    │  ExifTool       │
│  文件夹管理     │    │  EXIF 编辑      │    │                 │
│  进度显示       │    │  文件去重       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 技术栈详情

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| PyQt6 | 6.5.0+ | GUI 框架 |
| Pillow | 11.3.0+ | 图像处理 |
| piexif | 1.1.3+ | EXIF 处理 |
| exifread | 3.0.0+ | EXIF 读取 |
| pillow-heif | 0.16.0+ | HEIC/HEIF 支持 |
| requests | 2.31.0+ | HTTP 请求 |

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
    ├── exiftool/                   # EXIF 工具
    │   ├── exiftool.exe            # EXIF 工具可执行文件
    │   ├── exiftool(-k).exe        # EXIF 工具（保持窗口）
    │   └── exiftool_files/         # EXIF 工具依赖文件
    ├── img/                        # 图像资源
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
- **common.py**: 通用工具库，提供资源路径管理、文件类型检测、媒体类型检测等功能
- **config_manager.py**: 配置管理器，线程安全的配置读写操作
- **update_dialog.py**: 更新检查对话框，检查 GitHub 上的最新版本

### 线程模型

软件使用 Qt 信号槽机制进行线程通信。主线程处理所有 UI 交互和响应，工作线程执行耗时的文件操作任务。所有工作线程继承自 QThread，支持随时停止操作，保持 UI 响应性。

## 开发指南

### 代码规范

类名使用 PascalCase 命名规范，如 SmartArrangeManager。函数名使用小写字母加下划线，如 get_exif_data。变量名使用小写字母加下划线，如 file_path。常量使用大写字母加下划线，如 IMAGE_EXTENSIONS。私有方法使用单下划线前缀，如 _process_file。

### 错误处理

所有可能抛出异常的操作都应该使用 try-except 块进行捕获和处理。异常信息应该记录到日志中，并在必要时向用户显示友好的错误提示。对于关键操作失败，应该提供重试机制或回滚机制。

### 日志记录

使用 Python 标准库 logging 进行日志记录。日志级别分为 DEBUG、INFO、WARNING、ERROR、CRITICAL 五个级别。DEBUG 级别用于详细的调试信息，INFO 级别用于一般信息，WARNING 级别用于警告信息，ERROR 级别用于错误信息，CRITICAL 级别用于严重错误信息。

### 测试建议

在开发新功能时，应该编写单元测试和集成测试。测试应该覆盖正常流程和异常流程。测试数据应该使用模拟数据，避免使用真实用户数据。

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 贡献指南

欢迎提交 Issue 和 Pull Request。提交 Issue 时，请详细描述问题现象、复现步骤、期望结果等信息。提交 Pull Request 时，请确保代码符合项目的代码规范，并通过所有测试。

## 联系方式

- **GitHub**: https://github.com/YangShengzhou03/LeafSort
- **Gitee**: https://gitee.com/Yangshengzhou/leaf-sort
- **Microsoft Store**: https://apps.microsoft.com/detail/9p3mkv4xslj8

## 更新日志

### v2.0.2 (2025-02-08)
- 优化文件处理逻辑，改为边处理边移动/复制，提升性能
- 优化内存使用，减少记录的数据量
- 修复停止按钮响应慢的问题
- 移除未使用的依赖包和资源文件
- 修复 smart_arrange.py 中的 QtWidgets 导入错误

### v2.0.1 (2025-01-15)
- 修复地理编码功能
- 优化文件去重算法
- 改进用户界面响应速度

### v2.0.0 (2025-01-01)
- 初始版本发布
- 支持智能整理功能
- 支持 EXIF 编辑功能
- 支持文件去重功能
- 支持地理编码功能

## 致谢

感谢所有为本项目做出贡献的开发者和用户。特别感谢以下开源项目：

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python GUI 框架
- [Pillow](https://python-pillow.org/) - Python 图像处理库
- [piexif](https://github.com/hMatoba/Piexif) - EXIF 处理库
- [exifread](https://github.com/ianare/exifread) - EXIF 读取库
- [pillow-heif](https://github.com/bigcat88/pillow_heif) - HEIC/HEIF 支持库
- [ExifTool](https://exiftool.org/) - EXIF 工具

## 关于作者

杨圣洲，来自江西吉安县。2022 年参加江西省职教高考，以 559 分的成绩获得全省第一名，考入江西科技师范大学信息管理与信息系统专业。在校期间系统学习了 Linux、Docker、K8S 等 DevOps 与运维相关技术，专注于 Windows 桌面工具、自动化解决方案及企业级系统的研发与落地，开发了多款不同场景的项目。

在众多项目中，Jobs_helper（海投助手）是一款聚焦 Boss 直聘平台的浏览器脚本插件，具备自动化简历投递、AI 智能回复 HR 消息等功能。LeafSort（轻羽媒体整理）融合深度学习算法与多线程处理能力，可对海量照片与视频进行整理、归类及去重，已通过微软应用商店、联想应用商店分发，适配 Windows 系统。LeafPan 是基于 Vue 3 和 Spring Boot 3 构建的企业级文件管理平台。LeafBoss 专注于卡密全生命周期管理与安全验证服务。Lucky_SMS 是教育类开源系统，具备多角色权限控制，适用于毕业设计、商业应用及教育管理场景，后续更新了用户信息脱敏功能。HiTutor 好会帮则是一个基于 Flutter 和 Spring Boot 的家教信息对接共享平台，为学生和家教老师提供免费、公平、透明的信息对接服务。

---

<div align="center">
  <p>Made with ❤️ by Yangshengzhou</p>
</div>
