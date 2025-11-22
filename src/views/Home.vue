<template>
  <div class="home-container">
    <!-- 欢迎页面 -->
    <div v-if="!currentLibrary" class="welcome-page">
      <div class="welcome-content">
        <div class="welcome-header">
          <el-icon size="64" color="var(--el-color-primary)">
            <FolderOpened />
          </el-icon>
          <h1>欢迎使用 LeafView</h1>
          <p>您的数字素材管理专家，对标 Eagle 的强大功能</p>
        </div>

        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="createLibrary">
            <el-icon><Plus /></el-icon>
            创建新素材库
          </el-button>
          <el-button size="large" @click="openLibrary">
            <el-icon><FolderOpened /></el-icon>
            打开现有素材库
          </el-button>
        </div>

        <div class="recent-libraries" v-if="recentLibraries.length > 0">
          <h3>最近打开的素材库</h3>
          <div class="library-list">
            <div 
              v-for="lib in recentLibraries" 
              :key="lib.id"
              class="library-item"
              @click="openLibraryFromRecent(lib)"
            >
              <el-icon size="24"><Folder /></el-icon>
              <div class="library-info">
                <div class="library-name">{{ lib.name }}</div>
                <div class="library-path">{{ lib.path }}</div>
                <div class="library-stats">
                  {{ lib.assetCount }} 个素材 • {{ formatFileSize(lib.size) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="feature-showcase">
          <h3>核心功能特性</h3>
          <div class="features-grid">
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-primary)">
                <UploadFilled />
              </el-icon>
              <h4>高效素材收集</h4>
              <p>支持拖拽、截图、网页采集等多种方式</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-success)">
                <Collection />
              </el-icon>
              <h4>智能整理</h4>
              <p>自动分类、标签管理、智能文件夹</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-warning)">
                <Search />
              </el-icon>
              <h4>精准检索</h4>
              <p>多条件筛选、关键词搜索、颜色搜索</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-danger)">
                <Edit />
              </el-icon>
              <h4>素材处理</h4>
              <p>批量编辑、格式转换、水印添加</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 素材库主界面 - 三栏布局 -->
    <div v-else class="library-interface">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentLibrary.name }}</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentFolder">{{ currentFolder.name }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="toolbar-center">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索素材..."
            clearable
            style="width: 300px"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="toolbar-right">
          <el-button-group>
            <el-button 
              :type="viewMode === 'grid' ? 'primary' : ''"
              @click="viewMode = 'grid'"
            >
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button 
              :type="viewMode === 'list' ? 'primary' : ''"
              @click="viewMode = 'list'"
            >
              <el-icon><List /></el-icon>
            </el-button>
            <el-button 
              :type="viewMode === 'masonry' ? 'primary' : ''"
              @click="viewMode = 'masonry'"
            >
              <el-icon><Picture /></el-icon>
            </el-button>
          </el-button-group>
          
          <el-dropdown @command="handleViewCommand">
            <el-button>
              <el-icon><Setting /></el-icon>
              视图
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="thumbnailSize">缩略图大小</el-dropdown-item>
                <el-dropdown-item command="showMetadata">显示元数据</el-dropdown-item>
                <el-dropdown-item command="groupBy">分组方式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 三栏布局 -->
      <div class="main-layout">
        <!-- 左侧侧边栏 -->
        <div class="sidebar-container">
          <Sidebar 
            @folder-click="handleFolderClick"
            @tag-click="handleTagClick"
            @search-panel-toggle="searchPanelVisible = !searchPanelVisible"
          />
        </div>
        
        <!-- 中间内容区域 -->
        <div class="content-container">
          <!-- 搜索面板 -->
          <div class="search-panel" v-show="searchPanelVisible">
            <SearchPanel @search="handleSearch" />
          </div>
          
          <!-- 素材展示 -->
          <div class="assets-container">
            <div 
              class="assets-grid"
              :class="viewMode + '-view'"
            >
              <div
                v-for="asset in filteredAssets"
                :key="asset.id"
                class="asset-item"
                :class="{ selected: selectedAssets.includes(asset.id) }"
                @click="selectAsset(asset)"
                @dblclick="openAsset(asset)"
              >
                <div class="asset-thumbnail-container">
                  <img 
                    :src="getThumbnailUrl(asset)" 
                    :alt="asset.name"
                    class="asset-thumbnail"
                    @error="handleImageError"
                  />
                  <div class="asset-overlay">
                    <el-icon class="asset-type-icon">
                      <component :is="getAssetTypeIcon(asset.type)" />
                    </el-icon>
                    <div class="asset-actions">
                      <el-button size="small" circle @click.stop="previewAsset(asset)">
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button size="small" circle @click.stop="editAsset(asset)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
                
                <div class="asset-info">
                  <div class="asset-name">{{ asset.name }}</div>
                  <div class="asset-meta">
                    {{ formatFileSize(asset.size) }} • {{ formatDate(asset.createdAt) }}
                  </div>
                  <div class="asset-tags">
                    <el-tag
                      v-for="tag in asset.tags.slice(0, 2)"
                      :key="tag"
                      size="small"
                      class="tag"
                    >
                      {{ tag }}
                    </el-tag>
                    <span v-if="asset.tags.length > 2" class="more-tags">
                      +{{ asset.tags.length - 2 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="filteredAssets.length === 0" class="empty-state">
              <el-icon size="64" color="var(--el-text-color-placeholder)">
                <Files />
              </el-icon>
              <p>暂无素材</p>
              <el-button type="primary" @click="importAssets">
                <el-icon><Plus /></el-icon>
                导入素材
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 右侧详情面板 -->
        <div class="detail-panel" v-if="selectedAsset">
          <DetailPanel 
            :asset="selectedAsset"
            @close="selectedAsset = null"
          />
        </div>
      </div>
    </div>

    <!-- 素材导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入素材"
      width="600px"
    >
      <ImportAssets @close="showImportDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLibraryStore } from '@/stores/library'
import { useThemeStore } from '@/stores/theme'
import { Library, Asset, Folder } from '@/types'
import ImportAssets from '@/components/ImportAssets.vue'
import Sidebar from '@/components/Sidebar.vue'
import SearchPanel from '@/components/SearchPanel.vue'
import DetailPanel from '@/components/DetailPanel.vue'

// 图标导入
import {
  FolderOpened,
  Plus,
  Folder,
  UploadFilled,
  Collection,
  Search,
  Edit,
  Grid,
  List,
  Picture,
  Setting,
  View,
  Files
} from '@element-plus/icons-vue'

const libraryStore = useLibraryStore()
const themeStore = useThemeStore()

// 响应式数据
const currentLibrary = ref<Library | null>(null)
const currentFolder = ref<Folder | null>(null)
const recentLibraries = ref<Library[]>([])
const searchKeyword = ref('')
const viewMode = ref<'grid' | 'list' | 'masonry'>('grid')
const selectedAssets = ref<string[]>([])
const showImportDialog = ref(false)
const selectedAsset = ref<Asset | null>(null)
const searchPanelVisible = ref(false)

// 计算属性
const filteredAssets = computed(() => {
  let assets = mockAssets // 使用模拟数据
  
  // 根据当前文件夹过滤
  if (currentFolder.value) {
    // 模拟按文件夹过滤
    if (currentFolder.value.name === '插画') {
      assets = assets.filter(asset => asset.id === '2')
    } else if (currentFolder.value.name === '摄影') {
      assets = assets.filter(asset => asset.id === '3')
    } else if (currentFolder.value.name === '包装模板') {
      assets = assets.filter(asset => asset.id === '4')
    } else if (currentFolder.value.name === '室内设计') {
      assets = assets.filter(asset => asset.id === '5')
    } else if (currentFolder.value.name === 'AI咒语') {
      assets = assets.filter(asset => asset.id === '1')
    }
  }
  
  // 根据搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    assets = assets.filter(asset => 
      asset.name.toLowerCase().includes(keyword) ||
      asset.tags.some(tag => tag.toLowerCase().includes(keyword))
    )
  }
  
  return assets
})

// 方法
const createLibrary = async () => {
  try {
    const library = await libraryStore.createLibrary('新素材库', '')
    currentLibrary.value = library
  } catch (error) {
    console.error('创建素材库失败:', error)
  }
const openLibrary = async () => {
  try {
    const library = await libraryStore.openLibrary()
    if (library) {
      currentLibrary.value = library
      addToRecentLibraries(library)
    }
  } catch (error) {
    console.error('打开素材库失败:', error)
  }
}

// 处理侧边栏交互
const handleFolderClick = (folder: Folder) => {
  currentFolder.value = folder
  selectedAsset.value = null
}

const handleTagClick = (tag: string) => {
  // 实现标签筛选逻辑
  searchKeyword.value = tag
  selectedAsset.value = null
}

const handleSearch = (filters: any) => {
  // 实现高级搜索逻辑
  searchKeyword.value = filters.keyword || ''
  searchPanelVisible.value = false
}

const selectAsset = (asset: Asset) => {
  // 实现单选逻辑
  selectedAssets.value = [asset.id]
  selectedAsset.value = asset
}

// 模拟数据 - 用于展示
const mockAssets: Asset[] = [
  {
    id: '1',
    name: 'Cat & Starry Night',
    path: '',
    type: 'image',
    size: 2097152,
    width: 1920,
    height: 1080,
    createdAt: new Date('2024-04-25'),
    modifiedAt: new Date('2024-04-25'),
    tags: ['Prompt', 'Midjourney'],
    rating: 5,
    metadata: {
      format: 'jpg',
      dominantColor: '#1a2b3c'
    }
  },
  {
    id: '2',
    name: 'Stylized Human',
    path: '',
    type: 'image',
    size: 1572864,
    width: 1500,
    height: 2250,
    createdAt: new Date('2024-04-25'),
    modifiedAt: new Date('2024-04-25'),
    tags: ['风格化', 'Procreate'],
    rating: 5,
    metadata: {
      format: 'png',
      dominantColor: '#e63946'
    }
  },
  {
    id: '3',
    name: '首尔塔',
    path: '',
    type: 'image',
    size: 886000,
    width: 2666,
    height: 3999,
    createdAt: new Date('2024-04-25'),
    modifiedAt: new Date('2024-04-25'),
    tags: ['自然光', '建筑', 'SONY ILCE-6700'],
    rating: 5,
    metadata: {
      format: 'jpg',
      camera: 'SONY ILCE-6700',
      dominantColor: '#457b9d'
    }
  },
  {
    id: '4',
    name: 'Free milk mockup',
    path: '',
    type: 'image',
    size: 2990000,
    width: 1292,
    height: 1292,
    createdAt: new Date('2024-04-25'),
    modifiedAt: new Date('2024-04-25'),
    tags: ['盒装', 'Mockup', 'Photoshop'],
    rating: 5,
    metadata: {
      format: 'psd',
      dominantColor: '#f1faee'
    }
  },
  {
    id: '5',
    name: '起居室',
    path: '',
    type: 'image',
    size: 1722900,
    width: 1800,
    height: 1800,
    createdAt: new Date('2024-04-25'),
    modifiedAt: new Date('2024-04-25'),
    tags: ['北欧风格', '起居室'],
    rating: 5,
    metadata: {
      format: 'jpg',
      dominantColor: '#a8dadc'
    }
  }
]

// 模拟文件夹数据
const mockFolders: Folder[] = [
  { id: '1', name: 'AI咒语', parentId: null, createdAt: new Date() },
  { id: '2', name: '插画', parentId: null, createdAt: new Date() },
  { id: '3', name: '摄影', parentId: null, createdAt: new Date() },
  { id: '4', name: '室内设计', parentId: null, createdAt: new Date() },
  { id: '5', name: '游戏概念', parentId: null, createdAt: new Date() },
  { id: '6', name: 'UI设计', parentId: null, createdAt: new Date() },
  { id: '7', name: '包装模板', parentId: null, createdAt: new Date() },
  { id: '8', name: '图标', parentId: null, createdAt: new Date() }
]

const openLibraryFromRecent = (library: Library) => {
  currentLibrary.value = library
  libraryStore.setCurrentLibrary(library)
}

const addToRecentLibraries = (library: Library) => {
  const existingIndex = recentLibraries.value.findIndex(lib => lib.id === library.id)
  if (existingIndex >= 0) {
    recentLibraries.value.splice(existingIndex, 1)
  }
  recentLibraries.value.unshift(library)
  
  // 限制最近打开数量
  if (recentLibraries.value.length > 5) {
    recentLibraries.value = recentLibraries.value.slice(0, 5)
  }
  
  // 保存到本地存储
  localStorage.setItem('recentLibraries', JSON.stringify(recentLibraries.value))
}

const selectAsset = (asset: Asset) => {
  const index = selectedAssets.value.indexOf(asset.id)
  if (index >= 0) {
    selectedAssets.value.splice(index, 1)
  } else {
    selectedAssets.value.push(asset.id)
  }
}

const openAsset = (asset: Asset) => {
  // 打开素材预览
  console.log('打开素材:', asset)
}

const previewAsset = (asset: Asset) => {
  // 预览素材
  console.log('预览素材:', asset)
}

const editAsset = (asset: Asset) => {
  // 编辑素材
  console.log('编辑素材:', asset)
}

const importAssets = () => {
  showImportDialog.value = true
}

const getThumbnailUrl = (asset: Asset) => {
  // 返回模拟图片URL
  if (asset.id === '1') return 'https://picsum.photos/id/433/500/300'
  if (asset.id === '2') return 'https://picsum.photos/id/429/500/750'
  if (asset.id === '3') return 'https://picsum.photos/id/424/500/750'
  if (asset.id === '4') return 'https://picsum.photos/id/425/500/500'
  if (asset.id === '5') return 'https://picsum.photos/id/426/500/500'
  return 'https://picsum.photos/500/500'
}

const handleImageError = (event: Event) => {
  // 处理图片加载错误
  const img = event.target as HTMLImageElement
  img.src = '/placeholder-image.png'
}

const getAssetTypeIcon = (type: string) => {
  const icons = {
    image: 'Picture',
    video: 'VideoPlay',
    audio: 'Headphone',
    document: 'Document',
    other: 'File'
  }
  return icons[type as keyof typeof icons] || 'File'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString('zh-CN')
}

const handleViewCommand = (command: string) => {
  switch (command) {
    case 'thumbnailSize':
      // 设置缩略图大小
      break
    case 'showMetadata':
      // 切换显示元数据
      break
    case 'groupBy':
      // 设置分组方式
      break
  }
}

// 生命周期
onMounted(() => {
  // 加载最近打开的素材库
  const saved = localStorage.getItem('recentLibraries')
  if (saved) {
    recentLibraries.value = JSON.parse(saved)
  }
  
  // 设置当前素材库
  if (libraryStore.currentLibrary) {
    currentLibrary.value = libraryStore.currentLibrary
  }
  
  // 初始化模拟数据到store
  libraryStore.folders = mockFolders
  libraryStore.assets = mockAssets
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.home-container {
  height: 100vh;
  background: var(--el-bg-color-page);
}

.welcome-page {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
}

.welcome-content {
  max-width: 800px;
  text-align: center;
}

.welcome-header {
  margin-bottom: 60px;
  
  h1 {
    font-size: 36px;
    font-weight: 600;
    margin: 20px 0 10px;
    color: var(--el-text-color-primary);
  }
  
  p {
    font-size: 16px;
    color: var(--el-text-color-secondary);
  }
}

.welcome-actions {
  margin-bottom: 60px;
  
  .el-button {
    margin: 0 12px;
    padding: 12px 24px;
    font-size: 16px;
  }
}

.recent-libraries {
  margin-bottom: 60px;
  
  h3 {
    margin-bottom: 20px;
    color: var(--el-text-color-primary);
  }
}

.library-list {
  display: grid;
  gap: 12px;
  max-width: 500px;
  margin: 0 auto;
}

.library-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  background: var(--el-bg-color);
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: var(--el-box-shadow-light);
  }
  
  .el-icon {
    margin-right: 12px;
    color: var(--el-color-primary);
  }
}

.library-info {
  flex: 1;
  
  .library-name {
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 4px;
  }
  
  .library-path {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 4px;
  }
  
  .library-stats {
    font-size: 12px;
    color: var(--el-text-color-placeholder);
  }
}

.feature-showcase {
  h3 {
    margin-bottom: 30px;
    color: var(--el-text-color-primary);
  }
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 30px;
  max-width: 600px;
  margin: 0 auto;
}

.feature-item {
  text-align: center;
  padding: 20px;
  
  h4 {
    margin: 12px 0 8px;
    font-size: 16px;
    color: var(--el-text-color-primary);
  }
  
  p {
    font-size: 14px;
    color: var(--el-text-color-secondary);
    line-height: 1.4;
  }
}

.library-interface {
  height: 100vh;
  display: flex;
  flex-direction: column;
}

.toolbar {
  height: 60px;
  padding: 0 20px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.content-area {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.assets-container {
  flex: 1;
  overflow-y: auto;
}

.assets-grid {
  padding: 20px;
  
  &.grid-view {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
  }
  
  &.list-view {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  
  &.masonry-view {
    column-count: 4;
    column-gap: 16px;
    
    .asset-item {
      break-inside: avoid;
      margin-bottom: 16px;
    }
  }
}

.asset-item {
  border-radius: 8px;
  overflow: hidden;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  transition: all 0.3s ease;
  cursor: pointer;
  
  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: var(--el-box-shadow-light);
    
    .asset-overlay {
      opacity: 1;
    }
  }
  
  &.selected {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px var(--el-color-primary-light-5);
  }
}

.asset-thumbnail-container {
  position: relative;
  overflow: hidden;
}

.asset-thumbnail {
  width: 100%;
  height: 150px;
  object-fit: cover;
  background: var(--el-bg-color-page);
}

.asset-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  
  .asset-type-icon {
    position: absolute;
    top: 8px;
    left: 8px;
    color: white;
    font-size: 16px;
  }
  
  .asset-actions {
    display: flex;
    gap: 8px;
  }
}

.asset-info {
  padding: 12px;
  
  .asset-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .asset-meta {
    font-size: 12px;
    color: var(--el-text-color-secondary);
    margin-bottom: 8px;
  }
  
  .asset-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .more-tags {
    font-size: 11px;
    color: var(--el-text-color-placeholder);
    align-self: center;
  }
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--el-text-color-secondary);
  
  p {
    margin: 16px 0 24px;
    font-size: 16px;
  }
}

@media (max-width: 768px) {
  .welcome-page {
    padding: 20px;
  }
  
  .welcome-header h1 {
    font-size: 28px;
  }
  
  .welcome-actions {
    .el-button {
      display: block;
      width: 100%;
      margin: 8px 0;
    }
  }
  
  .features-grid {
    grid-template-columns: 1fr;
    gap: 20px;
  }
  
  .toolbar {
    flex-direction: column;
    height: auto;
    padding: 12px;
    gap: 12px;
  }
  
  .assets-grid.grid-view {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
    padding: 12px;
  }
  
  .assets-grid.masonry-view {
    column-count: 2;
  }
}
</style>