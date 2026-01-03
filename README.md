# LeafSort Pro

智能相册管理系统 - 基于 Vue 3 + Electron 的桌面应用

## 项目简介

LeafSort Pro 是一个正在开发中的智能相册管理系统，使用现代化的 Web 技术栈构建跨平台桌面应用。项目目前处于早期开发阶段，已完成基础架构搭建和主要页面框架。

## 技术栈

- **前端框架**：Vue 3.2.13
- **UI 组件库**：Element Plus 2.4.4
- **桌面应用**：Electron 27.0.0
- **状态管理**：Pinia 2.1.7
- **路由管理**：Vue Router 4.0.3
- **图标库**：@element-plus/icons-vue 2.3.1
- **开发工具**：Vue CLI 5.0.0

## 项目结构

```
LeafSort/
├── electron/              # Electron 主进程
│   ├── main.js           # 主进程入口
│   └── preload.js        # 预加载脚本
├── public/               # 静态资源
│   └── index.html        # HTML 入口文件
├── src/                  # 源代码
│   ├── components/       # Vue 组件
│   │   └── TitleBar.vue      # 标题栏组件
│   ├── layouts/          # 布局组件
│   │   └── MainLayout.vue    # 主布局组件
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定义
│   ├── utils/            # 工具函数
│   │   ├── database.js   # IndexedDB 数据库封装
│   │   └── index.js      # 通用工具函数
│   ├── views/            # 页面组件
│   │   ├── HomePage.vue       # 首页
│   │   ├── NotFoundView.vue   # 404 页面
│   │   ├── gallery/          # 相册页面
│   │   │   ├── PeopleGallery.vue     # 人物相册
│   │   │   ├── PlacesGallery.vue     # 地点相册
│   │   │   ├── EventsGallery.vue     # 事件相册
│   │   │   ├── EmotionsGallery.vue   # 情感相册
│   │   │   └── ColorsGallery.vue     # 色彩相册
│   │   └── tools/           # 工具页面
│   │       ├── SmartSearch.vue        # 智能搜索
│   │       ├── SmartArrange.vue      # 智能整理
│   │       ├── DeduplicationPage.vue  # 文件去重
│   │       ├── ExifEdit.vue          # EXIF 编辑
│   │       └── BatchProcess.vue      # 批量处理
│   ├── App.vue           # 根组件
│   └── main.js           # 应用入口
├── .gitignore
├── package.json
├── package-lock.json
├── vue.config.js
└── README.md
```

## 当前功能

### 已完成

- **基础架构**：Vue 3 + Electron + Element Plus 集成
- **主布局**：可折叠侧边栏导航，自定义标题栏
- **路由系统**：基于 Vue Router 的单页应用路由
- **状态管理**：Pinia 状态管理集成
- **数据库**：IndexedDB 数据库封装（photos, people, places, events, albums, tags）
- **首页**：轮播图展示和快速访问入口
- **相册页面**：人物、地点、事件、情感、色彩相册的界面框架
- **工具页面**：智能搜索、智能整理、文件去重、EXIF 编辑、批量处理的界面框架

### 开发中

- **核心功能**：图片导入、管理、搜索、标签功能的具体实现
- **数据存储**：本地文件系统管理和数据库操作
- **用户交互**：界面响应和用户体验优化

### 规划中

- **AI 功能**：智能分类、物体识别、情感分析等
- **高级功能**：插件系统、云同步、协作功能
- **性能优化**：大数据量处理、内存管理

## 页面路由

| 路径 | 名称 | 描述 |
|------|------|------|
| `/` | 首页 | 应用首页，展示轮播图和快速访问入口 |
| `/gallery/people` | 人物相册 | 管理和查看人物照片 |
| `/gallery/places` | 地点相册 | 按地理位置管理照片 |
| `/gallery/events` | 事件相册 | 按事件管理照片 |
| `/gallery/emotions` | 情感相册 | 按情感分类管理照片 |
| `/gallery/colors` | 色彩相册 | 按色彩分类管理照片 |
| `/search/smart` | 智能搜索 | 自然语言搜索照片 |
| `/media/smart-arrange` | 智能整理 | 智能整理照片 |
| `/media/deduplication` | 文件去重 | 去除重复照片 |
| `/media/exif-edit` | EXIF 编辑 | 编辑照片 EXIF 信息 |
| `/media/batch-process` | 批量处理 | 批量处理照片 |

## 快速开始

### 环境要求

- Node.js >= 16.0.0
- npm >= 8.0.0

### 安装和运行

```bash
# 克隆项目
git clone https://github.com/your-org/LeafSort.git
cd LeafSort

# 安装依赖
npm install

# 开发模式（同时启动前端服务和 Electron 应用）
npm run electron

# 仅启动前端服务
npm run server

# 代码检查
npm run lint

# 清理构建文件
npm run pack-clean
```

### 可用脚本

- `npm run electron` - 开发模式，同时启动前端服务和 Electron 应用
- `npm run server` - 仅启动前端开发服务（默认端口 8080）
- `npm run lint` - 运行 ESLint 代码检查
- `npm run pack-clean` - 清理构建文件

## 数据库设计

项目使用 IndexedDB 进行本地数据存储，包含以下数据表：

- **photos** - 照片数据（id, date, people, places, events, tags）
- **people** - 人物数据（id, name）
- **places** - 地点数据（id, name）
- **events** - 事件数据（id, date）
- **albums** - 相册数据（id, name）
- **tags** - 标签数据（name, count）

## 开发路线图

### 第一阶段（当前）
- 基础项目架构搭建
- 主界面布局和导航结构
- 基础页面路由和组件结构
- 跨平台桌面应用框架

### 第二阶段
- 图片管理核心功能开发
- 基础搜索和筛选功能
- 标签管理系统实现
- 工具功能具体实现

### 第三阶段
- AI 智能分类功能
- 高级搜索功能
- 插件系统架构
- 云同步服务

## 贡献指南

我们欢迎各种形式的贡献，包括代码、文档、设计、测试等。

### 如何贡献

1. Fork 项目仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循 Vue 3 最佳实践
- 编写清晰的代码注释
- 遵循 ESLint 代码规范
- 更新相关文档

## 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

## 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [Electron](https://electronjs.org/) - 跨平台桌面应用框架
- [Element Plus](https://element-plus.org/) - Vue 3 UI 组件库

---

**LeafSort Pro** - 让每一张照片都有归属，让每一个创意都被珍藏
