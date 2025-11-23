<template>
  <div class="audio-asset-item" :class="{ 'selected': isSelected }" @click="handleClick">
    <!-- 音频波形预览 -->
    <div class="asset-thumbnail">
      <WaveformComponent 
        :audio-id="asset.id" 
        :is-playing="isPlaying" 
        :progress="progress" 
        :color="getWaveformColor()"
      />
      <div class="asset-duration">{{ formatDuration(asset.duration) }}</div>
      <div class="asset-format-badge">{{ asset.format }}</div>
    </div>
    
    <!-- 音频信息 -->
    <div class="asset-info">
      <div class="asset-name">{{ asset.name }}</div>
      <div class="asset-meta">
        <span class="bpm-info">BPM: {{ asset.bpm }}</span>
        <span class="size-info">{{ formatFileSize(asset.size) }}</span>
        <span v-if="asset.artist" class="artist-info">{{ asset.artist }}</span>
      </div>
      
      <!-- 标签显示 -->
      <div class="asset-tags" v-if="assetTags && assetTags.length > 0">
        <div 
          v-for="tag in assetTags.slice(0, 3)" 
          :key="tag.id" 
          class="tag-chip"
          :style="{ backgroundColor: tag.color + '20', color: tag.color }"
        >
          {{ tag.name }}
        </div>
        <div v-if="assetTags.length > 3" class="more-tags">
          +{{ assetTags.length - 3 }}
        </div>
      </div>
      
      <!-- 评分 -->
      <div class="asset-rating" v-if="asset.rating > 0">
        <el-rate 
          :model-value="asset.rating" 
          :max="5" 
          disabled 
          size="small" 
          show-score 
          score-template="{{ value }}"
        />
      </div>
    </div>
    
    <!-- 悬停操作按钮 -->
    <div class="asset-actions" v-if="showActions">
      <el-button 
        type="text" 
        size="small" 
        class="action-btn"
        @click.stop="handlePlayPause"
      >
        <el-icon v-if="!isPlaying"><play /></el-icon>
        <el-icon v-else><pause /></el-icon>
      </el-button>
      <el-button 
        type="text" 
        size="small" 
        class="action-btn"
        @click.stop="handleFavorite"
      >
        <el-icon :class="{ 'favorite-active': isFavorite }">
          <star v-if="isFavorite" />
          <star-outline v-else />
        </el-icon>
      </el-button>
      <el-button 
        type="text" 
        size="small" 
        class="action-btn"
        @click.stop="handleEdit"
      >
        <el-icon><edit /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import WaveformComponent from './WaveformComponent.vue'
import { Star, StarOutline, Play, Pause, Edit } from '@element-plus/icons-vue'

interface Tag {
  id: string
  name: string
  color: string
}

interface AudioAsset {
  id: string
  name: string
  format: string
  duration: number
  bpm: number
  size: number
  tagIds: string[]
  rating: number
  folderId?: string
  isFavorite?: boolean
  artist?: string
}

interface AudioAssetItemProps {
  asset: AudioAsset
  isSelected?: boolean
  isPlaying?: boolean
  progress?: number
  showActions?: boolean
  allTags?: Tag[]
}

const props = withDefaults(defineProps<AudioAssetItemProps>(), {
  isSelected: false,
  isPlaying: false,
  progress: 0,
  showActions: false,
  allTags: () => []
})

const emit = defineEmits<{
  select: [asset: AudioAsset]
  playPause: [assetId: string]
  favorite: [assetId: string, isFavorite: boolean]
  edit: [asset: AudioAsset]
}>()

const isFavorite = ref(props.asset.isFavorite || false)
const maxDisplayTags = 3

// 计算显示的标签 - 保留兼容旧版本
const displayedTags = computed(() => {
  // 如果使用新的tagIds方式，则使用assetTags
  if (props.asset.tagIds) {
    return assetTags.value.slice(0, 3)
  }
  // 兼容旧版本的tags属性
  if (!props.asset.tags) return []
  return props.asset.tags.slice(0, 3)
})

// 根据资产状态获取波形颜色
const getWaveformColor = () => {
  if (props.isPlaying) {
    return '#409eff' // 播放时使用主题色
  }
  if (props.asset.rating >= 4) {
    return '#67c23a' // 高分使用绿色
  }
  return '#909399' // 普通使用灰色
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

// 获取资产的标签对象
const assetTags = computed(() => {
  if (!props.allTags || !props.asset.tagIds) return []
  return props.allTags.filter(tag => props.asset.tagIds!.includes(tag.id))
})

// 处理点击事件
const handleClick = () => {
  emit('select', props.asset)
}

// 处理播放/暂停
const handlePlayPause = () => {
  emit('playPause', props.asset.id)
}

// 处理收藏
const handleFavorite = () => {
  isFavorite.value = !isFavorite.value
  emit('favorite', props.asset.id, isFavorite.value)
}

// 处理编辑
const handleEdit = () => {
  emit('edit', props.asset)
}

// 监听资产变化，更新收藏状态
watch(() => props.asset, (newAsset) => {
  isFavorite.value = newAsset.isFavorite || false
}, { deep: true })
</script>

<style scoped>
.audio-asset-item {
  background-color: v-bind('isDarkTheme ? "#222" : "#fff"');
  border-radius: 8px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  border: 2px solid transparent;
}

.audio-asset-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.audio-asset-item.selected {
  border-color: #409eff;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.asset-thumbnail {
  height: 120px;
  position: relative;
  overflow: hidden;
  background-color: v-bind('isDarkTheme ? "#1a1a1a" : "#f0f0f0"');
}

.asset-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 3px 8px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
}

.asset-format-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
}

.asset-info {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.asset-name {
  font-size: 14px;
  font-weight: 500;
  color: v-bind('isDarkTheme ? "#fff" : "#333"');
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  line-height: 1.4;
}

.asset-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: v-bind('isDarkTheme ? "#999" : "#666"');
}

.bpm-info {
  font-weight: 500;
}

.size-info {
  opacity: 0.8;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-top: 4px;
}

.tag-chip {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 500;
  border: 1px solid currentColor;
}

.more-tags {
  font-size: 11px;
  padding: 2px 6px;
  border-radius: 10px;
  background-color: v-bind('isDarkTheme ? "#333" : "#f0f0f0"');
  color: v-bind('isDarkTheme ? "#999" : "#666"');
  font-weight: 500;
}

.asset-rating {
  margin-top: 4px;
}

.asset-actions {
  position: absolute;
  top: 8px;
  right: 8px;
  display: flex;
  gap: 4px;
  opacity: 1;
  transition: opacity 0.2s;
}

.action-btn {
  width: 28px;
  height: 28px;
  padding: 0;
  min-width: 0;
  border-radius: 50%;
  background-color: rgba(0, 0, 0, 0.6);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.action-btn:hover {
  background-color: rgba(0, 0, 0, 0.8);
  color: #409eff;
}

.favorite-active {
  color: #f56c6c !important;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .audio-asset-item {
    max-width: 100%;
  }
  
  .asset-thumbnail {
    height: 100px;
  }
}
</style>