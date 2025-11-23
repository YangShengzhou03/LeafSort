<template>
  <div class="sidebar">
    <!-- 素材库信息 -->
    <div class="library-info" v-if="currentLibrary">
      <div class="library-header">
        <el-icon size="24"><FolderOpened /></el-icon>
        <div class="library-details">
          <div class="library-name">{{ currentLibrary.name }}</div>
          <div class="library-stats">
            {{ currentLibrary.assetCount }} 个素材 • {{ formatFileSize(currentLibrary.size) }}
          </div>
        </div>
      </div>
      
      <div class="library-actions">
        <el-button size="small" @click="importAssets">
          <el-icon><Plus /></el-icon>
          导入
        </el-button>
        <el-button size="small" @click="showLibrarySettings">
          <el-icon><Setting /></el-icon>
        </el-button>
      </div>
    </div>

    <!-- 快速操作 -->
    <div class="quick-actions">
      <el-button 
        type="primary" 
        size="large" 
        class="quick-action-btn"
        @click="importAssets"
      >
        <el-icon><UploadFilled /></el-icon>
        快速导入
      </el-button>
      
      <div class="action-grid">
        <div class="action-item" @click="takeScreenshot">
          <el-icon><Camera /></el-icon>
          <span>截图</span>
        </div>
        <div class="action-item" @click="startWebCapture">
          <el-icon><Globe /></el-icon>
          <span>网页采集</span>
        </div>
        <div class="action-item" @click="showSmartFolders">
          <el-icon><MagicStick /></el-icon>
          <span>智能整理</span>
        </div>
        <div class="action-item" @click="showSearch">
          <el-icon><Search /></el-icon>
          <span>高级搜索</span>
        </div>
      </div>
    </div>

    <!-- 文件夹树 -->
    <div class="folders-section">
      <div class="section-header">
        <span>文件夹</span>
        <el-button size="small" text @click="createFolder">
          <el-icon><FolderAdd /></el-icon>
        </el-button>
      </div>
      
      <el-tree
        ref="folderTreeRef"
        :data="folderTree"
        :props="treeProps"
        node-key="id"
        :expand-on-click-node="false"
        :default-expanded-keys="expandedKeys"
        @node-click="handleFolderClick"
        @node-contextmenu="handleFolderContextMenu"
      >
        <template #default="{ node, data }">
          <div class="tree-node">
            <el-icon v-if="data.type === 'smart-folder'" class="smart-folder-icon">
              <MagicStick />
            </el-icon>
            <span class="node-label">{{ node.label }}</span>
            <span class="node-count">{{ data.assetCount || 0 }}</span>
          </div>
        </template>
      </el-tree>
    </div>

    <!-- 标签云 -->
    <div class="tags-section">
      <div class="section-header">
        <span>标签</span>
        <el-button size="small" text @click="createTag">
          <el-icon><Plus /></el-icon>
        </el-button>
      </div>
      
      <div class="tags-cloud">
        <el-tag 
          v-for="tag in popularTags"
          :key="tag.id"
          :color="tag.color"
          size="small"
          class="tag-item"
          :class="{ 'active-tag': libraryStore.activeTagId === tag.id }"
          closable
          @click="filterByTag(tag)"
          @close="deleteTag(tag)"
          @contextmenu.prevent="renameTag(tag)"
        >
          {{ tag.name }} ({{ tag.assetCount }})
        </el-tag>
        
        <el-button 
          v-if="tags.length > 5" 
          size="small" 
          text 
          @click="showAllTags = !showAllTags"
        >
          {{ showAllTags ? '收起' : `查看更多 (${tags.length - 5})` }}
        </el-button>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="recent-section">
      <div class="section-header">
        <span>最近活动</span>
      </div>
      
      <div class="recent-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.id"
          class="activity-item"
          @click="handleActivityClick(activity)"
        >
          <el-icon class="activity-icon">
            <component :is="getActivityIcon(activity.type)" />
          </el-icon>
          <div class="activity-info">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-time">{{ formatRelativeTime(activity.timestamp) }}</div>
          </div>
        </div>
      </div>
    </div>

    <!-- 文件夹右键菜单 -->
    <el-dropdown-menu
      v-if="contextMenu.visible"
      :style="{ 
        left: contextMenu.x + 'px', 
        top: contextMenu.y + 'px',
        position: 'fixed',
        zIndex: 9999
      }"
    >
      <el-dropdown-item @click="renameFolder">
        <el-icon><Edit /></el-icon>
        重命名
      </el-dropdown-item>
      <el-dropdown-item @click="deleteFolder">
        <el-icon><Delete /></el-icon>
        删除
      </el-dropdown-item>
      <el-dropdown-item divided @click="exportFolder">
        <el-icon><Download /></el-icon>
        导出文件夹
      </el-dropdown-item>
    </el-dropdown-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'
import { Folder, Tag } from '@/types'

// 图标导入
import {
  FolderOpened,
  Plus,
  Setting,
  UploadFilled,
  Camera,
  Globe,
  MagicStick,
  Search,
  FolderAdd,
  Edit,
  Delete,
  Download,
  Picture,
  VideoCamera,
  Document,
  Collection
} from '@element-plus/icons-vue'

const libraryStore = useLibraryStore()

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
@import '@/styles/index.scss';

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