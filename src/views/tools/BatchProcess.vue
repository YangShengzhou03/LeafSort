<template>
  <div class="batch-process-page">
    <div class="header-actions">
      <el-button type="primary">
        <el-icon><FolderOpened /></el-icon>
        选择照片
      </el-button>
      <el-button>
        <el-icon><Upload /></el-icon>
        导入照片
      </el-button>
    </div>

    <div class="content-section">
      <div class="selected-photos">
        <div class="section-header">
          <h2 class="section-title">已选择 <span class="count">0</span> 张照片</h2>
          <el-button type="danger" size="small" :disabled="true">
            <el-icon><Delete /></el-icon>
            清空选择
          </el-button>
        </div>
        <el-empty description="请选择要处理的照片" />
      </div>

      <div class="process-options">
        <el-card>
          <template #header>
            <span>处理选项</span>
          </template>
          <el-tabs>
            <el-tab-pane label="调整大小">
              <el-form label-width="100px">
                <el-form-item label="调整方式">
                  <el-radio-group>
                    <el-radio label="percentage">按百分比</el-radio>
                    <el-radio label="pixel">按像素</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="缩放比例">
                  <el-slider :min="10" :max="200" />
                </el-form-item>
                <el-form-item label="保持比例">
                  <el-switch />
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="格式转换">
              <el-form label-width="100px">
                <el-form-item label="目标格式">
                  <el-select>
                    <el-option label="JPEG" value="jpeg" />
                    <el-option label="PNG" value="png" />
                    <el-option label="WEBP" value="webp" />
                  </el-select>
                </el-form-item>
                <el-form-item label="质量">
                  <el-slider :min="1" :max="100" />
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="水印">
              <el-form label-width="100px">
                <el-form-item label="添加水印">
                  <el-switch />
                </el-form-item>
                <el-form-item label="水印类型">
                  <el-radio-group>
                    <el-radio label="text">文字</el-radio>
                    <el-radio label="image">图片</el-radio>
                  </el-radio-group>
                </el-form-item>
                <el-form-item label="水印内容">
                  <el-input placeholder="输入水印文字" />
                </el-form-item>
                <el-form-item label="位置">
                  <el-select>
                    <el-option label="右下角" value="bottom-right" />
                    <el-option label="左下角" value="bottom-left" />
                    <el-option label="右上角" value="top-right" />
                    <el-option label="左上角" value="top-left" />
                    <el-option label="居中" value="center" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>

            <el-tab-pane label="重命名">
              <el-form label-width="100px">
                <el-form-item label="重命名规则">
                  <el-input placeholder="例如：IMG_{date}_{index}" />
                </el-form-item>
                <el-form-item label="日期格式">
                  <el-select>
                    <el-option label="YYYY-MM-DD" value="yyyy-mm-dd" />
                    <el-option label="YYYYMMDD" value="yyyymmdd" />
                    <el-option label="MM-DD-YYYY" value="mm-dd-yyyy" />
                  </el-select>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>

          <div class="form-actions">
            <el-button type="primary" :disabled="true">
              <el-icon><Check /></el-icon>
              开始处理
            </el-button>
            <el-button>重置选项</el-button>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { FolderOpened, Upload, Delete, Check } from '@element-plus/icons-vue'
</script>

<style scoped>
.batch-process-page {
  padding: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.content-section {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 16px;
}

.selected-photos {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  min-height: 450px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h2 {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  margin: 0;
}

.count {
  color: #409eff;
  font-weight: 700;
}

.process-options {
  background: #fff;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e6eb;
}

@media (max-width: 1200px) {
  .content-section {
    grid-template-columns: 1fr;
  }
}
</style>
