<template>
  <div class="search-panel">
    <!-- 搜索工具栏 -->
    <div class="search-toolbar">
      <div class="search-input-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索素材..."
          clearable
          @input="handleSearch"
          @clear="handleClear"
          class="search-input"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-button
          type="primary"
          @click="showAdvancedSearch = true"
          class="advanced-search-btn"
        >
          <el-icon><Filter /></el-icon>
          高级搜索
        </el-button>
      </div>
      
      <div class="search-actions">
        <el-button-group>
          <el-button
            :type="searchMode === 'all' ? 'primary' : ''"
            @click="setSearchMode('all')"
          >
            全部
          </el-button>
          <el-button
            :type="searchMode === 'images' ? 'primary' : ''"
            @click="setSearchMode('images')"
          >
            图片
          </el-button>
          <el-button
            :type="searchMode === 'videos' ? 'primary' : ''"
            @click="setSearchMode('videos')"
          >
            视频
          </el-button>
          <el-button
            :type="searchMode === 'documents' ? 'primary' : ''"
            @click="setSearchMode('documents')"
          >
            文档
          </el-button>
        </el-button-group>
        
        <el-dropdown @command="handleSortCommand" class="sort-dropdown">
          <el-button>
            {{ sortOptions.find(opt => opt.value === sortBy)?.label || '排序' }}
            <el-icon class="el-icon--right">
              <arrow-down />
            </el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item
                v-for="option in sortOptions"
                :key="option.value"
                :command="option.value"
                :class="{ active: sortBy === option.value }"
              >
                {{ option.label }}
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 搜索条件标签 -->
    <div v-if="activeFilters.length > 0" class="filter-tags">
      <div class="filter-tags-header">
        <span>搜索条件：</span>
        <el-button type="text" @click="clearAllFilters" size="small">
          清除全部
        </el-button>
      </div>
      <div class="tags-container">
        <el-tag
          v-for="filter in activeFilters"
          :key="filter.id"
          closable
          @close="removeFilter(filter.id)"
          type="info"
          size="small"
        >
          {{ getFilterLabel(filter) }}
        </el-tag>
      </div>
    </div>

    <!-- 搜索结果 -->
    <div class="search-results">
      <div v-if="searching" class="search-loading">
        <el-skeleton :rows="6" animated />
      </div>
      
      <div v-else-if="searchResults.length === 0 && (searchQuery || activeFilters.length > 0)" class="no-results">
        <el-empty description="未找到匹配的素材">
          <template #image>
            <el-icon size="48">
              <Search />
            </el-icon>
          </template>
          <p>尝试调整搜索条件或关键词</p>
        </el-empty>
      </div>
      
      <div v-else-if="searchResults.length > 0" class="results-grid">
        <div class="results-header">
          <span>找到 {{ searchResults.length }} 个结果</span>
          <el-button type="text" @click="exportSearchResults" size="small">
            导出结果
          </el-button>
        </div>
        
        <div class="assets-grid">
          <div
            v-for="asset in paginatedResults"
            :key="asset.id"
            class="asset-card"
            @click="previewAsset(asset)"
            @contextmenu="showAssetContextMenu($event, asset)"
          >
            <div class="asset-thumb">
              <img :src="asset.thumbnail" :alt="asset.name" />
              <div class="asset-overlay">
                <div class="asset-actions">
                  <el-button size="small" circle @click.stop="quickPreview(asset)">
                    <el-icon><ZoomIn /></el-icon>
                  </el-button>
                  <el-button size="small" circle @click.stop="addToCollection(asset)">
                    <el-icon><Star /></el-icon>
                  </el-button>
                </div>
              </div>
              <div v-if="asset.type" class="asset-type-badge">
                {{ getAssetTypeLabel(asset.type) }}
              </div>
            </div>
            <div class="asset-info">
              <div class="asset-name" :title="asset.name">
                {{ asset.name }}
              </div>
              <div class="asset-meta">
                <span>{{ formatFileSize(asset.size) }}</span>
                <span>{{ formatDate(asset.createdAt) }}</span>
              </div>
              <div v-if="asset.tags && asset.tags.length > 0" class="asset-tags">
                <el-tag
                  v-for="tag in asset.tags.slice(0, 2)"
                  :key="tag"
                  size="small"
                  type="info"
                >
                  {{ tag }}
                </el-tag>
                <span v-if="asset.tags.length > 2" class="more-tags">
                  +{{ asset.tags.length - 2 }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-container">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pageSize"
            :total="searchResults.length"
            layout="prev, pager, next, jumper"
            @current-change="handlePageChange"
          />
        </div>
      </div>
      
      <div v-else class="search-placeholder">
        <div class="placeholder-content">
          <el-icon size="64" color="var(--el-text-color-placeholder)">
            <Search />
          </el-icon>
          <h3>开始搜索您的素材</h3>
          <p>输入关键词或使用高级搜索来查找特定素材</p>
          <div class="search-tips">
            <h4>搜索提示：</h4>
            <ul>
              <li>使用文件名、标签、描述进行搜索</li>
              <li>支持通配符 * 和 ?</li>
              <li>使用引号进行精确匹配</li>
              <li>组合多个条件进行高级搜索</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 高级搜索对话框 -->
    <el-dialog
      v-model="showAdvancedSearch"
      title="高级搜索"
      width="800px"
      class="advanced-search-dialog"
    >
      <div class="advanced-search-content">
        <div class="search-criteria">
          <div class="criteria-header">
            <h4>搜索条件</h4>
            <el-button type="primary" text @click="addFilter">
              <el-icon><Plus /></el-icon>
              添加条件
            </el-button>
          </div>
          
          <div class="criteria-list">
            <div
              v-for="(filter, index) in advancedFilters"
              :key="filter.id"
              class="criteria-item"
            >
              <div class="criteria-controls">
                <el-select
                  v-model="filter.field"
                  placeholder="选择字段"
                  style="width: 120px"
                  @change="handleFilterFieldChange(filter)"
                >
                  <el-option
                    v-for="field in filterFields"
                    :key="field.value"
                    :label="field.label"
                    :value="field.value"
                  />
                </el-select>
                
                <el-select
                  v-model="filter.operator"
                  placeholder="选择操作符"
                  style="width: 120px"
                >
                  <el-option
                    v-for="op in getOperatorsForField(filter.field)"
                    :key="op.value"
                    :label="op.label"
                    :value="op.value"
                  />
                </el-select>
                
                <el-input
                  v-model="filter.value"
                  :placeholder="getValuePlaceholder(filter.field)"
                  style="flex: 1"
                />
                
                <el-button
                  type="danger"
                  text
                  @click="removeAdvancedFilter(index)"
                  class="remove-criteria-btn"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
              
              <div v-if="index < advancedFilters.length - 1" class="criteria-logic">
                <el-radio-group v-model="filter.logic" size="small">
                  <el-radio label="and">且</el-radio>
                  <el-radio label="or">或</el-radio>
                </el-radio-group>
              </div>
            </div>
          </div>
        </div>
        
        <div class="search-options">
          <el-form label-width="100px">
            <el-form-item label="搜索范围：">
              <el-checkbox-group v-model="searchScopes">
                <el-checkbox label="name">文件名</el-checkbox>
                <el-checkbox label="tags">标签</el-checkbox>
                <el-checkbox label="description">描述</el-checkbox>
                <el-checkbox label="content">内容（OCR）</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="文件类型：">
              <el-checkbox-group v-model="fileTypes">
                <el-checkbox label="image">图片</el-checkbox>
                <el-checkbox label="video">视频</el-checkbox>
                <el-checkbox label="audio">音频</el-checkbox>
                <el-checkbox label="document">文档</el-checkbox>
                <el-checkbox label="other">其他</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="时间范围：">
              <el-date-picker
                v-model="dateRange"
                type="daterange"
                range-separator="至"
                start-placeholder="开始日期"
                end-placeholder="结束日期"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
            
            <el-form-item label="文件大小：">
              <div class="size-range">
                <el-input-number
                  v-model="sizeRange[0]"
                  :min="0"
                  :max="sizeRange[1]"
                  placeholder="最小"
                  style="width: 100px"
                />
                <span class="range-separator">-</span>
                <el-input-number
                  v-model="sizeRange[1]"
                  :min="sizeRange[0]"
                  :max="1000"
                  placeholder="最大"
                  style="width: 100px"
                />
                <span class="size-unit">MB</span>
              </div>
            </el-form-item>
          </el-form>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showAdvancedSearch = false">取消</el-button>
        <el-button type="primary" @click="applyAdvancedSearch">搜索</el-button>
      </template>
    </el-dialog>

    <!-- 右键菜单 -->
    <el-dropdown-menu
      v-model:visible="contextMenuVisible"
      :position="contextMenuPosition"
      class="asset-context-menu"
    >
      <el-dropdown-item @click="previewSelectedAsset">
        <el-icon><View /></el-icon>
        预览
      </el-dropdown-item>
      <el-dropdown-item @click="openAssetLocation">
        <el-icon><FolderOpened /></el-icon>
        打开文件位置
      </el-dropdown-item>
      <el-dropdown-item @click="copyAssetPath">
        <el-icon><DocumentCopy /></el-icon>
        复制路径
      </el-dropdown-item>
      <el-dropdown-item divided @click="addToCollectionFromContext">
        <el-icon><Star /></el-icon>
        添加到收藏
      </el-dropdown-item>
      <el-dropdown-item @click="editAssetTags">
        <el-icon><PriceTag /></el-icon>
        编辑标签
      </el-dropdown-item>
      <el-dropdown-item divided @click="downloadAsset">
        <el-icon><Download /></el-icon>
        下载
      </el-dropdown-item>
      <el-dropdown-item @click="shareAsset" class="danger">
        <el-icon><Share /></el-icon>
        分享
      </el-dropdown-item>
    </el-dropdown-menu>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useLibraryStore } from '@/stores/library'
import {
  Search,
  Filter,
  ArrowDown,
  ZoomIn,
  Star,
  Plus,
  Close,
  View,
  FolderOpened,
  DocumentCopy,
  PriceTag,
  Download,
  Share
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const libraryStore = useLibraryStore()

// 搜索状态
const searchQuery = ref('')
const searchMode = ref('all') // all, images, videos, documents
const sortBy = ref('date-desc') // date-desc, date-asc, name-asc, name-desc, size-desc, size-asc
const currentPage = ref(1)
const pageSize = ref(24)
const searching = ref(false)

// 高级搜索
const showAdvancedSearch = ref(false)
const advancedFilters = ref<any[]>([])
const searchScopes = ref(['name', 'tags', 'description'])
const fileTypes = ref<string[]>([])
const dateRange = ref<string[]>([])
const sizeRange = ref([0, 1000])

// 搜索结果
const searchResults = ref<any[]>([])
const activeFilters = ref<any[]>([])

// 右键菜单
const contextMenuVisible = ref(false)
const contextMenuPosition = ref({ x: 0, y: 0 })
const selectedAsset = ref<any>(null)

// 排序选项
const sortOptions = [
  { label: '最新优先', value: 'date-desc' },
  { label: '最旧优先', value: 'date-asc' },
  { label: '名称 A-Z', value: 'name-asc' },
  { label: '名称 Z-A', value: 'name-desc' },
  { label: '文件大小降序', value: 'size-desc' },
  { label: '文件大小升序', value: 'size-asc' }
]

// 搜索字段选项
const filterFields = [
  { label: '文件名', value: 'name' },
  { label: '标签', value: 'tags' },
  { label: '描述', value: 'description' },
  { label: '文件类型', value: 'type' },
  { label: '文件大小', value: 'size' },
  { label: '创建时间', value: 'createdAt' },
  { label: '修改时间', value: 'updatedAt' },
  { label: '文件夹', value: 'folder' }
]

// 操作符映射
const operatorMap = {
  name: [
    { label: '包含', value: 'contains' },
    { label: '不包含', value: 'notContains' },
    { label: '等于', value: 'equals' },
    { label: '开头为', value: 'startsWith' },
    { label: '结尾为', value: 'endsWith' }
  ],
  tags: [
    { label: '包含', value: 'contains' },
    { label: '不包含', value: 'notContains' },
    { label: '等于', value: 'equals' }
  ],
  description: [
    { label: '包含', value: 'contains' },
    { label: '不包含', value: 'notContains' }
  ],
  type: [
    { label: '等于', value: 'equals' },
    { label: '不等于', value: 'notEquals' }
  ],
  size: [
    { label: '大于', value: 'greaterThan' },
    { label: '小于', value: 'lessThan' },
    { label: '等于', value: 'equals' },
    { label: '介于', value: 'between' }
  ],
  createdAt: [
    { label: '早于', value: 'before' },
    { label: '晚于', value: 'after' },
    { label: '介于', value: 'between' }
  ],
  updatedAt: [
    { label: '早于', value: 'before' },
    { label: '晚于', value: 'after' },
    { label: '介于', value: 'between' }
  ],
  folder: [
    { label: '等于', value: 'equals' },
    { label: '不等于', value: 'notEquals' }
  ]
}

// 计算属性
const paginatedResults = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return searchResults.value.slice(start, end)
})

// 方法
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  
  searching.value = true
  
  // 模拟搜索延迟
  setTimeout(() => {
    performSearch()
    searching.value = false
  }, 300)
}

const handleClear = () => {
  searchResults.value = []
  activeFilters.value = []
  currentPage.value = 1
}

const setSearchMode = (mode: string) => {
  searchMode.value = mode
  handleSearch()
}

const handleSortCommand = (command: string) => {
  sortBy.value = command
  sortSearchResults()
}

const performSearch = () => {
  const query = searchQuery.value.toLowerCase().trim()
  
  if (!query && activeFilters.value.length === 0) {
    searchResults.value = []
    return
  }
  
  // 获取所有素材
  let results = [...libraryStore.assets]
  
  // 应用搜索模式过滤
  if (searchMode.value !== 'all') {
    results = results.filter(asset => {
      const assetType = getAssetMainType(asset.type)
      return assetType === searchMode.value
    })
  }
  
  // 应用关键词搜索
  if (query) {
    results = results.filter(asset => {
      return (
        asset.name.toLowerCase().includes(query) ||
        (asset.tags && asset.tags.some((tag: string) => tag.toLowerCase().includes(query))) ||
        (asset.description && asset.description.toLowerCase().includes(query))
      )
    })
  }
  
  // 应用高级过滤器
  if (activeFilters.value.length > 0) {
    results = results.filter(asset => {
      return evaluateFilters(asset, activeFilters.value)
    })
  }
  
  searchResults.value = results
  sortSearchResults()
  currentPage.value = 1
}

const sortSearchResults = () => {
  const [field, order] = sortBy.value.split('-')
  
  searchResults.value.sort((a, b) => {
    let aValue, bValue
    
    switch (field) {
      case 'date':
        aValue = new Date(a.createdAt).getTime()
        bValue = new Date(b.createdAt).getTime()
        break
      case 'name':
        aValue = a.name.toLowerCase()
        bValue = b.name.toLowerCase()
        break
      case 'size':
        aValue = a.size || 0
        bValue = b.size || 0
        break
      default:
        return 0
    }
    
    if (order === 'desc') {
      return bValue - aValue
    } else {
      return aValue - bValue
    }
  })
}

const evaluateFilters = (asset: any, filters: any[]) => {
  for (let i = 0; i < filters.length; i++) {
    const filter = filters[i]
    const matches = evaluateSingleFilter(asset, filter)
    
    if (i === 0) continue // 第一个条件没有逻辑操作符
    
    const prevFilter = filters[i - 1]
    if (prevFilter.logic === 'and' && !matches) {
      return false
    }
    if (prevFilter.logic === 'or' && matches) {
      return true
    }
  }
  
  return evaluateSingleFilter(asset, filters[0])
}

const evaluateSingleFilter = (asset: any, filter: any) => {
  const assetValue = asset[filter.field]
  
  switch (filter.operator) {
    case 'contains':
      return assetValue?.toString().toLowerCase().includes(filter.value.toLowerCase())
    case 'notContains':
      return !assetValue?.toString().toLowerCase().includes(filter.value.toLowerCase())
    case 'equals':
      return assetValue?.toString().toLowerCase() === filter.value.toLowerCase()
    case 'notEquals':
      return assetValue?.toString().toLowerCase() !== filter.value.toLowerCase()
    case 'startsWith':
      return assetValue?.toString().toLowerCase().startsWith(filter.value.toLowerCase())
    case 'endsWith':
      return assetValue?.toString().toLowerCase().endsWith(filter.value.toLowerCase())
    case 'greaterThan':
      return parseFloat(assetValue) > parseFloat(filter.value)
    case 'lessThan':
      return parseFloat(assetValue) < parseFloat(filter.value)
    case 'before':
      return new Date(assetValue) < new Date(filter.value)
    case 'after':
      return new Date(assetValue) > new Date(filter.value)
    case 'between':
      const [min, max] = filter.value.split(',').map((v: string) => v.trim())
      const value = field === 'size' ? parseFloat(assetValue) : new Date(assetValue).getTime()
      return value >= parseFloat(min) && value <= parseFloat(max)
    default:
      return false
  }
}

// 高级搜索相关方法
const addFilter = () => {
  advancedFilters.value.push({
    id: Date.now(),
    field: 'name',
    operator: 'contains',
    value: '',
    logic: 'and'
  })
}

const removeAdvancedFilter = (index: number) => {
  advancedFilters.value.splice(index, 1)
}

const handleFilterFieldChange = (filter: any) => {
  // 重置操作符为第一个可用选项
  const operators = getOperatorsForField(filter.field)
  if (operators.length > 0) {
    filter.operator = operators[0].value
  }
}

const getOperatorsForField = (field: string) => {
  return operatorMap[field as keyof typeof operatorMap] || []
}

const getValuePlaceholder = (field: string) => {
  switch (field) {
    case 'size':
      return '输入文件大小（KB）'
    case 'createdAt':
    case 'updatedAt':
      return 'YYYY-MM-DD'
    default:
      return '输入值'
  }
}

const applyAdvancedSearch = () => {
  // 将高级搜索条件转换为活动过滤器
  activeFilters.value = advancedFilters.value.filter(filter => 
    filter.value && filter.value.trim() !== ''
  )
  
  showAdvancedSearch.value = false
  handleSearch()
}

// 过滤器标签管理
const getFilterLabel = (filter: any) => {
  const fieldLabel = filterFields.find(f => f.value === filter.field)?.label || filter.field
  const operatorLabel = getOperatorsForField(filter.field)
    .find(op => op.value === filter.operator)?.label || filter.operator
  
  return `${fieldLabel} ${operatorLabel} ${filter.value}`
}

const removeFilter = (filterId: string) => {
  activeFilters.value = activeFilters.value.filter(f => f.id !== filterId)
  handleSearch()
}

const clearAllFilters = () => {
  activeFilters.value = []
  handleSearch()
}

// 素材操作
const previewAsset = (asset: any) => {
  window.electronAPI.previewImage(asset.path)
}

const quickPreview = (asset: any) => {
  // 快速预览实现
  console.log('快速预览:', asset.name)
}

const addToCollection = (asset: any) => {
  // 添加到收藏实现
  ElMessage.success(`已添加 "${asset.name}" 到收藏`)
}

const showAssetContextMenu = (event: MouseEvent, asset: any) => {
  event.preventDefault()
  selectedAsset.value = asset
  contextMenuPosition.value = { x: event.clientX, y: event.clientY }
  contextMenuVisible.value = true
}

const previewSelectedAsset = () => {
  if (selectedAsset.value) {
    previewAsset(selectedAsset.value)
  }
  contextMenuVisible.value = false
}

const openAssetLocation = () => {
  if (selectedAsset.value) {
    window.electronAPI.showItemInFolder(selectedAsset.value.path)
  }
  contextMenuVisible.value = false
}

const copyAssetPath = () => {
  if (selectedAsset.value) {
    navigator.clipboard.writeText(selectedAsset.value.path)
    ElMessage.success('已复制文件路径')
  }
  contextMenuVisible.value = false
}

const addToCollectionFromContext = () => {
  if (selectedAsset.value) {
    addToCollection(selectedAsset.value)
  }
  contextMenuVisible.value = false
}

const editAssetTags = () => {
  // 编辑标签实现
  ElMessage.info('编辑标签功能开发中')
  contextMenuVisible.value = false
}

const downloadAsset = () => {
  if (selectedAsset.value) {
    window.electronAPI.downloadFile(selectedAsset.value.path)
  }
  contextMenuVisible.value = false
}

const shareAsset = () => {
  ElMessage.info('分享功能开发中')
  contextMenuVisible.value = false
}

const exportSearchResults = () => {
  // 导出搜索结果实现
  ElMessage.info('导出功能开发中')
}

const handlePageChange = (page: number) => {
  currentPage.value = page
}

// 工具函数
const getAssetMainType = (type: string) => {
  if (type.startsWith('image/')) return 'images'
  if (type.startsWith('video/')) return 'videos'
  if (type.startsWith('audio/')) return 'audio'
  if (['application/pdf', 'text/plain', 'application/msword'].includes(type)) return 'documents'
  return 'other'
}

const getAssetTypeLabel = (type: string) => {
  const typeMap: Record<string, string> = {
    'image/jpeg': 'JPG',
    'image/png': 'PNG',
    'image/gif': 'GIF',
    'image/webp': 'WEBP',
    'video/mp4': 'MP4',
    'video/avi': 'AVI',
    'application/pdf': 'PDF',
    'text/plain': 'TXT'
  }
  return typeMap[type] || type.split('/')[1]?.toUpperCase() || 'FILE'
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 初始化
onMounted(() => {
  // 添加一个默认的搜索条件
  addFilter()
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.search-panel {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.search-toolbar {
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  flex-shrink: 0;
  
  .search-input-container {
    display: flex;
    gap: 12px;
    align-items: center;
    margin-bottom: 16px;
    
    .search-input {
      flex: 1;
      max-width: 400px;
    }
    
    .advanced-search-btn {
      flex-shrink: 0;
    }
  }
  
  .search-actions {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    .sort-dropdown {
      margin-left: auto;
    }
  }
}

.filter-tags {
  padding: 12px 24px;
  background: var(--el-bg-color-overlay);
  border-bottom: 1px solid var(--el-border-color-light);
  
  .filter-tags-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
    
    span {
      font-size: 14px;
      color: var(--el-text-color-regular);
    }
  }
  
  .tags-container {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
  }
}

.search-results {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

.search-loading {
  padding: 40px 0;
}

.no-results {
  text-align: center;
  padding: 60px 20px;
}

.results-grid {
  .results-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    span {
      font-size: 16px;
      color: var(--el-text-color-primary);
      font-weight: 500;
    }
  }
  
  .assets-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }
}

.asset-card {
    background: var(--el-bg-color-overlay);
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    overflow: hidden;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      border-color: var(--el-color-primary);
      transform: translateY(-2px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      
      .asset-overlay {
        opacity: 1;
      }
    }
    
    .asset-thumb {
      position: relative;
      width: 100%;
      aspect-ratio: 1;
      overflow: hidden;
      
      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }
      
      .asset-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.2s;
        
        .asset-actions {
          display: flex;
          gap: 8px;
        }
      }
      
      .asset-type-badge {
        position: absolute;
        top: 8px;
        right: 8px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 10px;
        font-weight: 500;
      }
    }
    
    .asset-info {
      padding: 12px;
      
      .asset-name {
        font-size: 14px;
        font-weight: 500;
        color: var(--el-text-color-primary);
        margin-bottom: 8px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      
      .asset-meta {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: var(--el-text-color-secondary);
        margin-bottom: 8px;
      }
      
      .asset-tags {
        display: flex;
        gap: 4px;
        flex-wrap: wrap;
        
        .more-tags {
          font-size: 11px;
          color: var(--el-text-color-placeholder);
          align-self: center;
        }
      }
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

.search-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  
  .placeholder-content {
    text-align: center;
    max-width: 400px;
    
    h3 {
      margin: 16px 0 8px;
      color: var(--el-text-color-primary);
    }
    
    p {
      color: var(--el-text-color-secondary);
      margin-bottom: 24px;
    }
    
    .search-tips {
      text-align: left;
      
      h4 {
        margin: 0 0 12px;
        color: var(--el-text-color-primary);
        font-size: 14px;
      }
      
      ul {
        margin: 0;
        padding-left: 20px;
        color: var(--el-text-color-secondary);
        font-size: 13px;
        
        li {
          margin-bottom: 4px;
        }
      }
    }
  }
}

.advanced-search-dialog {
  .advanced-search-content {
    max-height: 60vh;
    overflow-y: auto;
    
    .search-criteria {
      margin-bottom: 24px;
      
      .criteria-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 16px;
        
        h4 {
          margin: 0;
          color: var(--el-text-color-primary);
        }
      }
      
      .criteria-list {
        .criteria-item {
          margin-bottom: 16px;
          
          .criteria-controls {
            display: flex;
            gap: 8px;
            align-items: center;
            
            .remove-criteria-btn {
              flex-shrink: 0;
            }
          }
          
          .criteria-logic {
            margin-top: 8px;
            padding-left: 128px; // 对齐操作符选择器
          }
        }
      }
    }
    
    .search-options {
      .size-range {
        display: flex;
        align-items: center;
        gap: 8px;
        
        .range-separator {
          color: var(--el-text-color-placeholder);
        }
        
        .size-unit {
          color: var(--el-text-color-secondary);
          font-size: 14px;
        }
      }
    }
  }
}

.asset-context-menu {
  .el-dropdown-menu__item {
    &.danger {
      color: var(--el-color-danger);
      
      &:hover {
        background: var(--el-color-danger-light-9);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
  }
}

@media (max-width: 768px) {
  .search-toolbar {
    padding: 12px 16px;
    
    .search-input-container {
      flex-direction: column;
      align-items: stretch;
      
      .search-input {
        max-width: none;
        margin-bottom: 12px;
      }
    }
    
    .search-actions {
      flex-direction: column;
      gap: 12px;
      
      .sort-dropdown {
        margin-left: 0;
        align-self: flex-end;
      }
    }
  }
  
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)) !important;
    gap: 12px !important;
  }
  
  .filter-tags {
    padding: 8px 16px;
  }
  
  .search-results {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)) !important;
  }
  
  .asset-card {
    .asset-info {
      padding: 8px;
      
      .asset-name {
        font-size: 12px;
      }
      
      .asset-meta {
        font-size: 10px;
      }
    }
  }
}
</style>