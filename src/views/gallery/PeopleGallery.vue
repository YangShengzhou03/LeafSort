<template>
  <div class="people-gallery-page">
    <div class="header-actions">
      <el-button type="primary" @click="showAddPersonDialog = true">
        <el-icon>
          <Plus />
        </el-icon>
        添加人物
      </el-button>
      <el-button @click="refreshPeople">
        <el-icon>
          <Refresh />
        </el-icon>
        刷新
      </el-button>
    </div>

    <div class="people-grid" v-loading="loading">
      <div v-for="person in people" :key="person.id" class="person-card" @click="openPerson(person)">
        <div class="person-avatar">
          <img :src="person.avatar" :alt="person.name" />
          <div class="photo-count">{{ person.photoCount }}</div>
        </div>
        <div class="person-info">
          <h3 class="person-name">{{ person.name }}</h3>
          <p class="person-description">{{ person.description }}</p>
          <div class="person-tags">
            <el-tag v-for="(tag, index) in person.tags" :key="tag" size="small" :type="getTagType(index)">
              {{ tag }}
            </el-tag>
          </div>
        </div>
        <el-button link type="danger" class="delete-btn" @click.stop="deletePerson(person)">
          <el-icon>
            <Delete />
          </el-icon>
        </el-button>
      </div>
    </div>

    <el-empty v-if="!loading && people.length === 0" description="暂无人物数据，请先添加人物或导入照片">
      <el-button type="primary" @click="showAddPersonDialog = true">
        添加人物
      </el-button>
    </el-empty>

    <el-dialog v-model="showAddPersonDialog" title="添加人物" width="500px">
      <el-form :model="newPersonForm" label-width="80px">
        <el-form-item label="姓名">
          <el-input v-model="newPersonForm.name" placeholder="请输入人物姓名" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="newPersonForm.description" type="textarea" placeholder="请输入人物描述" />
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="newPersonForm.tags" multiple filterable allow-create placeholder="请输入标签">
            <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddPersonDialog = false">取消</el-button>
        <el-button type="primary" @click="addPerson">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { notify, getTagType } from '@/utils'
import { Plus, Refresh, Delete } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'
const loading = ref(false)
const showAddPersonDialog = ref(false)

const people = ref([])

const newPersonForm = reactive({
  name: '',
  description: '',
  tags: []
})

const availableTags = ref(['家人', '朋友', '同事', '同学', '旅行'])

const refreshPeople = async () => {
  loading.value = true
  try {
    await dbHelper.init()
    people.value = await dbHelper.getAll(STORES.people)
    notify.success('人物数据已刷新')
  } catch (error) {
    notify.error('刷新失败')
  } finally {
    loading.value = false
  }
}

const addPerson = async () => {
  if (!newPersonForm.name.trim()) {
    notify.warning('请输入人物姓名')
    return
  }

  try {
    const newPerson = {
      id: Date.now() + Math.random(),
      name: newPersonForm.name,
      avatar: '/api/placeholder/200/200',
      photoCount: 0,
      description: newPersonForm.description,
      tags: newPersonForm.tags,
      createdAt: new Date().toISOString()
    }

    await dbHelper.add(STORES.people, newPerson)
    people.value.push(newPerson)
    showAddPersonDialog.value = false

    newPersonForm.name = ''
    newPersonForm.description = ''
    newPersonForm.tags = []

    notify.success('人物添加成功')
  } catch (error) {
    notify.error('添加失败')
  }
}

const deletePerson = async (person) => {
  try {
    await dbHelper.delete(STORES.people, person.id)
    const index = people.value.findIndex(p => p.id === person.id)
    if (index > -1) {
      people.value.splice(index, 1)
    }
    notify.success('人物删除成功')
  } catch (error) {
    notify.error('删除失败')
  }
}

onMounted(() => {
  refreshPeople()
})
</script>

<style scoped>
.people-gallery-page {
  padding: 20px;
}

.header-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 30px;
}

.people-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.person-card {
  background: #fff;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s ease;
}

.person-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}

.person-avatar {
  position: relative;
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
}

.person-avatar img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #f5f7fa;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.photo-count {
  position: absolute;
  bottom: -4px;
  right: -4px;
  background: #409eff;
  color: white;
  border-radius: 4px;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 700;
  border: 3px solid #fff;
}

.person-info {
  text-align: center;
}

.person-name {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 8px 0;
}

.person-description {
  font-size: 14px;
  color: #909399;
  margin: 0 0 16px 0;
  line-height: 1.5;
}

.person-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  justify-content: center;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  padding: 4px;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.person-card:hover .delete-btn {
  opacity: 1;
}
</style>
