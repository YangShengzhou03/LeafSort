const { app, BrowserWindow, Menu, ipcMain } = require('electron')
const path = require('path')
const isDev = process.env.NODE_ENV === 'development'

let mainWindow

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    frame: false, // 隐藏原生标题栏
    titleBarStyle: 'hidden', // 隐藏标题栏但保留窗口控制
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: false,
      webSecurity: true,
      preload: path.join(__dirname, 'preload.js') // 启用预加载脚本
    },
    icon: path.join(__dirname, '../public/favicon.ico'),
    show: false
  })

  // 加载应用

  mainWindow.loadURL('http://localhost:8080')

  // if (isDev) {
  //   mainWindow.loadURL('http://localhost:8080')
  //   mainWindow.webContents.openDevTools()
  // } else {
  //   mainWindow.loadFile(path.join(__dirname, '../dist/index.html'))
  // }

  // 窗口准备好后显示
  mainWindow.once('ready-to-show', () => {
    mainWindow.show()
  })

  mainWindow.on('closed', () => {
    mainWindow = null
  })

  // 设置菜单
  setApplicationMenu()
  
  // 窗口状态变化事件（必须在窗口创建后监听）
  mainWindow.on('maximize', () => {
    mainWindow.webContents.send('window-maximized')
  })
  
  mainWindow.on('unmaximize', () => {
    mainWindow.webContents.send('window-unmaximized')
  })
}

function setApplicationMenu() {
  const template = [
    {
      label: '文件',
      submenu: [
        {
          label: '退出',
          accelerator: process.platform === 'darwin' ? 'Cmd+Q' : 'Ctrl+Q',
          click: () => {
            app.quit()
          }
        }
      ]
    },
    {
      label: '编辑',
      submenu: [
        { role: 'undo', label: '撤销' },
        { role: 'redo', label: '重做' },
        { type: 'separator' },
        { role: 'cut', label: '剪切' },
        { role: 'copy', label: '复制' },
        { role: 'paste', label: '粘贴' }
      ]
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
        { role: 'togglefullscreen', label: '切换全屏' }
      ]
    }
  ]

  const menu = Menu.buildFromTemplate(template)
  Menu.setApplicationMenu(menu)
}

// 应用准备就绪时创建窗口
app.whenReady().then(createWindow)

// 所有窗口关闭时退出应用（macOS除外）
app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit()
  }
})

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow()
  }
})

// 安全设置
app.on('web-contents-created', (event, contents) => {
  contents.on('new-window', (event) => {
    event.preventDefault()
  })
})

// 窗口控制 IPC 处理程序
ipcMain.handle('window-control:minimize', () => {
  if (mainWindow) {
    mainWindow.minimize()
  }
})

ipcMain.handle('window-control:maximize', () => {
  if (mainWindow) {
    mainWindow.maximize()
  }
})

ipcMain.handle('window-control:unmaximize', () => {
  if (mainWindow) {
    mainWindow.unmaximize()
  }
})

ipcMain.handle('window-control:close', () => {
  if (mainWindow) {
    mainWindow.close()
  }
})

ipcMain.handle('window-control:isMaximized', () => {
  return mainWindow ? mainWindow.isMaximized() : false
})