<template>
  <div class="asset-editor">
    <!-- 编辑工具栏 -->
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button @click="$emit('close')" text>
          <el-icon><ArrowLeft /></el-icon>
          返回
        </el-button>
        <h2>{{ currentAsset?.name || '素材编辑' }}</h2>
      </div>
      
      <div class="toolbar-center">
        <el-button-group>
          <el-button
            :type="activeTool === 'select' ? 'primary' : ''"
            @click="setActiveTool('select')"
          >
            <el-icon><Select /></el-icon>
            选择
          </el-button>
          <el-button
            :type="activeTool === 'crop' ? 'primary' : ''"
            @click="setActiveTool('crop')"
          >
            <el-icon><Crop /></el-icon>
            裁剪
          </el-button>
          <el-button
            :type="activeTool === 'rotate' ? 'primary' : ''"
            @click="setActiveTool('rotate')"
          >
            <el-icon><Refresh /></el-icon>
            旋转
          </el-button>
          <el-button
            :type="activeTool === 'text' ? 'primary' : ''"
            @click="setActiveTool('text')"
          >
            <el-icon><EditPen /></el-icon>
            文字
          </el-button>
          <el-button
            :type="activeTool === 'draw' ? 'primary' : ''"
            @click="setActiveTool('draw')"
          >
            <el-icon><Brush /></el-icon>
            画笔
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <el-button @click="undo" :disabled="!canUndo">
          <el-icon><RefreshLeft /></el-icon>
          撤销
        </el-button>
        <el-button @click="redo" :disabled="!canRedo">
          <el-icon><RefreshRight /></el-icon>
          重做
        </el-button>
        <el-button type="primary" @click="saveChanges">
          <el-icon><Check /></el-icon>
          保存
        </el-button>
        <el-button @click="exportAsset">
          <el-icon><Download /></el-icon>
          导出
        </el-button>
      </div>
    </div>

    <!-- 编辑区域 -->
    <div class="editor-content">
      <!-- 左侧工具面板 -->
      <div class="tool-panel">
        <!-- 裁剪工具 -->
        <div v-if="activeTool === 'crop'" class="tool-section">
          <h4>裁剪设置</h4>
          <el-form label-width="80px">
            <el-form-item label="比例：">
              <el-select v-model="cropRatio" placeholder="选择比例">
                <el-option label="自由" value="free" />
                <el-option label="1:1" value="1:1" />
                <el-option label="4:3" value="4:3" />
                <el-option label="16:9" value="16:9" />
                <el-option label="3:2" value="3:2" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="cropRatio === 'custom'" label="自定义：">
              <div class="custom-ratio">
                <el-input-number v-model="customRatio.width" :min="1" />
                <span>:</span>
                <el-input-number v-model="customRatio.height" :min="1" />
              </div>
            </el-form-item>
            
            <el-form-item label="旋转：">
              <el-slider
                v-model="cropRotation"
                :min="-180"
                :max="180"
                show-input
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="applyCrop" style="width: 100%">
                应用裁剪
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 旋转工具 -->
        <div v-if="activeTool === 'rotate'" class="tool-section">
          <h4>旋转设置</h4>
          <div class="rotation-presets">
            <el-button
              v-for="angle in [90, 180, 270]"
              :key="angle"
              @click="rotateByAngle(angle)"
            >
              旋转 {{ angle }}°
            </el-button>
          </div>
          
          <el-form label-width="80px">
            <el-form-item label="角度：">
              <el-slider
                v-model="rotationAngle"
                :min="-180"
                :max="180"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="水平翻转：">
              <el-switch v-model="flipHorizontal" />
            </el-form-item>
            
            <el-form-item label="垂直翻转：">
              <el-switch v-model="flipVertical" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="applyRotation" style="width: 100%">
                应用旋转
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 文字工具 -->
        <div v-if="activeTool === 'text'" class="tool-section">
          <h4>文字设置</h4>
          <el-form label-width="80px">
            <el-form-item label="内容：">
              <el-input
                v-model="textContent"
                type="textarea"
                :rows="3"
                placeholder="输入文字内容"
              />
            </el-form-item>
            
            <el-form-item label="字体：">
              <el-select v-model="textFont" placeholder="选择字体">
                <el-option
                  v-for="font in availableFonts"
                  :key="font"
                  :label="font"
                  :value="font"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="大小：">
              <el-slider
                v-model="textSize"
                :min="12"
                :max="72"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="颜色：">
              <el-color-picker v-model="textColor" />
            </el-form-item>
            
            <el-form-item label="样式：">
              <el-checkbox-group v-model="textStyles">
                <el-checkbox label="bold">粗体</el-checkbox>
                <el-checkbox label="italic">斜体</el-checkbox>
                <el-checkbox label="underline">下划线</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            
            <el-form-item label="对齐：">
              <el-radio-group v-model="textAlign">
                <el-radio label="left">左对齐</el-radio>
                <el-radio label="center">居中</el-radio>
                <el-radio label="right">右对齐</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="addText" style="width: 100%">
                添加文字
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 画笔工具 -->
        <div v-if="activeTool === 'draw'" class="tool-section">
          <h4>画笔设置</h4>
          <el-form label-width="80px">
            <el-form-item label="画笔：">
              <el-radio-group v-model="brushType">
                <el-radio label="pencil">铅笔</el-radio>
                <el-radio label="brush">画笔</el-radio>
                <el-radio label="eraser">橡皮擦</el-radio>
              </el-radio-group>
            </el-form-item>
            
            <el-form-item label="大小：">
              <el-slider
                v-model="brushSize"
                :min="1"
                :max="50"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="颜色：">
              <el-color-picker v-model="brushColor" />
            </el-form-item>
            
            <el-form-item label="透明度：">
              <el-slider
                v-model="brushOpacity"
                :min="0.1"
                :max="1"
                :step="0.1"
                show-input
              />
            </el-form-item>
            
            <el-form-item>
              <el-button @click="clearDrawing" style="width: 100%">
                清除绘画
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 调整工具 -->
        <div class="tool-section">
          <h4>图像调整</h4>
          <el-form label-width="80px">
            <el-form-item label="亮度：">
              <el-slider
                v-model="adjustments.brightness"
                :min="-100"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="对比度：">
              <el-slider
                v-model="adjustments.contrast"
                :min="-100"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="饱和度：">
              <el-slider
                v-model="adjustments.saturation"
                :min="-100"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="色相：">
              <el-slider
                v-model="adjustments.hue"
                :min="-180"
                :max="180"
                show-input
              />
            </el-form-item>
            
            <el-form-item>
              <el-button @click="resetAdjustments" style="width: 100%">
                重置调整
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 滤镜工具 -->
        <div class="tool-section">
          <h4>滤镜效果</h4>
          <div class="filter-presets">
            <div
              v-for="filter in filterPresets"
              :key="filter.name"
              class="filter-preset"
              :class="{ active: activeFilter === filter.name }"
              @click="applyFilter(filter)"
            >
              <div class="filter-preview" :style="{ filter: filter.css }" />
              <span>{{ filter.label }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央画布区域 -->
      <div class="canvas-container">
        <div class="canvas-wrapper">
          <canvas
            ref="canvas"
            :width="canvasSize.width"
            :height="canvasSize.height"
            @mousedown="startDrawing"
            @mousemove="draw"
            @mouseup="stopDrawing"
            @mouseleave="stopDrawing"
          />
          
          <!-- 缩放控制 -->
          <div class="zoom-controls">
            <el-button
              circle
              size="small"
              @click="zoomOut"
              :disabled="zoomLevel <= 0.1"
            >
              <el-icon><Minus /></el-icon>
            </el-button>
            <span class="zoom-level">{{ Math.round(zoomLevel * 100) }}%</span>
            <el-button
              circle
              size="small"
              @click="zoomIn"
              :disabled="zoomLevel >= 5"
            >
              <el-icon><Plus /></el-icon>
            </el-button>
            <el-button
              circle
              size="small"
              @click="resetZoom"
            >
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </div>
        </div>
        
        <!-- 画布信息 -->
        <div class="canvas-info">
          <span>尺寸: {{ originalSize.width }} × {{ originalSize.height }}</span>
          <span>格式: {{ currentAsset?.type || '未知' }}</span>
          <span>大小: {{ formatFileSize(currentAsset?.size || 0) }}</span>
        </div>
      </div>

      <!-- 右侧属性面板 -->
      <div class="property-panel">
        <div class="property-section">
          <h4>素材属性</h4>
          <el-form label-width="80px">
            <el-form-item label="文件名：">
              <el-input v-model="assetName" />
            </el-form-item>
            
            <el-form-item label="描述：">
              <el-input
                v-model="assetDescription"
                type="textarea"
                :rows="3"
                placeholder="输入素材描述"
              />
            </el-form-item>
            
            <el-form-item label="标签：">
              <el-select
                v-model="assetTags"
                multiple
                filterable
                allow-create
                placeholder="添加标签"
                style="width: 100%"
              >
                <el-option
                  v-for="tag in availableTags"
                  :key="tag"
                  :label="tag"
                  :value="tag"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="评分：">
              <el-rate
                v-model="assetRating"
                show-score
                text-color="#ff9900"
              />
            </el-form-item>
          </el-form>
        </div>

        <div class="property-section">
          <h4>导出设置</h4>
          <el-form label-width="80px">
            <el-form-item label="格式：">
              <el-select v-model="exportFormat">
                <el-option label="原格式" value="original" />
                <el-option label="JPEG" value="jpeg" />
                <el-option label="PNG" value="png" />
                <el-option label="WEBP" value="webp" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="exportFormat !== 'png'" label="质量：">
              <el-slider
                v-model="exportQuality"
                :min="1"
                :max="100"
                show-input
              />
            </el-form-item>
            
            <el-form-item label="尺寸：">
              <el-select v-model="exportSize">
                <el-option label="原尺寸" value="original" />
                <el-option label="自定义" value="custom" />
                <el-option label="小 (800px)" value="small" />
                <el-option label="中 (1200px)" value="medium" />
                <el-option label="大 (1920px)" value="large" />
              </el-select>
            </el-form-item>
            
            <el-form-item v-if="exportSize === 'custom'" label="自定义：">
              <div class="custom-size">
                <el-input-number v-model="customSize.width" :min="1" />
                <span>×</span>
                <el-input-number v-model="customSize.height" :min="1" />
              </div>
            </el-form-item>
            
            <el-form-item>
              <el-checkbox v-model="preserveAspectRatio">保持宽高比</el-checkbox>
            </el-form-item>
          </el-form>
        </div>

        <div class="property-section">
          <h4>历史记录</h4>
          <div class="history-list">
            <div
              v-for="(action, index) in history"
              :key="index"
              class="history-item"
              :class="{ active: historyIndex === index }"
              @click="jumpToHistory(index)"
            >
              <span>{{ action.description }}</span>
              <span class="history-time">{{ action.timestamp }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 导出对话框 -->
    <el-dialog
      v-model="showExportDialog"
      title="导出素材"
      width="500px"
    >
      <el-form label-width="100px">
        <el-form-item label="导出路径：">
          <el-input v-model="exportPath" readonly>
            <template #append>
              <el-button @click="chooseExportPath">选择</el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="文件名：">
          <el-input v-model="exportFileName" />
        </el-form-item>
        
        <el-form-item label="覆盖确认：">
          <el-switch v-model="overwriteConfirm" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showExportDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmExport">导出</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useLibraryStore } from '@/stores/library'
import {
  ArrowLeft,
  Select,
  Crop,
  Refresh,
  EditPen,
  Brush,
  RefreshLeft,
  RefreshRight,
  Check,
  Download,
  Minus,
  Plus,
  FullScreen
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  asset: any
}>()

const emit = defineEmits(['close', 'saved'])

const libraryStore = useLibraryStore()

// 编辑状态
const currentAsset = ref(props.asset)
const activeTool = ref('select')
const canvas = ref<HTMLCanvasElement>()
const ctx = ref<CanvasRenderingContext2D>()

// 画布状态
const canvasSize = reactive({ width: 800, height: 600 })
const originalSize = reactive({ width: 0, height: 0 })
const zoomLevel = ref(1)
const isDrawing = ref(false)

// 编辑历史
const history = ref<any[]>([])
const historyIndex = ref(-1)
const canUndo = computed(() => historyIndex.value > 0)
const canRedo = computed(() => historyIndex.value < history.value.length - 1)

// 裁剪工具
const cropRatio = ref('free')
const cropRotation = ref(0)
const customRatio = reactive({ width: 1, height: 1 })

// 旋转工具
const rotationAngle = ref(0)
const flipHorizontal = ref(false)
const flipVertical = ref(false)

// 文字工具
const textContent = ref('')
const textFont = ref('Arial')
const textSize = ref(24)
const textColor = ref('#000000')
const textStyles = ref<string[]>([])
const textAlign = ref('left')
const availableFonts = ref([
  'Arial', 'Helvetica', 'Times New Roman', 'Georgia', 
  'Verdana', 'Tahoma', 'Courier New', 'Impact'
])

// 画笔工具
const brushType = ref('pencil')
const brushSize = ref(5)
const brushColor = ref('#000000')
const brushOpacity = ref(1)

// 调整工具
const adjustments = reactive({
  brightness: 0,
  contrast: 0,
  saturation: 0,
  hue: 0
})

// 滤镜工具
const activeFilter = ref('')
const filterPresets = ref([
  { name: 'none', label: '无', css: 'none' },
  { name: 'grayscale', label: '灰度', css: 'grayscale(100%)' },
  { name: 'sepia', label: '复古', css: 'sepia(100%)' },
  { name: 'blur', label: '模糊', css: 'blur(2px)' },
  { name: 'brightness', label: '明亮', css: 'brightness(1.2)' },
  { name: 'contrast', label: '对比', css: 'contrast(1.5)' }
])

// 属性编辑
const assetName = ref('')
const assetDescription = ref('')
const assetTags = ref<string[]>([])
const assetRating = ref(0)
const availableTags = ref<string[]>([])

// 导出设置
const showExportDialog = ref(false)
const exportFormat = ref('original')
const exportQuality = ref(90)
const exportSize = ref('original')
const customSize = reactive({ width: 0, height: 0 })
const preserveAspectRatio = ref(true)
const exportPath = ref('')
const exportFileName = ref('')
const overwriteConfirm = ref(true)

// 初始化
onMounted(() => {
  initializeCanvas()
  loadAssetData()
  saveToHistory('初始化')
})

// 监听素材变化
watch(() => props.asset, (newAsset) => {
  currentAsset.value = newAsset
  loadAssetData()
  resetCanvas()
})

const initializeCanvas = () => {
  if (!canvas.value) return
  
  ctx.value = canvas.value.getContext('2d')!
  
  // 设置画布样式
  ctx.value.imageSmoothingEnabled = true
  ctx.value.imageSmoothingQuality = 'high'
}

const loadAssetData = () => {
  if (!currentAsset.value) return
  
  assetName.value = currentAsset.value.name
  assetDescription.value = currentAsset.value.description || ''
  assetTags.value = currentAsset.value.tags || []
  assetRating.value = currentAsset.value.rating || 0
  
  // 加载图片到画布
  const img = new Image()
  img.onload = () => {
    originalSize.width = img.width
    originalSize.height = img.height
    
    // 计算适合画布的尺寸
    const scale = Math.min(
      canvasSize.width / img.width,
      canvasSize.height / img.height
    )
    
    canvasSize.width = img.width * scale
    canvasSize.height = img.height * scale
    
    drawImageToCanvas(img)
  }
  img.src = currentAsset.value.thumbnail || currentAsset.value.path
}

const drawImageToCanvas = (img: HTMLImageElement) => {
  if (!ctx.value || !canvas.value) return
  
  ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)
  ctx.value.drawImage(img, 0, 0, canvasSize.width, canvasSize.height)
}

const resetCanvas = () => {
  loadAssetData()
  resetAdjustments()
  activeFilter.value = 'none'
  saveToHistory('重置画布')
}

// 工具操作
const setActiveTool = (tool: string) => {
  activeTool.value = tool
}

const applyCrop = () => {
  // 实现裁剪逻辑
  saveToHistory('应用裁剪')
  ElMessage.success('裁剪已应用')
}

const rotateByAngle = (angle: number) => {
  rotationAngle.value = angle
  applyRotation()
}

const applyRotation = () => {
  // 实现旋转逻辑
  saveToHistory('应用旋转')
  ElMessage.success('旋转已应用')
}

const addText = () => {
  if (!textContent.value.trim()) {
    ElMessage.warning('请输入文字内容')
    return
  }
  
  // 实现添加文字逻辑
  saveToHistory('添加文字')
  ElMessage.success('文字已添加')
}

const clearDrawing = () => {
  if (!ctx.value || !canvas.value) return
  
  ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height)
  drawImageToCanvas(new Image()) // 重新绘制原始图像
  saveToHistory('清除绘画')
}

// 绘画功能
const startDrawing = (event: MouseEvent) => {
  if (activeTool.value !== 'draw') return
  
  isDrawing.value = true
  // 开始绘画逻辑
}

const draw = (event: MouseEvent) => {
  if (!isDrawing.value || !ctx.value) return
  
  // 绘画逻辑
}

const stopDrawing = () => {
  isDrawing.value = false
}

// 调整功能
const resetAdjustments = () => {
  Object.assign(adjustments, {
    brightness: 0,
    contrast: 0,
    saturation: 0,
    hue: 0
  })
  
  saveToHistory('重置调整')
}

const applyFilter = (filter: any) => {
  activeFilter.value = filter.name
  // 应用滤镜逻辑
  saveToHistory(`应用滤镜: ${filter.label}`)
}

// 缩放功能
const zoomIn = () => {
  if (zoomLevel.value >= 5) return
  zoomLevel.value = Math.min(zoomLevel.value + 0.1, 5)
  updateCanvasScale()
}

const zoomOut = () => {
  if (zoomLevel.value <= 0.1) return
  zoomLevel.value = Math.max(zoomLevel.value - 0.1, 0.1)
  updateCanvasScale()
}

const resetZoom = () => {
  zoomLevel.value = 1
  updateCanvasScale()
}

const updateCanvasScale = () => {
  if (!canvas.value) return
  
  canvas.value.style.transform = `scale(${zoomLevel.value})`
  canvas.value.style.transformOrigin = 'center center'
}

// 历史记录功能
const saveToHistory = (description: string) => {
  const timestamp = new Date().toLocaleTimeString()
  
  // 如果当前不是最新状态，删除后面的历史
  if (historyIndex.value < history.value.length - 1) {
    history.value = history.value.slice(0, historyIndex.value + 1)
  }
  
  history.value.push({
    description,
    timestamp,
    canvasState: canvas.value?.toDataURL()
  })
  
  historyIndex.value = history.value.length - 1
}

const undo = () => {
  if (historyIndex.value <= 0) return
  
  historyIndex.value--
  restoreFromHistory()
}

const redo = () => {
  if (historyIndex.value >= history.value.length - 1) return
  
  historyIndex.value++
  restoreFromHistory()
}

const jumpToHistory = (index: number) => {
  historyIndex.value = index
  restoreFromHistory()
}

const restoreFromHistory = () => {
  const historyItem = history.value[historyIndex.value]
  if (!historyItem) return
  
  // 恢复画布状态
  const img = new Image()
  img.onload = () => {
    drawImageToCanvas(img)
  }
  img.src = historyItem.canvasState
}

// 保存功能
const saveChanges = async () => {
  try {
    // 保存编辑后的素材
    await libraryStore.updateAsset(currentAsset.value.id, {
      name: assetName.value,
      description: assetDescription.value,
      tags: assetTags.value,
      rating: assetRating.value
    })
    
    ElMessage.success('素材已保存')
    emit('saved', currentAsset.value)
  } catch (error) {
    console.error('保存失败:', error)
    ElMessage.error('保存失败')
  }
}

// 导出功能
const exportAsset = () => {
  showExportDialog.value = true
  exportFileName.value = assetName.value
  exportPath.value = currentAsset.value.path
}

const chooseExportPath = async () => {
  try {
    const path = await window.electronAPI.showSaveDialog({
      defaultPath: exportFileName.value,
      filters: [
        { name: 'Images', extensions: ['jpg', 'png', 'webp'] }
      ]
    })
    
    if (path) {
      exportPath.value = path
    }
  } catch (error) {
    console.error('选择路径失败:', error)
  }
}

const confirmExport = async () => {
  try {
    // 实现导出逻辑
    await window.electronAPI.exportImage({
      canvas: canvas.value,
      format: exportFormat.value,
      quality: exportQuality.value / 100,
      path: exportPath.value
    })
    
    ElMessage.success('素材已导出')
    showExportDialog.value = false
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error('导出失败')
  }
}

// 工具函数
const formatFileSize = (bytes: number) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped lang="scss">
@use '@/styles/index.scss' as global;

.asset-editor {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.editor-toolbar {
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
  
  .toolbar-center {
    flex: 1;
    display: flex;
    justify-content: center;
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.editor-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.tool-panel {
  width: 300px;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
  
  .tool-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
    
    .rotation-presets {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 8px;
      margin-bottom: 16px;
    }
    
    .filter-presets {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      
      .filter-preset {
        text-align: center;
        cursor: pointer;
        padding: 8px;
        border-radius: 6px;
        border: 2px solid var(--el-border-color-light);
        transition: all 0.3s ease;
        
        &.active {
          border-color: var(--el-color-primary);
          background: var(--el-color-primary-light-9);
        }
        
        &:hover {
          border-color: var(--el-color-primary-light-3);
        }
        
        .filter-preview {
          width: 100%;
          height: 40px;
          background: linear-gradient(45deg, #666, #999);
          border-radius: 4px;
          margin-bottom: 8px;
        }
        
        span {
          font-size: 12px;
          color: var(--el-text-color-regular);
        }
      }
    }
    
    .custom-ratio,
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

.canvas-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--el-bg-color-page);
  position: relative;
  
  .canvas-wrapper {
    position: relative;
    border: 1px solid var(--el-border-color-light);
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
    overflow: hidden;
    
    canvas {
      display: block;
      cursor: crosshair;
      transition: transform 0.3s ease;
    }
    
    .zoom-controls {
      position: absolute;
      bottom: 16px;
      right: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
      background: rgba(255, 255, 255, 0.9);
      border-radius: 20px;
      padding: 8px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
      
      .zoom-level {
        font-size: 12px;
        color: var(--el-text-color-secondary);
        min-width: 40px;
        text-align: center;
      }
    }
  }
  
  .canvas-info {
    margin-top: 16px;
    display: flex;
    gap: 24px;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.property-panel {
  width: 300px;
  border-left: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
  
  .property-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
    
    .history-list {
      max-height: 200px;
      overflow-y: auto;
      
      .history-item {
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
        
        .history-time {
          font-size: 10px;
          color: var(--el-text-color-placeholder);
          display: block;
        }
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .tool-panel,
  .property-panel {
    width: 250px;
  }
}

@media (max-width: 992px) {
  .editor-content {
    flex-direction: column;
  }
  
  .tool-panel {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
    max-height: 200px;
    overflow-x: auto;
    
    .tool-section {
      display: inline-block;
      width: 200px;
      vertical-align: top;
      margin-right: 20px;
      margin-bottom: 0;
    }
  }
  
  .property-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--el-border-color-light);
    max-height: 200px;
  }
}

@media (max-width: 768px) {
  .editor-toolbar {
    padding: 8px 16px;
    flex-wrap: wrap;
    gap: 8px;
    
    .toolbar-left {
      order: 1;
      flex: 1;
    }
    
    .toolbar-center {
      order: 3;
      flex: 100%;
      justify-content: flex-start;
      margin-top: 8px;
    }
    
    .toolbar-right {
      order: 2;
    }
  }
  
  .canvas-container {
    .canvas-wrapper {
      .zoom-controls {
        bottom: 8px;
        right: 8px;
        
        .zoom-level {
          display: none;
        }
      }
    }
    
    .canvas-info {
      flex-direction: column;
      gap: 8px;
      text-align: center;
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

// 工具图标样式
.tool-icon {
  font-size: 16px;
  margin-right: 4px;
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

// 错误状态
.error-message {
  text-align: center;
  color: var(--el-color-error);
  padding: 40px;
  
  .error-icon {
    font-size: 48px;
    margin-bottom: 16px;
  }
}

// 空状态
.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--el-text-color-secondary);
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  .empty-text {
    font-size: 16px;
  }
}
</style>