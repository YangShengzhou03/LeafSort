<template>
  <div class="import-assets">
    <!-- 导入方式选择 -->
    <div class="import-methods">
      <el-radio-group v-model="importMethod" size="large">
        <el-radio-button label="drag">拖拽导入</el-radio-button>
        <el-radio-button label="file">文件选择</el-radio-button>
        <el-radio-button label="folder">文件夹导入</el-radio-button>
        <el-radio-button label="screenshot">截图导入</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 拖拽区域 -->
    <div 
      v-show="importMethod === 'drag'"
      class="drop-zone"
      :class="{ active: isDragOver }"
      @drop="handleDrop"
      @dragover="handleDragOver"
      @dragleave="handleDragLeave"
    >
      <el-icon class="drop-icon">
        <UploadFilled />
      </el-icon>
      <div class="drop-text">拖拽文件到此处导入</div>
      <div class="drop-hint">支持图片、视频、音频等格式</div>
    </div>

    <!-- 文件选择器 -->
    <div v-show="importMethod === 'file'" class="file-selector">
      <el-upload
        ref="uploadRef"
        :auto-upload="false"
        :multiple="true"
        :show-file-list="true"
        :file-list="fileList"
        :before-upload="beforeUpload"
        :on-change="handleFileChange"
        :on-remove="handleFileRemove"
        accept="image/*,video/*,audio/*,.psd,.ai,.sketch"
        drag
      >
        <el-icon size="48" class="el-icon--upload">
          <UploadFilled />
        </el-icon>
        <div class="el-upload__text">
          将文件拖到此处，或<em>点击选择</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            支持 jpg/png/gif/webp/mp4/mov/mp3/wav/psd/ai/sketch 等格式，单个文件不超过 100MB
          </div>
        </template>
      </el-upload>
    </div>

    <!-- 文件夹导入 -->
    <div v-show="importMethod === 'folder'" class="folder-import">
      <el-button 
        type="primary" 
        @click="selectFolder"
        :loading="isScanning"
      >
        <el-icon><FolderOpened /></el-icon>
        选择文件夹
      </el-button>
      
      <div v-if="selectedFolder" class="folder-info">
        <div class="folder-path">
          <el-icon><Folder /></el-icon>
          {{ selectedFolder }}
        </div>
        <div class="folder-stats" v-if="folderStats">
          发现 {{ folderStats.fileCount }} 个文件，总计 {{ formatFileSize(folderStats.totalSize) }}
        </div>
      </div>

      <div v-if="folderFiles.length > 0" class="folder-files">
        <div class="files-header">
          <span>文件夹内容预览</span>
          <el-button size="small" @click="toggleSelectAll">
            {{ isAllSelected ? '取消全选' : '全选' }}
          </el-button>
        </div>
        
        <div class="files-grid">
          <div
            v-for="file in folderFiles"
            :key="file.path"
            class="file-item"
            :class="{ selected: selectedFiles.includes(file.path) }"
            @click="toggleFileSelection(file)"
          >
            <div class="file-thumbnail">
              <img 
                v-if="isImageFile(file.name)"
                :src="getFileThumbnail(file)"
                :alt="file.name"
                @error="handleThumbnailError"
              />
              <el-icon v-else class="file-icon">
                <component :is="getFileTypeIcon(file.name)" />
              </el-icon>
            </div>
            <div class="file-info">
              <div class="file-name">{{ file.name }}</div>
              <div class="file-size">{{ formatFileSize(file.size) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 截图导入 -->
    <div v-show="importMethod === 'screenshot'" class="screenshot-import">
      <div class="screenshot-options">
        <el-button @click="takeScreenshot" type="primary">
          <el-icon><Camera /></el-icon>
          拍摄截图
        </el-button>
        <el-button @click="pasteScreenshot">
          <el-icon><DocumentCopy /></el-icon>
          粘贴截图
        </el-button>
      </div>
      
      <div v-if="screenshotData" class="screenshot-preview">
        <div class="preview-header">
          <span>截图预览</span>
          <el-button size="small" @click="screenshotData = null">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        <img :src="screenshotData" alt="截图" class="screenshot-image" />
      </div>
    </div>

    <!-- 导入配置 -->
    <div class="import-config">
      <el-divider>导入设置</el-divider>
      
      <el-form :model="config" label-width="120px">
        <el-form-item label="目标文件夹">
          <el-select v-model="config.targetFolder" placeholder="选择导入位置">
            <el-option label="根目录" value=""></el-option>
            <el-option 
              v-for="folder in availableFolders" 
              :key="folder.id"
              :label="folder.name" 
              :value="folder.id"
            ></el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="重复文件处理">
          <el-radio-group v-model="config.duplicateHandling">
            <el-radio label="skip">跳过重复文件</el-radio>
            <el-radio label="rename">重命名文件</el-radio>
            <el-radio label="replace">替换原文件</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="自动标签">
          <el-switch v-model="config.autoTagging" />
          <el-input 
            v-if="config.autoTagging"
            v-model="config.autoTags" 
            placeholder="输入标签，用逗号分隔"
            style="width: 200px; margin-left: 10px;"
          />
        </el-form-item>
        
        <el-form-item label="保留文件夹结构">
          <el-switch v-model="config.preserveStructure" />
        </el-form-item>
        
        <el-form-item label="生成缩略图">
          <el-switch v-model="config.generateThumbnails" />
        </el-form-item>
      </el-form>
    </div>

    <!-- 操作按钮 -->
    <div class="import-actions">
      <el-button @click="$emit('close')">取消</el-button>
      <el-button 
        type="primary" 
        @click="startImport"
        :loading="isImporting"
        :disabled="!hasFilesToImport"
      >
        开始导入
      </el-button>
    </div>

    <!-- 导入进度 -->
    <el-dialog
      v-model="showProgress"
      title="导入进度"
      width="500px"
      :close-on-click-modal="false"
      :show-close="false"
    >
      <div class="import-progress">
        <el-progress 
          :percentage="importProgress" 
          :status="importStatus"
          :stroke-width="8"
        />
        <div class="progress-info">
          <span>{{ importCurrentFile }}</span>
          <span>{{ importProgress }}%</span>
        </div>
        
        <div class="progress-actions">
          <el-button 
            v-if="importStatus === 'success'" 
            type="primary" 
            @click="handleImportComplete"
          >
            完成
          </el-button>
          <el-button 
            v-else-if="importStatus === 'exception'" 
            @click="handleImportError"
          >
            重试
          </el-button>
          <el-button 
            v-else 
            :loading="isImporting"
            @click="cancelImport"
          >
            取消
          </el-button>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'
import { Folder } from '@/types'

// 图标导入
import {
  UploadFilled,
  FolderOpened,
  Folder,
  Camera,
  DocumentCopy,
  Close,
  Picture,
  VideoCamera,
  Headphone,
  Document,
  File
} from '@element-plus/icons-vue'

const emit = defineEmits(['close'])
const libraryStore = useLibraryStore()

// 响应式数据
const importMethod = ref<'drag' | 'file' | 'folder' | 'screenshot'>('drag')
const isDragOver = ref(false)
const fileList = ref<any[]>([])
const selectedFolder = ref('')
const folderStats = ref<{ fileCount: number; totalSize: number } | null>(null)
const folderFiles = ref<any[]>([])
const selectedFiles = ref<string[]>([])
const screenshotData = ref<string | null>(null)
const isScanning = ref(false)
const isImporting = ref(false)
const showProgress = ref(false)
const importProgress = ref(0)
const importStatus = ref<'success' | 'exception' | ''>('')
const importCurrentFile = ref('')

// 导入配置
const config = ref({
  targetFolder: '',
  duplicateHandling: 'skip' as 'skip' | 'rename' | 'replace',
  autoTagging: false,
  autoTags: '',
  preserveStructure: true,
  generateThumbnails: true
})

// 计算属性
const availableFolders = computed(() => {
  return libraryStore.folders
})

const hasFilesToImport = computed(() => {
  switch (importMethod.value) {
    case 'drag':
    case 'file':
      return fileList.value.length > 0
    case 'folder':
      return selectedFiles.value.length > 0
    case 'screenshot':
      return screenshotData.value !== null
    default:
      return false
  }
})

const isAllSelected = computed(() => {
  return selectedFiles.value.length === folderFiles.value.length && folderFiles.value.length > 0
})

// 方法
const handleDrop = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = false
  
  const files = Array.from(event.dataTransfer?.files || [])
  if (files.length > 0) {
    addFilesToImport(files)
  }
}

const handleDragOver = (event: DragEvent) => {
  event.preventDefault()
  isDragOver.value = true
}

const handleDragLeave = (event: DragEvent) => {
  event.preventDefault()
  if (!event.currentTarget?.contains(event.relatedTarget as Node)) {
    isDragOver.value = false
  }
}

const beforeUpload = (file: File) => {
  const maxSize = 100 * 1024 * 1024 // 100MB
  if (file.size > maxSize) {
    ElMessage.error(`文件 ${file.name} 超过 100MB 限制`)
    return false
  }
  return true
}

const handleFileChange = (file: any, fileList: any[]) => {
  // 过滤掉不符合条件的文件
  const validFiles = fileList.filter(f => beforeUpload(f.raw))
  fileList.value = validFiles
}

const handleFileRemove = (file: any, fileList: any[]) => {
  fileList.value = fileList
}

const selectFolder = async () => {
  try {
    const result = await window.electronAPI.selectDirectory()
    if (result) {
      selectedFolder.value = result
      await scanFolder(result)
    }
  } catch (error) {
    console.error('选择文件夹失败:', error)
    ElMessage.error('选择文件夹失败')
  }
}

const scanFolder = async (folderPath: string) => {
  isScanning.value = true
  try {
    // 扫描文件夹中的文件
    const files = await window.electronAPI.scanDirectory(folderPath)
    folderFiles.value = files
    
    // 计算统计信息
    folderStats.value = {
      fileCount: files.length,
      totalSize: files.reduce((sum, file) => sum + file.size, 0)
    }
    
    // 自动选择所有文件
    selectedFiles.value = files.map(file => file.path)
  } catch (error) {
    console.error('扫描文件夹失败:', error)
    ElMessage.error('扫描文件夹失败')
  } finally {
    isScanning.value = false
  }
}

const toggleFileSelection = (file: any) => {
  const index = selectedFiles.value.indexOf(file.path)
  if (index >= 0) {
    selectedFiles.value.splice(index, 1)
  } else {
    selectedFiles.value.push(file.path)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedFiles.value = []
  } else {
    selectedFiles.value = folderFiles.value.map(file => file.path)
  }
}

const takeScreenshot = async () => {
  try {
    const screenshot = await window.electronAPI.takeScreenshot()
    if (screenshot) {
      screenshotData.value = screenshot
    }
  } catch (error) {
    console.error('截图失败:', error)
    ElMessage.error('截图失败')
  }
}

const pasteScreenshot = async () => {
  try {
    // 从剪贴板读取图片
    const items = await navigator.clipboard.read()
    for (const item of items) {
      for (const type of item.types) {
        if (type.startsWith('image/')) {
          const blob = await item.getType(type)
          const reader = new FileReader()
          reader.onload = () => {
            screenshotData.value = reader.result as string
          }
          reader.readAsDataURL(blob)
          return
        }
      }
    }
    ElMessage.warning('剪贴板中没有图片')
  } catch (error) {
    console.error('粘贴截图失败:', error)
    ElMessage.error('粘贴截图失败')
  }
}

const addFilesToImport = (files: File[]) => {
  files.forEach(file => {
    if (beforeUpload(file)) {
      fileList.value.push({
        name: file.name,
        size: file.size,
        raw: file
      })
    }
  })
}

const startImport = async () => {
  if (!hasFilesToImport.value) {
    ElMessage.warning('请选择要导入的文件')
    return
  }

  try {
    isImporting.value = true
    showProgress.value = true
    importProgress.value = 0
    importStatus.value = ''

    let filesToImport: any[] = []

    // 准备导入文件
    switch (importMethod.value) {
      case 'drag':
      case 'file':
        filesToImport = fileList.value
        break
      case 'folder':
        filesToImport = folderFiles.value.filter(file => 
          selectedFiles.value.includes(file.path)
        )
        break
      case 'screenshot':
        if (screenshotData.value) {
          filesToImport = [{
            name: `screenshot_${Date.now()}.png`,
            data: screenshotData.value,
            isScreenshot: true
          }]
        }
        break
    }

    // 执行导入
    for (let i = 0; i < filesToImport.length; i++) {
      const file = filesToImport[i]
      importCurrentFile.value = file.name
      
      try {
        await libraryStore.importAsset(file, config.value)
        importProgress.value = Math.round(((i + 1) / filesToImport.length) * 100)
      } catch (error) {
        console.error(`导入文件 ${file.name} 失败:`, error)
        importStatus.value = 'exception'
        break
      }
    }

    if (importStatus.value !== 'exception') {
      importStatus.value = 'success'
      ElMessage.success(`成功导入 ${filesToImport.length} 个文件`)
    }

  } catch (error) {
    console.error('导入过程出错:', error)
    importStatus.value = 'exception'
    ElMessage.error('导入失败')
  } finally {
    isImporting.value = false
  }
}

const cancelImport = () => {
  isImporting.value = false
  showProgress.value = false
  ElMessage.info('导入已取消')
}

const handleImportComplete = () => {
  showProgress.value = false
  emit('close')
}

const handleImportError = () => {
  showProgress.value = false
  importStatus.value = ''
  importProgress.value = 0
}

const isImageFile = (filename: string) => {
  const imageExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.tiff']
  return imageExtensions.some(ext => filename.toLowerCase().endsWith(ext))
}

const getFileThumbnail = (file: any) => {
  return `file://${file.path}`
}

const getFileTypeIcon = (filename: string) => {
  const ext = filename.toLowerCase().split('.').pop()
  
  if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(ext || '')) {
    return 'Picture'
  } else if (['mp4', 'mov', 'avi', 'mkv', 'webm'].includes(ext || '')) {
    return 'VideoCamera'
  } else if (['mp3', 'wav', 'flac', 'aac'].includes(ext || '')) {
    return 'Headphone'
  } else if (['pdf', 'doc', 'docx', 'txt'].includes(ext || '')) {
    return 'Document'
  } else {
    return 'File'
  }
}

const handleThumbnailError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 生命周期
onMounted(() => {
  // 监听粘贴事件
  document.addEventListener('paste', (event) => {
    if (importMethod.value === 'screenshot') {
      const items = event.clipboardData?.items
      if (items) {
        for (let i = 0; i < items.length; i++) {
          if (items[i].type.indexOf('image') !== -1) {
            const blob = items[i].getAsFile()
            if (blob) {
              const reader = new FileReader()
              reader.onload = (e) => {
                screenshotData.value = e.target?.result as string
              }
              reader.readAsDataURL(blob)
            }
            break
          }
        }
      }
    }
  })
})
</script>

<style scoped lang="scss">
@use '@/styles/index.scss' as global;

.import-assets {
  padding: 20px;
}

.import-methods {
  margin-bottom: 30px;
  text-align: center;
}

.drop-zone {
  border: 2px dashed rgba(255, 255, 255, 0.2);
  border-radius: 10px;
  padding: 60px 20px;
  text-align: center;
  transition: all 0.3s ease;
  background: rgba(24, 25, 35, 0.6);
  margin-bottom: 30px;
  backdrop-filter: blur(5px);
  
  &.active {
    border-color: var(--el-color-primary);
    background: rgba(45, 140, 240, 0.15);
    box-shadow: 0 0 0 1px var(--el-color-primary);
  }
  
  .drop-icon {
    font-size: 64px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 16px;
  }
  
  .drop-text {
    font-size: 18px;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 8px;
  }
  
  .drop-hint {
    font-size: 14px;
    color: rgba(255, 255, 255, 0.5);
  }
}

.file-selector {
  margin-bottom: 30px;
}

.folder-import {
  margin-bottom: 30px;
  
  .folder-info {
    margin-top: 20px;
    padding: 16px;
    background: rgba(24, 25, 35, 0.6);
    border-radius: 8px;
    border: 1px solid rgba(255, 255, 255, 0.1);
    
    .folder-path {
      display: flex;
      align-items: center;
      margin-bottom: 8px;
      
      .el-icon {
        margin-right: 8px;
        color: var(--el-color-primary);
      }
    }
    
    .folder-stats {
      font-size: 14px;
      color: rgba(255, 255, 255, 0.6);
    }
  }
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.files-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
  padding: 8px;
  background: rgba(24, 25, 35, 0.6);
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.file-item {
  border: 2px solid transparent;
  border-radius: 6px;
  padding: 8px;
  background: rgba(12, 13, 18, 0.8);
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
  
  &:hover {
    border-color: rgba(255, 255, 255, 0.3);
    background: rgba(24, 25, 35, 0.8);
  }
  
  &.selected {
    border-color: var(--el-color-primary);
    background: rgba(45, 140, 240, 0.15);
  }
}

.file-thumbnail {
  width: 64px;
  height: 64px;
  margin: 0 auto 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(12, 13, 18, 0.8);
  border-radius: 4px;
  overflow: hidden;
  
  img {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
  
  .file-icon {
    font-size: 24px;
    color: rgba(255, 255, 255, 0.5);
  }
}

.file-info {
  .file-name {
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.8);
    margin-bottom: 4px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .file-size {
    font-size: 11px;
    color: rgba(255, 255, 255, 0.5);
  }
}

.screenshot-import {
  margin-bottom: 30px;
  
  .screenshot-options {
    display: flex;
    gap: 12px;
    margin-bottom: 20px;
  }
  
  .screenshot-preview {
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    overflow: hidden;
    background: rgba(12, 13, 18, 0.8);
  }
  
  .preview-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px;
    background: rgba(24, 25, 35, 0.6);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }
}

.import-config {
  margin-bottom: 30px;
}

.import-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

.import-progress {
  text-align: center;
  
  .progress-info {
    display: flex;
    justify-content: space-between;
    margin: 16px 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
  
  .progress-actions {
    margin-top: 20px;
  }
}

@media (max-width: 768px) {
  .import-assets {
    padding: 16px;
  }
  
  .import-methods {
    .el-radio-group {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
    }
  }
  
  .drop-zone {
    padding: 40px 16px;
    
    .drop-icon {
      font-size: 48px;
    }
  }
  
  .files-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 8px;
  }
  
  .screenshot-options {
    flex-direction: column;
  }
  
  .import-config {
    .el-form {
      .el-form-item {
        label-width: 100px;
      }
    }
  }
  
  .import-actions {
    flex-direction: column-reverse;
  }
  
  .folder-info {
    padding: 12px;
    
    .folder-path {
      font-size: 14px;
      word-break: break-all;
    }
  }
}

@media (max-width: 480px) {
  .import-assets {
    padding: 12px;
  }
  
  .import-methods {
    .el-radio-group {
      display: block;
      
      .el-radio-button {
        display: block;
        margin-bottom: 8px;
      }
    }
  }
  
  .drop-zone {
    padding: 30px 12px;
    
    .drop-icon {
      font-size: 40px;
    }
    
    .drop-text {
      font-size: 16px;
    }
  }
  
  .files-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
    gap: 6px;
    max-height: 250px;
  }
  
  .file-item {
    padding: 6px;
  }
  
  .file-thumbnail {
    width: 50px;
    height: 50px;
    
    .file-icon {
      font-size: 20px;
    }
  }
  
  .file-name {
    font-size: 11px;
  }
  
  .file-size {
    font-size: 10px;
  }
  
  .import-config {
    .el-form {
      .el-form-item {
        label-width: 90px;
      }
    }
  }
}
</style>