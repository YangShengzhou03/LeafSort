import smartTagging from './smartTagging.js'
import { applyMaterialQuery, filterMaterials as filterList, sortMaterials as sortList, searchMaterials as searchList, groupDuplicates } from './materialQuery.js'

class MaterialManager {
  constructor() {
    this.materials = new Map()
    this.materialIndex = new Map()
    this.favorites = new Set()
    this.recentlyViewed = []
    this.subscribers = new Set()
    this.loadMaterials()
  }

  subscribe(callback) {
    if (typeof callback !== 'function') return () => {}
    this.subscribers.add(callback)
    return () => {
      this.subscribers.delete(callback)
    }
  }

  notify(event) {
    for (const cb of this.subscribers) {
      try {
        cb(event)
      } catch (e) {
        void e
      }
    }
  }

  loadMaterials() {
    const savedMaterials = localStorage.getItem('leafview-materials')
    const savedFavorites = localStorage.getItem('leafview-favorites')
    const savedRecent = localStorage.getItem('leafview-recent')
    
    if (savedMaterials) {
      const data = JSON.parse(savedMaterials)
      this.materials = new Map(data.materials || [])
      this.buildIndex()
    }
    
    if (savedFavorites) {
      this.favorites = new Set(JSON.parse(savedFavorites))
    }
    
    if (savedRecent) {
      this.recentlyViewed = JSON.parse(savedRecent)
    }
  }

  saveMaterials() {
    const data = {
      materials: Array.from(this.materials.entries()),
      lastModified: Date.now()
    }
    localStorage.setItem('leafview-materials', JSON.stringify(data))
    localStorage.setItem('leafview-favorites', JSON.stringify(Array.from(this.favorites)))
    localStorage.setItem('leafview-recent', JSON.stringify(this.recentlyViewed))
  }

  buildIndex() {
    this.materialIndex.clear()
    for (const [id, material] of this.materials) {
      this.indexMaterial(id, material)
    }
  }

  indexMaterial(id, material) {
    const keywords = [
      material.name.toLowerCase(),
      ...(material.tags || []).map(tag => tag.toLowerCase()),
      material.type.toLowerCase(),
      material.format.toLowerCase()
    ]
    
    keywords.forEach(keyword => {
      if (!this.materialIndex.has(keyword)) {
        this.materialIndex.set(keyword, new Set())
      }
      this.materialIndex.get(keyword).add(id)
    })
  }

  async addMaterial(file) {
    const id = this.generateId()
    const material = {
      id,
      name: file.name,
      path: file.path || file.name,
      size: file.size,
      type: this.detectFileType(file.name),
      format: this.getFileExtension(file.name),
      date: new Date().toISOString(),
      modified: new Date().toISOString(),
      tags: [],
      rating: 0,
      description: '',
      metadata: {},
      thumbnail: null,
      duration: '00:00',
      width: null,
      height: null,
      layers: null,
      isTrashed: false,
      trashedAt: null
    }

    // 提取文件元数据
    await this.extractFileMetadata(file, material)
    
    // 生成缩略图
    await this.generateThumbnail(file, material)
    
    // 自动添加智能标签
    material.tags = smartTagging.autoTagMaterial(material)
    
    this.materials.set(id, material)
    this.indexMaterial(id, material)
    this.addToRecent(id)
    
    // 更新搜索索引
    this.updateSearchIndex()
    this.saveMaterials()
    this.notify({ type: 'material-added', id })
    
    return material
  }

  extractFileMetadata(file, material) {
    // 根据文件类型提取不同的元数据
    switch (material.type) {
    case 'image':
      this.extractImageMetadata(file, material)
      break
    case 'audio':
      this.extractAudioMetadata(file, material)
      break
    case 'video':
      this.extractVideoMetadata(file, material)
      break
    case 'design':
      this.extractDesignMetadata(file, material)
      break
    default:
      // 默认不提取元数据
      break
    }
  }

  extractImageMetadata(file, material) {
    // 创建一个图片对象来获取尺寸信息
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const img = new Image()
        const reader = new FileReader()
        
        reader.onload = (e) => {
          img.onload = () => {
            material.width = img.width
            material.height = img.height
            resolve()
          }
          img.src = e.target.result
        }
        
        reader.readAsDataURL(file)
      } else {
        resolve()
      }
    })
  }

  extractAudioMetadata(file, material) {
    // 使用Audio对象提取音频元数据
    return new Promise((resolve) => {
      if (file.type.startsWith('audio/')) {
        const audio = new Audio()
        audio.preload = 'metadata'
        
        audio.onloadedmetadata = () => {
          material.duration = this.formatDuration(audio.duration)
          resolve()
        }
        
        audio.onerror = () => resolve()
        audio.src = URL.createObjectURL(file)
      } else {
        resolve()
      }
    })
  }

  extractVideoMetadata(file, material) {
    // 使用Video对象提取视频元数据
    return new Promise((resolve) => {
      if (file.type.startsWith('video/')) {
        const video = document.createElement('video')
        video.preload = 'metadata'
        
        video.onloadedmetadata = () => {
          material.duration = this.formatDuration(video.duration)
          material.width = video.videoWidth
          material.height = video.videoHeight
          resolve()
        }
        
        video.onerror = () => resolve()
        video.src = URL.createObjectURL(file)
      } else {
        resolve()
      }
    })
  }

  extractDesignMetadata(file, material) {
    // 设计文件元数据提取，这里只是模拟实现
    // 实际应用中可能需要第三方库来解析PSD、AI等文件格式
    material.layers = Math.floor(Math.random() * 50) + 1 // 模拟图层数量
  }

  generateThumbnail(file, material) {
    // 根据文件类型生成不同的缩略图
    switch (material.type) {
    case 'image':
      this.generateImageThumbnail(file, material)
      break
    case 'video':
      this.generateVideoThumbnail(file, material)
      break
    case 'audio':
      material.thumbnail = null // 音频不需要缩略图，使用默认UI
      break
    default:
      material.thumbnail = null // 默认不生成缩略图
      break
    }
  }

  generateImageThumbnail(file, material) {
    // 生成图片缩略图
    return new Promise((resolve) => {
      if (file.type.startsWith('image/')) {
        const img = new Image()
        const reader = new FileReader()
        
        reader.onload = (e) => {
          img.onload = () => {
            // 创建一个canvas来生成缩略图
            const canvas = document.createElement('canvas')
            const maxSize = 300
            
            let width = img.width
            let height = img.height
            
            // 保持宽高比，缩放到最大尺寸
            if (width > height) {
              height = Math.round((height * maxSize) / width)
              width = maxSize
            } else {
              width = Math.round((width * maxSize) / height)
              height = maxSize
            }
            
            canvas.width = width
            canvas.height = height
            
            const ctx = canvas.getContext('2d')
            ctx.drawImage(img, 0, 0, width, height)
            
            // 转换为base64格式
            material.thumbnail = canvas.toDataURL('image/jpeg', 0.8)
            resolve()
          }
          img.src = e.target.result
        }
        
        reader.readAsDataURL(file)
      } else {
        resolve()
      }
    })
  }

  generateVideoThumbnail(file, material) {
    // 生成视频缩略图
    return new Promise((resolve) => {
      if (file.type.startsWith('video/')) {
        const video = document.createElement('video')
        video.preload = 'metadata'
        
        video.onloadedmetadata = () => {
          // 设置视频播放位置到中间
          video.currentTime = video.duration / 2
        }
        
        video.ontimeupdate = () => {
          // 创建canvas来捕获视频帧
          const canvas = document.createElement('canvas')
          canvas.width = video.videoWidth
          canvas.height = video.videoHeight
          
          const ctx = canvas.getContext('2d')
          ctx.drawImage(video, 0, 0)
          
          // 转换为base64格式
          material.thumbnail = canvas.toDataURL('image/jpeg', 0.8)
          
          // 释放视频资源
          URL.revokeObjectURL(video.src)
          resolve()
        }
        
        video.onerror = () => resolve()
        video.src = URL.createObjectURL(file)
      } else {
        resolve()
      }
    })
  }

  formatDuration(seconds) {
    // 将秒数格式化为HH:MM:SS格式
    if (!seconds || isNaN(seconds)) return '00:00'
    
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }

  detectFileType(filename) {
    const ext = this.getFileExtension(filename).toLowerCase()
    const imageExts = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico']
    const videoExts = ['mp4', 'avi', 'mov', 'wmv', 'flv', 'webm', 'mkv']
    const audioExts = ['mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a']
    const designExts = ['psd', 'ai', 'sketch', 'figma', 'xd', 'afdesign']
    
    if (imageExts.includes(ext)) return 'image'
    if (videoExts.includes(ext)) return 'video'
    if (audioExts.includes(ext)) return 'audio'
    if (designExts.includes(ext)) return 'design'
    
    return 'document'
  }

  getFileExtension(filename) {
    return filename.split('.').pop() || ''
  }

  generateId() {
    return 'mat_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9)
  }

  getMaterial(id) {
    return this.materials.get(id)
  }

  getAllMaterials(options = {}) {
    const includeTrashed = Boolean(options.includeTrashed)
    const all = Array.from(this.materials.values())
    return includeTrashed ? all : all.filter(m => !m.isTrashed)
  }

  getMaterialsByType(type) {
    return this.getAllMaterials().filter(material => material.type === type)
  }

  getMaterialsByTag(tag) {
    return this.getAllMaterials().filter(material => 
      material.tags && material.tags.includes(tag)
    )
  }

  getMaterialsByScene(scene) {
    return this.getAllMaterials().filter(material => 
      material.tags && material.tags.includes(scene)
    )
  }

  getFavorites() {
    return this.getAllMaterials().filter(material =>
      this.favorites.has(material.id)
    )
  }

  getRecent() {
    return this.recentlyViewed
      .map(id => this.getMaterial(id))
      .filter(material => material)
      .filter(material => !material.isTrashed)
      .slice(0, 50)
  }

  getByCategory(category) {
    // 不同分类的映射关系
    const categoryMap = {
      'icons': ['svg', 'ico', 'icon'],
      'illustration': ['jpg', 'jpeg', 'png'],
      'photography': ['jpg', 'jpeg', 'png'],
      'audio': ['mp3', 'wav', 'ogg'],
      'video': ['mp4', 'avi', 'mov'],
      'fonts': ['ttf', 'otf', 'woff', 'woff2'],
      'packaging-templates': ['psd', 'ai', 'pdf'],
      'ui-design': ['psd', 'sketch', 'figma', 'xd', 'ai'],
      'game-concept': ['jpg', 'jpeg', 'png', 'psd'],
      'interior-design': ['jpg', 'jpeg', 'png', 'pdf']
    }
    
    const formats = categoryMap[category] || []
    return this.getAllMaterials().filter(material => 
      formats.includes(material.format.toLowerCase()) ||
      (material.tags || []).includes(category) ||
      (material.tags || []).includes(this.mapCategoryToTag(category))
    )
  }

  mapCategoryToTag(category) {
    const tagMap = {
      'packaging-templates': '包装模板',
      'ui-design': 'UI设计',
      'game-concept': '游戏概念',
      'interior-design': '室内设计',
      'ai-prompts': 'AI咒语',
      'illustration': '插画',
      'photography': '摄影'
    }
    return tagMap[category] || category
  }

  getDuplicates() {
    // 使用groupDuplicates函数检测重复文件
    const materials = this.getAllMaterials()
    const duplicates = groupDuplicates(materials)
    
    // 返回所有被标记为重复的文件
    return duplicates.reduce((result, group) => {
      if (group.length > 1) {
        result.push(...group)
      }
      return result
    }, [])
  }

  searchMaterials(query) {
    return searchList(this.getAllMaterials(), query)
  }

  updateMaterial(id, updates) {
    const material = this.getMaterial(id)
    if (material) {
      Object.assign(material, updates, { modified: new Date().toISOString() })
      this.materials.set(id, material)
      this.saveMaterials()
      this.notify({ type: 'material-updated', id })
      return true
    }
    return false
  }

  trashMaterial(id) {
    const material = this.getMaterial(id)
    if (material) {
      if (!material.isTrashed) {
        material.isTrashed = true
        material.trashedAt = new Date().toISOString()
        material.modified = new Date().toISOString()
        this.materials.set(id, material)
      }
      this.recentlyViewed = this.recentlyViewed.filter(viewedId => viewedId !== id)
      this.saveMaterials()
      this.notify({ type: 'material-trashed', id })
      return true
    }
    return false
  }

  restoreMaterial(id) {
    const material = this.getMaterial(id)
    if (material && material.isTrashed) {
      material.isTrashed = false
      material.trashedAt = null
      material.modified = new Date().toISOString()
      this.materials.set(id, material)
      this.saveMaterials()
      this.notify({ type: 'material-restored', id })
      return true
    }
    return false
  }

  deleteMaterialPermanently(id) {
    const material = this.getMaterial(id)
    if (material) {
      this.materials.delete(id)
      this.favorites.delete(id)
      this.recentlyViewed = this.recentlyViewed.filter(viewedId => viewedId !== id)
      this.buildIndex()
      this.saveMaterials()
      this.notify({ type: 'material-deleted', id })
      return true
    }
    return false
  }

  getTrashed() {
    return this.getAllMaterials({ includeTrashed: true }).filter(m => Boolean(m.isTrashed))
  }

  emptyTrash() {
    const trashed = this.getTrashed()
    trashed.forEach(m => {
      this.materials.delete(m.id)
      this.favorites.delete(m.id)
      this.recentlyViewed = this.recentlyViewed.filter(viewedId => viewedId !== m.id)
    })
    this.buildIndex()
    this.saveMaterials()
    this.notify({ type: 'trash-emptied', count: trashed.length })
    return trashed.length
  }

  toggleFavorite(id) {
    if (this.favorites.has(id)) {
      this.favorites.delete(id)
    } else {
      this.favorites.add(id)
    }
    this.saveMaterials()
    this.notify({ type: 'favorite-toggled', id, isFavorite: this.favorites.has(id) })
    return this.favorites.has(id)
  }

  addToRecent(id) {
    this.recentlyViewed = this.recentlyViewed.filter(viewedId => viewedId !== id)
    this.recentlyViewed.unshift(id)
    if (this.recentlyViewed.length > 100) {
      this.recentlyViewed = this.recentlyViewed.slice(0, 100)
    }
    this.saveMaterials()
  }

  updateSearchIndex() {
    // 更新搜索索引，确保搜索功能正常工作
    this.buildIndex()
  }

  getStatistics() {
    const materials = this.getAllMaterials()
    const stats = {
      total: materials.length,
      byType: {},
      byFormat: {},
      totalSize: 0,
      favorites: this.favorites.size,
      untagged: 0,
      averageRating: 0
    }

    let totalRating = 0
    let ratedCount = 0

    materials.forEach(material => {
      stats.totalSize += material.size || 0
      
      stats.byType[material.type] = (stats.byType[material.type] || 0) + 1
      stats.byFormat[material.format] = (stats.byFormat[material.format] || 0) + 1
      
      if (!material.tags || material.tags.length === 0) {
        stats.untagged++
      }
      
      if (material.rating > 0) {
        totalRating += material.rating
        ratedCount++
      }
    })

    stats.averageRating = ratedCount > 0 ? (totalRating / ratedCount).toFixed(1) : 0
    
    return stats
  }

  filterMaterials(filters) {
    return filterList(this.getAllMaterials({ includeTrashed: true }), filters)
  }

  sortMaterials(materials, sortBy) {
    return sortList(materials, sortBy)
  }

  getFilteredAndSortedMaterials(filters, sortBy) {
    const filtered = this.filterMaterials(filters)
    return this.sortMaterials(filtered, sortBy)
  }

  applyQuery(query) {
    return applyMaterialQuery(this.getAllMaterials({ includeTrashed: true }), query)
  }

  findDuplicates() {
    return groupDuplicates(this.getAllMaterials({ includeTrashed: true }))
  }

  renameTag(oldTag, newTag) {
    const oldName = typeof oldTag === 'string' ? oldTag.trim() : ''
    const newName = typeof newTag === 'string' ? newTag.trim() : ''
    if (!oldName || !newName || oldName === newName) return 0

    let changed = 0
    for (const [id, material] of this.materials.entries()) {
      if (!material || !Array.isArray(material.tags)) continue
      const tags = material.tags
      if (!tags.includes(oldName)) continue
      const next = tags.filter(t => t !== oldName)
      if (!next.includes(newName)) next.push(newName)
      material.tags = next
      material.modified = new Date().toISOString()
      this.materials.set(id, material)
      changed++
    }

    if (changed > 0) {
      this.updateSearchIndex()
      this.saveMaterials()
      this.notify({ type: 'tag-renamed', oldTag: oldName, newTag: newName, changed })
    }
    return changed
  }

  deleteTag(tag) {
    const name = typeof tag === 'string' ? tag.trim() : ''
    if (!name) return 0

    let changed = 0
    for (const [id, material] of this.materials.entries()) {
      if (!material || !Array.isArray(material.tags)) continue
      if (!material.tags.includes(name)) continue
      material.tags = material.tags.filter(t => t !== name)
      material.modified = new Date().toISOString()
      this.materials.set(id, material)
      changed++
    }

    if (changed > 0) {
      this.updateSearchIndex()
      this.saveMaterials()
      this.notify({ type: 'tag-deleted', tag: name, changed })
    }
    return changed
  }

  exportMaterials(format = 'json') {
    const materials = this.getAllMaterials()
    
    switch (format) {
    case 'json':
      return JSON.stringify(materials, null, 2)
    case 'csv':
      return this.exportToCSV(materials)
    case 'xml':
      return this.exportToXML(materials)
    default:
      return JSON.stringify(materials)
    }
  }

  exportToCSV(materials) {
    const headers = ['ID', 'Name', 'Type', 'Format', 'Size', 'Date', 'Tags', 'Rating']
    const rows = materials.map(material => [
      material.id,
      `"${material.name}"`,
      material.type,
      material.format,
      material.size,
      material.date,
      `"${(material.tags || []).join(',')}"`,
      material.rating
    ])
    
    return [headers.join(','), ...rows.map(row => row.join(','))].join('\n')
  }

  exportToXML(materials) {
    let xml = '<?xml version="1.0" encoding="UTF-8"?>\n<materials>\n'
    
    materials.forEach(material => {
      xml += `  <material id="${material.id}">\n`
      xml += `    <name>${this.escapeXML(material.name)}</name>\n`
      xml += `    <type>${material.type}</type>\n`
      xml += `    <format>${material.format}</format>\n`
      xml += `    <size>${material.size}</size>\n`
      xml += `    <date>${material.date}</date>\n`
      xml += `    <tags>${(material.tags || []).join(',')}</tags>\n`
      xml += `    <rating>${material.rating}</rating>\n`
      xml += '  </material>\n'
    })
    
    xml += '</materials>'
    return xml
  }

  escapeXML(str) {
    return str.replace(/[<>&"']/g, char => {
      switch (char) {
      case '<': return '&lt;'
      case '>': return '&gt;'
      case '&': return '&amp;'
      case '"': return '&quot;'
      case '\'': return '&apos;'
      default: return char
      }
    })
  }
}

export default new MaterialManager()
