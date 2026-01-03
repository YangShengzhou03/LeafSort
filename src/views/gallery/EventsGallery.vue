<template>
  <div class="events-gallery-page">
    <div class="header-actions">
      <el-button type="primary" @click="showCreateEventDialog = true">
        <el-icon><Plus /></el-icon>
        创建事件
      </el-button>
      <el-button @click="refreshEvents">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <div class="events-grid" v-loading="loading">
      <div v-for="event in events" :key="event.id" class="event-card" @click="openEvent(event)">
        <div class="event-image">
          <img v-if="event.coverImage" :src="event.coverImage" :alt="event.title" />
          <div v-else class="event-image-placeholder">
            <el-icon><Calendar /></el-icon>
          </div>
          <div class="event-overlay">
            <div class="photo-count">{{event.photoCount}}</div>
          </div>
        </div>
        <div class="event-info">
          <h3 class="event-title">{{event.title}}</h3>
          <p class="event-description">{{event.description}}</p>
          <div class="event-location">
            <el-icon><Location /></el-icon>
            <span>{{event.location}}</span>
          </div>
          <div class="event-date">
            <el-icon><Calendar /></el-icon>
            <span>{{event.date.toLocaleDateString('zh-CN')}}</span>
          </div>
          <div class="event-tags">
            <el-tag v-for="(tag, index) in event.tags" :key="tag" size="small" :type="getTagType(index)">
              {{tag}}
            </el-tag>
          </div>
        </div>
      </div>
    </div>

    <el-empty
      v-if="!loading && events.length === 0"
      description="暂无事件数据，请先创建事件或导入照片"
    >
      <el-button type="primary" @click="showCreateEventDialog = true">
        创建事件
      </el-button>
    </el-empty>

    <el-dialog
      v-model="showCreateEventDialog"
      title="创建事件"
      width="500px"
    >
      <el-form :model="newEventForm" label-width="80px">
        <el-form-item label="事件标题">
          <el-input v-model="newEventForm.title" placeholder="请输入事件标题" />
        </el-form-item>
        <el-form-item label="事件日期">
          <el-date-picker
            v-model="newEventForm.date"
            type="date"
            placeholder="选择日期"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="地点">
          <el-input v-model="newEventForm.location" placeholder="请输入地点" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="newEventForm.description"
            type="textarea"
            placeholder="请输入事件描述"
          />
        </el-form-item>
        <el-form-item label="标签">
          <el-select
            v-model="newEventForm.tags"
            multiple
            filterable
            allow-create
            placeholder="请输入标签"
          >
            <el-option
              v-for="tag in availableTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateEventDialog = false">取消</el-button>
        <el-button type="primary" @click="createEvent">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { notify, getTagType } from '@/utils'
import { Plus, Refresh, Calendar, Location } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'

const loading = ref(false)
const showCreateEventDialog = ref(false)

const events = ref([])

const newEventForm = reactive({
  title: '',
  date: new Date(),
  location: '',
  description: '',
  tags: []
})

const availableTags = ref(['生日', '聚会', '旅行', '婚礼', '毕业', '节日', '运动', '美食'])

const refreshEvents = async () => {
  loading.value = true
  try {
    await dbHelper.init()
    events.value = await dbHelper.getAll(STORES.events)
    notify.success('事件数据已刷新')
  } catch (error) {
    notify.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const openEvent = () => {
  notify.info('查看事件详情功能开发中')
}

const createEvent = async () => {
  if (!newEventForm.title.trim()) {
    notify.warning('请输入事件标题')
    return
  }

  try {
    const newEvent = {
      id: Date.now(),
      title: newEventForm.title,
      coverImage: '',
      photoCount: 0,
      description: newEventForm.description,
      location: newEventForm.location,
      date: newEventForm.date,
      tags: newEventForm.tags,
      createdAt: new Date().toISOString()
    }

    await dbHelper.add(STORES.events, newEvent)
    events.value.unshift(newEvent)
    showCreateEventDialog.value = false

    newEventForm.title = ''
    newEventForm.date = new Date()
    newEventForm.location = ''
    newEventForm.description = ''
    newEventForm.tags = []

    notify.success('事件创建成功')
  } catch (error) {
    notify.error('创建失败')
  }
}

onMounted(() => {
  refreshEvents()
})
</script>

<style scoped>
.events-gallery-page {
  padding: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.events-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.event-card {
  background: #fff;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: all 0.2s ease;
}

.event-card:hover {
  background: #fafafa;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.event-image {
  position: relative;
  width: 100%;
  height: 140px;
  overflow: hidden;
  background: #f5f7fa;
}

.event-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease;
}

.event-image-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
}

.event-image-placeholder .el-icon {
  font-size: 48px;
  color: rgba(255, 255, 255, 0.3);
}

.event-card:hover .event-image img {
  transform: scale(1.02);
}

.event-overlay {
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

.event-info {
  padding: 16px;
}

.event-title {
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 6px 0;
}

.event-description {
  font-size: 13px;
  color: #606266;
  margin: 0 0 6px 0;
}

.event-location {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 6px;
}

.event-date {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: #909399;
  margin-bottom: 10px;
}

.event-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
</style>
