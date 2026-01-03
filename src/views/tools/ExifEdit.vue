<template>
  <div class="exif-edit-page">
    <div class="header-actions">
      <el-button type="primary">
        <el-icon><FolderOpened /></el-icon>
        选择目录
      </el-button>
      <el-button>
        <el-icon><Download /></el-icon>
        导出EXIF
      </el-button>
    </div>

    <div class="content-section">
      <div class="photo-preview">
        <el-empty description="请选择要编辑的照片" />
      </div>

      <div class="exif-info">
        <div class="info-card">
          <div class="card-title">EXIF信息</div>
          <div class="form-list">
            <div class="form-item">
              <span class="item-label">相机品牌</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">相机型号</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">拍摄时间</span>
              <el-date-picker type="datetime" placeholder="选择日期时间" />
            </div>
            <div class="form-item">
              <span class="item-label">拍摄地点</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">光圈值</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">快门速度</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">ISO</span>
              <el-input placeholder="未设置" />
            </div>
            <div class="form-item">
              <span class="item-label">焦距</span>
              <el-input placeholder="未设置" />
            </div>
          </div>
          <div class="form-actions">
            <el-button type="primary">写入</el-button>
            <el-button>重置</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FolderOpened, Download } from '@element-plus/icons-vue'
</script>

<style scoped>
.exif-edit-page {
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

.photo-preview {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  padding: 20px;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.exif-info {
  background: #fff;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.info-card {
  padding: 20px;
}

.card-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  margin-bottom: 20px;
}

.form-list {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px 24px;
}

.form-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}
</style>
