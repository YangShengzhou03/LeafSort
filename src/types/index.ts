// 素材库类型
export interface Library {
  id: string
  name: string
  path: string
  createdAt: Date
  assetCount: number
  size: number
  description?: string
}

// 素材类型
export interface Asset {
  id: string
  name: string
  path: string
  type: 'image' | 'video' | 'audio' | 'document' | 'other'
  size: number
  width?: number
  height?: number
  duration?: number
  createdAt: Date
  modifiedAt: Date
  tags: string[]
  rating: number
  folderId?: string
  metadata?: AssetMetadata
}

// 素材元数据
export interface AssetMetadata {
  format?: string
  camera?: string
  lens?: string
  exposure?: string
  iso?: number
  gps?: {
    latitude: number
    longitude: number
  }
  colorPalette?: string[]
  dominantColor?: string
  // 音频相关元数据
  bpm?: number
  sampleRate?: string
  bitRate?: string
  channels?: string
  artist?: string
  album?: string
  // 图像和视频相关元数据
  width?: number
  height?: number
  quality?: number
  hasWatermark?: boolean
  watermarkText?: string
  includeCursor?: boolean
  videoUrl?: string | null
  // 网页采集相关元数据
  source?: string
  captureType?: string
  duration?: string
  originalUrl?: string
}

// 文件夹类型
export interface Folder {
  id: string
  name: string
  parentId?: string
  createdAt: Date
  assetCount: number
  children?: Folder[]
}

// 标签类型
export interface Tag {
  id: string
  name: string
  color: string
  assetCount: number
}

export type ActivityType = 'import' | 'delete' | 'move' | 'rename' | 'tag' | 'rating' | 'favorite' | 'folder'

export interface Activity {
  id?: string
  type: ActivityType
  assetId?: string
  folderId?: string
  timestamp: Date
  description: string
  metadata?: Record<string, any>
}

// 智能文件夹规则
export interface SmartFolderRule {
  field: string
  operator: 'equals' | 'contains' | 'greater' | 'less' | 'between'
  value: any
}

// 智能文件夹类型
export interface SmartFolder {
  id: string
  name: string
  rules: SmartFolderRule[]
  assetCount: number
}

// 最近活动类型
export interface RecentActivity {
  id: string
  type: 'import' | 'edit' | 'delete' | 'tag' | 'folder' | 'web_capture'
  assetId?: string
  folderId?: string
  timestamp: Date
  description: string
}

// 搜索过滤器
export interface SearchFilters {
  keyword: string
  fileType: string
  sizeRange: { min: number; max: number }
  dateRange: { start: Date | null; end: Date | null }
  tags: string[]
  rating: number
  color?: string
}

// 视图配置
export interface ViewConfig {
  mode: 'grid' | 'list' | 'masonry'
  thumbnailSize: number
  showMetadata: boolean
  groupBy: 'none' | 'folder' | 'date' | 'type'
}

// 应用设置
export interface AppSettings {
  theme: 'light' | 'dark' | 'auto'
  language: string
  thumbnailQuality: 'low' | 'medium' | 'high'
  autoImport: boolean
  backupInterval: number
  hotkeys: Record<string, string>
}

// 导入配置
export interface ImportConfig {
  preserveFolderStructure: boolean
  duplicateHandling: 'skip' | 'rename' | 'replace'
  autoTagging: boolean
  generateThumbnails: boolean
}

// 导出配置
export interface ExportConfig {
  format: 'original' | 'jpeg' | 'png' | 'webp'
  quality: number
  resize: {
    enabled: boolean
    width?: number
    height?: number
    maintainAspectRatio: boolean
  }
  watermark: {
    enabled: boolean
    text?: string
    imagePath?: string
    position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right' | 'center'
  }
}