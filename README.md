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
- **智能整理功能**：按时间、地点、设备、类型等多维度自动分类整理文件
- **文件去重**：基于MD5哈希算法精确识别完全相同的文件
- **EXIF编辑**：查看和修改图片元数据信息，支持多种格式
- **批量处理**：支持批量重命名、EXIF写入等操作
- **地理编码**：自动将GPS坐标转换为地址信息
- **多格式支持**：支持图片、视频、音频、文档、压缩包等多种文件类型

## 技术架构

### 技术栈

- **开发语言**: Python 3.11+
- **GUI框架**: PyQt6 6.5.0+
- **图像处理**: Pillow 11.3.0+, opencv-python 4.8.0+, scikit-image 0.24.0+, numpy 1.24.0+
- **元数据处理**: piexif 1.1.3+, exifread 3.0.0+
- **HEIC/HEIF支持**: pillow-heif 0.16.0+
- **网络请求**: requests 2.31.0+
- **浏览器自动化**: playwright 1.40.0+（用于获取地理编码API凭证）
- **配置管理**: JSON格式配置文件，支持线程安全操作

### 架构设计

LeafSort采用三层架构设计，确保代码的可维护性和扩展性：

1. **用户界面层**：基于PyQt6构建的现代化GUI界面
2. **业务逻辑层**：处理核心业务逻辑和功能实现
3. **数据处理层**：负责文件操作、元数据处理和数据库交互

#### 系统架构详解

**模块依赖关系图**：

```
App.py (应用入口)
    └── main_window.py (主窗口)
            ├── Ui_MainWindow.py (UI界面，自动生成)
            ├── add_folder.py (文件夹管理)
            │       └── config_manager.py (配置管理)
            ├── smart_arrange.py (智能整理管理器)
            │       └── smart_arrange_thread.py (智能整理工作线程)
            │               └── common.py (通用工具)
            ├── write_exif.py (EXIF编辑管理器)
            │       └── write_exif_thread.py (EXIF编辑工作线程)
            │               └── common.py (通用工具)
            ├── file_deduplication.py (文件去重管理器)
            │       └── file_deduplication_thread.py (文件去重工作线程)
            └── update_dialog.py (更新检查)
```

**核心模块职责**：

1. **App.py** - 应用程序入口
   - 初始化QApplication
   - 创建主窗口实例
   - 设置全局异常处理
   - 单实例检测（通过端口绑定）

2. **main_window.py** - 主窗口控制器
   - 管理所有功能页面
   - 处理窗口事件（最小化、最大化、关闭）
   - 管理系统托盘图标
   - 协调各功能模块的通信

3. **Ui_MainWindow.py** - UI界面定义
   - 由Qt Designer的.ui文件自动生成
   - 定义所有UI组件和布局
   - **警告**：不要手动修改，会被重新生成覆盖

4. **add_folder.py** - 文件夹管理页面
   - 管理源文件夹和目标文件夹的选择
   - 验证文件夹路径的有效性
   - 保存和加载文件夹配置
   - 显示文件夹信息（文件数量、大小等）

5. **smart_arrange.py** - 智能整理业务逻辑管理器
   - 管理智能整理的UI交互
   - 收集用户配置（分类规则、文件名规则等）
   - 启动和停止智能整理线程
   - 处理线程返回的日志和进度

6. **smart_arrange_thread.py** - 智能整理工作线程
   - 在独立线程中执行整理任务，避免阻塞UI
   - 遍历文件夹，收集文件
   - 读取EXIF元数据
   - 构建目标路径和文件名
   - 执行文件复制或移动操作
   - 发送进度和日志信号到主线程

7. **write_exif.py** - EXIF编辑业务逻辑管理器
   - 管理EXIF编辑的UI交互
   - 收集用户配置（标题、作者、评分等）
   - 管理相机品牌和型号选择
   - 自动匹配镜头信息
   - 启动和停止EXIF写入线程

8. **write_exif_thread.py** - EXIF写入工作线程
   - 在独立线程中执行EXIF写入任务
   - 根据文件格式选择处理策略
   - 使用piexif库写入EXIF数据
   - 使用exiftool处理复杂格式
   - 发送进度和日志信号到主线程

9. **file_deduplication.py** - 文件去重业务逻辑管理器
   - 管理文件去重的UI交互
   - 显示重复文件列表
   - 处理用户选择（手动选择、随机选择）
   - 启动和停止去重线程

10. **file_deduplication_thread.py** - 文件去重工作线程
    - **FileScanThread**：扫描文件并计算MD5
      - 两阶段筛选：先按文件大小分组，再计算MD5
      - 使用线程池并发计算MD5
      - 缓存文件哈希值
    - **FileDeduplicateThread**：删除重复文件
      - 根据用户选择删除文件
      - 发送进度信号

11. **common.py** - 通用工具库
    - **ResourceManager**：资源路径管理
      - 处理开发环境和打包环境的路径差异
    - **FileMagicNumberDetector**：文件类型检测
      - 通过文件头魔数识别真实文件类型
      - 验证文件扩展名是否正确
    - **MediaTypeDetector**：媒体类型检测
      - 判断文件是图片、视频还是音频
    - **GeocodingService**：地理编码服务
      - 使用高德地图API进行逆地理编码
      - 管理Cookie和API Key
      - 缓存地理编码结果

12. **config_manager.py** - 配置管理器（线程安全）
    - 管理所有配置项（文件夹路径、窗口设置等）
    - 线程安全的读写操作
    - 自动保存和加载配置
    - 管理地理编码缓存
    - API调用限流控制

13. **update_dialog.py** - 更新检查对话框
    - 检查GitHub上的最新版本
    - 显示更新信息
    - 提供下载链接

**数据流向**：

1. **智能整理流程**：
   ```
   用户选择文件夹 → add_folder.py
       ↓
   用户配置分类规则 → smart_arrange.py
       ↓
   启动工作线程 → smart_arrange_thread.py
       ↓
   遍历文件 → 读取EXIF → 构建路径 → 复制/移动文件
       ↓
   发送进度/日志 → smart_arrange.py → 更新UI
   ```

2. **文件去重流程**：
   ```
   用户选择文件夹 → add_folder.py
       ↓
   点击查重 → file_deduplication.py
       ↓
   启动扫描线程 → FileScanThread
       ↓
   收集文件 → 按大小分组 → 计算MD5 → 分组重复文件
       ↓
   显示重复列表 → file_deduplication.py
       ↓
   用户选择 → 启动删除线程 → FileDeduplicateThread
       ↓
   删除文件 → 发送进度 → 更新UI
   ```

3. **EXIF编辑流程**：
   ```
   用户选择文件夹 → add_folder.py
       ↓
   用户配置EXIF信息 → write_exif.py
       ↓
   启动写入线程 → write_exif_thread.py
       ↓
   遍历文件 → 读取现有EXIF → 更新EXIF → 写入文件
       ↓
   发送进度/日志 → write_exif.py → 更新UI
   ```

**线程模型**：

- **主线程（UI线程）**：
  - 处理所有UI交互
  - 响应用户操作
  - 更新界面显示
  - 接收工作线程的信号

- **工作线程**：
  - SmartArrangeThread：智能整理任务
  - WriteExifThread：EXIF写入任务
  - FileScanThread：文件扫描任务
  - FileDeduplicateThread：文件删除任务
  - 所有工作线程都继承自QThread

- **线程通信**：
  - 使用Qt的信号槽机制（Signal/Slot）
  - 工作线程发送信号，主线程接收并更新UI
  - 线程安全，不会阻塞UI

**关键设计决策**：

1. **为什么使用MD5而不是感知哈希？**
   - MD5是精确哈希，能100%识别完全相同的文件
   - 感知哈希虽然能识别相似文件，但可能产生误判
   - 文件去重的目标是删除完全重复的文件，不是相似文件
   - MD5计算速度快，适合大量文件处理

2. **为什么使用piexif而不是其他库？**
   - piexif专门用于EXIF读写，API简洁
   - 支持JPEG、PNG、WebP等主流格式
   - 文档完善，社区活跃
   - 对于复杂格式，使用exiftool作为备选方案

3. **为什么用Playwright获取Cookie？**
   - 高德地图API需要Cookie和Key才能调用
   - Cookie和Key会定期变化，需要动态获取
   - Playwright可以模拟浏览器访问，自动提取Cookie
   - 比手动抓取更稳定可靠

4. **为什么使用独立线程处理任务？**
   - 文件操作是IO密集型，会阻塞UI
   - 独立线程可以保持UI响应流畅
   - 支持随时停止操作，提升用户体验
   - Qt的信号槽机制保证线程安全

5. **为什么使用两阶段筛选进行文件去重？**
   - 第一阶段按文件大小分组，快速排除不重复的文件
   - 第二阶段只对相同大小的文件计算MD5，大幅减少计算量
   - 性能提升明显，特别是文件数量多时
   - 缓存机制避免重复计算

**线程安全机制**：

1. **ConfigManager的线程安全**：
   - 使用threading.RLock保护所有配置读写
   - 使用装饰器`@_thread_safe_method`确保方法线程安全
   - 所有公共方法都加锁保护

2. **地理编码缓存的线程安全**：
   - 缓存读写都使用RLock保护
   - 支持多线程并发访问
   - 自动清理过期缓存

3. **工作线程的停止机制**：
   - 使用`_stop_flag`标志位控制线程停止
   - 定期检查标志位，及时响应停止请求
   - 使用`isInterruptionRequested()`检查中断

**错误处理策略**：

1. **文件操作错误**：
   - 文件不存在：跳过并记录日志
   - 权限不足：记录错误并继续处理其他文件
   - 文件损坏：记录错误并跳过

2. **EXIF读取错误**：
   - 格式不支持：使用文件系统时间
   - 数据损坏：记录警告并使用默认值
   - 缺少字段：使用空值或默认值

3. **网络请求错误**：
   - API调用失败：使用缓存数据
   - Cookie过期：重新获取Cookie
   - 超时：重试3次后放弃

4. **线程错误**：
   - 线程崩溃：捕获异常并记录日志
   - 停止失败：强制终止线程
   - 资源泄漏：使用try-finally确保释放

**性能优化策略**：

1. **缓存机制**：
   - 缩略图缓存：避免重复生成
   - 元数据缓存：避免重复读取EXIF
   - 地理编码缓存：避免重复API调用
   - 文件哈希缓存：避免重复计算MD5

2. **并发处理**：
   - 使用线程池并发计算MD5
   - 多个文件同时处理
   - 最大线程数限制为CPU核心数

3. **内存管理**：
   - 大文件分块读取，避免一次性加载
   - 及时释放不再使用的资源
   - 限制缓存大小，防止内存溢出

4. **智能筛选**：
   - 文件去重时先按大小分组
   - 跳过空文件和过大文件
   - 跳过系统文件夹和隐藏文件

**配置数据结构**：

```json
{
  "version": "1.1",
  "last_modified": "2025-01-03T12:00:00",
  "folders": [
    "D:/Photos",
    "D:/Videos"
  ],
  "settings": {
    "thumbnail_size": 200,
    "max_cache_size": 10000,
    "default_view": "grid",
    "dark_mode": false,
    "auto_update_metadata": true,
    "use_gps_cache": true,
    "map_provider": "gaode",
    "show_thumbnails": true,
    "enable_exif_edit": true,
    "remember_window_size": true,
    "max_threads": 4,
    "memory_limit_mb": 2048,
    "last_opened_folder": "",
    "window_position": {"x": 100, "y": 100},
    "window_size": {"width": 942, "height": 580},
    "location_cache_tolerance": 0.027,
    "source_folder": "",
    "target_folder": ""
  },
  "api_limits": {
    "gaode": {
      "daily_calls": 50,
      "max_daily_calls": 100,
      "last_reset_date": "2025-01-03",
      "last_call_time": "2025-01-03T12:00:00"
    }
  },
  "cache_settings": {
    "max_location_cache_size": 500000,
    "cache_expiry_days": 0
  }
}
```

**地理编码缓存数据结构**：

```json
{
  "39.916527,116.397128": {
    "address": "北京市东城区天安门广场",
    "last_access": "2025-01-03T12:00:00"
  },
  "30.274085,120.15507": {
    "address": "浙江省杭州市西湖区西湖",
    "last_access": "2025-01-03T12:00:00"
  }
}
```

**性能瓶颈分析**：

1. **文件去重的MD5计算**：
   - 瓶颈：大文件的MD5计算耗时
   - 优化：使用两阶段筛选，减少MD5计算量
   - 优化：使用线程池并发计算
   - 优化：缓存已计算的MD5值

2. **地理编码API调用**：
   - 瓶颈：网络请求延迟和API限流
   - 优化：使用缓存减少API调用
   - 优化：批量处理相同位置的文件
   - 优化：使用离线地理数据作为备选

3. **EXIF数据读取**：
   - 瓶颈：大量文件的EXIF读取
   - 优化：缓存已读取的EXIF数据
   - 优化：跳过不支持EXIF的文件
   - 优化：使用高效的EXIF库

4. **文件复制/移动**：
   - 瓶颈：大文件的IO操作
   - 优化：使用异步IO（未来可考虑）
   - 优化：分批处理，避免内存溢出
   - 优化：显示进度，提升用户体验

**未来优化方向**：

1. **使用异步IO**：提升文件操作性能
2. **增量处理**：支持断点续传
3. **分布式处理**：支持多机并行处理
4. **机器学习**：使用感知哈希识别相似文件
5. **云端同步**：支持云存储集成

## 项目结构

```
LeafSort/                    # 项目根目录
├── App.py                   # 应用程序入口
├── main_window.py           # 主窗口实现
├── Ui_MainWindow.py         # UI界面文件（自动生成）
├── Ui_MainWindow.ui         # Qt设计器界面文件
├── add_folder.py            # 文件夹管理功能
├── smart_arrange.py         # 智能整理服务管理器
├── smart_arrange_thread.py  # 智能整理工作线程
├── write_exif.py            # EXIF编辑管理器
├── write_exif_thread.py     # EXIF编辑工作线程
├── file_deduplication.py    # 文件去重管理器
├── file_deduplication_thread.py # 文件去重工作线程
├── common.py                # 通用函数和工具类
├── config_manager.py        # 配置管理器（线程安全）
├── update_dialog.py         # 更新检查对话框
├── UI_UpdateDialog.py       # 更新对话框UI（自动生成）
├── UI_UpdateDialog.ui       # Qt设计器界面文件
├── requirements.txt         # Python依赖列表
├── App.spec                 # PyInstaller打包配置
├── README.md                # 项目说明（中文）
├── README_EN.md             # 项目说明（英文）
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
    │   ├── exiftool(-k).exe # EXIF工具（保持窗口）
    │   └── exiftool_files/  # EXIF工具依赖文件
    ├── img/                 # 图片资源
    │   ├── activity/        # 活动相关图标
    │   ├── list/            # 列表图标
    │   ├── page_0/          # 页面0图标
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

### 开发环境搭建

**1. 克隆仓库**

```bash
git clone https://github.com/YangShengzhou03/LeafSort.git
cd LeafSort
```

**2. 创建虚拟环境（推荐）**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

**3. 安装依赖**

```bash
pip install -r requirements.txt
```

**4. 安装Playwright浏览器**

```bash
playwright install chromium
```

**5. 运行应用**

```bash
python App.py
```

### 开发工具推荐

- **IDE**：PyCharm Professional 或 VS Code
- **UI设计**：Qt Designer（PyQt6自带）
- **调试工具**：PyCharm Debugger 或 pdb
- **版本控制**：Git
- **依赖管理**：pip 或 poetry

### 代码规范

**命名规范**：

- 类名：大驼峰命名法（如 `SmartArrangeManager`）
- 函数名：小写+下划线（如 `get_exif_data`）
- 变量名：小写+下划线（如 `file_path`）
- 常量：大写+下划线（如 `IMAGE_EXTENSIONS`）
- 私有方法：单下划线前缀（如 `_process_file`）

**注释规范**：

- 类和函数使用docstring说明
- 复杂逻辑添加行内注释
- TODO标记待完成功能
- FIXME标记需要修复的问题

**错误处理**：

- 使用try-except捕获异常
- 记录详细的错误日志
- 向用户显示友好的错误提示
- 关键操作失败时提供恢复建议

### 调试技巧

**1. 启用详细日志**

在代码开头设置日志级别：

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**2. 使用PyQt调试模式**

```python
# 在App.py中添加
import sys
from PyQt6.QtCore import Qt
QtCore.qInstallMessageHandler(lambda t, c, m: print(f"[{t}] {c}: {m}"))
```

**3. 线程调试**

工作线程的日志会通过信号发送到主线程，在UI中显示。如果需要在线程内部调试，可以：

```python
import logging
logger = logging.getLogger(__name__)
logger.debug("调试信息")
```

**4. 断点调试**

在PyCharm中：
- 在代码行号左侧点击设置断点
- 右键点击"Debug 'App'"
- 程序会在断点处暂停，可以查看变量值

**5. 性能分析**

使用Python的cProfile分析性能：

```bash
python -m cProfile -o profile.stats App.py
```

### 常见开发问题

**1. UI文件修改后不生效**

**问题**：修改了Ui_MainWindow.ui文件，但运行时没有变化

**原因**：Ui_MainWindow.py是由.ui文件自动生成的

**解决**：
```bash
pyuic6 Ui_MainWindow.ui -o Ui_MainWindow.py
```

**2. 资源文件找不到**

**问题**：运行时报错"找不到资源文件"

**原因**：开发环境和打包环境的路径不同

**解决**：使用`get_resource_path()`函数获取资源路径

```python
from common import get_resource_path
icon_path = get_resource_path('resources/img/icon.ico')
```

**3. 线程阻塞UI**

**问题**：长时间操作时界面卡死

**原因**：在主线程中执行耗时操作

**解决**：将耗时操作放到工作线程中

```python
# 错误做法
def on_button_click(self):
    time.sleep(10)  # 会阻塞UI

# 正确做法
class WorkerThread(QThread):
    def run(self):
        time.sleep(10)  # 不会阻塞UI
```

**4. 信号槽连接错误**

**问题**：点击按钮没有反应

**原因**：信号没有正确连接到槽函数

**解决**：检查信号连接代码

```python
# 正确连接
self.btnStart.clicked.connect(self.start_task)

# 检查是否重复连接
try:
    self.btnStart.clicked.disconnect()
except TypeError:
    pass
self.btnStart.clicked.connect(self.start_task)
```

**5. 配置文件损坏**

**问题**：启动时报错"配置文件损坏"

**原因**：config.json文件格式错误

**解决**：删除配置文件，程序会自动重新生成

```bash
# Windows
del %LOCALAPPDATA%\LeafSort\_internal\config.json

# macOS/Linux
rm ~/.config/leafsort/_internal/config.json
```

**6. Playwright浏览器未安装**

**问题**：地理编码功能报错"浏览器未安装"

**原因**：Playwright需要单独安装浏览器

**解决**：
```bash
playwright install chromium
```

**7. HEIC文件无法处理**

**问题**：HEIC格式图片无法读取EXIF

**原因**：缺少pillow-heif库或未注册opener

**解决**：
```python
from pillow_heif import register_heif_opener
register_heif_opener()
```

**8. 内存占用过高**

**问题**：处理大量文件时内存占用过高

**原因**：一次性加载太多文件到内存

**解决**：
- 分批处理文件
- 及时释放不再使用的资源
- 增加缓存过期时间
- 减少缓存大小

### 测试指南

**1. 单元测试**

为关键函数编写单元测试：

```python
import unittest
from common import MediaTypeDetector

class TestMediaTypeDetector(unittest.TestCase):
    def test_is_image(self):
        self.assertTrue(MediaTypeDetector.is_image('test.jpg'))
        self.assertFalse(MediaTypeDetector.is_image('test.txt'))

if __name__ == '__main__':
    unittest.main()
```

**2. 集成测试**

测试完整的功能流程：

```python
def test_smart_arrange():
    # 准备测试数据
    test_folder = create_test_files()
    
    # 执行智能整理
    manager = SmartArrangeManager()
    manager.start_arrange(test_folder)
    
    # 验证结果
    assert check_arranged_files()
```

**3. 手动测试清单**

- [ ] 文件夹选择功能
- [ ] 智能整理功能（各种分类规则）
- [ ] 文件去重功能
- [ ] EXIF编辑功能
- [ ] 窗口最小化/最大化/关闭
- [ ] 系统托盘功能
- [ ] 配置保存和加载
- [ ] 错误处理和日志显示

### 打包发布

**1. 使用PyInstaller打包**

```bash
# Windows
pyinstaller -w -F --icon=resources/img/icon.ico App.py

# macOS
pyinstaller -w -F --icon=resources/img/icon.icns App.py

# Linux
pyinstaller -w -F --icon=resources/img/icon.png App.py
```

**2. 使用Inno Setup制作安装包（Windows）**

```bash
iscc LeafSort封装脚本.iss
```

**3. 数字签名（Windows）**

```bash
signtool sign /f License/Y.pfx /p 密码 /t 时间戳服务器 LeafSort.exe
```

**4. 发布到Microsoft Store**

- 准备应用包
- 提交到Microsoft Partner Center
- 等待审核通过

### 版本管理

**版本号格式**：主版本号.次版本号.修订号

- 主版本号：重大功能更新或不兼容的API变更
- 次版本号：新增功能，向后兼容
- 修订号：bug修复或小改进

**发布流程**：

1. 更新版本号（App.py和config_manager.py）
2. 更新README.md和更新日志
3. 提交代码到Git
4. 创建Git标签
5. 打包发布版本
6. 上传到GitHub Releases
7. 更新Microsoft Store版本

### 贡献指南

**1. Fork项目**

点击GitHub页面上的"Fork"按钮

**2. 创建分支**

```bash
git checkout -b feature/your-feature-name
```

**3. 提交更改**

```bash
git add .
git commit -m "添加新功能"
```

**4. 推送到Fork**

```bash
git push origin feature/your-feature-name
```

**5. 创建Pull Request**

在GitHub上创建Pull Request，描述你的更改

### 性能调优

**1. 调整线程数**

在config_manager.py中修改`max_threads`：

```python
"max_threads": 8  # 根据CPU核心数调整
```

**2. 调整缓存大小**

```python
"max_cache_size": 20000  # 增加缓存大小
```

**3. 调整内存限制**

```python
"memory_limit_mb": 4096  # 增加内存限制
```

**4. 调整API调用限制**

```python
"max_daily_calls": 300  # 增加每日API调用次数
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

#### 实现原理

**多线程架构**：

- 使用独立的工作线程（SmartArrangeThread）执行整理任务
- 避免阻塞主界面，保持UI响应流畅
- 支持随时停止操作，保障用户控制权
- 实时进度反馈和日志输出

**文件处理流程**：

1. **文件收集阶段**：
   - 遍历源文件夹及其子文件夹（可选）
   - 收集所有支持的文件
   - 统计总文件数用于进度计算

2. **元数据提取阶段**：
   - 读取文件的EXIF信息（如果存在）
   - 提取拍摄时间、GPS坐标、设备信息等
   - 对于非图片文件，使用文件系统时间戳

3. **分类路径构建**：
   - 根据用户选择的分类规则构建目标路径
   - 支持最多5级嵌套分类
   - 自动创建不存在的文件夹

4. **文件名构建**：
   - 根据用户选择的标签构建新文件名
   - 支持原始文件名、时间、设备、自定义标签等
   - 处理文件名冲突（自动添加序号）

5. **文件操作阶段**：
   - 支持复制或移动操作
   - 保持原文件属性（创建时间、修改时间等）
   - 记录操作日志，便于追踪

**EXIF数据读取**：

- **图片文件**：使用exifread库读取EXIF数据
- **RAW文件**：解析RAW格式的元数据
- **HEIC/HEIF文件**：使用pillow-heif库解码后读取
- **视频文件**：尝试读取视频元数据
- **其他文件**：使用文件系统时间戳

**地理信息处理**：

- 从EXIF的GPS段提取经纬度坐标
- 调用地理编码服务获取地址信息
- 优先使用缓存，避免重复API调用
- 支持离线地理数据作为备选方案

**设备信息识别**：

- 从EXIF的Make和Model字段读取设备信息
- 使用内置数据库匹配品牌和型号
- 自动匹配镜头信息
- 支持自定义设备信息

**时间处理**：

- 支持多种时间来源：
  - 最早时间：比较EXIF时间、创建时间、修改时间，取最早
  - 拍摄日期：使用EXIF的DateTimeOriginal字段
  - 创建时间：使用文件系统创建时间
  - 修改时间：使用文件系统修改时间
- 时间格式化：支持年份、月份、日期、星期、时间等多种格式
- 时区处理：自动处理时区信息

**文件名处理**：

- 支持保留原始文件名
- 支持基于时间、设备、位置等构建新文件名
- 支持自定义标签
- 处理特殊字符和保留名称
- 自动处理文件名冲突

**操作类型**：

- **复制**：保留原文件，在目标位置创建副本
- **移动**：将原文件移动到目标位置，删除原文件
- **仅重命名**：在原位置重命名文件
- **提取到顶层**：将所有文件提取到目标文件夹顶层，不进行分类

#### 支持的文件格式

- **图片格式**：`.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`, `.tiff`, `.heic`, `.heif`, `.svg`, `.cr2`, `.cr3`, `.nef`, `.arw`, `.orf`, `.sr2`, `.raf`, `.dng`, `.tif`, `.psd`, `.rw2`, `.pef`, `.nrw`
- **视频格式**：`.mp4`, `.avi`, `.mov`, `.wmv`, `.flv`, `.mkv`, `.webm`, `.m4v`, `.3gp`
- **音频格式**：`.mp3`, `.wav`, `.flac`, `.aac`, `.ogg`, `.wma`, `.m4a`
- **文档格式**：`.pdf`, `.doc`, `.docx`, `.txt`, `.rtf`, `.xls`, `.xlsx`, `.ppt`, `.pptx`, `.csv`, `.html`, `.htm`, `.xml`, `.epub`, `.md`, `.log`
- **压缩包格式**：`.zip`, `.rar`, `.7z`, `.tar`, `.gz`, `.bz2`, `.xz`, `.iso`, `.jar`

#### 分类方式及读取信息

**按时间分类**：

- 读取EXIF的`DateTimeOriginal`字段（拍摄日期）
- 支持年份/月份/日期/星期/时间层级结构
- 时间来源选择：最早时间、拍摄日期、创建时间、修改时间
- 如：`2024/01/15_文件名.jpg`

**按地点分类**：

- 基于GPS坐标进行地理编码
- 支持省份/城市自动识别
- 使用高德地图API进行逆地理编码
- 内置地理数据缓存机制，避免重复API调用
- 支持离线地理数据（基于内置的省份/城市JSON数据）
- 如：`江西省/南昌市_文件名.jpg`

**按设备分类**：

- **拍摄设备**：读取EXIF的`Make`字段（相机品牌、手机品牌）
- **相机型号**：读取EXIF的`Model`字段（具体设备型号）
- 支持主流相机品牌和手机品牌识别
- 内置相机品牌型号数据库（camera_brand_model.json）
- 自动匹配镜头信息（基于camera_lens_mapping.json）
- 如：`Apple/iPhone_15_Pro_文件名.jpg`

**按文件类型分类**：

- 直接使用文件扩展名进行分类
- 支持图片、视频、音频、文档、压缩包等多种类型
- 如：`JPEG/PNG/HEIC/文件名.jpg`

**多级分类组合**：

- 支持最多5级分类组合
- 可自定义分隔符（-、_、空格、.、,、~、无等）
- 支持自定义标签作为文件名的一部分
- 如：`2024/Apple/iPhone_15_Pro/JPEG/文件名.jpg`

#### 操作步骤

1. 选择需要整理的图片或文件夹
2. 点击"智能整理"按钮
3. 选择目标文件夹路径
4. 配置分类规则（支持多级组合）
5. 点击"开始整理"执行操作

#### 地理编码与缓存机制

**地理编码实现**：

- **主要API**：使用高德地图逆地理编码API
- **Cookie管理**：通过Playwright自动化获取API所需的Cookie和Key
- **请求流程**：
  1. 访问高德地图开发者示例页面
  2. 自动提取Cookie和API Key
  3. 使用提取的凭证调用逆地理编码API
  4. 解析返回的JSON数据获取地址信息

**缓存机制**：

- **本地缓存**：将经纬度与地址的映射关系存储在本地JSON文件
- **缓存位置**：`%LOCALAPPDATA%\LeafSort\_internal\cache_location.json`
- **缓存策略**：
  - 优先从缓存读取地址信息
  - 缓存未命中时调用API获取
  - API获取成功后更新缓存
  - 支持缓存过期清理（可配置过期天数）
  - 最大缓存条目数限制（默认50万条）
- **性能优化**：
  - 避免重复调用API，减少网络请求
  - 支持模糊匹配（可设置容差范围）
  - 自动清理过期和过多的缓存条目

**离线地理数据**：

- **省份数据**：Province_Reverse_Geocode.json
- **城市数据**：City_Reverse_Geocode.json
- **用途**：在API不可用时提供基本的地理信息
- **数据结构**：GeoJSON格式，包含行政区划边界和名称信息

**API限流**：

- **每日调用限制**：默认100次/天（可配置）
- **自动重置**：每日零点自动重置调用计数
- **限流保护**：超过限制时停止调用API，避免被封禁

### 文件去重

#### 查重功能详情

**支持的格式**：

- **主要支持**：所有文件格式（基于文件内容检测）
- **算法原理**：MD5哈希算法
- **精确识别**：基于文件内容的精确哈希计算
- **格式无关**：忽略文件格式差异，只要文件内容完全相同即可识别

**查重原理**：

- **两阶段筛选机制**：
  1. 第一阶段：按文件大小分组，仅对相同大小的文件进行哈希计算，大幅提升性能
  2. 第二阶段：对相同大小的文件计算MD5哈希值，精确识别内容完全相同的文件
- **MD5算法特点**：
  - 基于文件二进制内容计算哈希值
  - 文件内容完全相同时，MD5值必定相同
  - 文件内容有任何差异（哪怕一个字节），MD5值完全不同
  - 无法识别相似但不完全相同的文件（这是与感知哈希算法的关键区别）
- **缓存机制**：
  - 对文件大小、修改时间和MD5值进行缓存
  - 避免重复计算已处理的文件
  - 支持多线程并发处理，提升大文件处理效率

#### 操作步骤

1. 选择需要去重的文件夹或图片集
2. 点击"查找重复"按钮
3. 等待扫描完成，系统会自动找出所有完全相同的文件
4. 查看重复结果，选择保留或删除
5. 支持随机选择、批量操作和手动筛选

#### 重复文件处理

- **自动分组**：相同MD5值的文件自动分组显示
- **预览对比**：并排显示重复文件进行对比
- **手动筛选**：支持手动选择要保留或删除的文件
- **随机选择**：每组随机保留一个文件，删除其余文件
- **安全删除**：直接删除选定的重复文件（注意：删除操作不可恢复，请谨慎操作）
- **进度显示**：实时显示删除进度和状态

### EXIF编辑

#### EXIF编辑实现原理

**技术实现**：

- **主要库**：使用piexif库进行EXIF读写
- **辅助工具**：集成exiftool作为备选方案，用于处理复杂格式
- **HEIC/HEIF支持**：通过pillow-heif库解码HEIC格式
- **多格式支持**：针对不同格式采用不同的处理策略

**EXIF数据结构**：

- **0th段**：包含基本图像信息（ImageDescription、Make、Model、Copyright等）
- **Exif段**：包含拍摄参数（DateTimeOriginal、FNumber、FocalLength、LensMake、LensModel等）
- **GPS段**：包含地理位置信息（经纬度坐标）
- **Interop段**：互操作性信息

**写入流程**：

1. 读取现有EXIF数据（如果存在）
2. 根据用户配置更新相应字段
3. 将修改后的EXIF数据序列化为二进制格式
4. 将EXIF数据插入到图像文件中
5. 对于HEIC等特殊格式，先转换为临时JPEG文件，写入EXIF后再转换回原格式

**镜头信息自动匹配**：

- 基于相机品牌和型号，从内置数据库自动匹配镜头信息
- 使用camera_lens_mapping.json存储相机与镜头的映射关系
- 自动填充LensMake和LensModel字段

**GPS坐标处理**：

- 支持十进制格式：经度116.397128, 纬度39.916527
- 支持度分秒格式：经度120;23;53.34, 纬度30;6;51.51
- 自动转换和验证坐标范围（经度-180到180，纬度-90到90）
- 将坐标写入GPS段的相应字段

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

- **多线程处理**：
  - 智能整理、文件去重、EXIF编辑均使用独立线程处理
  - 避免阻塞主界面，保持UI响应流畅
  - 支持并发处理多个文件，提升处理效率

- **缓存机制**：
  - **缩略图缓存**：缓存生成的缩略图，避免重复计算
  - **元数据缓存**：缓存EXIF数据和文件信息
  - **地理编码缓存**：缓存经纬度与地址的映射关系
  - **文件哈希缓存**：缓存文件大小、修改时间和MD5值
  - 所有缓存支持过期清理和大小限制

- **批量处理优化**：
  - 分批处理大型文件集合，避免内存溢出
  - 支持断点续传和停止操作
  - 实时进度显示和日志输出

- **智能筛选**：
  - 文件去重时先按文件大小分组，减少哈希计算量
  - 跳过空文件和过大文件（超过2GB）
  - 自动跳过系统文件夹和隐藏文件

- **内存管理**：
  - 大文件分块读取，避免一次性加载到内存
  - 及时释放不再使用的资源
  - 支持配置最大内存使用限制

### 配置管理

- **配置文件位置**：`%LOCALAPPDATA%\LeafSort\_internal\config.json`
- **配置项**：
  - 文件夹路径（源文件夹、目标文件夹）
  - 窗口大小和位置
  - 缓存设置（最大缓存大小、过期天数）
  - API限制（每日调用次数、重置时间）
  - 其他用户偏好设置
- **自动保存**：用户操作自动保存配置
- **版本迁移**：支持配置版本升级和数据迁移

## 故障排除

### 常见问题

#### 安装和启动问题

**1. 模块导入错误**

**症状**：启动时报错`ModuleNotFoundError: No module named 'xxx'`

**原因**：缺少必要的Python依赖库

**解决方案**：
```bash
# 安装所有依赖
pip install -r requirements.txt --upgrade

# 如果特定模块缺失，单独安装
pip install PyQt6
pip install pillow
pip install piexif
```

**2. HEIC/HEIF格式支持**

**症状**：HEIC格式图片无法打开或读取EXIF

**原因**：缺少pillow-heif库或未注册opener

**解决方案**：
```bash
pip install pillow-heif --upgrade
```

然后在代码中注册opener：
```python
from pillow_heif import register_heif_opener
register_heif_opener()
```

**3. Playwright浏览器未安装**

**症状**：地理编码功能报错"浏览器未安装"

**原因**：Playwright需要单独安装浏览器

**解决方案**：
```bash
playwright install chromium
```

**4. 应用无法启动**

**症状**：双击exe文件没有反应或闪退

**原因**：可能是依赖库缺失或权限问题

**解决方案**：
- 以管理员权限运行
- 检查Windows Defender是否拦截
- 查看日志文件（`%LOCALAPPDATA%\LeafSort\_internal\`）
- 重新安装应用程序

#### 功能使用问题

**5. 智能整理后文件丢失**

**症状**：整理后找不到文件

**原因**：可能选择了"移动"操作，文件被移动到目标文件夹

**解决方案**：
- 检查目标文件夹
- 查看整理日志，了解文件去向
- 下次使用"复制"操作，保留原文件

**6. 文件去重速度慢**

**症状**：扫描大量文件时速度很慢

**原因**：MD5计算耗时，特别是大文件

**解决方案**：
- 减少处理的文件数量
- 跳过超大文件（>2GB）
- 增加线程数（在配置中调整）
- 使用SSD硬盘提升IO性能

**7. EXIF写入失败**

**症状**：写入EXIF时报错"写入失败"

**原因**：文件格式不支持或文件被占用

**解决方案**：
- 确保文件没有被其他程序打开
- 检查文件格式是否支持
- 以管理员权限运行
- 检查磁盘空间是否充足

**8. 地理编码失败**

**症状**：无法获取地址信息

**原因**：网络问题、API限流或Cookie过期

**解决方案**：
- 检查网络连接
- 等待API限流重置（每日100次）
- 清除Cookie缓存重新获取
- 使用离线地理数据

#### 性能问题

**9. 内存占用过高**

**症状**：处理大量文件时内存占用过高

**原因**：一次性加载太多文件到内存

**解决方案**：
- 分批处理文件
- 及时释放不再使用的资源
- 增加缓存过期时间
- 减少缓存大小
- 关闭不必要的后台程序

**10. CPU占用过高**

**症状**：处理时CPU占用100%

**原因**：线程数过多或MD5计算密集

**解决方案**：
- 减少线程数（在配置中调整）
- 降低处理优先级
- 使用性能更好的CPU
- 分批处理，避免同时处理太多文件

**11. 磁盘IO过高**

**症状**：整理时磁盘读写速度慢

**原因**：大量文件复制/移动操作

**解决方案**：
- 使用SSD硬盘
- 减少同时处理的文件数
- 关闭杀毒软件的实时扫描（临时）
- 使用"复制"而不是"移动"操作

#### 界面问题

**12. 窗口无法显示**

**症状**：启动后窗口不显示

**原因**：窗口在屏幕外或分辨率问题

**解决方案**：
- 删除配置文件，重置窗口位置
- 修改显示器分辨率
- 使用Alt+Tab切换窗口
- 检查任务栏是否有托盘图标

**13. 界面卡死**

**症状**：操作时界面无响应

**原因**：主线程被阻塞

**解决方案**：
- 等待操作完成
- 如果长时间卡死，强制关闭并重启
- 检查是否有大量文件需要处理
- 查看日志了解卡住的位置

**14. 进度条不更新**

**症状**：进度条一直不动

**原因**：线程通信失败或任务卡住

**解决方案**：
- 查看日志了解任务状态
- 检查是否有错误信息
- 尝试停止并重新开始任务
- 重启应用程序

#### 配置问题

**15. 配置文件损坏**

**症状**：启动时报错"配置文件损坏"

**原因**：config.json文件格式错误

**解决方案**：
```bash
# Windows
del %LOCALAPPDATA%\LeafSort\_internal\config.json

# macOS/Linux
rm ~/.config/leafsort/_internal/config.json
```

程序会自动重新生成默认配置。

**16. 设置无法保存**

**症状**：修改设置后重启恢复默认

**原因**：配置文件只读或权限不足

**解决方案**：
- 检查配置文件权限
- 以管理员权限运行
- 检查磁盘空间是否充足
- 关闭其他可能占用配置文件的程序

#### 网络问题

**17. 更新检查失败**

**症状**：无法检查更新

**原因**：网络问题或GitHub访问受限

**解决方案**：
- 检查网络连接
- 使用代理或VPN
- 手动访问GitHub查看最新版本
- 下载最新版本手动安装

**18. 地理编码API调用失败**

**症状**：无法获取地址信息

**原因**：高德地图API限流或Cookie过期

**解决方案**：
- 查看日志了解具体错误
- 等待API限流重置（每日100次）
- 清除Cookie缓存（`%LOCALAPPDATA%\LeafSort\_internal\cookies.json`）
- 检查网络连接
- 使用离线地理数据

#### 文件操作问题

**19. 文件被占用**

**症状**：操作时报错"文件被占用"

**原因**：文件被其他程序打开

**解决方案**：
- 关闭所有可能打开文件的程序
- 检查杀毒软件是否扫描文件
- 重启计算机
- 使用Process Explorer查看占用进程

**20. 权限不足**

**症状**：操作时报错"权限被拒绝"

**原因**：没有足够的文件系统权限

**解决方案**：
- 以管理员权限运行程序
- 检查文件和文件夹权限
- 修改文件权限（Linux/macOS）
- 关闭杀毒软件的实时保护

**21. 磁盘空间不足**

**症状**：操作时报错"磁盘空间不足"

**原因**：目标磁盘空间不够

**解决方案**：
- 清理磁盘空间
- 选择其他目标文件夹
- 删除临时文件
- 使用磁盘清理工具

#### 其他问题

**22. 托盘图标不显示**

**症状**：最小化后托盘图标不显示

**原因**：托盘区域隐藏或程序崩溃

**解决方案**：
- 检查任务栏的隐藏图标区域
- 重新启动程序
- 检查程序是否崩溃
- 查看日志了解崩溃原因

**23. 日志文件过大**

**症状**：日志文件占用大量磁盘空间

**原因**：长时间运行产生大量日志

**解决方案**：
- 定期清理日志文件
- 调整日志级别（从DEBUG改为INFO）
- 限制日志文件大小
- 使用日志轮转

**24. 系统托盘通知不显示**

**症状**：操作完成后没有通知

**原因**：系统通知被禁用或程序设置问题

**解决方案**：
- 检查Windows通知设置
- 在程序中启用通知
- 检查专注模式是否开启
- 重启程序

### 错误代码参考

| 错误代码 | 描述 | 可能原因 | 解决方案 |
|----------|------|----------|----------|
| ERR-001 | 文件不存在或无法访问 | 文件被删除、移动或权限不足 | 检查文件路径和权限 |
| ERR-002 | 不支持的文件格式 | 缺少解码器库或文件损坏 | 安装相应的解码器库 |
| ERR-003 | 内存不足 | 处理文件过多或内存泄漏 | 减少处理批量或增加内存 |
| ERR-004 | 磁盘空间不足 | 目标磁盘空间不够 | 清理磁盘空间 |
| ERR-005 | 网络连接失败 | 网络断开或防火墙阻止 | 检查网络设置 |
| ERR-006 | 权限被拒绝 | 文件系统权限不足 | 以管理员权限运行 |
| ERR-007 | 依赖库缺失 | Python库未安装或版本不兼容 | 重新安装依赖库 |
| ERR-008 | 配置文件损坏 | JSON格式错误或文件损坏 | 删除配置文件重新生成 |
| ERR-009 | EXIF读取失败 | 文件格式不支持或数据损坏 | 使用文件系统时间 |
| ERR-010 | EXIF写入失败 | 文件被占用或格式不支持 | 关闭文件或使用其他格式 |
| ERR-011 | 地理编码失败 | API限流或网络问题 | 检查网络或使用缓存 |
| ERR-012 | 线程启动失败 | 资源不足或系统限制 | 重启程序或增加资源 |
| ERR-013 | 文件去重失败 | MD5计算错误或文件损坏 | 检查文件完整性 |
| ERR-014 | 智能整理失败 | 路径构建错误或权限问题 | 检查目标路径和权限 |

### 日志分析

**日志位置**：
- Windows: `%LOCALAPPDATA%\LeafSort\_internal\`
- macOS: `~/Library/Application Support/LeafSort/_internal/`
- Linux: `~/.config/leafsort/_internal/`

**关键日志文件**：
- `app.log`：应用程序主日志
- `smart_arrange.log`：智能整理日志
- `file_deduplication.log`：文件去重日志
- `write_exif.log`：EXIF编辑日志

**日志级别**：
- DEBUG：详细的调试信息
- INFO：一般信息
- WARNING：警告信息
- ERROR：错误信息
- CRITICAL：严重错误

**常见日志错误**：

1. **`FileNotFoundError`**：文件不存在
   - 检查文件路径是否正确
   - 确认文件没有被删除

2. **`PermissionError`**：权限不足
   - 以管理员权限运行
   - 检查文件权限设置

3. **`MemoryError`**：内存不足
   - 减少处理批量
   - 增加系统内存
   - 关闭其他程序

4. **`ConnectionError`**：网络连接失败
   - 检查网络连接
   - 检查防火墙设置
   - 使用代理或VPN

5. **`JSONDecodeError`**：JSON解析失败
   - 配置文件损坏
   - 删除配置文件重新生成

### 性能监控

**使用任务管理器监控**：
- CPU使用率：正常<50%，高负载时可能达到100%
- 内存使用：正常<1GB，处理大量文件时可能达到2-4GB
- 磁盘IO：复制/移动文件时会有大量读写
- 网络IO：地理编码时会有网络请求

**性能基准**：
- 文件去重：约1000文件/分钟（取决于文件大小）
- 智能整理：约500文件/分钟（取决于EXIF读取）
- EXIF编辑：约200文件/分钟（取决于文件格式）
- 地理编码：约60次/分钟（受API限流限制）

**优化建议**：
- 使用SSD硬盘提升IO性能
- 增加内存提升处理能力
- 使用多核CPU提升并发性能
- 使用高速网络提升API调用速度 |

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

### v2.0.2 (2024-12-25)

#### 新增功能

- 初始版本发布
- 实现基本的图片浏览和管理功能
- 智能整理功能：支持按时间、设备等多维度分类
- 去重功能：基于MD5哈希算法检测重复文件
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