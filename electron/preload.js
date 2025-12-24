const { contextBridge, ipcRenderer } = require('electron')

// 暴露安全的API给渲染进程
contextBridge.exposeInMainWorld('electronAPI', {
  // 窗口控制
  minimizeWindow: () => ipcRenderer.invoke('window-control:minimize'),
  maximizeWindow: () => ipcRenderer.invoke('window-control:maximize'),
  unmaximizeWindow: () => ipcRenderer.invoke('window-control:unmaximize'),
  closeWindow: () => ipcRenderer.invoke('window-control:close'),
  isMaximized: () => ipcRenderer.invoke('window-control:isMaximized'),
  
  // 窗口事件监听
  onWindowMaximized: (callback) => ipcRenderer.on('window-maximized', callback),
  onWindowUnmaximized: (callback) => ipcRenderer.on('window-unmaximized', callback),
  
  // 平台信息
  platform: process.platform
})