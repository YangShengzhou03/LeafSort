class TagManager {
  constructor() {
    this.tags = new Map()
    this.tagFrequency = new Map()
    this.tagGroups = new Map()
    this.tagGroupIndex = new Map()
    this.saveTimeout = null
    this.predictionCache = new Map()
    this.loadTags()
  }

  loadTags() {
    const savedTags = localStorage.getItem('leafview-tags')
    if (savedTags) {
      const data = JSON.parse(savedTags)
      this.tags = new Map(data.tags || [])
      this.tagFrequency = new Map(data.frequency || [])
      this.tagGroups = new Map(data.groups || [])
      
      this.buildTagGroupIndex()
    }
  }

  saveTags() {
    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout)
    }
    
    this.saveTimeout = setTimeout(() => {
      const data = {
        tags: Array.from(this.tags.entries()),
        frequency: Array.from(this.tagFrequency.entries()),
        groups: Array.from(this.tagGroups.entries())
      }
      localStorage.setItem('leafview-tags', JSON.stringify(data))
    }, 300)
  }

  predictTags(fileName, fileType, existingTags = []) {
    const cacheKey = `${fileName}-${fileType}-${existingTags.join(',')}`
    
    if (this.predictionCache.has(cacheKey)) {
      return this.predictionCache.get(cacheKey)
    }
    
    const startTime = performance.now()
    const existingTagSet = new Set(existingTags)
    
    const predictions = [
      ...this.getFilenamePredictions(fileName, existingTagSet),
      ...this.getTypePredictions(fileType, existingTagSet),
      ...this.getSimilarityPredictions(existingTags, existingTagSet)
    ]

    const result = this.deduplicateAndSort(predictions)
    
    this.predictionCache.set(cacheKey, result)
    this.manageCacheSize()
    this.logPredictionTime(startTime, fileName)
    
    return result
  }

  manageCacheSize() {
    if (this.predictionCache.size > 100) {
      const firstKey = this.predictionCache.keys().next().value
      this.predictionCache.delete(firstKey)
    }
  }

  logPredictionTime(startTime, fileName) {
    const endTime = performance.now()
    if (endTime - startTime > 100) {
      // console.log(`Tag prediction took ${endTime - startTime}ms for ${fileName}`)
    }
  }

  getFilenamePredictions(fileName, existingTagSet) {
    return this.extractKeywords(fileName)
      .filter(keyword => this.tagFrequency.has(keyword) && !existingTagSet.has(keyword))
      .map(keyword => ({
        tag: keyword,
        confidence: Math.min(this.tagFrequency.get(keyword) / 100, 0.9),
        source: 'filename'
      }))
  }

  getTypePredictions(fileType, existingTagSet) {
    return this.getTypeBasedTags(fileType)
      .filter(tag => !existingTagSet.has(tag))
      .map(tag => ({
        tag,
        confidence: 0.7,
        source: 'filetype'
      }))
  }

  getSimilarityPredictions(existingTags, existingTagSet) {
    return existingTags.length > 0 
      ? this.getSimilarTags(existingTags)
        .filter(tag => !existingTagSet.has(tag))
        .map(tag => ({
          tag,
          confidence: 0.6,
          source: 'similarity'
        }))
      : []
  }

  extractKeywords(text) {
    const words = text.toLowerCase()
      .replace(/[^\w\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 2)
    
    return [...new Set(words)]
  }

  getTypeBasedTags(fileType) {
    const typeMap = {
      'image': ['图片', '视觉', '设计'],
      'audio': ['音频', '音乐', '声音'],
      'video': ['视频', '影片', '动画'],
      'psd': ['PSD', '设计稿', '分层'],
      'ai': ['AI', '矢量', '插画'],
      'pdf': ['PDF', '文档', '手册']
    }
    
    return typeMap[fileType] || []
  }

  getSimilarTags(existingTags) {
    const similar = []
    existingTags.forEach(tag => {
      const group = this.findTagGroup(tag)
      if (group) {
        group.members.forEach(member => {
          if (member !== tag && !existingTags.includes(member)) {
            similar.push(member)
          }
        })
      }
    })
    
    return [...new Set(similar)]
  }

  findTagGroup(tag) {
    if (this.tagGroupIndex.has(tag)) {
      return this.tagGroupIndex.get(tag)
    }
    
    for (let [, group] of this.tagGroups.entries()) {
      if (group.members.includes(tag)) {
        return group
      }
    }
    return null
  }

  deduplicateAndSort(predictions) {
    const seen = new Set()
    const unique = []
    
    predictions.forEach(pred => {
      if (!seen.has(pred.tag)) {
        seen.add(pred.tag)
        unique.push(pred)
      }
    })
    
    return unique.sort((a, b) => b.confidence - a.confidence).slice(0, 5)
  }

  addTag(tag, materialId) {
    if (!this.tags.has(materialId)) {
      this.tags.set(materialId, new Set())
    }
    
    this.tags.get(materialId).add(tag)
    
    this.tagFrequency.set(tag, (this.tagFrequency.get(tag) || 0) + 1)
    
    this.saveTags()
  }

  addTagsBatch(tags, materialIds) {
    materialIds.forEach(materialId => {
      tags.forEach(tag => {
        this.addTag(tag, materialId)
      })
    })
  }

  removeTag(tag, materialId) {
    if (this.tags.has(materialId)) {
      this.tags.get(materialId).delete(tag)
      
      const frequency = this.tagFrequency.get(tag) || 0
      if (frequency > 1) {
        this.tagFrequency.set(tag, frequency - 1)
      } else {
        this.tagFrequency.delete(tag)
      }
      
      this.saveTags()
    }
  }

  getTags(materialId) {
    return this.tags.has(materialId) ? Array.from(this.tags.get(materialId)) : []
  }

  searchTags(query) {
    const results = []
    for (let [tag, frequency] of this.tagFrequency.entries()) {
      if (tag.toLowerCase().includes(query.toLowerCase())) {
        results.push({
          tag,
          frequency,
          materials: this.getMaterialsWithTag(tag).length
        })
      }
    }
    
    return results.sort((a, b) => b.frequency - a.frequency)
  }

  getMaterialsWithTag(tag) {
    const materials = []
    for (let [materialId, tagSet] of this.tags.entries()) {
      if (tagSet.has(tag)) {
        materials.push(materialId)
      }
    }
    return materials
  }

  createTagGroup(name, tags) {
    const groupId = Date.now().toString()
    const group = {
      name,
      members: tags,
      createdAt: new Date()
    }
    
    this.tagGroups.set(groupId, group)
    
    tags.forEach(tag => {
      this.tagGroupIndex.set(tag, group)
    })
    
    this.saveTags()
    return groupId
  }

  buildTagGroupIndex() {
    this.tagGroupIndex.clear()
    for (let [, group] of this.tagGroups.entries()) {
      group.members.forEach(tag => {
        this.tagGroupIndex.set(tag, group)
      })
    }
  }

  getPopularTags(limit = 10) {
    return Array.from(this.tagFrequency.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, limit)
      .map(([tag, frequency]) => ({ tag, frequency }))
  }
}

export default new TagManager()