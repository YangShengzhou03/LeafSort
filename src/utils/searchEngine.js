import materialManager from './materialManager.js'

class SearchEngine {
  constructor() {
    this.index = new Map()
    this.filters = {
      type: new Set(),
      format: new Set(),
      size: { min: 0, max: Infinity },
      date: { start: null, end: null },
      rating: { min: 0, max: 5 },
      tags: new Set()
    }
    this.searchHistory = []
    this.suggestionsCache = new Map()
    
    // 加载搜索历史并构建索引
    this.loadSearchHistory()
    this.buildIndex()
  }

  buildIndex(materials = null) {
    this.index.clear()
    
    // 如果没有提供materials，则从materialManager获取
    const materialsToIndex = materials || materialManager.getAllMaterials()
    
    materialsToIndex.forEach(material => {
      this.indexMaterial(material)
    })
    
    this.updateFilterOptions(materialsToIndex)
  }

  indexMaterial(material) {
    const terms = this.extractSearchTerms(material)
    
    terms.forEach(term => {
      if (!this.index.has(term)) {
        this.index.set(term, new Set())
      }
      this.index.get(term).add(material.id)
    })
  }

  extractSearchTerms(material) {
    const terms = new Set()
    
    // 文件名分词
    const nameTerms = this.tokenize(material.name)
    nameTerms.forEach(term => terms.add(term))
    
    // 标签分词
    if (material.tags) {
      material.tags.forEach(tag => {
        const tagTerms = this.tokenize(tag)
        tagTerms.forEach(term => terms.add(term))
      })
    }
    
    // 智能标签分词
    if (material.scenes) {
      material.scenes.forEach(scene => {
        const sceneTerms = this.tokenize(scene)
        sceneTerms.forEach(term => terms.add(term))
      })
    }
    
    if (material.location) {
      const locationTerms = this.tokenize(material.location)
      locationTerms.forEach(term => terms.add(term))
    }
    
    if (material.people) {
      material.people.forEach(person => {
        if (person.name) {
          const personTerms = this.tokenize(person.name)
          personTerms.forEach(term => terms.add(term))
        }
      })
    }
    
    // 文件类型和格式
    terms.add(material.type)
    terms.add(material.format)
    
    // 添加描述信息（如果有）
    if (material.description) {
      const descTerms = this.tokenize(material.description)
      descTerms.forEach(term => terms.add(term))
    }
    
    return terms
  }

  tokenize(text) {
    if (!text) return []
    
    const normalizedText = text.toLowerCase().trim()
    
    // 中文分词增强：支持常见词语
    const chineseWords = this.extractChineseWords(normalizedText)
    
    // 英文分词（按单词分割）
    const englishTokens = normalizedText
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(token => token.length > 1)
    
    // 数字和特殊格式
    const specialTokens = normalizedText.match(/\b\d+[xkp]?\b/g) || []
    
    // 日期提取
    const dateTokens = this.extractDates(normalizedText)
    
    // 组合所有分词
    const allTokens = [...chineseWords, ...englishTokens, ...specialTokens, ...dateTokens]
    
    return [...new Set(allTokens)]
      .filter(token => token && token.length > 0)
  }
  
  // 提取中文词语（简单版本，基于常见词汇）
  extractChineseWords(text) {
    const commonWords = [
      // 场景相关
      '风景', '人物', '动物', '食物', '旅行', '建筑', '自然', '城市', '海滩', '山脉',
      '森林', '湖泊', '河流', '公园', '博物馆', '餐厅', '聚会', '婚礼', '生日',
      // 人物相关
      '家人', '朋友', '孩子', '婴儿', '老人', '情侣', '同学', '同事',
      // 时间相关
      '昨天', '今天', '明天', '上周', '上周日', '本周', '本周六', '上月', '下月',
      '去年', '今年', '明年', '春天', '夏天', '秋天', '冬天',
      // 地点相关
      '北京', '上海', '广州', '深圳', '成都', '杭州', '南京', '西安',
      '公园', '广场', '街道', '学校', '医院', '酒店', '机场', '车站',
      // 动作相关
      '拍摄', '旅行', '吃饭', '聚会', '游玩', '参观', '运动', '工作'
    ]
    
    const words = []
    
    // 查找常见词语
    commonWords.forEach(word => {
      if (text.includes(word)) {
        words.push(word)
      }
    })
    
    // 如果没有找到常见词语，回退到单字分词
    if (words.length === 0) {
      const chineseChars = text.match(/[\u4e00-\u9fa5]/g) || []
      return chineseChars
    }
    
    return words
  }
  
  // 提取日期
  extractDates(text) {
    const datePatterns = [
      /(\d{4})年(\d{1,2})月(\d{1,2})日/,  // 2023年12月25日
      /(\d{2})年(\d{1,2})月(\d{1,2})日/,  // 23年12月25日
      /(\d{4})-(\d{1,2})-(\d{1,2})/,      // 2023-12-25
      /(\d{1,2})\/(\d{1,2})\/(\d{4})/,    // 12/25/2023
      /(\d{1,2})\/(\d{1,2})\/(\d{2})/      // 12/25/23
    ]
    
    const dates = []
    
    datePatterns.forEach(pattern => {
      const matches = text.match(pattern)
      if (matches) {
        dates.push(matches[0])
      }
    })
    
    return dates
  }
  
  // 解析自然语言查询
  parseNaturalLanguageQuery(query) {
    const lowerQuery = query.toLowerCase()
    const parsed = {
      keywords: [],
      scenes: [],
      people: [],
      locations: [],
      timeRange: null,
      mustInclude: [],
      mustExclude: [],
      intent: 'general'
    }
    
    // 意图识别
    if (lowerQuery.includes('视频')) {
      parsed.intent = 'video'
    } else if (lowerQuery.includes('照片') || lowerQuery.includes('图片')) {
      parsed.intent = 'photo'
    }
    
    if (lowerQuery.includes('相似') || lowerQuery.includes('类似')) {
      parsed.intent = 'similar'
    }
    
    if (lowerQuery.includes('删除') || lowerQuery.includes('清理')) {
      parsed.intent = 'delete'
    }
    
    // 日期过滤
    if (lowerQuery.includes('昨天')) {
      const yesterday = new Date()
      yesterday.setDate(yesterday.getDate() - 1)
      parsed.timeRange = {
        start: yesterday,
        end: yesterday
      }
    } else if (lowerQuery.includes('今天')) {
      const today = new Date()
      parsed.timeRange = {
        start: today,
        end: today
      }
    } else if (lowerQuery.includes('明天')) {
      const tomorrow = new Date()
      tomorrow.setDate(tomorrow.getDate() + 1)
      parsed.timeRange = {
        start: tomorrow,
        end: tomorrow
      }
    } else if (lowerQuery.includes('上周')) {
      const lastWeek = new Date()
      lastWeek.setDate(lastWeek.getDate() - 7)
      parsed.timeRange = {
        start: lastWeek,
        end: new Date()
      }
    } else if (lowerQuery.includes('上月')) {
      const lastMonth = new Date()
      lastMonth.setMonth(lastMonth.getMonth() - 1)
      parsed.timeRange = {
        start: lastMonth,
        end: new Date()
      }
    } else if (lowerQuery.includes('去年')) {
      const lastYear = new Date()
      lastYear.setFullYear(lastYear.getFullYear() - 1)
      parsed.timeRange = {
        start: lastYear,
        end: new Date()
      }
    }
    
    // 场景识别
    const sceneKeywords = {
      '风景': '风景',
      '人物': '人物',
      '动物': '动物',
      '宠物': '动物',
      '狗': '动物',
      '猫': '动物',
      '食物': '食物',
      '美食': '食物',
      '旅行': '旅行',
      '建筑': '建筑',
      '自然': '风景',
      '城市': '建筑',
      '海滩': '风景',
      '山脉': '风景',
      '森林': '风景',
      '湖泊': '风景',
      '河流': '风景'
    }
    
    Object.entries(sceneKeywords).forEach(([keyword, scene]) => {
      if (lowerQuery.includes(keyword)) {
        parsed.scenes.push(scene)
      }
    })
    
    // 人物识别
    const peopleKeywords = ['小明', '小红', '爸爸', '妈妈', '爷爷', '奶奶', '朋友', '家人', '孩子', '婴儿', '老人', '情侣', '同学', '同事']
    peopleKeywords.forEach(person => {
      if (lowerQuery.includes(person)) {
        parsed.people.push(person)
      }
    })
    
    // 地点识别
    const locationKeywords = ['北京', '上海', '广州', '深圳', '杭州', '西安', '长城', '天安门', '公园', '海滩', '山脉', '森林', '湖泊', '河流', '成都', '南京', '广场', '街道', '学校', '医院', '酒店', '机场', '车站']
    locationKeywords.forEach(location => {
      if (lowerQuery.includes(location)) {
        parsed.locations.push(location)
      }
    })
    
    // 排除词识别
    if (lowerQuery.includes('不') || lowerQuery.includes('排除')) {
      const excludeWords = lowerQuery.split(/[不排除]/)
      if (excludeWords.length > 1) {
        parsed.mustExclude = this.tokenize(excludeWords[1])
      }
    }
    
    // 提取剩余关键词
    const stopWords = ['的', '了', '是', '在', '我', '有', '和', '就', '不', '人', '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', '着', '没有', '看', '好', '自己', '这']
    
    const remainingWords = this.tokenize(lowerQuery)
      .filter(word => !stopWords.includes(word))
      .filter(word => !Object.keys(sceneKeywords).includes(word))
      .filter(word => !peopleKeywords.includes(word))
      .filter(word => !locationKeywords.includes(word))
      .filter(word => !['视频', '照片', '图片', '相似', '类似', '删除', '清理', '昨天', '今天', '明天', '上周', '上月', '去年'].includes(word))
    
    parsed.keywords = remainingWords
    
    return parsed
  }


  search(query, filters = {}) {
    if (!query.trim()) {
      return this.applyFilters(this.getAllMaterials(), filters)
    }
    
    this.addToSearchHistory(query)
    
    // 解析自然语言查询
    const parsedQuery = this.parseNaturalLanguageQuery(query)
    
    // 基础关键词搜索
    const searchTerms = this.tokenize(query.toLowerCase())
    const results = new Map() // 使用Map来存储material和相关性分数
    
    searchTerms.forEach(term => {
      if (this.index.has(term)) {
        this.index.get(term).forEach(materialId => {
          const material = this.getMaterialById(materialId)
          if (material) {
            const score = results.get(material) || 0
            results.set(material, score + this.calculateRelevance(term, material, parsedQuery))
          }
        })
      }
    })
    
    // 添加自然语言解析结果的相关性增强
    const allMaterials = this.getAllMaterials()
    allMaterials.forEach(material => {
      let score = results.get(material) || 0
      
      // 场景相关性增强
      if (parsedQuery.scenes.length > 0 && material.scenes) {
        parsedQuery.scenes.forEach(scene => {
          if (material.scenes.includes(scene)) {
            score += 5 // 场景匹配权重更高
          }
        })
      }
      
      // 人物相关性增强
      if (parsedQuery.people.length > 0 && material.people) {
        parsedQuery.people.forEach(person => {
          if (material.people.some(p => p.name && p.name.includes(person))) {
            score += 4 // 人物匹配权重
          }
        })
      }
      
      // 地点相关性增强
      if (parsedQuery.locations.length > 0 && material.location) {
        parsedQuery.locations.forEach(location => {
          if (material.location.includes(location)) {
            score += 3 // 地点匹配权重
          }
        })
      }
      
      // 时间范围过滤
      if (parsedQuery.timeRange && material.date) {
        const materialDate = new Date(material.date)
        if (materialDate < parsedQuery.timeRange.start || materialDate > parsedQuery.timeRange.end) {
          score = 0 // 不在时间范围内的结果排除
        } else {
          score += 2 // 时间范围内的结果增强
        }
      }
      
      // 排除词处理
      if (parsedQuery.mustExclude.length > 0) {
        const shouldExclude = parsedQuery.mustExclude.some(excludeTerm => {
          return material.name.toLowerCase().includes(excludeTerm) ||
                 (material.tags && material.tags.some(tag => tag.toLowerCase().includes(excludeTerm))) ||
                 (material.description && material.description.toLowerCase().includes(excludeTerm))
        })
        if (shouldExclude) {
          score = 0 // 包含排除词的结果排除
        }
      }
      
      if (score > 0) {
        results.set(material, score)
      }
    })
    
    // 转换为数组并排序
    let sortedResults = Array.from(results.entries())
      .map(([material, score]) => ({ material, score }))
      .sort((a, b) => b.score - a.score)
    
    // 应用过滤器
    sortedResults = sortedResults.filter(item => 
      this.passesFilters(item.material, filters)
    )
    
    return sortedResults.map(item => item.material)
  }

  calculateRelevance(term, material, parsedQuery = null) {
    let relevance = 1
    
    // 在文件名中匹配
    if (material.name.toLowerCase().includes(term)) {
      relevance += 3
    }
    
    // 在标签中匹配
    if (material.tags && material.tags.some(tag => 
      tag.toLowerCase().includes(term))
    ) {
      relevance += 2
    }
    
    // 在描述中匹配
    if (material.description && material.description.toLowerCase().includes(term)) {
      relevance += 1
    }
    
    // 智能标签匹配增强
    if (material.scenes && material.scenes.some(scene => 
      scene.toLowerCase().includes(term))
    ) {
      relevance += 4 // 场景标签权重更高
    }
    
    if (material.location && material.location.toLowerCase().includes(term)) {
      relevance += 3 // 地点标签权重
    }
    
    if (material.people && material.people.some(person => 
      person.name.toLowerCase().includes(term))
    ) {
      relevance += 5 // 人物标签权重最高
    }
    
    // 精确匹配加分
    if (material.name.toLowerCase() === term) {
      relevance += 5
    }
    
    // 根据意图调整相关性
    if (parsedQuery) {
      if (parsedQuery.intent === 'video' && material.type === 'video') {
        relevance += 2
      } else if (parsedQuery.intent === 'photo' && material.type === 'image') {
        relevance += 2
      }
    }
    
    return relevance
  }

  applyFilters(materials, filters) {
    return materials.filter(material => this.passesFilters(material, filters))
  }

  passesFilters(material, filters) {
    // 类型过滤
    if (filters.type && filters.type.size > 0 && !filters.type.has(material.type)) {
      return false
    }
    
    // 格式过滤
    if (filters.format && filters.format.size > 0 && !filters.format.has(material.format)) {
      return false
    }
    
    // 大小过滤
    if (filters.size) {
      const fileSize = material.size || 0
      if (fileSize < filters.size.min || fileSize > filters.size.max) {
        return false
      }
    }
    
    // 日期过滤
    if (filters.date && (filters.date.start || filters.date.end)) {
      const fileDate = new Date(material.date)
      if (filters.date.start && fileDate < new Date(filters.date.start)) {
        return false
      }
      if (filters.date.end && fileDate > new Date(filters.date.end)) {
        return false
      }
    }
    
    // 评分过滤
    if (filters.rating) {
      const rating = material.rating || 0
      if (rating < filters.rating.min || rating > filters.rating.max) {
        return false
      }
    }
    
    // 标签过滤
    if (filters.tags && filters.tags.size > 0) {
      const hasMatchingTag = material.tags && 
        material.tags.some(tag => filters.tags.has(tag))
      if (!hasMatchingTag) {
        return false
      }
    }
    
    return true
  }

  updateFilterOptions(materials) {
    this.filters.type.clear()
    this.filters.format.clear()
    this.filters.tags.clear()
    
    materials.forEach(material => {
      this.filters.type.add(material.type)
      this.filters.format.add(material.format)
      
      if (material.tags) {
        material.tags.forEach(tag => this.filters.tags.add(tag))
      }
    })
    
    // 更新大小范围
    const sizes = materials.map(m => m.size || 0).filter(size => size > 0)
    if (sizes.length > 0) {
      this.filters.size = {
        min: Math.min(...sizes),
        max: Math.max(...sizes)
      }
    }
    
    // 更新日期范围
    const dates = materials.map(m => new Date(m.date)).filter(date => !isNaN(date.getTime()))
    if (dates.length > 0) {
      this.filters.date = {
        start: new Date(Math.min(...dates)),
        end: new Date(Math.max(...dates))
      }
    }
  }

  getSearchSuggestions(query, maxSuggestions = 5) {
    if (!query.trim()) return []
    
    const cacheKey = query.toLowerCase()
    if (this.suggestionsCache.has(cacheKey)) {
      return this.suggestionsCache.get(cacheKey)
    }
    
    const suggestions = new Set()
    const queryLower = query.toLowerCase()
    
    // 从搜索历史中获取建议
    this.searchHistory
      .filter(history => history.toLowerCase().includes(queryLower))
      .slice(0, maxSuggestions)
      .forEach(history => suggestions.add(history))
    
    // 从索引中获取建议
    for (const term of this.index.keys()) {
      if (term.toLowerCase().includes(queryLower)) {
        suggestions.add(term)
        if (suggestions.size >= maxSuggestions) break
      }
    }
    
    // 从过滤器选项中获取建议
    for (const type of this.filters.type) {
      if (type.toLowerCase().includes(queryLower)) {
        suggestions.add(type)
        if (suggestions.size >= maxSuggestions) break
      }
    }
    
    for (const tag of this.filters.tags) {
      if (tag.toLowerCase().includes(queryLower)) {
        suggestions.add(tag)
        if (suggestions.size >= maxSuggestions) break
      }
    }
    
    const result = Array.from(suggestions).slice(0, maxSuggestions)
    this.suggestionsCache.set(cacheKey, result)
    
    return result
  }

  addToSearchHistory(query) {
    this.searchHistory = this.searchHistory.filter(q => q !== query)
    this.searchHistory.unshift(query)
    
    // 限制历史记录数量
    if (this.searchHistory.length > 50) {
      this.searchHistory = this.searchHistory.slice(0, 50)
    }
    
    // 保存到localStorage
    this.saveSearchHistory()
  }

  getSearchHistory() {
    return this.searchHistory.slice(0, 10) // 返回最近10条
  }

  clearSearchHistory() {
    this.searchHistory = []
    this.saveSearchHistory()
  }

  saveSearchHistory() {
    localStorage.setItem('leafview-search-history', JSON.stringify(this.searchHistory))
  }

  loadSearchHistory() {
    const saved = localStorage.getItem('leafview-search-history')
    if (saved) {
      this.searchHistory = JSON.parse(saved)
    }
  }

  getAllMaterials(options = {}) {
    // 使用materialManager获取所有照片
    return materialManager.getAllMaterials(options)
  }

  getMaterialById(id) {
    // 使用materialManager根据ID获取照片
    return materialManager.getMaterial(id)
  }

  // 高级搜索功能
  advancedSearch(criteria) {
    const {
      keywords = '',
      mustInclude = [],
      mustExclude = [],
      fileTypes = [],
      minSize = 0,
      maxSize = Infinity,
      dateRange = { start: null, end: null },
      minRating = 0,
      tags = []
    } = criteria
    
    let results = this.search(keywords)
    
    // 必须包含的词汇
    mustInclude.forEach(term => {
      results = results.filter(material => 
        material.name.toLowerCase().includes(term.toLowerCase()) ||
        (material.tags && material.tags.some(tag => 
          tag.toLowerCase().includes(term.toLowerCase()))) ||
        (material.description && material.description.toLowerCase().includes(term.toLowerCase()))
      )
    })
    
    // 排除的词汇
    mustExclude.forEach(term => {
      results = results.filter(material => 
        !material.name.toLowerCase().includes(term.toLowerCase()) &&
        (!material.tags || !material.tags.some(tag => 
          tag.toLowerCase().includes(term.toLowerCase()))) &&
        (!material.description || !material.description.toLowerCase().includes(term.toLowerCase()))
      )
    })
    
    // 文件类型过滤
    if (fileTypes.length > 0) {
      results = results.filter(material => fileTypes.includes(material.type))
    }
    
    // 大小过滤
    results = results.filter(material => {
      const size = material.size || 0
      return size >= minSize && size <= maxSize
    })
    
    // 日期过滤
    if (dateRange.start || dateRange.end) {
      results = results.filter(material => {
        const fileDate = new Date(material.date)
        if (dateRange.start && fileDate < new Date(dateRange.start)) return false
        if (dateRange.end && fileDate > new Date(dateRange.end)) return false
        return true
      })
    }
    
    // 评分过滤
    results = results.filter(material => {
      const rating = material.rating || 0
      return rating >= minRating
    })
    
    // 标签过滤
    if (tags.length > 0) {
      results = results.filter(material => 
        material.tags && tags.every(tag => material.tags.includes(tag))
      )
    }
    
    return results
  }

  // 搜索分析
  analyzeSearchPatterns() {
    const analysis = {
      popularSearches: {},
      searchFrequency: {},
      searchSuccessRate: {},
      averageResults: {}
    }
    
    // 分析热门搜索词
    this.searchHistory.forEach(query => {
      analysis.popularSearches[query] = (analysis.popularSearches[query] || 0) + 1
    })
    
    return analysis
  }
}

export default new SearchEngine()