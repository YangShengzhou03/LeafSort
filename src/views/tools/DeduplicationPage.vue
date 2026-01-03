<template>
  <div class="deduplication-page">
    <div class="header-actions">
      <el-button type="primary">
        <el-icon><Search /></el-icon>
        开始扫描
      </el-button>
      <el-button>
        <el-icon><FolderOpened /></el-icon>
        选择文件夹
      </el-button>
    </div>

    <div class="content-section">
      <div class="scan-options">
        <div class="options-card">
          <div class="card-title">扫描选项</div>
          <div class="options-list">
            <div class="option-item">
              <span class="option-label">查重方式</span>
              <el-radio-group v-model="dedupMethod">
                <el-radio label="pHash">感知哈希</el-radio>
                <el-radio label="md5">MD5</el-radio>
              </el-radio-group>
            </div>
            <div v-if="dedupMethod === 'pHash'" class="option-item">
              <span class="option-label">相似度阈值</span>
              <el-slider :min="0" :max="100" :step="5" />
            </div>
          </div>
        </div>
      </div>

      <div class="duplicate-results">
        <h2 class="section-title">重复文件</h2>
        <el-empty description="点击开始扫描查找重复文件" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, FolderOpened } from '@element-plus/icons-vue'

const dedupMethod = ref('pHash')
</script>

<style scoped>
.deduplication-page {
  padding: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
}

.content-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.scan-options {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.options-card {
  padding: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.options-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.option-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.duplicate-results {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  min-height: 300px;
}

.duplicate-results h2 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 16px 0;
}
</style>
