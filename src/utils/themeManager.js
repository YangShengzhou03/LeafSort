class ThemeManager {
  constructor() {
    this.currentTheme = 'dark'
    this.themes = {
      dark: {
        name: 'dark',
        label: '深色主题',
        variables: {
          '--bg-primary': '#141414',
          '--bg-secondary': '#1a1a1a',
          '--bg-card': '#1e1e1e',
          '--bg-hover': '#2a2a2a',
          '--bg-active': '#3a3a3a',
          '--text-primary': '#ffffff',
          '--text-secondary': '#cccccc',
          '--text-tertiary': '#8c8c8c',
          '--border-light': '#2d2d2d',
          '--border-medium': '#404040',
          '--primary-color': '#1890ff',
          '--primary-hover': '#40a9ff',
          '--primary-active': '#096dd9',
          '--success-color': '#52c41a',
          '--warning-color': '#faad14',
          '--error-color': '#f5222d',
          '--info-color': '#1890ff'
        }
      },
      light: {
        name: 'light',
        label: '浅色主题',
        variables: {
          '--bg-primary': '#ffffff',
          '--bg-secondary': '#f8f9fa',
          '--bg-card': '#ffffff',
          '--bg-hover': '#f5f5f5',
          '--bg-active': '#e6f7ff',
          '--text-primary': '#262626',
          '--text-secondary': '#595959',
          '--text-tertiary': '#8c8c8c',
          '--border-light': '#d9d9d9',
          '--border-medium': '#bfbfbf',
          '--primary-color': '#1890ff',
          '--primary-hover': '#40a9ff',
          '--primary-active': '#096dd9',
          '--success-color': '#52c41a',
          '--warning-color': '#faad14',
          '--error-color': '#f5222d',
          '--info-color': '#1890ff'
        }
      }
    }
    
    this.initTheme()
  }

  initTheme() {
    const savedTheme = localStorage.getItem('leafview-theme')
    if (savedTheme && this.themes[savedTheme]) {
      this.currentTheme = savedTheme
    }
    
    this.applyTheme(this.currentTheme)
  }

  applyTheme(themeName) {
    if (!this.themes[themeName]) return
    
    const theme = this.themes[themeName]
    const root = document.documentElement
    
    Object.entries(theme.variables).forEach(([key, value]) => {
      root.style.setProperty(key, value)
    })
    
    this.currentTheme = themeName
    localStorage.setItem('leafview-theme', themeName)
    
    document.body.className = document.body.className.replace(/theme-\w+/g, '')
    document.body.classList.add(`theme-${themeName}`)
  }

  getCurrentTheme() {
    return this.themes[this.currentTheme]
  }

  getAvailableThemes() {
    return Object.values(this.themes)
  }

  toggleTheme() {
    const themeNames = Object.keys(this.themes)
    const currentIndex = themeNames.indexOf(this.currentTheme)
    const nextIndex = (currentIndex + 1) % themeNames.length
    const nextTheme = themeNames[nextIndex]
    
    this.applyTheme(nextTheme)
    return nextTheme
  }

  isDarkTheme() {
    return this.currentTheme === 'dark'
  }
}

export default new ThemeManager()