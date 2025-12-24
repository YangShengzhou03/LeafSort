<template>
  <div id="app" class="app-container">
    <div class="main-layout">
      <aside class="side-navigation">
        <div class="sidebar-header">
          <div class="sidebar-actions">
          </div>
        </div>
        
        <el-menu
          default-active="/"
          class="menu-container"
          :unique-opened="true"
          router
        >
          <!-- 首页/总览 -->
          <el-menu-item index="/home">
            <el-icon><House /></el-icon>
            <span>首页</span>
          </el-menu-item>
          
          <!-- 核心入口 -->
          <el-menu-item index="/all-photos">
            <el-icon><Picture /></el-icon>
            <span>所有照片</span>
          </el-menu-item>
          
          <el-menu-item index="/timeline">
            <el-icon><Calendar /></el-icon>
            <span>时间线</span>
          </el-menu-item>
          
          <!-- 相册管理 -->
          <el-sub-menu index="albums">
            <template #title>
              <el-icon><Film /></el-icon>
              <span>我的相册</span>
            </template>
            <el-menu-item index="/recent">
              <el-icon><Clock /></el-icon>
              <span>最近添加</span>
              <el-tag size="small" type="info">12</el-tag>
            </el-menu-item>
            <el-menu-item index="/favorites">
              <el-icon><Star /></el-icon>
              <span>我的收藏</span>
              <el-tag size="small" type="info">23</el-tag>
            </el-menu-item>
            <el-menu-item index="/videos">
              <el-icon><VideoCamera /></el-icon>
              <span>视频专辑</span>
              <el-tag size="small" type="info">45</el-tag>
            </el-menu-item>
            <el-menu-item index="/story-albums">
              <el-icon><Notebook /></el-icon>
              <span>故事影集</span>
              <el-tag size="small" type="info">8</el-tag>
            </el-menu-item>
            <el-menu-item index="/family">
              <el-icon><User /></el-icon>
              <span>家人</span>
              <el-tag size="small" type="info">67</el-tag>
            </el-menu-item>
            <el-menu-item index="/travel">
              <el-icon><MapLocation /></el-icon>
              <span>旅行</span>
              <el-tag size="small" type="info">23</el-tag>
            </el-menu-item>
            <el-menu-item index="/create-album">
              <el-icon><Plus /></el-icon>
              <span>创建相册</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 智能分类 -->
          <el-sub-menu index="smart">
            <template #title>
              <el-icon><MagicStick /></el-icon>
              <span>智能分类</span>
            </template>
            <el-menu-item index="/people">
              <el-icon><User /></el-icon>
              <span>人物</span>
              <el-tag size="small" type="info">189</el-tag>
            </el-menu-item>
            <el-menu-item index="/places">
              <el-icon><MapLocation /></el-icon>
              <span>地点</span>
              <el-tag size="small" type="info">45</el-tag>
            </el-menu-item>
            <el-menu-item index="/scenes">
              <el-icon><Camera /></el-icon>
              <span>场景</span>
              <el-tag size="small" type="info">52</el-tag>
            </el-menu-item>
            <el-menu-item index="/events">
              <el-icon><Calendar /></el-icon>
              <span>事件</span>
              <el-tag size="small" type="info">23</el-tag>
            </el-menu-item>
            <el-menu-item index="/pets">
              <el-icon><User /></el-icon>
              <span>宠物</span>
              <el-tag size="small" type="info">34</el-tag>
            </el-menu-item>
            <el-menu-item index="/food">
              <el-icon><Food /></el-icon>
              <span>美食</span>
              <el-tag size="small" type="info">28</el-tag>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 工具与功能 -->
          <el-sub-menu index="tools">
            <template #title>
              <el-icon><Tools /></el-icon>
              <span>工具</span>
            </template>
            <el-menu-item index="/photo-editor">
              <el-icon><Brush /></el-icon>
              <span>照片编辑</span>
            </el-menu-item>
            <el-menu-item index="/duplicates">
              <el-icon><CopyDocument /></el-icon>
              <span>相似照片</span>
              <el-tag size="small" type="info">142</el-tag>
            </el-menu-item>
            <el-menu-item index="/smart-cleanup">
              <el-icon><Brush /></el-icon>
              <span>智能清理</span>
              <el-tag size="small" type="info">45</el-tag>
            </el-menu-item>
            <el-menu-item index="/batch-operations">
              <el-icon><Collection /></el-icon>
              <span>批量操作</span>
            </el-menu-item>
            <el-menu-item index="/export">
              <el-icon><Download /></el-icon>
              <span>导出</span>
            </el-menu-item>
            <el-menu-item index="/print">
              <el-icon><Link /></el-icon>
              <span>打印</span>
            </el-menu-item>
          </el-sub-menu>
          
          <!-- 系统功能 -->
          <el-menu-item index="/settings">
            <el-icon><Setting /></el-icon>
            <span>设置</span>
          </el-menu-item>
          
          <el-menu-item index="/trash">
            <el-icon><Delete /></el-icon>
            <span>回收站</span>
            <el-tag v-if="trashCount > 0" size="small" type="danger">{{ trashCount }}</el-tag>
          </el-menu-item>
        </el-menu>
        </aside>
      
      <div class="right-section">
        <CustomTitleBar />
        
        <div class="content-section">
          <el-header class="toolbar-header" height="auto">
            <MaterialToolbar 
            :selected-count="selectedPhotos.length"
            :active-view="activeView"
            @view-change="handleViewChange"
            @search="handleSearch"
            @filter-change="handleFilterChange"
            @sort-change="handleSortChange"
            @import="handleImport"
          />
          </el-header>
          
          <el-main class="content-area">
            <router-view />
          </el-main>
        </div>
      </div>
      
      <el-aside class="detail-panel" width="320px" v-if="showDetailPanel">
        <div class="detail-header">
          <span>照片详情</span>
          <button class="btn btn-ghost btn-icon" @click="closeDetailPanel">
            <el-icon><Close /></el-icon>
          </button>
        </div>
        <div class="detail-content">
          <div v-if="selectedPhoto" class="photo-detail">
            <div class="photo-preview">
              <img v-if="selectedPhoto.type === 'image' && selectedPhoto.thumbnail" :src="selectedPhoto.thumbnail" alt="照片预览" />
              <div v-else-if="selectedPhoto.type === 'audio'" class="audio-preview">
                <div class="audio-wave" :class="selectedPhoto.color"></div>
              </div>
              <div v-else-if="selectedPhoto.type === 'video'" class="video-preview">
                <div class="video-icon"></div>
                <div class="video-duration">{{ selectedPhoto.duration || '00:00' }}</div>
              </div>
              <div v-else class="default-preview">
                <div class="file-icon">{{ getFileExtension(selectedPhoto.name).toUpperCase() }}</div>
              </div>
            </div>
            
            <div class="photo-info-section">
              <h3>{{ selectedPhoto.name }}</h3>
              <div class="photo-source">
                <span>来源: 本地文件</span>
              </div>
              <div class="view-stats">
                <span><el-icon><View /></el-icon> {{ selectedPhoto.views || 0 }}</span>
                <span><el-icon><Download /></el-icon> {{ selectedPhoto.downloads || 0 }}</span>
                <span><el-icon><Star /></el-icon> {{ selectedPhoto.favorites || 0 }}</span>
              </div>
            </div>
            
            <div class="tag-editor">
              <h4>标签</h4>
              <el-input
                v-model="tagInput"
                placeholder="添加标签"
                class="tag-input-area"
                @keyup.enter="addTag"
              >
                <template #suffix>
                  <el-button @click="addTag"><el-icon><Plus /></el-icon></el-button>
                </template>
              </el-input>
              <div class="tags-container">
                <el-tag
                  v-for="tag in selectedPhoto.tags"
                  :key="tag"
                  closable
                  @close="removeTag(tag)"
                  class="tag-item"
                >
                  {{ tag }}
                </el-tag>
              </div>
            </div>
            
            <!-- 智能识别信息 -->
            <div class="smart-recognition">
              <h4>智能识别</h4>
              
              <!-- 场景识别 -->
              <div class="recognition-section" v-if="selectedPhoto.scenes && selectedPhoto.scenes.length > 0">
                <div class="section-label">
                  <el-icon><Camera /></el-icon>
                  <span>场景</span>
                </div>
                <div class="recognition-tags">
                  <el-tag
                    v-for="scene in selectedPhoto.scenes"
                    :key="scene"
                    type="primary"
                    size="small"
                  >
                    {{ scene }}
                  </el-tag>
                </div>
              </div>
              
              <!-- 人物识别 -->
              <div class="recognition-section" v-if="selectedPhoto.people && selectedPhoto.people.length > 0">
                <div class="section-label">
                  <el-icon><User /></el-icon>
                  <span>人物</span>
                </div>
                <div class="recognition-tags">
                  <el-tag
                    v-for="(person, index) in selectedPhoto.people"
                    :key="index"
                    type="success"
                    size="small"
                  >
                    {{ person.name || `人物 ${index + 1}` }}
                    <span v-if="person.confidence" class="confidence">({{ person.confidence }}%)</span>
                  </el-tag>
                </div>
              </div>
              
              <!-- 地点识别 -->
              <div class="recognition-section" v-if="selectedPhoto.location">
                <div class="section-label">
                  <el-icon><MapLocation /></el-icon>
                  <span>地点</span>
                </div>
                <div class="location-info">
                  <span>{{ selectedPhoto.location }}</span>
                  <el-tag v-if="selectedPhoto.location_confidence" size="small" type="info">
                    {{ selectedPhoto.location_confidence }}%
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div class="folder归属">
              <h4>相册归属</h4>
              <el-select v-model="selectedFolder" placeholder="选择相册" style="width: 100%;">
                <el-option label="我的照片" value="my-photos" />
                <el-option label="风景" value="landscapes" />
                <el-option label="人物" value="people" />
                <el-option label="旅行" value="travel" />
                <el-option label="家庭" value="family" />
                <el-option label="宠物" value="pets" />
              </el-select>
            </div>
            
            <div class="basic-info">
              <h4>基本信息</h4>
              <div class="info-item">
                <span class="label">文件类型:</span>
                <span class="value">{{ getFileExtension(selectedPhoto.name).toUpperCase() }}</span>
              </div>
              <div class="info-item">
                <span class="label">文件大小:</span>
                <span class="value">{{ formatFileSize(selectedPhoto.size) }}</span>
              </div>
              <div class="info-item">
                <span class="label">拍摄时间:</span>
                <span class="value">{{ formatFileDate(selectedPhoto.date) }}</span>
              </div>
              <div class="info-item" v-if="selectedPhoto.type === 'image'">
                <span class="label">分辨率:</span>
                <span class="value">{{ selectedPhoto.width || '未知' }} × {{ selectedPhoto.height || '未知' }}</span>
              </div>
              <div class="info-item" v-if="selectedPhoto.type === 'video'">
                <span class="label">时长:</span>
                <span class="value">{{ selectedPhoto.duration || '00:00' }}</span>
              </div>
              <div class="info-item" v-if="selectedPhoto.location">
                <span class="label">拍摄地点:</span>
                <span class="value">{{ selectedPhoto.location }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-selection">
            <el-empty description="请选择一张照片查看详情" />
          </div>
        </div>
      </el-aside>
    </div>
  </div>
</template>

<script>
import CustomTitleBar from './components/CustomTitleBar.vue'
import MaterialToolbar from './components/MaterialToolbar.vue'

import {
  MagicStick,
  Clock,
  Star,
  CopyDocument,
  Collection,
  Delete,
  Close,
  Plus,
  Camera,
  Picture,
  User,
  VideoCamera,
  Food,
  Film,
  Notebook,
  Brush,
  Link
} from '@element-plus/icons-vue'
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import materialManager from './utils/materialManager'
import fileFormatManager from './utils/fileFormatManager'
import searchEngine from './utils/searchEngine'
import libraryQueryStore from './stores/libraryQueryStore'
import smartTagging from './utils/smartTagging'

export default {
  name: 'App',
  components: {
    CustomTitleBar,
    MaterialToolbar,
    MagicStick,
    Clock,
    Star,
    CopyDocument,
    Collection,
    Delete,
    Close,
    Plus,
    Camera,
    Picture,
    User,
    VideoCamera,
    Food,
    Film,
    Notebook,
    Brush,
    Link
  },
  setup() {
    const libraryStats = reactive({
      total: 0,
      folders: 0
    })
    const categoryCounts = reactive({
      images: 0,
      videos: 0,
      audio: 0,
      screenshots: 0
    })
    const trashCount = ref(0)
    const selectedPhotos = ref([])
    const activeView = ref('grid')
    const showDetailPanel = ref(false)
    const selectedPhoto = ref(null)
    const tagInput = ref('')
    const selectedFolder = ref('')

    const initializeData = () => {
      libraryStats.total = 1254
      libraryStats.folders = 23
      
      categoryCounts.images = 856
      categoryCounts.videos = 128
      categoryCounts.audio = 156
      categoryCounts.screenshots = 114
      
      trashCount.value = 12
    }
    
    // 筛选和排序状态
    const currentFilter = ref(null)
    const currentSort = ref('date')
    const currentSearch = ref('')

    const handleViewChange = (view) => {
      activeView.value = view
    }

    const handleSearch = (searchText) => {
      currentSearch.value = searchText
      
      // 使用搜索引擎进行搜索
      const results = searchEngine.search(searchText, {
        type: currentFilter.value?.type,
        tags: currentFilter.value?.tags
      })
      
      // 使用libraryQueryStore存储搜索结果
      libraryQueryStore.setSearchQuery(searchText)
      if (searchText) {
        libraryQueryStore.setSearchResults(results)
      } else {
        libraryQueryStore.clearSearchResults()
      }
      
      // 触发搜索结果更新事件（保持向后兼容）
      window.dispatchEvent(new CustomEvent('search-results-updated', {
        detail: {
          searchText,
          results
        }
      }))
    }

    const handleFilterChange = (filters) => {
      currentFilter.value = filters
      libraryQueryStore.setFilter(filters)
      
      // 如果当前有搜索条件，重新执行搜索
      if (currentSearch.value) {
        handleSearch(currentSearch.value)
      } else {
        // 否则只是更新筛选条件
        window.dispatchEvent(new CustomEvent('filter-changed', { detail: filters }))
      }
    }

    const handleSortChange = (sortOptions) => {
      currentSort.value = sortOptions
      libraryQueryStore.setSortBy(sortOptions)
      // 触发视图更新事件
      window.dispatchEvent(new CustomEvent('sort-changed', { detail: sortOptions }))
    }

    const handleImport = () => {
      // 创建一个隐藏的文件输入元素
      const fileInput = document.createElement('input')
      fileInput.type = 'file'
      fileInput.multiple = true
      
      // 定义支持的文件类型
      const supportedTypes = [
        'image/*',
        'video/*',
        'audio/*',
        '.psd', '.ai', '.sketch', '.xd', '.fig',
        '.ttf', '.otf', '.woff', '.woff2',
        '.pdf', '.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx',
        '.zip', '.rar', '.7z'
      ]
      
      fileInput.accept = supportedTypes.join(',')
      
      fileInput.onchange = async (e) => {
        const files = Array.from(e.target.files)
        
        if (files.length === 0) return
        
        try {
          // 导入文件到materialManager
          for (const file of files) {
            materialManager.addMaterial(file)
          }
          
          ElMessage.success(`成功导入 ${files.length} 张照片`)
        } catch (error) {
          console.error('导入失败:', error)
          ElMessage.error('导入失败，请重试')
        }
      }
      
      // 触发文件选择对话框
      fileInput.click()
    }

    const closeDetailPanel = () => {
      showDetailPanel.value = false
    }

    const addTag = () => {
      if (tagInput.value && selectedPhoto.value && !selectedPhoto.value.tags.includes(tagInput.value)) {
        selectedPhoto.value.tags.push(tagInput.value)
        tagInput.value = ''
      }
    }

    const removeTag = (tag) => {
      if (selectedPhoto.value) {
        const index = selectedPhoto.value.tags.indexOf(tag)
        if (index > -1) {
          selectedPhoto.value.tags.splice(index, 1)
        }
      }
    }

    // 防抖函数（暂时移除，需要时再添加）

    const getFileExtension = (filename) => {
      return fileFormatManager.getFileExtension(filename)
    }

    const formatFileSize = (bytes) => {
      return fileFormatManager.formatFileSize(bytes)
    }

    const formatFileDate = (timestamp) => {
      return fileFormatManager.formatFileDate(timestamp)
    }

    // 智能识别处理函数
    const processSmartRecognition = (photo) => {
      // 使用smartTagging进行场景识别
      const detectedScenes = smartTagging.detectScene(photo.name)
      
      // 模拟人物识别数据
      const detectedPeople = [
        { name: '小明', confidence: 92 },
        { name: '小红', confidence: 88 }
      ]
      
      // 模拟地点识别数据
      const detectedLocation = '北京天安门'
      const locationConfidence = 95
      
      // 将识别结果添加到照片对象中
      return {
        ...photo,
        scenes: detectedScenes,
        people: detectedPeople,
        location: detectedLocation,
        location_confidence: locationConfidence
      }
    }

    onMounted(() => {
      initializeData()
      
      window.addEventListener('preview-photo', (event) => {
        // 处理智能识别
        const photoWithSmartInfo = processSmartRecognition(event.detail)
        selectedPhoto.value = photoWithSmartInfo
        showDetailPanel.value = true
      })
    })

    return {
      libraryStats,
      categoryCounts,
      trashCount,
      selectedPhotos,
      activeView,
      showDetailPanel,
      selectedPhoto,
      tagInput,
      selectedFolder,
      handleViewChange,
      handleSearch,
      handleFilterChange,
      handleSortChange,
      handleImport,
      closeDetailPanel,
      addTag,
      removeTag,
      getFileExtension,
      formatFileSize,
      formatFileDate
    }
  }
}
</script>

<style>
@import './assets/styles/global.css';

html, body, #app {
  margin: 0;
  padding: 0;
  height: 100vh;
  overflow: hidden;
  font-family: var(--font-family-base);
  background-color: var(--bg-primary);
  color: var(--text-primary);
}

#app {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

/* 主布局 - 优化版 */
.main-layout {
  flex: 1;
  display: flex;
  background-color: var(--bg-primary);
  overflow: hidden;
  height: 100vh;
  position: relative;
}

/* 右侧区域 - 固定布局 */
.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  margin-left: 280px; /* 固定侧边栏宽度 */
}

/* 侧边栏 - 固定定位 */
.side-navigation {
  position: fixed;
  left: 0;
  top: 0;
  height: 100vh;
  width: 280px;
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  padding: 0;
  overflow-y: auto;
  z-index: 100;
}

/* 折叠功能已移除 - 保持固定宽度 */

/* 响应式布局支持 */
@media (max-width: 1200px) {
  .side-navigation {
    width: 240px;
  }
  
  .right-section {
    margin-left: 240px;
  }
}

@media (max-width: 768px) {
  .side-navigation {
    width: 200px;
  }
  
  .right-section {
    margin-left: 200px;
  }
  
  /* 移动端折叠功能已移除 */
}

@media (max-width: 480px) {
  .side-navigation {
    position: absolute;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform var(--transition-slow);
  }
  
  .right-section {
    margin-left: 0;
  }
}

/* 内容区域容器 */
.content-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 左侧导航栏 */
.side-navigation {
  background-color: var(--bg-secondary);
  border-right: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  padding: 0;
  height: 100%;
  overflow-y: auto;
  transition: width var(--transition-normal);
}

/* 侧边栏顶部操作区域 */
.sidebar-header {
  padding: var(--space-md);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-card);
}

.sidebar-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-md);
}

.action-buttons {
  display: flex;
  gap: var(--space-xs);
}

.action-buttons .btn {
  width: 32px;
  height: 32px;
  border-radius: var(--radius-base);
  color: var(--text-secondary);
  transition: all var(--transition-fast);
}

.action-buttons .btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

/* 库信息区域 */
.library-info {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-sm);
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
}

.library-avatar {
  flex-shrink: 0;
}

.library-avatar img {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  object-fit: cover;
}

.avatar-placeholder {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-lg);
  background: var(--bg-hover);
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  font-size: 20px;
}

.library-details {
  flex: 1;
}

.library-name {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--space-xs);
}

.library-stats {
  display: flex;
  gap: var(--space-lg);
}

.stat-item {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

/* 导航菜单 */
.menu-container {
  border-right: none;
  background-color: transparent;
  flex: 1;
  padding: var(--space-md);
}

.el-menu-item, .el-sub-menu__title {
  color: var(--text-secondary);
  height: 44px;
  line-height: 44px;
  font-size: var(--font-size-base);
  border-radius: var(--radius-base);
  margin-bottom: var(--space-xs);
}

.el-menu-item:hover, .el-sub-menu__title:hover {
  background-color: var(--bg-hover);
  color: var(--text-primary);
}

.el-menu-item.is-active {
  background-color: var(--bg-active);
  color: var(--primary-color);
  font-weight: 500;
}

.el-menu-item .el-tag {
  margin-left: auto;
}

/* 快速操作 */
.quick-actions {
  padding-top: var(--space-lg);
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.quick-action-item {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  padding: var(--space-md);
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.quick-action-item:hover {
  background: var(--bg-hover);
  border-color: var(--primary-color);
  transform: translateX(4px);
}

.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: var(--bg-secondary);
  border-radius: var(--radius-base);
  color: var(--primary-color);
  font-size: 18px;
  flex-shrink: 0;
}

.action-content {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.action-title {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.2;
}

.action-desc {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  line-height: 1.2;
}

/* 工具栏头部 */
.toolbar-header {
  padding: 0;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-light);
}

/* 内容区域 */
.content-area {
  padding: 0;
  background-color: var(--bg-primary);
  overflow-y: auto;
  flex: 1;
}

/* 右侧详情面板 */
.detail-panel {
  background-color: var(--bg-secondary);
  border-left: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-light);
  background: var(--bg-card);
}

.detail-header span {
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--text-primary);
}

.close-btn {
  color: var(--text-tertiary);
}

.close-btn:hover {
  color: var(--text-primary);
}

.detail-content {
  flex: 1;
  padding: var(--space-lg);
  overflow-y: auto;
}

/* 素材预览 */
.material-preview {
  width: 100%;
  height: 200px;
  background-color: var(--bg-card);
  border-radius: var(--radius-base);
  overflow: hidden;
  margin-bottom: var(--space-lg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.material-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .side-navigation {
    width: 220px !important;
  }
  
  .detail-panel {
    width: 280px !important;
  }
}

@media (max-width: 768px) {
  .side-navigation {
    width: 200px !important;
    padding: var(--space-sm);
  }
  
  .detail-panel {
    position: fixed;
    right: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    box-shadow: var(--shadow-lg);
  }
}

@media (max-width: 480px) {
  .side-navigation {
    width: 100% !important;
    position: fixed;
    z-index: 1000;
    transform: translateX(-100%);
    transition: transform var(--transition-slow);
  }
  
  .detail-panel {
    width: 100vw !important;
  }
}

/* 音频波形 */
.audio-wave {
  width: 120px;
  height: 60px;
  background-size: 100% 100%;
  background-repeat: no-repeat;
}

.audio-wave.blue {
  background-image: url('data:image/svg+xml;utf8,<svg width="120" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M0,30 L5,10 L10,25 L15,5 L20,35 L25,15 L30,40 L35,20 L40,45 L45,25 L50,50 L55,30 L60,45 L65,25 L70,40 L75,20 L80,35 L85,15 L90,30 L95,10 L100,25 L105,5 L110,20 L115,35 L120,30 Z" fill="%23409EFF" opacity="0.8"/></svg>');
}

.audio-wave.orange {
  background-image: url('data:image/svg+xml;utf8,<svg width="120" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M0,30 L5,10 L10,25 L15,5 L20,35 L25,15 L30,40 L35,20 L40,45 L45,25 L50,50 L55,30 L60,45 L65,25 L70,40 L75,20 L80,35 L85,15 L90,30 L95,10 L100,25 L105,5 L110,20 L115,35 L120,30 Z" fill="%23E6A23C" opacity="0.8"/></svg>');
}

.audio-wave.gray {
  background-image: url('data:image/svg+xml;utf8,<svg width="120" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M0,30 L5,10 L10,25 L15,5 L20,35 L25,15 L30,40 L35,20 L40,45 L45,25 L50,50 L55,30 L60,45 L65,25 L70,40 L75,20 L80,35 L85,15 L90,30 L95,10 L100,25 L105,5 L110,20 L115,35 L120,30 Z" fill="%23666666" opacity="0.8"/></svg>');
}

.audio-wave.red {
  background-image: url('data:image/svg+xml;utf8,<svg width="120" height="60" xmlns="http://www.w3.org/2000/svg"><path d="M0,30 L5,10 L10,25 L15,5 L20,35 L25,15 L30,40 L35,20 L40,45 L45,25 L50,50 L55,30 L60,45 L65,25 L70,40 L75,20 L80,35 L85,15 L90,30 L95,10 L100,25 L105,5 L110,20 L115,35 L120,30 Z" fill="%23F56C6C" opacity="0.8"/></svg>');
}

.view-stats {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.view-stats .el-icon {
  font-size: 14px;
  color: #999999;
  margin-right: 4px;
}

.view-stats span {
  font-size: 12px;
  color: #cccccc;
  margin-right: 16px;
}

/* 标签编辑 */
.tag-editor, .folder归属, .basic-info, .smart-recognition {
  margin-bottom: 20px;
}

.tag-editor h4, .folder归属 h4, .basic-info h4, .smart-recognition h4 {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 10px 0;
}

/* 智能识别 */
.smart-recognition {
  padding: 15px;
  background-color: #2a2a2a;
  border-radius: 4px;
}

.recognition-section {
  margin-bottom: 15px;
  padding: 10px;
  background-color: #333333;
  border-radius: 4px;
}

.recognition-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  color: #cccccc;
  font-size: 12px;
}

.section-label .el-icon {
  margin-right: 5px;
  font-size: 14px;
}

.recognition-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #ffffff;
  font-size: 13px;
}

.confidence {
  font-size: 11px;
  opacity: 0.8;
}

.tag-input-area {
  height: 36px;
  background-color: #2a2a2a;
  border-radius: 4px;
  border: 1px solid #3d3d3d;
}

/* 智能识别 */
.smart-recognition {
  margin-bottom: 20px;
}

.smart-recognition h4 {
  font-size: 14px;
  font-weight: 500;
  color: #ffffff;
  margin: 0 0 10px 0;
}

.recognition-section {
  margin-bottom: 12px;
  padding: 10px;
  background-color: #2a2a2a;
  border-radius: 4px;
}

.recognition-section:last-child {
  margin-bottom: 0;
}

.section-label {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  color: #999999;
}

.recognition-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.location-info {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.location-info span {
  font-size: 13px;
  color: #ffffff;
}

.confidence {
  font-size: 11px;
  opacity: 0.8;
}

/* 进度条 */
.progress-bar {
  padding: 10px 0;
}

.el-progress__text {
  color: #999999;
  font-size: 12px;
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #2a2a2a;
}

::-webkit-scrollbar-thumb {
  background: #4a4a4a;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #5a5a5a;
}
</style>
