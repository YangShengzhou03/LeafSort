<div align="center">
  <h1>🍁 枫叶相册 - LeafView</h1>
  
  <p>
    <em>基于 electron+vue3 构建的现代媒体管理工具</em>
  </p>

  <div>
    <a href="https://github.com/YangShengzhou03/LeafView/stargazers">
      <img src="https://img.shields.io/github/stars/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=ffd33d&labelColor=000000" alt="GitHub Stars">
    </a>
    <a href="https://github.com/YangShengzhou03/LeafView/forks">
      <img src="https://img.shields.io/github/forks/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=green&labelColor=000000" alt="GitHub Forks">
    </a>
    <a href="https://opensource.org/licenses/MIT">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=open-source-initiative&color=blue&labelColor=000000" alt="MIT License">
    </a>
    <a href="https://github.com/YangShengzhou03/LeafView/issues">
      <img src="https://img.shields.io/github/issues/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=purple&labelColor=000000" alt="GitHub Issues">
    </a>
  </div>

  <div>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" alt="Python Version">
    </a>
    <a href="https://www.riverbankcomputing.com/software/pyqt/">
      <img src="https://img.shields.io/badge/PyQt6-6.5.0-green?style=for-the-badge&logo=qt" alt="PyQt6 Version">
    </a>
    <a href="https://pillow.readthedocs.io/en/stable/">
      <img src="https://img.shields.io/badge/Pillow-11.3.0-orange?style=for-the-badge&logo=pypi" alt="Pillow Version">
    </a>
  </div>

  <br />

</div>

## 目录
1. [✨ 项目概述](#-项目概述)
2. [🚀 技术架构](#-技术架构)
3. [🌟 核心功能](#-核心功能)
4. [💻 安装部署](#-安装部署)
5. [📖 使用说明](#-使用说明)
6. [📁 目录结构](#-目录结构)
7. [🤝 参与贡献](#-参与贡献)
8. [📜 开源许可](#-开源许可)
9. [🔄 更新日志](#-更新日志)

## ✨ 项目概述
枫叶相册 (LeafView) 是一款基于 **Python** 和 **PyQt6** 构建的**开源图片与媒体管理工具**，为用户提供直观、高效的图片浏览和管理体验。系统采用单例模式设计，支持多种图片格式，并提供智能整理、去重、EXIF信息编辑等功能。

### 🎯 设计理念
- **用户友好**：简洁直观的界面设计，降低使用门槛
- **高效管理**：批量处理能力，提高工作效率
- **智能分析**：基于图像哈希和EXIF数据的智能分类与整理
- **安全可靠**：提供预览和确认机制，防止误操作

### 💡 适用场景
- 个人图片库管理与浏览
- 摄影爱好者的照片整理与分类
- 图片批量处理与重命名
- 图片元数据（EXIF）编辑
- 重复图片检测与清理
- 媒体文件组织与管理

## 🚀 技术架构

### 🔧 技术栈
| 技术                | 版本      | 描述                                                         |
|---------------------|-----------|--------------------------------------------------------------|
| **Python 3.11**     | 3.11+     | 主要编程语言，提供强大的后端处理能力                         |
| **PyQt6**           | 6.5.0     | 跨平台GUI框架，用于构建直观、美观的用户界面                  |
| **Pillow**          | 11.3.0    | Python图像处理库，支持各种图片格式的读写和处理              |
| **pillow-heif**     | 1.1.0     | HEIF格式支持，扩展Pillow对HEIC等格式的兼容性                 |
| **piexif**          | 1.1.3     | 用于读取和写入EXIF元数据信息                                |
| **pytesseract**     | 0.3.10    | OCR文字识别引擎，提供图片文字识别功能                        |
| **requests**        | 2.31.0    | HTTP客户端库，用于检查更新和网络请求                        |
| **send2trash**      | 1.8.2     | 安全删除文件到回收站的工具                                   |
| **numpy**           | 1.26.4    | 科学计算库，用于图像数据处理                                |
| **exifread**        | 3.0.0     | EXIF数据读取库                                              |
| **moviepy**         | 1.0.3     | 视频处理库，支持媒体文件处理                                |
| **python-magic**    | 0.4.27    | 文件类型检测库，用于识别媒体文件格式                        |

### 🏗️ 系统架构

LeafView采用经典的三层架构设计，确保系统的高内聚、低耦合和良好的可扩展性。

```
┌─────────────────────────────────────────────────────────────┐
│                    枫叶相册 - LeafView                      │
├─────────────────────────────────────────────────────────────┤
│                    用户界面层 (UI Layer)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 主窗口      │ │ 智能整理    │ │ 去重对比    │ │ EXIF编辑 │ │
│  │ MainWindow  │ │ SmartArrange│ │RemoveDupli..│ │WriteExif │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│  ┌─────────────┐ ┌─────────────┐                         │
│  │ 文字识别    │ │ 设置对话框  │                         │
│  │TextRecogni..│ │SettingsDial.│                         │
│  └─────────────┘ └─────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│                    业务逻辑层 (Business Layer)              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 文件夹管理  │ │ 整理线程    │ │ 去重线程    │ │ EXIF线程│ │
│  │ AddFolder   │ │SmartArrange.│ │RemoveDupli..│ │WriteExif│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│  ┌─────────────┐ ┌─────────────┐                         │
│  │ 识别线程    │ │ 更新检查    │                         │
│  │TextRecogni..│ │UpdateDialog │                         │
│  └─────────────┘ └─────────────┘                         │
├─────────────────────────────────────────────────────────────┤
│                    数据处理层 (Data Layer)                  │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────┐ │
│  │ 图像处理    │ │ EXIF数据    │ │ 哈希计算    │ │ OCR引擎 │ │
│  │   Pillow    │ │   piexif    │ │   感知哈希  │ │tesseract│ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────┘ │
│  ┌─────────────┐ ┌─────────────┐                         │
│  │ 配置管理    │ │ 公共工具    │                         │
│  │configManager│ │   common    │                         │
│  └─────────────┘ └─────────────┘                         │
└─────────────────────────────────────────────────────────────┘
```

#### 🔧 架构设计特点

**1. 用户界面层 (UI Layer)**
- **模块化设计**: 每个功能模块有独立的UI组件，便于维护和扩展
- **响应式布局**: 支持不同屏幕尺寸和分辨率，提供一致的用户体验
- **主题系统**: 支持明暗主题切换，用户可自定义界面样式
- **国际化支持**: 内置多语言支持框架，便于本地化

**2. 业务逻辑层 (Business Layer)**
- **多线程架构**: 所有耗时操作都在独立线程中执行，确保UI响应性
- **任务队列管理**: 智能管理并发任务，避免资源冲突和性能瓶颈
- **状态管理**: 统一的状态管理机制，确保数据一致性和可预测性
- **错误处理**: 完善的异常处理机制，提供友好的错误提示和恢复选项

**3. 数据处理层 (Data Layer)**
- **格式抽象**: 统一的接口处理不同图像格式，屏蔽底层差异
- **缓存优化**: 多级缓存策略（内存缓存、磁盘缓存）优化性能
- **数据持久化**: 配置和状态数据自动持久化，支持恢复上次操作
- **外部服务集成**: 标准化接口集成地图服务、OCR服务等外部API

#### 🚀 核心线程模型

LeafView采用生产者-消费者模式管理多线程任务：

- **主线程**: 负责UI渲染和用户交互，保持轻量和响应迅速
- **工作线程**: 执行耗时操作（图像处理、文件IO、网络请求）
- **线程通信**: 通过信号-槽机制实现线程间安全通信
- **资源管理**: 智能线程池管理，避免创建过多线程导致性能下降

#### 📊 数据流设计

```
用户操作 → UI事件 → 业务逻辑处理 → 数据处理 → 外部服务
    ↑           ↓           ↓           ↓           ↓
状态更新 ← 进度反馈 ← 结果返回 ← 数据缓存 ← API响应
```

这种数据流设计确保了:
- **单向数据流**: 数据流动方向清晰，便于调试和维护
- **状态隔离**: UI状态与业务数据分离，提高代码可测试性
- **异步处理**: 所有耗时操作异步执行，不阻塞用户界面
- **错误边界**: 错误在适当层级被捕获和处理，避免影响整体稳定性

## 🌟 核心功能

### 📷 **图片管理**
- **多格式支持**：JPG、PNG、HEIC、TIFF、BMP、WEBP、GIF等主流图片格式
- **文件夹导入**：支持拖拽操作，可递归导入子文件夹
- **缩略图预览**：高效生成和缓存缩略图，支持快速浏览
- **大图查看**：高质量图像渲染，支持缩放和导航
- **媒体类型检测**：自动识别文件类型，过滤非媒体文件

**技术实现:**
- **格式检测算法**: 使用文件魔数和扩展名双重验证确保格式识别准确性
- **缩略图缓存**: LRU缓存策略优化内存使用，支持动态调整缓存大小
- **渐进式加载**: 大图片采用渐进式加载技术，避免界面卡顿
- **EXIF方向自动校正**: 自动识别并校正相机拍摄方向，确保图片正确显示

### 🧹 **智能整理**
- **多级分类结构**：支持按年份、月份、日期、星期、时间、品牌、位置等多维度分类
- **自定义文件夹结构**：灵活配置分类层级，满足不同整理需求
- **批量重命名**：支持多种命名规则和分隔符，可组合使用多种标签
- **文件操作**：支持移动或复制到目标目录，保留原始文件结构
- **实时预览**：整理前预览目标路径结构，避免误操作
- **操作确认**：执行前提供详细操作说明和确认机制

**技术实现:**
- **多线程递归遍历**: SmartArrangeThread实现高效的文件夹扫描和文件处理
- **动态分类引擎**: 支持运行时动态加载和组合分类规则
- **智能路径构建**: 自动处理路径长度限制和非法字符过滤
- **冲突解决算法**: 智能检测和解决文件名冲突，支持多种重命名策略
- **GPS逆地理编码**: 集成高德地图API，将GPS坐标转换为详细地址信息用于分类

### 🔍 **去重功能**
- **智能检测**：基于感知哈希算法检测重复图片
- **相似度控制**：可调节相似度阈值，从完全一致到部分相似
- **可视化展示**：相似图片分组展示，直观对比
- **批量操作**：支持批量选择和操作（移动、删除）重复图片
- **安全删除**：使用回收站机制，防止误删重要文件
- **多线程处理**：提高处理性能，支持大量图片处理

**技术实现:**
- **dHash感知哈希算法**: ImageHasher类实现64位差异哈希，对旋转和缩放具有鲁棒性
- **汉明距离计算**: 精确计算图像相似度，支持可调节阈值
- **优化分组算法**: _optimized_grouping()方法实现高效的相似图片分组
- **多线程对比引擎**: ContrastWorker类管理多线程并行处理，大幅提升处理速度
- **内存映射技术**: 使用内存映射处理大文件，减少内存占用

### 📝 **EXIF编辑**
- **全面元数据支持**：查看和编辑图片EXIF信息
- **星级评分系统**：1-5星评分，便于图片筛选和管理
- **设备信息编辑**：支持修改相机品牌、型号、镜头等信息
- **时间调整**：修改拍摄日期和时间，支持批量调整
- **地理位置**：编辑GPS坐标信息，支持反向地理编码
- **批量处理**：一次性处理多张图片，提高效率

**技术实现:**
- **多格式EXIF处理**: WriteExifThread支持JPEG、PNG、WEBP、HEIC、RAW等多种格式
- **格式特定插件**: 不同格式使用专用处理模块（_jpeg_process, _process_png_format等）
- **GPS数据处理**: _create_gps_data()方法处理坐标格式转换和验证
- **批量操作优化**: 支持大量文件的批量EXIF编辑，具有事务性保证
- **错误恢复机制**: 写入失败时自动回滚，确保文件完整性

### 🔤 **文字识别**
- **OCR引擎**：基于Tesseract的高精度文字识别
- **多语言支持**：支持中文、英文等多种语言识别
- **批量处理**：一次识别多张图片中的文字
- **智能整理**：根据识别的文字内容自动分类整理
- **结果导出**：支持复制或保存识别结果
- **进度显示**：实时显示识别进度和统计信息

**技术实现:**
- **Tesseract集成**: 通过subprocess调用Tesseract OCR引擎，支持多语言识别
- **图像预处理**: 自动进行灰度化、二值化、降噪等预处理操作提高识别率
- **多线程识别**: 支持并行处理多张图片，大幅提升识别速度
- **结果后处理**: 对识别结果进行智能分段和格式整理，提高可读性
- **关键词提取**: 从识别文本中提取关键信息用于智能分类和整理

### ⚙️ **系统功能**
- **单例模式**：确保同一时间只有一个应用实例运行
- **自动更新**：内置更新检查机制，及时获取最新版本
- **设置管理**：个性化配置界面，自定义使用体验
- **日志记录**：详细操作日志，便于问题排查
- **无边框界面**：现代化UI设计，支持自定义主题

## 💻 安装部署

详细的安装说明请参考独立的 [安装指南](installation_guide.md) 文档，其中包含完整的环境要求、依赖安装步骤、多平台部署方法和常见问题解决方案。
### 📋 系统要求
- Python 3.11 或更高版本
- Windows/macOS/Linux 操作系统
- 至少 2GB RAM（推荐 4GB 或更多）
- 支持 OpenGL 的图形硬件

### 🚀 快速安装

#### 1. 克隆仓库
```bash
git clone https://github.com/YangShengzhou03/LeafView.git
cd LeafView
```

#### 2. 创建虚拟环境（推荐）
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 运行应用
```bash
python App.py
```

### ⚙️ 环境配置注意事项
- **Tesseract OCR**: 对于文字识别功能，需要安装 Tesseract OCR 引擎并配置环境变量
- **ffmpeg**: 对于视频处理功能，需要安装 ffmpeg
- **系统权限**: 确保应用有足够的文件系统权限来访问和管理图片文件

## 📁 目录结构

LeafView 项目采用清晰的目录结构组织代码和资源，便于维护和扩展：

```
LeafView/
├── App.py              # 应用程序入口文件
├── common.py           # 通用功能和工具函数
├── main_window.py      # 主窗口实现
├── resources/          # 资源文件目录
│   ├── img/            # 图标和图片资源
│   ├── stylesheet/     # CSS样式表
│   ├── cv2_date/       # 日期识别相关资源
│   ├── exiftool/       # EXIF工具
│   └── json/           # 配置和数据文件
├── requirements.txt    # 项目依赖列表
├── LeafView_version_info.txt  # 版本信息
├── README.md           # 项目说明文档
├── installation_guide.md      # 安装指南文档
└── comprehensive_guide.md     # 综合使用指南文档

```
LeafView/
├── App.py                 # 应用程序入口
├── main_window.py         # 主窗口实现
├── Ui_MainWindow.py       # UI界面生成文件
├── Ui_MainWindow.ui       # Qt Designer UI设计文件
├── add_folder.py          # 文件夹添加功能
├── smart_arrange.py       # 智能整理功能
├── smart_arrange_thread.py # 智能整理线程
├── remove_duplication.py  # 文件去重功能
├── remove_duplication_thread.py # 去重处理线程
├── write_exif.py          # EXIF属性写入功能
├── write_exif_thread.py   # EXIF写入线程
├── contrast_thread.py     # 对比处理线程
├── read_thread.py         # 读取处理线程
├── update_dialog.py       # 更新对话框
├── UI_UpdateDialog.py     # 更新对话框UI
├── UI_UpdateDialog.ui     # 更新对话框UI设计
├── config_manager.py      # 配置管理
├── common.py              # 公共工具函数
├── requirements.txt       # 项目依赖
├── README.md              # 项目文档
├── license.txt            # 许可证文件
├── .gitignore             # Git忽略文件
└── resources/             # 资源文件夹
    ├── img/               # 图像资源
    ├── exiftool/          # ExifTool工具
    ├── cv2_date/          # OpenCV日期处理
    └── json/              # JSON配置文件
```

## 📖 使用说明

详细的使用指南请参考独立的 [综合使用指南](comprehensive_guide.md) 文档，其中包含完整的功能介绍、操作步骤、快捷键说明和高级功能使用方法。
### 📷 图片浏览
1. 启动应用程序
2. 通过菜单栏或工具栏导入图片文件夹或单个图片文件
3. 在左侧文件列表中选择图片进行预览
4. 使用鼠标滚轮或键盘方向键浏览多张图片

### 🧹 智能整理
1. 选择要整理的图片文件夹
2. 在侧边栏选择"智能整理"功能
3. 设置整理规则（按日期、地点、格式等）
4. 预览整理结果
5. 确认并执行整理操作

### 🔍 文件去重
1. 选择要检查的文件夹
2. 在侧边栏选择"文件去重"功能
3. 设置相似度阈值
4. 等待扫描完成
5. 查看重复文件组并选择处理方式

### 📝 属性写入
1. 选择要修改EXIF属性的图片
2. 在侧边栏选择"属性写入"功能
3. 编辑或添加EXIF信息
4. 预览修改效果
5. 确认并保存修改

## ⚠️ 注意事项
- 请在执行文件整理、重命名和属性写入等操作前备份重要数据
- 大量图片处理可能需要较长时间，请耐心等待
- 部分功能（如OCR文字识别）需要额外安装第三方软件
- 应用采用单例模式设计，同一时间只能运行一个实例

### 🔧 环境准备
- **操作系统**：Windows 10/11、macOS 10.14+、Linux (Ubuntu 18.04+)
- **Python**：3.8 及以上版本
- **内存**：建议 4GB 以上 RAM
- **存储**：至少 500MB 可用空间
- **其他**：Tesseract OCR引擎（用于文字识别功能）

### 🚀 安装步骤

#### 方法一：从源码安装

1. **克隆项目到本地环境**
   ```bash
   git clone https://github.com/YangShengzhou03/LeafView.git
   cd LeafView
   ```

2. **创建虚拟环境（推荐）**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **安装Tesseract OCR（文字识别功能需要）**
   
   **Windows:**
   ```bash
   # 下载并安装Tesseract-OCR
   # https://github.com/UB-Mannheim/tesseract/wiki
   # 确保将Tesseract添加到系统PATH环境变量中
   ```
   
   **macOS:**
   ```bash
   brew install tesseract
   brew install tesseract-lang  # 安装语言包
   ```
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install tesseract-ocr
   sudo apt install libtesseract-dev  # 开发文件
   ```

5. **运行应用程序**
   ```bash
   python App.py
   ```

#### 方法二：使用预编译可执行文件

1. **下载最新版本**
   - 访问 [GitHub Releases](https://github.com/YangShengzhou03/LeafView/releases) 页面
   - 下载对应操作系统的最新版本安装包

2. **安装应用程序**
   - **Windows**: 运行 `.exe` 安装程序，按提示完成安装
   - **macOS**: 打开 `.dmg` 文件，将应用拖拽到应用程序文件夹
   - **Linux**: 解压 `.tar.gz` 文件，运行其中的可执行文件

### 📦 打包为可执行文件

如果您需要自行打包应用程序，可以使用PyInstaller：

```bash
# 安装PyInstaller
pip install pyinstaller

# 打包应用程序
pyinstaller App.spec

# 打包完成后，可执行文件位于dist目录中
```

### 🔧 常见问题解决

1. **导入错误：ModuleNotFoundError**
   ```bash
   # 确保所有依赖已正确安装
   pip install -r requirements.txt --upgrade
   ```

2. **OCR功能无法使用**
   ```bash
   # 确保Tesseract OCR已正确安装并添加到PATH
   # Windows下检查Tesseract安装路径
   where tesseract
   
   # 验证Tesseract是否可用
   tesseract --version
   ```

3. **HEIC/HEIF格式图片无法打开**
   ```bash
   # 确保pillow-heif已正确安装
   pip install pillow-heif --upgrade
   ```

## 📖 使用说明

### 🔑 基本操作

1. **启动程序**
   - 从源码运行：执行 `python App.py`
   - 从可执行文件运行：双击应用程序图标

2. **导入文件夹**
   - 点击界面上的"导入文件夹"按钮
   - 或直接拖拽文件夹到程序窗口
   - 可选择是否包含子文件夹

3. **浏览图片**
   - 在左侧导航栏选择功能模块
   - 在主界面浏览图片
   - 使用缩略图或大图模式查看

### 📝 功能使用

#### 1. **智能整理**

智能整理功能可以帮助您按照多种规则自动整理图片文件，基于先进的算法和逻辑实现高效的文件管理。

**操作步骤:**
1. 选择要整理的文件夹
2. 设置分类结构（最多5级分类）
3. 选择文件名结构和分隔符
4. 选择操作类型（移动或复制）
5. 点击"开始整理"按钮执行操作

**分类选项:**
- **时间分类**：年份、月份、日期、星期、时间
- **设备分类**：相机品牌、相机型号
- **位置分类**：拍摄地点（需要GPS信息）
- **自定义分类**：根据用户需求自定义分类规则

**文件名标签:**
- **原文件名**：保留原始文件名
- **时间标签**：年份、月份、日期、星期、时间
- **设备标签**：品牌、型号
- **位置标签**：拍摄地点
- **自定义标签**：用户自定义文本

**操作类型:**
- **移动**：将文件移动到新位置，原位置不再保留
- **复制**：在新位置创建文件副本，原文件保留

#### 🔍 技术实现细节

**文件整理逻辑:**
- **递归遍历**: 支持包含子文件夹的深度扫描，使用多线程优化遍历性能
- **智能过滤**: 自动识别并跳过系统文件、临时文件和无效媒体文件
- **元数据提取**: 从EXIF、IPTC、XMP等多种元数据标准中提取完整信息

**重命名逻辑原理:**
- **动态模板**: 支持灵活的命名模板系统，可组合时间、设备、位置等变量
- **冲突处理**: 自动检测文件名冲突并添加序号后缀（_1, _2, ...）
- **路径构建**: 智能构建文件夹路径，确保路径长度不超过系统限制
- **编码处理**: 正确处理Unicode文件名和多语言字符集

**GPS逆地理编码处理:**
- **坐标提取**: 从EXIF GPS标签提取经纬度坐标（度分秒格式和十进制格式）
- **格式转换**: 自动转换度分秒格式为十进制格式便于API调用
- **高德API集成**: 调用高德地图逆地理编码API获取详细地址信息
- **智能缓存**: 使用带容差的位置缓存机制，避免重复API调用
- **离线支持**: 内置省市地理编码数据库，支持离线位置识别

**分类算法:**
- **多级分类**: 支持最多5级嵌套分类结构
- **条件组合**: 支持AND/OR逻辑组合多个分类条件
- **自定义规则**: 用户可定义复杂的分类规则和优先级

#### 2. **去重操作**

去重功能可以帮助您查找并处理重复或相似的图片，基于先进的感知哈希算法实现高效的图像对比。

**操作步骤:**
1. 选择要检查重复的文件夹
2. 调整相似度阈值滑块（0-100%）
3. 点击"开始对比"查找重复图片
4. 查看分组结果，选择要处理的图片
5. 选择操作类型（移动或删除）

**相似度级别:**
- **完全一致 (100%)**：文件完全相同
- **高度相似 (75-99%)**：内容几乎相同，可能有轻微压缩差异
- **部分相似 (50-74%)**：内容相似，但有明显差异
- **略有相似 (25-49%)**：只有部分内容相似
- **巨大差异 (0-24%)**：相似度很低

**批量操作:**
- **自动选择**：根据规则自动选择重复图片
- **移动**：将选中的图片移动到指定文件夹
- **删除**：将选中的图片移至回收站

#### 🔍 技术实现细节

**图像对比算法:**
- **dHash感知哈希**: 使用差异哈希算法生成64位图像指纹
- **汉明距离计算**: 通过计算哈希值之间的汉明距离确定相似度
- **多分辨率处理**: 支持不同尺寸和分辨率的图像对比
- **格式无关**: 可处理JPEG、PNG、WEBP等多种图像格式

**优化策略:**
- **分组优化**: 使用_optimized_grouping()方法对相似图片进行智能分组
- **多线程处理**: ContrastWorker类实现多线程并行对比，大幅提升处理速度
- **内存优化**: 使用生成器处理大型图像集合，减少内存占用
- **缓存机制**: 哈希值缓存避免重复计算，提升对比效率

**相似度阈值:**
- **可调节阈值**: 支持0-100%的精细相似度调节
- **智能推荐**: 根据图像特性自动推荐最佳阈值
- **实时预览**: 对比过程中实时显示相似度结果

**批量处理能力:**
- **大规模处理**: 支持数万张图片的批量去重操作
- **增量处理**: 支持在已有结果基础上进行增量对比
- **断点续传**: 处理过程中断后可恢复进度

#### 3. **EXIF编辑**

EXIF编辑功能允许您查看和修改图片的元数据信息，支持多种图像格式和高级编辑操作。

**操作步骤:**
1. 选择要编辑EXIF信息的图片
2. 设置各项EXIF参数
3. 点击"应用"保存更改

**可编辑项目:**
- **星级评分**：1-5星评分
- **相机信息**：品牌、型号、镜头信息
- **拍摄时间**：日期和时间
- **地理位置**：经纬度坐标
- **其他参数**：曝光、光圈、ISO等

**批量处理:**
1. 选择多张图片
2. 设置要修改的EXIF项
3. 点击"批量应用"按钮
4. 确认操作并等待处理完成

#### 🔍 技术实现细节

**EXIF写入逻辑:**
- **格式兼容**: 支持JPEG、PNG、WEBP、HEIC、TIFF等多种格式
- **元数据保留**: 编辑时保留原始元数据结构和未修改的标签
- **数据验证**: 对输入的EXIF数据进行格式和范围验证
- **错误恢复**: 写入失败时自动恢复原始文件状态

**不同格式处理插件:**
- **JPEG/WEBP处理**: 使用piexif库进行原生EXIF操作，支持完整的EXIF、GPS、IPTC、XMP元数据
- **PNG格式处理**: 使用Pillow库处理PNG文本元数据，支持关键信息的读写操作
- **HEIC/HEIF处理**: 集成pillow-heif库，支持苹果格式的完整元数据编辑
- **RAW格式处理**: 使用rawpy库读取RAW文件元数据，支持专业相机格式
- **视频文件处理**: 通过exiftool命令行工具处理视频文件的元数据

**GPS数据处理:**
- **坐标格式转换**: 支持度分秒格式与十进制格式的相互转换
- **地址解析**: 通过高德地图API将文本地址转换为GPS坐标
- **IP定位**: 支持通过IP地址获取大致地理位置信息
- **批量地理编码**: 支持大量图片的批量地理位置处理

**高级特性:**
- **操作摘要**: 生成详细的编辑操作日志和统计信息
- **撤销重做**: 支持多步操作的撤销和重做功能
- **模板应用**: 支持将EXIF设置保存为模板并批量应用
- **时间调整**: 支持相对时间调整（如所有图片时间+1小时）

#### 4. **文字识别**

文字识别功能可以从图片中提取文字内容，并根据文字内容进行整理。

**操作步骤：**
1. 选择包含文字的图片
2. 点击"识别图片文字"按钮
3. 等待识别完成
4. 查看识别结果
5. 可选择"按文字整理"进行分类

**识别选项：**
- **语言选择**：中文、英文或多语言混合
- **预处理**：自动优化图像以提高识别率
- **批量处理**：一次识别多张图片

**整理选项：**
- **按内容分类**：根据识别的文字内容创建文件夹
- **关键词提取**：自动提取关键词作为分类依据
- **自定义规则**：用户可自定义分类规则

### ⚙️ **设置选项**

通过设置对话框，您可以自定义应用程序的行为：

1. **界面设置**
   - 主题颜色
   - 语言选择
   - 界面缩放

2. **功能设置**
   - 默认操作类型
   - 相似度阈值
   - 文件命名规则

3. **高级设置**
   - 缓存大小
   - 线程数量
   - 日志级别

## 📁 目录结构
```
LeafView/
├── AddFolder.py               # 文件夹导入功能
├── App.py                     # 应用程序入口，实现单例模式
├── App.spec                   # PyInstaller打包配置
├── MainWindow.py              # 主窗口实现，协调各功能模块
├── RemoveDuplication.py       # 去重功能界面
├── RemoveDuplicationThread.py # 去重功能线程处理
├── SmartArrange.py            # 智能整理功能界面
├── SmartArrangeThread.py      # 智能整理功能线程处理
├── TextRecognition.py         # 文字识别功能
├── Ui_MainWindow.py           # UI界面代码（自动生成）
├── Ui_MainWindow.ui           # UI设计文件
├── WriteExif.py               # EXIF编辑功能界面
├── WriteExifThread.py         # EXIF编辑功能线程处理
├── common.py                  # 公共函数和工具
├── config_manager.py          # 配置管理器
├── requirements.txt           # 项目依赖
├── SettingsDialog.py          # 设置对话框
├── UpdateDialog.py            # 更新检查对话框
├── UI_UpdateDialog.py         # UI更新对话框
└── resources/                 # 资源文件夹
    ├── img/                   # 图片资源
    │   ├── icon.ico           # 应用程序图标
    │   ├── page_0/            # 页面0资源
    │   ├── page_1/            # 页面1资源
    │   ├── page_2/            # 页面2资源
    │   ├── page_3/            # 页面3资源
    │   ├── page_4/            # 页面4资源
    │   ├── 头标/              # 标题栏资源
    │   └── 窗口控制/          # 窗口控制按钮资源
    ├── json/                  # JSON配置文件
    │   ├── camera_brand_model.json      # 相机品牌型号数据
    │   ├── camera_lens_mapping.json     # 相机镜头映射数据
    │   ├── lens_model.json             # 镜头型号数据
    │   ├── City_Reverse_Geocode.json    # 城市反向地理编码数据
    │   └── Province_Reverse_Geocode.json # 省份反向地理编码数据
    ├── cv2_date/              # OpenCV相关资源
    │   └── haarcascade_frontalface_alt2.xml  # 人脸检测级联文件
    └── stylesheet/            # 样式表
        ├── author.dialog.setStyleSheet.css  # 作者对话框样式
        └── close_button.setStyleSheet.css    # 关闭按钮样式
```

## 🤝 参与贡献
我们欢迎所有开发者参与项目改进与功能扩展，共同提升系统质量。贡献流程如下：

1. **Fork 仓库**：将项目复制到个人GitHub空间
2. **创建特性分支**：基于main分支创建新分支，命名规范建议使用"feat/功能名称"或"fix/问题描述"
3. **提交规范化代码**：遵循项目代码风格，提交信息使用规范格式（如"feat: 添加图片批量旋转功能"）
4. **推送分支**：将本地分支推送到个人远程仓库
5. **创建 Pull Request**：提交合并请求到原仓库，描述修改内容与目的，等待审核

### 👥 核心贡献者

[![Contributors](https://contrib.rocks/image?repo=YangShengzhou03/LeafView)](https://github.com/YangShengzhou03/LeafView/graphs/contributors)

### 💖 特别鸣谢
感谢以下开发者为项目做出的贡献：

- **UI/UX 设计团队** - 提供精美的界面设计和用户体验优化
- **测试团队** - 进行全面的功能测试和性能优化
- **社区贡献者** - 提供宝贵的反馈和建议
- **开源项目** - 感谢以下开源项目为本项目提供支持：
  - [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI框架
  - [Pillow](https://python-pillow.org/) - 图像处理库
  - [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) - OCR引擎
  - [PyInstaller](https://www.pyinstaller.org/) - 打包工具

### 🎯 贡献指南

#### 代码规范
- 遵循 PEP 8 Python 代码风格指南
- 使用有意义的变量名和函数名
- 添加适当的注释和文档字符串
- 确保代码通过静态检查工具（如flake8、pylint）
- 函数和类应包含完整的文档字符串，说明参数和返回值

#### 提交信息规范
```
类型(范围): 简短描述

详细描述（可选）

BREAKING CHANGE: 重大变更说明（可选）
```

**类型说明**:
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具变动

**范围说明**:
- `ui`: 用户界面相关更改
- `core`: 核心功能相关更改
- `perf`: 性能优化相关更改
- `docs`: 文档相关更改

#### 开发环境设置
1. 克隆项目到本地
2. 创建并激活虚拟环境
3. 安装开发依赖：`pip install -r requirements.txt`
4. 安装开发工具：`pip install flake8 pylint pytest`
5. 运行代码检查：`flake8 .` 和 `pylint *.py`
6. 运行测试：`pytest tests/`

#### 功能开发流程
1. 在GitHub Issues中创建新的功能请求或确认现有问题
2. 基于main分支创建功能分支：`git checkout -b feat/feature-name`
3. 开发功能并编写测试
4. 确保所有测试通过：`pytest`
5. 提交代码并推送到个人仓库
6. 创建Pull Request并关联对应的Issue

## 📜 开源许可
本项目采用 [MIT License](https://opensource.org/licenses/MIT) 授权。

### 📋 许可证条款
```
MIT License

Copyright (c) 2024 YangShengzhou03

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

### 🔒 知识产权声明
- 项目代码采用MIT许可证，允许自由使用、修改和分发
- 项目图标和界面设计受版权保护，仅限本项目使用
- 第三方库和资源遵循各自的许可证条款
- 用户生成的内容（图片、数据等）所有权归用户所有

---

## 🔄 更新日志

### v1.0.0 (2024-XX-XX)
#### ✨ 新增功能
- 初始版本发布
- 实现基本的图片浏览和管理功能
- 智能整理功能：支持按时间、设备等多维度分类
- 去重功能：基于感知哈希算法检测重复图片
- EXIF编辑功能：查看和修改图片元数据
- 文字识别功能：基于Tesseract OCR引擎
- 单例模式：确保同一时间只有一个应用实例运行

#### 🐛 修复问题
- 修复HEIC/HEIF格式图片无法打开的问题
- 修复大文件处理时的内存泄漏问题
- 修复多线程处理中的竞态条件

#### 🚀 性能优化
- 优化缩略图生成和缓存机制
- 改进大批量文件处理性能
- 减少内存占用，提高运行稳定性

#### 📝 文档更新
- 完善用户手册和使用说明
- 添加开发者贡献指南
- 更新API文档和代码注释

---

## 🚀 性能指标

### ⚡ 处理速度
| 操作类型 | 处理速度 | 备注 |
|----------|----------|------|
| 缩略图生成 | 100-500 张/秒 | 取决于图片大小和硬件性能 |
| 去重对比 | 50-200 张/秒 | 基于感知哈希算法 |
| EXIF读取 | 200-1000 张/秒 | 批量处理效率更高 |
| OCR识别 | 1-10 张/秒 | 取决于文字复杂度和图片质量 |

### 💾 内存占用
| 场景 | 内存使用 | 说明 |
|------|----------|------|
| 空载状态 | 50-100 MB | 仅运行主界面 |
| 浏览1000张图片 | 200-500 MB | 包含缩略图缓存 |
| 批量处理任务 | 500-1000 MB | 取决于处理文件数量 |
| 峰值使用 | 1-2 GB | 极端情况下的大批量处理 |

### 📊 文件格式支持
| 格式类型 | 支持程度 | 备注 |
|----------|----------|------|
| JPEG/JPG | ✅ 完全支持 | 标准图片格式 |
| PNG | ✅ 完全支持 | 透明通道支持 |
| HEIC/HEIF | ✅ 完全支持 | 需要pillow-heif库 |
| TIFF | ✅ 完全支持 | 多页TIFF支持 |
| WEBP | ✅ 完全支持 | 动画WEBP支持 |
| GIF | ✅ 完全支持 | 动画GIF支持 |
| BMP | ✅ 完全支持 | Windows位图格式 |
| RAW格式 | ⚠️ 部分支持 | 依赖系统解码器 |
| MP4 | ✅ 完全支持 | 视频缩略图生成 |
| MOV | ✅ 完全支持 | QuickTime格式 |

---

## 🔧 开发指南

### 🏗️ 项目架构详解

#### 核心模块设计

LeafView采用模块化设计，每个核心功能都有独立的线程和处理类：

```python
# 应用程序入口 - 单例模式实现
class App(QtWidgets.QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setQuitOnLastWindowClosed(False)
        
    def check_instance(self):
        """检查是否已有实例运行 - 基于进程锁的单例模式"""
        # 使用系统级进程锁确保单实例运行
        self.lock_file = os.path.join(tempfile.gettempdir(), "leafview.lock")
        try:
            self.lock_fd = os.open(self.lock_file, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        except OSError:
            # 已有实例运行
            return False
        return True
```

#### 线程管理模型

LeafView使用统一的工作线程基类，提供标准的进度报告和错误处理机制：

```python
# 基础工作线程类 - 所有耗时操作的基类
class BaseWorkerThread(QtCore.QThread):
    progress_updated = QtCore.pyqtSignal(int, int, str)  # 当前进度, 总数, 状态信息
    task_completed = QtCore.pyqtSignal(list)            # 完成的任务结果列表
    error_occurred = QtCore.pyqtSignal(str)             # 错误信息
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_running = True  # 线程运行状态控制
        self._mutex = QtCore.QMutex()  # 线程安全互斥锁
    
    def stop(self):
        """安全停止线程"""
        with QtCore.QMutexLocker(self._mutex):
            self._is_running = False
    
    def is_running(self):
        """检查线程是否正在运行"""
        with QtCore.QMutexLocker(self._mutex):
            return self._is_running
```

#### GPS逆地理编码处理逻辑

```python
def reverse_geocode(self, latitude, longitude):
    """GPS逆地理编码处理 - 将坐标转换为地址信息"""
    
    # 1. 坐标格式验证和转换
    if isinstance(latitude, str) and "°" in latitude:
        # 度分秒格式转换: 31°13'49.02"N → 31.230283
        latitude = self._convert_dms_to_decimal(latitude)
    
    # 2. 位置缓存检查（带容差）
    cache_key = f"{round(latitude, 4)}_{round(longitude, 4)}"
    cached_location = self.location_cache.get(cache_key)
    if cached_location:
        return cached_location
    
    # 3. 调用高德地图API进行逆地理编码
    try:
        url = f"https://restapi.amap.com/v3/geocode/regeo?output=json&location={longitude},{latitude}&key={self.amap_key}&radius=1000&extensions=all"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data['status'] == '1' and data['regeocode']:
            address = data['regeocode']['formatted_address']
            # 缓存结果
            self.location_cache[cache_key] = address
            return address
    
    except Exception as e:
        print(f"逆地理编码失败: {e}")
    
    # 4. 离线回退 - 使用内置地理编码数据库
    return self._offline_reverse_geocode(latitude, longitude)
```

#### 图像对比算法实现

```python
class ImageHasher:
    """感知哈希算法实现 - 基于dHash差异哈希"""
    
    def __init__(self, hash_size=8):
        self.hash_size = hash_size
    
    def dhash(self, image):
        """计算图像的dHash值"""
        # 1. 图像预处理：灰度化+缩放
        image = image.convert('L').resize((self.hash_size + 1, self.hash_size))
        
        pixels = list(image.getdata())
        
        # 2. 计算差异哈希
        difference = []
        for row in range(self.hash_size):
            for col in range(self.hash_size):
                left_pixel = pixels[row * (self.hash_size + 1) + col]
                right_pixel = pixels[row * (self.hash_size + 1) + col + 1]
                difference.append(left_pixel > right_pixel)
        
        # 3. 转换为64位整数哈希值
        return sum([2 ** i for i, bit in enumerate(difference) if bit])
    
    def hamming_distance(self, hash1, hash2):
        """计算两个哈希值的汉明距离"""
        return bin(hash1 ^ hash2).count('1')
    
    def similarity(self, hash1, hash2):
        """计算相似度百分比"""
        distance = self.hamming_distance(hash1, hash2)
        max_distance = self.hash_size * self.hash_size
        return (1 - distance / max_distance) * 100
```

#### 多格式EXIF处理架构

```python
def process_image(self, file_path):
    """多格式EXIF处理主入口"""
    
    # 1. 文件格式检测
    file_ext = os.path.splitext(file_path)[1].lower()
    
    # 2. 根据格式调用相应的处理插件
    if file_ext in ['.jpg', '.jpeg', '.webp']:
        return self._jpeg_process(file_path)
    elif file_ext == '.png':
        return self._process_png_format(file_path)
    elif file_ext in ['.heic', '.heif']:
        return self._process_heic_format(file_path)
    elif file_ext in ['.cr2', '.nef', '.arw', '.dng']:
        return self._process_raw_format(file_path)
    elif file_ext in ['.mp4', '.mov', '.avi']:
        return self._process_video_format(file_path)
    else:
        raise ValueError(f"不支持的格式: {file_ext}")

def _jpeg_process(self, file_path):
    """JPEG/WEBP格式处理 - 使用piexif库"""
    try:
        exif_dict = piexif.load(file_path)
        
        # 更新EXIF数据
        if self.rating is not None:
            exif_dict['0th'][piexif.ImageIFD.Rating] = self.rating
        
        # 保存修改
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, file_path)
        return True
        
    except Exception as e:
        self.error_occurred.emit(f"处理JPEG文件失败: {str(e)}")
        return False

def _process_raw_format(self, file_path):
    """RAW格式处理 - 使用rawpy和exiftool组合"""
    try:
        # 使用rawpy读取元数据
        with rawpy.imread(file_path) as raw:
            metadata = raw.metadata
        
        # 使用exiftool写入修改
        cmd = ['exiftool', f'-Rating={self.rating}', file_path]
        subprocess.run(cmd, check=True, capture_output=True)
        return True
        
    except (rawpy.LibRawFileUnsupportedError, subprocess.CalledProcessError) as e:
        self.error_occurred.emit(f"处理RAW文件失败: {str(e)}")
        return False
```

### 🎯 扩展开发示例

#### 自定义整理规则实现

LeafView提供灵活的规则引擎，支持基于正则表达式、文件属性和内容的自定义整理规则：

```python
# 自定义整理规则基类
class BaseArrangeRule:
    """整理规则基类 - 所有自定义规则必须继承此类"""
    
    def __init__(self, priority=10):
        self.priority = priority  # 规则优先级，数值越小优先级越高
        self.enabled = True
    
    def match(self, file_info):
        """匹配文件信息，返回是否匹配此规则"""
        raise NotImplementedError("子类必须实现match方法")
    
    def get_target_path(self, file_info, base_dir):
        """获取文件的目标路径"""
        raise NotImplementedError("子类必须实现get_target_path方法")

# 正则表达式文件名匹配规则
class RegexFilenameRule(BaseArrangeRule):
    """基于正则表达式的文件名匹配规则"""
    
    def __init__(self, pattern, target_template, priority=10):
        super().__init__(priority)
        self.pattern = re.compile(pattern, re.IGNORECASE)
        self.target_template = target_template  # 目标路径模板
    
    def match(self, file_info):
        """匹配文件名"""
        filename = os.path.basename(file_info['path'])
        return bool(self.pattern.search(filename))
    
    def get_target_path(self, file_info, base_dir):
        """生成目标路径"""
        filename = os.path.basename(file_info['path'])
        match = self.pattern.search(filename)
        
        # 使用匹配组填充模板
        target_path = self.target_template
        if match.groups():
            for i, group in enumerate(match.groups(), 1):
                target_path = target_path.replace(f'${i}', group or '')
        
        return os.path.join(base_dir, target_path, filename)

# EXIF元数据匹配规则
class ExifMetadataRule(BaseArrangeRule):
    """基于EXIF元数据的整理规则"""
    
    def __init__(self, exif_field, value_pattern, target_template, priority=5):
        super().__init__(priority)
        self.exif_field = exif_field  # EXIF字段，如'DateTimeOriginal'
        self.value_pattern = re.compile(value_pattern, re.IGNORECASE)
        self.target_template = target_template
    
    def match(self, file_info):
        """匹配EXIF元数据"""
        if 'exif' not in file_info or self.exif_field not in file_info['exif']:
            return False
        
        exif_value = file_info['exif'][self.exif_field]
        return bool(self.value_pattern.search(str(exif_value)))
    
    def get_target_path(self, file_info, base_dir):
        """基于EXIF数据生成路径"""
        exif_value = file_info['exif'][self.exif_field]
        
        # 处理日期时间格式
        if self.exif_field in ['DateTimeOriginal', 'DateTime', 'DateTimeDigitized']:
            # 将"2023:12:25 15:30:45"转换为"2023/12/25"
            date_str = str(exif_value).split()[0].replace(':', '/')
            target_path = self.target_template.replace('{date}', date_str)
        else:
            target_path = self.target_template.replace('{value}', str(exif_value))
        
        filename = os.path.basename(file_info['path'])
        return os.path.join(base_dir, target_path, filename)

# GPS位置规则
class GpsLocationRule(BaseArrangeRule):
    """基于GPS位置的整理规则"""
    
    def __init__(self, location_pattern, target_template, priority=3):
        super().__init__(priority)
        self.location_pattern = re.compile(location_pattern, re.IGNORECASE)
        self.target_template = target_template
        self.geocoder = ReverseGeocoder()
    
    def match(self, file_info):
        """匹配GPS位置信息"""
        if 'gps' not in file_info or not file_info['gps']:
            return False
        
        # 获取地址信息
        address = self.geocoder.reverse_geocode(
            file_info['gps']['latitude'], 
            file_info['gps']['longitude']
        )
        return bool(self.location_pattern.search(address))
    
    def get_target_path(self, file_info, base_dir):
        """基于位置信息生成路径"""
        address = self.geocoder.reverse_geocode(
            file_info['gps']['latitude'], 
            file_info['gps']['longitude']
        )
        
        # 简化地址信息（提取省市信息）
        simplified_address = self._simplify_address(address)
        target_path = self.target_template.replace('{location}', simplified_address)
        
        filename = os.path.basename(file_info['path'])
        return os.path.join(base_dir, target_path, filename)
```

#### 云存储集成实现

LeafView支持多种云存储服务的集成，提供统一的接口：

```python
# 云存储基类
class CloudStorageBase:
    """云存储服务基类"""
    
    def __init__(self, config):
        self.config = config
        self.connected = False
    
    def connect(self):
        """连接到云存储服务"""
        raise NotImplementedError("子类必须实现connect方法")
    
    def upload_file(self, local_path, remote_path, callback=None):
        """上传文件"""
        raise NotImplementedError("子类必须实现upload_file方法")
    
    def download_file(self, remote_path, local_path, callback=None):
        """下载文件"""
        raise NotImplementedError("子类必须实现download_file方法")
    
    def list_files(self, remote_prefix=""):
        """列出文件"""
        raise NotImplementedError("子类必须实现list_files方法")

# AWS S3 集成
class AwsS3Storage(CloudStorageBase):
    """AWS S3 云存储集成"""
    
    def __init__(self, config):
        super().__init__(config)
        self.client = None
        self.bucket = config.get('bucket', '')
    
    def connect(self):
        """连接到AWS S3"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.config['access_key'],
                aws_secret_access_key=self.config['secret_key'],
                region_name=self.config.get('region', 'us-east-1')
            )
            self.client = session.client('s3')
            self.connected = True
            
            # 验证连接和桶权限
            self.client.head_bucket(Bucket=self.bucket)
            return True
            
        except (ClientError, NoCredentialsError) as e:
            print(f"AWS S3连接失败: {e}")
            return False
    
    def upload_file(self, local_path, remote_path, callback=None):
        """分块上传文件到S3"""
        if not self.connected:
            self.connect()
        
        try:
            # 计算文件大小用于进度回调
            file_size = os.path.getsize(local_path)
            uploaded = 0
            
            # 使用分块上传支持大文件
            with open(local_path, 'rb') as file_data:
                self.client.upload_fileobj(
                    file_data, 
                    self.bucket, 
                    remote_path,
                    Callback=lambda bytes_transferred: self._update_progress(bytes_transferred, file_size, callback)
                )
            
            return True
            
        except Exception as e:
            print(f"S3上传失败: {e}")
            return False
    
    def _update_progress(self, bytes_transferred, total_size, callback):
        """更新上传进度"""
        if callback:
            progress = min(100, int((bytes_transferred / total_size) * 100))
            callback(progress)

# 阿里云OSS集成
class AliyunOssStorage(CloudStorageBase):
    """阿里云OSS存储集成"""
    
    def __init__(self, config):
        super().__init__(config)
        self.client = None
        self.bucket = None
    
    def connect(self):
        """连接到阿里云OSS"""
        try:
            auth = oss2.Auth(
                self.config['access_key_id'], 
                self.config['access_key_secret']
            )
            self.bucket = oss2.Bucket(
                auth, 
                self.config['endpoint'], 
                self.config['bucket_name']
            )
            self.connected = True
            return True
            
        except Exception as e:
            print(f"阿里云OSS连接失败: {e}")
            return False
    
    def upload_file(self, local_path, remote_path, callback=None):
        """断点续传上传到OSS"""
        if not self.connected:
            self.connect()
        
        try:
            # 使用断点续传功能
            oss2.resumable_upload(
                self.bucket, 
                remote_path, 
                local_path,
                progress_callback=lambda progress: callback(progress) if callback else None
            )
            return True
            
        except Exception as e:
            print(f"OSS上传失败: {e}")
            return False
```

### 🔌 插件系统架构

#### 插件接口定义与实现

LeafView采用模块化的插件系统，支持动态加载和卸载插件：

```python
# 插件基类 - 所有插件必须继承此类
class LeafViewPlugin:
    """LeafView插件基类"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.plugin_name = "未命名插件"
        self.plugin_version = "1.0.0"
        self.plugin_description = "插件描述"
        self.plugin_author = "未知作者"
        self.plugin_config = {}  # 插件配置存储
    
    def initialize(self):
        """插件初始化 - 在插件加载时调用"""
        # 注册插件到主窗口
        self.main_window.register_plugin(self)
        
        # 加载插件配置
        self._load_config()
        
        # 创建插件菜单和工具栏
        self._create_ui_elements()
    
    def get_menu_items(self):
        """返回插件菜单项列表"""
        return []
    
    def get_toolbar_buttons(self):
        """返回插件工具栏按钮列表"""
        return []
    
    def get_settings_widget(self):
        """返回插件设置面板"""
        return None
    
    def cleanup(self):
        """插件清理 - 在插件卸载时调用"""
        # 保存插件配置
        self._save_config()
        
        # 清理UI元素
        self._cleanup_ui_elements()
    
    def _load_config(self):
        """加载插件配置"""
        config_path = os.path.join(
            self.main_window.get_plugin_config_dir(), 
            f"{self.plugin_name}.json"
        )
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.plugin_config = json.load(f)
            except Exception as e:
                print(f"加载插件配置失败: {e}")
    
    def _save_config(self):
        """保存插件配置"""
        config_path = os.path.join(
            self.main_window.get_plugin_config_dir(), 
            f"{self.plugin_name}.json"
        )
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.plugin_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存插件配置失败: {e}")
    
    def _create_ui_elements(self):
        """创建插件UI元素"""
        # 创建菜单项
        menu_items = self.get_menu_items()
        for menu_path, action_name, callback in menu_items:
            self._add_menu_item(menu_path, action_name, callback)
        
        # 创建工具栏按钮
        toolbar_buttons = self.get_toolbar_buttons()
        for button_text, icon_path, callback in toolbar_buttons:
            self._add_toolbar_button(button_text, icon_path, callback)
    
    def _cleanup_ui_elements(self):
        """清理插件UI元素"""
        # 由主窗口负责清理注册的UI元素
        self.main_window.unregister_plugin(self)
```

#### 高级插件实现示例

```python
# 高级图片处理插件示例
class AdvancedFilterPlugin(LeafViewPlugin):
    """高级图片处理插件 - 支持批量处理和预设管理"""
    
    def __init__(self, main_window):
        super().__init__(main_window)
        self.plugin_name = "高级图片滤镜"
        self.plugin_version = "2.0.0"
        self.plugin_description = "提供高级图片滤镜效果和批量处理功能"
        self.plugin_author = "LeafView Team"
        
        # 滤镜预设
        self.filter_presets = {
            'vintage': {
                'brightness': 0.9,
                'contrast': 1.1,
                'saturation': 0.8,
                'vignette': True
            },
            'cinematic': {
                'brightness': 0.8,
                'contrast': 1.2,
                'saturation': 0.7,
                'vignette': True
            }
        }
    
    def initialize(self):
        super().initialize()
        
        # 创建滤镜处理工作线程
        self.filter_thread = FilterWorkerThread()
        self.filter_thread.progress_updated.connect(self._on_filter_progress)
        self.filter_thread.task_completed.connect(self._on_filter_complete)
    
    def get_menu_items(self):
        """返回插件菜单项"""
        return [
            ("滤镜/批量处理", "批量应用滤镜", self.batch_apply_filters),
            ("滤镜/预设/复古", "应用复古预设", lambda: self.apply_preset('vintage')),
            ("滤镜/预设/电影", "应用电影预设", lambda: self.apply_preset('cinematic')),
            ("滤镜/自定义", "自定义滤镜设置", self.open_filter_settings)
        ]
    
    def get_toolbar_buttons(self):
        """返回工具栏按钮"""
        return [
            ("批量滤镜", "filter_icon.png", self.batch_apply_filters),
            ("滤镜设置", "settings_icon.png", self.open_filter_settings)
        ]
    
    def get_settings_widget(self):
        """返回插件设置面板"""
        settings_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout()
        
        # 亮度调节滑块
        brightness_label = QtWidgets.QLabel("亮度:")
        brightness_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        brightness_slider.setRange(0, 200)
        brightness_slider.setValue(100)
        brightness_slider.valueChanged.connect(self._on_brightness_changed)
        
        layout.addWidget(brightness_label)
        layout.addWidget(brightness_slider)
        settings_widget.setLayout(layout)
        
        return settings_widget
    
    def batch_apply_filters(self):
        """批量应用滤镜到选中的图片"""
        selected_files = self.main_window.get_selected_files()
        if not selected_files:
            QtWidgets.QMessageBox.warning(self.main_window, "警告", "请先选择要处理的图片")
            return
        
        # 弹出滤镜选择对话框
        filter_dialog = FilterSelectionDialog(self.filter_presets, self.main_window)
        if filter_dialog.exec_() == QtWidgets.QDialog.Accepted:
            selected_preset = filter_dialog.get_selected_preset()
            
            # 启动批量处理
            self.filter_thread.process_files(selected_files, selected_preset)
    
    def apply_preset(self, preset_name):
        """应用预设滤镜"""
        current_image = self.main_window.get_current_image()
        if current_image:
            preset = self.filter_presets.get(preset_name, {})
            filtered_image = self._apply_filter(current_image, preset)
            self.main_window.update_image(filtered_image)
    
    def open_filter_settings(self):
        """打开滤镜设置对话框"""
        settings_dialog = FilterSettingsDialog(self.filter_presets, self.main_window)
        settings_dialog.exec_()
    
    def _apply_filter(self, image, filter_config):
        """应用单个滤镜"""
        # 实现具体的滤镜算法
        from PIL import ImageEnhance, ImageFilter
        
        # 亮度调整
        if 'brightness' in filter_config:
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(filter_config['brightness'])
        
        # 对比度调整
        if 'contrast' in filter_config:
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(filter_config['contrast'])
        
        # 饱和度调整
        if 'saturation' in filter_config:
            enhancer = ImageEnhance.Color(image)
            image = enhancer.enhance(filter_config['saturation'])
        
        # 暗角效果
        if filter_config.get('vignette', False):
            image = self._apply_vignette(image)
        
        return image
    
    def _apply_vignette(self, image):
        """应用暗角效果"""
        width, height = image.size
        center_x, center_y = width // 2, height // 2
        max_distance = math.sqrt(center_x**2 + center_y**2)
        
        # 创建暗角遮罩
        vignette = Image.new('L', (width, height), 255)
        draw = ImageDraw.Draw(vignette)
        
        for x in range(width):
            for y in range(height):
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                intensity = int(255 * (1 - distance / max_distance * 0.5))
                draw.point((x, y), intensity)
        
        # 应用暗角效果
        return Image.composite(image, Image.new(image.mode, image.size, 'black'), vignette)
    
    def _on_filter_progress(self, current, total, filename):
        """处理进度更新"""
        self.main_window.update_status(f"正在处理: {filename} ({current}/{total})")
    
    def _on_filter_complete(self, results):
        """处理完成"""
        success_count = sum(1 for result in results if result['success'])
        self.main_window.update_status(f"批量处理完成: {success_count}/{len(results)} 成功")
        
        if success_count < len(results):
            QtWidgets.QMessageBox.warning(self.main_window, "处理结果", 
                                        f"成功处理 {success_count} 个文件，失败 {len(results) - success_count} 个")
```

#### 插件管理器实现

```python
class PluginManager:
    """插件管理器 - 负责插件的加载、卸载和管理"""
    
    def __init__(self, main_window):
        self.main_window = main_window
        self.loaded_plugins = {}  # 已加载的插件
        self.plugin_dir = os.path.join(os.path.dirname(__file__), 'plugins')
    
    def load_plugins(self):
        """加载所有可用插件"""
        if not os.path.exists(self.plugin_dir):
            os.makedirs(self.plugin_dir)
            return
        
        # 扫描插件目录
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                plugin_name = filename[:-3]  # 移除.py扩展名
                try:
                    self.load_plugin(plugin_name)
                except Exception as e:
                    print(f"加载插件 {plugin_name} 失败: {e}")
    
    def load_plugin(self, plugin_name):
        """加载单个插件"""
        if plugin_name in self.loaded_plugins:
            print(f"插件 {plugin_name} 已加载")
            return
        
        try:
            # 动态导入插件模块
            spec = importlib.util.spec_from_file_location(
                plugin_name, 
                os.path.join(self.plugin_dir, f"{plugin_name}.py")
            )
            plugin_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(plugin_module)
            
            # 查找插件类（约定插件类名与文件名相同）
            plugin_class = getattr(plugin_module, plugin_name, None)
            if plugin_class and issubclass(plugin_class, LeafViewPlugin):
                # 实例化插件
                plugin_instance = plugin_class(self.main_window)
                plugin_instance.initialize()
                
                self.loaded_plugins[plugin_name] = plugin_instance
                print(f"插件 {plugin_name} 加载成功")
            else:
                print(f"在插件 {plugin_name} 中未找到合适的插件类")
                
        except Exception as e:
            print(f"加载插件 {plugin_name} 时发生错误: {e}")
            raise
    
    def unload_plugin(self, plugin_name):
        """卸载插件"""
        if plugin_name in self.loaded_plugins:
            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()
            del self.loaded_plugins[plugin_name]
            print(f"插件 {plugin_name} 已卸载")
    
    def get_plugin(self, plugin_name):
        """获取指定插件实例"""
        return self.loaded_plugins.get(plugin_name)
    
    def get_all_plugins(self):
        """获取所有已加载插件"""
        return list(self.loaded_plugins.values())
    
    def reload_plugin(self, plugin_name):
        """重新加载插件"""
        self.unload_plugin(plugin_name)
        self.load_plugin(plugin_name)
```

### 📚 API参考

#### 配置文件管理 API
```python
# 配置管理器使用示例
from config_manager import config_manager

# 读取配置
folders = config_manager.get_folders()
settings = config_manager.get_settings()

# 更新配置
config_manager.update_setting('theme', 'dark')
config_manager.save_config()

# 管理文件夹列表
config_manager.add_folder('/path/to/folder', include_sub=True)
config_manager.remove_folder('/path/to/folder')
config_manager.clear_folders()

# 位置缓存管理
config_manager.get_location_cache()
config_manager.update_location_cache('key', 'value')
config_manager.clear_location_cache()
```

#### 媒体文件检测 API
```python
# 文件类型检测示例
from common import detect_media_type

result = detect_media_type('image.jpg')
print(f"文件类型: {result['type']}")
print(f"MIME类型: {result['mime']}")
print(f"扩展名: {result['extension']}")
print(f"是否有效: {result['valid']}")
print(f"扩展名匹配: {result['extension_match']}")

# 支持的媒体类型检测
SUPPORTED_IMAGE_FORMATS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic']
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.flac', '.aac']
```

#### 图像处理 API
```python
# 使用Pillow进行图像处理示例
from PIL import Image, ImageFilter, ImageEnhance

def process_image(image_path, operations):
    """应用多种图像处理操作"""
    with Image.open(image_path) as img:
        for operation in operations:
            if operation == 'rotate':
                img = img.rotate(90)
            elif operation == 'resize':
                img = img.resize((800, 600))
            elif operation == 'filter':
                img = img.filter(ImageFilter.BLUR)
            elif operation == 'enhance':
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
        return img
```

#### EXIF数据处理 API
```python
# EXIF数据读写示例
import piexif
from PIL import Image

def read_exif_data(image_path):
    """读取图片的EXIF数据"""
    try:
        exif_dict = piexif.load(image_path)
        return exif_dict
    except Exception as e:
        print(f"读取EXIF数据失败: {e}")
        return None

def write_exif_data(image_path, exif_dict):
    """写入EXIF数据到图片"""
    try:
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, image_path)
        return True
    except Exception as e:
        print(f"写入EXIF数据失败: {e}")
        return False
```

#### 多线程处理 API
```python
# 自定义工作线程示例
from PyQt6.QtCore import QThread, pyqtSignal

class CustomWorkerThread(QThread):
    progress_updated = pyqtSignal(int, int, str)  # 当前进度, 总数, 状态信息
    task_completed = pyqtSignal(list)  # 完成的任务结果
    error_occurred = pyqtSignal(str)  # 错误信息
    
    def __init__(self, task_data, parent=None):
        super().__init__(parent)
        self.task_data = task_data
        self.is_running = True
    
    def run(self):
        """线程执行逻辑"""
        try:
            total = len(self.task_data)
            results = []
            
            for i, item in enumerate(self.task_data):
                if not self.is_running:
                    break
                    
                # 处理单个任务项
                result = self.process_item(item)
                results.append(result)
                
                # 发送进度更新信号
                progress_percent = int((i + 1) / total * 100)
                self.progress_updated.emit(i + 1, total, f"处理中: {progress_percent}%")
            
            self.task_completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))
    
    def process_item(self, item):
        """处理单个任务项的具体逻辑"""
        # 实现具体的处理逻辑
        return {"status": "success", "data": item}
    
    def stop(self):
        """停止线程"""
        self.is_running = False
```

### 🧪 测试指南

#### 单元测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定模块测试
pytest tests/test_image_processing.py -v

# 生成测试覆盖率报告
pytest --cov=. tests/
```

#### 性能测试
```bash
# 内存使用分析
python -m memory_profiler main.py

# CPU性能分析
python -m cProfile -o profile_stats main.py
```

### 🚀 最佳实践与性能优化

#### 内存管理最佳实践
```python
# 使用上下文管理器处理图像资源
from contextlib import contextmanager
from PIL import Image

@contextmanager
def safe_image_processing(image_path):
    """安全的图像处理上下文管理器"""
    img = None
    try:
        img = Image.open(image_path)
        yield img
    finally:
        if img:
            img.close()

# 使用示例
with safe_image_processing('large_image.jpg') as img:
    # 处理图像
    thumbnail = img.resize((200, 200))
    thumbnail.save('thumbnail.jpg')
```

#### 批量处理优化
```python
# 使用生成器处理大型文件集合
def batch_process_files(file_paths, batch_size=100):
    """分批处理文件，减少内存占用"""
    for i in range(0, len(file_paths), batch_size):
        batch = file_paths[i:i + batch_size]
        yield batch
        
        # 显式清理内存
        import gc
        gc.collect()

# 使用示例
all_files = ['image1.jpg', 'image2.jpg', ...]  # 大量文件
for batch in batch_process_files(all_files, batch_size=50):
    process_batch(batch)
```

#### 缓存策略优化
```python
# 使用LRU缓存优化重复操作
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_image_metadata_cached(image_path):
    """带缓存的图像元数据获取"""
    return get_image_metadata(image_path)  # 昂贵的操作

# 使用内存映射处理大文件
import mmap

def process_large_file(file_path):
    """使用内存映射处理大文件"""
    with open(file_path, 'rb') as f:
        with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
            # 处理映射的内存
            process_mapped_data(mm)
```

#### 并发处理优化
```python
# 使用线程池处理IO密集型任务
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_files_concurrently(file_paths, max_workers=4):
    """并发处理多个文件"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # 提交所有任务
        future_to_file = {
            executor.submit(process_single_file, file_path): file_path 
            for file_path in file_paths
        }
        
        # 收集结果
        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append((file_path, result))
            except Exception as e:
                print(f"处理文件 {file_path} 时出错: {e}")
    
    return results
```

#### 数据库优化
```python
# 使用批量插入优化数据库操作
import sqlite3

def batch_insert_images(conn, image_data_list):
    """批量插入图像数据到数据库"""
    cursor = conn.cursor()
    
    try:
        # 开始事务
        cursor.execute('BEGIN TRANSACTION')
        
        # 批量插入
        cursor.executemany('''
            INSERT OR REPLACE INTO images 
            (path, size, modified_time, metadata) 
            VALUES (?, ?, ?, ?)
        ''', image_data_list)
        
        # 提交事务
        conn.commit()
        
    except Exception as e:
        # 回滚事务
        conn.rollback()
        raise e
```

#### 错误处理与重试机制
```python
# 实现带指数退避的重试机制
import time
from functools import wraps

def retry_with_backoff(max_retries=3, initial_delay=1, backoff_factor=2):
    """带指数退避的重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            delay = initial_delay
            
            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries == max_retries:
                        raise e
                    
                    print(f"重试 {retries}/{max_retries}，等待 {delay} 秒后重试...")
                    time.sleep(delay)
                    delay *= backoff_factor
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# 使用示例
@retry_with_backoff(max_retries=5, initial_delay=2)
def download_file(url, destination):
    """下载文件，失败时自动重试"""
    # 下载逻辑
    pass
```

#### 性能监控与分析
```python
# 使用性能分析装饰器
import time
from functools import wraps

def profile_performance(func):
    """性能分析装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        print(f"函数 {func.__name__} 执行时间: {end_time - start_time:.4f} 秒")
        return result
    return wrapper

## 📊 性能优化建议

### 🔧 常见性能问题
- **大量图片处理时的性能优化**：建议分批处理大型图片集合
- **内存占用优化**：可在设置中调整缓存大小以平衡性能和内存使用
- **启动速度优化**：减少不必要的启动时加载项
```

---

## 🆘 故障排除

### 🔍 常见问题解答

#### Q: 程序启动时报错 "ModuleNotFoundError"
**A:** 确保所有依赖已正确安装：
```bash
pip install -r requirements.txt --upgrade
```

#### Q: HEIC/HEIF格式图片无法打开
**A:** 安装pillow-heif库：
```bash
pip install pillow-heif --upgrade
```

#### Q: OCR文字识别功能无法使用
**A:** 确保Tesseract OCR已正确安装：
```bash
# Windows
where tesseract

# macOS/Linux
which tesseract
```

#### Q: 处理大量图片时内存占用过高
**A:** 调整缓存设置或分批处理：
- 在设置中减少缓存大小
- 分批导入文件夹进行处理
- 增加系统虚拟内存

#### Q: 程序界面显示异常或乱码
**A:** 尝试以下解决方案：
- 检查系统语言和区域设置
- 重新安装PyQt6库
- 清除应用程序缓存

### 📋 错误代码参考

| 错误代码 | 描述 | 解决方案 |
|----------|------|----------|
| ERR-001 | 文件不存在或无法访问 | 检查文件路径和权限 |
| ERR-002 | 不支持的文件格式 | 安装相应的解码器库 |
| ERR-003 | 内存不足 | 减少处理批量或增加内存 |
| ERR-004 | 磁盘空间不足 | 清理磁盘空间 |
| ERR-005 | 网络连接失败 | 检查网络设置 |
| ERR-006 | 权限被拒绝 | 以管理员权限运行 |
| ERR-007 | 依赖库缺失 | 重新安装依赖库 |
| ERR-008 | 配置文件损坏 | 删除配置文件重新生成 |

---

## 🤝 社区支持

### 📞 联系方式

#### 开发者信息
- **作者**: YangShengzhou03
- **邮箱**: [通过GitHub Issues联系]
- **GitHub**: [https://github.com/YangShengzhou03](https://github.com/YangShengzhou03)

#### 技术支持
- 📧 **问题反馈**: [GitHub Issues](https://github.com/YangShengzhou03/LeafView/issues)
- 💬 **讨论区**: [GitHub Discussions](https://github.com/YangShengzhou03/LeafView/discussions)
- 🐛 **Bug报告**: [提交Bug报告](https://github.com/YangShengzhou03/LeafView/issues/new?template=bug_report.md)
- 💡 **功能请求**: [请求新功能](https://github.com/YangShengzhou03/LeafView/issues/new?template=feature_request.md)

#### 社交媒体
- 🌐 **博客**: [CSDN博客](https://blog.csdn.net/Yang_shengzhou)
- 💬 **QQ群**: [扫码联系开发者](resources/img/activity/QQ_名片.png)
- 📱 **微信公众号**: 即将开通

### 🌟 如何获取帮助

1. **查阅文档**: 首先查看本文档和[Wiki页面](https://github.com/YangShengzhou03/LeafView/wiki)
2. **搜索问题**: 在[Issues](https://github.com/YangShengzhou03/LeafView/issues)中搜索类似问题
3. **提交问题**: 如果找不到解决方案，提交新的Issue
4. **加入社区**: 参与Discussions分享经验和技巧

### 🎯 商业支持

本项目主要依靠社区维护，如需商业技术支持或定制开发，请联系开发者。

---

<div align="center">
  <p>
    <strong>🍁 枫叶相册 - 让图片管理更简单 🍁</strong>
  </p>
  <p>
    如果这个项目对您有帮助，请给个 ⭐ Star 支持一下！
  </p>
  
  <p>
    <a href="https://github.com/YangShengzhou03/LeafView/stargazers">
      <img src="https://img.shields.io/github/stars/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=ffd33d&labelColor=000000" alt="GitHub Stars">
    </a>
    <a href="https://github.com/YangShengzhou03/LeafView/forks">
      <img src="https://img.shields.io/github/forks/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=green&labelColor=000000" alt="GitHub Forks">
    </a>
    <a href="https://github.com/YangShengzhou03/LeafView/issues">
      <img src="https://img.shields.io/github/issues/YangShengzhou03/LeafView?style=for-the-badge&logo=github&color=purple&labelColor=000000" alt="GitHub Issues">
    </a>
    <a href="https://github.com/YangShengzhou03/LeafView/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=open-source-initiative&color=blue&labelColor=000000" alt="MIT License">
    </a>
  </p>
  
  <p>
    <sub>Built with ❤️ using Python and PyQt6</sub>
  </p>
</div>

```
MIT License

Copyright (c) 2024 YangShengzhou03

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🔄 更新日志

### v1.0.0 (2024-XX-XX)
#### ✨ 新增功能
- 初始版本发布
- 实现基本的图片浏览和管理功能
- 智能整理功能：支持按时间、设备等多维度分类
- 去重功能：基于感知哈希算法检测重复图片
- EXIF编辑功能：查看和修改图片元数据
- 文字识别功能：基于Tesseract OCR引擎
- 单例模式：确保同一时间只有一个应用实例运行

#### 🐛 修复问题
- 修复HEIC/HEIF格式图片无法打开的问题
- 修复大文件处理时的内存泄漏问题
- 修复多线程处理中的竞态条件

#### 🚀 性能优化
- 优化缩略图生成和缓存机制
- 改进大批量文件处理性能
- 减少内存占用，提高运行稳定性

#### 📝 文档更新
- 完善用户手册和使用说明
- 添加开发者贡献指南
- 更新API文档和代码注释

---

<div align="center">
  <sub>Built with ❤️ using Python and PyQt6</sub>
</div>

从提供的网页内容及相关搜索结果来看，Eagle 是一款专为设计师、摄影师等创作人群打造的数字资产管理软件，核心定位是解决海量素材（图片、视频、设计文件等）的 “收集 - 整理 - 检索” 全流程效率问题，同时兼顾稳定性、兼容性与个性化操作，支持 macOS 和 Windows 双平台，且持续通过版本更新优化功能体验。
一、核心定位与核心价值
Eagle 的核心价值在于替代传统 “文件夹混乱管理” 模式，通过智能化、自动化工具减少素材管理的重复操作，让创作者将时间聚焦于设计本身而非 “找素材”，尤其适合素材量庞大（如数千 / 数万张图片、设计源文件）的场景，是设计师的 “数字素材第二大脑”。
二、详细功能拆解
根据网页更新日志及搜索结果，Eagle 的功能可分为 6 大核心模块，覆盖素材管理全流程：
模块 1：高效素材收集（解决 “怎么存” 的问题）
核心目标是 “无门槛、快速捕获各类素材”，支持多种收集方式，突破传统保存限制：
网页素材采集
浏览器插件（支持 Chrome、Firefox 等）：可一键采集网页全部图片，或手动拖拽单张图片；对设置 “禁止保存” 的网站（如 Instagram、500px），通过快捷键 Alt+右键 直接破解限制保存。
网页长截图 / 区域截图：插件支持截取整个网页（含滚动内容）或指定区域，截图后直接存入 Eagle 素材库，无需先存本地再导入。
本地 / 跨应用收集
拖拽添加：从桌面、文件夹或其他应用（如 Photoshop、浏览器）直接拖拽素材到 Eagle，自动导入并保留文件属性。
剪贴板粘贴：复制图片（如从聊天软件、文档中复制）后，直接粘贴到 Eagle，跳过 “下载 - 找路径” 步骤。
截图 / 录屏：Eagle 内置截图功能，后台运行时可快速启动，截图 / 录屏后直接存入素材库（补充设备原生录屏功能的不足）。
第三方平台导入
支持从花瓣网、Inboard 等设计素材平台批量导入图片，迁移旧素材库更便捷。
模块 2：智能素材整理（解决 “怎么分类” 的问题）
核心目标是 “结构化管理素材，避免混乱”，提供手动 + 自动结合的整理工具：
分层级文件夹体系
普通文件夹：支持多层级创建（如 “设计素材→Logo→科技风”），可自定义文件夹图标、名称，还能设置密码保护（双图层保护，支持快捷键快速锁定，忘记密码可通过序列号恢复），保护敏感素材。
智能文件夹（核心功能）：按 “规则自动筛选素材”，类似 iTunes 智能播放列表。例如设置规则 “格式 = PNG + 尺寸 > 1920px”，智能文件夹会实时从全库中抓取符合条件的素材，且后续新增的 PNG 大图会自动归类，无需手动移动。
标签与自动化标记
手动标签：为单张 / 多张素材添加标签（如 “扁平风”“banner”），支持批量标签操作；
自动标签：为文件夹设置 “默认标签”，后续导入该文件夹的所有素材会自动带上标签（如 “Logo 文件夹” 默认标签 “Logo”，避免重复打标）。
素材标注与备注
内置标注工具：直接在图片上框选、添加文字注释（记录灵感或修改意见），不破坏原图本身，方便团队协作或个人回顾。
“动作” 自动化（进阶功能）
通过 “动作” 功能将重复操作一键化：例如设置 “动作 = 添加标签‘电商’+ 移动到‘电商素材’文件夹”，并绑定快捷键，选中素材后按快捷键即可完成两步操作，支持批量处理（如批量打标、批量归类、批量评分）。
模块 3：精准高效检索（解决 “怎么找” 的问题）
核心目标是 “0.5 秒定位素材”，提供多维度检索工具，覆盖 “已知条件” 和 “模糊需求”：
基础检索：关键词 + 快捷键
快捷键 J（Windows）/ Command+J（macOS）呼出快速搜索框，支持搜索 “文件名、标签、备注、来源网址”，模糊匹配（如输入 “ban” 可找到 “banner” 相关素材）。
高级筛选：多条件组合
支持按 “格式（PSD/AI/PNG 等）、尺寸（如 1080P/4K）、颜色（如红色系素材）、时间（导入日期）、评分（1-5 星）、标签” 等条件组合筛选。例如 “格式 = PSD + 颜色 = 蓝色 + 评分≥4 星”，快速定位高质量蓝色 PSD 素材。
视觉筛选：颜色与预览
颜色筛选：点击色卡即可筛选含该颜色的素材（如找 “橙色主色调的海报”），适合忘记关键词但记得视觉特征的场景；
多格式预览：无需打开原软件，直接在 Eagle 中预览 PSD、AI、Word、PPT、MP4 等文件（支持 59+ 格式），避免 “逐个打开验证内容” 的麻烦。
快速切换：跨文件夹检索
支持在普通文件夹、智能文件夹、标签分类间快速切换，无需反复跳转路径，尤其适合跨分类找素材（如同时查看 “电商素材” 文件夹和 “橙色系” 标签下的素材）。
模块 4：素材处理与导出（解决 “怎么用” 的问题）
核心目标是 “减少跨软件操作”，内置轻量处理工具，满足基础设计需求：
内置图片编辑器
支持 “旋转、裁剪、翻转”，无需打开 Photoshop，快速调整素材尺寸或方向，适合临时处理（如裁剪截图、调整图片比例）。
批量导出与格式转换
选中单张 / 多张素材，右键选择 “导出”，可自定义 “格式（如 PNG 转 JPG）、尺寸（如压缩至 1080P）、质量（如 80% 清晰度）”，支持批量操作（如批量将 100 张 PSD 导出为 JPG），节省手动转换时间。
RAW 文件支持
优化 RAW 格式（相机原始文件）的验证机制，确保 RAW 文件导入后可预览、可管理，适合摄影师整理相机素材。
模块 5：多设备同步与隐私安全（解决 “怎么跨设备用” 的问题）
灵活同步方案
不强制绑定云服务，支持将素材库放在 “本地硬盘 + 第三方云盘”（如 iCloud、Dropbox、坚果云），云盘同步后，多台设备（如办公室电脑 + 家用电脑）的 Eagle 可实时访问最新素材，适合多设备办公。
隐私与安全
素材默认存储在本地，不强制上传云端，保护商业素材或个人隐私；
双重安全：文件夹密码保护 + 应用锁定（快捷键锁定 Eagle），防止他人查看敏感素材。
模块 6：个性化与稳定性（解决 “用得爽” 的问题）
个性化操作设置
鼠标滚轮自定义：支持 “垂直滚动、页面翻转、直接缩放” 三种模式，切换快捷键即可匹配不同操作习惯（如设计时用 “直接缩放” 精准查看细节，浏览时用 “页面翻转” 快速翻页）；
灰度模式：快捷键切换灰度视图，帮助设计师检查 “视觉层级” 和 “黑白稿兼容性”（如确保印刷品在黑白模式下仍清晰）；
子文件夹视图：一键切换 “仅查看当前文件夹” 或 “查看当前文件夹 + 所有子文件夹”，适合需要 “全局浏览” 或 “聚焦单个子文件夹” 的场景；
150+ 自定义快捷键：支持自定义 “截图、搜索、导出、标签” 等所有操作的快捷键，适配不同用户的操作习惯。
持续稳定性优化（版本更新）
从 V4.0 到 V5.0 的更新中，重点修复 “文件夹重命名 bug、macOS 系统兼容性（如 macOS Sequoia）、快捷键冲突、RAW 文件验证” 等问题，提升操作流畅度（如解决 macOS 聚焦卡顿）；
V5.0 预告加入 AI 功能（AI 搜索、AI Action、Eagle MCP），将从 “手动管理” 升级为 “智能管理”（如 AI 自动打标签、AI 识别素材内容并分类）。
三、版本与价格信息
版本支持：双平台（macOS + Windows），持续更新（最新 V4.0 Build14-16，2025 年 10 月发布；V5.0 为预告版本，主打 AI 功能）；
试用与付费：30 天免费试用，付费为 “终身 license”（199 元 / 2 台设备），支持序列号激活，忘记密码可通过序列号恢复；
替代方案：若需免费工具，可考虑 Connecter（界面英文，功能较基础），但 Eagle 功能更全面且适合专业场景。
四、适合人群
Eagle 核心服务于创作型用户，尤其适合：
设计师（UI/UX、电商、平面设计等）：管理大量设计源文件、参考图；
摄影师：整理 RAW 格式照片、分类作品集；
内容创作者（自媒体、视频博主）：管理封面图、视频素材、文案文档；
团队协作：多人共享素材库，通过标签和标注提升协作效率。
综上，Eagle 不是简单的 “图片管理器”，而是一套 “从素材收集到最终使用” 的全流程效率工具，通过 “自动化 + 精准化 + 个性化” 解决创作人群的核心痛点，是目前设计领域口碑较高的数字资产管理软件之一。

6 篇资料
他的本地功能是怎样的
Eagle 作为主打 “本地优先” 的数字资产管理软件，其本地功能围绕素材的本地收集、整理、检索、处理及安全管理展开，核心优势是 “不依赖云端、响应速度快、数据自主掌控”，同时通过灵活设计兼容多场景本地使用需求，具体功能可拆解为以下 6 大模块：
一、本地素材收集：零门槛捕获各类本地 / 网页素材
Eagle 支持多种本地场景下的素材捕获方式，无需依赖云端同步即可完成 “从外部到本地素材库” 的快速导入，覆盖设计中常见的素材来源：
本地文件直接导入
拖拽添加：从电脑桌面、系统文件夹（如 “下载”“文档”）或其他应用（如 Photoshop、Figma）直接拖拽图片、视频、音频、字体文件（.ttf/.otf）等至 Eagle 窗口，自动存入本地资源库，无需手动选择保存路径；
剪贴板粘贴：从微信、QQ、文档中复制图片 / 文字后，直接在 Eagle 中 “粘贴”，素材会跳过 “本地保存” 步骤，直接写入资源库；
批量导入：支持选中多个本地文件（或整个文件夹）批量导入，导入时可选择 “保留原文件结构” 或 “合并到指定文件夹”，适合迁移旧素材库。
本地截图与录屏（无需第三方工具）
内置截图功能：通过自定义快捷键（如 Ctrl+Shift+A）快速启动截图，支持 “区域截图”“窗口截图”“全屏截图”，截图后可直接标注（添加文字、箭头）并保存到本地资源库，不依赖系统自带截图工具；
视频 / 音频捕获：若需收集本地屏幕操作（如教程片段），可启动内置录屏功能，录制完成后直接以视频格式（如 MP4）存入本地，同时支持捕获本地音频文件（如会议录音），无需额外转换格式。
突破限制的网页素材本地化
浏览器插件辅助：安装 Eagle 浏览器插件（支持 Chrome、Edge、Firefox）后，可一键将网页图片、视频链接（如 YouTube、Bilibili 视频）保存到本地资源库，即使网页设置 “禁止右键保存”，也可通过 Alt+右键 穿透限制，下载高清原图；
网页书签本地化：将常用设计网站（如 Behance、Dribbble）的链接保存为 “网页书签”，在 Eagle 本地直接预览链接缩略图，无需打开浏览器即可快速定位常用素材源。
二、本地素材整理：结构化管理，避免本地文件混乱
针对传统 “本地文件夹层层嵌套、素材难找” 的痛点，Eagle 提供多维度本地整理工具，让海量素材在本地形成有序体系：
分层级本地文件夹体系
普通文件夹：支持创建多层级本地文件夹（如 “设计素材→UI→登录页→扁平风”），可自定义文件夹图标、名称，还能设置本地密码保护（双图层加密，忘记密码可通过本地序列号恢复），保护本地敏感素材（如未公开的设计方案）；
智能文件夹（本地规则驱动）：基于 “本地筛选规则” 自动归类素材，类似 “本地智能筛选器”。例如设置规则 “格式 = PSD + 尺寸 > 1920px”，智能文件夹会实时从本地全库中抓取符合条件的素材，后续新增的 PSD 大图也会自动加入，无需手动移动文件，避免本地文件夹重复归类。
本地标签与自动化标记
手动标签：为单张 / 多张本地素材添加标签（如 “电商 banner”“科技风图标”），标签信息存储在本地资源库，不依赖云端，支持批量标签操作（如选中 100 张素材批量添加 “2024 项目” 标签）；
自动标签：为本地文件夹设置 “默认标签”（如 “Logo 文件夹” 默认标签 “Logo”），后续导入该文件夹的所有素材会自动带上标签，减少重复手动打标；
标签管理：本地标签支持 “分类分组”（如将 “风格类标签”“用途类标签” 分开管理），避免标签混乱，同时支持标签重命名、删除，操作仅影响本地资源库，不同步到其他设备（除非手动迁移）。
本地素材标注与备注
内置本地标注工具：直接在本地图片上添加文字注释、箭头、矩形框，标注内容与素材绑定存储在本地，不破坏原图文件，方便后续本地回顾（如记录设计灵感、修改意见），无需依赖外部标注软件（如 Snipaste）。
本地 “动作” 自动化：简化重复操作
通过 “动作” 功能将本地重复整理步骤一键化：例如设置 “动作 = 添加标签‘待优化’+ 移动到‘待处理’本地文件夹”，并绑定快捷键，选中素材后按快捷键即可完成两步操作，支持批量处理（如批量将本地素材打标、归类、评分），提升本地整理效率。
三、本地素材检索：0.5 秒定位本地素材，无需联网
Eagle 的检索功能完全基于本地数据运算，不依赖云端服务器，即使断网也能快速找到所需素材，核心检索方式包括：
本地关键词精准检索
快速搜索：通过快捷键（如 Ctrl+J）呼出本地搜索框，输入 “文件名、标签、备注、来源网址” 等关键词，0.5 秒内从本地资源库匹配结果，支持模糊搜索（如输入 “ban” 可找到 “banner” 相关素材）；
全维度匹配：检索范围覆盖本地素材的所有属性（如 “2024 年 5 月导入的 PNG 图”“带‘红色’标签的素材”），无需记住素材具体存储路径，解决传统本地文件夹 “记路径” 的痛点。
本地多条件筛选
基础筛选：支持按 “本地素材格式（PSD/AI/PNG 等）、尺寸（如 1080P/4K）、颜色（如红色系、蓝色系）、导入时间（如近 7 天）、星级评分（1-5 星）” 等条件组合筛选，例如 “格式 = PNG + 颜色 = 红色 + 评分≥4 星”，快速定位本地高质量红色 PNG 素材；
进阶筛选：针对特殊素材类型，支持 “字体是否已安装”（筛选本地已安装的字体文件）、“视频时长”（筛选本地短于 1 分钟的视频片段）、“音频 BPM”（筛选本地特定节奏的音频），满足细分场景需求。
本地视觉筛选：凭 “视觉记忆” 找素材
颜色筛选：点击本地色卡（如红色、蓝色），即可筛选含该颜色的本地素材，适合 “记得素材颜色但忘记关键词” 的场景（如 “找上次用的橙色按钮素材”）；
预览辅助：无需打开外部软件，在 Eagle 本地直接预览 59+ 种格式的素材，包括 PSD、AI、Figma 文件、视频、音频、字体（无需安装字体即可预览文字效果），避免 “逐个打开本地文件验证内容” 的麻烦。
四、本地素材处理：轻量编辑，无需切换外部软件
Eagle 内置本地素材处理工具，满足设计中 “临时调整” 的需求，无需打开 Photoshop、Premiere 等重型软件，提升本地操作流畅度：
本地图片基础编辑
旋转 / 裁剪 / 翻转：直接在本地调整图片方向（顺时针 / 逆时针旋转）、裁剪尺寸（自定义比例或固定比例如 16:9）、水平 / 垂直翻转，调整后保存为新文件或覆盖原文件，操作仅影响本地素材库；
灰度模式：通过快捷键切换本地图片为 “灰度视图”，帮助设计师检查视觉层级（如确保黑白印刷时素材清晰），无需在外部软件中转换模式。
本地批量处理与格式转换
批量格式转换：选中本地多个素材（如 100 张 PNG 图），可批量转换为 JPG、WebP 等格式，自定义压缩质量（如 80% 清晰度），适合本地素材格式统一（如为项目导出统一的 JPG 素材）；
批量重命名：支持按 “规则批量重命名” 本地素材（如 “项目名 + 序号 + 格式”），避免本地素材文件名混乱（如 “IMG_1234.png” 这类无意义名称）；
重复素材清理：扫描本地 “完全相同” 或 “高度相似” 的素材（如同一图片的不同尺寸版本），支持批量删除重复项，节省本地硬盘空间。
本地视频 / 音频轻处理
视频预览与标记：在本地直接预览视频素材，支持 “视频书签”（标记视频中的关键时间点，如 “00:05 处为按钮动画”），后续查看时可直接跳转到标记点，无需从头播放；
音频预览：鼠标悬停在本地音频文件上即可播放，支持 MP3、WAV、AAC 等格式，无需打开播放器即可快速判断音频内容（如筛选本地会议录音片段）。
五、本地资源库管理：数据自主掌控，灵活迁移
Eagle 的本地资源库是素材存储的核心载体，设计上强调 “数据本地化、迁移灵活”，避免传统本地工具 “资源库绑定设备” 的问题：
本地资源库的创建与备份
多资源库支持：可创建多个本地资源库（如 “工作素材库”“个人灵感库”“客户项目库”），资源库之间完全独立，互不影响，适合按场景区分素材；
本地备份：支持将资源库完整备份为本地文件（.eaglepack 格式），备份文件存储在电脑本地（如移动硬盘、外接存储），无需依赖云端备份，数据安全性由用户自主掌控；
资源库合并：若需整合多个本地资源库（如 “旧电脑素材库”“新电脑素材库”），可通过 “导入资源库” 功能将多个库合并为一个，避免本地素材分散。
本地资源库的灵活迁移
跨设备迁移：若需将本地资源库迁移到另一台电脑，只需将资源库文件夹（默认存储在 “文档 / Eagle”）复制到新设备，在新设备的 Eagle 中 “打开现有资源库” 即可，所有素材、标签、文件夹结构完全保留，无需重新上传；
兼容本地同步工具：若需多设备同步本地资源库，可将资源库文件夹放入本地同步工具（如坚果云、Dropbox、OneDrive），同步工具会自动将本地修改同步到其他设备，Eagle 支持识别同步后的素材变化，无需手动刷新。
六、本地隐私与性能优化：保障数据安全，避免本地卡顿
本地隐私保护
应用锁与文件夹锁：支持设置本地应用启动密码（或 Touch ID 解锁，仅限 macOS），同时可对敏感本地文件夹设置独立密码，解锁前无法查看文件夹内素材，避免他人使用电脑时访问私密设计；
本地数据隔离：所有素材、标签、备注信息均存储在本地资源库，不自动上传云端，用户可自主决定是否备份或分享，避免云端数据泄露风险。
本地性能优化：万级素材也流畅
本地缓存加速：Eagle 会对本地素材生成缩略图缓存，下次打开时无需重新读取原图，即使本地存储数万张素材，打开速度也能保持在 1-2 秒内；
低硬件占用：针对低配电脑优化，本地运行时 CPU 占用率低（日常浏览素材时占用率＜5%），内存消耗小，避免因管理素材导致电脑卡顿，不影响设计软件（如 Photoshop）的正常运行。
总结：Eagle 本地功能的核心价值
Eagle 的本地功能围绕 “高效、自主、流畅” 三大核心，解决传统本地素材管理的痛点：
对比 “系统自带文件夹”：避免 “层层找文件、记路径”，通过标签、智能文件夹实现结构化管理；
对比 “云端素材工具”：不依赖网络，数据存储在本地，响应速度快，隐私更安全；
对比 “重型设计软件”：内置轻量处理工具，无需切换应用，提升本地素材 “收集 - 整理 - 使用” 的全流程效率，尤其适合设计师、摄影师等需要高频管理本地素材的人群。

6 篇资料
个人能用吗，比如我有一大堆照片，想根据印象找或者人脸找或者拍摄地点找
结合 Eagle 软件的功能特性及你的需求（管理大量照片、按印象 / 人脸 / 拍摄地点查找），个人完全可以使用 Eagle 管理照片，但需结合其功能特点判断是否完全匹配你的核心查找需求，以下是具体分析：
一、个人使用的可行性：支持免费试用与基础功能覆盖
从版本与授权来看，Eagle 对个人用户友好，完全满足 “非商业场景下的照片管理” 需求：
免费试用与低成本付费
提供 30 天全功能免费试用，无需绑定付费信息，可先体验照片导入、整理、检索等核心功能；
付费为 “终身许可证”（约 199 元 / 2 台设备），无订阅费用，个人长期使用成本低，且支持 Windows 10+、macOS 10.13+ 双平台，适配主流个人电脑。
无 “个人 / 商业” 功能阉割
个人使用时，可完整调用 Eagle 的本地素材管理功能（如文件夹分类、标签检索、颜色筛选等），无 “免费版限制功能”（区别于摘要 2 中提及的 “电路设计类 Eagle 免费版的尺寸 / 层数限制”，此处为数字资产管理类 Eagle，功能无阉割），管理数千 / 数万张照片无压力。
二、你的核心需求匹配度分析：“印象找” 完全支持，“人脸 / 地点找” 需分情况
你的需求可拆解为 “按模糊印象查找”“按人脸查找”“按拍摄地点查找”，Eagle 的支持程度不同，具体如下：
1. 完全支持：按 “印象” 查找（核心优势）
“印象找” 本质是 “通过模糊特征定位照片”，Eagle 提供多维度检索工具，完美匹配这类需求，尤其适合 “记不清具体信息，但记得部分特征” 的场景：
关键词模糊搜索：若记得照片的 “大致场景”（如 “海边”“生日”）、“拍摄时间”（如 “2023 年夏天”）或 “文件相关信息”（如文件名含 “毕业”），可通过快捷键呼出搜索框，输入关键词（如 “海边 2023”），Eagle 会自动匹配 “文件名、标签、备注、导入时间” 等信息，快速筛选出相关照片；
颜色筛选：若记得照片的 “主色调”（如 “红色晚霞”“蓝色海水”），点击界面中的色卡（如红色、蓝色），可瞬间筛选出含该颜色的所有照片，无需回忆具体内容；
格式 / 尺寸筛选：若记得照片是 “手机拍摄的竖屏照”（尺寸比例 9:16）或 “相机拍摄的 RAW 格式”，可通过 “格式 = JPG/RAW”“尺寸 = 竖屏” 等条件组合筛选，缩小查找范围；
标签联想：可提前为照片添加 “场景标签”（如 “旅行”“家庭聚会”），后续按标签检索（如点击 “旅行” 标签，查看所有旅行相关照片），标签支持批量添加，避免重复操作。
2. 部分支持：按 “拍摄地点” 查找（需依赖照片原生信息）
Eagle 本身不直接支持 “地图定位查找”，但可利用照片的 EXIF 元数据（手机 / 相机拍摄时自动记录的 “拍摄地点、时间、设备型号” 等信息）实现间接查找：
前提条件：你的照片需保留 EXIF 信息（未通过软件删除定位数据），手机 / 相机拍摄时需开启 “位置服务”，确保照片包含经纬度信息；
实现方式：
导入照片后，Eagle 会自动读取并保留照片的 EXIF 信息（在 “素材详情” 中可查看拍摄地点、时间等）；
通过 “高级筛选” 功能，按 “EXIF 拍摄地点” 相关关键词检索（如照片拍摄地点为 “北京故宫”，EXIF 信息中会包含 “北京”，输入关键词 “北京” 即可匹配）；
若需更精准的 “地图式查找”（如在地图上点击地点查看对应照片），Eagle 暂不支持，需配合第三方工具（如先通过手机相册按地点筛选照片，再导入 Eagle 管理）。
3. 暂不支持：按 “人脸” 查找（无 AI 人脸识别功能）
目前 Eagle 的核心定位是 “数字资产管理工具”，而非 “专业照片管理软件”，暂未内置 AI 人脸识别功能，无法实现 “自动识别照片中的人脸，按人脸分类查找”（如 “查找所有含‘家人 A’的照片”）。
替代方案：若需人脸查找，可先通过专业照片软件（如手机相册、Adobe Lightroom、Google 相册）完成人脸分类，再将分类后的照片按文件夹 / 标签导入 Eagle，后续在 Eagle 中按 “文件夹 / 标签” 检索（如创建 “家人 A” 文件夹，存放所有含该人脸的照片）。
三、个人照片管理的额外优势：提升长期整理效率
除了查找需求，Eagle 对个人照片的 “长期整理” 也有显著帮助，解决传统 “文件夹混乱” 的痛点：
结构化分类：支持多层级文件夹（如 “2023 照片→10 月→国庆旅行”），可设置文件夹密码（保护私密照片，如家庭照），避免他人误看；
预览与轻编辑：无需打开照片软件，鼠标悬停即可预览照片，支持 “旋转、裁剪、添加备注”（如在照片上标注 “2023 国庆和家人一起”），备注内容会随照片保存，方便后续回忆；
重复照片清理：内置 “重复素材检测” 功能，可扫描并删除完全相同或高度相似的照片（如同一角度连拍的多张照片），节省电脑存储空间；
多设备同步：若需在 “电脑 + 笔记本” 上管理同一份照片库，可将 Eagle 资源库放在云端同步盘（如坚果云、OneDrive），实现多设备实时同步，避免照片多设备分散。
四、总结：是否适合你的个人照片管理？
推荐场景：若你更看重 “按印象、颜色、标签快速查找照片”，且需要长期结构化整理大量照片（数千 / 数万张），Eagle 是合适的选择，尤其适合同时管理 “照片 + 设计素材 + 截图” 等多种数字资产的用户；
谨慎选择：若 “人脸查找” 是核心需求（如频繁需要按家人 / 朋友人脸分类照片），或需要 “地图式地点查找”，Eagle 暂无法满足，建议优先选择专业照片管理软件（如 Google 相册、Lightroom），或采用 “专业软件分类 + Eagle 长期管理” 的组合方案。
总体而言，Eagle 对个人照片的 “查找 + 整理” 需求覆盖度较高，尤其适合注重 “效率与结构化” 的用户，可通过 30 天免费试用体验核心功能，判断是否符合你的使用习惯。