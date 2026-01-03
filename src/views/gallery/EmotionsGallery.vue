<template>
  <div class="emotions-gallery-page">
    <div class="header-actions">
      <el-button type="primary" @click="showAddEmotionDialog = true">
        <el-icon><Plus /></el-icon>
        添加情绪
      </el-button>
      <el-button @click="refreshEmotions">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="emotions-grid" v-loading="loading">
      <div v-for="emotion in emotions" :key="emotion.id" class="emotion-card" @click="openEmotion(emotion)">
        <div class="emotion-image">
          <img v-if="emotion.coverImage" :src="emotion.coverImage" :alt="emotion.name" />
          <div v-else class="emotion-image-placeholder">
            <el-icon><Star /></el-icon>
          </div>
          <div class="emotion-overlay">
            <div class="photo-count">{{emotion.photoCount}}</div>
          </div>
        </div>
        <div class="emotion-info">
          <h3 class="emotion-name">{{emotion.name}}</h3>
          <p class="emotion-description">{{emotion.description}}</p>
          <div class="emotion-intensity">
            <el-icon><TrendCharts /></el-icon>
            <span>强度: {{emotion.intensity}}</span>
          </div>
          <div class="emotion-tags">
            <el-tag v-for="(tag, index) in emotion.tags" :key="tag" size="small" :type="getTagType(index)">
              {{tag}}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && emotions.length === 0" description="暂无情绪数据，请先添加情绪或导入照片">
      <el-button type="primary" @click="showAddEmotionDialog = true">
        添加情绪
      </el-button>
    </el-empty>

    <el-dialog v-model="showAddEmotionDialog" title="添加情绪" width="500px">
      <el-form :model="newEmotionForm" label-width="80px">
        <el-form-item label="情绪名称">
          <el-input v-model="newEmotionForm.name" placeholder="请输入情绪名称" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newEmotionForm.description" type="textarea" placeholder="请输入情绪描述" />
        </el-form-item>
        <el-form-item label="强度">
          <el-rate v-model="newEmotionForm.intensity" :max="5" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="newEmotionForm.tags" multiple filterable allow-create placeholder="请输入标签">
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddEmotionDialog = false">取消</el-button>
        <el-button type="primary" @click="addEmotion">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { notify, getTagType } from '@/utils'
import { Plus, Refresh, Star, TrendCharts } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'

const loading = ref(false)
const showAddEmotionDialog = ref(false)

const emotions = ref([])

const newEmotionForm = reactive({
  name: '',
  description: '',
  intensity: 3,
  tags: []
})

const availableTags = ref(['快乐', '感动', '温馨', '宁静', '激动', '惊喜', '满足', '期待'])

const refreshEmotions = async () => {
  loading.value = true
  try {
    await dbHelper.init()
    const allAlbums = await dbHelper.getAll(STORES.albums)
    emotions.value = allAlbums.filter(album => album.type === 'emotion')
    notify.success('情绪数据已刷新')
  } catch (error) {
    notify.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const openEmotion = () => {
  notify.info('查看情绪详情功能开发中')
}

const addEmotion = async () => {
  if (!newEmotionForm.name.trim()) {
    notify.warning('请输入情绪名称')
    return
  }

  try {
    const newEmotion = {
      id: Date.now(),
      name: newEmotionForm.name,
      type: 'emotion',
      coverImage: '',
      photoCount: 0,
      description: newEmotionForm.description,
      intensity: newEmotionForm.intensity,
      tags: newEmotionForm.tags,
      createdAt: new Date().toISOString()
    }

    await dbHelper.add(STORES.albums, newEmotion)
    emotions.value.push(newEmotion)
    showAddEmotionDialog.value = false

    newEmotionForm.name = ''
    newEmotionForm.description = ''
    newEmotionForm.intensity = 3
    newEmotionForm.tags = []

    notify.success('情绪添加成功')
  } catch (error) {
    notify.error('添加失败')
  }
}

onMounted(() => {
  refreshEmotions()
})
</script>

<style scoped>
.emotions-gallery-page {
  padding: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.emotions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.emotion-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.emotion-card:hover {
  background: #fafafa;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.emotion-image {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f5f7fa;
}

.emotion-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.emotion-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fce4ec 0%, #f8bbd9 100%);
}

.emotion-image-placeholder .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.3);
}

.emotion-card:hover .emotion-image img {
  transform: scale(1.02);
}

.emotion-overlay {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 20px;
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  backdrop-filter: blur(4px);
}

.emotion-info {
  padding: 16px;
}

.emotion-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.emotion-description {
  font-size: 13px;
  color: #606266;
  margin: 0 0 6px 0;
}

.emotion-intensity {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 10px;
}

.emotion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
