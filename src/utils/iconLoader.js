class IconLoader {
  constructor() {
    this.iconCache = new Map()
    this.loadingPromises = new Map()
    this.maxCacheSize = 50
  }

  async loadIcon(iconName) {
    if (this.iconCache.has(iconName)) {
      return this.iconCache.get(iconName)
    }

    if (this.loadingPromises.has(iconName)) {
      return this.loadingPromises.get(iconName)
    }

    const loadPromise = this.doLoadIcon(iconName)
    this.loadingPromises.set(iconName, loadPromise)

    try {
      const icon = await loadPromise
      this.cacheIcon(iconName, icon)
      return icon
    } finally {
      this.loadingPromises.delete(iconName)
    }
  }

  async doLoadIcon(iconName) {
    try {
      const iconModule = await import('@element-plus/icons-vue')
      
      if (iconModule[iconName]) {
        return iconModule[iconName]
      }

      return await this.loadCustomIcon(iconName)
    } catch (error) {
      console.warn(`Failed to load icon: ${iconName}`, error)
      return this.getFallbackIcon()
    }
  }

  async loadCustomIcon(iconName) {
    try {
      const icon = await import(/* webpackChunkName: "icon-[request]" */ `@/assets/icons/${iconName}.svg`)
      return icon.default || icon
    } catch (error) {
      throw new Error(`Custom icon not found: ${iconName}`)
    }
  }

  getFallbackIcon() {
    return {
      name: 'FallbackIcon',
      template: `<svg viewBox="0 0 24 24" fill="currentColor" width="1em" height="1em">
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
      </svg>`
    }
  }

  cacheIcon(iconName, icon) {
    if (this.iconCache.size >= this.maxCacheSize) {
      const firstKey = this.iconCache.keys().next().value
      this.iconCache.delete(firstKey)
    }

    this.iconCache.set(iconName, icon)
  }

  async preloadIcons(iconNames) {
    const promises = iconNames.map(iconName => this.loadIcon(iconName))
    return Promise.allSettled(promises)
  }

  clearCache() {
    this.iconCache.clear()
    this.loadingPromises.clear()
  }

  getCacheStats() {
    return {
      cachedCount: this.iconCache.size,
      loadingCount: this.loadingPromises.size,
      maxCacheSize: this.maxCacheSize
    }
  }
}

const iconLoader = new IconLoader()

export function loadIcon(iconName) {
  return iconLoader.loadIcon(iconName)
}

export function preloadIcons(iconNames) {
  return iconLoader.preloadIcons(iconNames)
}

export function clearIconCache() {
  iconLoader.clearCache()
}

export function getIconCacheStats() {
  return iconLoader.getCacheStats()
}