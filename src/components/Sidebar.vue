<template>
  <div class="sidebar">
    <!-- 顶部标题 -->
    <div class="sidebar-header">
      <div class="logo">
        <el-icon size="20" color="#00B42A"><FolderOpened /></el-icon>
        <span class="logo-text">Eagle</span>
      </div>
    </div>

    <!-- 快捷导航 -->
    <div class="quick-nav">
      <div class="nav-item active" @click="selectAll">
        <el-icon size="18"><Collection /></el-icon>
        <span>全部</span>
        <span class="count">2553</span>
      </div>
      <div class="nav-item" @click="selectUnclassified">
        <el-icon size="18"><Folder /></el-icon>
        <span>未分类</span>
        <span class="count">1082</span>
      </div>
      <div class="nav-item" @click="selectUntagged">
        <el-icon size="18"><TagIcon /></el-icon>
        <span>未标签</span>
        <span class="count">1882</span>
      </div>
      <div class="nav-item" @click="selectTagManager">
        <el-icon size="18"><Ticket /></el-icon>
        <span>标签管理</span>
        <span class="count">142</span>
      </div>
      <div class="nav-item" @click="selectTrash">
        <el-icon size="18"><Delete /></el-icon>
        <span>回收站</span>
        <span class="count">36</span>
      </div>
    </div>

    <!-- 智能文件夹 -->
    <div class="smart-folders-section">
      <div class="section-title">
        <el-icon size="16"><MagicStick /></el-icon>
        <span>智能文件夹</span>
      </div>
      <div class="nav-item" @click="selectSmartFolder('recent')">
        <el-icon size="18" color="#1677FF"><Clock /></el-icon>
        <span>最近收集</span>
        <span class="count">113</span>
      </div>
    </div>

    <!-- 文件夹树 -->
    <div class="folders-section">
      <!-- 灵感采集 -->
      <div class="folder-group">
        <div class="section-title" @click="toggleFolderGroup('inspiration')">
          <el-icon size="16">{{ isExpanded('inspiration') ? 'ArrowUp' : 'ArrowDown' }}</el-icon>
          <span>灵感采集</span>
          <span class="count">665</span>
        </div>
        <div v-if="isExpanded('inspiration')" class="folder-children">
          <div class="nav-item sub-item" @click="selectFolder('illustration')">
            <el-icon size="18" color="#FF7D00"><Picture /></el-icon>
            <span>插画</span>
            <span class="count">275</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('photography')">
            <el-icon size="18" color="#1677FF"><Camera /></el-icon>
            <span>摄影</span>
            <span class="count">881</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('interior')">
            <el-icon size="18" color="#00B42A"><OfficeBuilding /></el-icon>
            <span>室内设计</span>
            <span class="count">103</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('game')">
            <el-icon size="18" color="#722ED1"><StampFilled /></el-icon>
            <span>游戏概念</span>
            <span class="count">234</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('ui')">
            <el-icon size="18" color="#F53F3F"><Monitor /></el-icon>
            <span>UI设计</span>
            <span class="count">159</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('animation')">
            <el-icon size="18" color="#FF7D00"><VideoCamera /></el-icon>
            <span>动画</span>
            <span class="count">117</span>
          </div>
        </div>
      </div>

      <!-- 设计素材 -->
      <div class="folder-group">
        <div class="section-title" @click="toggleFolderGroup('design')">
          <el-icon size="16">{{ isExpanded('design') ? 'ArrowUp' : 'ArrowDown' }}</el-icon>
          <span>设计素材</span>
          <span class="count">117</span>
        </div>
        <div v-if="isExpanded('design')" class="folder-children">
          <div class="nav-item sub-item" @click="selectFolder('packaging')">
            <el-icon size="18" color="#F7BA1E"><Package /></el-icon>
            <span>包装模板</span>
            <span class="count">108</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('icons')">
            <el-icon size="18" color="#4E5969"><Setting /></el-icon>
            <span>图标</span>
            <span class="count">91</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('fonts')">
            <el-icon size="18" color="#909399"><Font /></el-icon>
            <span>字体</span>
            <span class="count">85</span>
          </div>
          <div class="nav-item sub-item" @click="selectFolder('audio')">
            <el-icon size="18" color="#13C2C2"><Microphone /></el-icon>
            <span>音频</span>
            <span class="count">52</span>
          </div>
        </div>
      </div>

      <!-- 教程 -->
      <div class="folder-group">
        <div class="section-title" @click="toggleFolderGroup('tutorial')">
          <el-icon size="16">{{ isExpanded('tutorial') ? 'ArrowUp' : 'ArrowDown' }}</el-icon>
          <span>教程</span>
          <span class="count">202</span>
        </div>
        <div v-if="isExpanded('tutorial')" class="folder-children">
          <div class="nav-item sub-item" @click="selectFolder('figma')">
            <el-icon size="18" color="#00B42A"><EditPen /></el-icon>
            <span>Figma</span>
            <span class="count">148</span>
          </div>
        </div>
      </div>

      <!-- 精选 -->
      <div class="nav-item" @click="selectFolder('favorites')">
        <el-icon size="18" color="#F7BA1E"><Star /></el-icon>
        <span>精选</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLibraryStore } from '@/stores/library'
import type { Folder } from '@/types'

// 定义事件
const emit = defineEmits<{
  'folder-click': [folderId: string]
  'tag-click': [tagId: string]
  'search-panel-toggle': []
}>()

// Store
const libraryStore = useLibraryStore()

// 响应式数据
const expandedGroups = ref<Record<string, boolean>>({
  inspiration: true,
  design: true,
  tutorial: true
})

// 方法
const toggleFolderGroup = (group: string) => {
  expandedGroups.value[group] = !expandedGroups.value[group]
}

const isExpanded = (group: string) => {
  return expandedGroups.value[group] || false
}

const selectAll = () => {
  emit('folder-click', 'all')
}

const selectUnclassified = () => {
  emit('folder-click', 'unclassified')
}

const selectUntagged = () => {
  emit('folder-click', 'untagged')
}

const selectTagManager = () => {
  emit('folder-click', 'tag-manager')
}

const selectTrash = () => {
  emit('folder-click', 'trash')
}

const selectSmartFolder = (folderId: string) => {
  emit('folder-click', `smart-${folderId}`)
}

const selectFolder = (folderId: string) => {
  emit('folder-click', folderId)
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 图标导入
import {
  FolderOpened,
  Collection,
  Folder,
  TagIcon,
  Ticket,
  Delete,
  MagicStick,
  Clock,
  ArrowUp,
  ArrowDown,
  Picture,
  Camera,
  OfficeBuilding,
  StampFilled,
  Monitor,
  VideoCamera,
  Package,
  Setting,
  Font,
  Microphone,
  EditPen,
  Star
} from '@element-plus/icons-vue'
</script>

<style scoped lang="scss">
.sidebar {
  width: 240px;
  height: 100vh;
  background-color: #1E1E1E;
  border-right: 1px solid #333;
  overflow-y: auto;
  color: #DADADA;
  font-size: 14px;
}

/* 顶部标题 */
.sidebar-header {
  padding: 12px 16px;
  border-bottom: 1px solid #333;
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}

.logo-text {
  font-size: 16px;
  font-weight: 500;
  color: #FFFFFF;
}

/* 快捷导航 */
.quick-nav {
  padding: 8px 0;
  border-bottom: 1px solid #333;
}

/* 导航项通用样式 */
.nav-item {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  cursor: pointer;
  gap: 12px;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    background-color: #2A2A2A;
  }

  &.active {
    background-color: #2A2A2A;
    color: #FFFFFF;

    &::before {
      content: '';
      position: absolute;
      left: 0;
      top: 0;
      height: 100%;
      width: 3px;
      background-color: #00B42A;
    }
  }

  .count {
    margin-left: auto;
    font-size: 12px;
    color: #888;
  }

  &.sub-item {
    padding-left: 40px;
    font-size: 13px;
  }
}

/* 智能文件夹 */
.smart-folders-section {
  padding: 12px 0;
  border-bottom: 1px solid #333;
}

/* 分组标题 */
.section-title {
  display: flex;
  align-items: center;
  padding: 8px 16px;
  font-size: 12px;
  color: #888;
  gap: 6px;
  cursor: pointer;

  &:hover {
    background-color: #2A2A2A;
  }
}

/* 文件夹分组 */
.folders-section {
  padding: 12px 0;
}

.folder-group {
  margin-bottom: 4px;
}

.folder-children {
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 500px;
  }
}
</style>

// 响应式数据
const showAllTags = ref(false)
const expandedKeys = ref<string[]>([])
const contextMenu = ref({
  visible: false,
  x: 0,
  y: 0,
  folder: null as Folder | null
})

// 计算属性
const currentLibrary = computed(() => libraryStore.currentLibrary)
const folders = computed(() => libraryStore.folders)
const tags = computed(() => libraryStore.tags)

const folderTree = computed(() => {
  const tree: any[] = [
    {
      id: 'all',
      label: '所有素材',
      type: 'root',
      assetCount: libraryStore.assets.length
    },
    {
      id: 'recent',
      label: '最近添加',
      type: 'smart-folder',
      assetCount: libraryStore.recentAssets.length
    },
    {
      id: 'untagged',
      label: '未标记',
      type: 'smart-folder',
      assetCount: libraryStore.untaggedAssets.length
    }
  ]
  
  // 添加普通文件夹
  const rootFolders = folders.value.filter(f => !f.parentId)
  rootFolders.forEach(folder => {
    tree.push(buildFolderTree(folder))
  })
  
  return tree
})

const popularTags = computed(() => {
  const sortedTags = [...tags.value].sort((a, b) => b.assetCount - a.assetCount)
  return showAllTags.value ? sortedTags : sortedTags.slice(0, 5)
})

const recentActivities = computed(() => {
  return [
    {
      id: '1',
      type: 'import',
      title: '导入了 5 个图片',
      timestamp: new Date(Date.now() - 1000 * 60 * 5) // 5分钟前
    },
    {
      id: '2',
      type: 'tag',
      title: '为 3 个素材添加了标签',
      timestamp: new Date(Date.now() - 1000 * 60 * 30) // 30分钟前
    },
    {
      id: '3',
      type: 'create',
      title: '创建了新文件夹',
      timestamp: new Date(Date.now() - 1000 * 60 * 60) // 1小时前
    }
  ]
})

// 树形配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 方法
const buildFolderTree = (folder: Folder) => {
  const children = folders.value.filter(f => f.parentId === folder.id)
  return {
    id: folder.id,
    label: folder.name,
    type: 'folder',
    assetCount: folder.assetCount,
    children: children.map(child => buildFolderTree(child))
  }
}

const handleFolderClick = (data: any) => {
  if (data.type === 'folder') {
    libraryStore.setCurrentFolder(data.id)
  } else if (data.type === 'smart-folder') {
    // 处理智能文件夹点击
    switch (data.id) {
      case 'all':
        libraryStore.setCurrentFolder(null)
        break
      case 'recent':
        libraryStore.filterRecentAssets()
        break
      case 'untagged':
        libraryStore.filterUntaggedAssets()
        break
    }
  }
}

const handleFolderContextMenu = (event: Event, data: any) => {
  if (data.type === 'folder') {
    event.preventDefault()
    contextMenu.value = {
      visible: true,
      x: (event as MouseEvent).clientX,
      y: (event as MouseEvent).clientY,
      folder: folders.value.find(f => f.id === data.id) || null
    }
  }
}

const importAssets = () => {
  // 触发导入操作
  libraryStore.showImportDialog = true
}

const takeScreenshot = async () => {
  try {
    const screenshot = await window.electronAPI.takeScreenshot()
    if (screenshot) {
      // 处理截图导入
      await libraryStore.importScreenshot(screenshot)
      ElMessage.success('截图导入成功')
    }
  } catch (error) {
    console.error('截图失败:', error)
    ElMessage.error('截图失败')
  }
}

const startWebCapture = () => {
  // 启动网页采集功能
  window.electronAPI.startWebCapture()
}

const showSmartFolders = () => {
  // 显示智能整理界面
  libraryStore.showSmartFolders = true
}

const showSearch = () => {
  // 显示高级搜索界面
  libraryStore.showAdvancedSearch = true
}

const createFolder = async () => {
  try {
    const { value: folderName } = await ElMessageBox.prompt(
      '请输入文件夹名称',
      '创建文件夹',
      {
        confirmButtonText: '创建',
        cancelButtonText: '取消',
        inputPattern: /^[^\\/:*?"<>|]{1,50}$/,
        inputErrorMessage: '文件夹名称不能包含特殊字符且长度不超过50个字符'
      }
    )
    
    if (folderName) {
      await libraryStore.createFolder(folderName)
      ElMessage.success('文件夹创建成功')
    }
  } catch (error) {
    // 用户取消操作
  }
}

const renameFolder = async () => {
  if (!contextMenu.value.folder) return
  
  try {
    const { value: newName } = await ElMessageBox.prompt(
      '请输入新名称',
      '重命名文件夹',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: contextMenu.value.folder.name,
        inputPattern: /^[^\\/:*?"<>|]{1,50}$/,
        inputErrorMessage: '文件夹名称不能包含特殊字符且长度不超过50个字符'
      }
    )
    
    if (newName) {
      await libraryStore.renameFolder(contextMenu.value.folder!.id, newName)
      ElMessage.success('文件夹重命名成功')
      closeContextMenu()
    }
  } catch (error) {
    // 用户取消操作
  }
}

const deleteFolder = async () => {
  if (!contextMenu.value.folder) return
  
  try {
    await ElMessageBox.confirm(
      `确定要删除文件夹 "${contextMenu.value.folder.name}" 吗？此操作无法撤销。`,
      '删除文件夹',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await libraryStore.deleteFolder(contextMenu.value.folder.id)
    ElMessage.success('文件夹删除成功')
    closeContextMenu()
  } catch (error) {
    // 用户取消操作
  }
}

const exportFolder = () => {
  if (!contextMenu.value.folder) return
  
  // 导出文件夹功能
  window.electronAPI.exportFolder(contextMenu.value.folder.id)
  closeContextMenu()
}

const createTag = async () => {
  try {
    const { value: tagName } = await ElMessageBox.prompt(
      '请输入标签名称',
      '创建标签',
      {
        confirmButtonText: '创建',
        cancelButtonText: '取消'
      }
    )
    
    if (tagName) {
      await libraryStore.createTag(tagName)
      ElMessage.success('标签创建成功')
    }
  } catch (error) {
    // 用户取消操作
  }
}

const filterByTag = (tag: Tag) => {
  libraryStore.filterByTag(tag.id)
}

const deleteTag = async (tag: Tag) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除标签 "${tag.name}" 吗？`,
      '删除标签',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await libraryStore.deleteTag(tag.id)
    ElMessage.success('标签删除成功')
  } catch (error) {
    // 用户取消操作
  }
}

const renameTag = async (tag: Tag) => {
  try {
    const { value: newTagName } = await ElMessageBox.prompt(
      '请输入新的标签名称',
      '重命名标签',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        inputValue: tag.name
      }
    )
    
    if (newTagName && newTagName !== tag.name) {
      await libraryStore.renameTag(tag.id, newTagName)
      ElMessage.success('标签重命名成功')
    }
  } catch (error) {
    // 用户取消操作
  }
}

const showLibrarySettings = () => {
  // 显示素材库设置
  libraryStore.showLibrarySettings = true
}

const handleActivityClick = (activity: any) => {
  // 处理活动项点击
  switch (activity.type) {
    case 'import':
      libraryStore.showRecentImports = true
      break
    case 'tag':
      libraryStore.showTagManager = true
      break
    case 'create':
      libraryStore.showFolderManager = true
      break
  }
}

const getActivityIcon = (type: string) => {
  const icons: Record<string, string> = {
    import: 'UploadFilled',
    tag: 'Collection',
    create: 'FolderAdd'
  }
  return icons[type] || 'Collection'
}

const formatRelativeTime = (timestamp: Date) => {
  const now = new Date()
  const diff = now.getTime() - timestamp.getTime()
  
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  return `${days}天前`
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const closeContextMenu = () => {
  contextMenu.value.visible = false
}

// 生命周期
onMounted(() => {
  // 点击其他地方关闭右键菜单
  document.addEventListener('click', closeContextMenu)
  document.addEventListener('contextmenu', closeContextMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeContextMenu)
  document.removeEventListener('contextmenu', closeContextMenu)
})
</script>

<style scoped lang="scss">
@use '@/styles/index.scss' as global;

.sidebar {
  width: 280px;
  height: 100%;
  background: $sidebar-bg-color;
  border-right: 1px solid $border-color;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  transition: width 0.3s ease;
}

// 滚动条样式
.sidebar::-webkit-scrollbar {
  width: 6px;
}

.sidebar::-webkit-scrollbar-track {
  background: $scrollbar-track-color;
}

.sidebar::-webkit-scrollbar-thumb {
  background: $scrollbar-thumb-color;
  border-radius: 3px;
}

.sidebar::-webkit-scrollbar-thumb:hover {
  background: $scrollbar-thumb-hover-color;
}

.library-info {
  padding: 20px;
  border-bottom: 1px solid $border-color;
  background: $sidebar-header-bg-color;
  transition: all 0.3s ease;
}

.library-header {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
  
  .el-icon {
    margin-right: 12px;
    color: $primary-color;
  }
}

.library-details {
  flex: 1;
  
  .library-name {
    font-size: 16px;
    font-weight: 600;
    color: $text-primary;
    margin-bottom: 4px;
  }
  
  .library-stats {
    font-size: 12px;
    color: $text-secondary;
  }
}

.library-actions {
  display: flex;
  gap: 8px;
}

.library-actions .el-button {
  background: $card-bg-color;
  border-color: $border-color;
  color: $text-primary;
  
  &:hover {
    background: $hover-bg-color;
    border-color: $primary-color;
    color: $primary-color;
  }
}

.quick-actions {
  padding: 20px;
  border-bottom: 1px solid $border-color;
  background: $sidebar-section-bg-color;
}

.quick-action-btn {
  width: 100%;
  margin-bottom: 16px;
  background: $primary-color;
  border-color: $primary-color;
  box-shadow: $button-shadow;
  transition: all 0.3s ease;
  
  &:hover {
    background: $primary-hover-color;
    border-color: $primary-hover-color;
    transform: translateY(-1px);
    box-shadow: $button-hover-shadow;
  }
  
  .el-icon {
    margin-right: 8px;
  }
}

.action-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 12px 8px;
  border: 1px solid $border-color;
  border-radius: $border-radius;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  background: $card-bg-color;
  
  &:hover {
    border-color: $primary-color;
    background: $hover-bg-color;
    transform: translateY(-1px);
    box-shadow: $card-shadow;
  }
  
  .el-icon {
    font-size: 20px;
    margin-bottom: 8px;
    color: $primary-color;
  }
  
  span {
    font-size: 12px;
    color: $text-secondary;
  }
}

.folders-section,
.tags-section,
.recent-section {
  padding: 20px;
  border-bottom: 1px solid $border-color;
  background: $sidebar-section-bg-color;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  
  span {
    font-size: 14px;
    font-weight: 600;
    color: $text-primary;
  }
}

.section-header .el-button {
  color: $text-secondary;
  
  &:hover {
    color: $primary-color;
    background: transparent;
  }
}

:deep(.el-tree) {
  background: transparent;
  
  .el-tree-node {
    .el-tree-node__content {
      height: 36px;
      border-radius: $border-radius;
      
      &:hover {
        background: $hover-bg-color;
      }
    }
    
    &.is-current {
      > .el-tree-node__content {
        background: $primary-light-bg;
        color: $primary-color;
        font-weight: 500;
      }
    }
    
    &.is-current.is-focused > .el-tree-node__content {
      background: $primary-light-bg;
      color: $primary-color;
    }
  }
  
  .el-tree-node__expand-icon {
    color: $text-secondary;
    
    &:hover {
      color: $primary-color;
    }
  }
  
  .el-tree-node__children {
    overflow: hidden;
    transition: all 0.3s ease;
  }
}

.tree-node {
  display: flex;
  align-items: center;
  width: 100%;
  
  .smart-folder-icon {
    margin-right: 6px;
    color: $warning-color;
  }
  
  .node-label {
    flex: 1;
    font-size: 14px;
    color: $text-primary;
  }
  
  .node-count {
    font-size: 12px;
    color: $text-tertiary;
    margin-left: 8px;
    background: $badge-bg-color;
    padding: 2px 6px;
    border-radius: 10px;
  }
}

.tags-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  
  .tag-item {
    margin: 0;
    cursor: pointer;
    transition: all 0.3s ease;
    border: 1px solid transparent;
    background: $card-bg-color;
    
    &:hover {
      transform: translateY(-2px);
      box-shadow: $card-shadow;
    }
    
    &.active-tag {
      font-weight: bold;
      box-shadow: 0 0 0 2px $sidebar-bg-color, 0 0 0 4px currentColor;
      border-color: currentColor;
    }
  }
}

.recent-list {
  .activity-item {
    display: flex;
    align-items: center;
    padding: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    border-radius: $border-radius;
    margin-bottom: 8px;
    background: $card-bg-color;
    border: 1px solid $border-color;
    
    &:hover {
      background: $hover-bg-color;
      border-color: $primary-color;
    }
    
    .activity-icon {
      margin-right: 12px;
      color: $primary-color;
      font-size: 16px;
    }
  }
}

.activity-info {
  flex: 1;
  
  .activity-title {
    font-size: 13px;
    color: $text-primary;
    margin-bottom: 2px;
  }
  
  .activity-time {
    font-size: 11px;
    color: $text-tertiary;
  }
}

// 右键菜单样式
:deep(.el-dropdown-menu) {
  background: $dropdown-bg-color;
  border: 1px solid $border-color;
  box-shadow: $dropdown-shadow;
  border-radius: $border-radius;
  
  .el-dropdown-item {
    color: $text-primary;
    transition: all 0.2s ease;
    
    &:hover {
      background: $hover-bg-color;
      color: $primary-color;
    }
    
    &.is-disabled {
      color: $text-tertiary;
    }
    
    .el-icon {
      margin-right: 8px;
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .sidebar {
    width: 260px;
  }
  
  .library-info,
  .quick-actions,
  .folders-section,
  .tags-section,
  .recent-section {
    padding: 16px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    width: 220px;
  }
  
  .action-grid {
    grid-template-columns: 1fr;
  }
  
  .action-item {
    padding: 8px;
    
    span {
      font-size: 11px;
    }
  }
}

@media (max-width: 480px) {
  .sidebar {
    width: 200px;
  }
}
</style>