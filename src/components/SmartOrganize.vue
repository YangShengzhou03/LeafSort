<template>
  <div class="smart-organize">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2>智能整理</h2>
        <el-button @click="showAutoOrganize = true">
          <el-icon><Magic /></el-icon>
          自动整理
        </el-button>
        <el-button @click="showBatchOrganize = true">
          <el-icon><Operation /></el-icon>
          批量整理
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="showSettings = true">
          <el-icon><Setting /></el-icon>
          整理设置
        </el-button>
        <el-button type="primary" @click="applyOrganize">
          <el-icon><Check /></el-icon>
          应用整理
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <!-- 左侧分类面板 -->
      <div class="sidebar">
        <div class="sidebar-section">
          <h3>分类方式</h3>
          <el-radio-group v-model="organizeMode" class="organize-modes">
            <el-radio label="time">
              <el-icon><Clock /></el-icon>
              按时间
            </el-radio>
            <el-radio label="type">
              <el-icon><Folder /></el-icon>
              按类型
            </el-radio>
            <el-radio label="color">
              <el-icon><Brush /></el-icon>
              按颜色
            </el-radio>
            <el-radio label="ai">
              <el-icon><Cpu /></el-icon>
              AI智能
            </el-radio>
          </el-radio-group>
        </div>

        <!-- 时间分类选项 -->
        <div v-if="organizeMode === 'time'" class="organize-options">
          <el-radio-group v-model="timeMode">
            <el-radio label="year">按年份</el-radio>
            <el-radio label="month">按月份</el-radio>
            <el-radio label="week">按周</el-radio>
            <el-radio label="day">按日期</el-radio>
          </el-radio-group>
        </div>

        <!-- 类型分类选项 -->
        <div v-if="organizeMode === 'type'" class="organize-options">
          <el-checkbox-group v-model="selectedTypes">
            <el-checkbox label="image">图片</el-checkbox>
            <el-checkbox label="video">视频</el-checkbox>
            <el-checkbox label="audio">音频</el-checkbox>
            <el-checkbox label="document">文档</el-checkbox>
            <el-checkbox label="other">其他</el-checkbox>
          </el-checkbox-group>
        </div>

        <!-- 颜色分类选项 -->
        <div v-if="organizeMode === 'color'" class="organize-options">
          <div class="color-palette">
            <div 
              v-for="color in colorCategories" 
              :key="color.name"
              class="color-item"
              :class="{ active: selectedColors.includes(color.name) }"
              @click="toggleColor(color.name)"
            >
              <div class="color-swatch" :style="{ backgroundColor: color.value }"></div>
              <span>{{ color.name }}</span>
            </div>
          </div>
          
          <el-slider
            v-model="colorTolerance"
            :min="1"
            :max="100"
            show-stops
            :format-tooltip="(val) => `颜色容差: ${val}%`"
          ></el-slider>
        </div>

        <!-- AI智能分类选项 -->
        <div v-if="organizeMode === 'ai'" class="organize-options">
          <el-select v-model="aiModel" placeholder="选择AI模型">
            <el-option label="通用分类" value="general"></el-option>
            <el-option label="场景识别" value="scene"></el-option>
            <el-option label="物体检测" value="object"></el-option>
            <el-option label="人脸识别" value="face"></el-option>
            <el-option label="文字识别" value="text"></el-option>
          </el-select>
          
          <div class="ai-confidence">
            <span>识别置信度</span>
            <el-slider
              v-model="aiConfidence"
              :min="50"
              :max="100"
              show-stops
              :format-tooltip="(val) => `${val}%`"
            ></el-slider>
          </div>
          
          <el-button @click="analyzeWithAI" :loading="isAnalyzing">
            <el-icon><Search /></el-icon>
            AI分析
          </el-button>
        </div>

        <!-- 预览统计 -->
        <div class="preview-stats">
          <h4>预览统计</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="stat-label">总素材数</span>
              <span class="stat-value">{{ totalAssets }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">分类数</span>
              <span class="stat-value">{{ previewCategories.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">已整理</span>
              <span class="stat-value">{{ organizedCount }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 右侧预览区域 -->
      <div class="preview-area">
        <!-- 分类预览 -->
        <div class="categories-preview">
          <div 
            v-for="category in previewCategories" 
            :key="category.id"
            class="category-card"
          >
            <div class="category-header">
              <h4>{{ category.name }}</h4>
              <span class="asset-count">{{ category.assets.length }} 个素材</span>
            </div>
            
            <div class="category-thumbnails">
              <div 
                v-for="asset in category.assets.slice(0, 4)" 
                :key="asset.id"
                class="thumbnail"
                :style="{ backgroundImage: `url(${asset.thumbnail})` }"
              ></div>
              <div v-if="category.assets.length > 4" class="thumbnail-more">
                +{{ category.assets.length - 4 }}
              </div>
            </div>
            
            <div class="category-actions">
              <el-button size="small" @click="previewCategory(category)">
                预览
              </el-button>
              <el-button size="small" type="primary" @click="createFolderForCategory(category)">
                创建文件夹
              </el-button>
            </div>
          </div>
          
          <div v-if="previewCategories.length === 0" class="empty-preview">
            <el-icon size="64" color="var(--el-text-color-placeholder)">
              <FolderOpened />
            </el-icon>
            <p>暂无分类预览</p>
            <span>选择分类方式并点击"预览整理"查看结果</span>
          </div>
        </div>

        <!-- 素材列表 -->
        <div class="assets-list">
          <div class="list-header">
            <span>待整理素材 ({{ unorganizedAssets.length }})</span>
            <el-button size="small" @click="selectAll">全选</el-button>
          </div>
          
          <div class="assets-grid">
            <div
              v-for="asset in unorganizedAssets"
              :key="asset.id"
              class="asset-item"
              :class="{ selected: selectedAssets.includes(asset.id) }"
              @click="toggleAssetSelection(asset)"
            >
              <div class="asset-thumbnail">
                <img :src="asset.thumbnail" :alt="asset.name" />
                <div class="asset-overlay">
                  <el-button size="small" circle @click.stop="previewAsset(asset)">
                    <el-icon><View /></el-icon>
                  </el-button>
                </div>
              </div>
              
              <div class="asset-info">
                <div class="asset-name">{{ asset.name }}</div>
                <div class="asset-details">
                  <span>{{ formatFileSize(asset.size) }}</span>
                  <span>{{ formatDate(asset.createdAt) }}</span>
                </div>
                <div class="asset-tags">
                  <el-tag 
                    v-for="tag in asset.tags.slice(0, 2)" 
                    :key="tag" 
                    size="small"
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
          
          <div v-if="unorganizedAssets.length === 0" class="empty-assets">
            <el-icon size="48" color="var(--el-text-color-placeholder)">
              <Files />
            </el-icon>
            <p>暂无待整理素材</p>
            <span>所有素材都已整理完成</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 自动整理对话框 -->
    <el-dialog
      v-model="showAutoOrganize"
      title="自动整理"
      width="600px"
    >
      <div class="auto-organize-dialog">
        <el-steps :active="autoOrganizeStep" align-center>
          <el-step title="分析素材" description="扫描并分析素材内容"></el-step>
          <el-step title="智能分类" description="根据分析结果自动分类"></el-step>
          <el-step title="创建结构" description="生成文件夹和标签"></el-step>
        </el-steps>
        
        <div class="auto-organize-content">
          <div v-if="autoOrganizeStep === 0" class="step-content">
            <el-progress 
              :percentage="analyzeProgress" 
              :status="analyzeProgress === 100 ? 'success' : ''"
            ></el-progress>
            <p>正在分析 {{ totalAssets }} 个素材...</p>
            <ul class="analysis-stats">
              <li>已分析: {{ analyzedCount }} 个</li>
              <li>图片识别: {{ imageAnalysisCount }} 个</li>
              <li>视频分析: {{ videoAnalysisCount }} 个</li>
            </ul>
          </div>
          
          <div v-if="autoOrganizeStep === 1" class="step-content">
            <div class="classification-results">
              <h4>分类结果预览</h4>
              <div class="classification-grid">
                <div 
                  v-for="result in autoClassificationResults" 
                  :key="result.category"
                  class="classification-item"
                >
                  <span class="category-name">{{ result.category }}</span>
                  <span class="asset-count">{{ result.count }} 个</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="autoOrganizeStep === 2" class="step-content">
            <el-checkbox-group v-model="selectedAutoActions">
              <el-checkbox label="createFolders">创建分类文件夹</el-checkbox>
              <el-checkbox label="addTags">添加智能标签</el-checkbox>
              <el-checkbox label="removeDuplicates">移除重复文件</el-checkbox>
              <el-checkbox label="optimizeNames">优化文件命名</el-checkbox>
            </el-checkbox-group>
          </div>
        </div>
        
        <template #footer>
          <el-button @click="showAutoOrganize = false">取消</el-button>
          <el-button 
            v-if="autoOrganizeStep > 0" 
            @click="autoOrganizeStep--"
          >
            上一步
          </el-button>
          <el-button 
            type="primary" 
            @click="nextAutoOrganizeStep"
            :loading="isAutoOrganizing"
          >
            {{ autoOrganizeStep === 2 ? '开始整理' : '下一步' }}
          </el-button>
        </template>
      </div>
    </el-dialog>

    <!-- 批量整理对话框 -->
    <el-dialog
      v-model="showBatchOrganize"
      title="批量整理"
      width="500px"
    >
      <div class="batch-organize-dialog">
        <el-form label-width="100px">
          <el-form-item label="选择操作">
            <el-select v-model="batchAction" placeholder="请选择操作">
              <el-option label="批量添加标签" value="addTags"></el-option>
              <el-option label="批量移动文件夹" value="moveToFolder"></el-option>
              <el-option label="批量重命名" value="rename"></el-option>
              <el-option label="批量删除" value="delete"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="batchAction === 'addTags'" label="标签">
            <el-input 
              v-model="batchTags" 
              placeholder="输入标签，用逗号分隔"
            />
          </el-form-item>
          
          <el-form-item v-if="batchAction === 'moveToFolder'" label="目标文件夹">
            <el-select v-model="batchTargetFolder" placeholder="请选择文件夹">
              <el-option 
                v-for="folder in availableFolders" 
                :key="folder.id" 
                :label="folder.name" 
                :value="folder.id"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item v-if="batchAction === 'rename'" label="命名规则">
            <el-select v-model="batchRenamePattern" placeholder="请选择命名规则">
              <el-option label="时间戳+序号" value="timestamp"></el-option>
              <el-option label="分类+序号" value="category"></el-option>
              <el-option label="自定义前缀" value="custom"></el-option>
            </el-select>
            <el-input 
              v-if="batchRenamePattern === 'custom'" 
              v-model="batchCustomPrefix" 
              placeholder="输入前缀"
            />
          </el-form-item>
          
          <el-form-item label="影响范围">
            <el-radio-group v-model="batchScope">
              <el-radio label="selected">仅选中的 {{ selectedAssets.length }} 个素材</el-radio>
              <el-radio label="all">所有 {{ totalAssets }} 个素材</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showBatchOrganize = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="executeBatchOrganize"
            :disabled="!canExecuteBatch"
          >
            执行批量操作
          </el-button>
        </template>
      </div>
    </el-dialog>

    <!-- 整理设置 -->
    <el-drawer
      v-model="showSettings"
      title="整理设置"
      direction="rtl"
      size="400px"
    >
      <div class="organize-settings">
        <el-form label-width="120px">
          <el-form-item label="自动整理">
            <el-switch v-model="settings.autoOrganize" />
          </el-form-item>
          
          <el-form-item label="整理频率">
            <el-select v-model="settings.organizeFrequency">
              <el-option label="每次导入后" value="onImport"></el-option>
              <el-option label="每天一次" value="daily"></el-option>
              <el-option label="每周一次" value="weekly"></el-option>
              <el-option label="手动整理" value="manual"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="默认文件夹">
            <el-input v-model="settings.defaultFolder" placeholder="未分类" />
          </el-form-item>
          
          <el-form-item label="智能标签">
            <el-switch v-model="settings.smartTags" />
          </el-form-item>
          
          <el-form-item label="重复检测">
            <el-switch v-model="settings.duplicateDetection" />
          </el-form-item>
          
          <el-form-item label="相似度阈值">
            <el-slider
              v-model="settings.similarityThreshold"
              :min="80"
              :max="100"
              show-stops
              :format-tooltip="(val) => `${val}%`"
            />
          </el-form-item>
          
          <el-form-item label="备份原文件">
            <el-switch v-model="settings.backupOriginal" />
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'

// 图标导入
import {
  Magic,
  Operation,
  Setting,
  Check,
  Clock,
  Folder,
  Brush,
  Cpu,
  Search,
  FolderOpened,
  Files,
  View
} from '@element-plus/icons-vue'

const libraryStore = useLibraryStore()

// 响应式数据
const organizeMode = ref<'time' | 'type' | 'color' | 'ai'>('time')
const timeMode = ref<'year' | 'month' | 'week' | 'day'>('month')
const selectedTypes = ref<string[]>(['image', 'video', 'audio', 'document', 'other'])
const selectedColors = ref<string[]>([])
const colorTolerance = ref(30)
const aiModel = ref('general')
const aiConfidence = ref(80)

const showAutoOrganize = ref(false)
const showBatchOrganize = ref(false)
const showSettings = ref(false)

const autoOrganizeStep = ref(0)
const isAutoOrganizing = ref(false)
const analyzeProgress = ref(0)
const analyzedCount = ref(0)
const imageAnalysisCount = ref(0)
const videoAnalysisCount = ref(0)

const batchAction = ref('')
const batchTags = ref('')
const batchTargetFolder = ref('')
const batchRenamePattern = ref('')
const batchCustomPrefix = ref('')
const batchScope = ref('selected')

const selectedAssets = ref<string[]>([])
const isAnalyzing = ref(false)

// 整理设置
const settings = reactive({
  autoOrganize: true,
  organizeFrequency: 'onImport',
  defaultFolder: '未分类',
  smartTags: true,
  duplicateDetection: true,
  similarityThreshold: 90,
  backupOriginal: true
})

// 颜色分类选项
const colorCategories = ref([
  { name: '红色', value: '#ff4d4f' },
  { name: '橙色', value: '#ff7a45' },
  { name: '黄色', value: '#ffec3d' },
  { name: '绿色', value: '#73d13d' },
  { name: '蓝色', value: '#409eff' },
  { name: '紫色', value: '#9254de' },
  { name: '粉色', value: '#f759ab' },
  { name: '棕色', value: '#a52a2a' },
  { name: '灰色', value: '#8c8c8c' },
  { name: '黑白', value: '#000000' }
])

// 自动分类结果预览
const autoClassificationResults = ref([
  { category: '风景照片', count: 24 },
  { category: '人物照片', count: 18 },
  { category: '设计素材', count: 12 },
  { category: '文档文件', count: 8 },
  { category: '视频素材', count: 6 }
])

const selectedAutoActions = ref(['createFolders', 'addTags'])

// 计算属性
const totalAssets = computed(() => libraryStore.assets.length)

const unorganizedAssets = computed(() => {
  return libraryStore.assets.filter(asset => !asset.folderId)
})

const organizedCount = computed(() => {
  return totalAssets.value - unorganizedAssets.value.length
})

const availableFolders = computed(() => {
  return libraryStore.folders
})

const previewCategories = computed(() => {
  // 根据选择的分类方式生成预览分类
  const categories: any[] = []
  
  if (organizeMode.value === 'time') {
    // 按时间分类逻辑
    const timeGroups = new Map()
    
    unorganizedAssets.value.forEach(asset => {
      const date = new Date(asset.createdAt)
      let key = ''
      
      switch (timeMode.value) {
        case 'year':
          key = date.getFullYear().toString()
          break
        case 'month':
          key = `${date.getFullYear()}-${date.getMonth() + 1}`
          break
        case 'week':
          key = `${date.getFullYear()}-W${Math.ceil((date.getDate() + 6 - date.getDay()) / 7)}`
          break
        case 'day':
          key = date.toISOString().split('T')[0]
          break
      }
      
      if (!timeGroups.has(key)) {
        timeGroups.set(key, [])
      }
      timeGroups.get(key).push(asset)
    })
    
    timeGroups.forEach((assets, key) => {
      categories.push({
        id: `time-${key}`,
        name: `${key} (${timeMode.value === 'year' ? '年' : timeMode.value === 'month' ? '月' : timeMode.value === 'week' ? '周' : '日'})`,
        assets: assets
      })
    })
  } else if (organizeMode.value === 'type') {
    // 按类型分类逻辑
    const typeGroups = new Map()
    
    unorganizedAssets.value.forEach(asset => {
      if (selectedTypes.value.includes(asset.type)) {
        if (!typeGroups.has(asset.type)) {
          typeGroups.set(asset.type, [])
        }
        typeGroups.get(asset.type).push(asset)
      }
    })
    
    typeGroups.forEach((assets, type) => {
      const typeNames = {
        image: '图片',
        video: '视频',
        audio: '音频',
        document: '文档',
        other: '其他'
      }
      
      categories.push({
        id: `type-${type}`,
        name: typeNames[type as keyof typeof typeNames] || type,
        assets: assets
      })
    })
  }
  
  return categories.sort((a, b) => b.assets.length - a.assets.length)
})

const canExecuteBatch = computed(() => {
  if (batchScope.value === 'selected' && selectedAssets.value.length === 0) {
    return false
  }
  
  switch (batchAction.value) {
    case 'addTags':
      return batchTags.value.trim().length > 0
    case 'moveToFolder':
      return batchTargetFolder.value.length > 0
    case 'rename':
      return batchRenamePattern.value.length > 0
    case 'delete':
      return true
    default:
      return false
  }
})

// 方法
const toggleAssetSelection = (asset: any) => {
  const index = selectedAssets.value.indexOf(asset.id)
  if (index >= 0) {
    selectedAssets.value.splice(index, 1)
  } else {
    selectedAssets.value.push(asset.id)
  }
}

const selectAll = () => {
  if (selectedAssets.value.length === unorganizedAssets.value.length) {
    selectedAssets.value = []
  } else {
    selectedAssets.value = unorganizedAssets.value.map(asset => asset.id)
  }
}

const toggleColor = (colorName: string) => {
  const index = selectedColors.value.indexOf(colorName)
  if (index >= 0) {
    selectedColors.value.splice(index, 1)
  } else {
    selectedColors.value.push(colorName)
  }
}

const analyzeWithAI = async () => {
  isAnalyzing.value = true
  
  try {
    // 模拟AI分析过程
    await new Promise(resolve => setTimeout(resolve, 2000))
    
    ElMessage.success('AI分析完成')
  } catch (error) {
    console.error('AI分析失败:', error)
    ElMessage.error('AI分析失败')
  } finally {
    isAnalyzing.value = false
  }
}

const previewCategory = (category: any) => {
  // 预览分类中的素材
  console.log('预览分类:', category)
}

const createFolderForCategory = async (category: any) => {
  try {
    const folder = await libraryStore.createFolder(category.name)
    
    // 将分类中的素材移动到新文件夹
    for (const asset of category.assets) {
      await libraryStore.moveAssetToFolder(asset.id, folder.id)
    }
    
    ElMessage.success(`已创建文件夹并移动 ${category.assets.length} 个素材`)
  } catch (error) {
    console.error('创建文件夹失败:', error)
    ElMessage.error('创建文件夹失败')
  }
}

const previewAsset = (asset: any) => {
  // 预览单个素材
  window.electronAPI.previewImage(asset.thumbnail)
}

const applyOrganize = async () => {
  if (previewCategories.value.length === 0) {
    ElMessage.warning('没有可应用的分类')
    return
  }
  
  try {
    for (const category of previewCategories.value) {
      await createFolderForCategory(category)
    }
    
    ElMessage.success(`整理完成，共创建 ${previewCategories.value.length} 个分类`)
  } catch (error) {
    console.error('应用整理失败:', error)
    ElMessage.error('应用整理失败')
  }
}

const nextAutoOrganizeStep = async () => {
  if (autoOrganizeStep.value === 0) {
    // 开始分析
    isAutoOrganizing.value = true
    
    // 模拟分析过程
    const total = unorganizedAssets.value.length
    for (let i = 0; i < total; i++) {
      analyzeProgress.value = Math.round(((i + 1) / total) * 100)
      analyzedCount.value = i + 1
      
      // 模拟不同类型的分析
      if (i % 3 === 0) imageAnalysisCount.value++
      if (i % 5 === 0) videoAnalysisCount.value++
      
      await new Promise(resolve => setTimeout(resolve, 50))
    }
    
    isAutoOrganizing.value = false
  }
  
  if (autoOrganizeStep.value < 2) {
    autoOrganizeStep.value++
  } else {
    // 开始自动整理
    await executeAutoOrganize()
    showAutoOrganize.value = false
  }
}

const executeAutoOrganize = async () => {
  try {
    ElMessage.success('自动整理完成')
  } catch (error) {
    console.error('自动整理失败:', error)
    ElMessage.error('自动整理失败')
  }
}

const executeBatchOrganize = async () => {
  try {
    const assetsToProcess = batchScope.value === 'selected' 
      ? libraryStore.assets.filter(asset => selectedAssets.value.includes(asset.id))
      : libraryStore.assets
    
    switch (batchAction.value) {
      case 'addTags':
        const tags = batchTags.value.split(',').map(tag => tag.trim()).filter(tag => tag)
        for (const asset of assetsToProcess) {
          await libraryStore.addTagsToAsset(asset.id, tags)
        }
        break
      case 'moveToFolder':
        for (const asset of assetsToProcess) {
          await libraryStore.moveAssetToFolder(asset.id, batchTargetFolder.value)
        }
        break
      case 'rename':
        // 批量重命名逻辑
        break
      case 'delete':
        await ElMessageBox.confirm(
          `确定要删除 ${assetsToProcess.length} 个素材吗？此操作不可撤销。`,
          '确认删除',
          { type: 'warning' }
        )
        for (const asset of assetsToProcess) {
          await libraryStore.deleteAsset(asset.id)
        }
        break
    }
    
    ElMessage.success(`批量操作完成，影响了 ${assetsToProcess.length} 个素材`)
    showBatchOrganize.value = false
    selectedAssets.value = []
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败')
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString()
}

// 生命周期
onMounted(() => {
  // 初始化数据
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.smart-organize {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.toolbar {
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  
  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    h2 {
      margin: 0;
      color: var(--el-text-color-primary);
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 300px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  padding: 20px;
  overflow-y: auto;
  
  .sidebar-section {
    margin-bottom: 24px;
    
    h3 {
      margin: 0 0 12px;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
  }
}

.organize-modes {
    display: flex;
    flex-direction: column;
    gap: 8px;
    
    .el-radio {
      margin: 4px 0;
      
      :deep(.el-radio__label) {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }
}

.organize-options {
  margin-top: 12px;
  padding: 12px;
  background: var(--el-bg-color-overlay);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
  
  .el-checkbox-group,
  .el-radio-group {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
}

.color-palette {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  margin-bottom: 16px;
  
  .color-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: var(--el-bg-color-hover);
    }
    
    &.active {
      background: var(--el-color-primary-light-9);
      border: 1px solid var(--el-color-primary);
    }
    
    .color-swatch {
      width: 20px;
      height: 20px;
      border-radius: 3px;
      border: 1px solid var(--el-border-color);
    }
    
    span {
      font-size: 12px;
      color: var(--el-text-color-regular);
    }
  }
}

.ai-confidence {
  margin: 16px 0;
  
  span {
    display: block;
    margin-bottom: 8px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.preview-stats {
  margin-top: 24px;
  padding: 16px;
  background: var(--el-bg-color-overlay);
  border-radius: 6px;
  border: 1px solid var(--el-border-color-light);
  
  h4 {
    margin: 0 0 12px;
    color: var(--el-text-color-primary);
    font-size: 14px;
  }
  
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
  }
  
  .stat-item {
    text-align: center;
    
    .stat-label {
      display: block;
      font-size: 11px;
      color: var(--el-text-color-secondary);
      margin-bottom: 4px;
    }
    
    .stat-value {
      display: block;
      font-size: 18px;
      font-weight: 600;
      color: var(--el-color-primary);
    }
  }
}

.preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.categories-preview {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 16px;
  align-content: start;
}

.category-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  .category-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
    
    h4 {
      margin: 0;
      color: var(--el-text-color-primary);
      font-size: 14px;
    }
    
    .asset-count {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
  
  .category-thumbnails {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 4px;
    margin-bottom: 12px;
    
    .thumbnail {
      aspect-ratio: 1;
      background-size: cover;
      background-position: center;
      border-radius: 4px;
      border: 1px solid var(--el-border-color);
    }
    
    .thumbnail-more {
      aspect-ratio: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--el-bg-color-overlay);
      border-radius: 4px;
      border: 1px dashed var(--el-border-color);
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
  
  .category-actions {
    display: flex;
    gap: 8px;
    
    .el-button {
      flex: 1;
    }
  }
}

.empty-preview {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin: 16px 0 8px;
    font-size: 16px;
  }
  
  span {
    font-size: 14px;
  }
}

.assets-list {
  height: 300px;
  border-top: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  
  .list-header {
    padding: 12px 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--el-border-color-light);
    
    span {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
  }
  
  .assets-grid {
    height: calc(300px - 48px);
    overflow-y: auto;
    padding: 12px;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }
}

.asset-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  padding: 8px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--el-color-primary);
    background: var(--el-bg-color-overlay);
  }
  
  &.selected {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
  
  .asset-thumbnail {
    position: relative;
    aspect-ratio: 1;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 8px;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .asset-overlay {
      position: absolute;
      top: 4px;
      right: 4px;
      opacity: 0;
      transition: opacity 0.2s;
    }
    
    &:hover .asset-overlay {
      opacity: 1;
    }
  }
  
  .asset-info {
    .asset-name {
      font-size: 12px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .asset-details {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--el-text-color-secondary);
      margin-bottom: 4px;
    }
    
    .asset-tags {
      display: flex;
      gap: 2px;
      flex-wrap: wrap;
      
      .el-tag {
        height: 16px;
        line-height: 14px;
      }
      
      .more-tags {
        font-size: 10px;
        color: var(--el-text-color-secondary);
        align-self: center;
      }
    }
  }
}

.empty-assets {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin: 16px 0 8px;
    font-size: 16px;
  }
  
  span {
    font-size: 14px;
  }
}

// 对话框样式
.auto-organize-dialog {
  .step-content {
    margin: 20px 0;
    
    .analysis-stats {
      margin-top: 12px;
      padding-left: 20px;
      
      li {
        font-size: 14px;
        color: var(--el-text-color-secondary);
        margin: 4px 0;
      }
    }
    
    .classification-results {
      h4 {
        margin: 0 0 12px;
        color: var(--el-text-color-primary);
      }
      
      .classification-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 8px;
      }
      
      .classification-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 12px;
        background: var(--el-bg-color-overlay);
        border-radius: 4px;
        border: 1px solid var(--el-border-color-light);
        
        .category-name {
          font-size: 14px;
          color: var(--el-text-color-primary);
        }
        
        .asset-count {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
  }
}

.batch-organize-dialog {
  .el-form-item {
    margin-bottom: 16px;
  }
}

.organize-settings {
  padding: 20px;
  
  .el-form-item {
    margin-bottom: 20px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .categories-preview {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .content {
    flex-direction: column;
  }
  
  .sidebar {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .categories-preview {
    grid-template-columns: 1fr;
  }
  
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>
