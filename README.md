<div align="center">
  <h1>LeafSort（轻羽媒体整理）</h1>
  <p>高效、智能的图片管理工具</p>
  
  <p>
    <a href="https://github.com/YangShengzhou03/LeafSort/stargazers">
<img src="https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=ffd33d&labelColor=000000" alt="GitHub Stars">
<a href="https://github.com/YangShengzhou03/LeafSort/forks">
<img src="https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=green&labelColor=000000" alt="GitHub Forks">
<a href="https://github.com/YangShengzhou03/LeafSort/issues">
<img src="https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=for-the-badge&logo=github&color=purple&labelColor=000000" alt="GitHub Issues">
<a href="https://github.com/YangShengzhou03/LeafSort/blob/main/LICENSE">
      <img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge&logo=open-source-initiative&color=blue&labelColor=000000" alt="MIT License">
    </a>
    <a href="https://apps.microsoft.com/detail/9p3mkv4xslj8?referrer=appbadge&mode=direct">
 <img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>
  </p>
</div>

## 项目简介

LeafSort是一款功能强大的图片管理工具，专注于高效管理、智能整理和批量处理各类图片文件。

### 核心功能

- **高效图片管理**：支持多种图片格式，快速浏览和管理大量图片
- **智能整理功能**：按时间、地点、设备等多维度自动分类整理图片
- **文件去重**：基于感知哈希算法智能识别相似图片
- **EXIF编辑**：查看和修改图片元数据信息

- **批量处理**：支持批量重命名操作

## 技术架构

### 技术栈

- **开发语言**: Python 3.11+
- **GUI框架**: PyQt6 6.5.0+
- **图像处理**: Pillow 11.3.0+

- **元数据处理**: piexif, exiftool
- **其他依赖**: numpy, scikit-image, opencv-python

### 架构设计

LeafSort采用三层架构设计，确保代码的可维护性和扩展性：

1. **用户界面层**：基于PyQt6构建的现代化GUI界面
2. **业务逻辑层**：处理核心业务逻辑和功能实现
3. **数据处理层**：负责文件操作、元数据处理和数据库交互

## 项目结构

```
LeafSort/                    # 项目根目录
├── App.py                   # 应用程序入口
├── main_window.py           # 主窗口实现
├── Ui_MainWindow.py         # UI界面文件
├── Ui_MainWindow.ui         # Qt设计器界面文件
├── add_folder.py            # 文件夹管理功能
├── smart_arrange.py         # 智能整理服务
├── smart_arrange_thread.py  # 智能整理线程
├── write_exif.py            # EXIF编辑功能
├── write_exif_thread.py     # EXIF编辑线程
├── file_deduplication.py    # 文件去重功能
├── file_deduplication_thread.py # 文件去重线程
├── common.py                # 通用函数
├── config_manager.py        # 配置管理器
├── update_dialog.py         # 更新对话框
├── UI_UpdateDialog.py       # 更新对话框UI
├── UI_UpdateDialog.ui       # Qt设计器界面文件
├── License\                 # 许可证相关文件
├── resources/               # 资源文件
│   ├── cv2_date/            # OpenCV相关文件
│   ├── exiftool/            # EXIF工具
│   ├── img/                 # 图片资源
│   ├── json/                # JSON数据文件
│   └── stylesheet/          # 样式表文件
├── requirements.txt         # 依赖列表
├── README.md                # 项目说明（中文）
└── README_EN.md             # 项目说明（英文）
```

## 安装部署

### 环境要求

- Python 3.11 或更高版本
- Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)


### 源码安装

1. 克隆仓库

   ```bash
   git clone https://github.com/YangShengzhou03/LeafSort.git
   cd LeafSort
   ```

2. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```

3. 运行应用
   ```bash
   python App.py
   ```

### 预编译版本

可在[GitHub Releases](https://github.com/YangShengzhou03/LeafSort/releases)页面下载对应平台的预编译可执行文件。

### 打包为可执行文件

```bash
# Windows
pyinstaller -w -F --icon=resources/img/icon.ico App.py
```

## 使用指南

### 基本操作

1. **导入图片**：通过"文件"菜单或拖拽方式导入图片
2. **浏览图片**：使用鼠标滚轮、方向键或缩略图列表浏览
3. **查看详情**：点击"详情"按钮查看图片元数据
4. **批量处理**：选择多张图片后使用右键菜单进行批量操作

### 智能整理

智能整理功能支持以下分类方式和文件格式：

#### 支持的文件格式

- **图片格式**：`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`, `.tiff`, `.heic`, `.heif`, `.svg`
- **视频格式**：`.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.mkv`, `.webm`, `.m4v`, `.3gp`
- **音频格式**：`.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`

#### 分类方式及读取信息

**按时间分类**：

- 读取EXIF的`DateTimeOriginal`字段
- 支持年份/月份/日期层级结构
- 如：`2024/01/15_文件名.jpg`

**按地点分类**：

- 基于GPS坐标进行地理编码
- 支持省份/城市自动识别
- 如：`北京市/朝阳区_文件名.jpg`

**按设备分类**：

- **拍摄设备**：读取EXIF的`Make`字段（相机品牌、手机品牌）
- **相机型号**：读取EXIF的`Model`字段（具体设备型号）
- 支持主流相机品牌和手机品牌识别
- 如：`Apple/iPhone_15_Pro_文件名.jpg`

**按文件类型分类**：

- 直接使用文件扩展名进行分类
- 如：`JPEG/PNG/HEIC/文件名.jpg`

**多级分类组合**：

- 支持最多4级分类组合
- 可自定义分隔符（-、_、空格、无等）
- 如：`2024/Apple/iPhone_15_Pro/JPEG/文件名.jpg`

#### 操作步骤

1. 选择需要整理的图片或文件夹
2. 点击"智能整理"按钮
3. 选择目标文件夹路径
4. 配置分类规则（支持多级组合）
5. 点击"开始整理"执行操作

### 文件去重

#### 查重功能详情

**支持的格式**：

- **主要支持**：所有图片格式（基于文件内容检测）
- **算法原理**：感知哈希算法(Perceptual Hash)
- **智能识别**：支持不同尺寸但内容相似的图片识别
- **格式无关**：忽略文件格式差异（只要是图片即可）

**查重原理**：

- 将图片转换为哈希值进行比较
- 检测图片内容的相似性，而非文件名或大小
- 支持完全相同、轻微编辑、尺寸调整的图片识别

#### 操作步骤

1. 选择需要去重的文件夹或图片集
2. 点击"查找重复"按钮
3. 设置相似度阈值（0-100%）
   - 90-100%：识别几乎相同的图片
   - 70-89%：识别相似但可能有轻微差异的图片
   - 50-69%：识别有部分相似性的图片
4. 查看重复结果，选择保留或删除
5. 支持随机选择、批量操作和手动筛选

#### 重复文件处理

- **自动分组**：相似文件自动分组显示
- **预览对比**：并排显示重复图片进行对比
- **智能建议**：根据文件大小、创建时间等提供保留建议
- **安全删除**：支持移动到回收站或永久删除

### EXIF编辑

#### 支持的文件格式和可写入属性

**JPEG/PNG/WebP格式**：

- **标题** (Title/ImageDescription)
- **作者** (Artist/Creator)
- **评级** (Rating) - 1-5星评分系统
- **拍摄时间** (DateTimeOriginal) - 支持自定义时间源
- **拍摄设备信息** (Make/Model) - 支持主流相机和手机品牌
- **镜头信息** (LensModel/LensMake) - 基于设备自动匹配
- **地理位置信息** (GPS相关标签) - 支持经纬度写入
- **版权信息** (Copyright)
- **关键词/标签** (XPKeywords等)

**HEIC/HEIF格式**：

- **标题和描述** (部分支持)
- **作者信息** (有限支持)
- **评级** (部分设备支持)
- **拍摄时间**
- **设备信息**
- *注：部分属性支持可能有限，取决于设备兼容性*

**视频格式(MOV/MP4/AVI/MKV)**：

- **标题** (Title)
- **作者/创建者** (Author/Creator)
- **评级** (有限支持)
- **拍摄时间**
- **基本设备信息**
- *注：视频元数据支持相对简单，主要用于基本标识*

**RAW格式(CR2/CR3/NEF/ARW/ORF/DNG/RAF)**：

- **标题** (Title)
- **作者信息**
- **评级** (受限于格式规范)
- **拍摄时间**
- **部分设备信息**
- *注：RAW格式的元数据写入受到相机厂商格式限制*

#### 设备信息数据库

内置丰富的设备信息数据库，支持：

- **相机品牌**：Canon、Nikon、Sony、Fujifilm、Leica、Panasonic、Olympus、Pentax、Sigma等
- **手机品牌**：Apple、Xiaomi、Huawei、OPPO、vivo、OnePlus、Samsung、Google等
- **自动镜头匹配**：根据相机型号自动匹配对应的镜头信息

#### 操作步骤

1. 选择需要编辑的图片
2. 点击"编辑EXIF"按钮
3. 配置编辑选项：
   - **时间设置**：使用文件时间/EXIF时间/自定义时间
   - **设备信息**：选择相机品牌和型号（自动匹配镜头信息）
   - **评级设置**：1-5星评分
   - **基本信息**：标题、作者、版权等
4. 点击"开始写入EXIF信息"应用修改

#### 重要提醒

- **不可逆操作**：EXIF写入一旦完成无法撤销，建议先备份原文件
- **格式兼容**：不同格式的EXIF支持程度不同，兼容性有所差异
- **HEIC支持**：需要额外的解码器支持（pillow-heif库）
- **地理信息**：需要图片本身包含GPS数据才能获取和设置位置信息



## 高级功能

### 性能优化

- **缓存机制**：缩略图和元数据缓存
- **批量处理**：分批处理大型图片集合
- **并发处理**：使用多线程优化IO密集型任务

## 故障排除

### 常见问题

1. **模块导入错误**
   - 确保所有依赖已正确安装：`pip install -r requirements.txt --upgrade`

2. **HEIC/HEIF格式支持**
   - 安装pillow-heif库：`pip install pillow-heif --upgrade`



4. **内存占用过高**
   - 减少缓存大小或分批处理图片

### 错误代码参考

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

## 社区支持

### 联系方式

- **作者**: YangShengzhou03
- **GitHub**: [https://github.com/YangShengzhou03](https://github.com/YangShengzhou03)
- **问题反馈**: [GitHub Issues](https://github.com/YangShengzhou03/LeafSort/issues)
- **讨论区**: [GitHub Discussions](https://github.com/YangShengzhou03/LeafSort/discussions)

## 许可证

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

## 更新日志

### v1.0.0 (2024-XX-XX)

#### 新增功能

- 初始版本发布
- 实现基本的图片浏览和管理功能
- 智能整理功能：支持按时间、设备等多维度分类
- 去重功能：基于感知哈希算法检测重复图片
- EXIF编辑功能：查看和修改图片元数据


#### 修复问题

- 修复HEIC/HEIF格式图片无法打开的问题
- 修复大文件处理时的内存泄漏问题
- 修复多线程处理中的竞态条件

#### 性能优化

- 优化缩略图生成和缓存机制
- 改进大批量文件处理性能
- 减少内存占用，提高运行稳定性

<div align="center">
  <p>Built with Python and PyQt6</p>
</div>