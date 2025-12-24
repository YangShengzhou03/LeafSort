<template>
  <el-dropdown 
    trigger="click" 
    placement="bottom-end"
    @command="handleThemeChange"
    class="theme-toggle"
  >
    <el-button 
      :icon="currentThemeIcon" 
      size="small" 
      circle 
      class="theme-button"
      :title="`当前主题: ${currentThemeLabel}`"
    />
    
    <template #dropdown>
      <el-dropdown-menu class="theme-menu">
        <el-dropdown-item 
          v-for="theme in availableThemes" 
          :key="theme.name"
          :command="theme.name"
          :class="{ active: currentTheme === theme.name }"
        >
          <div class="theme-option">
            <el-icon class="theme-icon">
              <component :is="getThemeIcon(theme.name)" />
            </el-icon>
            <span class="theme-label">{{ theme.label }}</span>
            <el-icon v-if="currentTheme === theme.name" class="check-icon">
              <Check />
            </el-icon>
          </div>
        </el-dropdown-item>
        
        <el-dropdown-item divided @click="handleToggleTheme">
          <div class="theme-option">
            <el-icon class="theme-icon">
              <Switch />
            </el-icon>
            <span class="theme-label">切换主题</span>
          </div>
        </el-dropdown-item>
      </el-dropdown-menu>
    </template>
  </el-dropdown>
</template>

<script>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { Moon, Sunny, Check, Switch, Monitor } from '@element-plus/icons-vue'
import themeManager from '../utils/themeManager'

export default {
  name: 'ThemeToggle',
  components: {
    Moon, Sunny, Check, Switch, Monitor
  },
  setup() {
    const currentTheme = ref(themeManager.getCurrentTheme())
    const availableThemes = ref(themeManager.getAvailableThemes())

    const currentThemeIcon = computed(() => {
      return themeManager.getThemeIcon()
    })

    const currentThemeLabel = computed(() => {
      const theme = availableThemes.value.find(t => t.name === currentTheme.value)
      return theme ? theme.label : '未知主题'
    })

    const handleThemeChange = (themeName) => {
      themeManager.applyTheme(themeName)
    }

    const handleToggleTheme = () => {
      themeManager.toggleTheme()
    }

    const getThemeIcon = (themeName) => {
      switch (themeName) {
      case 'dark':
        return 'Moon'
      case 'light':
        return 'Sunny'
      case 'auto':
        return 'Monitor'
      default:
        return 'Sunny'
      }
    }

    const handleThemeChangeEvent = (event) => {
      currentTheme.value = event.detail.theme
    }

    onMounted(() => {
      themeManager.onThemeChange(handleThemeChangeEvent)
    })

    onUnmounted(() => {
      themeManager.offThemeChange(handleThemeChangeEvent)
    })

    return {
      currentTheme,
      availableThemes,
      currentThemeIcon,
      currentThemeLabel,
      handleThemeChange,
      handleToggleTheme,
      getThemeIcon
    }
  }
}
</script>

<style scoped>
.theme-toggle {
  display: inline-block;
}

.theme-button {
  border: 1px solid var(--border-light);
  background: var(--bg-card);
  color: var(--text-secondary);
  transition: border-color 0.3s ease, color 0.3s ease, background-color 0.3s ease, transform 0.3s ease, box-shadow 0.3s ease;
  will-change: border-color, color, background-color, transform, box-shadow;
}

.theme-button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
  background: var(--bg-hover);
}

.theme-menu {
  min-width: 160px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-xs) 0;
}

.theme-icon {
  font-size: 16px;
  color: var(--text-secondary);
}

.theme-label {
  flex: 1;
  font-size: var(--font-size-sm);
  color: var(--text-primary);
}

.check-icon {
  color: var(--primary-color);
  font-size: 14px;
}

.el-dropdown-item.active {
  background-color: var(--bg-active);
}

.el-dropdown-item:hover {
  background-color: var(--bg-hover);
}

.theme-button {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  will-change: transform, box-shadow;
}

.theme-button:hover {
  transform: scale(1.05);
  box-shadow: var(--shadow-md);
}

.theme-option {
  transition: all 0.2s ease;
  will-change: transform;
}

.theme-option:hover .theme-icon {
  color: var(--primary-color);
  transform: scale(1.1);
}

@media (max-width: 768px) {
  .theme-menu {
    min-width: 140px;
  }
  
  .theme-option {
    padding: var(--space-xs) 0;
  }
  
  .theme-label {
    font-size: var(--font-size-xs);
  }
}
</style>