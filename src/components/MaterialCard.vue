<template>
  <div 
    class="material-card"
    :class="{ 
      selected: isSelected, 
      'hover-lift': true,
      'fade-in': true 
    }"
    @click="handleClick"
    @contextmenu="handleContextMenu"
  >
    <div class="card-thumbnail" :style="{ backgroundColor: thumbnailBackground }">
      <img 
        v-if="material.type === 'image' && material.thumbnail" 
        :src="material.thumbnail" 
        :alt="material.name"
        class="thumbnail-image"
        @load="handleImageLoad"
        @error="handleImageError"
      />
      
      <div v-else-if="material.type === 'audio'" class="audio-preview">
        <div class="audio-wave" :class="material.color">
          <div class="wave-bar" v-for="n in 12" :key="n" :style="{ animationDelay: `${n * 0.1}s` }"></div>
        </div>
        <div class="audio-icon"></div>
      </div>
      
      <div v-else-if="material.type === 'video'" class="video-preview">
        <div class="video-icon"></div>
        <div class="video-duration">{{ material.duration || '00:00' }}</div>
      </div>
      
      <div v-else-if="material.type === 'design'" class="design-preview">
        <div class="design-icon">{{ getFormatIcon(material.name) }}</div>
        <div class="design-layers" v-if="material.layers">
          <span class="layer-count">{{ material.layers }}层</span>
        </div>
      </div>
      
      <div v-else class="default-preview">
        <div class="file-icon">{{ getFormatIcon(material.name) }}</div>
        <div class="file-extension">{{ getFileExtension(material.name) }}</div>
      </div>

      <div class="hover-actions" v-if="showHoverActions">
        <el-button 
          type="primary" 
          size="small" 
          circle
          @click.stop="handleQuickPreview"
          class="action-button"
        >
          <el-icon class="icon-sm"><View /></el-icon>
        </el-button>
        <el-button 
          type="success" 
          size="small" 
          circle
          @click.stop="handleDownload"
          class="action-button"
        >
          <el-icon class="icon-sm"><Download /></el-icon>
        </el-button>
        <el-button 
          type="warning" 
          size="small" 
          circle
          @click.stop="handleFavorite"
          class="action-button"
        >
          <el-icon class="icon-sm"><Star /></el-icon>
        </el-button>
      </div>

      <div v-if="isSelected" class="selection-indicator">
        <el-icon color="white" class="icon-sm"><Select /></el-icon>
      </div>

      <div v-if="material.rating" class="rating-badge">
        <el-rate 
          :model-value="material.rating" 
          disabled 
          :max="5" 
          size="small"
          show-score
          text-color="#ff9900"
          score-template="{value}"
          class="rating-control"
        />
      </div>

      <div class="format-badge" :style="{ backgroundColor: getFormatColor(material.name) }">
        {{ getFileExtension(material.name).toUpperCase() }}
      </div>
    </div>
    <div class="card-info">
      <div class="material-name" :title="material.name">
        {{ material.name }}
      </div>
      <div class="material-meta">
        <span class="file-size">{{ formatFileSize(material.size) }}</span>
        <span class="file-date">{{ formatFileDate(material.date) }}</span>
      </div>

      <div class="material-tags" v-if="material.tags && material.tags.length > 0">
        <el-tag 
          v-for="tag in material.tags.slice(0, 3)" 
          :key="tag" 
          size="small" 
          type="info"
          class="tag-item"
          :title="tag"
        >
          {{ tag }}
        </el-tag>
        <span v-if="material.tags.length > 3" class="more-tags">+{{ material.tags.length - 3 }}</span>
      </div>

      <div class="quick-actions">
        <el-button 
          type="text" 
          size="small" 
          @click.stop="handleEdit"
          class="quick-action-btn"
        >
          <el-icon class="icon-sm"><Edit /></el-icon>
          编辑
        </el-button>
        <el-button 
          type="text" 
          size="small" 
          @click.stop="handleShare"
          class="quick-action-btn"
        >
          <el-icon class="icon-sm"><Share /></el-icon>
          分享
        </el-button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { View, Download, Star, Select, Edit, Share } from '@element-plus/icons-vue'
import fileFormatManager from '../utils/fileFormatManager'

export default {
  name: 'MaterialCard',
  components: {
    View,
    Download,
    Star,
    Select,
    Edit,
    Share
  },
  props: {
    material: {
      type: Object,
      required: true
    },
    isSelected: {
      type: Boolean,
      default: false
    },
    showHoverActions: {
      type: Boolean,
      default: true
    }
  },
  emits: ['select', 'preview', 'download', 'favorite', 'edit', 'share', 'contextmenu'],
  setup(props, { emit }) {
    const imageLoaded = ref(false)
    const imageError = ref(false)

    const thumbnailBackground = computed(() => {
      if (props.material.type === 'image' && !imageLoaded.value) {
        return '#f5f5f5'
      }
      return props.material.backgroundColor || '#f8f9fa'
    })

    const handleClick = (event) => {
      emit('select', props.material, event)
      emit('preview', props.material)
    }

    const handleContextMenu = (event) => {
      event.preventDefault()
      emit('contextmenu', props.material, event)
    }

    const handleQuickPreview = () => {
      emit('preview', props.material)
    }

    const handleDownload = () => {
      emit('download', props.material)
    }

    const handleFavorite = () => {
      emit('favorite', props.material)
    }

    const handleEdit = () => {
      emit('edit', props.material)
    }

    const handleShare = () => {
      emit('share', props.material)
    }

    const handleImageLoad = () => {
      imageLoaded.value = true
      imageError.value = false
    }

    const handleImageError = () => {
      imageLoaded.value = false
      imageError.value = true
    }

    const getFormatIcon = (filename) => {
      return fileFormatManager.getFormatIcon(filename)
    }

    const getFormatColor = (filename) => {
      return fileFormatManager.getFormatColor(filename)
    }

    const getFileExtension = (filename) => {
      return fileFormatManager.getFileExtension(filename)
    }

    const formatFileSize = (bytes) => {
      return fileFormatManager.formatFileSize(bytes)
    }

    const formatFileDate = (timestamp) => {
      return fileFormatManager.formatFileDate(timestamp)
    }

    return {
      imageLoaded,
      imageError,
      thumbnailBackground,
      handleClick,
      handleContextMenu,
      handleQuickPreview,
      handleDownload,
      handleFavorite,
      handleEdit,
      handleShare,
      handleImageLoad,
      handleImageError,
      getFormatIcon,
      getFormatColor,
      getFileExtension,
      formatFileSize,
      formatFileDate
    }
  }
}
</script>

<style scoped>
.material-card {
  position: relative;
  background: var(--color-bg-elevated);
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border-light);
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--transition-base), box-shadow var(--transition-base), transform var(--transition-base);
  box-shadow: var(--shadow-sm);
  will-change: transform, box-shadow;
}

.material-card:hover {
  border-color: var(--color-primary-300);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.material-card.selected {
  border-color: var(--color-primary-500);
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
  background: var(--color-primary-50);
}

.card-thumbnail {
  position: relative;
  aspect-ratio: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.thumbnail-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.material-card:hover .thumbnail-image {
  transform: scale(1.05);
}

.audio-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.audio-wave {
  display: flex;
  align-items: end;
  gap: 2px;
  height: 30px;
}

.wave-bar {
  width: 3px;
  background: currentColor;
  border-radius: 2px;
  animation: wave 1.5s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% { height: 5px; }
  50% { height: 20px; }
}

.audio-wave.blue { color: #1890ff; }
.audio-wave.orange { color: #fa8c16; }
.audio-wave.red { color: #f5222d; }
.audio-wave.gray { color: #8c8c8c; }

.audio-icon {
  font-size: 32px;
}

.video-preview {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

.video-icon {
  font-size: 48px;
  opacity: 0.7;
}

.video-duration {
  position: absolute;
  bottom: 8px;
  right: 8px;
  background: rgba(0, 0, 0, 0.7);
  color: var(--text-primary);
  padding: 2px 6px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.design-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.design-icon {
  font-size: 48px;
}

.design-layers {
  background: var(--bg-tertiary);
  padding: 4px 8px;
  border-radius: var(--radius-sm);
  font-size: var(--font-size-xs);
}

.default-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.file-icon {
  font-size: 48px;
  opacity: 0.7;
}

.file-extension {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  text-transform: uppercase;
}

.hover-actions {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  display: flex;
  gap: var(--space-2);
  opacity: 0;
  transform: translateY(-10px);
  transition: opacity var(--transition-base), transform var(--transition-base);
  will-change: opacity, transform;
  pointer-events: none;
}

.material-card:hover .hover-actions {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}

.action-button {
  width: 32px;
  height: 32px;
  padding: 0;
  border-radius: var(--radius-base);
  transition: transform var(--transition-fast), box-shadow var(--transition-fast);
  box-shadow: var(--shadow-sm);
  will-change: transform, box-shadow;
}

.action-button:hover {
  transform: scale(1.1);
  box-shadow: var(--shadow-md);
}

.selection-indicator {
  position: absolute;
  top: var(--space-3);
  left: var(--space-3);
  width: 24px;
  height: 24px;
  background: var(--color-primary-500);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: var(--shadow-md);
  border: 2px solid white;
}

.rating-badge {
  position: absolute;
  bottom: var(--space-3);
  left: var(--space-3);
  background: var(--color-bg-secondary);
  color: var(--color-text-primary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-base);
  box-shadow: var(--shadow-sm);
}

.rating-control :deep(.el-rate__item) {
  margin-right: 2px;
}

.rating-control :deep(.el-rate__icon) {
  font-size: 12px;
}

.format-badge {
  position: absolute;
  top: var(--space-3);
  right: var(--space-3);
  color: var(--color-text-primary);
  background: var(--color-bg-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-base);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--color-border-lighter);
}

.card-info {
  padding: var(--space-4);
  background: var(--color-bg-primary);
}

.material-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: var(--space-2);
  line-height: var(--line-height-normal);
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 2.8em;
}

.material-meta {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-3);
  font-weight: var(--font-weight-medium);
}

.material-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-bottom: var(--space-3);
  min-height: 24px;
  max-width: 100%;
}

.tag-item {
  max-width: 60px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: var(--font-size-xs);
  padding: var(--space-1) var(--space-2);
  height: 20px;
  line-height: 18px;
  border-radius: var(--radius-sm);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-lighter);
  color: var(--color-text-secondary);
  font-weight: var(--font-weight-medium);
  transition: all var(--transition-fast);
}

.tag-item:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-primary-300);
}

.more-tags {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  align-self: center;
  font-weight: var(--font-weight-medium);
  background: var(--color-bg-secondary);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  border: 1px solid var(--color-border-lighter);
}

.quick-actions {
  display: flex;
  justify-content: space-between;
  gap: var(--space-2);
}

.quick-action-btn {
  padding: var(--space-2) var(--space-3);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary-600);
  border-radius: var(--radius-sm);
  transition: all var(--transition-fast);
  flex: 1;
  text-align: center;
  justify-content: center;
}

.quick-action-btn:hover {
  background: var(--color-primary-50);
  color: var(--color-primary-700);
  transform: translateY(-1px);
}

@media (max-width: 768px) {
  .material-card {
    border-radius: var(--radius-base);
  }
  
  .card-info {
    padding: var(--space-sm);
  }
  
  .material-name {
    font-size: var(--font-size-xs);
  }
  
  .hover-actions {
    display: none;
  }
}
</style>