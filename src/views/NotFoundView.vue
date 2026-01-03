<template>
  <div class="not-found">
    <el-icon :size="100" class="error-icon"><WarningFilled /></el-icon>
    <h1 class="error-title">404</h1>
    <p class="error-description">抱歉，您访问的页面不存在</p>
    <div class="error-actions">
      <el-button type="primary" size="large" @click="$router.push('/')">
        <el-icon><House /></el-icon>
        返回首页
      </el-button>
      <el-button size="large" @click="$router.back()">
        <el-icon><Back /></el-icon>
        返回上页
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { WarningFilled, House, Back } from '@element-plus/icons-vue'
</script>

<style scoped>
.not-found {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 60px);
  background: #f5f7fa;
  color: #303133;
  padding: 40px;
}

.error-icon {
  margin-bottom: 16px;
  color: #f56c6c;
}

.error-title {
  font-size: 64px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #303133;
}

.error-description {
  font-size: 16px;
  margin: 0 0 32px 0;
  color: #606266;
}

.error-actions {
  display: flex;
  gap: 12px;
}
</style>
