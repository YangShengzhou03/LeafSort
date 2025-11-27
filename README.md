<div align="center">
  <h1>🍁 LeafView - 枫叶相册</h1>
  <p>高效、智能的图片管理工具</p>
  
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
</div>

## 📋 项目简介

LeafView是一款功能强大的图片管理工具，专注于高效管理、智能整理和批量处理各类图片文件。

### ✨ 核心功能

- **高效图片管理**：支持多种图片格式，快速浏览和管理大量图片
- **智能整理功能**：按时间、地点、设备等多维度自动分类整理图片
- **文件去重**：基于感知哈希算法智能识别相似图片
- **EXIF编辑**：查看和修改图片元数据信息
- **OCR文字识别**：从图片中提取文字内容
- **批量处理**：支持批量重命名、转换格式、应用滤镜等操作

## 🛠️ 技术架构

### 技术栈

- **开发语言**: Python 3.11+
- **GUI框架**: PyQt6 6.5.0+
- **图像处理**: Pillow 11.3.0+
- **OCR引擎**: Tesseract OCR 5.3.0+
- **元数据处理**: piexif, exiftool
- **其他依赖**: numpy, scikit-image, opencv-python

### 架构设计

LeafView采用三层架构设计，确保代码的可维护性和扩展性：

1. **用户界面层**：基于PyQt6构建的现代化GUI界面
2. **业务逻辑层**：处理核心业务逻辑和功能实现
3. **数据处理层**：负责文件操作、元数据处理和数据库交互

## 📁 项目结构

```
LeafView/                    # 项目根目录
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
├── _internal/               # 内部配置目录
│   ├── cache_location.json  # 缓存位置配置
│   └── config.json          # 主配置文件
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

## 🚀 安装部署

### 环境要求

- Python 3.11 或更高版本
- Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)
- Tesseract OCR (用于文字识别功能)

### 源码安装

1. 克隆仓库
   ```bash
   git clone https://github.com/YangShengzhou03/LeafView.git
   cd LeafView
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

可在[GitHub Releases](https://github.com/YangShengzhou03/LeafView/releases)页面下载对应平台的预编译可执行文件。

### 打包为可执行文件

```bash
# Windows
pyinstaller -w -F --icon=resources/img/icon.ico App.py
```

## 💡 使用指南

### 基本操作

1. **导入图片**：通过"文件"菜单或拖拽方式导入图片
2. **浏览图片**：使用鼠标滚轮、方向键或缩略图列表浏览
3. **查看详情**：点击"详情"按钮查看图片元数据
4. **批量处理**：选择多张图片后使用右键菜单进行批量操作

### 智能整理

智能整理功能支持以下分类方式：

- **按时间分类**：年/月/日层级结构
- **按地点分类**：基于GPS信息自动分类
- **按设备分类**：根据相机型号、手机品牌分类
- **按类型分类**：按图片格式或内容类型分类
- **自定义规则**：支持基于正则表达式的自定义整理规则

操作步骤：
1. 选择需要整理的图片
2. 点击"智能整理"按钮
3. 选择整理方式和目标位置
4. 点击"开始整理"执行操作

### 文件去重

1. 选择需要去重的文件夹或图片集
2. 点击"查找重复"按钮
3. 设置相似度阈值（0-100%）
4. 查看重复结果，选择保留或删除

### EXIF编辑

1. 选择需要编辑的图片
2. 点击"编辑EXIF"按钮
3. 修改需要更新的元数据（如标题、作者、评分等）
4. 点击"保存"应用修改

### 文字识别

1. 选择包含文字的图片
2. 点击"OCR识别"按钮
3. 选择识别语言（支持多语言）
4. 等待识别完成，查看或复制识别结果



## ⚙️ 高级功能



### 云存储集成

支持AWS S3、阿里云OSS等云存储服务的集成，方便图片备份和同步。

### 性能优化

- **缓存机制**：缩略图和元数据缓存
- **批量处理**：分批处理大型图片集合
- **并发处理**：使用多线程优化IO密集型任务

## 🆘 故障排除

### 常见问题

1. **模块导入错误**
   - 确保所有依赖已正确安装：`pip install -r requirements.txt --upgrade`

2. **HEIC/HEIF格式支持**
   - 安装pillow-heif库：`pip install pillow-heif --upgrade`

3. **OCR功能无法使用**
   - 确保Tesseract OCR已正确安装并添加到系统PATH

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

## 🤝 社区支持

### 联系方式

- **作者**: YangShengzhou03
- **GitHub**: [https://github.com/YangShengzhou03](https://github.com/YangShengzhou03)
- **问题反馈**: [GitHub Issues](https://github.com/YangShengzhou03/LeafView/issues)
- **讨论区**: [GitHub Discussions](https://github.com/YangShengzhou03/LeafView/discussions)

## 📄 许可证

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

## 🔄 更新日志

### v1.0.0 (2024-XX-XX)

#### ✨ 新增功能
- 初始版本发布
- 实现基本的图片浏览和管理功能
- 智能整理功能：支持按时间、设备等多维度分类
- 去重功能：基于感知哈希算法检测重复图片
- EXIF编辑功能：查看和修改图片元数据
- 文字识别功能：基于Tesseract OCR引擎

#### 🐛 修复问题
- 修复HEIC/HEIF格式图片无法打开的问题
- 修复大文件处理时的内存泄漏问题
- 修复多线程处理中的竞态条件

#### 🚀 性能优化
- 优化缩略图生成和缓存机制
- 改进大批量文件处理性能
- 减少内存占用，提高运行稳定性

<div align="center">
  <p>Built with ❤️ using Python and PyQt6</p>
</div>