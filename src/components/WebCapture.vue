<template>
  <div class="web-capture">
    <!-- 控制栏 -->
    <div class="control-bar">
      <div class="url-input">
        <el-input
          v-model="currentUrl"
          placeholder="输入网址或搜索内容"
          clearable
          @keyup.enter="navigateToUrl"
        >
          <template #prepend>
            <el-button @click="goBack" :disabled="!canGoBack">
              <el-icon><ArrowLeft /></el-icon>
            </el-button>
            <el-button @click="goForward" :disabled="!canGoForward">
              <el-icon><ArrowRight /></el-icon>
            </el-button>
            <el-button @click="reload">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </template>
          <template #append>
            <el-button @click="navigateToUrl">
              <el-icon><Search /></el-icon>
            </el-button>
          </template>
        </el-input>
      </div>
      
      <div class="capture-controls">
        <el-button-group>
          <el-button 
            type="primary" 
            @click="startSelection"
            :class="{ active: captureMode === 'selection' }"
          >
            <el-icon><Mouse /></el-icon>
            选择采集
          </el-button>
          <el-button 
            @click="captureFullPage"
            :class="{ active: captureMode === 'fullpage' }"
          >
            <el-icon><FullScreen /></el-icon>
            整页截图
          </el-button>
          <el-button 
            @click="captureVisible"
            :class="{ active: captureMode === 'visible' }"
          >
            <el-icon><View /></el-icon>
            可见区域
          </el-button>
        </el-button-group>
        
        <el-button @click="showBookmarks">
          <el-icon><Star /></el-icon>
          书签
        </el-button>
        
        <el-button @click="closeCapture" type="danger">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </div>

    <!-- 网页内容区域 -->
    <div class="web-content">
      <!-- 网页视图 -->
      <div 
        v-if="!showBookmarkPanel"
        class="web-view"
        ref="webViewRef"
        @mousedown="handleMouseDown"
        @mousemove="handleMouseMove"
        @mouseup="handleMouseUp"
      >
        <!-- 选择区域高亮 -->
        <div 
          v-if="selection.active && selectionRect"
          class="selection-overlay"
          :style="{
            left: selectionRect.x + 'px',
            top: selectionRect.y + 'px',
            width: selectionRect.width + 'px',
            height: selectionRect.height + 'px'
          }"
        >
          <div class="selection-info">
            {{ selectionRect.width }} × {{ selectionRect.height }}
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-overlay">
          <el-icon class="loading-icon"><Loading /></el-icon>
          <span>加载中...</span>
        </div>
        
        <!-- 网页内容占位 -->
        <div v-if="!currentUrl" class="welcome-screen">
          <div class="welcome-content">
            <el-icon size="64" color="var(--el-color-primary)">
              <Globe />
            </el-icon>
            <h2>网页素材采集器</h2>
            <p>输入网址开始采集网页中的图片和内容</p>
            
            <div class="quick-links">
              <div 
                v-for="site in popularSites" 
                :key="site.name"
                class="quick-link"
                @click="navigateToQuickLink(site.url)"
              >
                <el-avatar :size="32" :src="site.icon" />
                <span>{{ site.name }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 书签面板 -->
      <div v-else class="bookmark-panel">
        <div class="panel-header">
          <h3>我的书签</h3>
          <el-button size="small" @click="addCurrentBookmark">
            <el-icon><Plus /></el-icon>
            添加当前页面
          </el-button>
        </div>
        
        <div class="bookmark-list">
          <div 
            v-for="bookmark in bookmarks" 
            :key="bookmark.id"
            class="bookmark-item"
            @click="navigateToBookmark(bookmark)"
          >
            <el-avatar :size="32" :src="bookmark.favicon" />
            <div class="bookmark-info">
              <div class="bookmark-title">{{ bookmark.title }}</div>
              <div class="bookmark-url">{{ bookmark.url }}</div>
            </div>
            <el-button 
              size="small" 
              text 
              @click.stop="removeBookmark(bookmark.id)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>
          
          <div v-if="bookmarks.length === 0" class="empty-bookmarks">
            <el-icon size="48" color="var(--el-text-color-placeholder)">
              <Star />
            </el-icon>
            <p>暂无书签</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 采集结果面板 -->
    <div class="capture-results" v-if="capturedItems.length > 0">
      <div class="results-header">
        <span>采集结果 ({{ capturedItems.length }})</span>
        <el-button size="small" @click="importAll">导入全部</el-button>
      </div>
      
      <div class="results-grid">
        <div
          v-for="item in capturedItems"
          :key="item.id"
          class="capture-item"
          :class="{ selected: selectedItems.includes(item.id) }"
          @click="toggleItemSelection(item)"
        >
          <div class="item-thumbnail">
            <img v-if="item.type === 'image'" :src="item.data" :alt="item.title" />
            <div v-else class="text-preview">
              <el-icon><Document /></el-icon>
            </div>
            <div class="item-overlay">
              <el-button size="small" circle @click.stop="previewItem(item)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button size="small" circle @click.stop="removeItem(item.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div class="item-info">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-source">{{ item.source }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 采集设置 -->
    <el-drawer
      v-model="showSettings"
      title="采集设置"
      direction="rtl"
      size="300px"
    >
      <div class="capture-settings">
        <el-form label-width="80px">
          <el-form-item label="图片质量">
            <el-select v-model="settings.quality">
              <el-option label="高" value="high"></el-option>
              <el-option label="中" value="medium"></el-option>
              <el-option label="低" value="low"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="自动保存">
            <el-switch v-model="settings.autoSave" />
          </el-form-item>
          
          <el-form-item label="添加水印">
            <el-switch v-model="settings.addWatermark" />
          </el-form-item>
          
          <el-form-item label="默认标签">
            <el-input v-model="settings.defaultTags" placeholder="网页采集,截图" />
          </el-form-item>
          
          <el-form-item label="保存格式">
            <el-radio-group v-model="settings.format">
              <el-radio label="png">PNG</el-radio>
              <el-radio label="jpg">JPG</el-radio>
              <el-radio label="webp">WebP</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'

// 图标导入
import {
  ArrowLeft,
  ArrowRight,
  Refresh,
  Search,
  Close,
  Mouse,
  FullScreen,
  View,
  Star,
  Loading,
  Globe,
  Plus,
  Delete,
  Document
} from '@element-plus/icons-vue'

const emit = defineEmits(['close'])
const libraryStore = useLibraryStore()

// 响应式数据
const currentUrl = ref('')
const captureMode = ref<'selection' | 'fullpage' | 'visible'>('selection')
const showBookmarkPanel = ref(false)
const showSettings = ref(false)
const isLoading = ref(false)
const canGoBack = ref(false)
const canGoForward = ref(false)

// 选择区域
const selection = reactive({
  active: false,
  startX: 0,
  startY: 0,
  endX: 0,
  endY: 0
})

const selectionRect = ref({
  x: 0,
  y: 0,
  width: 0,
  height: 0
})

// 采集设置
const settings = reactive({
  quality: 'high' as 'high' | 'medium' | 'low',
  autoSave: true,
  addWatermark: false,
  defaultTags: '网页采集,截图',
  format: 'png' as 'png' | 'jpg' | 'webp'
})

// 采集结果
const capturedItems = ref<any[]>([])
const selectedItems = ref<string[]>([])

// 书签数据
const bookmarks = ref<any[]>([])

// 热门网站
const popularSites = ref([
  { name: 'Unsplash', url: 'https://unsplash.com', icon: '' },
  { name: 'Pinterest', url: 'https://pinterest.com', icon: '' },
  { name: 'Dribbble', url: 'https://dribbble.com', icon: '' },
  { name: 'Behance', url: 'https://behance.net', icon: '' },
  { name: '花瓣网', url: 'https://huaban.com', icon: '' }
])

// 方法
const navigateToUrl = () => {
  if (!currentUrl.value) return
  
  // 添加协议前缀
  let url = currentUrl.value
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    url = 'https://' + url
  }
  
  isLoading.value = true
  currentUrl.value = url
  
  // 模拟网页加载
  setTimeout(() => {
    isLoading.value = false
    canGoBack.value = true
  }, 1000)
}

const navigateToQuickLink = (url: string) => {
  currentUrl.value = url
  navigateToUrl()
}

const goBack = () => {
  if (canGoBack.value) {
    canGoForward.value = true
    // 模拟后退操作
  }
}

const goForward = () => {
  if (canGoForward.value) {
    // 模拟前进操作
  }
}

const reload = () => {
  isLoading.value = true
  setTimeout(() => {
    isLoading.value = false
  }, 500)
}

const startSelection = () => {
  captureMode.value = 'selection'
  selection.active = true
}

const captureFullPage = async () => {
  captureMode.value = 'fullpage'
  
  try {
    const screenshot = await window.electronAPI.captureFullPage(currentUrl.value)
    if (screenshot) {
      addCapturedItem({
        type: 'image',
        data: screenshot,
        title: `整页截图_${Date.now()}`,
        source: currentUrl.value
      })
      ElMessage.success('整页截图已添加到采集结果')
    }
  } catch (error) {
    console.error('整页截图失败:', error)
    ElMessage.error('截图失败')
  }
}

const captureVisible = async () => {
  captureMode.value = 'visible'
  
  try {
    const screenshot = await window.electronAPI.captureVisibleArea(currentUrl.value)
    if (screenshot) {
      addCapturedItem({
        type: 'image',
        data: screenshot,
        title: `可见区域_${Date.now()}`,
        source: currentUrl.value
      })
      ElMessage.success('可见区域截图已添加到采集结果')
    }
  } catch (error) {
    console.error('可见区域截图失败:', error)
    ElMessage.error('截图失败')
  }
}

const handleMouseDown = (event: MouseEvent) => {
  if (captureMode.value !== 'selection') return
  
  selection.active = true
  selection.startX = event.clientX
  selection.startY = event.clientY
  selection.endX = event.clientX
  selection.endY = event.clientY
  
  updateSelectionRect()
}

const handleMouseMove = (event: MouseEvent) => {
  if (!selection.active) return
  
  selection.endX = event.clientX
  selection.endY = event.clientY
  updateSelectionRect()
}

const handleMouseUp = async () => {
  if (!selection.active) return
  
  selection.active = false
  
  if (selectionRect.value.width > 10 && selectionRect.value.height > 10) {
    // 捕获选择区域
    try {
      const screenshot = await window.electronAPI.captureSelection(
        currentUrl.value,
        selectionRect.value
      )
      
      if (screenshot) {
        addCapturedItem({
          type: 'image',
          data: screenshot,
          title: `选择区域_${Date.now()}`,
          source: currentUrl.value
        })
        ElMessage.success('选择区域截图已添加到采集结果')
      }
    } catch (error) {
      console.error('选择区域截图失败:', error)
      ElMessage.error('截图失败')
    }
  }
  
  // 重置选择区域
  selectionRect.value = { x: 0, y: 0, width: 0, height: 0 }
}

const updateSelectionRect = () => {
  const x = Math.min(selection.startX, selection.endX)
  const y = Math.min(selection.startY, selection.endY)
  const width = Math.abs(selection.endX - selection.startX)
  const height = Math.abs(selection.endY - selection.startY)
  
  selectionRect.value = { x, y, width, height }
}

const addCapturedItem = (item: any) => {
  const newItem = {
    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    ...item,
    timestamp: new Date()
  }
  
  capturedItems.value.unshift(newItem)
  
  // 自动保存设置
  if (settings.autoSave) {
    importItem(newItem)
  }
}

const toggleItemSelection = (item: any) => {
  const index = selectedItems.value.indexOf(item.id)
  if (index >= 0) {
    selectedItems.value.splice(index, 1)
  } else {
    selectedItems.value.push(item.id)
  }
}

const previewItem = (item: any) => {
  // 预览采集的项目
  window.electronAPI.previewImage(item.data)
}

const removeItem = (itemId: string) => {
  const index = capturedItems.value.findIndex(item => item.id === itemId)
  if (index >= 0) {
    capturedItems.value.splice(index, 1)
    
    // 同时从选中项中移除
    const selectedIndex = selectedItems.value.indexOf(itemId)
    if (selectedIndex >= 0) {
      selectedItems.value.splice(selectedIndex, 1)
    }
  }
}

const importItem = async (item: any) => {
  try {
    await libraryStore.importWebCapture(item, settings)
    ElMessage.success('素材导入成功')
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  }
}

const importAll = async () => {
  if (capturedItems.value.length === 0) {
    ElMessage.warning('没有可导入的项目')
    return
  }
  
  const itemsToImport = selectedItems.value.length > 0 
    ? capturedItems.value.filter(item => selectedItems.value.includes(item.id))
    : capturedItems.value
  
  try {
    for (const item of itemsToImport) {
      await importItem(item)
    }
    
    ElMessage.success(`成功导入 ${itemsToImport.length} 个项目`)
    
    // 清空采集结果
    capturedItems.value = []
    selectedItems.value = []
  } catch (error) {
    console.error('批量导入失败:', error)
    ElMessage.error('导入失败')
  }
}

const showBookmarks = () => {
  showBookmarkPanel.value = !showBookmarkPanel.value
  loadBookmarks()
}

const loadBookmarks = () => {
  // 从本地存储加载书签
  const saved = localStorage.getItem('webCaptureBookmarks')
  if (saved) {
    bookmarks.value = JSON.parse(saved)
  }
}

const addCurrentBookmark = async () => {
  if (!currentUrl.value) {
    ElMessage.warning('当前没有打开的网页')
    return
  }
  
  try {
    const { value: title } = await ElMessageBox.prompt(
      '请输入书签标题',
      '添加书签',
      {
        confirmButtonText: '添加',
        cancelButtonText: '取消',
        inputValue: `网页采集_${new Date().toLocaleDateString()}`
      }
    )
    
    if (title) {
      const newBookmark = {
        id: Date.now().toString(),
        title,
        url: currentUrl.value,
        favicon: '',
        createdAt: new Date()
      }
      
      bookmarks.value.unshift(newBookmark)
      saveBookmarks()
      ElMessage.success('书签添加成功')
    }
  } catch (error) {
    // 用户取消操作
  }
}

const navigateToBookmark = (bookmark: any) => {
  currentUrl.value = bookmark.url
  navigateToUrl()
  showBookmarkPanel.value = false
}

const removeBookmark = async (bookmarkId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个书签吗？',
      '删除书签',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    bookmarks.value = bookmarks.value.filter(b => b.id !== bookmarkId)
    saveBookmarks()
    ElMessage.success('书签删除成功')
  } catch (error) {
    // 用户取消操作
  }
}

const saveBookmarks = () => {
  localStorage.setItem('webCaptureBookmarks', JSON.stringify(bookmarks.value))
}

const closeCapture = () => {
  emit('close')
}

// 生命周期
onMounted(() => {
  // 加载书签
  loadBookmarks()
  
  // 监听键盘事件
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

const handleKeyDown = (event: KeyboardEvent) => {
  // ESC键关闭选择模式
  if (event.key === 'Escape' && selection.active) {
    selection.active = false
    selectionRect.value = { x: 0, y: 0, width: 0, height: 0 }
  }
  
  // Ctrl+D 添加书签
  if (event.ctrlKey && event.key === 'd') {
    event.preventDefault()
    addCurrentBookmark()
  }
  
  // Ctrl+S 保存设置
  if (event.ctrlKey && event.key === 's') {
    event.preventDefault()
    showSettings.value = true
  }
}
</script>

<style scoped lang="scss">
@use '@/styles/index.scss' as global;

.web-capture {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.control-bar {
  padding: 16px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  gap: 16px;
  align-items: center;
  flex-shrink: 0;
}

.url-input {
  flex: 1;
  
  .el-input-group__prepend {
    .el-button {
      padding: 8px 12px;
      
      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }
}

.capture-controls {
  display: flex;
  gap: 8px;
  align-items: center;
  
  .el-button {
    &.active {
      background: var(--el-color-primary);
      color: white;
    }
  }
}

.web-content {
  flex: 1;
  display: flex;
  overflow: hidden;
  position: relative;
}

.web-view {
  flex: 1;
  position: relative;
  background: white;
  margin: 16px;
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  overflow: hidden;
}

.selection-overlay {
  position: absolute;
  border: 2px solid var(--el-color-primary);
  background: rgba(64, 158, 255, 0.1);
  z-index: 10;
  pointer-events: none;
  
  .selection-info {
    position: absolute;
    top: -30px;
    left: 0;
    background: var(--el-color-primary);
    color: white;
    padding: 4px 8px;
    border-radius: 4px;
    font-size: 12px;
    white-space: nowrap;
  }
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.9);
  z-index: 5;
  
  .loading-icon {
    font-size: 32px;
    margin-bottom: 16px;
    color: var(--el-color-primary);
    animation: spin 1s linear infinite;
  }
  
  span {
    color: var(--el-text-color-secondary);
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.welcome-screen {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  
  .welcome-content {
    text-align: center;
    max-width: 400px;
    
    h2 {
      margin: 16px 0 8px;
      color: var(--el-text-color-primary);
    }
    
    p {
      color: var(--el-text-color-secondary);
      margin-bottom: 24px;
    }
  }
}

.quick-links {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  
  .quick-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 16px;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    cursor: pointer;
    transition: all 0.2s ease;
    
    &:hover {
      border-color: var(--el-color-primary);
      background: var(--el-color-primary-light-9);
    }
    
    span {
      margin-top: 8px;
      font-size: 14px;
      color: var(--el-text-color-primary);
    }
  }
}

.bookmark-panel {
  width: 300px;
  background: var(--el-bg-color);
  border-left: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  h3 {
    margin: 0;
    color: var(--el-text-color-primary);
  }
}

.bookmark-list {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
}

.bookmark-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s ease;
  margin-bottom: 8px;
  
  &:hover {
    background: var(--el-bg-color-page);
  }
  
  .bookmark-info {
    flex: 1;
    margin-left: 12px;
    
    .bookmark-title {
      font-size: 14px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
    }
    
    .bookmark-url {
      font-size: 12px;
      color: var(--el-text-color-secondary);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

.empty-bookmarks {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin-top: 16px;
  }
}

.capture-results {
  height: 200px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
}

.results-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  span {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
}

.results-grid {
  flex: 1;
  display: flex;
  overflow-x: auto;
  padding: 8px;
  gap: 8px;
}

.capture-item {
  width: 120px;
  flex-shrink: 0;
  border: 2px solid transparent;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--el-border-color);
    
    .item-overlay {
      opacity: 1;
    }
  }
  
  &.selected {
    border-color: var(--el-color-primary);
  }
}

.item-thumbnail {
  position: relative;
  height: 80px;
  background: var(--el-bg-color-page);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .text-preview {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    
    .el-icon {
      font-size: 24px;
      color: var(--el-text-color-placeholder);
    }
  }
}

.item-overlay {
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
  transition: opacity 0.2s ease;
}

.item-info {
  padding: 8px;
  
  .item-title {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .item-source {
    font-size: 10px;
    color: var(--el-text-color-secondary);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
}

.capture-settings {
  padding: 20px;
}

@media (max-width: 768px) {
  .control-bar {
    flex-direction: column;
    gap: 12px;
  }
  
  .url-input {
    width: 100%;
  }
  
  .capture-controls {
    width: 100%;
    justify-content: space-between;
  }
  
  .web-view {
    margin: 8px;
  }
  
  .bookmark-panel {
    width: 100%;
  }
  
  .quick-links {
    grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  }
}
</style>