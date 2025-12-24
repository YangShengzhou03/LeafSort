<template>
  <div class="material-toolbar glass-dark">
    <div class="toolbar-left">
      <div class="view-controls btn-row">
        <button 
          :class="['btn', activeView === 'grid' ? 'btn-primary' : 'btn-secondary']" 
          @click="changeView('grid')"
        >
          <el-icon class="icon-sm"><Grid /></el-icon>
          <span class="button-text">网格</span>
        </button>
        <button 
          :class="['btn', activeView === 'list' ? 'btn-primary' : 'btn-secondary']" 
          @click="changeView('list')"
        >
          <el-icon class="icon-sm"><List /></el-icon>
          <span class="button-text">列表</span>
        </button>
      </div>

      <div class="search-container">
        <div class="input-wrapper">
          <el-icon class="prefix-icon"><Search /></el-icon>
          <input
            v-model="searchText"
            type="text"
            placeholder="搜索素材名称、标签、格式..."
            class="input"
            @input="handleSearch"
          />
          <el-icon class="clear-icon" v-if="searchText" @click="handleSearchClear"><Close /></el-icon>
        </div>
      </div>
    </div>

    <div class="toolbar-center btn-row">
      <el-dropdown trigger="click" @command="handleFilter">
        <button class="btn btn-secondary">
          <el-icon><Filter /></el-icon>
          筛选
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="image">
              <el-icon><Picture /></el-icon>
              图片
            </el-dropdown-item>
            <el-dropdown-item command="video">
              <el-icon><VideoPlay /></el-icon>
              视频
            </el-dropdown-item>
            <el-dropdown-item command="audio">
              <el-icon><Headset /></el-icon>
              音频
            </el-dropdown-item>
            <el-dropdown-item command="design">
              <el-icon><Brush /></el-icon>
              设计文件
            </el-dropdown-item>
            <el-dropdown-item command="document">
              <el-icon><Document /></el-icon>
              文档
            </el-dropdown-item>
            <el-dropdown-item divided command="clear">
              <el-icon><RefreshRight /></el-icon>
              清除筛选
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <el-dropdown trigger="click" @command="handleSort">
        <button class="btn btn-secondary">
          <el-icon><Top /></el-icon>
          排序
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="name">
              <el-icon><Sort /></el-icon>
              按名称
            </el-dropdown-item>
            <el-dropdown-item command="date">
              <el-icon><Clock /></el-icon>
              按日期
            </el-dropdown-item>
            <el-dropdown-item command="size">
              <el-icon><ScaleToOriginal /></el-icon>
              按大小
            </el-dropdown-item>
            <el-dropdown-item command="rating">
              <el-icon><Star /></el-icon>
              按评分
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <div class="toolbar-right btn-row">
      <div v-if="selectedCount > 0" class="batch-info glass-card">
        <span class="selected-count">已选 {{ selectedCount }} 项</span>
        <div class="btn-group">
          <button class="btn btn-sm" @click="handleBatchTag">
            <el-icon><PriceTag /></el-icon>
            标签
          </button>
          <button class="btn btn-sm" @click="handleBatchMove">
            <el-icon><FolderOpened /></el-icon>
            移动
          </button>
          <button class="btn btn-sm btn-danger" @click="handleBatchDelete">
            <el-icon><Delete /></el-icon>
            删除
          </button>
        </div>
      </div>
      <div class="btn-group">
        <button class="btn btn-primary" @click="handleImport">
          <el-icon><Upload /></el-icon>
          导入
        </button>
        
        <el-dropdown trigger="click" @command="handleMoreActions">
          <button class="btn btn-secondary btn-icon">
            <el-icon><More /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="refresh">
                <el-icon><Refresh /></el-icon>
                刷新
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item divided command="export">
                <el-icon><Download /></el-icon>
                导出数据
              </el-dropdown-item>
              <el-dropdown-item command="help">
                <el-icon><QuestionFilled /></el-icon>
                帮助
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
      <el-dropdown trigger="click">
        <button class="btn btn-secondary">
          <el-icon><Operation /></el-icon>
          显示
        </button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item @click="handleThumbnailSizeChange('small')">
              <el-icon v-if="thumbnailSize === 'small'"><Check /></el-icon>
              小缩略图
            </el-dropdown-item>
            <el-dropdown-item @click="handleThumbnailSizeChange('medium')">
              <el-icon v-if="thumbnailSize === 'medium'"><Check /></el-icon>
              中缩略图
            </el-dropdown-item>
            <el-dropdown-item @click="handleThumbnailSizeChange('large')">
              <el-icon v-if="thumbnailSize === 'large'"><Check /></el-icon>
              大缩略图
            </el-dropdown-item>
            <el-dropdown-item divided @click="handleShowFileInfoToggle">
              <el-icon v-if="showFileInfo"><Check /></el-icon>
              显示文件信息
            </el-dropdown-item>
            <el-dropdown-item @click="handleShowTagsToggle">
              <el-icon v-if="showTags"><Check /></el-icon>
              显示标签
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { 
  Grid, List, Search, Upload, More, 
  Refresh, Setting, Download, QuestionFilled, Operation, 
  Check, PriceTag, FolderOpened, Delete, Close, 
  Filter, Picture, VideoPlay, Headset, Brush, 
  Document, RefreshRight, Top, Sort, Clock, ScaleToOriginal, Star 
} from '@element-plus/icons-vue'

export default {
  name: 'MaterialToolbar',
  components: {
    Grid, List, Search, Upload, More,
    Refresh, Setting, Download, QuestionFilled, Operation,
    Check, PriceTag, FolderOpened, Delete, Close,
    Filter, Picture, VideoPlay, Headset, Brush,
    Document, RefreshRight, Top, Sort, Clock, ScaleToOriginal, Star
  },
  props: {
    selectedCount: {
      type: Number,
      default: 0
    },
    activeView: {
      type: String,
      default: 'grid'
    }
  },
  emits: [
    'view-change', 'search', 'filter-change', 'sort-change',
    'import', 'batch-tag', 'batch-move', 'batch-delete',
    'refresh', 'settings', 'export', 'help',
    'thumbnail-size-change', 'show-file-info-change', 'show-tags-change'
  ],
  setup(props, { emit }) {
    const searchText = ref('')
    const thumbnailSize = ref('medium')
    const showFileInfo = ref(true)
    const showTags = ref(true)



    const changeView = (view) => emit('view-change', view)
    const handleSearch = () => emit('search', searchText.value)
    const handleSearchClear = () => {
      searchText.value = ''
      emit('search', '')
    }
    const handleImport = () => emit('import')
    const handleBatchTag = () => emit('batch-tag')
    const handleBatchMove = () => emit('batch-move')
    const handleBatchDelete = () => emit('batch-delete')

    const handleMoreActions = (command) => emit(command)

    const handleFilter = (filterType) => {
      if (filterType === 'clear') {
        emit('filter-change', null)
      } else {
        emit('filter-change', { type: filterType })
      }
    }

    const handleSort = (sortBy) => {
      emit('sort-change', { sortBy })
    }

    const handleThumbnailSizeChange = (size) => {
      thumbnailSize.value = size
      emit('thumbnail-size-change', size)
    }

    const handleShowFileInfoToggle = () => {
      showFileInfo.value = !showFileInfo.value
      emit('show-file-info-change', showFileInfo.value)
    }

    const handleShowTagsToggle = () => {
      showTags.value = !showTags.value
      emit('show-tags-change', showTags.value)
    }

    return {
      searchText,
      thumbnailSize,
      showFileInfo,
      showTags,
      changeView,
      handleSearch,
      handleSearchClear,
      handleImport,
      handleBatchTag,
      handleBatchMove,
      handleBatchDelete,
      handleMoreActions,
      handleFilter,
      handleSort,
      handleThumbnailSizeChange,
      handleShowFileInfoToggle,
      handleShowTagsToggle
    }
  }
}
</script>

<style scoped>
.material-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-6);
  gap: var(--space-6);
  flex-wrap: wrap;
  min-height: 64px;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex: 1;
  min-width: 320px;
}

.search-container {
  flex: 1;
  max-width: 420px;
  min-width: 280px;
}

.input-wrapper {
  width: 100%;
}

.input-wrapper .prefix-icon {
  margin-left: var(--space-3);
}

.input-wrapper .clear-icon {
  margin-right: var(--space-3);
  cursor: pointer;
  color: var(--text-tertiary);
  transition: color var(--transition-fast);
}

.input-wrapper .clear-icon:hover {
  color: var(--text-primary);
}

.toolbar-center {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.select-wrapper {
  min-width: 120px;
  width: 140px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-4);
  border-radius: var(--radius-lg);
}

.selected-count {
  font-size: var(--font-size-sm);
  color: var(--primary-400);
  font-weight: var(--weight-semibold);
  white-space: nowrap;
}

.btn-danger {
  background: linear-gradient(
    180deg,
    var(--error) 0%,
    #d9363e 100%
  );
  border-color: transparent;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: linear-gradient(
    180deg,
    #ff6163 0%,
    var(--error) 100%
  );
}

@media (max-width: 1280px) {
  .material-toolbar {
    gap: var(--space-4);
    padding: var(--space-3) var(--space-4);
  }
  
  .toolbar-left {
    min-width: 280px;
  }
  
  .search-container {
    max-width: 350px;
    min-width: 250px;
  }
  
  .select-wrapper {
    width: 130px;
  }
}

@media (max-width: 1024px) {
  .material-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: var(--space-4);
    padding: var(--space-4);
  }
  
  .toolbar-left {
    min-width: auto;
    order: 1;
    justify-content: space-between;
  }
  
  .toolbar-center {
    order: 2;
    justify-content: center;
  }
  
  .toolbar-right {
    order: 3;
    justify-content: center;
  }
  
  .search-container {
    max-width: none;
    min-width: 200px;
    flex: 1;
  }
  
  .batch-info {
    flex-direction: row;
    justify-content: space-between;
    gap: var(--space-3);
  }
}

@media (max-width: 768px) {
  .material-toolbar {
    padding: var(--space-3);
    gap: var(--space-3);
  }
  
  .toolbar-left {
    flex-direction: column;
    gap: var(--space-3);
    align-items: stretch;
  }
  
  .toolbar-center {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    gap: var(--space-2);
  }
  
  .select-wrapper {
    width: 120px;
    min-width: 120px;
  }
  
  .toolbar-right {
    flex-direction: column;
    gap: var(--space-3);
  }
  
  .batch-info {
    flex-direction: column;
    text-align: center;
    gap: var(--space-2);
  }
}

@media (max-width: 480px) {
  .material-toolbar {
    padding: var(--space-2);
    gap: var(--space-2);
  }
  
  .toolbar-center {
    flex-direction: column;
    width: 100%;
  }
  
  .select-wrapper {
    width: 100%;
    min-width: auto;
  }
}
</style>