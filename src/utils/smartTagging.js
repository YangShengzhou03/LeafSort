class SmartTagging {
  constructor() {
    this.tagPatterns = {
      // 文件类型相关
      image: ['图片', '照片', '图像', '图库', '视觉'],
      video: ['视频', '影片', '动画', '剪辑', '影视'],
      audio: ['音频', '音乐', '声音', '音效', '歌曲'],
      design: ['设计', '创意', '艺术', '美术', '视觉设计'],
      
      // 行业相关
      business: ['商业', '企业', '办公', '商务', '营销'],
      education: ['教育', '学习', '学校', '课程', '培训'],
      technology: ['科技', '技术', '互联网', '软件', '数字'],
      healthcare: ['医疗', '健康', '医院', '医生', '保健'],
      
      // 风格相关
      modern: ['现代', '简约', '时尚', '潮流', '当代'],
      classic: ['经典', '传统', '复古', '怀旧', '古典'],
      abstract: ['抽象', '艺术', '创意', '概念', '现代艺术'],
      realistic: ['写实', '真实', '自然', '逼真', '现实'],
      
      // 颜色相关
      colorful: ['彩色', '多彩', '鲜艳', '丰富', '亮丽'],
      monochrome: ['黑白', '单色', '灰度', '简约', '经典'],
      warm: ['温暖', '温馨', '柔和', '舒适', '暖色'],
      cool: ['冷静', '清爽', '冷色', '科技', '现代'],
      
      // 用途相关
      background: ['背景', '底图', '纹理', '图案', '壁纸'],
      icon: ['图标', '符号', '标志', '按钮', '界面'],
      texture: ['纹理', '材质', '表面', '质感', '图案'],
      pattern: ['图案', '花纹', '装饰', '设计', '样式']
    }
    
    // 智能场景识别关键词
    this.scenePatterns = {
      // 自然风景
      '风景': ['风景', '山水', '风景照', '自然风光'],
      '山脉': ['山脉', '山峰', '雪山', '大山', '山景'],
      '海洋': ['海洋', '大海', '海滩', '海边', '海景'],
      '湖泊': ['湖泊', '湖面', '湖水', '湖景'],
      '森林': ['森林', '树林', '树木', '林景'],
      '草原': ['草原', '草地', '牧场'],
      '沙漠': ['沙漠', '沙丘', '荒漠'],
      '瀑布': ['瀑布', '水帘', '飞瀑'],
      '日出': ['日出', '朝霞', '晨曦'],
      '日落': ['日落', '夕阳', '晚霞'],
      '星空': ['星空', '星星', '夜空', '银河'],
      '雪景': ['雪景', '雪花', '下雪', '积雪'],
      '雾景': ['雾景', '雾气', '薄雾', '晨雾'],
      
      // 人物相关
      '人物': ['人物', '人像', '人物照', '人像摄影'],
      '儿童': ['儿童', '小孩', '宝宝', '孩子'],
      '老人': ['老人', '长辈', '老者'],
      '家庭': ['家庭', '全家福', '家人'],
      '情侣': ['情侣', '爱人', '恋人'],
      '婚礼': ['婚礼', '结婚', '婚纱照', '婚庆'],
      '聚会': ['聚会', '聚餐', '派对', '聚会照'],
      '团队': ['团队', '合影', '集体照'],
      
      // 动物相关
      '动物': ['动物', '宠物', '野生动物'],
      '狗': ['狗', '小狗', '宠物狗'],
      '猫': ['猫', '小猫', '宠物猫'],
      '鸟类': ['鸟', '鸟类', '飞鸟'],
      '海洋动物': ['鱼', '海洋动物', '海底生物'],
      '野生动物': ['野生动物', '野兽', '猛兽'],
      
      // 食物相关
      '食物': ['食物', '美食', '餐饮'],
      '甜点': ['甜点', '蛋糕', '甜品', '甜点'],
      '水果': ['水果', '鲜果', '果品'],
      '蔬菜': ['蔬菜', '青菜', '蔬果'],
      '肉类': ['肉', '肉类', '荤菜'],
      '饮品': ['饮品', '饮料', '咖啡', '茶', '酒水'],
      '烹饪': ['烹饪', '做饭', '厨房', '美食制作'],
      
      // 旅行相关
      '旅行': ['旅行', '旅游', '出行', '旅途'],
      '城市': ['城市', '都市', '城市景观', '都市风光'],
      '建筑': ['建筑', '建筑物', '地标', '建筑设计'],
      '历史遗迹': ['历史', '遗迹', '古迹', '古建筑'],
      '交通工具': ['汽车', '火车', '飞机', '船只', '交通工具'],
      
      // 生活相关
      '家居': ['家居', '家庭', '室内', '家装'],
      '运动': ['运动', '健身', '体育', '户外活动'],
      '工作': ['工作', '办公', '职场'],
      '学习': ['学习', '读书', '教育', '课堂'],
      '节日': ['节日', '庆典', '庆祝', '节日氛围'],
      '艺术': ['艺术', '绘画', '雕塑', '艺术作品'],
      '时尚': ['时尚', '服装', '穿搭', '时尚设计'],
      
      // 其他场景
      '文档': ['文档', '文件', '资料'],
      '图表': ['图表', '数据', '统计', '信息图'],
      'UI设计': ['UI', '界面', '设计', '用户界面']
    }
    
    this.aiKeywords = {
      // AI生成相关
      aiGenerated: ['AI生成', '人工智能', '机器学习', '智能创作', '算法生成'],
      prompt: ['提示词', '咒语', '描述', '指令', '关键词'],
      style: ['风格', '样式', '类型', '形式', '模式'],
      
      // 设计元素
      composition: ['构图', '布局', '结构', '排列', '组织'],
      lighting: ['光照', '灯光', '照明', '光影', '亮度'],
      color: ['色彩', '颜色', '色调', '配色', '色谱']
    }
  }

  detectScene(filename) {
    const detectedScenes = new Set()
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '').toLowerCase()
    
    // 根据文件名识别场景
    for (const [scene, patterns] of Object.entries(this.scenePatterns)) {
      for (const pattern of patterns) {
        if (nameWithoutExt.includes(pattern.toLowerCase())) {
          detectedScenes.add(scene)
          break
        }
      }
    }
    
    // 简单模拟AI场景识别
    // 在实际应用中，这里可以调用AI服务进行图像内容分析
    if (detectedScenes.size === 0) {
      // 根据文件类型和元数据进行一些智能推断
      const type = filename.split('.').pop().toLowerCase()
      if (['jpg', 'jpeg', 'png', 'gif'].includes(type)) {
        // 随机分配一些场景（模拟AI识别效果）
        const randomScenes = ['风景', '人物', '动物', '食物', '旅行', '建筑']
        const randomScene = randomScenes[Math.floor(Math.random() * randomScenes.length)]
        detectedScenes.add(randomScene)
      }
    }
    
    return Array.from(detectedScenes)
  }

  extractTagsFromFilename(filename) {
    const tags = new Set()
    const nameWithoutExt = filename.replace(/\.[^/.]+$/, '').toLowerCase()
    
    // 提取数字和尺寸信息
    const dimensions = nameWithoutExt.match(/(\d+)x(\d+)/)
    if (dimensions) {
      tags.add(`${dimensions[1]}x${dimensions[2]}`)
    }
    
    // 提取分辨率信息
    const resolution = nameWithoutExt.match(/(\d+)p/)
    if (resolution) {
      tags.add(`${resolution[1]}p`)
    }
    
    // 提取版本信息
    const version = nameWithoutExt.match(/v(\d+(\.\d+)*)/)
    if (version) {
      tags.add(`v${version[1]}`)
    }
    
    // 根据文件名关键词匹配标签
    Object.values(this.tagPatterns).forEach(patterns => {
      patterns.forEach(pattern => {
        if (nameWithoutExt.includes(pattern.toLowerCase())) {
          tags.add(pattern)
        }
      })
    })
    
    // 提取日期信息
    const datePattern = nameWithoutExt.match(/(\d{4})[-_]?(\d{2})[-_]?(\d{2})/)
    if (datePattern) {
      tags.add(`${datePattern[1]}-${datePattern[2]}-${datePattern[3]}`)
    }
    
    return Array.from(tags)
  }

  generateAITags(prompt, style) {
    const tags = new Set()
    
    Object.values(this.aiKeywords).forEach(keywords => {
      keywords.forEach(keyword => {
        if (prompt.toLowerCase().includes(keyword.toLowerCase())) {
          tags.add(keyword)
        }
      })
    })
    
    // 添加风格标签
    if (style) {
      tags.add(style)
    }
    
    // 从提示词中提取具体描述
    const descriptiveWords = ['精美', '高质量', '高清', '专业', '创意', '独特', '现代', '经典']
    descriptiveWords.forEach(word => {
      if (prompt.includes(word)) {
        tags.add(word)
      }
    })
    
    return Array.from(tags)
  }

  suggestTagsForMaterial(material) {
    const suggestedTags = new Set()
    
    // 基于文件类型
    suggestedTags.add(material.type)
    
    // 基于文件名
    const filenameTags = this.extractTagsFromFilename(material.name)
    filenameTags.forEach(tag => suggestedTags.add(tag))
    
    // 智能场景识别
    if (['image', 'video'].includes(material.type)) {
      const detectedScenes = this.detectScene(material.name, material.metadata)
      detectedScenes.forEach(scene => suggestedTags.add(scene))
    }
    
    // 基于文件大小（大文件标记为高清）
    if (material.size > 10 * 1024 * 1024) { // 10MB以上
      suggestedTags.add('高清')
      suggestedTags.add('高质量')
    }
    
    // 基于文件格式
    const formatTags = this.getFormatTags(material.format)
    formatTags.forEach(tag => suggestedTags.add(tag))
    
    return Array.from(suggestedTags).slice(0, 10) // 限制标签数量
  }

  getFormatTags(format) {
    const formatMap = {
      jpg: ['图片', '照片', 'JPEG'],
      jpeg: ['图片', '照片', 'JPEG'],
      png: ['图片', '透明背景', 'PNG'],
      gif: ['动画', 'GIF', '动态图'],
      webp: ['图片', 'WebP', '现代格式'],
      svg: ['矢量', 'SVG', '可缩放'],
      psd: ['设计', 'PSD', 'Photoshop'],
      ai: ['矢量', 'AI', 'Illustrator'],
      sketch: ['设计', 'Sketch', 'UI设计'],
      figma: ['设计', 'Figma', 'UI设计'],
      mp4: ['视频', 'MP4', '高清视频'],
      avi: ['视频', 'AVI', '传统格式'],
      mov: ['视频', 'MOV', '专业视频'],
      mp3: ['音频', 'MP3', '音乐'],
      wav: ['音频', 'WAV', '无损音频'],
      pdf: ['文档', 'PDF', '可打印'],
      doc: ['文档', 'Word', '文本'],
      docx: ['文档', 'Word', '文本']
    }
    
    return formatMap[format.toLowerCase()] || [format.toUpperCase()]
  }

  autoTagMaterial(material) {
    const suggestedTags = this.suggestTagsForMaterial(material)
    
    // 如果素材还没有标签，自动添加推荐的标签
    if (!material.tags || material.tags.length === 0) {
      material.tags = suggestedTags.slice(0, 5) // 限制为5个标签
      return material.tags
    }
    
    // 如果已有标签，建议补充缺失的标签
    const currentTags = new Set(material.tags)
    const missingTags = suggestedTags.filter(tag => !currentTags.has(tag))
    
    return missingTags.slice(0, 3) // 建议最多3个补充标签
  }

  analyzeTagUsage(materials) {
    const tagStats = {}
    
    materials.forEach(material => {
      if (material.tags && material.tags.length > 0) {
        material.tags.forEach(tag => {
          if (!tagStats[tag]) {
            tagStats[tag] = {
              count: 0,
              materials: [],
              types: new Set(),
              averageSize: 0,
              totalSize: 0
            }
          }
          
          tagStats[tag].count++
          tagStats[tag].materials.push(material.id)
          tagStats[tag].types.add(material.type)
          tagStats[tag].totalSize += material.size || 0
        })
      }
    })
    
    // 计算平均大小
    Object.keys(tagStats).forEach(tag => {
      tagStats[tag].averageSize = tagStats[tag].totalSize / tagStats[tag].count
      tagStats[tag].types = Array.from(tagStats[tag].types)
    })
    
    return tagStats
  }

  findSimilarMaterials(material, allMaterials, maxResults = 10) {
    const similarityScores = []
    
    allMaterials.forEach(otherMaterial => {
      if (otherMaterial.id === material.id) return
      
      let score = 0
      
      // 类型相似度
      if (otherMaterial.type === material.type) score += 3
      
      // 标签相似度
      if (material.tags && otherMaterial.tags) {
        const commonTags = material.tags.filter(tag => 
          otherMaterial.tags.includes(tag)
        ).length
        score += commonTags * 2
      }
      
      // 文件大小相似度（在相同数量级）
      const sizeRatio = Math.min(material.size, otherMaterial.size) / 
                       Math.max(material.size, otherMaterial.size)
      if (sizeRatio > 0.5) score += 1
      
      // 文件名相似度
      const nameSimilarity = this.calculateStringSimilarity(
        material.name.toLowerCase(),
        otherMaterial.name.toLowerCase()
      )
      score += nameSimilarity * 2
      
      if (score > 0) {
        similarityScores.push({
          material: otherMaterial,
          score: score,
          similarity: Math.min(score / 10, 1) // 归一化到0-1
        })
      }
    })
    
    return similarityScores
      .sort((a, b) => b.score - a.score)
      .slice(0, maxResults)
  }

  calculateStringSimilarity(str1, str2) {
    const longer = str1.length > str2.length ? str1 : str2
    const shorter = str1.length > str2.length ? str2 : str1
    
    if (longer.length === 0) return 1.0
    
    // 计算编辑距离相似度
    const editDistance = this.calculateEditDistance(longer, shorter)
    return (longer.length - editDistance) / parseFloat(longer.length)
  }

  calculateEditDistance(s1, s2) {
    s1 = s1.toLowerCase()
    s2 = s2.toLowerCase()
    
    const costs = []
    for (let i = 0; i <= s1.length; i++) {
      let lastValue = i
      for (let j = 0; j <= s2.length; j++) {
        if (i === 0) {
          costs[j] = j
        } else {
          if (j > 0) {
            let newValue = costs[j - 1]
            if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
              newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1
            }
            costs[j - 1] = lastValue
            lastValue = newValue
          }
        }
      }
      if (i > 0) costs[s2.length] = lastValue
    }
    return costs[s2.length]
  }
}

export default new SmartTagging()