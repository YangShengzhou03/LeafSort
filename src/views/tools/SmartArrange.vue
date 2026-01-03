<template>
  <div class="smart-arrange-page">
    <div class="page-header">
      <div class="header-title">
        <h2>智能整理</h2>
        <p class="header-desc">根据照片的EXIF信息自动整理到指定目录结构中</p>
      </div>
      <div class="header-actions">
        <el-button type="primary" @click="selectSourceFolder">
          <el-icon><FolderOpened /></el-icon>
          选择照片文件夹
        </el-button>
        <el-button @click="selectTargetFolder">
          <el-icon><Upload /></el-icon>
          选择输出文件夹
        </el-button>
      </div>
    </div>

    <div class="content-section">
      <div class="folder-info">
        <div class="info-card">
          <div class="info-row">
            <span class="label">源文件夹</span>
            <span class="value">{{ sourceFolder || '未选择' }}</span>
          </div>
          <div class="info-row">
            <span class="label">输出文件夹</span>
            <span class="value">{{ targetFolder || '未选择' }}</span>
          </div>
          <div class="info-row">
            <span class="label">照片数量</span>
            <span class="value">{{ photoCount }} 张</span>
          </div>
        </div>
      </div>

      <div class="arrange-section">
        <div class="section-header">
          <span>配置目录结构</span>
        </div>

        <div class="structure-builder">
          <div class="builder-header">
            <span>已选标签</span>
            <el-button type="primary" size="small" text @click="clearAllTags">清空</el-button>
          </div>

          <div class="selected-tags-container">
            <div v-if="selectedTags.length === 0" class="empty-state">
              <span>点击下方标签添加，构建目录层级</span>
            </div>
            <div v-else class="selected-tags-list">
              <div v-for="(tag, index) in selectedTags" :key="tag" class="selected-tag">
                <span class="tag-index">{{ index + 1 }}</span>
                <span>{{ getTagLabel(tag) }}</span>
                <el-icon class="close-icon" @click="removeTag(index)"><Close /></el-icon>
              </div>
            </div>
          </div>

          <div class="preview-section">
            <div class="preview-title">目录结构预览</div>
            <div class="preview-content">
              <div v-if="selectedTags.length === 0" class="preview-empty">
                选择标签后查看目录结构
              </div>
              <div v-else class="preview-tree">
                <div class="tree-item root">
                  <el-icon><FolderOpened /></el-icon>
                  <span>输出文件夹</span>
                </div>
                <div v-for="(tag, index) in selectedTags" :key="tag" class="tree-item" :style="{ paddingLeft: (index + 1) * 24 + 'px' }">
                  <el-icon><Folder /></el-icon>
                  <span>{{ getTagLabel(tag) }}</span>
                  <span class="tree-value">/ 示例值</span>
                </div>
                <div class="tree-item file" :style="{ paddingLeft: (selectedTags.length + 1) * 24 + 'px' }">
                  <el-icon><Picture /></el-icon>
                  <span>照片.jpg</span>
                </div>
              </div>
            </div>
          </div>

          <div class="tags-selector">
            <div class="selector-title">选择标签（点击添加到目录结构）</div>
            <div class="tag-groups">
              <div v-for="group in tagGroups" :key="group.name" class="tag-group">
                <div class="group-name">{{ group.name }}</div>
                <div class="tags-list">
                  <div
                    v-for="tag in group.tags"
                    :key="tag.value"
                    class="tag-item"
                    :class="{ 'tag-selected': selectedTags.includes(tag.value) }"
                    @click="selectTag(tag.value)"
                  >
                    {{ tag.label }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="action-section">
        <el-button type="primary" size="large" @click="startArrange" :loading="arranging" :disabled="!canArrange">
          开始整理
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { notify } from '@/utils'
import { FolderOpened, Upload, Close, Folder, Picture } from '@element-plus/icons-vue'

const sourceFolder = ref('')
const targetFolder = ref('')
const photoCount = ref(0)
const arranging = ref(false)

const availableTags = [
  { label: '年份', value: 'year' },
  { label: '月份', value: 'month' },
  { label: '日期', value: 'day' },
  { label: '小时', value: 'hour' },
  { label: '分钟', value: 'minute' },
  { label: '星期', value: 'weekday' },
  { label: '相机品牌', value: 'cameraBrand' },
  { label: '相机型号', value: 'cameraModel' },
  { label: '镜头型号', value: 'lensModel' },
  { label: '焦段', value: 'focalLength' },
  { label: '光圈', value: 'aperture' },
  { label: 'ISO', value: 'iso' },
  { label: '快门速度', value: 'shutterSpeed' },
  { label: '曝光时间', value: 'exposureTime' },
  { label: '曝光补偿', value: 'exposureCompensation' },
  { label: '白平衡', value: 'whiteBalance' },
  { label: '闪光灯', value: 'flash' },
  { label: '拍摄模式', value: 'shootingMode' },
  { label: '测光模式', value: 'meteringMode' },
  { label: '色彩空间', value: 'colorSpace' },
  { label: '图片宽度', value: 'imageWidth' },
  { label: '图片高度', value: 'imageHeight' },
  { label: '省份', value: 'province' },
  { label: '城市', value: 'city' },
  { label: '区县', value: 'district' },
  { label: '具体地点', value: 'location' },
  { label: '海拔', value: 'altitude' },
  { label: 'GPS经度', value: 'longitude' },
  { label: 'GPS纬度', value: 'latitude' },
  { label: '方向', value: 'orientation' },
  { label: '文件格式', value: 'fileFormat' },
  { label: '文件大小', value: 'fileSize' }
]

const tagGroups = computed(() => [
  {
    name: '时间信息',
    tags: availableTags.filter(t => ['year', 'month', 'day', 'hour', 'minute', 'weekday'].includes(t.value))
  },
  {
    name: '相机信息',
    tags: availableTags.filter(t => ['cameraBrand', 'cameraModel', 'lensModel', 'focalLength', 'aperture', 'iso', 'shutterSpeed', 'exposureTime', 'exposureCompensation', 'whiteBalance', 'flash', 'shootingMode', 'meteringMode', 'colorSpace'].includes(t.value))
  },
  {
    name: '图片信息',
    tags: availableTags.filter(t => ['imageWidth', 'imageHeight', 'fileFormat', 'fileSize'].includes(t.value))
  },
  {
    name: '位置信息',
    tags: availableTags.filter(t => ['province', 'city', 'district', 'location', 'altitude', 'longitude', 'latitude', 'orientation'].includes(t.value))
  }
])

const selectedTags = ref([])

const canArrange = computed(() => {
  return sourceFolder.value && targetFolder.value && selectedTags.value.length > 0
})

const getTagLabel = (value) => {
  const tag = availableTags.find(t => t.value === value)
  return tag ? tag.label : value
}

const selectTag = (value) => {
  if (!selectedTags.value.includes(value)) {
    selectedTags.value.push(value)
  }
}

const removeTag = (index) => {
  selectedTags.value.splice(index, 1)
}

const clearAllTags = () => {
  selectedTags.value = []
}

const selectSourceFolder = () => {
  notify.info('选择照片文件夹功能开发中')
}

const selectTargetFolder = () => {
  notify.info('选择输出文件夹功能开发中')
}

const startArrange = () => {
  notify.info('开始整理功能开发中')
}
</script>

<style scoped>
.smart-arrange-page {
  padding: 24px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.header-title h2 {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.header-desc {
  margin: 0;
  font-size: 14px;
  color: #909399;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.folder-info {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.info-card {
  padding: 20px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-row:last-child {
  border-bottom: none;
}

.info-row .label {
  width: 100px;
  font-size: 14px;
  color: #606266;
}

.info-row .value {
  flex: 1;
  font-size: 14px;
  color: #303133;
  font-weight: 500;
}

.arrange-section {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.section-header {
  padding: 20px;
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
}

.structure-builder {
  padding: 24px;
}

.builder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.builder-header > span {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
}

.selected-tags-container {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  min-height: 80px;
  margin-bottom: 24px;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 40px;
  color: #909399;
  font-size: 14px;
}

.selected-tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.selected-tag {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #ecf5ff;
  border: 1px solid #409eff;
  border-radius: 4px;
  font-size: 14px;
  color: #409eff;
}

.tag-index {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  background: #409eff;
  color: #fff;
  border-radius: 50%;
  font-size: 12px;
  font-weight: 600;
}

.close-icon {
  cursor: pointer;
  color: #909399;
  font-size: 14px;
}

.close-icon:hover {
  color: #f56c6c;
}

.preview-section {
  background: #f8f9fa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  margin-bottom: 24px;
}

.preview-title {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 16px;
}

.preview-content {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
  min-height: 120px;
}

.preview-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 88px;
  color: #909399;
  font-size: 14px;
}

.preview-tree {
  display: flex;
  flex-direction: column;
}

.tree-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  font-size: 14px;
  color: #606266;
}

.tree-item.root {
  font-weight: 600;
  color: #303133;
}

.tree-item.file {
  color: #909399;
}

.tree-item .el-icon {
  color: #409eff;
}

.tree-item.file .el-icon {
  color: #909399;
}

.tree-value {
  color: #c0c4cc;
  font-size: 12px;
}

.tags-selector {
  border-top: 1px solid #e4e7ed;
  padding-top: 24px;
}

.selector-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.tag-groups {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.tag-group {
  background: #fafafa;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 16px;
}

.group-name {
  font-size: 14px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 12px;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-item {
  padding: 6px 14px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.2s;
}

.tag-item:hover {
  border-color: #409eff;
  color: #409eff;
}

.tag-item.tag-selected {
  background: #ecf5ff;
  border-color: #409eff;
  color: #409eff;
}

.action-section {
  display: flex;
  justify-content: center;
  padding: 24px 0;
}
</style>
