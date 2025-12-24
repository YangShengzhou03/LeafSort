class FileFormatManager {
  constructor() {
    this.supportedFormats = this.initializeSupportedFormats()
    this.formatIcons = this.initializeFormatIcons()
    this.formatColors = this.initializeFormatColors()
  }

  initializeSupportedFormats() {
    return {
      image: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'ico', 'tiff', 'tif'],
      
      design: ['psd', 'ai', 'sketch', 'xd', 'fig', 'afdesign', 'afphoto'],
      
      video: ['mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'm4v', '3gp'],
      
      audio: ['mp3', 'wav', 'flac', 'aac', 'ogg', 'wma', 'm4a'],
      
      font: ['ttf', 'otf', 'woff', 'woff2', 'eot'],
      
      document: ['pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'md'],
      
      archive: ['zip', 'rar', '7z', 'tar', 'gz']
    }
  }

  initializeFormatIcons() {
    return {
      jpg: '🖼️', jpeg: '🖼️', png: '🖼️', gif: '🖼️', bmp: '🖼️', webp: '🖼️', svg: '🔤',
      
      psd: '🎨', ai: '🎨', sketch: '🎨', xd: '🎨', fig: '🎨', afdesign: '🎨', afphoto: '🎨',
      
      mp4: '🎬', mov: '🎬', avi: '🎬', mkv: '🎬', wmv: '🎬', flv: '🎬', webm: '🎬', m4v: '🎬', '3gp': '🎬',
      
      mp3: '🎵', wav: '🎵', flac: '🎵', aac: '🎵', ogg: '🎵', wma: '🎵', m4a: '🎵',
      
      ttf: '🔤', otf: '🔤', woff: '🔤', woff2: '🔤', eot: '🔤',
      
      pdf: '📄', doc: '📄', docx: '📄', ppt: '📄', pptx: '📄', xls: '📄', xlsx: '📄', txt: '📄', md: '📄',
      
      zip: '📦', rar: '📦', '7z': '📦', tar: '📦', gz: '📦'
    }
  }

  initializeFormatColors() {
    return {
      image: '#1890ff',
      design: '#722ed1',
      video: '#fa541c',
      audio: '#52c41a',
      font: '#eb2f96',
      document: '#faad14',
      archive: '#13c2c2'
    }
  }

  getFileType(filename) {
    const extension = this.getFileExtension(filename).toLowerCase()
    return Object.entries(this.supportedFormats)
      .find(([, extensions]) => extensions.includes(extension))?.[0] || 'unknown'
  }

  getFileExtension(filename) {
    const parts = filename.split('.')
    return parts.length > 1 ? parts.pop() : ''
  }

  getFormatIcon(filename) {
    const extension = this.getFileExtension(filename).toLowerCase()
    return this.formatIcons[extension] || ''
  }

  getFormatColor(filename) {
    const fileType = this.getFileType(filename)
    return this.formatColors[fileType] || '#d9d9d9'
  }

  isSupportedFormat(filename) {
    const fileType = this.getFileType(filename)
    return fileType !== 'unknown'
  }

  getSupportedExtensions() {
    return Object.values(this.supportedFormats).flat()
  }

  getSupportedFormats() {
    return Object.keys(this.supportedFormats)
  }

  getFormatsByType(type) {
    return this.supportedFormats[type] || []
  }

  formatFileSize(bytes) {
    if (!bytes || bytes === 0) return '0 B'
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  formatFileDate(timestamp) {
    if (!timestamp) return ''
    const date = new Date(timestamp)
    const now = new Date()
    const diff = now - date
    const minutes = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days = Math.floor(diff / 86400000)

    if (minutes < 60) {
      return `${minutes}分钟前`
    } else if (hours < 24) {
      return `${hours}小时前`
    } else if (days < 30) {
      return `${days}天前`
    } else {
      return `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`
    }
  }
}

export default new FileFormatManager()
