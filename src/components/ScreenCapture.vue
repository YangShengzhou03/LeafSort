<template>
  <div class="screen-capture">
    <!-- 控制栏 -->
    <div class="control-bar">
      <div class="capture-mode">
        <el-button-group>
          <el-button 
            type="primary" 
            @click="setCaptureMode('fullscreen')"
            :class="{ active: captureMode === 'fullscreen' }"
          >
            <el-icon><FullScreen /></el-icon>
            全屏
          </el-button>
          <el-button 
            @click="setCaptureMode('window')"
            :class="{ active: captureMode === 'window' }"
          >
            <el-icon><Monitor /></el-icon>
            窗口
          </el-button>
          <el-button 
            @click="setCaptureMode('area')"
            :class="{ active: captureMode === 'area' }"
          >
            <el-icon><Crop /></el-icon>
            区域
          </el-button>
        </el-button-group>
      </div>
      
      <div class="capture-options">
        <el-button @click="showSettings = true">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
        
        <el-button @click="startCountdown" :disabled="isCapturing">
          <el-icon><Timer /></el-icon>
          倒计时
        </el-button>
        
        <el-button @click="toggleRecording" :type="isRecording ? 'danger' : 'primary'">
          <el-icon><VideoCamera v-if="!isRecording" /><VideoPause v-else /></el-icon>
          {{ isRecording ? '停止录制' : '开始录制' }}
        </el-button>
        
        <el-button @click="closeCapture" type="danger">
          <el-icon><Close /></el-icon>
          关闭
        </el-button>
      </div>
    </div>

    <!-- 截图预览区域 -->
    <div class="preview-area">
      <!-- 全屏截图预览 -->
      <div v-if="captureMode === 'fullscreen'" class="fullscreen-preview">
        <div class="preview-content">
          <div class="screen-grid">
            <div 
              v-for="screen in availableScreens" 
              :key="screen.id"
              class="screen-item"
              :class="{ active: selectedScreen === screen.id }"
              @click="selectScreen(screen.id)"
            >
              <div class="screen-thumbnail">
                <img :src="screen.thumbnail" :alt="`屏幕 ${screen.id + 1}`" />
                <div class="screen-overlay">
                  <span>屏幕 {{ screen.id + 1 }}</span>
                </div>
              </div>
              <div class="screen-info">
                <span>{{ screen.width }} × {{ screen.height }}</span>
              </div>
            </div>
          </div>
          
          <div class="capture-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="captureFullscreen"
              :loading="isCapturing"
            >
              <el-icon><Camera /></el-icon>
              截图当前屏幕
            </el-button>
            
            <el-button 
              @click="captureAllScreens"
              :loading="isCapturing"
              :disabled="availableScreens.length <= 1"
            >
              <el-icon><Collection /></el-icon>
              截图所有屏幕
            </el-button>
          </div>
        </div>
      </div>

      <!-- 窗口截图预览 -->
      <div v-if="captureMode === 'window'" class="window-preview">
        <div class="preview-content">
          <div class="window-list">
            <div 
              v-for="window in availableWindows" 
              :key="window.id"
              class="window-item"
              :class="{ active: selectedWindow === window.id }"
              @click="selectWindow(window.id)"
            >
              <div class="window-thumbnail">
                <img :src="window.thumbnail" :alt="window.title" />
              </div>
              <div class="window-info">
                <div class="window-title">{{ window.title }}</div>
                <div class="window-details">
                  <span>{{ window.appName }}</span>
                  <span>{{ window.width }} × {{ window.height }}</span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="availableWindows.length === 0" class="empty-windows">
            <el-icon size="64" color="var(--el-text-color-placeholder)">
              <Monitor />
            </el-icon>
            <p>未检测到可用窗口</p>
            <el-button @click="refreshWindows">刷新窗口列表</el-button>
          </div>
          
          <div class="capture-actions">
            <el-button 
              type="primary" 
              size="large" 
              @click="captureWindow"
              :loading="isCapturing"
              :disabled="!selectedWindow"
            >
              <el-icon><Camera /></el-icon>
              截图选中窗口
            </el-button>
          </div>
        </div>
      </div>

      <!-- 区域截图界面 -->
      <div v-if="captureMode === 'area'" class="area-capture">
        <div class="area-instructions">
          <h3>区域截图模式</h3>
          <p>使用鼠标拖拽选择要截图的区域，按 ESC 取消选择</p>
          
          <div class="shortcut-list">
            <div class="shortcut-item">
              <kbd>鼠标拖拽</kbd>
              <span>选择截图区域</span>
            </div>
            <div class="shortcut-item">
              <kbd>ESC</kbd>
              <span>取消选择</span>
            </div>
            <div class="shortcut-item">
              <kbd>空格键</kbd>
              <span>切换屏幕</span>
            </div>
            <div class="shortcut-item">
              <kbd>Enter</kbd>
              <span>确认截图</span>
            </div>
          </div>
        </div>
        
        <div class="area-preview">
          <canvas 
            ref="areaCanvas" 
            class="area-canvas"
            @mousedown="startAreaSelection"
            @mousemove="updateAreaSelection"
            @mouseup="endAreaSelection"
          ></canvas>
          
          <!-- 选择区域信息 -->
          <div v-if="areaSelection.active" class="area-info">
            <div class="area-dimensions">
              {{ areaSelection.width }} × {{ areaSelection.height }}
            </div>
            <div class="area-actions">
              <el-button size="small" @click="captureArea">截图</el-button>
              <el-button size="small" @click="cancelAreaSelection">取消</el-button>
            </div>
          </div>
        </div>
      </div>

      <!-- 倒计时显示 -->
      <div v-if="countdown > 0" class="countdown-overlay">
        <div class="countdown-content">
          <div class="countdown-number">{{ countdown }}</div>
          <div class="countdown-text">截图倒计时</div>
        </div>
      </div>
    </div>

    <!-- 截图结果 -->
    <div class="capture-results" v-if="capturedImages.length > 0">
      <div class="results-header">
        <span>截图结果 ({{ capturedImages.length }})</span>
        <div class="results-actions">
          <el-button size="small" @click="clearAll">清空</el-button>
          <el-button size="small" type="primary" @click="importAll">导入全部</el-button>
        </div>
      </div>
      
      <div class="results-grid">
        <div
          v-for="image in capturedImages"
          :key="image.id"
          class="capture-item"
          :class="{ selected: selectedImages.includes(image.id) }"
          @click="toggleImageSelection(image)"
        >
          <div class="item-thumbnail">
            <img :src="image.data" :alt="image.title" />
            <div class="item-overlay">
              <el-button size="small" circle @click.stop="previewImage(image)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button size="small" circle @click.stop="copyImage(image)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button size="small" circle @click.stop="removeImage(image.id)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
          </div>
          
          <div class="item-info">
            <div class="item-title">{{ image.title }}</div>
            <div class="item-details">
              <span>{{ image.width }} × {{ image.height }}</span>
              <span>{{ formatFileSize(image.size) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 截图设置 -->
    <el-drawer
      v-model="showSettings"
      title="截图设置"
      direction="rtl"
      size="300px"
    >
      <div class="capture-settings">
        <el-form label-width="80px">
          <el-form-item label="图片格式">
            <el-select v-model="settings.format">
              <el-option label="PNG" value="png"></el-option>
              <el-option label="JPG" value="jpg"></el-option>
              <el-option label="WebP" value="webp"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="图片质量">
            <el-slider
              v-model="settings.quality"
              :min="1"
              :max="100"
              show-stops
            ></el-slider>
          </el-form-item>
          
          <el-form-item label="自动保存">
            <el-switch v-model="settings.autoSave" />
          </el-form-item>
          
          <el-form-item label="添加水印">
            <el-switch v-model="settings.addWatermark" />
          </el-form-item>
          
          <el-form-item label="水印文字">
            <el-input 
              v-model="settings.watermarkText" 
              placeholder="请输入水印文字"
              :disabled="!settings.addWatermark"
            />
          </el-form-item>
          
          <el-form-item label="包含光标">
            <el-switch v-model="settings.includeCursor" />
          </el-form-item>
          
          <el-form-item label="延时截图">
            <el-input-number
              v-model="settings.delaySeconds"
              :min="0"
              :max="60"
              controls-position="right"
            />
            <template #label>
              <span>延时截图 (秒)</span>
            </template>
          </el-form-item>
          
          <el-form-item label="默认标签">
            <el-input v-model="settings.defaultTags" placeholder="截图,屏幕截图" />
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'

// 图标导入
import {
  FullScreen,
  Monitor,
  Crop,
  Setting,
  Timer,
  VideoCamera,
  VideoPause,
  Close,
  Camera,
  Collection,
  View,
  CopyDocument,
  Delete
} from '@element-plus/icons-vue'

const emit = defineEmits(['close'])
const libraryStore = useLibraryStore()

// 响应式数据
const captureMode = ref<'fullscreen' | 'window' | 'area'>('fullscreen')
const showSettings = ref(false)
const isCapturing = ref(false)
const isRecording = ref(false)
const countdown = ref(0)

// 屏幕相关
const availableScreens = ref<any[]>([])
const selectedScreen = ref<number>(0)

// 窗口相关
const availableWindows = ref<any[]>([])
const selectedWindow = ref<string>('')

// 区域截图相关
const areaCanvas = ref<HTMLCanvasElement>()
const areaSelection = reactive({
  active: false,
  startX: 0,
  startY: 0,
  endX: 0,
  endY: 0,
  width: 0,
  height: 0
})

// 截图设置
const settings = reactive({
  format: 'png' as 'png' | 'jpg' | 'webp',
  quality: 90,
  autoSave: true,
  addWatermark: false,
  watermarkText: 'LeafView',
  includeCursor: false,
  delaySeconds: 0,
  defaultTags: '截图,屏幕截图'
})

// 截图结果
const capturedImages = ref<any[]>([])
const selectedImages = ref<string[]>([])

// 方法
const setCaptureMode = (mode: 'fullscreen' | 'window' | 'area') => {
  captureMode.value = mode
  
  if (mode === 'fullscreen') {
    loadAvailableScreens()
  } else if (mode === 'window') {
    loadAvailableWindows()
  } else if (mode === 'area') {
    initializeAreaCanvas()
  }
}

const loadAvailableScreens = async () => {
  try {
    const screens = await window.electronAPI.getAvailableScreens()
    availableScreens.value = screens.map((screen: any, index: number) => ({
      ...screen,
      id: index,
      thumbnail: generateScreenThumbnail(screen)
    }))
    
    if (availableScreens.value.length > 0) {
      selectedScreen.value = availableScreens.value[0].id
    }
  } catch (error) {
    console.error('获取屏幕信息失败:', error)
    ElMessage.error('获取屏幕信息失败')
  }
}

const loadAvailableWindows = async () => {
  try {
    const windows = await window.electronAPI.getAvailableWindows()
    availableWindows.value = windows.map((win: any) => ({
      ...win,
      thumbnail: generateWindowThumbnail(win)
    }))
  } catch (error) {
    console.error('获取窗口信息失败:', error)
    ElMessage.error('获取窗口信息失败')
  }
}

const refreshWindows = () => {
  loadAvailableWindows()
}

const selectScreen = (screenId: number) => {
  selectedScreen.value = screenId
}

const selectWindow = (windowId: string) => {
  selectedWindow.value = windowId
}

const generateScreenThumbnail = (screen: any) => {
  // 生成屏幕缩略图（实际应用中应该从Electron获取）
  return `data:image/svg+xml;base64,${btoa(`
    <svg width="${screen.width / 10}" height="${screen.height / 10}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f0f0f0"/>
      <text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="12" fill="#666">
        屏幕 ${screen.id + 1}
      </text>
    </svg>
  `)}`
}

const generateWindowThumbnail = (window: any) => {
  // 生成窗口缩略图（实际应用中应该从Electron获取）
  return `data:image/svg+xml;base64,${btoa(`
    <svg width="${window.width / 10}" height="${window.height / 10}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#e8f4fd"/>
      <rect width="100%" height="20" fill="#409eff"/>
      <text x="10" y="13" font-size="10" fill="white">${window.title}</text>
    </svg>
  `)}`
}

const startCountdown = () => {
  if (settings.delaySeconds <= 0) {
    ElMessage.warning('请先设置延时时间')
    showSettings.value = true
    return
  }
  
  countdown.value = settings.delaySeconds
  
  const timer = setInterval(() => {
    countdown.value--
    
    if (countdown.value <= 0) {
      clearInterval(timer)
      performCapture()
    }
  }, 1000)
}

const performCapture = async () => {
  isCapturing.value = true
  
  try {
    let captureResult
    
    switch (captureMode.value) {
      case 'fullscreen':
        captureResult = await captureFullscreen()
        break
      case 'window':
        captureResult = await captureWindow()
        break
      case 'area':
        captureResult = await captureArea()
        break
    }
    
    if (captureResult) {
      addCapturedImage(captureResult)
      ElMessage.success('截图成功')
    }
  } catch (error) {
    console.error('截图失败:', error)
    ElMessage.error('截图失败')
  } finally {
    isCapturing.value = false
  }
}

const captureFullscreen = async () => {
  try {
    const screen = availableScreens.value.find(s => s.id === selectedScreen.value)
    if (!screen) throw new Error('未选择屏幕')
    
    const screenshot = await window.electronAPI.captureScreen(screen.id, settings)
    
    return {
      data: screenshot,
      title: `全屏截图_${Date.now()}`,
      width: screen.width,
      height: screen.height,
      size: screenshot.length // 近似大小
    }
  } catch (error) {
    throw error
  }
}

const captureAllScreens = async () => {
  try {
    const results = []
    
    for (const screen of availableScreens.value) {
      const screenshot = await window.electronAPI.captureScreen(screen.id, settings)
      results.push({
        data: screenshot,
        title: `屏幕${screen.id + 1}_${Date.now()}`,
        width: screen.width,
        height: screen.height,
        size: screenshot.length
      })
    }
    
    return results
  } catch (error) {
    throw error
  }
}

const captureWindow = async () => {
  try {
    const window = availableWindows.value.find(w => w.id === selectedWindow.value)
    if (!window) throw new Error('未选择窗口')
    
    const screenshot = await window.electronAPI.captureWindow(window.id, settings)
    
    return {
      data: screenshot,
      title: `${window.title}_${Date.now()}`,
      width: window.width,
      height: window.height,
      size: screenshot.length
    }
  } catch (error) {
    throw error
  }
}

const initializeAreaCanvas = async () => {
  await nextTick()
  
  if (!areaCanvas.value) return
  
  // 设置画布大小为屏幕大小
  const screen = availableScreens.value[selectedScreen.value]
  if (screen) {
    areaCanvas.value.width = screen.width / 4 // 缩小显示
    areaCanvas.value.height = screen.height / 4
    
    // 绘制屏幕背景
    const ctx = areaCanvas.value.getContext('2d')
    if (ctx) {
      ctx.fillStyle = '#f0f0f0'
      ctx.fillRect(0, 0, areaCanvas.value.width, areaCanvas.value.height)
      
      ctx.fillStyle = '#666'
      ctx.font = '16px Arial'
      ctx.fillText('拖拽选择截图区域', 10, 30)
    }
  }
}

const startAreaSelection = (event: MouseEvent) => {
  if (!areaCanvas.value) return
  
  const rect = areaCanvas.value.getBoundingClientRect()
  areaSelection.active = true
  areaSelection.startX = event.clientX - rect.left
  areaSelection.startY = event.clientY - rect.top
  areaSelection.endX = areaSelection.startX
  areaSelection.endY = areaSelection.startY
  
  updateAreaDisplay()
}

const updateAreaSelection = (event: MouseEvent) => {
  if (!areaSelection.active || !areaCanvas.value) return
  
  const rect = areaCanvas.value.getBoundingClientRect()
  areaSelection.endX = event.clientX - rect.left
  areaSelection.endY = event.clientY - rect.top
  
  updateAreaDisplay()
}

const endAreaSelection = () => {
  if (!areaSelection.active) return
  
  areaSelection.active = false
  areaSelection.width = Math.abs(areaSelection.endX - areaSelection.startX)
  areaSelection.height = Math.abs(areaSelection.endY - areaSelection.startY)
  
  // 只有选择区域足够大时才允许截图
  if (areaSelection.width > 10 && areaSelection.height > 10) {
    // 可以在这里自动截图或等待用户确认
  }
}

const updateAreaDisplay = () => {
  if (!areaCanvas.value) return
  
  const ctx = areaCanvas.value.getContext('2d')
  if (!ctx) return
  
  // 清除画布
  ctx.clearRect(0, 0, areaCanvas.value.width, areaCanvas.value.height)
  
  // 绘制背景
  ctx.fillStyle = '#f0f0f0'
  ctx.fillRect(0, 0, areaCanvas.value.width, areaCanvas.value.height)
  
  // 绘制选择区域
  if (areaSelection.active) {
    const x = Math.min(areaSelection.startX, areaSelection.endX)
    const y = Math.min(areaSelection.startY, areaSelection.endY)
    const width = Math.abs(areaSelection.endX - areaSelection.startX)
    const height = Math.abs(areaSelection.endY - areaSelection.startY)
    
    ctx.fillStyle = 'rgba(64, 158, 255, 0.3)'
    ctx.fillRect(x, y, width, height)
    
    ctx.strokeStyle = '#409eff'
    ctx.lineWidth = 2
    ctx.strokeRect(x, y, width, height)
    
    // 显示尺寸信息
    ctx.fillStyle = '#409eff'
    ctx.font = '12px Arial'
    ctx.fillText(`${width} × ${height}`, x + 5, y + 15)
  }
}

const captureArea = async () => {
  try {
    if (areaSelection.width <= 10 || areaSelection.height <= 10) {
      ElMessage.warning('请选择更大的区域')
      return
    }
    
    // 计算实际屏幕坐标（需要根据缩放比例转换）
    const screen = availableScreens.value[selectedScreen.value]
    const scaleX = screen.width / areaCanvas.value!.width
    const scaleY = screen.height / areaCanvas.value!.height
    
    const captureRect = {
      x: Math.min(areaSelection.startX, areaSelection.endX) * scaleX,
      y: Math.min(areaSelection.startY, areaSelection.endY) * scaleY,
      width: areaSelection.width * scaleX,
      height: areaSelection.height * scaleY
    }
    
    const screenshot = await window.electronAPI.captureArea(captureRect, settings)
    
    return {
      data: screenshot,
      title: `区域截图_${Date.now()}`,
      width: captureRect.width,
      height: captureRect.height,
      size: screenshot.length
    }
  } catch (error) {
    throw error
  }
}

const cancelAreaSelection = () => {
  areaSelection.active = false
  areaSelection.startX = areaSelection.startY = areaSelection.endX = areaSelection.endY = 0
  initializeAreaCanvas()
}

const toggleRecording = () => {
  if (isRecording.value) {
    stopRecording()
  } else {
    startRecording()
  }
}

const startRecording = async () => {
  try {
    await window.electronAPI.startScreenRecording(settings)
    isRecording.value = true
    ElMessage.success('开始录制屏幕')
  } catch (error) {
    console.error('开始录制失败:', error)
    ElMessage.error('开始录制失败')
  }
}

const stopRecording = async () => {
  try {
    const recording = await window.electronAPI.stopScreenRecording()
    isRecording.value = false
    
    if (recording) {
      addCapturedImage({
        data: recording.thumbnail,
        title: `屏幕录制_${Date.now()}`,
        width: recording.width,
        height: recording.height,
        size: recording.size,
        videoUrl: recording.videoUrl
      })
      
      ElMessage.success('录制已保存')
    }
  } catch (error) {
    console.error('停止录制失败:', error)
    ElMessage.error('停止录制失败')
  }
}

const addCapturedImage = (imageData: any) => {
  const newImage = {
    id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
    ...imageData,
    timestamp: new Date()
  }
  
  capturedImages.value.unshift(newImage)
  
  // 自动保存设置
  if (settings.autoSave) {
    importImage(newImage)
  }
}

const toggleImageSelection = (image: any) => {
  const index = selectedImages.value.indexOf(image.id)
  if (index >= 0) {
    selectedImages.value.splice(index, 1)
  } else {
    selectedImages.value.push(image.id)
  }
}

const previewImage = (image: any) => {
  window.electronAPI.previewImage(image.data)
}

const copyImage = async (image: any) => {
  try {
    await window.electronAPI.copyImageToClipboard(image.data)
    ElMessage.success('图片已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

const removeImage = (imageId: string) => {
  const index = capturedImages.value.findIndex(img => img.id === imageId)
  if (index >= 0) {
    capturedImages.value.splice(index, 1)
    
    const selectedIndex = selectedImages.value.indexOf(imageId)
    if (selectedIndex >= 0) {
      selectedImages.value.splice(selectedIndex, 1)
    }
  }
}

const clearAll = () => {
  if (capturedImages.value.length === 0) {
    ElMessage.warning('没有可清空的截图')
    return
  }
  
  ElMessageBox.confirm(
    '确定要清空所有截图吗？此操作不可撤销。',
    '清空截图',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    capturedImages.value = []
    selectedImages.value = []
    ElMessage.success('已清空所有截图')
  })
}

const importImage = async (image: any) => {
  try {
    await libraryStore.importScreenCapture(image, settings)
    ElMessage.success('截图导入成功')
  } catch (error) {
    console.error('导入失败:', error)
    ElMessage.error('导入失败')
  }
}

const importAll = async () => {
  if (capturedImages.value.length === 0) {
    ElMessage.warning('没有可导入的截图')
    return
  }
  
  const imagesToImport = selectedImages.value.length > 0 
    ? capturedImages.value.filter(img => selectedImages.value.includes(img.id))
    : capturedImages.value
  
  try {
    for (const image of imagesToImport) {
      await importImage(image)
    }
    
    ElMessage.success(`成功导入 ${imagesToImport.length} 张截图`)
    
    // 清空已导入的截图
    capturedImages.value = capturedImages.value.filter(
      img => !imagesToImport.includes(img)
    )
    selectedImages.value = []
  } catch (error) {
    console.error('批量导入失败:', error)
    ElMessage.error('导入失败')
  }
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const closeCapture = () => {
  emit('close')
}

// 键盘事件处理
const handleKeyDown = (event: KeyboardEvent) => {
  if (event.key === 'Escape') {
    if (areaSelection.active) {
      cancelAreaSelection()
    } else if (countdown.value > 0) {
      countdown.value = 0
    }
  }
  
  if (event.key === 'Enter' && areaSelection.active) {
    event.preventDefault()
    captureArea()
  }
  
  if (event.key === ' ' && captureMode.value === 'area') {
    event.preventDefault()
    // 切换屏幕
    const nextScreen = (selectedScreen.value + 1) % availableScreens.value.length
    selectScreen(nextScreen)
    initializeAreaCanvas()
  }
}

// 生命周期
onMounted(() => {
  loadAvailableScreens()
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
  
  // 如果正在录制，停止录制
  if (isRecording.value) {
    stopRecording()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.screen-capture {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.control-bar {
  padding: 16px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

.capture-mode {
  .el-button {
    &.active {
      background: var(--el-color-primary);
      color: white;
    }
  }
}

.capture-options {
  display: flex;
  gap: 8px;
  align-items: center;
}

.preview-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.preview-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 20px;
  overflow-y: auto;
}

.screen-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
}

.screen-item {
  border: 2px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  
  &:hover {
    border-color: var(--el-color-primary-light-5);
  }
  
  &.active {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
}

.screen-thumbnail {
  position: relative;
  margin-bottom: 8px;
  
  img {
    width: 100%;
    height: 120px;
    object-fit: cover;
    border-radius: 4px;
  }
  
  .screen-overlay {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.7);
    color: white;
    padding: 4px;
    font-size: 12px;
  }
}

.screen-info {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.window-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 12px;
  margin-bottom: 20px;
}

.window-item {
  display: flex;
  align-items: center;
  padding: 12px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--el-color-primary-light-5);
  }
  
  &.active {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
}

.window-thumbnail {
  width: 60px;
  height: 40px;
  margin-right: 12px;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 4px;
  }
}

.window-info {
  flex: 1;
  
  .window-title {
    font-weight: 500;
    margin-bottom: 4px;
    font-size: 14px;
    color: var(--el-text-color-primary);
  }
  
  .window-details {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: var(--el-text-color-secondary);
  }
}

.empty-windows {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin: 16px 0;
  }
}

.area-capture {
  display: flex;
  height: 100%;
}

.area-instructions {
  width: 300px;
  padding: 20px;
  background: var(--el-bg-color);
  border-right: 1px solid var(--el-border-color-light);
  
  h3 {
    margin: 0 0 8px;
    color: var(--el-text-color-primary);
  }
  
  p {
    margin: 0 0 20px;
    color: var(--el-text-color-secondary);
    font-size: 14px;
  }
}

.shortcut-list {
  .shortcut-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid var(--el-border-color-lighter);
    
    &:last-child {
      border-bottom: none;
    }
    
    kbd {
      background: var(--el-bg-color-page);
      border: 1px solid var(--el-border-color);
      border-radius: 4px;
      padding: 2px 6px;
      font-size: 12px;
      font-family: monospace;
    }
    
    span {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
}

.area-preview {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.area-canvas {
  max-width: 90%;
  max-height: 90%;
  border: 1px solid var(--el-border-color);
  border-radius: 4px;
  cursor: crosshair;
}

.area-info {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 12px;
  border-radius: 4px;
  
  .area-dimensions {
    font-size: 14px;
    margin-bottom: 8px;
  }
  
  .area-actions {
    display: flex;
    gap: 8px;
  }
}

.capture-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 20px;
}

.countdown-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.countdown-content {
  text-align: center;
  color: white;
  
  .countdown-number {
    font-size: 120px;
    font-weight: bold;
    margin-bottom: 20px;
  }
  
  .countdown-text {
    font-size: 24px;
  }
}

.capture-results {
  height: 200px;
  background: var(--el-bg-color);
  border-top: 1px solid var(--el-border-color-light);
  display: flex;
  flex-direction: column;
}

.results-header {
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  
  span {
    font-weight: 500;
    color: var(--el-text-color-primary);
  }
}

.results-grid {
  flex: 1;
  display: flex;
  overflow-x: auto;
  padding: 8px;
  gap: 8px;
}

.capture-item {
  width: 120px;
  flex-shrink: 0;
  border: 2px solid transparent;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--el-border-color);
    
    .item-overlay {
      opacity: 1;
    }
  }
  
  &.selected {
    border-color: var(--el-color-primary);
  }
}

.item-thumbnail {
  position: relative;
  height: 80px;
  background: var(--el-bg-color-page);
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}

.item-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease;
}

.item-info {
  padding: 8px;
  
  .item-title {
    font-size: 12px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .item-details {
    display: flex;
    justify-content: space-between;
    font-size: 10px;
    color: var(--el-text-color-secondary);
  }
}

.capture-settings {
  padding: 20px;
}

@media (max-width: 768px) {
  .control-bar {
    flex-direction: column;
    gap: 12px;
  }
  
  .capture-options {
    width: 100%;
    justify-content: space-between;
  }
  
  .area-capture {
    flex-direction: column;
  }
  
  .area-instructions {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .screen-grid,
  .window-list {
    grid-template-columns: 1fr;
  }
  
  .capture-actions {
    flex-direction: column;
  }
}
</style>