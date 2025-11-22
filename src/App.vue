<template>
  <div id="app" :class="{ 'dark-theme': isDarkTheme }">
    <el-config-provider :locale="zhCn">
      <router-view />
    </el-config-provider>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
const isDarkTheme = ref(false)

onMounted(() => {
  // 监听主题变化
  isDarkTheme.value = themeStore.isDark
  
  // 监听系统主题变化
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handleThemeChange = (e: MediaQueryListEvent) => {
    if (themeStore.followSystem) {
      isDarkTheme.value = e.matches
    }
  }
  
  mediaQuery.addEventListener('change', handleThemeChange)
  
  return () => {
    mediaQuery.removeEventListener('change', handleThemeChange)
  }
})
</script>

<style lang="scss">
#app {
  width: 100vw;
  height: 100vh;
  overflow: hidden;
  font-family: 'Inter', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  
  &.dark-theme {
    background-color: #1a1a1a;
    color: #ffffff;
  }
  
  &.light-theme {
    background-color: #ffffff;
    color: #303133;
  }
}

// 全局样式重置
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

// 滚动条样式
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.dark-theme {
  ::-webkit-scrollbar-track {
    background: #2d2d2d;
  }
  
  ::-webkit-scrollbar-thumb {
    background: #555;
  }
  
  ::-webkit-scrollbar-thumb:hover {
    background: #666;
  }
}
</style>