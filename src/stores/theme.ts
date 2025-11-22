import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'

export const useThemeStore = defineStore('theme', () => {
  // 主题模式
  const themeMode = ref<'light' | 'dark' | 'auto'>('auto')
  
  // 主题色
  const primaryColor = ref('#409EFF')
  
  // 字体设置
  const fontFamily = ref('system-ui')
  const fontSize = ref(14)
  const fontWeight = ref('400')
  
  // 动画设置
  const enableAnimations = ref(true)
  const animationSpeed = ref(1.0)
  const animationType = ref('fade')
  
  // 界面设置
  const layout = ref('classic')
  const sidebarPosition = ref('left')
  const sidebarWidth = ref(280)
  const showToolbar = ref(true)
  const toolbarPosition = ref('top')
  const toolbarButtonSize = ref('medium')
  const gridDensity = ref(3)
  const thumbnailSize = ref(120)
  const showFileInfo = ref(true)
  const showFileExtension = ref(false)
  
  // 计算当前主题
  const currentTheme = computed(() => {
    if (themeMode.value === 'auto') {
      // 检测系统主题
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return themeMode.value
  })
  
  // 设置主题模式
  const setTheme = (mode: 'light' | 'dark' | 'auto') => {
    themeMode.value = mode
    applyTheme()
  }
  
  // 设置主题色
  const setPrimaryColor = (color: string) => {
    primaryColor.value = color
    applyTheme()
  }
  
  // 设置字体
  const setFontFamily = (family: string) => {
    fontFamily.value = family
    applyTheme()
  }
  
  const setFontSize = (size: number) => {
    fontSize.value = size
    applyTheme()
  }
  
  const setFontWeight = (weight: string) => {
    fontWeight.value = weight
    applyTheme()
  }
  
  // 设置动画
  const setAnimationSettings = (settings: {
    enable: boolean
    speed: number
    type: string
  }) => {
    enableAnimations.value = settings.enable
    animationSpeed.value = settings.speed
    animationType.value = settings.type
    applyTheme()
  }
  
  // 设置界面
  const setInterfaceSettings = (settings: {
    layout: string
    sidebarPosition: string
    sidebarWidth: number
    showToolbar: boolean
    toolbarPosition: string
    toolbarButtonSize: string
    gridDensity: number
    thumbnailSize: number
    showFileInfo: boolean
    showFileExtension: boolean
  }) => {
    layout.value = settings.layout
    sidebarPosition.value = settings.sidebarPosition
    sidebarWidth.value = settings.sidebarWidth
    showToolbar.value = settings.showToolbar
    toolbarPosition.value = settings.toolbarPosition
    toolbarButtonSize.value = settings.toolbarButtonSize
    gridDensity.value = settings.gridDensity
    thumbnailSize.value = settings.thumbnailSize
    showFileInfo.value = settings.showFileInfo
    showFileExtension.value = settings.showFileExtension
    applyTheme()
  }
  
  // 切换主题
  const toggleTheme = () => {
    themeMode.value = themeMode.value === 'light' ? 'dark' : 'light'
    applyTheme()
  }
  
  // 应用主题
  const applyTheme = () => {
    const theme = currentTheme.value
    document.documentElement.setAttribute('data-theme', theme)
    
    // 应用主题色
    if (primaryColor.value) {
      document.documentElement.style.setProperty('--el-color-primary', primaryColor.value)
      // 生成主题色相关变量
      generateColorVariables(primaryColor.value)
    }
    
    // 应用字体设置
    document.documentElement.style.setProperty('--el-font-family', fontFamily.value)
    document.documentElement.style.setProperty('--el-font-size-base', `${fontSize.value}px`)
    document.documentElement.style.setProperty('--el-font-weight-primary', fontWeight.value)
    
    // 应用动画设置
    document.documentElement.style.setProperty('--el-transition-duration', `${enableAnimations.value ? 0.3 / animationSpeed.value : 0}s`)
    
    // 应用界面设置
    document.documentElement.style.setProperty('--sidebar-width', `${sidebarWidth.value}px`)
    document.documentElement.style.setProperty('--thumbnail-size', `${thumbnailSize.value}px`)
    
    // 保存设置到本地存储
    saveSettings()
  }
  
  // 生成颜色变量
  const generateColorVariables = (color: string) => {
    // 这里可以添加更复杂的颜色生成逻辑
    // 暂时使用简单的实现
    document.documentElement.style.setProperty('--el-color-primary-light-3', lightenColor(color, 0.3))
    document.documentElement.style.setProperty('--el-color-primary-light-5', lightenColor(color, 0.5))
    document.documentElement.style.setProperty('--el-color-primary-light-7', lightenColor(color, 0.7))
    document.documentElement.style.setProperty('--el-color-primary-light-8', lightenColor(color, 0.8))
    document.documentElement.style.setProperty('--el-color-primary-light-9', lightenColor(color, 0.9))
    document.documentElement.style.setProperty('--el-color-primary-dark-2', darkenColor(color, 0.2))
  }
  
  // 颜色工具函数
  const lightenColor = (color: string, amount: number): string => {
    // 简化实现，实际项目中可以使用更复杂的颜色处理库
    return color
  }
  
  const darkenColor = (color: string, amount: number): string => {
    // 简化实现，实际项目中可以使用更复杂的颜色处理库
    return color
  }
  
  // 保存设置到本地存储
  const saveSettings = () => {
    const settings = {
      themeMode: themeMode.value,
      primaryColor: primaryColor.value,
      fontFamily: fontFamily.value,
      fontSize: fontSize.value,
      fontWeight: fontWeight.value,
      enableAnimations: enableAnimations.value,
      animationSpeed: animationSpeed.value,
      animationType: animationType.value,
      layout: layout.value,
      sidebarPosition: sidebarPosition.value,
      sidebarWidth: sidebarWidth.value,
      showToolbar: showToolbar.value,
      toolbarPosition: toolbarPosition.value,
      toolbarButtonSize: toolbarButtonSize.value,
      gridDensity: gridDensity.value,
      thumbnailSize: thumbnailSize.value,
      showFileInfo: showFileInfo.value,
      showFileExtension: showFileExtension.value
    }
    
    localStorage.setItem('leafview-theme-settings', JSON.stringify(settings))
  }
  
  // 加载设置
  const loadSettings = () => {
    const saved = localStorage.getItem('leafview-theme-settings')
    if (saved) {
      try {
        const settings = JSON.parse(saved)
        themeMode.value = settings.themeMode || 'auto'
        primaryColor.value = settings.primaryColor || '#409EFF'
        fontFamily.value = settings.fontFamily || 'system-ui'
        fontSize.value = settings.fontSize || 14
        fontWeight.value = settings.fontWeight || '400'
        enableAnimations.value = settings.enableAnimations ?? true
        animationSpeed.value = settings.animationSpeed || 1.0
        animationType.value = settings.animationType || 'fade'
        layout.value = settings.layout || 'classic'
        sidebarPosition.value = settings.sidebarPosition || 'left'
        sidebarWidth.value = settings.sidebarWidth || 280
        showToolbar.value = settings.showToolbar ?? true
        toolbarPosition.value = settings.toolbarPosition || 'top'
        toolbarButtonSize.value = settings.toolbarButtonSize || 'medium'
        gridDensity.value = settings.gridDensity || 3
        thumbnailSize.value = settings.thumbnailSize || 120
        showFileInfo.value = settings.showFileInfo ?? true
        showFileExtension.value = settings.showFileExtension ?? false
        
        applyTheme()
      } catch (error) {
        console.error('加载主题设置失败:', error)
      }
    }
  }
  
  // 重置设置
  const resetSettings = () => {
    themeMode.value = 'auto'
    primaryColor.value = '#409EFF'
    fontFamily.value = 'system-ui'
    fontSize.value = 14
    fontWeight.value = '400'
    enableAnimations.value = true
    animationSpeed.value = 1.0
    animationType.value = 'fade'
    layout.value = 'classic'
    sidebarPosition.value = 'left'
    sidebarWidth.value = 280
    showToolbar.value = true
    toolbarPosition.value = 'top'
    toolbarButtonSize.value = 'medium'
    gridDensity.value = 3
    thumbnailSize.value = 120
    showFileInfo.value = true
    showFileExtension.value = false
    
    applyTheme()
  }
  
  // 监听系统主题变化
  const watchSystemTheme = () => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = (e: MediaQueryListEvent) => {
      if (themeMode.value === 'auto') {
        applyTheme()
      }
    }
    mediaQuery.addEventListener('change', handleChange)
    
    // 返回清理函数
    return () => {
      mediaQuery.removeEventListener('change', handleChange)
    }
  }
  
  // 初始化时加载设置
  loadSettings()
  
  // 监听设置变化并自动保存
  watch([
    themeMode, primaryColor, fontFamily, fontSize, fontWeight,
    enableAnimations, animationSpeed, animationType,
    layout, sidebarPosition, sidebarWidth, showToolbar, toolbarPosition,
    toolbarButtonSize, gridDensity, thumbnailSize, showFileInfo, showFileExtension
  ], () => {
    saveSettings()
  })
  
  return {
    // 状态
    themeMode,
    primaryColor,
    fontFamily,
    fontSize,
    fontWeight,
    enableAnimations,
    animationSpeed,
    animationType,
    layout,
    sidebarPosition,
    sidebarWidth,
    showToolbar,
    toolbarPosition,
    toolbarButtonSize,
    gridDensity,
    thumbnailSize,
    showFileInfo,
    showFileExtension,
    
    // 计算属性
    currentTheme,
    
    // 方法
    setTheme,
    setPrimaryColor,
    setFontFamily,
    setFontSize,
    setFontWeight,
    setAnimationSettings,
    setInterfaceSettings,
    toggleTheme,
    applyTheme,
    loadSettings,
    resetSettings,
    watchSystemTheme
  }
})