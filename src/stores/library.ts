import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import type { Library, Asset, Folder, Tag } from '@/types'

export const useLibraryStore = defineStore('library', () => {
  // 当前激活的素材库
  const currentLibrary = ref<Library | null>(null)
  
  // 素材列表
  const assets = ref<Asset[]>([])
  
  // 文件夹结构
  const folders = ref<Folder[]>([])
  
  // 标签系统
  const tags = ref<Tag[]>([])
  
  // 当前选中的素材
  const selectedAssets = ref<Set<string>>(new Set())
  
  // 搜索条件
  const searchFilters = reactive({
    keyword: '',
    fileType: '',
    sizeRange: { min: 0, max: Infinity },
    dateRange: { start: null, end: null },
    tags: [] as string[],
    rating: 0
  })
  
  // 视图模式
  const viewMode = ref<'grid' | 'list' | 'masonry'>('grid')
  
  // 排序方式
  const sortBy = ref<'name' | 'size' | 'date' | 'rating'>('date')
  const sortOrder = ref<'asc' | 'desc'>('desc')
  
  // 创建新素材库
  const createLibrary = (name: string, path: string) => {
    const newLibrary: Library = {
      id: generateId(),
      name,
      path,
      createdAt: new Date(),
      assetCount: 0,
      size: 0
    }
    currentLibrary.value = newLibrary
    return newLibrary
  }
  
  // 打开素材库
  const openLibrary = (library: Library) => {
    currentLibrary.value = library
    // 这里应该加载素材库数据
  }
  
  // 导入素材
  const importAssets = async (files: FileList | File[], folderId?: string) => {
    const fileArray = Array.from(files)
    
    for (const file of fileArray) {
      const asset: Asset = {
        id: generateId(),
        name: file.name,
        path: file.name,
        type: getFileType(file.name),
        size: file.size,
        createdAt: new Date(),
        updatedAt: new Date(),
        tags: [],
        metadata: {},
        folderId: folderId || null,
        thumbnail: await generateThumbnail(file)
      }
      
      assets.value.push(asset)
      
      // 添加到最近活动
      addRecentActivity({
        type: 'import',
        assetId: asset.id,
        timestamp: new Date(),
        description: `导入了 ${file.name}`
      })
    }
    
    // 保存到本地存储
    saveToLocalStorage()
  }

  // 导入网页采集内容
  const importWebCapture = async (captureItem: any, settings: any) => {
    try {
      // 生成唯一的文件名
      const timestamp = new Date().getTime()
      const extension = settings.format || 'png'
      const fileName = `web_capture_${timestamp}.${extension}`
      
      // 创建素材对象
      const asset: Asset = {
        id: generateId(),
        name: captureItem.title || fileName,
        path: fileName,
        type: 'image', // 网页采集主要是图片
        size: 0, // 实际大小需要从数据计算
        createdAt: new Date(),
        updatedAt: new Date(),
        tags: settings.defaultTags ? settings.defaultTags.split(',').map((tag: string) => tag.trim()) : ['网页采集'],
        metadata: {
          source: captureItem.source || '',
          captureType: captureItem.captureType || 'web',
          originalUrl: captureItem.source || '',
          quality: settings.quality || 'high',
          hasWatermark: settings.addWatermark || false,
          format: settings.format || 'png'
        },
        folderId: null,
        thumbnail: captureItem.data // 直接使用base64数据作为缩略图
      }
      
      // 如果是base64数据，计算实际大小
      if (captureItem.data && captureItem.data.startsWith('data:')) {
        const base64Data = captureItem.data.split(',')[1]
        asset.size = Math.floor(base64Data.length * 0.75) // 近似计算
      }
      
      assets.value.push(asset)
      
      // 添加到最近活动
      addRecentActivity({
        type: 'web_capture',
        assetId: asset.id,
        timestamp: new Date(),
        description: `网页采集: ${captureItem.title || '未命名'}`
      })
      
      // 保存到本地存储
      saveToLocalStorage()
      
      return asset
    } catch (error) {
      console.error('导入网页采集失败:', error)
      throw error
    }
  }

  // 导入屏幕截图
  const importScreenCapture = async (captureItem: any, settings: any) => {
    try {
      // 生成唯一的文件名
      const timestamp = new Date().getTime()
      const extension = settings.format || 'png'
      const fileName = `screenshot_${timestamp}.${extension}`
      
      // 创建素材对象
      const asset: Asset = {
        id: generateId(),
        name: captureItem.title || fileName,
        path: fileName,
        type: 'image',
        size: captureItem.size || 0,
        createdAt: new Date(),
        updatedAt: new Date(),
        tags: settings.defaultTags ? settings.defaultTags.split(',').map((tag: string) => tag.trim()) : ['截图', '屏幕截图'],
        metadata: {
          captureType: 'screenshot',
          width: captureItem.width || 0,
          height: captureItem.height || 0,
          quality: settings.quality || 90,
          hasWatermark: settings.addWatermark || false,
          watermarkText: settings.watermarkText || '',
          includeCursor: settings.includeCursor || false,
          format: settings.format || 'png',
          videoUrl: captureItem.videoUrl || null // 如果是录屏
        },
        folderId: null,
        thumbnail: captureItem.data
      }
      
      assets.value.push(asset)
      
      // 添加到最近活动
      addRecentActivity({
        type: 'web_capture',
        assetId: asset.id,
        timestamp: new Date(),
        description: `屏幕截图: ${captureItem.title || '未命名'}`
      })
      
      // 保存到本地存储
      saveToLocalStorage()
      
      return asset
    } catch (error) {
      console.error('导入屏幕截图失败:', error)
      throw error
    }
  }
  
  // 创建文件夹
  const createFolder = (name: string, parentId?: string) => {
    const folder: Folder = {
      id: generateId(),
      name,
      parentId,
      createdAt: new Date(),
      assetCount: 0
    }
    folders.value.push(folder)
    return folder
  }
  
  // 添加标签
  const addTag = (name: string, color?: string) => {
    const tag: Tag = {
      id: generateId(),
      name,
      color: color || getRandomColor(),
      assetCount: 0
    }
    tags.value.push(tag)
    return tag
  }
  
  // 选择素材
  const selectAsset = (assetId: string, multiple = false) => {
    if (!multiple) {
      selectedAssets.value.clear()
    }
    selectedAssets.value.add(assetId)
  }
  
  // 取消选择
  const deselectAsset = (assetId: string) => {
    selectedAssets.value.delete(assetId)
  }
  
  // 清空选择
  const clearSelection = () => {
    selectedAssets.value.clear()
  }
  
  // 工具函数
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }
  
  const getRandomColor = () => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    return colors[Math.floor(Math.random() * colors.length)]
  }
  
  const createAssetFromFile = async (filePath: string): Promise<Asset | null> => {
    // 这里应该实现文件信息读取逻辑
    return {
      id: generateId(),
      name: filePath.split(/[\\/]/).pop() || 'unknown',
      path: filePath,
      type: 'image',
      size: 0,
      createdAt: new Date(),
      modifiedAt: new Date(),
      tags: [],
      rating: 0
    }
  }
  
  return {
    currentLibrary,
    assets,
    folders,
    tags,
    selectedAssets,
    searchFilters,
    viewMode,
    sortBy,
    sortOrder,
    createLibrary,
    openLibrary,
    importAssets,
    createFolder,
    addTag,
    selectAsset,
    deselectAsset,
    clearSelection
  }
})