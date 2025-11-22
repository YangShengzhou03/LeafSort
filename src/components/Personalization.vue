<template>
  <div class="personalization">
    <!-- 顶部工具栏 -->
    <div class="personalization-toolbar">
      <div class="toolbar-left">
        <h2><el-icon><Setting /></el-icon> 个性化设置</h2>
      </div>
      <div class="toolbar-right">
        <el-button @click="exportSettings">
          <el-icon><Download /></el-icon> 导出配置
        </el-button>
        <el-button @click="importSettings">
          <el-icon><Upload /></el-icon> 导入配置
        </el-button>
        <el-button type="primary" @click="saveSettings">
          <el-icon><Check /></el-icon> 保存设置
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="personalization-content">
      <!-- 左侧导航菜单 -->
      <div class="settings-nav">
        <el-menu 
          :default-active="activeNav" 
          class="settings-menu"
          @select="handleNavSelect"
        >
          <el-menu-item index="appearance">
            <el-icon><Brush /></el-icon>
            <span>外观主题</span>
          </el-menu-item>
          <el-menu-item index="interface">
            <el-icon><Monitor /></el-icon>
            <span>界面定制</span>
          </el-menu-item>
          <el-menu-item index="shortcuts">
            <el-icon><Keyboard /></el-icon>
            <span>快捷键</span>
          </el-menu-item>
          <el-menu-item index="behavior">
            <el-icon><Operation /></el-icon>
            <span>行为设置</span>
          </el-menu-item>
          <el-menu-item index="notifications">
            <el-icon><Bell /></el-icon>
            <span>通知设置</span>
          </el-menu-item>
          <el-menu-item index="advanced">
            <el-icon><Cpu /></el-icon>
            <span>高级设置</span>
          </el-menu-item>
        </el-menu>
      </div>

      <!-- 右侧设置内容 -->
      <div class="settings-content">
        <!-- 外观主题设置 -->
        <div v-show="activeNav === 'appearance'" class="settings-section">
          <h3>外观主题设置</h3>
          
          <div class="theme-settings">
            <!-- 主题模式选择 -->
            <div class="setting-group">
              <h4>主题模式</h4>
              <div class="theme-modes">
                <div 
                  class="theme-mode-card"
                  :class="{ active: appearanceSettings.themeMode === 'light' }"
                  @click="appearanceSettings.themeMode = 'light'"
                >
                  <div class="theme-preview light">
                    <div class="preview-header"></div>
                    <div class="preview-content">
                      <div class="preview-sidebar"></div>
                      <div class="preview-main"></div>
                    </div>
                  </div>
                  <div class="theme-info">
                    <div class="theme-name">浅色主题</div>
                    <div class="theme-description">明亮舒适的界面</div>
                  </div>
                </div>
                
                <div 
                  class="theme-mode-card"
                  :class="{ active: appearanceSettings.themeMode === 'dark' }"
                  @click="appearanceSettings.themeMode = 'dark'"
                >
                  <div class="theme-preview dark">
                    <div class="preview-header"></div>
                    <div class="preview-content">
                      <div class="preview-sidebar"></div>
                      <div class="preview-main"></div>
                    </div>
                  </div>
                  <div class="theme-info">
                    <div class="theme-name">深色主题</div>
                    <div class="theme-description">护眼舒适的界面</div>
                  </div>
                </div>
                
                <div 
                  class="theme-mode-card"
                  :class="{ active: appearanceSettings.themeMode === 'auto' }"
                  @click="appearanceSettings.themeMode = 'auto'"
                >
                  <div class="theme-preview auto">
                    <div class="preview-header"></div>
                    <div class="preview-content">
                      <div class="preview-sidebar"></div>
                      <div class="preview-main"></div>
                    </div>
                  </div>
                  <div class="theme-info">
                    <div class="theme-name">自动切换</div>
                    <div class="theme-description">跟随系统主题</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- 主题色选择 -->
            <div class="setting-group">
              <h4>主题色彩</h4>
              <div class="color-picker-section">
                <div class="color-presets">
                  <div 
                    v-for="color in colorPresets" 
                    :key="color.name"
                    class="color-preset"
                    :style="{ backgroundColor: color.value }"
                    :class="{ active: appearanceSettings.primaryColor === color.value }"
                    @click="appearanceSettings.primaryColor = color.value"
                  >
                    <el-icon v-if="appearanceSettings.primaryColor === color.value">
                      <Check />
                    </el-icon>
                  </div>
                </div>
                
                <div class="custom-color">
                  <span>自定义颜色:</span>
                  <el-color-picker 
                    v-model="appearanceSettings.primaryColor"
                    show-alpha
                    :predefine="predefineColors"
                  />
                  <span class="color-value">{{ appearanceSettings.primaryColor }}</span>
                </div>
              </div>
            </div>

            <!-- 字体设置 -->
            <div class="setting-group">
              <h4>字体设置</h4>
              <el-form :model="appearanceSettings" label-width="120px">
                <el-form-item label="字体家族">
                  <el-select v-model="appearanceSettings.fontFamily">
                    <el-option label="系统默认" value="system-ui"></el-option>
                    <el-option label="微软雅黑" value="Microsoft YaHei"></el-option>
                    <el-option label="思源黑体" value="Source Han Sans"></el-option>
                    <el-option label="苹方" value="PingFang SC"></el-option>
                    <el-option label="HarmonyOS Sans" value="HarmonyOS Sans"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="字体大小">
                  <el-slider 
                    v-model="appearanceSettings.fontSize" 
                    :min="12" 
                    :max="18"
                    :step="1"
                    show-stops
                  />
                  <span class="slider-value">{{ appearanceSettings.fontSize }}px</span>
                </el-form-item>
                
                <el-form-item label="字体粗细">
                  <el-select v-model="appearanceSettings.fontWeight">
                    <el-option label="细体" value="300"></el-option>
                    <el-option label="常规" value="400"></el-option>
                    <el-option label="中等" value="500"></el-option>
                    <el-option label="粗体" value="600"></el-option>
                  </el-select>
                </el-form-item>
              </el-form>
            </div>

            <!-- 动画效果 -->
            <div class="setting-group">
              <h4>动画效果</h4>
              <el-form :model="appearanceSettings" label-width="120px">
                <el-form-item label="启用动画">
                  <el-switch v-model="appearanceSettings.enableAnimations"></el-switch>
                </el-form-item>
                
                <el-form-item label="动画速度">
                  <el-slider 
                    v-model="appearanceSettings.animationSpeed" 
                    :min="0.5" 
                    :max="2"
                    :step="0.1"
                    show-stops
                  />
                  <span class="slider-value">{{ appearanceSettings.animationSpeed }}x</span>
                </el-form-item>
                
                <el-form-item label="动画类型">
                  <el-select v-model="appearanceSettings.animationType">
                    <el-option label="淡入淡出" value="fade"></el-option>
                    <el-option label="滑动" value="slide"></el-option>
                    <el-option label="缩放" value="scale"></el-option>
                    <el-option label="组合动画" value="combined"></el-option>
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 界面定制设置 -->
        <div v-show="activeNav === 'interface'" class="settings-section">
          <h3>界面定制设置</h3>
          
          <div class="interface-settings">
            <!-- 布局设置 -->
            <div class="setting-group">
              <h4>布局设置</h4>
              <el-form :model="interfaceSettings" label-width="120px">
                <el-form-item label="界面布局">
                  <el-radio-group v-model="interfaceSettings.layout">
                    <el-radio label="classic">经典布局</el-radio>
                    <el-radio label="compact">紧凑布局</el-radio>
                    <el-radio label="modern">现代布局</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="侧边栏位置">
                  <el-radio-group v-model="interfaceSettings.sidebarPosition">
                    <el-radio label="left">左侧</el-radio>
                    <el-radio label="right">右侧</el-radio>
                    <el-radio label="top">顶部</el-radio>
                  </el-radio-group>
                </el-form-item>
                
                <el-form-item label="侧边栏宽度">
                  <el-slider 
                    v-model="interfaceSettings.sidebarWidth" 
                    :min="200" 
                    :max="400"
                    :step="10"
                  />
                  <span class="slider-value">{{ interfaceSettings.sidebarWidth }}px</span>
                </el-form-item>
              </el-form>
            </div>

            <!-- 工具栏设置 -->
            <div class="setting-group">
              <h4>工具栏设置</h4>
              <el-form :model="interfaceSettings" label-width="120px">
                <el-form-item label="显示工具栏">
                  <el-switch v-model="interfaceSettings.showToolbar"></el-switch>
                </el-form-item>
                
                <el-form-item label="工具栏位置">
                  <el-select v-model="interfaceSettings.toolbarPosition">
                    <el-option label="顶部" value="top"></el-option>
                    <el-option label="底部" value="bottom"></el-option>
                    <el-option label="左侧" value="left"></el-option>
                    <el-option label="右侧" value="right"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="工具栏按钮大小">
                  <el-radio-group v-model="interfaceSettings.toolbarButtonSize">
                    <el-radio label="small">小</el-radio>
                    <el-radio label="medium">中</el-radio>
                    <el-radio label="large">大</el-radio>
                  </el-radio-group>
                </el-form-item>
              </el-form>
            </div>

            <!-- 内容区域设置 -->
            <div class="setting-group">
              <h4>内容区域设置</h4>
              <el-form :model="interfaceSettings" label-width="120px">
                <el-form-item label="网格密度">
                  <el-slider 
                    v-model="interfaceSettings.gridDensity" 
                    :min="1" 
                    :max="5"
                    :step="1"
                    show-stops
                  />
                  <span class="slider-value">{{ getGridDensityText(interfaceSettings.gridDensity) }}</span>
                </el-form-item>
                
                <el-form-item label="缩略图大小">
                  <el-slider 
                    v-model="interfaceSettings.thumbnailSize" 
                    :min="80" 
                    :max="200"
                    :step="10"
                  />
                  <span class="slider-value">{{ interfaceSettings.thumbnailSize }}px</span>
                </el-form-item>
                
                <el-form-item label="显示文件信息">
                  <el-switch v-model="interfaceSettings.showFileInfo"></el-switch>
                </el-form-item>
                
                <el-form-item label="显示文件扩展名">
                  <el-switch v-model="interfaceSettings.showFileExtension"></el-switch>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 快捷键设置 -->
        <div v-show="activeNav === 'shortcuts'" class="settings-section">
          <h3>快捷键设置</h3>
          
          <div class="shortcuts-settings">
            <div class="shortcuts-list">
              <div v-for="shortcut in shortcuts" :key="shortcut.id" class="shortcut-item">
                <div class="shortcut-info">
                  <div class="shortcut-name">{{ shortcut.name }}</div>
                  <div class="shortcut-description">{{ shortcut.description }}</div>
                </div>
                <div class="shortcut-keys">
                  <el-input 
                    v-model="shortcut.key" 
                    placeholder="点击设置快捷键"
                    @focus="startRecording(shortcut)"
                    @blur="stopRecording"
                    readonly
                  />
                </div>
                <div class="shortcut-actions">
                  <el-button @click="resetShortcut(shortcut)" size="small">重置</el-button>
                </div>
              </div>
            </div>
            
            <div class="shortcuts-actions">
              <el-button @click="resetAllShortcuts" type="warning">重置所有快捷键</el-button>
              <el-button @click="importShortcuts" type="info">导入快捷键</el-button>
              <el-button @click="exportShortcuts" type="primary">导出快捷键</el-button>
            </div>
          </div>
        </div>

        <!-- 行为设置 -->
        <div v-show="activeNav === 'behavior'" class="settings-section">
          <h3>行为设置</h3>
          
          <div class="behavior-settings">
            <!-- 文件操作行为 -->
            <div class="setting-group">
              <h4>文件操作行为</h4>
              <el-form :model="behaviorSettings" label-width="160px">
                <el-form-item label="双击文件行为">
                  <el-select v-model="behaviorSettings.doubleClickAction">
                    <el-option label="预览文件" value="preview"></el-option>
                    <el-option label="打开文件" value="open"></el-option>
                    <el-option label="编辑文件" value="edit"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="拖拽文件行为">
                  <el-select v-model="behaviorSettings.dragAction">
                    <el-option label="移动文件" value="move"></el-option>
                    <el-option label="复制文件" value="copy"></el-option>
                    <el-option label="创建快捷方式" value="shortcut"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="删除文件确认">
                  <el-switch v-model="behaviorSettings.confirmDelete"></el-switch>
                </el-form-item>
                
                <el-form-item label="删除文件到回收站">
                  <el-switch v-model="behaviorSettings.moveToRecycleBin"></el-switch>
                </el-form-item>
              </el-form>
            </div>

            <!-- 搜索行为 -->
            <div class="setting-group">
              <h4>搜索行为</h4>
              <el-form :model="behaviorSettings" label-width="160px">
                <el-form-item label="实时搜索">
                  <el-switch v-model="behaviorSettings.realTimeSearch"></el-switch>
                </el-form-item>
                
                <el-form-item label="搜索延迟">
                  <el-slider 
                    v-model="behaviorSettings.searchDelay" 
                    :min="100" 
                    :max="1000"
                    :step="100"
                  />
                  <span class="slider-value">{{ behaviorSettings.searchDelay }}ms</span>
                </el-form-item>
                
                <el-form-item label="保存搜索历史">
                  <el-switch v-model="behaviorSettings.saveSearchHistory"></el-switch>
                </el-form-item>
                
                <el-form-item label="搜索历史数量">
                  <el-input-number 
                    v-model="behaviorSettings.searchHistoryLimit" 
                    :min="10" 
                    :max="100"
                  />
                </el-form-item>
              </el-form>
            </div>

            <!-- 启动行为 -->
            <div class="setting-group">
              <h4>启动行为</h4>
              <el-form :model="behaviorSettings" label-width="160px">
                <el-form-item label="开机自启动">
                  <el-switch v-model="behaviorSettings.autoStart"></el-switch>
                </el-form-item>
                
                <el-form-item label="启动时显示欢迎页">
                  <el-switch v-model="behaviorSettings.showWelcome"></el-switch>
                </el-form-item>
                
                <el-form-item label="启动时恢复上次会话">
                  <el-switch v-model="behaviorSettings.restoreSession"></el-switch>
                </el-form-item>
                
                <el-form-item label="最小化到系统托盘">
                  <el-switch v-model="behaviorSettings.minimizeToTray"></el-switch>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 通知设置 -->
        <div v-show="activeNav === 'notifications'" class="settings-section">
          <h3>通知设置</h3>
          
          <div class="notifications-settings">
            <!-- 通知类型 -->
            <div class="setting-group">
              <h4>通知类型</h4>
              <el-form :model="notificationSettings" label-width="140px">
                <el-form-item label="系统通知">
                  <el-switch v-model="notificationSettings.systemNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="操作成功通知">
                  <el-switch v-model="notificationSettings.successNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="操作失败通知">
                  <el-switch v-model="notificationSettings.errorNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="警告通知">
                  <el-switch v-model="notificationSettings.warningNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="信息通知">
                  <el-switch v-model="notificationSettings.infoNotifications"></el-switch>
                </el-form-item>
              </el-form>
            </div>

            <!-- 通知方式 -->
            <div class="setting-group">
              <h4>通知方式</h4>
              <el-form :model="notificationSettings" label-width="140px">
                <el-form-item label="桌面通知">
                  <el-switch v-model="notificationSettings.desktopNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="声音提醒">
                  <el-switch v-model="notificationSettings.soundNotifications"></el-switch>
                </el-form-item>
                
                <el-form-item label="任务栏闪烁">
                  <el-switch v-model="notificationSettings.taskbarFlash"></el-switch>
                </el-form-item>
                
                <el-form-item label="通知持续时间">
                  <el-slider 
                    v-model="notificationSettings.notificationDuration" 
                    :min="2000" 
                    :max="10000"
                    :step="1000"
                  />
                  <span class="slider-value">{{ notificationSettings.notificationDuration / 1000 }}秒</span>
                </el-form-item>
              </el-form>
            </div>

            <!-- 通知内容 -->
            <div class="setting-group">
              <h4>通知内容</h4>
              <el-form :model="notificationSettings" label-width="140px">
                <el-form-item label="显示详细内容">
                  <el-switch v-model="notificationSettings.showDetails"></el-switch>
                </el-form-item>
                
                <el-form-item label="显示操作按钮">
                  <el-switch v-model="notificationSettings.showActions"></el-switch>
                </el-form-item>
                
                <el-form-item label="显示应用图标">
                  <el-switch v-model="notificationSettings.showAppIcon"></el-switch>
                </el-form-item>
                
                <el-form-item label="通知位置">
                  <el-select v-model="notificationSettings.notificationPosition">
                    <el-option label="右上角" value="top-right"></el-option>
                    <el-option label="右下角" value="bottom-right"></el-option>
                    <el-option label="左上角" value="top-left"></el-option>
                    <el-option label="左下角" value="bottom-left"></el-option>
                  </el-select>
                </el-form-item>
              </el-form>
            </div>
          </div>
        </div>

        <!-- 高级设置 -->
        <div v-show="activeNav === 'advanced'" class="settings-section">
          <h3>高级设置</h3>
          
          <div class="advanced-settings">
            <!-- 性能设置 -->
            <div class="setting-group">
              <h4>性能设置</h4>
              <el-form :model="advancedSettings" label-width="160px">
                <el-form-item label="硬件加速">
                  <el-switch v-model="advancedSettings.hardwareAcceleration"></el-switch>
                </el-form-item>
                
                <el-form-item label="缓存大小">
                  <el-slider 
                    v-model="advancedSettings.cacheSize" 
                    :min="100" 
                    :max="1000"
                    :step="50"
                  />
                  <span class="slider-value">{{ advancedSettings.cacheSize }}MB</span>
                </el-form-item>
                
                <el-form-item label="最大线程数">
                  <el-input-number 
                    v-model="advancedSettings.maxThreads" 
                    :min="1" 
                    :max="16"
                  />
                </el-form-item>
                
                <el-form-item label="内存使用限制">
                  <el-slider 
                    v-model="advancedSettings.memoryLimit" 
                    :min="512" 
                    :max="4096"
                    :step="256"
                  />
                  <span class="slider-value">{{ advancedSettings.memoryLimit }}MB</span>
                </el-form-item>
              </el-form>
            </div>

            <!-- 开发者选项 -->
            <div class="setting-group">
              <h4>开发者选项</h4>
              <el-form :model="advancedSettings" label-width="160px">
                <el-form-item label="开发者模式">
                  <el-switch v-model="advancedSettings.developerMode"></el-switch>
                </el-form-item>
                
                <el-form-item label="调试模式">
                  <el-switch v-model="advancedSettings.debugMode"></el-switch>
                </el-form-item>
                
                <el-form-item label="日志级别">
                  <el-select v-model="advancedSettings.logLevel">
                    <el-option label="错误" value="error"></el-option>
                    <el-option label="警告" value="warn"></el-option>
                    <el-option label="信息" value="info"></el-option>
                    <el-option label="调试" value="debug"></el-option>
                  </el-select>
                </el-form-item>
                
                <el-form-item label="性能监控">
                  <el-switch v-model="advancedSettings.performanceMonitoring"></el-switch>
                </el-form-item>
              </el-form>
            </div>

            <!-- 重置选项 -->
            <div class="setting-group">
              <h4>重置选项</h4>
              <div class="reset-options">
                <el-button @click="resetAppearance" type="warning" size="small">重置外观设置</el-button>
                <el-button @click="resetInterface" type="warning" size="small">重置界面设置</el-button>
                <el-button @click="resetShortcuts" type="warning" size="small">重置快捷键</el-button>
                <el-button @click="resetAllSettings" type="danger" size="small">重置所有设置</el-button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useThemeStore } from '@/stores/theme'

// 主题存储
const themeStore = useThemeStore()

// 响应式数据
const activeNav = ref('appearance')

// 外观设置
const appearanceSettings = reactive({
  themeMode: 'auto', // light, dark, auto
  primaryColor: '#409EFF',
  fontFamily: 'system-ui',
  fontSize: 14,
  fontWeight: '400',
  enableAnimations: true,
  animationSpeed: 1.0,
  animationType: 'fade'
})

// 界面设置
const interfaceSettings = reactive({
  layout: 'classic',
  sidebarPosition: 'left',
  sidebarWidth: 280,
  showToolbar: true,
  toolbarPosition: 'top',
  toolbarButtonSize: 'medium',
  gridDensity: 3,
  thumbnailSize: 120,
  showFileInfo: true,
  showFileExtension: false
})

// 行为设置
const behaviorSettings = reactive({
  doubleClickAction: 'preview',
  dragAction: 'move',
  confirmDelete: true,
  moveToRecycleBin: true,
  realTimeSearch: true,
  searchDelay: 300,
  saveSearchHistory: true,
  searchHistoryLimit: 20,
  autoStart: false,
  showWelcome: true,
  restoreSession: true,
  minimizeToTray: true
})

// 通知设置
const notificationSettings = reactive({
  systemNotifications: true,
  successNotifications: true,
  errorNotifications: true,
  warningNotifications: true,
  infoNotifications: false,
  desktopNotifications: true,
  soundNotifications: false,
  taskbarFlash: true,
  notificationDuration: 5000,
  showDetails: true,
  showActions: true,
  showAppIcon: true,
  notificationPosition: 'top-right'
})

// 高级设置
const advancedSettings = reactive({
  hardwareAcceleration: true,
  cacheSize: 500,
  maxThreads: 4,
  memoryLimit: 2048,
  developerMode: false,
  debugMode: false,
  logLevel: 'info',
  performanceMonitoring: false
})

// 快捷键设置
const shortcuts = ref([
  { id: 'newFile', name: '新建文件', description: '创建新文件', key: 'Ctrl+N' },
  { id: 'openFile', name: '打开文件', description: '打开文件对话框', key: 'Ctrl+O' },
  { id: 'saveFile', name: '保存文件', description: '保存当前文件', key: 'Ctrl+S' },
  { id: 'search', name: '搜索', description: '打开搜索面板', key: 'Ctrl+F' },
  { id: 'preview', name: '预览文件', description: '预览选中文件', key: 'Space' },
  { id: 'zoomIn', name: '放大', description: '放大视图', key: 'Ctrl+Plus' },
  { id: 'zoomOut', name: '缩小', description: '缩小视图', key: 'Ctrl+Minus' },
  { id: 'actualSize', name: '实际大小', description: '恢复实际大小', key: 'Ctrl+0' },
  { id: 'toggleSidebar', name: '切换侧边栏', description: '显示/隐藏侧边栏', key: 'Ctrl+B' },
  { id: 'toggleDarkMode', name: '切换暗色模式', description: '切换明暗主题', key: 'Ctrl+D' }
])

// 颜色预设
const colorPresets = ref([
  { name: '蓝色', value: '#409EFF' },
  { name: '绿色', value: '#67C23A' },
  { name: '橙色', value: '#E6A23C' },
  { name: '红色', value: '#F56C6C' },
  { name: '紫色', value: '#8E44AD' },
  { name: '青色', value: '#17A2B8' }
])

// 预定义颜色
const predefineColors = ref([
  '#409EFF',
  '#67C23A',
  '#E6A23C',
  '#F56C6C',
  '#8E44AD',
  '#17A2B8',
  '#606266',
  '#C0C4CC',
  '#909399',
  '#F2F6FC'
])

// 方法定义
const handleNavSelect = (index: string) => {
  activeNav.value = index
}

const getGridDensityText = (density: number) => {
  const texts = ['极稀疏', '稀疏', '适中', '密集', '极密集']
  return texts[density - 1] || '适中'
}

const startRecording = (shortcut: any) => {
  ElMessage.info('请按下新的快捷键组合...')
  // 快捷键录制逻辑
}

const stopRecording = () => {
  // 停止录制逻辑
}

const resetShortcut = (shortcut: any) => {
  const defaultShortcuts = {
    newFile: 'Ctrl+N',
    openFile: 'Ctrl+O',
    saveFile: 'Ctrl+S',
    search: 'Ctrl+F',
    preview: 'Space',
    zoomIn: 'Ctrl+Plus',
    zoomOut: 'Ctrl+Minus',
    actualSize: 'Ctrl+0',
    toggleSidebar: 'Ctrl+B',
    toggleDarkMode: 'Ctrl+D'
  }
  
  shortcut.key = defaultShortcuts[shortcut.id as keyof typeof defaultShortcuts] || shortcut.key
  ElMessage.success(`已重置快捷键: ${shortcut.name}`)
}

const resetAllShortcuts = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有快捷键吗？', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    shortcuts.value.forEach(shortcut => {
      resetShortcut(shortcut)
    })
    
    ElMessage.success('所有快捷键已重置为默认值')
  } catch {
    // 用户取消操作
  }
}

const importShortcuts = () => {
  ElMessage.info('快捷键导入功能开发中...')
}

const exportShortcuts = () => {
  ElMessage.info('快捷键导出功能开发中...')
}

const exportSettings = () => {
  const settings = {
    appearance: appearanceSettings,
    interface: interfaceSettings,
    behavior: behaviorSettings,
    notifications: notificationSettings,
    advanced: advancedSettings,
    shortcuts: shortcuts.value
  }
  
  const blob = new Blob([JSON.stringify(settings, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'leafview-settings.json'
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('设置已导出')
}

const importSettings = () => {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.json'
  input.onchange = (e) => {
    const file = (e.target as HTMLInputElement).files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        try {
          const settings = JSON.parse(event.target?.result as string)
          Object.assign(appearanceSettings, settings.appearance || {})
          Object.assign(interfaceSettings, settings.interface || {})
          Object.assign(behaviorSettings, settings.behavior || {})
          Object.assign(notificationSettings, settings.notifications || {})
          Object.assign(advancedSettings, settings.advanced || {})
          
          if (settings.shortcuts) {
            shortcuts.value = settings.shortcuts
          }
          
          ElMessage.success('设置已导入')
        } catch (error) {
          ElMessage.error('导入失败：文件格式错误')
        }
      }
      reader.readAsText(file)
    }
  }
  input.click()
}

const saveSettings = () => {
  // 保存设置到本地存储
  const settings = {
    appearance: appearanceSettings,
    interface: interfaceSettings,
    behavior: behaviorSettings,
    notifications: notificationSettings,
    advanced: advancedSettings,
    shortcuts: shortcuts.value
  }
  
  localStorage.setItem('leafview-settings', JSON.stringify(settings))
  
  // 应用主题设置
  themeStore.setTheme(appearanceSettings.themeMode)
  themeStore.setPrimaryColor(appearanceSettings.primaryColor)
  
  ElMessage.success('设置已保存')
}

const resetAppearance = async () => {
  try {
    await ElMessageBox.confirm('确定要重置外观设置吗？', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    Object.assign(appearanceSettings, {
      themeMode: 'auto',
      primaryColor: '#409EFF',
      fontFamily: 'system-ui',
      fontSize: 14,
      fontWeight: '400',
      enableAnimations: true,
      animationSpeed: 1.0,
      animationType: 'fade'
    })
    
    ElMessage.success('外观设置已重置')
  } catch {
    // 用户取消操作
  }
}

const resetInterface = async () => {
  try {
    await ElMessageBox.confirm('确定要重置界面设置吗？', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    Object.assign(interfaceSettings, {
      layout: 'classic',
      sidebarPosition: 'left',
      sidebarWidth: 280,
      showToolbar: true,
      toolbarPosition: 'top',
      toolbarButtonSize: 'medium',
      gridDensity: 3,
      thumbnailSize: 120,
      showFileInfo: true,
      showFileExtension: false
    })
    
    ElMessage.success('界面设置已重置')
  } catch {
    // 用户取消操作
  }
}

const resetAllSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有设置吗？此操作不可撤销！', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'error'
    })
    
    resetAppearance()
    resetInterface()
    resetAllShortcuts()
    
    Object.assign(behaviorSettings, {
      doubleClickAction: 'preview',
      dragAction: 'move',
      confirmDelete: true,
      moveToRecycleBin: true,
      realTimeSearch: true,
      searchDelay: 300,
      saveSearchHistory: true,
      searchHistoryLimit: 20,
      autoStart: false,
      showWelcome: true,
      restoreSession: true,
      minimizeToTray: true
    })
    
    Object.assign(notificationSettings, {
      systemNotifications: true,
      successNotifications: true,
      errorNotifications: true,
      warningNotifications: true,
      infoNotifications: false,
      desktopNotifications: true,
      soundNotifications: false,
      taskbarFlash: true,
      notificationDuration: 5000,
      showDetails: true,
      showActions: true,
      showAppIcon: true,
      notificationPosition: 'top-right'
    })
    
    Object.assign(advancedSettings, {
      hardwareAcceleration: true,
      cacheSize: 500,
      maxThreads: 4,
      memoryLimit: 2048,
      developerMode: false,
      debugMode: false,
      logLevel: 'info',
      performanceMonitoring: false
    })
    
    ElMessage.success('所有设置已重置')
  } catch {
    // 用户取消操作
  }
}

// 生命周期
onMounted(() => {
  // 从本地存储加载设置
  const savedSettings = localStorage.getItem('leafview-settings')
  if (savedSettings) {
    try {
      const settings = JSON.parse(savedSettings)
      Object.assign(appearanceSettings, settings.appearance || {})
      Object.assign(interfaceSettings, settings.interface || {})
      Object.assign(behaviorSettings, settings.behavior || {})
      Object.assign(notificationSettings, settings.notifications || {})
      Object.assign(advancedSettings, settings.advanced || {})
      
      if (settings.shortcuts) {
        shortcuts.value = settings.shortcuts
      }
    } catch (error) {
      console.error('加载设置失败:', error)
    }
  }
})
</script>

<style scoped>
.personalization {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color);
}

.personalization-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

.toolbar-left h2 {
  margin: 0;
  color: var(--el-text-color-primary);
  font-size: 18px;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-right {
  display: flex;
  gap: 12px;
}

.personalization-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.settings-nav {
  width: 240px;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color-page);
}

.settings-menu {
  border: none;
  background: transparent;
}

.settings-menu .el-menu-item {
  height: 48px;
  line-height: 48px;
  margin: 4px 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.settings-menu .el-menu-item.is-active {
  background: var(--el-color-primary-light-9);
  color: var(--el-color-primary);
}

.settings-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.settings-section h3 {
  margin: 0 0 24px 0;
  color: var(--el-text-color-primary);
  font-size: 20px;
  font-weight: 600;
}

.setting-group {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--el-bg-color);
  border-radius: 12px;
  border: 1px solid var(--el-border-color-light);
}

.setting-group h4 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
  font-size: 16px;
  font-weight: 600;
}

/* 主题模式卡片 */
.theme-modes {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 16px;
}

.theme-mode-card {
  border: 2px solid var(--el-border-color-light);
  border-radius: 12px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--el-bg-color);
}

.theme-mode-card:hover {
  border-color: var(--el-color-primary-light-5);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.theme-mode-card.active {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

.theme-preview {
  width: 100%;
  height: 80px;
  border-radius: 8px;
  margin-bottom: 12px;
  overflow: hidden;
  position: relative;
}

.theme-preview.light {
  background: #f5f7fa;
}

.theme-preview.dark {
  background: #1f2d3d;
}

.theme-preview.auto {
  background: linear-gradient(135deg, #f5f7fa 50%, #1f2d3d 50%);
}

.preview-header {
  height: 20px;
  background: var(--el-color-primary);
  border-radius: 4px 4px 0 0;
}

.preview-content {
  height: 60px;
  display: flex;
  padding: 8px;
}

.preview-sidebar {
  width: 30%;
  background: var(--el-color-primary-light-8);
  border-radius: 4px;
  margin-right: 8px;
}

.preview-main {
  flex: 1;
  background: var(--el-color-primary-light-9);
  border-radius: 4px;
}

.theme-info {
  text-align: center;
}

.theme-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.theme-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

/* 颜色预设 */
.color-picker-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.color-presets {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.color-preset {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  cursor: pointer;
  border: 2px solid transparent;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.color-preset:hover {
  transform: scale(1.1);
}

.color-preset.active {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.color-preset .el-icon {
  color: white;
  font-size: 16px;
}

.custom-color {
  display: flex;
  align-items: center;
  gap: 12px;
}

.color-value {
  font-family: 'Courier New', monospace;
  background: var(--el-fill-color-light);
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

/* 滑块值显示 */
.slider-value {
  margin-left: 12px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  min-width: 60px;
  display: inline-block;
}

/* 快捷键设置 */
.shortcuts-list {
  margin-bottom: 24px;
}

.shortcut-item {
  display: flex;
  align-items: center;
  padding: 16px;
  margin-bottom: 8px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.shortcut-item:hover {
  border-color: var(--el-color-primary-light-5);
}

.shortcut-info {
  flex: 1;
}

.shortcut-name {
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 4px;
}

.shortcut-description {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.shortcut-keys {
  width: 200px;
  margin: 0 16px;
}

.shortcut-actions {
  width: 80px;
}

.shortcuts-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 重置选项 */
.reset-options {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .theme-modes {
    grid-template-columns: 1fr;
  }
  
  .shortcut-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .shortcut-keys {
    width: 100%;
    margin: 0;
  }
  
  .shortcut-actions {
    width: 100%;
    text-align: right;
  }
}

@media (max-width: 768px) {
  .personalization-content {
    flex-direction: column;
  }
  
  .settings-nav {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .settings-menu {
    display: flex;
    overflow-x: auto;
  }
  
  .settings-menu .el-menu-item {
    flex-shrink: 0;
    white-space: nowrap;
  }
  
  .settings-content {
    padding: 16px;
  }
  
  .setting-group {
    padding: 16px;
  }
  
  .toolbar-right {
    flex-direction: column;
    gap: 8px;
  }
}

/* 动画效果 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 加载状态 */
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: var(--el-text-color-secondary);
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-secondary);
}

.empty-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
  color: var(--el-text-color-placeholder);
}

/* 错误状态 */
.error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--el-color-error);
}

.error-state .el-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
</style>