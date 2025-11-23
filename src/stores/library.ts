import { defineStore } from 'pinia'
import { ref, reactive, computed } from 'vue'
import type { Library, Asset, Folder, Tag, Activity } from '@/types'

export const useLibraryStore = defineStore('library', () => {
  // 当前激活的素材库
  const currentLibrary = ref<Library | null>(null)
  
  // 素材列表
  const assets = ref<Asset[]>([])
  
  // 文件夹结构
  const folders = ref<Folder[]>([])
  
  // 标签系统
  const tags = ref<Tag[]>([])
  const activeTagId = ref<string | null>(null)
  
  // 当前选中的素材
  const selectedAssets = ref<Set<string>>(new Set())
  
  // 最近活动
  const recentActivities = ref<Activity[]>([])
  
  // 收藏的素材
  const favoriteAssets = ref<string[]>([])
  
  // 搜索条件
  const searchFilters = reactive({
    keyword: '',
    fileType: '',
    sizeRange: { min: 0, max: Infinity },
    dateRange: { start: null, end: null },
    tags: [] as string[],
    rating: 0
  })
  
  // 搜索历史
  const searchHistory = ref<string[]>([])
    
  // 添加搜索历史
  const addSearchHistory = (keyword: string) => {
    // 移除重复项
    const index = searchHistory.value.indexOf(keyword)
    if (index !== -1) {
      searchHistory.value.splice(index, 1)
    }
    
    // 添加到开头
    searchHistory.value.unshift(keyword)
    
    // 限制历史记录数量
    if (searchHistory.value.length > 20) {
      searchHistory.value = searchHistory.value.slice(0, 20)
    }
    
    // 保存到本地存储
    saveSearchHistoryToLocalStorage()
  }
    
  // 清除搜索历史
  const clearSearchHistory = () => {
    searchHistory.value = []
    // 保存到本地存储
    saveSearchHistoryToLocalStorage()
  }
  
  // 保存搜索历史到本地存储
  const saveSearchHistoryToLocalStorage = () => {
    try {
      localStorage.setItem('searchHistory', JSON.stringify(searchHistory.value))
    } catch (error) {
      console.error('保存搜索历史失败:', error)
    }
  }
  
  // 从本地存储加载搜索历史
  const loadSearchHistoryFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('searchHistory')
      if (saved) {
        searchHistory.value = JSON.parse(saved)
      }
    } catch (error) {
      console.error('加载搜索历史失败:', error)
    }
  }
  
  // 当前选中的文件夹
  const currentFolderId = ref<string | null>(null)
  
  // 视图状态
  const showImportDialog = ref(false)
  const showSmartFolders = ref(false)
  const showAdvancedSearch = ref(false)
  const showLibrarySettings = ref(false)
  const showRecentImports = ref(false)
  const showTagManager = ref(false)
  const showFolderManager = ref(false)
  
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
  
  // 删除资产
  const deleteAssets = (assetIds: string[]) => {
    const deletedAssets = assets.value.filter(asset => assetIds.includes(asset.id))
    assets.value = assets.value.filter(asset => !assetIds.includes(asset.id))
    
    // 清除选中状态
    assetIds.forEach(id => selectedAssets.value.delete(id))
    
    // 添加到最近活动
    deletedAssets.forEach(asset => {
      addRecentActivity({
        type: 'delete',
        assetId: asset.id,
        timestamp: new Date(),
        description: `删除了 ${asset.name}`
      })
    })
    
    // 更新素材库统计信息
    updateLibraryStats()
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 移动资产
  const moveAssets = (assetIds: string[], folderId: string | null) => {
    assets.value.forEach(asset => {
      if (assetIds.includes(asset.id)) {
        asset.folderId = folderId
        asset.updatedAt = new Date()
        
        // 添加到最近活动
        addRecentActivity({
          type: 'move',
          assetId: asset.id,
          timestamp: new Date(),
          description: `移动了 ${asset.name} 到 ${folderId ? getFolderName(folderId) : '根目录'}`
        })
      }
    })
    
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 重命名资产
  const renameAsset = (assetId: string, newName: string) => {
    const asset = assets.value.find(a => a.id === assetId)
    if (asset) {
      const oldName = asset.name
      asset.name = newName
      asset.updatedAt = new Date()
      
      // 添加到最近活动
      addRecentActivity({
        type: 'rename',
        assetId: asset.id,
        timestamp: new Date(),
        description: `重命名了 ${oldName} 为 ${newName}`
      })
      
      // 保存到本地存储
      saveToLocalStorage()
    }
  }
  
  // 更新资产标签
  const updateAssetTags = (assetId: string, newTags: string[]) => {
    const asset = assets.value.find(a => a.id === assetId)
    if (asset) {
      asset.tags = newTags
      asset.updatedAt = new Date()
      
      // 添加到最近活动
      addRecentActivity({
        type: 'tag',
        assetId: asset.id,
        timestamp: new Date(),
        description: `更新了 ${asset.name} 的标签`
      })
      
      // 更新标签计数
      updateTagCounts()
      // 保存到本地存储
      saveToLocalStorage()
    }
  }
  
  // 添加标签到资产
  const addTagToAsset = async (assetId: string, tagName: string) => {
    const asset = assets.value.find(a => a.id === assetId)
    const tag = tags.value.find(t => t.name === tagName)
    
    if (asset && tag && !asset.tags.includes(tagName)) {
      asset.tags.push(tagName)
      asset.updatedAt = new Date()
      
      saveToLocalStorage()
      updateTagCounts()
      
      addRecentActivity({
        type: 'tag',
        assetId,
        timestamp: new Date(),
        description: `添加标签到资产: ${tagName}`
      })
    }
  }
  
  // 从资产中移除标签
  const removeTagFromAsset = async (assetId: string, tagName: string) => {
    const asset = assets.value.find(a => a.id === assetId)
    
    if (asset) {
      asset.tags = asset.tags.filter(tag => tag !== tagName)
      asset.updatedAt = new Date()
      
      saveToLocalStorage()
      updateTagCounts()
      
      addRecentActivity({
        type: 'tag',
        assetId,
        timestamp: new Date(),
        description: `从资产中移除标签: ${tagName}`
      })
    }
  }
  
  // 更新资产评分
  const updateAssetRating = (assetId: string, rating: number) => {
    const asset = assets.value.find(a => a.id === assetId)
    if (asset) {
      asset.rating = rating
      asset.updatedAt = new Date()
      
      // 添加到最近活动
      addRecentActivity({
        type: 'rating',
        assetId: asset.id,
        timestamp: new Date(),
        description: `评分了 ${asset.name} 为 ${rating} 星`
      })
      
      // 保存到本地存储
      saveToLocalStorage()
    }
  }
  
  // 收藏/取消收藏资产
  const toggleFavorite = (assetId: string) => {
    const index = favoriteAssets.value.indexOf(assetId)
    if (index > -1) {
      favoriteAssets.value.splice(index, 1)
    } else {
      favoriteAssets.value.push(assetId)
    }
    
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 批量操作 - 添加标签
  const batchAddTags = (assetIds: string[], tagsToAdd: string[]) => {
    assetIds.forEach(assetId => {
      const asset = assets.value.find(a => a.id === assetId)
      if (asset) {
        // 添加不存在的标签
        tagsToAdd.forEach(tag => {
          if (!asset.tags.includes(tag)) {
            asset.tags.push(tag)
          }
        })
        asset.updatedAt = new Date()
      }
    })
    
    // 更新标签计数
    updateTagCounts()
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 批量操作 - 移除标签
  const batchRemoveTags = (assetIds: string[], tagsToRemove: string[]) => {
    assetIds.forEach(assetId => {
      const asset = assets.value.find(a => a.id === assetId)
      if (asset) {
        asset.tags = asset.tags.filter(tag => !tagsToRemove.includes(tag))
        asset.updatedAt = new Date()
      }
    })
    
    // 更新标签计数
    updateTagCounts()
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 计算属性 - 获取收藏的资产
  const favoritedAssets = computed(() => {
    return assets.value.filter(asset => favoriteAssets.value.includes(asset.id))
  })
  
  // 计算属性 - 获取最近添加的资产
  const recentlyAddedAssets = computed(() => {
    return [...assets.value]
      .sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
      .slice(0, 20)
  })
  
  // 计算属性 - 获取按文件夹分组的资产
  const assetsByFolder = computed(() => {
    const result: Record<string, Asset[]> = {}
    assets.value.forEach(asset => {
      const folderId = asset.folderId || 'root'
      if (!result[folderId]) {
        result[folderId] = []
      }
      result[folderId].push(asset)
    })
    return result
  })
  
  // 计算属性 - 获取按标签分组的资产
  const assetsByTag = computed(() => {
    const result: Record<string, Asset[]> = {}
    assets.value.forEach(asset => {
      asset.tags.forEach(tag => {
        if (!result[tag]) {
          result[tag] = []
        }
        if (!result[tag].includes(asset)) {
          result[tag].push(asset)
        }
      })
    })
    return result
  })
  
  // 计算属性 - 获取最近资产
  const recentAssets = computed(() => {
    const now = new Date()
    const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    return assets.value.filter(asset => new Date(asset.createdAt) > sevenDaysAgo)
  })
  
  // 计算属性 - 获取未标记资产
  const untaggedAssets = computed(() => {
    return assets.value.filter(asset => asset.tags.length === 0)
  })
  
  // 计算属性 - 获取当前文件夹的资产
  const currentFolderAssets = computed(() => {
    if (!currentFolderId.value) {
      return assets.value.filter(asset => !asset.folderId)
    }
    return assets.value.filter(asset => asset.folderId === currentFolderId.value)
  })

  // 计算属性：热门标签（使用频率最高的标签）
  const popularTags = computed(() => {
    // 返回按资产数量排序的前5个标签
    return [...tags.value]
      .sort((a, b) => (b.assetCount || 0) - (a.assetCount || 0))
      .slice(0, 5)
  })

  // 计算属性：按标签筛选的资产
  const filteredByTagAssets = computed(() => {
    if (!activeTagId.value) return []
    return assets.value.filter(asset => asset.tags.includes(activeTagId.value!))
  })

  // 计算属性：当前展示的资产列表（根据当前筛选条件）
  const currentDisplayAssets = computed(() => {
    // 有活跃标签时，显示按标签筛选的资产
    if (activeTagId.value) {
      return assets.value.filter(asset => asset.tags.includes(activeTagId.value!))
    }
    // 否则显示当前文件夹的资产
    return currentFolderAssets.value
  })
  
  // 工具函数已在上方定义
  
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
      rating: 0,
      metadata: {}
    }
  }
  
  // 工具函数
  const generateId = () => {
    return Date.now().toString(36) + Math.random().toString(36).substr(2)
  }
  
  const getRandomColor = () => {
    const colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57', '#FF9FF3', '#54A0FF']
    return colors[Math.floor(Math.random() * colors.length)]
  }
  
  // 设置当前文件夹
  const setCurrentFolder = (folderId: string | null) => {
    currentFolderId.value = folderId
    // 清除搜索过滤器
    searchFilters.keyword = ''
    searchFilters.tags = []
  }
  
  // 筛选最近资产
  const filterRecentAssets = () => {
    currentFolderId.value = null
    // 可以在这里添加额外的过滤逻辑
  }
  
  // 筛选未标记资产
  const filterUntaggedAssets = () => {
    currentFolderId.value = null
    // 可以在这里添加额外的过滤逻辑
  }
  
  // 按标签筛选
  const filterByTag = (tagId: string) => {
    // 如果点击的是当前活跃标签，则清除筛选
    if (activeTagId.value === tagId) {
      activeTagId.value = null
      searchFilters.tags = []
      return
    }
    
    activeTagId.value = tagId
    // 重置文件夹筛选，确保只按标签筛选
    currentFolderId.value = null
    
    const tag = tags.value.find(t => t.id === tagId)
    if (tag) {
      searchFilters.tags = [tag.name]
      
      // 添加活动记录
      addRecentActivity({
        type: 'filter',
        assetId: null,
        timestamp: new Date(),
        description: `筛选标签: ${tag.name}`
      })
    }
  }
  
  // 清除标签筛选
  const clearTagFilter = () => {
    activeTagId.value = null
    searchFilters.tags = []
  }
  
  // 重命名文件夹
  const renameFolder = async (folderId: string, newName: string) => {
    const folder = folders.value.find(f => f.id === folderId)
    if (folder) {
      folder.name = newName
      
      // 添加到最近活动
      addRecentActivity({
        type: 'folder',
        folderId: folder.id,
        timestamp: new Date(),
        description: `重命名了文件夹 ${folder.name}`
      })
      
      // 保存到本地存储
      saveToLocalStorage()
    }
  }
  
  // 删除文件夹
  const deleteFolder = async (folderId: string) => {
    // 先删除子文件夹
    const childFolders = folders.value.filter(f => f.parentId === folderId)
    for (const child of childFolders) {
      await deleteFolder(child.id)
    }
    
    // 移动文件夹中的资产到根目录
    assets.value.forEach(asset => {
      if (asset.folderId === folderId) {
        asset.folderId = null
        asset.updatedAt = new Date()
      }
    })
    
    // 删除文件夹
    folders.value = folders.value.filter(f => f.id !== folderId)
    
    // 添加到最近活动
    addRecentActivity({
      type: 'folder',
      folderId: folderId,
      timestamp: new Date(),
      description: `删除了文件夹`
    })
    
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  // 创建标签
  const createTag = async (tagName: string) => {
    // 检查标签是否已存在
    if (tags.value.some(tag => tag.name === tagName)) {
      throw new Error('标签已存在')
    }
    
    const newTag = {
      id: generateId(),
      name: tagName,
      color: getRandomColor(),
      assetCount: 0,
      createdAt: new Date().toISOString()
    }
    tags.value.push(newTag)
    
    // 保存到本地存储
    saveToLocalStorage()
    
    // 添加活动记录
    addRecentActivity({
      type: 'tag',
      assetId: null,
      timestamp: new Date(),
      description: `创建了标签: ${tagName}`
    })
  }
  
  // 重命名标签
  const renameTag = async (tagId: string, newName: string) => {
    const tagIndex = tags.value.findIndex(tag => tag.id === tagId)
    if (tagIndex !== -1) {
      // 检查新名称是否与其他标签重复
      if (tags.value.some(tag => tag.id !== tagId && tag.name === newName)) {
        throw new Error('标签名称已存在')
      }
      
      const oldName = tags.value[tagIndex].name
      tags.value[tagIndex].name = newName
      
      // 更新使用该标签的所有资产
      assets.value.forEach(asset => {
        asset.tags = asset.tags.map(tag => tag === oldName ? newName : tag)
      })
      
      saveToLocalStorage()
      
      // 添加活动记录
      addRecentActivity({
        type: 'tag',
        assetId: null,
        timestamp: new Date(),
        description: `重命名标签: ${oldName} -> ${newName}`
      })
    }
  }
  
  // 删除标签
  const deleteTag = async (tagId: string) => {
    const tag = tags.value.find(t => t.id === tagId)
    if (tag) {
      const tagName = tag.name
      
      // 从所有资产中移除该标签
      assets.value.forEach(asset => {
        asset.tags = asset.tags.filter(t => t !== tagName)
        asset.updatedAt = new Date()
      })
      
      // 删除标签
      tags.value = tags.value.filter(t => t.id !== tagId)
      
      // 如果当前正在按该标签筛选，清除筛选
      if (activeTagId.value === tagId) {
        activeTagId.value = null
      }
      
      // 更新标签计数
      updateTagCounts()
      // 保存到本地存储
      saveToLocalStorage()
      
      // 添加活动记录
      addRecentActivity({
        type: 'tag',
        assetId: null,
        timestamp: new Date(),
        description: `删除了标签: ${tagName}`
      })
    }
  }
  
  // 更新标签资产数量
  const updateTagAssetCounts = () => {
    // 重置所有标签的资产数量
    tags.value.forEach(tag => {
      tag.assetCount = assets.value.filter(asset => asset.tags.includes(tag.name)).length
    })
  }
  
  // 导入截图
  const importScreenshot = async (screenshotData: string) => {
    const newAsset: Asset = {
      id: generateId(),
      name: `screenshot_${new Date().getTime()}.png`,
      path: screenshotData, // 实际应该保存到文件系统
      type: 'image',
      size: 0,
      createdAt: new Date(),
      modifiedAt: new Date(),
      tags: ['截图'],
      rating: 0,
      folderId: currentFolderId.value || undefined,
      metadata: {}
    }
    
    assets.value.push(newAsset)
    
    // 添加到最近活动
    addRecentActivity({
      type: 'import',
      assetId: newAsset.id,
      timestamp: new Date(),
      description: `导入了截图`
    })
    
    // 更新素材库统计信息
    updateLibraryStats()
    // 保存到本地存储
    saveToLocalStorage()
  }
  
  const getFileType = (fileName: string): string => {
    const extension = fileName.split('.').pop()?.toLowerCase() || ''
    const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'tiff']
    const videoExtensions = ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm']
    const audioExtensions = ['mp3', 'wav', 'aac', 'flac', 'ogg']
    const documentExtensions = ['pdf', 'doc', 'docx', 'txt', 'xlsx', 'pptx']
    
    if (imageExtensions.includes(extension)) return 'image'
    if (videoExtensions.includes(extension)) return 'video'
    if (audioExtensions.includes(extension)) return 'audio'
    if (documentExtensions.includes(extension)) return 'document'
    return 'other'
  }
  
  const generateThumbnail = async (file: File): Promise<string> => {
    // 模拟生成缩略图，实际应用中应该根据文件类型生成不同的缩略图
    return new Promise((resolve) => {
      resolve(`data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><rect width="100" height="100" fill="%23f0f0f0"/><text x="50" y="50" font-size="12" text-anchor="middle" dominant-baseline="middle" fill="%23666">${file.name}</text></svg>`)
    })
  }
  
  const addRecentActivity = (activity: Activity) => {
    recentActivities.value.unshift(activity)
    // 只保留最近100条活动
    if (recentActivities.value.length > 100) {
      recentActivities.value = recentActivities.value.slice(0, 100)
    }
  }
  
  const getFolderName = (folderId: string): string => {
    const folder = folders.value.find(f => f.id === folderId)
    return folder?.name || '未知文件夹'
  }
  
  const updateLibraryStats = () => {
    if (currentLibrary.value) {
      currentLibrary.value.assetCount = assets.value.length
      currentLibrary.value.size = assets.value.reduce((sum, asset) => sum + asset.size, 0)
    }
  }
  
  const updateTagCounts = () => {
    // 更新所有标签的资产计数
    tags.value.forEach(tag => {
      tag.assetCount = assets.value.filter(asset => asset.tags.includes(tag.name)).length
    })
  }
  
  const saveToLocalStorage = () => {
    // 保存当前状态到本地存储
    try {
      localStorage.setItem('libraryState', JSON.stringify({
        assets: assets.value,
        folders: folders.value,
        tags: tags.value,
        favoriteAssets: favoriteAssets.value,
        recentActivities: recentActivities.value,
        searchHistory: searchHistory.value
      }))
    } catch (error) {
      console.error('保存状态到本地存储失败:', error)
    }
  }
  
  const loadFromLocalStorage = () => {
    // 从本地存储加载状态
    try {
      const savedState = localStorage.getItem('libraryState')
      if (savedState) {
        const state = JSON.parse(savedState)
        assets.value = state.assets || []
        folders.value = state.folders || []
        tags.value = state.tags || []
        favoriteAssets.value = state.favoriteAssets || []
        recentActivities.value = state.recentActivities || []
        searchHistory.value = state.searchHistory || []
      } else {
        // 如果没有完整的状态，尝试只加载搜索历史
        loadSearchHistoryFromLocalStorage()
      }
    } catch (error) {
      console.error('从本地存储加载状态失败:', error)
    }
  }
  
  // 初始化时加载本地存储数据
  loadFromLocalStorage()
  
  return {
    // 状态
    currentLibrary,
    assets,
    folders,
    tags,
    selectedAssets,
    searchFilters,
    searchHistory,
    viewMode,
    sortBy,
    sortOrder,
    favoriteAssets,
    recentActivities,
    currentFolderId,
    activeTagId,
    showImportDialog,
    showSmartFolders,
    showAdvancedSearch,
    showLibrarySettings,
    showRecentImports,
    showTagManager,
    showFolderManager,
    
    // 计算属性
    favoritedAssets,
    recentlyAddedAssets,
    assetsByFolder,
    assetsByTag,
    recentAssets,
    untaggedAssets,
    currentFolderAssets,
    popularTags,
    filteredByTagAssets,
    currentDisplayAssets,
    
    // 方法
    createLibrary,
    openLibrary,
    importAssets,
    importWebCapture,
    importScreenCapture,
    importScreenshot,
    createFolder,
    createTag,
    deleteTag,
    renameTag,
    renameFolder,
    deleteFolder,
    addTag,
    addTagToAsset,
    removeTagFromAsset,
    selectAsset,
    deselectAsset,
    clearSelection,
    deleteAssets,
    moveAssets,
    renameAsset,
    updateAssetTags,
    updateAssetRating,
    toggleFavorite,
    batchAddTags,
    batchRemoveTags,
    setCurrentFolder,
    filterRecentAssets,
    filterUntaggedAssets,
    filterByTag,
    clearTagFilter,
    updateTagAssetCounts,
    updateTagCounts,
    saveToLocalStorage,
    loadFromLocalStorage,
    addSearchHistory,
    clearSearchHistory
  }
})