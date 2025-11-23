import { app, BrowserWindow, Menu, shell, ipcMain, dialog } from 'electron'
import path, { join } from 'path'
import fs from 'fs'
import { isDev } from './utils'

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
  SEND: [
    'menu-new-library',
    'menu-open-library',
    'menu-import-files',
    'app:update-available',
    'app:update-downloaded'
  ]
}

let mainWindow: BrowserWindow | null = null

function createWindow(): void {
  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1200,
    minHeight: 800,
    titleBarStyle: 'hiddenInset',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: join(__dirname, 'preload.js'),
      webSecurity: !isDev,
    },
    icon: join(__dirname, '../assets/icon.ico'),
  })

  if (isDev) {
    mainWindow.loadURL('http://localhost:5173')
    mainWindow.webContents.openDevTools()
  } else {
    mainWindow.loadFile(join(__dirname, '../dist/index.html'))
  }

  // 处理外部链接
  mainWindow.webContents.setWindowOpenHandler(({ url }) => {
    shell.openExternal(url)
    return { action: 'deny' }
  })

  // 创建菜单
  createMenu()
}

function createMenu(): void {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '新建库',
          accelerator: process.platform === 'darwin' ? 'Cmd+N' : 'Ctrl+N',
          click: () => {
            mainWindow?.webContents.send('menu-new-library')
          },
        },
        {
          label: '打开库',
          accelerator: process.platform === 'darwin' ? 'Cmd+O' : 'Ctrl+O',
          click: async () => {
            const result = await dialog.showOpenDialog(mainWindow!, {
              properties: ['openDirectory'],
            })
            if (!result.canceled && result.filePaths.length > 0) {
              mainWindow?.webContents.send('menu-open-library', result.filePaths[0])
            }
          },
        },
        { type: 'separator' },
        {
          label: '导入文件',
          accelerator: process.platform === 'darwin' ? 'Cmd+I' : 'Ctrl+I',
          click: () => {
            mainWindow?.webContents.send('menu-import-files')
          },
        },
        { type: 'separator' },
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          },
        },
      ],
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' },
      ],
    },
    {
      label: '视图',
      submenu: [
        { role: 'reload', label: '重新加载' },
        { role: 'forceReload', label: '强制重新加载' },
        { role: 'toggleDevTools', label: '开发者工具' },
        { type: 'separator' },
        { role: 'resetZoom', label: '实际大小' },
        { role: 'zoomIn', label: '放大' },
        { role: 'zoomOut', label: '缩小' },
        { type: 'separator' },
        { role: 'togglefullscreen', label: '切换全屏' },
      ],
    },
    {
      label: '窗口',
      submenu: [
        { role: 'minimize', label: '最小化' },
        { role: 'close', label: '关闭' },
      ],
    },
  ]

  const menu = Menu.buildFromTemplate(template as any)
  Menu.setApplicationMenu(menu)
}

// 应用准备就绪
app.whenReady().then(() => {
  createWindow()

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow()
  })
})

// 所有窗口关闭时退出应用
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

// 处理对话框相关的IPC请求
ipcMain.handle('dialog:openDirectory', async (_, options = {}) => {
  const result = await dialog.showOpenDialog(mainWindow!, {
    properties: ['openDirectory'],
    ...options
  })
  return result
})

ipcMain.handle('dialog:openFile', async (_, options = {}) => {
  const defaultOptions = {
    properties: ['openFile', 'multiSelections'],
    filters: [
      { name: '图片文件', extensions: ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'heic'] },
      { name: '视频文件', extensions: ['mp4', 'mov', 'avi', 'mkv'] },
      { name: '所有文件', extensions: ['*'] },
    ]
  }
  const result = await dialog.showOpenDialog(mainWindow!, {
    ...defaultOptions,
    ...options
  })
  return result
})

ipcMain.handle('dialog:saveFile', async (_, options = {}) => {
  const defaultOptions = {
    properties: ['createDirectory']
  }
  const result = await dialog.showSaveDialog(mainWindow!, {
    ...defaultOptions,
    ...options
  })
  return result
})

// 文件操作相关的IPC请求
ipcMain.handle('file:getFileInfo', async (_, filePath) => {
  try {
    const stats = await fs.promises.stat(filePath)
    return {
      path: filePath,
      size: stats.size,
      type: stats.isDirectory() ? 'directory' : 'file',
      modified: stats.mtimeMs
    }
  } catch (error) {
    console.error('Error getting file info:', error)
    throw error
  }
})

ipcMain.handle('file:readFile', async (_, filePath, options = { encoding: 'utf8' }) => {
  try {
    return await fs.promises.readFile(filePath, options)
  } catch (error) {
    console.error('Error reading file:', error)
    throw error
  }
})

ipcMain.handle('file:writeFile', async (_, filePath, content, options = {}) => {
  try {
    // 确保目录存在
    const dir = join(path.dirname(filePath))
    await fs.promises.mkdir(dir, { recursive: true })
    await fs.promises.writeFile(filePath, content, options)
  } catch (error) {
    console.error('Error writing file:', error)
    throw error
  }
})

ipcMain.handle('file:deleteFile', async (_, filePath) => {
  try {
    const stats = await fs.promises.stat(filePath)
    if (stats.isDirectory()) {
      await fs.promises.rmdir(filePath, { recursive: true })
    } else {
      await fs.promises.unlink(filePath)
    }
  } catch (error) {
    console.error('Error deleting file:', error)
    throw error
  }
})

// 文件夹操作相关的IPC请求
ipcMain.handle('folder:getContents', async (_, folderPath) => {
  try {
    const entries = await fs.promises.readdir(folderPath, { withFileTypes: true })
    const contents = []
    
    for (const entry of entries) {
      const entryPath = join(folderPath, entry.name)
      let size = undefined
      
      if (!entry.isDirectory()) {
        try {
          const stats = await fs.promises.stat(entryPath)
          size = stats.size
        } catch (e) {
          console.warn(`Could not get size for ${entryPath}:`, e)
        }
      }
      
      contents.push({
        name: entry.name,
        path: entryPath,
        isDirectory: entry.isDirectory(),
        size
      })
    }
    
    return contents
  } catch (error) {
    console.error('Error getting folder contents:', error)
    throw error
  }
})

// 应用信息相关的IPC请求
ipcMain.handle('app:getAppInfo', async () => {
  return {
    name: app.name,
    version: app.getVersion(),
    electron: process.versions.electron,
    chrome: process.versions.chrome,
    node: process.versions.node
  }
})

ipcMain.handle('app:setAppInfo', async (_, info) => {
  // 这里可以根据需要设置应用信息
  console.log('Setting app info:', info)
})