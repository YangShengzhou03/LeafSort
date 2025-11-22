import { contextBridge, ipcRenderer } from 'electron'

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 对话框相关
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  openFile: () => ipcRenderer.invoke('dialog:openFile'),
  
  // 文件操作相关
  getFileInfo: (filePath: string) => ipcRenderer.invoke('file:getFileInfo', filePath),
  
  // 菜单事件监听
  onMenuEvent: (callback: (event: string, data?: any) => void) => {
    ipcRenderer.on('menu-event', (event, type, data) => {
      callback(type, data)
    })
  },
  
  // 移除监听器
  removeAllListeners: (channel: string) => {
    ipcRenderer.removeAllListeners(channel)
  }
})

// 类型声明
declare global {
  interface Window {
    electronAPI: {
      openDirectory: () => Promise<any>
      openFile: () => Promise<any>
      getFileInfo: (filePath: string) => Promise<any>
      onMenuEvent: (callback: (event: string, data?: any) => void) => void
      removeAllListeners: (channel: string) => void
    }
  }
}