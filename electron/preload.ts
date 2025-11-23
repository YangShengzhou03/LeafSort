import { contextBridge, ipcRenderer } from 'electron'

// 安全的通道白名单
const VALID_CHANNELS = {
  // 从渲染进程到主进程的通道
  INVOKE: [
    'dialog:openDirectory',
    'dialog:openFile',
    'dialog:saveFile',
    'file:getFileInfo',
    'file:readFile',
    'file:writeFile',
    'file:deleteFile',
    'folder:getContents',
    'app:getAppInfo',
    'app:setAppInfo'
  ],
  // 从主进程到渲染进程的通道
  ON: [
    'menu-new-library',
    'menu-open-library',
    'menu-import-files',
    'app:update-available',
    'app:update-downloaded'
  ]
}

// 暴露安全的 API 给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 对话框相关
  openDirectory: () => ipcRenderer.invoke('dialog:openDirectory'),
  openFile: (options?: Electron.OpenDialogOptions) => 
    ipcRenderer.invoke('dialog:openFile', options),
  saveFile: (options?: Electron.SaveDialogOptions) => 
    ipcRenderer.invoke('dialog:saveFile', options),
  
  // 文件操作相关
  getFileInfo: (filePath: string) => 
    ipcRenderer.invoke('file:getFileInfo', filePath),
  readFile: (filePath: string, options?: any) => 
    ipcRenderer.invoke('file:readFile', filePath, options),
  writeFile: (filePath: string, content: string | Buffer, options?: any) => 
    ipcRenderer.invoke('file:writeFile', filePath, content, options),
  deleteFile: (filePath: string) => 
    ipcRenderer.invoke('file:deleteFile', filePath),
  
  // 文件夹操作
  getFolderContents: (folderPath: string) => 
    ipcRenderer.invoke('folder:getContents', folderPath),
  
  // 应用信息
  getAppInfo: () => ipcRenderer.invoke('app:getAppInfo'),
  setAppInfo: (info: Record<string, any>) => 
    ipcRenderer.invoke('app:setAppInfo', info),
  
  // 菜单事件监听
  onMenuNewLibrary: (callback: () => void) => {
    const subscription = (_: any) => callback()
    ipcRenderer.on('menu-new-library', subscription)
    return () => ipcRenderer.removeListener('menu-new-library', subscription)
  },
  
  onMenuOpenLibrary: (callback: (path: string) => void) => {
    const subscription = (_: any, path: string) => callback(path)
    ipcRenderer.on('menu-open-library', subscription)
    return () => ipcRenderer.removeListener('menu-open-library', subscription)
  },
  
  onMenuImportFiles: (callback: () => void) => {
    const subscription = (_: any) => callback()
    ipcRenderer.on('menu-import-files', subscription)
    return () => ipcRenderer.removeListener('menu-import-files', subscription)
  },
  
  // 应用更新事件
  onUpdateAvailable: (callback: (info: any) => void) => {
    const subscription = (_: any, info: any) => callback(info)
    ipcRenderer.on('app:update-available', subscription)
    return () => ipcRenderer.removeListener('app:update-available', subscription)
  },
  
  onUpdateDownloaded: (callback: () => void) => {
    const subscription = (_: any) => callback()
    ipcRenderer.on('app:update-downloaded', subscription)
    return () => ipcRenderer.removeListener('app:update-downloaded', subscription)
  },
  
  // 移除所有监听器
  removeAllListeners: () => {
    VALID_CHANNELS.ON.forEach(channel => {
      ipcRenderer.removeAllListeners(channel)
    })
  },
  
  // 环境信息
  isDev: process.env.NODE_ENV === 'development',
  platform: process.platform
})

// 类型声明
declare global {
  interface Window {
    electronAPI: {
      // 对话框相关
      openDirectory: () => Promise<Electron.OpenDialogReturnValue>
      openFile: (options?: Electron.OpenDialogOptions) => Promise<Electron.OpenDialogReturnValue>
      saveFile: (options?: Electron.SaveDialogOptions) => Promise<Electron.SaveDialogReturnValue>
      
      // 文件操作
      getFileInfo: (filePath: string) => Promise<{ path: string; size: number; type: string; modified?: number }>
      readFile: (filePath: string, options?: any) => Promise<string | Buffer>
      writeFile: (filePath: string, content: string | Buffer, options?: any) => Promise<void>
      deleteFile: (filePath: string) => Promise<void>
      
      // 文件夹操作
      getFolderContents: (folderPath: string) => Promise<Array<{ name: string; path: string; isDirectory: boolean; size?: number }>>
      
      // 应用信息
      getAppInfo: () => Promise<{ name: string; version: string; electron: string; chrome: string; node: string }>
      setAppInfo: (info: Record<string, any>) => Promise<void>
      
      // 事件监听器
      onMenuNewLibrary: () => () => void
      onMenuOpenLibrary: (callback: (path: string) => void) => () => void
      onMenuImportFiles: () => () => void
      onUpdateAvailable: (callback: (info: any) => void) => () => void
      onUpdateDownloaded: () => () => void
      removeAllListeners: () => void
      
      // 环境信息
      isDev: boolean
      platform: NodeJS.Platform
    }
  }
}