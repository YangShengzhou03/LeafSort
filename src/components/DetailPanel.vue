<template>
  <div class="detail-panel" v-if="asset">
    <div class="detail-header">
      <h3>{{ asset.name }}</h3>
      <button class="close-btn" @click="$emit('close')">×</button>
    </div>
    
    <div class="detail-content">
      <!-- 预览区域 -->
      <div class="preview-section">
        <img 
          v-if="asset.type === 'image'" 
          :src="getPreviewUrl()" 
          alt="Asset Preview" 
          class="preview-image"
        >
        <div v-else class="non-image-preview">
          非图片类型预览
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
              class="tag-clickable"
            >
              {{ tag }}
            </el-tag>
          </div>
        </div>
        
        <!-- 评分区域 -->
        <div class="rating-section">
          <h4>评分</h4>
          <div class="rating-stars">
            <span v-for="n in 5" :key="n" class="star" :class="{ active: asset.rating >= n }">
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
        <el-button type="danger" icon="el-icon-delete">删除</el-button>
      </el-button-group>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Asset } from '@/types'

// 定义属性
const props = defineProps<{
  asset: Asset | null
}>()

// 定义事件
const emit = defineEmits<{
  close: []
  'tag-click': [tag: string]
}>()

// 获取预览URL
const getPreviewUrl = () => {
  if (!props.asset) return ''
  // 根据资产ID返回对应的预览图片
  if (props.asset.id === '1') return 'https://picsum.photos/id/433/800/600'
  if (props.asset.id === '2') return 'https://picsum.photos/id/429/800/1200'
  if (props.asset.id === '3') return 'https://picsum.photos/id/424/800/1200'
  if (props.asset.id === '4') return 'https://picsum.photos/id/425/800/800'
  if (props.asset.id === '5') return 'https://picsum.photos/id/426/800/800'
  return 'https://picsum.photos/800/600'
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
  margin-bottom: 24px;
  border-radius: 8px;
  overflow: hidden;
  background-color: #f5f5f5;
}

.preview-image {
  width: 100%;
  height: auto;
  display: block;
}

.non-image-preview {
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
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
}

.tag-clickable {
  cursor: pointer;
}

.rating-stars {
  display: flex;
  gap: 2px;
}

.star {
  font-size: 20px;
  color: #e0e0e0;
}

.star.active {
  color: #ffd700;
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
