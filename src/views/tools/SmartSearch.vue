<template>
  <div class="smart-search-page">
    <div class="search-section">
      <el-input v-model="searchQuery" type="textarea" :rows="3" placeholder="例如：找一张去年夏天在海边拍的全家福，有夕阳和海浪..."
        class="smart-search-input">
        <template #prefix>
          <el-icon>
            <ChatDotRound />
          </el-icon>
        </template>
      </el-input>

      <div class="search-actions">
        <el-button type="primary" size="large" @click="performSmartSearch" :loading="searching"
          :disabled="!searchQuery.trim()">
          智能搜索
        </el-button>
      </div>

      <div class="search-suggestions">
        <h4>试试这些搜索：</h4>
        <div class="suggestion-tags">
          <el-tag v-for="suggestion in searchSuggestions" :key="suggestion" type="info" effect="plain"
            class="suggestion-tag" @click="useSuggestion(suggestion)">
            {{ suggestion }}
          </el-tag>
        </div>
      </div>
    </div>

    <div class="search-results" v-if="hasSearched">
      <div class="results-grid" v-loading="searching">
        <div v-for="result in searchResults" :key="result.id" class="result-card" @click="openPhoto(result)">
          <div class="result-image">
            <img :src="result.url" :alt="result.description" />
          </div>

          <div class="result-info">
            <p class="result-description">{{ result.description }}</p>
            <div class="result-meta">
              <span class="result-date">{{ result.date }}</span>
            </div>
          </div>
        </div>
      </div>

      <el-empty v-if="!searching && searchResults.length === 0" description="未找到匹配的照片" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { notify } from '@/utils'
import { ChatDotRound } from '@element-plus/icons-vue'
import { dbHelper, STORES } from '@/utils/database'

const searchQuery = ref('')
const searching = ref(false)
const hasSearched = ref(false)

const searchSuggestions = ref([
  '去年夏天的海边照片',
  '和家人的合照',
  '旅行中的风景照',
  '生日聚会的照片',
  '宠物可爱瞬间',
  '美食照片',
  '夕阳西下的景色',
  '雪景照片'
])

const searchResults = ref([])

const performSmartSearch = async () => {
  if (!searchQuery.value.trim()) {
    notify.warning('请输入搜索描述')
    return
  }

  searching.value = true
  hasSearched.value = true

  try {
    await dbHelper.init()
    const allPhotos = await dbHelper.getAll(STORES.photos)

    const query = searchQuery.value.toLowerCase()
    const results = allPhotos.filter(photo => {
      const matchName = photo.name?.toLowerCase().includes(query)
      const matchDesc = photo.description?.toLowerCase().includes(query)
      const matchTags = photo.tags?.some(tag =>
        tag.toLowerCase().includes(query)
      )
      const matchPeople = photo.people?.some(person =>
        person.toLowerCase().includes(query)
      )
      const matchPlaces = photo.places?.some(place =>
        place.toLowerCase().includes(query)
      )

      return matchName || matchDesc || matchTags || matchPeople || matchPlaces
    })

    searchResults.value = results
    notify.success(`找到 ${searchResults.value.length} 张匹配的照片`)
  } catch (error) {
    notify.error('搜索失败')
  } finally {
    searching.value = false
  }
}

const useSuggestion = (suggestion) => {
  searchQuery.value = suggestion
  performSmartSearch()
}

const openPhoto = () => {
  notify.info('查看照片详情功能开发中')
}

onMounted(async () => {
  try {
    await dbHelper.init()
  } catch (error) {
    notify.error('初始化失败')
  }
})
</script>

<style scoped>
.smart-search-page {
  padding: 16px;
}

.search-section {
  background: #fff;
  border-radius: 4px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.smart-search-input {
  margin-bottom: 14px;
}

.smart-search-input :deep(.el-textarea__inner) {
  border-radius: 4px;
  font-size: 14px;
  line-height: 1.5;
}

.search-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.search-suggestions {
  padding-top: 18px;
}

.search-suggestions h4 {
  font-size: 13px;
  color: #606266;
  margin: 0 0 12px 0;
  font-weight: 500;
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tag {
  cursor: pointer;
  padding: 6px 12px;
  font-size: 13px;
}

.search-results {
  background: #fff;
  border-radius: 4px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.results-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}

.result-card {
  background: #fff;
  border-radius: 4px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  cursor: pointer;
}

.result-image {
  width: 100%;
  height: 180px;
  overflow: hidden;
}

.result-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.result-info {
  padding: 16px;
}

.result-description {
  font-size: 14px;
  color: #303133;
  margin: 0 0 10px 0;
  line-height: 1.5;
  font-weight: 500;
}

.result-meta {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.result-date {
  font-size: 12px;
  color: #909399;
}
</style>
