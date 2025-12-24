<template>
  <div class="custom-title-bar" :class="{ 'maximized': isMaximized }">
    <div class="title-bar-center">
      <div class="search-container">
        <div class="input-wrapper search-input-wrapper">
          <el-icon class="search-icon"><Search /></el-icon>
          <input
            v-model="searchText"
            type="text"
            placeholder="搜索真/原型"
            class="input"
            @keyup.enter="handleSearch"
          />
          <el-icon class="clear-icon" v-if="searchText" @click="searchText = ''">
            <Close />
          </el-icon>
        </div>
      </div>
    </div>

    <div class="title-bar-right">
      <div class="function-buttons btn-row">
        <button class="btn btn-primary" @click="handleFunctionClick">
          <el-icon><Function /></el-icon>
          <span class="button-text">功能</span>
        </button>
        <button class="btn btn-secondary" @click="handleAdvancedSearch">
          <el-icon><Filter /></el-icon>
          <span class="button-text">多条件搜索</span>
        </button>
        <button class="btn btn-secondary" @click="handleExportImport">
          <el-icon><Document /></el-icon>
          <span class="button-text">导出/导入</span>
        </button>
        <button class="btn btn-secondary" @click="handleBatchOperations">
          <el-icon><Operation /></el-icon>
          <span class="button-text">批量操作</span>
        </button>
      </div>
      
      <div class="window-controls btn-row">
        <button class="btn btn-ghost btn-icon" @click="minimizeWindow" title="最小化">
          <el-icon><Minus /></el-icon>
        </button>

        <button class="btn btn-ghost btn-icon" @click="toggleMaximize" :title="isMaximized ? '还原' : '最大化'">
          <el-icon v-if="isMaximized"><CopyDocument /></el-icon>
          <el-icon v-else><FullScreen /></el-icon>
        </button>

        <button class="btn btn-ghost btn-icon close-btn" @click="closeWindow" title="关闭">
          <el-icon><Close /></el-icon>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import {
  Search,
  Close,
  Menu as Function,
  Document,
  Operation,
  Minus,
  FullScreen,
  CopyDocument,
  Filter
} from '@element-plus/icons-vue'

export default {
  name: 'CustomTitleBar',
  components: {
    Search,
    Close,
    Function,
    Document,
    Operation,
    Minus,
    FullScreen,
    CopyDocument,
    Filter
  },
  setup() {
    const searchText = ref('')
    const isDark = ref(true)
    const isMaximized = ref(false)

    const isElectron = typeof window !== 'undefined' && window.electronAPI

    const windowControl = (action) => {
      if (isElectron && window.electronAPI[action]) {
        window.electronAPI[action]()
      }
    }

    const minimizeWindow = () => windowControl('minimizeWindow')
    const maximizeWindow = () => windowControl('maximizeWindow')
    const unmaximizeWindow = () => windowControl('unmaximizeWindow')
    const closeWindow = () => windowControl('closeWindow')

    const toggleMaximize = async () => {
      if (!isElectron) return
      
      if (isMaximized.value) {
        unmaximizeWindow()
      } else {
        maximizeWindow()
      }
    }

    const checkWindowState = async () => {
      if (isElectron) {
        isMaximized.value = await window.electronAPI.isMaximized()
      }
    }

    const handleSearch = () => {
      // 搜索功能待实现
    }

    const handleFunctionClick = () => {
      // 功能按钮点击事件待实现
    }

    const handleAdvancedSearch = () => {
      // 多条件搜索功能待实现
    }

    const handleExportImport = () => {
      // 导出/导入功能待实现
    }

    const handleBatchOperations = () => {
      // 批量操作功能待实现
    }

    onMounted(() => {
      checkWindowState()
      
      document.documentElement.setAttribute('data-theme', 'dark')
      
      if (isElectron) {
        window.electronAPI.onWindowMaximized(() => {
          isMaximized.value = true
        })
        
        window.electronAPI.onWindowUnmaximized(() => {
          isMaximized.value = false
        })
      }
    })

    return {
      searchText,
      isDark,
      isMaximized,
      minimizeWindow,
      toggleMaximize,
      closeWindow,
      handleSearch,
      handleFunctionClick,
      handleAdvancedSearch,
      handleExportImport,
      handleBatchOperations
    }
  }
}
</script>

<style scoped>
.custom-title-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  background: rgba(30, 30, 30, 0.85);
  backdrop-filter: blur(12px) saturate(150%);
  -webkit-backdrop-filter: blur(12px) saturate(150%);
  color: #ffffff;
  -webkit-app-region: drag;
  user-select: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  position: relative;
  z-index: 1000;
  padding: 0 20px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.custom-title-bar.maximized {
  padding-top: 0;
}

.title-bar-left,
.title-bar-center,
.title-bar-right {
  display: flex;
  align-items: center;
  height: 100%;
}

.title-bar-left {
  min-width: 180px;
  gap: 12px;
}

.app-icon {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  overflow: hidden;
  background-color: rgba(255, 255, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.app-icon img {
  width: 70%;
  height: 70%;
  object-fit: contain;
}

.app-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 18px;
  font-weight: 600;
  background: linear-gradient(135deg, #ffffff 0%, #cccccc 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.title-icon {
  font-size: 22px;
  color: #409EFF;
  filter: drop-shadow(0 2px 4px rgba(64, 158, 255, 0.3));
}

.title-bar-center {
  flex: 1;
  justify-content: center;
  max-width: 600px;
  margin: 0 30px;
}

.search-container {
  width: 100%;
  max-width: 500px;
  position: relative;
}

.search-input-wrapper {
  width: 100%;
  max-width: 450px;
  background-color: rgba(40, 40, 40, 0.8);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
}

.search-input-wrapper:focus-within {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px var(--accent-primary-glow);
}

.search-icon {
  color: var(--text-tertiary);
  font-size: 16px;
  margin-left: var(--space-3);
}

.clear-icon {
  color: var(--text-tertiary);
  font-size: 14px;
  cursor: pointer;
  margin-right: var(--space-3);
  transition: all var(--transition-fast);
}

.clear-icon:hover {
  color: var(--text-primary);
  transform: scale(1.1);
}

.title-bar-right {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  min-width: 320px;
}

.function-buttons {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  -webkit-app-region: no-drag;
}

.function-buttons .btn {
  font-size: var(--font-size-sm);
  border-radius: var(--radius-full);
  padding: 0 var(--space-4);
}

.window-controls {
  display: flex;
  align-items: center;
  -webkit-app-region: no-drag;
  gap: var(--space-1);
}

.window-controls .btn-icon {
  width: 36px;
  height: 36px;
  min-width: 36px;
  padding: 0;
  border-radius: var(--radius-md);
  background: transparent;
  border: 1px solid transparent;
  color: var(--text-secondary);
}

.window-controls .btn-icon:hover {
  background: var(--glass-light);
  color: var(--text-primary);
}

.window-controls .close-btn:hover {
  background: rgba(245, 108, 108, 0.15);
  color: var(--error);
  border-color: rgba(245, 108, 108, 0.3);
}

@media (max-width: 1200px) {
  .function-buttons .btn .button-text {
    display: none;
  }
  
  .function-buttons .btn {
    width: 36px;
    min-width: 36px;
    padding: 0;
  }
  
  .title-bar-right {
    gap: var(--space-3);
    min-width: 280px;
  }
}

@media (max-width: 768px) {
  .title-bar-center {
    display: none;
  }
  
  .title-bar-left {
    min-width: auto;
  }
  
  .title-bar-right {
    min-width: auto;
  }
  
  .app-title span {
    display: none;
  }
}
</style>