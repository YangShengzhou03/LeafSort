# LeafSort 轻羽媒体整理

![GitHub Stars](https://img.shields.io/github/stars/YangShengzhou03/LeafSort?style=flat-square) ![GitHub Forks](https://img.shields.io/github/forks/YangShengzhou03/LeafSort?style=flat-square) ![GitHub Issues](https://img.shields.io/github/issues/YangShengzhou03/LeafSort?style=flat-square) ![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

<a href="https://apps.microsoft.com/detail/9p3mkv4xslj8?referrer=appbadge&mode=direct">
 <img src="https://get.microsoft.com/images/en-us%20dark.svg" width="200"/>
</a>

LeafSort 是一款基于 Python 开发的图片管理工具,专注于高效管理、智能整理和批量处理各类图片文件。软件支持多种图片格式的快速浏览和管理,提供按时间、地点、设备、类型等多维度自动分类整理功能,基于 MD5 哈希算法进行文件去重,支持 EXIF 元数据的查看和编辑,以及批量重命名和地理编码等操作。

## 软件功能

### 图片管理

支持多种图片格式的快速浏览和管理,包括 JPEG、PNG、WebP、HEIC、HEIF 等主流格式,可以快速加载和显示大量图片文件。

### 智能整理

提供智能整理功能,可以根据图片的拍摄时间、GPS 位置、拍摄设备、文件类型等多个维度自动分类整理文件。用户可以自定义分类规则和文件命名规则,软件会自动读取图片的 EXIF 元数据,构建目标路径和文件名,执行文件复制或移动操作。

### 文件去重

基于 MD5 哈希算法精确识别完全相同的文件,支持两阶段筛选机制:第一阶段按文件大小分组快速排除不重复的文件,第二阶段只对相同大小的文件计算 MD5,大幅减少计算量。使用线程池并发计算 MD5,支持缓存已计算的哈希值,提高处理效率。

### EXIF 编辑

支持查看和修改图片的 EXIF 元数据信息,包括标题、作者、评分、相机品牌、型号、镜头信息等。软件内置了相机品牌型号数据库和镜头型号数据库,可以自动匹配镜头信息。支持 JPEG、PNG、WebP 等多种格式的 EXIF 读写,对于复杂格式使用 exiftool 作为备选方案。

### 地理编码

自动将 GPS 坐标转换为地址信息,使用高德地图 API 进行逆地理编码。软件会缓存地理编码结果,避免重复 API 调用,支持批量处理相同位置的文件,提高处理效率。

### 多格式支持

除了图片格式,还支持视频、音频、文档、压缩包等多种文件类型的管理和处理。

## 技术架构

### 开发环境

- Python 3.11+
- PyQt6 6.5.0+
- Pillow 11.3.0+
- opencv-python 4.8.0+
- scikit-image 0.24.0+
- numpy 1.24.0+
- piexif 1.1.3+
- exifread 3.0.0+
- pillow-heif 0.16.0+
- requests 2.31.0+
- playwright 1.40.0+

### 架构设计

软件采用三层架构设计,包括用户界面层、业务逻辑层和数据处理层。用户界面层基于 PyQt6 构建现代化 GUI 界面,业务逻辑层处理核心业务逻辑和功能实现,数据处理层负责文件操作、元数据处理和配置管理。

### 核心模块

- App.py: 应用程序入口,负责初始化 QApplication、创建主窗口实例、设置全局异常处理和单实例检测
- main_window.py: 主窗口控制器,管理所有功能页面,处理窗口事件,管理系统托盘图标
- add_folder.py: 文件夹管理页面,管理源文件夹和目标文件夹的选择,验证文件夹路径的有效性
- smart_arrange.py: 智能整理业务逻辑管理器,管理智能整理的 UI 交互,收集用户配置
- smart_arrange_thread.py: 智能整理工作线程,在独立线程中执行整理任务,避免阻塞 UI
- write_exif.py: EXIF 编辑业务逻辑管理器,管理 EXIF 编辑的 UI 交互,收集用户配置
- write_exif_thread.py: EXIF 写入工作线程,在独立线程中执行 EXIF 写入任务
- file_deduplication.py: 文件去重业务逻辑管理器,管理文件去重的 UI 交互
- file_deduplication_thread.py: 文件去重工作线程,扫描文件并计算 MD5,删除重复文件
- common.py: 通用工具库,提供资源路径管理、文件类型检测、媒体类型检测、地理编码服务等功能
- config_manager.py: 配置管理器,线程安全的配置读写操作,管理地理编码缓存和 API 调用限流
- update_dialog.py: 更新检查对话框,检查 GitHub 上的最新版本

### 线程模型

软件使用 Qt 的信号槽机制进行线程通信,主线程处理所有 UI 交互和响应,工作线程执行耗时的文件操作任务。所有工作线程都继承自 QThread,支持随时停止操作,保持 UI 响应流畅。

## 使用方法

### 安装软件

#### Windows 用户

可以直接从 Microsoft Store 下载安装,搜索"LeafSort"或访问应用商店页面。

#### 开发者安装

1. 克隆仓库

```bash
git clone https://github.com/YangShengzhou03/LeafSort.git
cd LeafSort
```

2. 创建虚拟环境(推荐)

```bash
python -m venv venv
venv\Scripts\activate
```

3. 安装依赖

```bash
pip install -r requirements.txt
```

4. 安装 Playwright 浏览器

```bash
playwright install chromium
```

5. 运行应用

```bash
python App.py
```

### 文件夹管理

启动软件后,首先需要设置源文件夹和目标文件夹。点击"添加文件夹"按钮,选择要整理的图片所在的文件夹作为源文件夹,选择整理后的图片存放位置作为目标文件夹。软件会显示文件夹的基本信息,包括文件数量和总大小。

### 智能整理

在智能整理页面,可以配置分类规则和文件命名规则。支持按年、年月、年月日、年月日时分秒等时间维度分类,支持按省份、城市、区县等地理位置分类,支持按设备类型分类,支持按文件类型分类。配置完成后,点击"开始整理"按钮,软件会自动遍历文件夹,读取图片的 EXIF 元数据,构建目标路径和文件名,执行文件复制或移动操作。

### EXIF 编辑

在 EXIF 编辑页面,可以为图片添加或修改 EXIF 元数据。支持设置标题、作者、评分、相机品牌、型号、镜头信息等。软件内置了相机品牌型号数据库和镜头型号数据库,选择相机品牌和型号后会自动匹配镜头信息。配置完成后,点击"开始写入"按钮,软件会遍历文件夹,更新图片的 EXIF 数据。

### 文件去重

在文件去重页面,可以查找和删除重复文件。点击"开始查重"按钮,软件会扫描文件夹,计算文件的 MD5 哈希值,找出完全相同的文件。查重完成后,会显示重复文件列表,用户可以选择手动选择要保留的文件,或者让软件随机选择。选择完成后,点击"开始删除"按钮,软件会删除选中的重复文件。

### 地理编码

软件会自动将图片的 GPS 坐标转换为地址信息。使用高德地图 API 进行逆地理编码,支持缓存地理编码结果,避免重复 API 调用。如果 API 调用失败,会使用离线地理数据作为备选方案。

## 项目结构

```
LeafSort/
├── App.py                   # 应用程序入口
├── main_window.py           # 主窗口实现
├── Ui_MainWindow.py         # UI界面文件(自动生成)
├── Ui_MainWindow.ui         # Qt设计器界面文件
├── add_folder.py            # 文件夹管理功能
├── smart_arrange.py         # 智能整理服务管理器
├── smart_arrange_thread.py  # 智能整理工作线程
├── write_exif.py            # EXIF编辑管理器
├── write_exif_thread.py     # EXIF编辑工作线程
├── file_deduplication.py    # 文件去重管理器
├── file_deduplication_thread.py # 文件去重工作线程
├── common.py                # 通用函数和工具类
├── config_manager.py        # 配置管理器(线程安全)
├── update_dialog.py         # 更新检查对话框
├── UI_UpdateDialog.py       # 更新对话框UI(自动生成)
├── UI_UpdateDialog.ui       # Qt设计器界面文件
├── requirements.txt         # Python依赖列表
├── App.spec                 # PyInstaller打包配置
├── README.md                # 项目说明(中文)
├── README_EN.md             # 项目说明(英文)
├── license.txt              # 许可证文本
├── .gitignore               # Git忽略文件配置
├── License/                 # 数字签名相关文件
│   ├── Y.cer                # 证书文件
│   ├── Y.pfx                # 私钥文件
│   ├── Y.pvk                # 私钥容器
│   ├── Y.spc                # 软件发布者证书
│   ├── cert2spc.exe         # 证书转换工具
│   └── certmgr.exe          # 证书管理工具
└── resources/               # 资源文件
    ├── cv2_date/            # OpenCV相关文件
    │   └── haarcascade_frontalface_alt2.xml  # 人脸检测模型
    ├── exiftool/            # EXIF工具
    │   ├── exiftool.exe     # EXIF工具可执行文件
    │   ├── exiftool(-k).exe # EXIF工具(保持窗口)
    │   └── exiftool_files/  # EXIF工具依赖文件
    ├── img/                 # 图片资源
    │   ├── activity/        # 活动相关图标
    │   ├── list/            # 列表图标
    │   ├── page_0/          # 页面0图标
    │   ├── page_1/          # 页面1图标
    │   ├── page_2/          # 页面2图标
    │   ├── page_3/          # 页面3图标
    │   ├── page_4/          # 页面4图标
    │   ├── 头标/            # 会员头标
    │   ├── 窗口控制/        # 窗口控制图标
    │   ├── icon.ico         # 应用图标
    │   └── setup.ico        # 安装图标
    ├── json/                # JSON数据文件
    │   ├── City_Reverse_Geocode.json         # 城市地理编码数据
    │   ├── Province_Reverse_Geocode.json     # 省份地理编码数据
    │   ├── camera_brand_model.json           # 相机品牌型号数据库
    │   ├── camera_lens_mapping.json          # 相机镜头映射数据库
    │   └── lens_model.json                  # 镜头型号数据库
    └── stylesheet/          # 样式表文件
        └── menu.setStyleSheet.css  # 菜单样式表
```

## 开发指南

### 代码规范

类名使用大驼峰命名法,如 SmartArrangeManager。函数名使用小写加下划线,如 get_exif_data。变量名使用小写加下划线,如 file_path。常量使用大写加下划线,如 IMAGE_EXTENSIONS。私有方法使用单下划线前缀,如\_process_file。

### 错误处理

使用 try-except 捕获异常,记录详细的错误日志,向用户显示友好的错误提示。关键操作失败时提供恢复建议。文件操作错误时,文件不存在则跳过并记录日志,权限不足则记录错误并继续处理其他文件,文件损坏则记录错误并跳过。EXIF 读取错误时,格式不支持则使用文件系统时间,数据损坏则记录警告并使用默认值,缺少字段则使用空值或默认值。网络请求错误时,API 调用失败则使用缓存数据,Cookie 过期则重新获取 Cookie,超时则重试 3 次后放弃。

### 性能优化

软件使用缓存机制提高性能,包括缩略图缓存、元数据缓存、地理编码缓存和文件哈希缓存。使用线程池并发计算 MD5,多个文件同时处理,最大线程数限制为 CPU 核心数。大文件分块读取,避免一次性加载,及时释放不再使用的资源,限制缓存大小,防止内存溢出。文件去重时先按大小分组,跳过空文件和过大文件,跳过系统文件夹和隐藏文件。

## 许可证

本项目采用 MIT 许可证,详见 license.txt 文件。

## 联系方式

GitHub: https://github.com/YangShengzhou03/LeafSort
Microsoft Store: https://apps.microsoft.com/detail/9p3mkv4xslj8
