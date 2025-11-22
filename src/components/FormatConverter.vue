<template>
  <div class="format-converter">
    <!-- 转换工具栏 -->
    <div class="converter-toolbar">
      <div class="toolbar-left">
        <el-button @click="$emit('close')" text>
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>格式转换</h2>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="addFiles">
          <el-icon><Plus /></el-icon>
          添加文件
        </el-button>
        <el-button @click="addFolder">
          <el-icon><FolderAdd /></el-icon>
          添加文件夹
        </el-button>
        <el-button @click="clearAll" :disabled="conversionList.length === 0">
          <el-icon><Delete /></el-icon>
          清空列表
        </el-button>
        <el-button type="primary" @click="startConversion" :disabled="conversionList.length === 0">
          <el-icon><VideoPlay /></el-icon>
          开始转换
        </el-button>
      </div>
    </div>

    <!-- 转换内容区域 -->
    <div class="converter-content">
      <!-- 左侧设置面板 -->
      <div class="settings-panel">
        <div class="settings-section">
          <h4>输出设置</h4>
          <el-form label-width="80px">
            <el-form-item label="目标格式：">
              <el-select v-model="outputFormat" placeholder="选择输出格式">
                <el-option-group
                  v-for="group in formatGroups"
                  :key="group.label"
                  :label="group.label"
                >
                  <el-option
                    v-for="format in group.options"
                    :key="format.value"
                    :label="format.label"
                    :value="format.value"
                  />
                </el-option-group>
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="showQualitySetting" label="质量：">
              <el-slider
                v-model="outputQuality"
                :min="1"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item v-if="showCompressionSetting" label="压缩：">
              <el-slider
                v-model="compressionLevel"
                :min="0"
                :max="9"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="尺寸调整：">
              <el-select v-model="resizeMode">
                <el-option label="保持原尺寸" value="original" />
                <el-option label="按比例缩放" value="scale" />
                <el-option label="自定义尺寸" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="resizeMode === 'scale'" label="缩放比例：">
              <el-slider
                v-model="scaleFactor"
                :min="10"
                :max="200"
                :step="5"
                show-input
                :format-tooltip="(val) => `${val}%`"
              />
            </el-form-item>
            
            <el-form-item v-if="resizeMode === 'custom'" label="自定义：">
              <div class="custom-size">
                <el-input-number v-model="customSize.width" :min="1" placeholder="宽" />
                <span>×</span>
                <el-input-number v-model="customSize.height" :min="1" placeholder="高" />
              </div>
              <el-checkbox v-model="preserveAspectRatio" style="margin-top: 8px">
                保持宽高比
              </el-checkbox>
            </el-form-item>
            
            <el-form-item label="输出目录：">
              <el-input v-model="outputDirectory" readonly>
                <template #append>
                  <el-button @click="chooseOutputDirectory">选择</el-button>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item label="文件名：">
              <el-select v-model="namingConvention">
                <el-option label="原文件名" value="original" />
                <el-option label="原文件名+格式后缀" value="with-suffix" />
                <el-option label="时间戳" value="timestamp" />
                <el-option label="自定义前缀" value="custom-prefix" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="namingConvention === 'custom-prefix'" label="前缀：">
              <el-input v-model="customPrefix" placeholder="输入文件名前缀" />
            </el-form-item>
          </el-form>
        </div>

        <div class="settings-section">
          <h4>批量设置</h4>
          <el-form label-width="80px">
            <el-form-item label="并发数量：">
              <el-slider
                v-model="concurrentTasks"
                :min="1"
                :max="10"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="覆盖策略：">
              <el-radio-group v-model="overwritePolicy">
                <el-radio label="skip">跳过已存在</el-radio>
                <el-radio label="overwrite">覆盖</el-radio>
                <el-radio label="rename">重命名</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="转换后：">
              <el-checkbox-group v-model="postConversionActions">
                <el-checkbox label="openFolder">打开输出目录</el-checkbox>
                <el-checkbox label="deleteOriginal">删除原文件</el-checkbox>
                <el-checkbox label="addToLibrary">添加到素材库</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item>
              <el-button @click="savePreset" style="width: 100%">
                保存为预设
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <div class="settings-section">
          <h4>预设管理</h4>
          <div class="preset-list">
            <div
              v-for="preset in conversionPresets"
              :key="preset.id"
              class="preset-item"
              :class="{ active: activePreset === preset.id }"
              @click="loadPreset(preset)"
            >
              <span class="preset-name">{{ preset.name }}</span>
              <span class="preset-format">{{ preset.format }}</span>
              <el-button
                size="small"
                text
                @click.stop="deletePreset(preset.id)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央转换列表 -->
      <div class="conversion-list-panel">
        <div class="list-header">
          <span>待转换文件 ({{ conversionList.length }})</span>
          <div class="header-actions">
            <el-button size="small" @click="selectAll">
              <el-icon><Select /></el-icon>
              全选
            </el-button>
            <el-button size="small" @click="deselectAll">
              <el-icon><CircleClose /></el-icon>
              取消选择
            </el-button>
            <el-button size="small" @click="removeSelected" :disabled="selectedCount === 0">
              <el-icon><Remove /></el-icon>
              移除选中
            </el-button>
          </div>
        </div>
        
        <div class="conversion-list">
          <div
            v-for="(item, index) in conversionList"
            :key="item.id"
            class="conversion-item"
            :class="{ 
              selected: item.selected, 
              converting: item.status === 'converting',
              success: item.status === 'success',
              error: item.status === 'error'
            }"
            @click="toggleSelection(item)"
          >
            <div class="item-preview">
              <img v-if="isImage(item.originalPath)" :src="getThumbnail(item.originalPath)" />
              <div v-else class="file-icon">
                <el-icon><Document /></el-icon>
              </div>
            </div>
            
            <div class="item-info">
              <div class="file-name">{{ getFileName(item.originalPath) }}</div>
              <div class="file-details">
                <span class="original-format">{{ getFileExtension(item.originalPath) }}</span>
                <span class="file-size">{{ formatFileSize(item.fileSize) }}</span>
                <span class="dimensions" v-if="item.dimensions">
                  {{ item.dimensions.width }}×{{ item.dimensions.height }}
                </span>
              </div>
              
              <div class="conversion-progress" v-if="item.status === 'converting'">
                <el-progress
                  :percentage="item.progress || 0"
                  :show-text="false"
                  :stroke-width="4"
                />
                <span class="progress-text">{{ item.progress || 0 }}%</span>
              </div>
              
              <div class="conversion-result" v-if="item.status === 'success'">
                <el-icon color="#67C23A"><SuccessFilled /></el-icon>
                <span>转换成功</span>
              </div>
              
              <div class="conversion-result" v-if="item.status === 'error'">
                <el-icon color="#F56C6C"><WarningFilled /></el-icon>
                <span>{{ item.errorMessage || '转换失败' }}</span>
              </div>
            </div>
            
            <div class="item-actions">
              <el-button
                size="small"
                text
                @click.stop="removeItem(index)"
              >
                <el-icon><Close /></el-icon>
              </el-button>
              
              <el-button
                v-if="item.status === 'success'"
                size="small"
                text
                @click.stop="openOutputFile(item)"
              >
                <el-icon><View /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div v-if="conversionList.length === 0" class="empty-state">
            <el-icon class="empty-icon"><Picture /></el-icon>
            <p>暂无待转换文件</p>
            <p class="empty-hint">点击上方按钮添加文件或文件夹</p>
          </div>
        </div>
        
        <!-- 转换统计 -->
        <div class="conversion-stats" v-if="conversionList.length > 0">
          <div class="stat-item">
            <span>总计: {{ conversionList.length }}</span>
          </div>
          <div class="stat-item">
            <span>成功: {{ successCount }}</span>
          </div>
          <div class="stat-item">
            <span>失败: {{ errorCount }}</span>
          </div>
          <div class="stat-item">
            <span>进行中: {{ convertingCount }}</span>
          </div>
          <div class="stat-item">
            <span>待处理: {{ pendingCount }}</span>
          </div>
        </div>
      </div>

      <!-- 右侧预览面板 -->
      <div class="preview-panel">
        <div class="preview-section">
          <h4>预览</h4>
          <div class="preview-content" v-if="selectedItem">
            <div class="preview-image" v-if="isImage(selectedItem.originalPath)">
              <img :src="getThumbnail(selectedItem.originalPath)" />
              <div class="preview-overlay">
                <div class="preview-info">
                  <span>原格式: {{ getFileExtension(selectedItem.originalPath) }}</span>
                  <span>目标格式: {{ outputFormat }}</span>
                  <span>尺寸: {{ selectedItem.dimensions?.width }}×{{ selectedItem.dimensions?.height }}</span>
                </div>
              </div>
            </div>
            
            <div v-else class="preview-file">
              <el-icon class="file-icon-large"><Document /></el-icon>
              <p>{{ getFileName(selectedItem.originalPath) }}</p>
            </div>
            
            <div class="preview-settings">
              <h5>转换设置预览</h5>
              <el-descriptions :column="1" size="small" border>
                <el-descriptions-item label="输出格式">
                  {{ getFormatLabel(outputFormat) }}
                </el-descriptions-item>
                <el-descriptions-item label="质量" v-if="showQualitySetting">
                  {{ outputQuality }}%
                </el-descriptions-item>
                <el-descriptions-item label="压缩级别" v-if="showCompressionSetting">
                  {{ compressionLevel }}
                </el-descriptions-item>
                <el-descriptions-item label="尺寸调整">
                  {{ getResizeModeLabel() }}
                </el-descriptions-item>
                <el-descriptions-item label="输出目录">
                  {{ outputDirectory }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </div>
          
          <div v-else class="preview-empty">
            <el-icon class="empty-icon"><Search /></el-icon>
            <p>选择文件查看预览</p>
          </div>
        </div>
        
        <div class="preview-section">
          <h4>转换日志</h4>
          <div class="conversion-log">
            <div
              v-for="(log, index) in conversionLogs"
              :key="index"
              class="log-entry"
              :class="log.type"
            >
              <span class="log-time">{{ log.timestamp }}</span>
              <span class="log-message">{{ log.message }}</span>
            </div>
            
            <div v-if="conversionLogs.length === 0" class="log-empty">
              <p>暂无转换日志</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 批量添加对话框 -->
    <el-dialog
      v-model="showBatchAddDialog"
      title="批量添加文件"
      width="600px"
    >
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :multiple="true"
        :file-list="uploadFiles"
        :on-change="handleFileChange"
        drag
      >
        <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击选择</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持批量上传图片、视频、文档等文件
          </div>
        </template>
      </el-upload>
      
      <template #footer>
        <el-button @click="showBatchAddDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmBatchAdd">确认添加</el-button>
      </template>
    </el-dialog>

    <!-- 转换进度对话框 -->
    <el-dialog
      v-model="showProgressDialog"
      title="正在转换"
      width="500px"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      :show-close="false"
    >
      <div class="progress-dialog">
        <el-progress
          :percentage="overallProgress"
          :stroke-width="8"
          :text-inside="true"
        />
        
        <div class="progress-details">
          <p>正在转换: {{ currentConvertingFile }}</p>
          <p>已完成: {{ successCount }} / 总计: {{ conversionList.length }}</p>
        </div>
        
        <div class="progress-actions">
          <el-button @click="pauseConversion" v-if="!isPaused">
            <el-icon><VideoPause /></el-icon>
            暂停
          </el-button>
          <el-button @click="resumeConversion" v-else>
            <el-icon><VideoPlay /></el-icon>
            继续
          </el-button>
          <el-button @click="stopConversion" type="danger">
            <el-icon><SwitchButton /></el-icon>
            停止
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useLibraryStore } from '@/stores/library'
import {
  ArrowLeft,
  Plus,
  FolderAdd,
  Delete,
  VideoPlay,
  Select,
  CircleClose,
  Remove,
  Document,
  Close,
  View,
  Picture,
  SuccessFilled,
  WarningFilled,
  Search,
  UploadFilled,
  VideoPause,
  SwitchButton
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const emit = defineEmits(['close'])

const libraryStore = useLibraryStore()

// 转换设置
const outputFormat = ref('jpeg')
const outputQuality = ref(90)
const compressionLevel = ref(6)
const resizeMode = ref('original')
const scaleFactor = ref(100)
const customSize = reactive({ width: 0, height: 0 })
const preserveAspectRatio = ref(true)
const outputDirectory = ref('')
const namingConvention = ref('with-suffix')
const customPrefix = ref('')

// 批量设置
const concurrentTasks = ref(3)
const overwritePolicy = ref('rename')
const postConversionActions = ref<string[]>(['openFolder'])

// 预设管理
const activePreset = ref('')
const conversionPresets = ref<any[]>([])

// 转换列表
const conversionList = ref<any[]>([])
const selectedItem = ref<any>(null)
const uploadFiles = ref<any[]>([])
const showBatchAddDialog = ref(false)

// 转换状态
const showProgressDialog = ref(false)
const overallProgress = ref(0)
const currentConvertingFile = ref('')
const isPaused = ref(false)
const conversionLogs = ref<any[]>([])

// 格式分组
const formatGroups = ref([
  {
    label: '图片格式',
    options: [
      { label: 'JPEG', value: 'jpeg' },
      { label: 'PNG', value: 'png' },
      { label: 'WEBP', value: 'webp' },
      { label: 'GIF', value: 'gif' },
      { label: 'BMP', value: 'bmp' }
    ]
  },
  {
    label: '文档格式',
    options: [
      { label: 'PDF', value: 'pdf' },
      { label: 'TXT', value: 'txt' }
    ]
  }
])

// 计算属性
const showQualitySetting = computed(() => {
  return ['jpeg', 'webp'].includes(outputFormat.value)
})

const showCompressionSetting = computed(() => {
  return ['png', 'gif'].includes(outputFormat.value)
})

const selectedCount = computed(() => {
  return conversionList.value.filter(item => item.selected).length
})

const successCount = computed(() => {
  return conversionList.value.filter(item => item.status === 'success').length
})

const errorCount = computed(() => {
  return conversionList.value.filter(item => item.status === 'error').length
})

const convertingCount = computed(() => {
  return conversionList.value.filter(item => item.status === 'converting').length
})

const pendingCount = computed(() => {
  return conversionList.value.filter(item => !item.status).length
})

// 初始化
onMounted(() => {
  loadPresets()
  setDefaultOutputDirectory()
})

// 文件操作
const addFiles = async () => {
  try {
    const files = await window.electronAPI.showOpenDialog({
      properties: ['openFile', 'multiSelections'],
      filters: [
        { name: '所有支持的文件', extensions: ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'pdf', 'txt'] }
      ]
    })
    
    if (files && files.length > 0) {
      await addFilesToList(files)
    }
  } catch (error) {
    console.error('添加文件失败:', error)
    ElMessage.error('添加文件失败')
  }
}

const addFolder = async () => {
  try {
    const folder = await window.electronAPI.showOpenDialog({
      properties: ['openDirectory']
    })
    
    if (folder && folder.length > 0) {
      const files = await window.electronAPI.readDirectory(folder[0])
      await addFilesToList(files.filter(file => isSupportedFormat(file)))
    }
  } catch (error) {
    console.error('添加文件夹失败:', error)
    ElMessage.error('添加文件夹失败')
  }
}

const addFilesToList = async (files: string[]) => {
  for (const filePath of files) {
    if (conversionList.value.some(item => item.originalPath === filePath)) {
      continue // 跳过已存在的文件
    }
    
    const fileInfo = await getFileInfo(filePath)
    conversionList.value.push({
      id: generateId(),
      originalPath: filePath,
      fileSize: fileInfo.size,
      dimensions: fileInfo.dimensions,
      selected: false,
      status: undefined
    })
  }
  
  ElMessage.success(`成功添加 ${files.length} 个文件`)
}

const getFileInfo = async (filePath: string) => {
  const stats = await window.electronAPI.getFileStats(filePath)
  let dimensions = null
  
  if (isImage(filePath)) {
    dimensions = await getImageDimensions(filePath)
  }
  
  return {
    size: stats.size,
    dimensions
  }
}

const getImageDimensions = async (filePath: string): Promise<{ width: number; height: number }> => {
  return new Promise((resolve) => {
    const img = new Image()
    img.onload = () => {
      resolve({ width: img.width, height: img.height })
    }
    img.onerror = () => {
      resolve({ width: 0, height: 0 })
    }
    img.src = filePath
  })
}

// 列表操作
const toggleSelection = (item: any) => {
  item.selected = !item.selected
  if (item.selected) {
    selectedItem.value = item
  }
}

const selectAll = () => {
  conversionList.value.forEach(item => {
    item.selected = true
  })
  if (conversionList.value.length > 0) {
    selectedItem.value = conversionList.value[0]
  }
}

const deselectAll = () => {
  conversionList.value.forEach(item => {
    item.selected = false
  })
  selectedItem.value = null
}

const removeSelected = () => {
  conversionList.value = conversionList.value.filter(item => !item.selected)
  if (selectedItem.value && !selectedItem.value.selected) {
    selectedItem.value = null
  }
}

const removeItem = (index: number) => {
  conversionList.value.splice(index, 1)
  if (selectedItem.value === conversionList.value[index]) {
    selectedItem.value = null
  }
}

const clearAll = () => {
  conversionList.value = []
  selectedItem.value = null
  conversionLogs.value = []
}

// 转换操作
const startConversion = async () => {
  if (conversionList.value.length === 0) {
    ElMessage.warning('请先添加要转换的文件')
    return
  }
  
  if (!outputDirectory.value) {
    ElMessage.warning('请选择输出目录')
    return
  }
  
  showProgressDialog.value = true
  overallProgress.value = 0
  isPaused.value = false
  
  await processConversionBatch()
}

const processConversionBatch = async () => {
  const pendingItems = conversionList.value.filter(item => !item.status)
  
  for (let i = 0; i < pendingItems.length && !isPaused.value; i++) {
    const item = pendingItems[i]
    item.status = 'converting'
    currentConvertingFile.value = getFileName(item.originalPath)
    
    try {
      await convertFile(item)
      item.status = 'success'
      addLog('success', `转换成功: ${getFileName(item.originalPath)}`)
    } catch (error) {
      item.status = 'error'
      item.errorMessage = error instanceof Error ? error.message : '转换失败'
      addLog('error', `转换失败: ${getFileName(item.originalPath)} - ${item.errorMessage}`)
    }
    
    overallProgress.value = Math.round((successCount.value + errorCount.value) / conversionList.value.length * 100)
    
    // 控制并发数量
    if ((i + 1) % concurrentTasks.value === 0) {
      await new Promise(resolve => setTimeout(resolve, 100))
    }
  }
  
  if (!isPaused.value) {
    showProgressDialog.value = false
    ElMessage.success(`转换完成! 成功: ${successCount.value}, 失败: ${errorCount.value}`)
    
    // 执行转换后操作
    await executePostConversionActions()
  }
}

const convertFile = async (item: any) => {
  return new Promise<void>((resolve, reject) => {
    // 模拟转换过程
    const totalSteps = 10
    let currentStep = 0
    
    const interval = setInterval(() => {
      if (isPaused.value) {
        clearInterval(interval)
        return
      }
      
      currentStep++
      item.progress = (currentStep / totalSteps) * 100
      
      if (currentStep >= totalSteps) {
        clearInterval(interval)
        
        // 模拟转换结果
        const outputPath = generateOutputPath(item.originalPath)
        
        // 实际转换逻辑会在这里调用 Electron API
        window.electronAPI.convertImage({
          inputPath: item.originalPath,
          outputPath,
          format: outputFormat.value,
          quality: outputQuality.value / 100,
          resize: getResizeOptions(),
          compression: compressionLevel.value
        }).then(() => {
          item.outputPath = outputPath
          resolve()
        }).catch(reject)
      }
    }, 200)
  })
}

const generateOutputPath = (originalPath: string) => {
  const fileName = getFileName(originalPath)
  const ext = getFileExtension(originalPath)
  const baseName = fileName.replace(`.${ext}`, '')
  
  let newFileName = baseName
  
  switch (namingConvention.value) {
    case 'original':
      newFileName = baseName
      break
    case 'with-suffix':
      newFileName = `${baseName}_converted`
      break
    case 'timestamp':
      newFileName = `${Date.now()}`
      break
    case 'custom-prefix':
      newFileName = `${customPrefix.value}${baseName}`
      break
  }
  
  return `${outputDirectory.value}/${newFileName}.${outputFormat.value}`
}

const getResizeOptions = () => {
  switch (resizeMode.value) {
    case 'scale':
      return { mode: 'scale', factor: scaleFactor.value / 100 }
    case 'custom':
      return { 
        mode: 'custom', 
        width: customSize.width, 
        height: customSize.height,
        preserveAspectRatio: preserveAspectRatio.value
      }
    default:
      return { mode: 'original' }
  }
}

const pauseConversion = () => {
  isPaused.value = true
}

const resumeConversion = () => {
  isPaused.value = false
  processConversionBatch()
}

const stopConversion = () => {
  isPaused.value = false
  showProgressDialog.value = false
  
  // 重置进行中的任务
  conversionList.value.forEach(item => {
    if (item.status === 'converting') {
      item.status = undefined
      item.progress = 0
    }
  })
  
  ElMessage.info('转换已停止')
}

// 预设管理
const loadPresets = () => {
  const saved = localStorage.getItem('formatConverterPresets')
  if (saved) {
    conversionPresets.value = JSON.parse(saved)
  }
}

const savePreset = () => {
  const preset = {
    id: generateId(),
    name: `预设_${conversionPresets.value.length + 1}`,
    format: outputFormat.value,
    settings: {
      outputFormat: outputFormat.value,
      outputQuality: outputQuality.value,
      compressionLevel: compressionLevel.value,
      resizeMode: resizeMode.value,
      scaleFactor: scaleFactor.value,
      customSize: { ...customSize },
      preserveAspectRatio: preserveAspectRatio.value,
      namingConvention: namingConvention.value,
      customPrefix: customPrefix.value,
      concurrentTasks: concurrentTasks.value,
      overwritePolicy: overwritePolicy.value,
      postConversionActions: [...postConversionActions.value]
    }
  }
  
  conversionPresets.value.push(preset)
  localStorage.setItem('formatConverterPresets', JSON.stringify(conversionPresets.value))
  
  ElMessage.success('预设已保存')
}

const loadPreset = (preset: any) => {
  activePreset.value = preset.id
  Object.assign({
    outputFormat,
    outputQuality,
    compressionLevel,
    resizeMode,
    scaleFactor,
    customSize,
    preserveAspectRatio,
    namingConvention,
    customPrefix,
    concurrentTasks,
    overwritePolicy,
    postConversionActions
  }, preset.settings)
  
  ElMessage.success(`已加载预设: ${preset.name}`)
}

const deletePreset = (presetId: string) => {
  conversionPresets.value = conversionPresets.value.filter(p => p.id !== presetId)
  localStorage.setItem('formatConverterPresets', JSON.stringify(conversionPresets.value))
  
  if (activePreset.value === presetId) {
    activePreset.value = ''
  }
  
  ElMessage.success('预设已删除')
}

// 工具函数
const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const isSupportedFormat = (filePath: string) => {
  const ext = getFileExtension(filePath).toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'pdf', 'txt'].includes(ext)
}

const isImage = (filePath: string) => {
  const ext = getFileExtension(filePath).toLowerCase()
  return ['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext)
}

const getFileName = (filePath: string) => {
  return filePath.split(/[\\/]/).pop() || filePath
}

const getFileExtension = (filePath: string) => {
  return filePath.split('.').pop()?.toLowerCase() || ''
}

const getThumbnail = (filePath: string) => {
  return filePath // 实际应用中可能需要生成缩略图
}

const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const getFormatLabel = (format: string) => {
  const formatMap: Record<string, string> = {
    jpeg: 'JPEG',
    png: 'PNG',
    webp: 'WEBP',
    gif: 'GIF',
    bmp: 'BMP',
    pdf: 'PDF',
    txt: 'TXT'
  }
  return formatMap[format] || format.toUpperCase()
}

const getResizeModeLabel = () => {
  switch (resizeMode.value) {
    case 'original':
      return '保持原尺寸'
    case 'scale':
      return `缩放 ${scaleFactor.value}%`
    case 'custom':
      return `自定义 ${customSize.width}×${customSize.height}`
    default:
      return resizeMode.value
  }
}

const setDefaultOutputDirectory = async () => {
  try {
    const downloadsPath = await window.electronAPI.getPath('downloads')
    outputDirectory.value = downloadsPath
  } catch (error) {
    outputDirectory.value = 'C:\\Downloads'
  }
}

const chooseOutputDirectory = async () => {
  try {
    const directory = await window.electronAPI.showOpenDialog({
      properties: ['openDirectory']
    })
    
    if (directory && directory.length > 0) {
      outputDirectory.value = directory[0]
    }
  } catch (error) {
    console.error('选择目录失败:', error)
    ElMessage.error('选择目录失败')
  }
}

const openOutputFile = (item: any) => {
  if (item.outputPath) {
    window.electronAPI.openFile(item.outputPath)
  }
}

const addLog = (type: 'info' | 'success' | 'error', message: string) => {
  conversionLogs.value.unshift({
    type,
    message,
    timestamp: new Date().toLocaleTimeString()
  })
  
  // 限制日志数量
  if (conversionLogs.value.length > 100) {
    conversionLogs.value = conversionLogs.value.slice(0, 100)
  }
}

const executePostConversionActions = async () => {
  if (postConversionActions.value.includes('openFolder')) {
    window.electronAPI.openFile(outputDirectory.value)
  }
  
  if (postConversionActions.value.includes('deleteOriginal')) {
    // 删除原文件逻辑
    const successItems = conversionList.value.filter(item => item.status === 'success')
    for (const item of successItems) {
      try {
        await window.electronAPI.deleteFile(item.originalPath)
      } catch (error) {
        console.error('删除原文件失败:', error)
      }
    }
  }
  
  if (postConversionActions.value.includes('addToLibrary')) {
    // 添加到素材库逻辑
    const successItems = conversionList.value.filter(item => item.status === 'success')
    for (const item of successItems) {
      try {
        await libraryStore.addAsset({
          name: getFileName(item.outputPath),
          path: item.outputPath,
          type: outputFormat.value,
          size: await getFileSize(item.outputPath),
          dimensions: item.dimensions
        })
      } catch (error) {
        console.error('添加到素材库失败:', error)
      }
    }
  }
}

const getFileSize = async (filePath: string) => {
  try {
    const stats = await window.electronAPI.getFileStats(filePath)
    return stats.size
  } catch (error) {
    return 0
  }
}

// 上传相关
const handleFileChange = (file: any) => {
  uploadFiles.value.push(file)
}

const confirmBatchAdd = () => {
  const files = uploadFiles.value.map(file => file.raw?.path || file.name)
  addFilesToList(files)
  showBatchAddDialog.value = false
  uploadFiles.value = []
}
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.format-converter {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.converter-toolbar {
  padding: 12px 24px;
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
      font-size: 18px;
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.converter-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.settings-panel {
  width: 320px;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
  
  .settings-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
    
    .preset-list {
      max-height: 200px;
      overflow-y: auto;
      
      .preset-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 8px 12px;
        border-radius: 6px;
        cursor: pointer;
        transition: all 0.3s ease;
        margin-bottom: 4px;
        
        &.active {
          background: var(--el-color-primary-light-9);
          color: var(--el-color-primary);
        }
        
        &:hover {
          background: var(--el-fill-color-light);
        }
        
        .preset-name {
          font-weight: 500;
        }
        
        .preset-format {
          font-size: 12px;
          color: var(--el-text-color-secondary);
          background: var(--el-fill-color-light);
          padding: 2px 6px;
          border-radius: 3px;
        }
      }
    }
    
    .custom-size {
      display: flex;
      align-items: center;
      gap: 8px;
      
      span {
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.conversion-list-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
  
  .list-header {
    padding: 16px 24px;
    background: var(--el-bg-color);
    border-bottom: 1px solid var(--el-border-color-light);
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    span {
      font-weight: 500;
      color: var(--el-text-color-primary);
    }
    
    .header-actions {
      display: flex;
      gap: 8px;
    }
  }
  
  .conversion-list {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    
    .conversion-item {
      display: flex;
      align-items: center;
      padding: 12px 16px;
      border-radius: 8px;
      border: 1px solid var(--el-border-color-light);
      margin-bottom: 8px;
      cursor: pointer;
      transition: all 0.3s ease;
      
      &.selected {
        border-color: var(--el-color-primary);
        background: var(--el-color-primary-light-9);
      }
      
      &.converting {
        border-color: var(--el-color-warning);
        background: var(--el-color-warning-light-9);
      }
      
      &.success {
        border-color: var(--el-color-success);
        background: var(--el-color-success-light-9);
      }
      
      &.error {
        border-color: var(--el-color-error);
        background: var(--el-color-error-light-9);
      }
      
      .item-preview {
        width: 48px;
        height: 48px;
        border-radius: 4px;
        overflow: hidden;
        margin-right: 12px;
        flex-shrink: 0;
        
        img {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }
        
        .file-icon {
          width: 100%;
          height: 100%;
          display: flex;
          align-items: center;
          justify-content: center;
          background: var(--el-fill-color-light);
          color: var(--el-text-color-secondary);
          
          .el-icon {
            font-size: 24px;
          }
        }
      }
      
      .item-info {
        flex: 1;
        
        .file-name {
          font-weight: 500;
          color: var(--el-text-color-primary);
          margin-bottom: 4px;
          word-break: break-all;
        }
        
        .file-details {
          display: flex;
          gap: 12px;
          font-size: 12px;
          color: var(--el-text-color-secondary);
          
          .original-format {
            background: var(--el-fill-color-light);
            padding: 2px 6px;
            border-radius: 3px;
          }
        }
        
        .conversion-progress {
          margin-top: 8px;
          display: flex;
          align-items: center;
          gap: 8px;
          
          .el-progress {
            flex: 1;
          }
          
          .progress-text {
            font-size: 12px;
            color: var(--el-text-color-secondary);
            min-width: 30px;
          }
        }
        
        .conversion-result {
          display: flex;
          align-items: center;
          gap: 4px;
          margin-top: 4px;
          font-size: 12px;
          
          .el-icon {
            font-size: 14px;
          }
        }
      }
      
      .item-actions {
        display: flex;
        gap: 4px;
        opacity: 0;
        transition: opacity 0.3s ease;
      }
      
      &:hover .item-actions {
        opacity: 1;
      }
    }
    
    .empty-state {
      text-align: center;
      padding: 60px 20px;
      color: var(--el-text-color-secondary);
      
      .empty-icon {
        font-size: 64px;
        margin-bottom: 16px;
        opacity: 0.5;
      }
      
      .empty-hint {
        font-size: 14px;
        margin-top: 8px;
      }
    }
  }
  
  .conversion-stats {
    padding: 16px 24px;
    background: var(--el-bg-color);
    border-top: 1px solid var(--el-border-color-light);
    display: flex;
    justify-content: space-around;
    
    .stat-item {
      text-align: center;
      
      span {
        font-size: 14px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

.preview-panel {
  width: 320px;
  border-left: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  
  .preview-section {
    padding: 20px;
    border-bottom: 1px solid var(--el-border-color-light);
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
    
    .preview-content {
      .preview-image {
        position: relative;
        border-radius: 8px;
        overflow: hidden;
        margin-bottom: 16px;
        
        img {
          width: 100%;
          height: auto;
          display: block;
        }
        
        .preview-overlay {
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 12px;
          
          .preview-info {
            font-size: 12px;
            
            span {
              display: block;
              margin-bottom: 2px;
            }
          }
        }
      }
      
      .preview-file {
        text-align: center;
        padding: 40px 20px;
        
        .file-icon-large {
          font-size: 64px;
          color: var(--el-text-color-secondary);
          margin-bottom: 16px;
        }
        
        p {
          margin: 0;
          color: var(--el-text-color-primary);
          word-break: break-all;
        }
      }
      
      .preview-settings {
        h5 {
          margin: 0 0 12px;
          color: var(--el-text-color-primary);
          font-size: 14px;
        }
      }
    }
    
    .preview-empty {
      text-align: center;
      padding: 40px 20px;
      color: var(--el-text-color-secondary);
      
      .empty-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
      }
    }
    
    .conversion-log {
      max-height: 200px;
      overflow-y: auto;
      
      .log-entry {
        padding: 8px 12px;
        border-radius: 4px;
        margin-bottom: 4px;
        font-size: 12px;
        
        &.info {
          background: var(--el-color-info-light-9);
          color: var(--el-color-info);
        }
        
        &.success {
          background: var(--el-color-success-light-9);
          color: var(--el-color-success);
        }
        
        &.error {
          background: var(--el-color-error-light-9);
          color: var(--el-color-error);
        }
        
        .log-time {
          font-weight: 500;
          margin-right: 8px;
        }
      }
      
      .log-empty {
        text-align: center;
        padding: 20px;
        color: var(--el-text-color-placeholder);
      }
    }
  }
}

.progress-dialog {
  .progress-details {
    margin: 16px 0;
    
    p {
      margin: 8px 0;
      color: var(--el-text-color-secondary);
    }
  }
  
  .progress-actions {
    display: flex;
    justify-content: center;
    gap: 12px;
    margin-top: 20px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .settings-panel,
  .preview-panel {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .converter-content {
    flex-direction: column;
  }
  
  .settings-panel {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
    max-height: 300px;
    
    .settings-section {
      display: inline-block;
      width: 300px;
      vertical-align: top;
      margin-right: 20px;
      margin-bottom: 0;
    }
  }
  
  .preview-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--el-border-color-light);
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .converter-toolbar {
    padding: 8px 16px;
    flex-wrap: wrap;
    gap: 8px;
    
    .toolbar-left {
      order: 1;
      flex: 1;
    }
    
    .toolbar-right {
      order: 2;
      flex: 100%;
      justify-content: flex-end;
      margin-top: 8px;
    }
  }
  
  .conversion-list-panel {
    .list-header {
      padding: 12px 16px;
      flex-direction: column;
      gap: 8px;
      align-items: flex-start;
      
      .header-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }
    
    .conversion-stats {
      flex-wrap: wrap;
      gap: 8px;
      
      .stat-item {
        flex: 1;
        min-width: 80px;
      }
    }
  }
}

// 动画效果
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(100%);
}

// 加载状态
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
</style>