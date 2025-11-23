<template>
  <div class="detail-panel" v-if="asset">
    <div class="detail-header">
      <h3>{{ asset.name }}</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="detail-content">
      <!-- 预览区域 -->
      <div class="preview-section">
        <!-- 根据资产类型显示不同的预览 -->
        <img 
          v-if="asset.type === 'image'" 
          :src="getPreviewUrl()" 
          :alt="asset.name" 
          class="preview-image"
        >
        <div v-else-if="asset.type === 'video'" class="video-preview">
          <img 
            :src="getPreviewUrl()" 
            :alt="asset.name" 
            class="preview-image"
          >
          <div class="play-icon">▶</div>
        </div>
        <div v-else class="document-preview">
          <i class="el-icon-document"></i>
          <p>{{ asset.name }}</p>
        </div>
      </div>
      
      <!-- 信息区域 -->
      <div class="info-section">
        <div class="info-group">
          <h4>基本信息</h4>
          <div class="info-item">
            <span class="info-label">名称：</span>
            <span class="info-value">{{ asset.name }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">类型：</span>
            <span class="info-value">{{ asset.type }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">尺寸：</span>
            <span class="info-value">{{ formatSize(asset.size) }}</span>
          </div>
          <div v-if="asset.width && asset.height" class="info-item">
            <span class="info-label">分辨率：</span>
            <span class="info-value">{{ asset.width }} × {{ asset.height }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">创建时间：</span>
            <span class="info-value">{{ formatDate(asset.createdAt) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">修改时间：</span>
            <span class="info-value">{{ formatDate(asset.modifiedAt) }}</span>
          </div>
        </div>
        
        <!-- 标签区域 -->
        <div class="tags-section">
          <h4>标签</h4>
          <div class="tags-container">
            <el-tag 
              v-for="tag in asset.tags" 
              :key="tag" 
              size="small"
              @click="$emit('tag-click', tag)"
              closable
              @close="removeTag(tag)"
              class="tag-clickable"
            >
              {{ tag }}
            </el-tag>
            <el-button 
              size="small" 
              plain 
              icon="el-icon-plus" 
              @click="showAddTagInput = !showAddTagInput"
            >
              添加标签
            </el-button>
            <div v-if="showAddTagInput" class="add-tag-input-container">
              <el-input 
                v-model="newTag" 
                @keyup.enter="addTag" 
                placeholder="输入标签名" 
                size="small"
                style="width: 150px; margin-right: 8px;"
              ></el-input>
              <el-button size="small" type="primary" @click="addTag">确定</el-button>
            </div>
          </div>
        </div>
        
        <!-- 评分区域 -->
        <div class="rating-section">
          <h4>评分</h4>
          <div class="rating-stars">
            <span 
              v-for="n in 5" 
              :key="n" 
              class="star" 
              :class="{ active: asset.rating >= n }"
              @click="updateRating(n)"
              title="点击评分: {{ n }}星"
            >
              ★
            </span>
          </div>
        </div>
        
        <!-- 元数据区域 -->
        <div v-if="asset.metadata" class="metadata-section">
          <h4>元数据</h4>
          <div class="metadata-item" v-if="asset.metadata.format">
            <span class="info-label">格式：</span>
            <span class="info-value">{{ asset.metadata.format }}</span>
          </div>
          <div class="metadata-item" v-if="asset.metadata.dominantColor">
            <span class="info-label">主色调：</span>
            <span class="info-value">
              <span class="color-swatch" :style="{ backgroundColor: asset.metadata.dominantColor }"></span>
              {{ asset.metadata.dominantColor }}
            </span>
          </div>
          <div v-for="(value, key) in asset.metadata" :key="key" v-if="!['format', 'dominantColor'].includes(key)" class="metadata-item">
            <span class="info-label">{{ formatKey(key) }}：</span>
            <span class="info-value">{{ value }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 操作按钮 -->
    <div class="detail-footer">
      <el-button-group>
        <el-button icon="el-icon-download">下载</el-button>
        <el-button icon="el-icon-share">分享</el-button>
        <el-button icon="el-icon-edit">编辑</el-button>
        <el-button type="danger" icon="el-icon-delete" @click="deleteAsset">删除</el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { Asset } from '@/types'
import { useLibraryStore } from '../stores/library'

// Store
const libraryStore = useLibraryStore()

// 定义属性
const props = defineProps<{
  asset: Asset | null
}>()

// 定义事件
const emit = defineEmits<{
  close: []
  'tag-click': [tag: string]
}>()

// 响应式数据
const showAddTagInput = ref(false)
const newTag = ref('')

// 获取预览URL
const getPreviewUrl = () => {
  if (!props.asset) return ''
  
  // 根据资产类型返回不同的预览URL
  if (props.asset.type === 'image') {
    return `https://picsum.photos/seed/${props.asset.id}/800/600`
  } else if (props.asset.type === 'video') {
    // 对于视频，返回缩略图
    return `https://picsum.photos/seed/${props.asset.id}video/800/600`
  } else {
    // 对于文档，返回文档类型的缩略图
    return `https://picsum.photos/seed/${props.asset.id}doc/800/600`
  }
}

// 格式化文件大小
const formatSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (date: Date): string => {
  return new Date(date).toLocaleString('zh-CN')
}

// 格式化键名
const formatKey = (key: string): string => {
  // 简单的驼峰转空格
  return key.replace(/([A-Z])/g, ' $1').trim()
}

// 添加标签
const addTag = () => {
  if (!props.asset || !newTag.value.trim()) return
  
  const updatedAsset = {
    ...props.asset,
    tags: [...props.asset.tags, newTag.value.trim()]
  }
  
  // 使用store更新资产
  libraryStore.updateAsset(updatedAsset)
  newTag.value = ''
  showAddTagInput.value = false
}

// 移除标签
const removeTag = (tagToRemove: string) => {
  if (!props.asset) return
  
  const updatedAsset = {
    ...props.asset,
    tags: props.asset.tags.filter(tag => tag !== tagToRemove)
  }
  
  // 使用store更新资产
  libraryStore.updateAsset(updatedAsset)
}

// 更新评分
const updateRating = (rating: number) => {
  if (!props.asset) return
  
  const updatedAsset = {
    ...props.asset,
    rating
  }
  
  // 使用store更新资产
  libraryStore.updateAsset(updatedAsset)
}

// 删除资产
const deleteAsset = () => {
  if (!props.asset) return
  
  if (confirm(`确定要删除资产 "${props.asset.name}" 吗？`)) {
    // 使用store删除资产
    libraryStore.deleteAsset(props.asset.id)
    emit('close')
  }
}
</script>

<style scoped>
.detail-panel {
  position: absolute;
  top: 0;
  right: 0;
  width: 400px;
  height: 100%;
  background-color: #fff;
  border-left: 1px solid #e0e0e0;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  display: flex;
  flex-direction: column;
}

.detail-header {
  padding: 16px;
  border-bottom: 1px solid #e0e0e0;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  flex: 1;
  margin-right: 12px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  color: #333;
}

.detail-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.preview-section {
    width: 100%;
    height: 240px;
    background-color: #f5f7fa;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 20px;
    border-radius: 6px;
    overflow: hidden;
    position: relative;
  }

  .preview-image {
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    transition: transform 0.2s ease;
  }

  .non-image-preview {
    height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #666;
  }
  
  .video-preview {
    position: relative;
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .play-icon {
    position: absolute;
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background-color: rgba(0, 0, 0, 0.6);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    cursor: pointer;
    transition: all 0.3s ease;
  }

  .play-icon:hover {
    background-color: rgba(0, 0, 0, 0.8);
    transform: scale(1.1);
  }

  .document-preview {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: #909399;
  }

  .document-preview i {
    font-size: 48px;
    margin-bottom: 12px;
  }

  .document-preview p {
    font-size: 14px;
    text-align: center;
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

.info-section .info-group,
.tags-section,
.rating-section,
.metadata-section {
  margin-bottom: 24px;
}

.info-section h4 {
  font-size: 14px;
  font-weight: 500;
  color: #666;
  margin: 0 0 12px 0;
}

.info-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.info-label {
  color: #999;
  width: 80px;
  flex-shrink: 0;
}

.info-value {
  color: #333;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tags-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 8px;
  }

  .tag-clickable {
    cursor: pointer;
  }

  .add-tag-input-container {
    display: flex;
    align-items: center;
    margin-top: 8px;
  }

.rating-stars {
    display: flex;
    gap: 4px;
    margin-top: 8px;
  }

  .star {
    font-size: 18px;
    color: #dcdfe6;
    cursor: pointer;
    transition: color 0.2s ease;
  }

  .star:hover,
  .star:hover ~ .star {
    color: #f7ba2a;
  }

  .star.active {
    color: #f7ba2a;
  }

  .star.active ~ .star {
    color: #dcdfe6;
  }

.metadata-item {
  display: flex;
  margin-bottom: 8px;
  font-size: 14px;
}

.color-swatch {
  display: inline-block;
  width: 16px;
  height: 16px;
  border-radius: 2px;
  margin-right: 8px;
  border: 1px solid #e0e0e0;
}

.detail-footer {
  padding: 16px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: center;
}
</style>
