<template>
  <div class="colors-gallery-page">
    <div class="header-actions">
      <el-button type="primary" @click="showAddColorDialog = true">
        <el-icon><Plus /></el-icon>
        添加颜色
      </el-button>
      <el-button @click="refreshColors">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="colors-grid" v-loading="loading">
      <div v-for="color in colors" :key="color.id" class="color-card" @click="openColor(color)">
        <div class="color-image">
          <img v-if="color.coverImage" :src="color.coverImage" :alt="color.name" />
          <div v-else class="color-image-placeholder" :style="{ background: color.hexCode }">
            <el-icon><Brush /></el-icon>
          </div>
          <div class="color-overlay">
            <div class="photo-count">{{color.photoCount}}</div>
          </div>
        </div>
        <div class="color-info">
          <h3 class="color-name">{{color.name}}</h3>
          <p class="color-description">{{color.description}}</p>
          <div class="color-hex">
            <el-icon><Picture /></el-icon>
            <span>{{color.hexCode}}</span>
          </div>
          <div class="color-tags">
            <el-tag v-for="(tag, index) in color.tags" :key="tag" size="small" :type="getTagType(index)">
              {{tag}}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && colors.length === 0" description="暂无颜色数据，请先添加颜色或导入照片">
      <el-button type="primary" @click="showAddColorDialog = true">
        添加颜色
      </el-button>
    </el-empty>

    <el-dialog v-model="showAddColorDialog" title="添加颜色" width="500px">
      <el-form :model="newColorForm" label-width="80px">
        <el-form-item label="颜色名称">
          <el-input v-model="newColorForm.name" placeholder="请输入颜色名称" />
        </el-form-item>
        <el-form-item label="色值">
          <el-color-picker v-model="newColorForm.hexCode" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newColorForm.description" type="textarea" placeholder="请输入颜色描述" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="newColorForm.tags" multiple filterable allow-create placeholder="请输入标签">
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddColorDialog = false">取消</el-button>
        <el-button type="primary" @click="addColor">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { notify, getTagType } from '@/utils'
import { Plus, Refresh, Brush, Picture } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'

const loading = ref(false)
const showAddColorDialog = ref(false)

const colors = ref([])

const newColorForm = reactive({
  name: '',
  hexCode: '#409EFF',
  description: '',
  tags: []
})

const availableTags = ref(['蓝色', '红色', '绿色', '黄色', '紫色', '粉色', '黑色', '白色'])

const refreshColors = async () => {
  loading.value = true
  try {
    await dbHelper.init()
    const allAlbums = await dbHelper.getAll(STORES.albums)
    colors.value = allAlbums.filter(album => album.type === 'color')
    notify.success('颜色数据已刷新')
  } catch (error) {
    notify.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const openColor = () => {
  notify.info('查看颜色详情功能开发中')
}

const addColor = async () => {
  if (!newColorForm.name.trim()) {
    notify.warning('请输入颜色名称')
    return
  }

  try {
    const newColor = {
      id: Date.now(),
      name: newColorForm.name,
      type: 'color',
      coverImage: '',
      photoCount: 0,
      description: newColorForm.description,
      hexCode: newColorForm.hexCode,
      tags: newColorForm.tags,
      createdAt: new Date().toISOString()
    }

    await dbHelper.add(STORES.albums, newColor)
    colors.value.push(newColor)
    showAddColorDialog.value = false

    newColorForm.name = ''
    newColorForm.hexCode = '#409EFF'
    newColorForm.description = ''
    newColorForm.tags = []

    notify.success('颜色添加成功')
  } catch (error) {
    notify.error('添加失败')
  }
}

onMounted(() => {
  refreshColors()
})
</script>

<style scoped>
.colors-gallery-page {
  padding: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.colors-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.color-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.color-card:hover {
  background: #fafafa;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.color-image {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f5f7fa;
}

.color-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.color-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.color-image-placeholder .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.5);
}

.color-card:hover .color-image img {
  transform: scale(1.02);
}

.color-overlay {
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

.color-info {
  padding: 16px;
}

.color-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.color-description {
  font-size: 13px;
  color: #606266;
  margin: 0 0 6px 0;
}

.color-hex {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 10px;
}

.color-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
