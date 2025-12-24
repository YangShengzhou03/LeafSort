class ErrorHandler {
  constructor() {
    this.errorLog = []
    this.maxLogSize = 100
    this.reportUrl = process.env.VUE_APP_ERROR_REPORT_URL
  }

  handleError(error, context = '', instance = null, info = '') {
    const errorInfo = {
      type: instance ? 'vue_error' : 'general_error',
      message: error.message || error,
      stack: error.stack,
      context,
      instance: instance?.$options?.name || 'Unknown',
      info,
      timestamp: new Date().toISOString()
    }

    this.logError(errorInfo)
    this.showUserFriendlyError(error)
    this.reportError(errorInfo)
  }

  logError(errorInfo) {
    this.errorLog.push(errorInfo)
    
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog = this.errorLog.slice(-this.maxLogSize)
    }

    if (process.env.NODE_ENV === 'development') {
      // eslint-disable-next-line no-console
      console.error('Error logged:', errorInfo)
    }
  }

  showUserFriendlyError(error) {
    if (this.isShowingError) return
    
    this.isShowingError = true
    
    if (window.$message) {
      window.$message.error(this.getUserFriendlyMessage(error))
    }

    setTimeout(() => {
      this.isShowingError = false
    }, 1000)
  }

  getUserFriendlyMessage(error) {
    const message = error.message || error.toString()
    
    const errorMap = {
      'Network Error': '网络连接失败，请检查网络设置',
      'timeout': '请求超时，请稍后重试',
      '404': '请求的资源不存在',
      '401': '未授权访问，请重新登录',
      '403': '访问被拒绝',
      '500': '服务器内部错误'
    }

    for (const [key, friendlyMessage] of Object.entries(errorMap)) {
      if (message.includes(key)) {
        return friendlyMessage
      }
    }

    return '操作失败，请稍后重试'
  }

  async reportError(errorInfo) {
    if (!this.reportUrl) return

    try {
      await fetch(this.reportUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(errorInfo)
      })
    } catch (error) {
      // eslint-disable-next-line no-console
      console.warn('Failed to report error:', error)
    }
  }

  getErrorLog() {
    return [...this.errorLog]
  }

  clearErrorLog() {
    this.errorLog = []
  }
}

const errorHandler = new ErrorHandler()

export function handleError(error, instance, info) {
  errorHandler.handleError(error, '', instance, info)
}

export function getErrorLog() {
  return errorHandler.getErrorLog()
}

export function clearErrorLog() {
  errorHandler.clearErrorLog()
}