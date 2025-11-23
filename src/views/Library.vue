<template>
  <div class="library-container">
    <!-- 左侧导航栏 -->
    <div class="sidebar">
      <div class="sidebar-header">
        <h2 class="app-title">LeafView</h2>
      </div>
      <div class="sidebar-menu">
        <div class="menu-section">
          <h3 class="section-title">全部</h3>
          <div class="menu-item active">
            <el-icon><collection /></el-icon>
            <span>所有素材</span>
          </div>
          <div class="menu-item">
            <el-icon><timer /></el-icon>
            <span>最近添加</span>
          </div>
          <div class="menu-item">
            <el-icon><star /></el-icon>
            <span>收藏</span>
          </div>
          <div class="menu-item">
            <el-icon><warning /></el-icon>
            <span>未分类</span>
          </div>
        </div>
        
        <div class="menu-section">
          <h3 class="section-title">智能文件夹</h3>
          <div class="menu-item">
            <el-icon><music /></el-icon>
            <span>音频</span>
          </div>
          <div class="menu-item">
            <el-icon><picture /></el-icon>
            <span>图片</span>
          </div>
          <div class="menu-item">
            <el-icon><video-play /></el-icon>
            <span>视频</span>
          </div>
        </div>
        
        <div class="menu-section">
          <h3 class="section-title">文件夹</h3>
          <div class="menu-item">
            <el-icon><folder /></el-icon>
            <span>音频</span>
            <span class="item-count">52</span>
          </div>
          <div class="menu-item">
            <el-icon><folder /></el-icon>
            <span>插画</span>
            <span class="item-count">275</span>
          </div>
          <div class="menu-item">
            <el-icon><folder /></el-icon>
            <span>摄影</span>
            <span class="item-count">88</span>
          </div>
          <div class="menu-item">
            <el-icon><folder /></el-icon>
            <span>室内设计</span>
            <span class="item-count">103</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 中央内容区 -->
    <div class="main-content">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button type="primary" size="small">
            <el-icon><upload-filled /></el-icon>
            导入
          </el-button>
          <el-button size="small">
            <el-icon><folder-add /></el-icon>
            新建文件夹
          </el-button>
        </div>
        <FileOperations
          :selected-assets="selectedAssets"
          :available-folders="availableFolders"
          @import="handleImportFiles"
          @export="handleExportFiles"
          @delete="handleDeleteFiles"
          @move="handleMoveFiles"
          @batch-add-tag="handleBatchAddTag"
        />
        <div class="toolbar-right">
          <el-select v-model="viewMode" size="small" style="width: 120px;">
            <el-option label="网格视图" value="grid" />
            <el-option label="列表视图" value="list" />
          </el-select>
          <el-select v-model="sortBy" size="small" style="width: 120px;">
            <el-option label="创建时间" value="created" />
            <el-option label="文件名称" value="name" />
            <el-option label="文件大小" value="size" />
            <el-option label="时长" value="duration" />
            <el-option label="BPM" value="bpm" />
          </el-select>
        </div>
      </div>
      
      <!-- 搜索栏 -->
      <div class="search-bar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索素材..."
          prefix-icon="Search"
          clearable
          style="width: 100%;"
        />
      </div>
      
      <!-- 素材网格视图 -->
      <div class="assets-grid">
        <AudioAssetItem
              v-for="asset in audioAssets"
              :key="asset.id"
              :asset="asset"
              :all-tags="allTags"
              :is-selected="selectedAsset?.id === asset.id"
              :is-playing="playingAssetId === asset.id"
              :progress="playingProgress"
              :show-actions="true"
              @select="handleAssetSelect"
              @play-pause="handlePlayPause"
              @favorite="handleFavorite"
              @edit="handleEdit"
            />
      </div>
    </div>
    
    <!-- 右侧详情面板 -->
    <div class="detail-panel" v-if="selectedAsset">
      <div class="detail-header">
        <h3>详情</h3>
        <el-button type="text" @click="closeDetail">
          <el-icon><close /></el-icon>
        </el-button>
      </div>
      <div class="detail-content">
        <div class="detail-section">
          <h4>预览</h4>
          <div class="preview-container">
            <!-- 预览区域将在后续实现 -->
          </div>
        </div>
        
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="info-item">
            <span class="info-label">名称</span>
            <el-input v-model="selectedAsset.name" size="small" />
          </div>
          <div class="info-item">
            <span class="info-label">评分</span>
            <el-rate v-model="selectedAsset.rating" :max="5" size="small" />
          </div>
          <div class="info-item">
            <span class="info-label">格式</span>
            <span>{{ selectedAsset.format }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">时长</span>
            <span>{{ formatDuration(selectedAsset.duration) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">BPM</span>
            <span>{{ selectedAsset.bpm }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">采样率</span>
            <span>{{ selectedAsset.sampleRate || '44.1 kHz' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">比特率</span>
            <span>{{ selectedAsset.bitRate || '320 kbps' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">声道</span>
            <span>{{ selectedAsset.channels || '立体声' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">文件大小</span>
            <span>{{ formatFileSize(selectedAsset.size) }}</span>
          </div>
          <div class="info-item" v-if="selectedAsset.artist">
            <span class="info-label">艺术家</span>
            <span>{{ selectedAsset.artist }}</span>
          </div>
          <div class="info-item" v-if="selectedAsset.album">
            <span class="info-label">专辑</span>
            <span>{{ selectedAsset.album }}</span>
          </div>
        </div>
        
        <!-- 标签编辑器 -->
        <div class="detail-section" v-if="selectedAsset">
          <TagEditor
            :asset-id="selectedAsset.id"
            :asset-tags="selectedAssetTags"
            :all-tags="allTags"
            @add-tag="addTagToAsset"
            @remove-tag="removeTagFromAsset"
            @create-tag="createTag"
            @update-tag="updateTag"
            @delete-tag="deleteTag"
          />
        </div>
        
        <div class="detail-section">
          <h4>文件夹</h4>
          <div class="folder-info">
            <el-select v-model="selectedAsset.folderId" size="small" style="width: 100%;">
              <el-option label="音频" value="audio" />
              <el-option label="未分类" value="uncategorized" />
            </el-select>
          </div>
        </div>
        
        <div class="detail-actions">
          <el-button type="primary" size="small" style="width: 100%;">
            <el-icon><download /></el-icon>
            导出
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useLibraryStore } from '@/stores/library'
import { useThemeStore } from '@/stores/theme'
import type { Asset } from '@/types'
import AudioAssetItem from '@/components/AudioAssetItem.vue'
import TagEditor from '@/components/TagEditor.vue'
import FileOperations from '@/components/FileOperations.vue'

const libraryStore = useLibraryStore()
const themeStore = useThemeStore()
const viewMode = ref('grid')
const sortBy = ref('created')
const searchQuery = ref('')
const playingAssetId = ref<string | null>(null)
const playingProgress = ref(0)

// 模拟文件夹数据
const availableFolders = [
  { id: '1', name: '默认文件夹' },
  { id: '2', name: '音乐收藏' },
  { id: '3', name: '工作项目' },
  { id: '4', name: '环境音效' }
]

// 模拟标签数据
const allTags = [
  { id: '1', name: '流行', color: '#ff6b6b' },
  { id: '2', name: '品牌主题曲', color: '#4ecdc4' },
  { id: '3', name: '钢琴', color: '#ffe66d' },
  { id: '4', name: '弦乐', color: '#1a535c' },
  { id: '5', name: '电子', color: '#4ecdc4' },
  { id: '6', name: '爵士', color: '#fdcb6e' },
  { id: '7', name: '古典', color: '#6c5ce7' },
  { id: '8', name: '摇滚', color: '#e17055' }
]

// 模拟音频资产数据
const audioAssets = ref([
  {
    id: '1',
    name: '小岛上的星光',
    format: 'WAV',
    duration: 251,
    bpm: 148,
    size: 10660000,
    sampleRate: '48 kHz',
    bitRate: '1411 kbps',
    channels: '立体声',
    artist: '音乐家A',
    album: '自然之声',
    isFavorite: true,
    tagIds: ['1', '2', '3', '4'],
    folderId: 'audio',
    rating: 5
  },
    // 添加更多模拟数据
    { 
      id: '2', 
      name: '夏日回忆', 
      format: 'MP3', 
      duration: 180, 
      bpm: 121, 
      size: 5200000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '音乐家B',
      album: '夏日合集',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '3', 
      name: '城市夜景', 
      format: 'MP3', 
      duration: 210, 
      bpm: 148, 
      size: 6100000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '城市乐队',
      album: '都市印象',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 3 
    },
    { 
      id: '4', 
      name: '深海探索', 
      format: 'MP3', 
      duration: 245, 
      bpm: 165, 
      size: 7100000,
      sampleRate: '48 kHz',
      bitRate: '320 kbps',
      channels: '5.1环绕声',
      artist: '环境音乐家',
      album: '深海秘境',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 5 
    },
    { 
      id: '5', 
      name: '清晨冥想', 
      format: 'MP3', 
      duration: 300, 
      bpm: 125, 
      size: 8700000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '冥想大师',
      album: '心灵宁静',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '6', 
      name: '电子节拍', 
      format: 'MP3', 
      duration: 198, 
      bpm: 164, 
      size: 5700000,
      sampleRate: '44.1 kHz',
      bitRate: '256 kbps',
      channels: '立体声',
      artist: '电子音乐人',
      album: '节拍集合',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 3 
    },
    { 
      id: '7', 
      name: '乡村民谣', 
      format: 'MP3', 
      duration: 220, 
      bpm: 151, 
      size: 6400000,
      sampleRate: '48 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '乡村歌手',
      album: '乡村故事',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '8', 
      name: '爵士即兴', 
      format: 'MP3', 
      duration: 310, 
      bpm: 164, 
      size: 9000000,
      sampleRate: '96 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '爵士乐团',
      album: '即兴之夜',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 5 
    },
    { 
      id: '9', 
      name: '摇滚现场', 
      format: 'MP3', 
      duration: 280, 
      bpm: 193, 
      size: 8100000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '摇滚乐队',
      album: '现场实况',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '10', 
      name: '古典协奏曲', 
      format: 'MP3', 
      duration: 420, 
      bpm: 169, 
      size: 12200000,
      sampleRate: '96 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '交响乐团',
      album: '古典精选',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 5 
    },
    { 
      id: '11', 
      name: '环境音效', 
      format: 'MP3', 
      duration: 180, 
      bpm: 107, 
      size: 5200000,
      sampleRate: '44.1 kHz',
      bitRate: '256 kbps',
      channels: '立体声',
      artist: '音效设计师',
      album: '自然之声',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 3 
    },
    { 
      id: '12', 
      name: '节奏练习', 
      format: 'MP3', 
      duration: 240, 
      bpm: 127, 
      size: 6900000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '音乐教师',
      album: '练习曲集',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '13', 
      name: '电影配乐', 
      format: 'MP3', 
      duration: 360, 
      bpm: 145, 
      size: 10400000,
      sampleRate: '48 kHz',
      bitRate: '320 kbps',
      channels: '5.1环绕声',
      artist: '电影配乐师',
      album: '电影音乐精选',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 5 
    },
    { 
      id: '14', 
      name: '游戏音效', 
      format: 'MP3', 
      duration: 150, 
      bpm: 151, 
      size: 4300000,
      sampleRate: '44.1 kHz',
      bitRate: '256 kbps',
      channels: '立体声',
      artist: '游戏音效师',
      album: '游戏素材',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 3 
    },
    { 
      id: '15', 
      name: '嘻哈伴奏', 
      format: 'MP3', 
      duration: 180, 
      bpm: 173, 
      size: 5200000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '嘻哈制作人',
      album: '嘻哈素材包',
      isFavorite: false,
      tags: [], 
      folderId: 'audio', 
      rating: 4 
    },
    { 
      id: '16', 
      name: '背景音乐', 
      format: 'MP3', 
      duration: 210, 
      bpm: 142, 
      size: 6100000,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: '配乐师',
      album: '背景音乐集',
      isFavorite: true,
      tags: [], 
      folderId: 'audio', 
      rating: 5 
    }
  ])

// 当前选中的资产
const selectedAsset = ref(audioAssets.value[0])
const isDarkTheme = ref(themeStore.isDark)

// 计算属性：选中的资产列表（支持多选）
const selectedAssets = computed(() => {
  if (!selectedAsset.value) return []
  return audioAssets.value.filter(asset => asset.id === selectedAsset.value?.id)
})

// 计算属性：选中资产的标签对象列表
const selectedAssetTags = computed(() => {
  if (!selectedAsset.value) return []
  return allTags.filter(tag => selectedAsset.value.tagIds?.includes(tag.id))
})

// 标签管理相关方法
const addTagToAsset = (assetId: string, tagId: string) => {
  const asset = audioAssets.value.find(a => a.id === assetId)
  if (asset && !asset.tagIds.includes(tagId)) {
    asset.tagIds.push(tagId)
  }
}

const removeTagFromAsset = (assetId: string, tagId: string) => {
  const asset = audioAssets.value.find(a => a.id === assetId)
  if (asset) {
    const index = asset.tagIds.indexOf(tagId)
    if (index > -1) {
      asset.tagIds.splice(index, 1)
    }
  }
}

const createTag = (tagData: { name: string; color: string }) => {
  const newTag = {
    id: Date.now().toString(),
    ...tagData
  }
  allTags.push(newTag)
}

const updateTag = (tagData: { id: string; name: string; color: string }) => {
  const index = allTags.findIndex(t => t.id === tagData.id)
  if (index > -1) {
    allTags[index] = { ...tagData }
  }
}

const deleteTag = (tagId: string) => {
  // 删除标签
  const index = allTags.findIndex(t => t.id === tagId)
  if (index > -1) {
    allTags.splice(index, 1)
  }
  
  // 从所有资产中移除该标签
  audioAssets.value.forEach(asset => {
    const assetIndex = asset.tagIds.indexOf(tagId)
    if (assetIndex > -1) {
      asset.tagIds.splice(assetIndex, 1)
    }
  })
}

// 文件操作相关方法
const handleImportFiles = (files: File[]) => {
  // 模拟导入文件，生成新的资产数据
  files.forEach(file => {
    const newAsset = {
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      name: file.name.replace(/\.[^/.]+$/, ''),
      format: file.name.split('.').pop()?.toUpperCase() || 'MP3',
      duration: Math.floor(Math.random() * 300) + 60, // 1-6分钟
      bpm: Math.floor(Math.random() * 100) + 60, // 60-160 BPM
      size: file.size,
      tagIds: [],
      folderId: '1',
      rating: Math.floor(Math.random() * 5) + 1,
      sampleRate: '44.1 kHz',
      bitRate: '320 kbps',
      channels: '立体声',
      artist: 'Unknown Artist',
      album: 'Unknown Album',
      isFavorite: false,
      modifiedAt: new Date().toISOString()
    }
    audioAssets.value.push(newAsset)
  })
}

const handleExportFiles = (mode: 'selected' | 'all' | 'folder') => {
  let assetsToExport: typeof audioAssets.value = []
  
  switch (mode) {
    case 'selected':
      assetsToExport = selectedAssets.value
      break
    case 'all':
      assetsToExport = [...audioAssets.value]
      break
    case 'folder':
      if (selectedAsset.value?.folderId) {
        assetsToExport = audioAssets.value.filter(asset => asset.folderId === selectedAsset.value?.folderId)
      }
      break
  }
  
  // 模拟导出
  console.log(`导出了 ${assetsToExport.length} 个文件`)
  console.log('Exporting assets:', assetsToExport)
}

const handleDeleteFiles = (assetIds: string[]) => {
  assetIds.forEach(id => {
    const index = audioAssets.value.findIndex(asset => asset.id === id)
    if (index > -1) {
      audioAssets.value.splice(index, 1)
    }
  })
  
  // 如果删除了选中的资产，清空选中状态
  if (assetIds.includes(selectedAsset.value?.id)) {
    selectedAsset.value = null as any
  }
}

const handleMoveFiles = (assetIds: string[], targetFolderId: string) => {
  assetIds.forEach(id => {
    const asset = audioAssets.value.find(asset => asset.id === id)
    if (asset) {
      asset.folderId = targetFolderId
    }
  })
}

const handleBatchAddTag = (assetIds: string[]) => {
  // 这里可以打开一个对话框让用户选择要添加的标签
  console.log('批量添加标签功能待实现')
}

// 格式化时长
const formatDuration = (seconds: number): string => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

// 关闭详情面板
const closeDetail = () => {
  selectedAsset.value = null as any
}

// 处理资产选择
const handleAssetSelect = (asset: any) => {
  selectedAsset.value = asset
}

// 处理播放/暂停
const handlePlayPause = (assetId: string) => {
  if (playingAssetId.value === assetId) {
    // 暂停当前播放
    playingAssetId.value = null
    playingProgress.value = 0
  } else {
    // 切换到新的资产播放
    playingAssetId.value = assetId
    // 模拟播放进度
    simulatePlayProgress()
  }
}

// 处理收藏
const handleFavorite = (assetId: string, isFavorite: boolean) => {
  const asset = audioAssets.value.find(a => a.id === assetId)
  if (asset) {
    asset.isFavorite = isFavorite
  }
}

// 处理编辑
const handleEdit = (asset: any) => {
  selectedAsset.value = asset
}

// 模拟播放进度
const simulatePlayProgress = () => {
  let progress = 0
  const interval = setInterval(() => {
    if (!playingAssetId.value) {
      clearInterval(interval)
      return
    }
    
    progress += 0.01
    playingProgress.value = Math.min(progress, 1)
    
    if (progress >= 1) {
      clearInterval(interval)
      playingAssetId.value = null
      playingProgress.value = 0
    }
  }, 100)
}
</script>

<style scoped>
.library-container {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background-color: v-bind('isDarkTheme ? "#1a1a1a" : "#f5f7fa"');
}

/* 左侧导航栏 */
.sidebar {
  width: 240px;
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-right: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
}

.app-title {
  font-size: 20px;
  font-weight: 600;
  color: v-bind('isDarkTheme ? "#fff" : "#333"');
  margin: 0;
}

.sidebar-menu {
  flex: 1;
  padding: 10px 0;
}

.menu-section {
  margin-bottom: 20px;
}

.section-title {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: v-bind('isDarkTheme ? "#999" : "#666"');
  margin: 0 20px 10px;
  font-weight: 500;
}

.menu-item {
  display: flex;
  align-items: center;
  padding: 10px 20px;
  cursor: pointer;
  color: v-bind('isDarkTheme ? "#ccc" : "#333"');
  transition: all 0.2s;
  position: relative;
}

.menu-item:hover {
  background-color: v-bind('isDarkTheme ? "#333" : "#f5f5f5"');
  color: v-bind('isDarkTheme ? "#fff" : "#000"');
}

.menu-item.active {
  background-color: v-bind('isDarkTheme ? "#333" : "#ecf5ff"');
  color: v-bind('isDarkTheme ? "#409eff" : "#409eff"');
}

.menu-item .el-icon {
  margin-right: 10px;
  font-size: 18px;
}

.item-count {
  margin-left: auto;
  font-size: 12px;
  color: v-bind('isDarkTheme ? "#999" : "#999"');
  background-color: v-bind('isDarkTheme ? "#333" : "#f0f0f0"');
  padding: 2px 6px;
  border-radius: 10px;
}

/* 中央内容区 */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-bottom: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
}

.search-bar {
  padding: 15px 20px;
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-bottom: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
}

.assets-grid {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
  padding: 20px;
  overflow-y: auto;
  background-color: v-bind('isDarkTheme ? "#1a1a1a" : "#f5f7fa"');
}

.asset-item {
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.asset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.asset-thumbnail {
  height: 120px;
  background-color: v-bind('isDarkTheme ? "#1a1a1a" : "#f0f0f0"');
  position: relative;
  overflow: hidden;
}

.waveform-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, v-bind('isDarkTheme ? "#333" : "#e0e0e0"') 0%, v-bind('isDarkTheme ? "#222" : "#f0f0f0"') 100%);
  opacity: 0.7;
}

.asset-duration {
  position: absolute;
  bottom: 5px;
  right: 5px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.asset-info {
  padding: 10px;
}

.asset-format {
  font-size: 12px;
  color: v-bind('isDarkTheme ? "#409eff" : "#409eff"');
  margin-bottom: 4px;
}

.asset-name {
  font-size: 14px;
  font-weight: 500;
  color: v-bind('isDarkTheme ? "#fff" : "#333"');
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.asset-meta {
  font-size: 12px;
  color: v-bind('isDarkTheme ? "#999" : "#666"');
}

/* 右侧详情面板 */
.detail-panel {
  width: 320px;
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-left: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid v-bind('isDarkTheme ? "#333" : "#e0e0e0"');
}

.detail-header h3 {
  margin: 0;
  color: v-bind('isDarkTheme ? "#fff" : "#333"');
  font-size: 16px;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.detail-section {
  margin-bottom: 25px;
}

.detail-section h4 {
  font-size: 14px;
  font-weight: 500;
  color: v-bind('isDarkTheme ? "#ccc" : "#666"');
  margin: 0 0 15px 0;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.preview-container {
  height: 200px;
  background-color: v-bind('isDarkTheme ? "#1a1a1a" : "#f0f0f0"');
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.info-label {
  font-size: 13px;
  color: v-bind('isDarkTheme ? "#999" : "#666"');
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.folder-info {
  margin-bottom: 12px;
}

.detail-actions {
  margin-top: 30px;
}
</style>