<template>
  <div class="file-operations">
    <!-- 导入按钮 -->
    <div class="import-section">
      <el-button type="primary" @click="triggerFileInput" :loading="isImporting">
        <el-icon><Upload /></el-icon>
        导入音频文件
      </el-button>
      <input
        ref="fileInput"
        type="file"
        accept=".mp3,.wav,.flac,.aac,.ogg"
        multiple
        style="display: none"
        @change="handleFileImport"
      />
      <div v-if="isImporting" class="import-progress">
        <el-progress :percentage="importProgress" :status="importStatus" />
        <span class="progress-text">{{ importProgressText }}</span>
      </div>
    </div>

    <!-- 导出功能 -->
    <div class="export-section">
      <el-dropdown @command="handleExport">
        <el-button>
          <el-icon><Download /></el-icon>
          导出
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="selected">导出选中文件</el-dropdown-item>
            <el-dropdown-item command="all">导出所有文件</el-dropdown-item>
            <el-dropdown-item command="folder">导出当前文件夹</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 批量操作 -->
    <div class="batch-operations">
      <el-dropdown @command="handleBatchOperation">
        <el-button>
          <el-icon><MoreFilled /></el-icon>
          批量操作
          <el-icon class="el-icon--right"><ArrowDown /></el-icon>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="delete">批量删除</el-dropdown-item>
            <el-dropdown-item command="move">移动到文件夹</el-dropdown-item>
            <el-dropdown-item command="tag">批量添加标签</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>

    <!-- 文件预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      :title="`预览: ${previewAsset?.name}`"
      width="700px"
      destroy-on-close
    >
      <div class="preview-container">
        <!-- 音频播放器 -->
        <div class="audio-player">
          <audio
            ref="audioPlayer"
            :src="previewUrl"
            controls
            @play="handlePreviewPlay"
            @pause="handlePreviewPause"
            @ended="handlePreviewEnded"
            @timeupdate="handlePreviewTimeUpdate"
          />
        </div>

        <!-- 波形图预览 -->
        <div class="waveform-preview">
          <WaveformComponent
            :data="previewWaveformData"
            :progress="previewProgress"
            :is-playing="isPreviewPlaying"
          />
        </div>

        <!-- 详细元数据 -->
        <div class="preview-metadata">
          <h4>详细信息</h4>
          <el-descriptions :column="2" border>
            <el-descriptions-item label="文件名">{{ previewAsset?.name }}</el-descriptions-item>
            <el-descriptions-item label="格式">{{ previewAsset?.format }}</el-descriptions-item>
            <el-descriptions-item label="时长">{{ formatDuration(previewAsset?.duration || 0) }}</el-descriptions-item>
            <el-descriptions-item label="BPM">{{ previewAsset?.bpm || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="文件大小">{{ formatFileSize(previewAsset?.size || 0) }}</el-descriptions-item>
            <el-descriptions-item label="采样率">{{ previewAsset?.sampleRate || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="比特率">{{ previewAsset?.bitRate || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="声道">{{ previewAsset?.channels || 'N/A' }}</el-descriptions-item>
            <el-descriptions-item label="艺术家" :span="2">{{ previewAsset?.artist || 'Unknown' }}</el-descriptions-item>
            <el-descriptions-item label="专辑" :span="2">{{ previewAsset?.album || 'Unknown' }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPreviewDialog = false">关闭</el-button>
          <el-button type="primary" @click="downloadPreviewFile">下载文件</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 移动文件对话框 -->
    <el-dialog
      v-model="showMoveDialog"
      title="移动文件"
      width="400px"
      destroy-on-close
    >
      <div class="move-dialog-content">
        <el-form label-width="80px">
          <el-form-item label="目标文件夹">
            <el-select v-model="selectedFolderId" placeholder="选择目标文件夹">
              <el-option
                v-for="folder in availableFolders"
                :key="folder.id"
                :label="folder.name"
                :value="folder.id"
              />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showMoveDialog = false">取消</el-button>
          <el-button type="primary" @click="confirmMoveFiles">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import WaveformComponent from './WaveformComponent.vue'
import type { Asset } from '../types'

// Props
const props = defineProps<{
  selectedAssets: Asset[]
  currentFolderId?: string
  availableFolders?: Array<{ id: string; name: string }>
}>()

// Emits
const emit = defineEmits<{
  (e: 'import', files: File[]): void
  (e: 'export', mode: 'selected' | 'all' | 'folder'): void
  (e: 'delete', assetIds: string[]): void
  (e: 'move', assetIds: string[], targetFolderId: string): void
  (e: 'batchAddTag', assetIds: string[]): void
}>()

// 响应式数据
const fileInput = ref<HTMLInputElement>()
const isImporting = ref(false)
const importProgress = ref(0)
const importStatus = ref<'success' | 'exception'>('success')
const importProgressText = ref('')
const showPreviewDialog = ref(false)
const previewAsset = ref<Asset | null>(null)
const previewUrl = ref('')
const previewWaveformData = ref<number[]>([])
const isPreviewPlaying = ref(false)
const previewProgress = ref(0)
const audioPlayer = ref<HTMLAudioElement>()
const showMoveDialog = ref(false)
const selectedFolderId = ref('')

// 计算属性
const selectedAssetIds = computed(() => props.selectedAssets.map(asset => asset.id))

// 方法
const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileImport = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = Array.from(target.files || [])
  
  if (files.length === 0) return
  
  // 验证文件类型
  const validFiles = files.filter(file => {
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/aac', 'audio/ogg']
    return validTypes.includes(file.type) || 
           ['.mp3', '.wav', '.flac', '.aac', '.ogg'].some(ext => file.name.endsWith(ext))
  })
  
  if (validFiles.length === 0) {
    ElMessage.warning('请选择有效的音频文件（MP3、WAV、FLAC、AAC、OGG）')
    return
  }
  
  // 模拟导入进度
  simulateImportProgress(validFiles)
}

const simulateImportProgress = (files: File[]) => {
  isImporting.value = true
  importProgress.value = 0
  importStatus.value = 'success'
  importProgressText.value = `正在导入 ${files.length} 个文件...`
  
  const totalSteps = 100
  let currentStep = 0
  
  const interval = setInterval(() => {
    currentStep += 1
    importProgress.value = Math.floor((currentStep / totalSteps) * 100)
    
    if (importProgress.value >= 100) {
      clearInterval(interval)
      setTimeout(() => {
        isImporting.value = false
        emit('import', files)
        ElMessage.success(`成功导入 ${files.length} 个文件`)
        importProgressText.value = ''
        // 清空文件输入
        if (fileInput.value) {
          fileInput.value.value = ''
        }
      }, 500)
    }
  }, 30)
}

const handleExport = (mode: string) => {
  emit('export', mode as 'selected' | 'all' | 'folder')
  ElMessage.success(`开始导出文件`)
}

const handleBatchOperation = (operation: string) => {
  if (selectedAssets.length === 0 && operation !== 'delete') {
    ElMessage.warning('请先选择要操作的文件')
    return
  }
  
  switch (operation) {
    case 'delete':
      confirmDeleteFiles()
      break
    case 'move':
      if (props.availableFolders && props.availableFolders.length > 0) {
        selectedFolderId.value = props.availableFolders[0].id
        showMoveDialog.value = true
      } else {
        ElMessage.warning('没有可用的文件夹')
      }
      break
    case 'tag':
      emit('batchAddTag', selectedAssetIds.value)
      break
  }
}

const confirmDeleteFiles = () => {
  ElMessageBox.confirm(
    '确定要删除选中的文件吗？此操作不可撤销。',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(() => {
    emit('delete', selectedAssetIds.value)
    ElMessage.success('文件删除成功')
  }).catch(() => {
    // 取消删除
  })
}

const confirmMoveFiles = () => {
  if (!selectedFolderId.value) {
    ElMessage.warning('请选择目标文件夹')
    return
  }
  
  emit('move', selectedAssetIds.value, selectedFolderId.value)
  showMoveDialog.value = false
  ElMessage.success('文件移动成功')
}

// 预览相关方法
const openPreview = (asset: Asset) => {
  previewAsset.value = asset
  // 模拟文件URL
  previewUrl.value = `https://example.com/audio/${asset.id}`
  // 生成波形数据
  previewWaveformData.value = generateWaveformData(200)
  isPreviewPlaying.value = false
  previewProgress.value = 0
  showPreviewDialog.value = true
}

const handlePreviewPlay = () => {
  isPreviewPlaying.value = true
}

const handlePreviewPause = () => {
  isPreviewPlaying.value = false
}

const handlePreviewEnded = () => {
  isPreviewPlaying.value = false
  previewProgress.value = 0
}

const handlePreviewTimeUpdate = () => {
  if (audioPlayer.value && previewAsset.value) {
    previewProgress.value = (audioPlayer.value.currentTime / previewAsset.value.duration) * 100
  }
}

const downloadPreviewFile = () => {
  // 模拟下载
  ElMessage.success(`开始下载: ${previewAsset?.value?.name}`)
  // 在实际应用中，这里应该使用真实的文件URL进行下载
  const link = document.createElement('a')
  link.href = previewUrl.value
  link.download = previewAsset?.value?.name || 'audio.mp3'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

// 辅助方法
const formatDuration = (seconds: number): string => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = Math.floor(seconds % 60)
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const formatFileSize = (bytes: number): string => {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

const generateWaveformData = (points: number): number[] => {
  const data: number[] = []
  for (let i = 0; i < points; i++) {
    // 生成一些随机但看起来像波形的数据
    const value = 0.2 + Math.random() * 0.6 + (Math.sin(i * 0.1) * 0.1)
    data.push(value)
  }
  return data
}

// 暴露给父组件的方法
defineExpose({
  openPreview
})
</script>

<style scoped>
.file-operations {
  margin-bottom: 16px;
}

.import-section {
  margin-bottom: 16px;
}

.import-progress {
  margin-top: 12px;
}

.progress-text {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}

.export-section,
.batch-operations {
  margin-bottom: 8px;
}

.preview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.audio-player {
  margin-bottom: 10px;
}

.audio-player audio {
  width: 100%;
}

.waveform-preview {
  height: 120px;
  border-radius: 4px;
  background-color: var(--el-bg-color-secondary);
  display: flex;
  align-items: center;
  padding: 0 16px;
}

.preview-metadata {
  margin-top: 16px;
}

.preview-metadata h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 500;
}

.move-dialog-content {
  padding: 16px 0;
}

.move-dialog-content .el-form-item {
  margin-bottom: 0;
}
</style>