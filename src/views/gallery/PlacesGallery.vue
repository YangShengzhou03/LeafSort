<template>
  <div class="places-gallery-page">
    <div class="header-actions">
      <el-button type="primary" @click="showAddPlaceDialog = true">
        <el-icon>
          <Plus />
        </el-icon>
        添加地点
      </el-button>
      <el-button @click="refreshPlaces">
        <el-icon>
          <Refresh />
        </el-icon>
        刷新
      </el-button>
    </div>

    <div class="places-grid" v-loading="loading">
      <div v-for="place in places" :key="place.id" class="place-card" @click="openPlace(place)">
        <div class="place-image">
          <img v-if="place.coverImage" :src="place.coverImage" :alt="place.name" />
          <div v-else class="place-image-placeholder">
            <el-icon>
              <Location />
            </el-icon>
          </div>
          <div class="place-overlay">
            <div class="photo-count">{{ place.photoCount }}</div>
          </div>
        </div>
        <div class="place-info">
          <h3 class="place-name">{{ place.name }}</h3>
          <p class="place-address">{{ place.address }}</p>
          <div class="place-coordinates">
            <el-icon>
              <Location />
            </el-icon>
            <span>{{ place.coordinates }}</span>
          </div>
          <div class="place-tags">
            <el-tag v-for="(tag, index) in place.tags" :key="tag" size="small" :type="getTagType(index)">
              {{ tag }}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && places.length === 0" description="暂无地点数据，请先添加地点或导入带有位置信息的照片">
      <el-button type="primary" @click="showAddPlaceDialog = true">
        添加地点
      </el-button>
    </el-empty>

    <el-dialog v-model="showAddPlaceDialog" title="添加地点" width="500px">
      <el-form :model="newPlaceForm" label-width="80px">
        <el-form-item label="地点名称">
          <el-input v-model="newPlaceForm.name" placeholder="请输入地点名称" />
        </el-form-item>
        <el-form-item label="地址">
          <el-input v-model="newPlaceForm.address" placeholder="请输入详细地址" />
        </el-form-item>
        <el-form-item label="坐标">
          <el-input v-model="newPlaceForm.coordinates" placeholder="纬度, 经度" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="newPlaceForm.tags" multiple filterable allow-create placeholder="请输入标签">
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPlaceDialog = false">取消</el-button>
        <el-button type="primary" @click="addPlace">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { notify, getTagType } from '@/utils'
import { Plus, Refresh, Location } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'
const loading = ref(false)
const showAddPlaceDialog = ref(false)

const places = ref([])

const loadPlaces = async () => {
  try {
    loading.value = true
    const data = await dbHelper.getAll(STORES.places)
    places.value = data || []
  } catch (error) {
    notify.error('加载地点数据失败')
    places.value = []
  } finally {
    loading.value = false
  }
}

const newPlaceForm = reactive({
  name: '',
  address: '',
  coordinates: '',
  tags: []
})

const availableTags = ref(['旅游', '地标', '历史', '城市', '自然', '美食', '购物'])

const refreshPlaces = () => {
  loadPlaces()
  notify.success('地点数据已刷新')
}

const openPlace = () => {
  notify.info('查看地点详情功能开发中')
}

const addPlace = async () => {
  if (!newPlaceForm.name.trim()) {
    notify.warning('请输入地点名称')
    return
  }

  const newPlace = {
    id: Date.now(),
    name: newPlaceForm.name,
    coverImage: '/api/placeholder/300/200',
    photoCount: 0,
    address: newPlaceForm.address,
    coordinates: newPlaceForm.coordinates,
    tags: newPlaceForm.tags
  }

  try {
    await dbHelper.add(STORES.places, newPlace)
    places.value.push(newPlace)
    showAddPlaceDialog.value = false

    newPlaceForm.name = ''
    newPlaceForm.address = ''
    newPlaceForm.coordinates = ''
    newPlaceForm.tags = []

    notify.success('地点添加成功')
  } catch (error) {
    notify.error('添加地点失败')
  }
}

onMounted(() => {
  loadPlaces()
})
</script>

<style scoped>
.places-gallery-page {
  padding: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.places-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.place-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.place-card:hover {
  background: #fafafa;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.place-image {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f5f7fa;
}

.place-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.place-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #e8f5e9 0%, #d4e4f8 100%);
}

.place-image-placeholder .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.3);
}

.place-card:hover .place-image img {
  transform: scale(1.02);
}

.place-overlay {
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

.place-info {
  padding: 16px;
}

.place-name {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.place-address {
  font-size: 13px;
  color: #606266;
  margin: 0 0 6px 0;
}

.place-coordinates {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 10px;
}

.place-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
