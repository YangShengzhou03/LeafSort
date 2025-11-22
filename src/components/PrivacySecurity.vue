<template>
  <div class="privacy-security">
    <!-- 顶部工具栏 -->
    <div class="security-toolbar">
      <div class="toolbar-left">
        <h2><el-icon><Lock /></el-icon> 隐私与安全</h2>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="runSecurityScan">
          <el-icon><Search /></el-icon> 安全扫描
        </el-button>
        <el-button @click="exportSecurityReport">
          <el-icon><Document /></el-icon> 导出报告
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="security-content">
      <!-- 左侧安全概览面板 -->
      <div class="security-overview-panel">
        <div class="overview-section">
          <h4>安全概览</h4>
          <div class="security-score">
            <div class="score-circle">
              <div class="score-value">{{ securityScore }}</div>
              <div class="score-label">安全评分</div>
            </div>
            <div class="score-details">
              <div class="detail-item">
                <span>上次扫描:</span>
                <span>{{ lastScanTime || '从未扫描' }}</span>
              </div>
              <div class="detail-item">
                <span>发现威胁:</span>
                <span class="threat-count">{{ threatCount }} 个</span>
              </div>
              <div class="detail-item">
                <span>保护状态:</span>
                <span :class="protectionStatusClass">{{ protectionStatus }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="overview-section">
          <h4>快速操作</h4>
          <div class="quick-actions">
            <el-button @click="clearCache" type="warning" size="small">
              <el-icon><Delete /></el-icon> 清理缓存
            </el-button>
            <el-button @click="encryptFiles" type="success" size="small">
              <el-icon><Lock /></el-icon> 加密文件
            </el-button>
            <el-button @click="backupData" type="info" size="small">
              <el-icon><CopyDocument /></el-icon> 备份数据
            </el-button>
            <el-button @click="viewLogs" type="primary" size="small">
              <el-icon><Document /></el-icon> 查看日志
            </el-button>
          </div>
        </div>

        <div class="overview-section">
          <h4>系统状态</h4>
          <div class="system-status">
            <div class="status-item" v-for="item in systemStatus" :key="item.name">
              <div class="status-info">
                <span class="status-name">{{ item.name }}</span>
                <span class="status-value">{{ item.value }}</span>
              </div>
              <el-progress 
                :percentage="item.percentage" 
                :status="item.status"
                :show-text="false"
                style="width: 100%; margin-top: 4px;"
              ></el-progress>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央安全设置面板 -->
      <div class="security-settings-panel">
        <el-tabs v-model="activeTab" type="card">
          <!-- 隐私保护标签页 -->
          <el-tab-pane label="隐私保护" name="privacy">
            <div class="tab-content">
              <div class="settings-group">
                <h5>数据收集</h5>
                <el-form :model="privacySettings" label-width="140px">
                  <el-form-item label="匿名使用统计">
                    <el-switch v-model="privacySettings.anonymousStats"></el-switch>
                    <span class="setting-description">帮助我们改进产品，不会收集个人身份信息</span>
                  </el-form-item>
                  
                  <el-form-item label="崩溃报告">
                    <el-switch v-model="privacySettings.crashReports"></el-switch>
                    <span class="setting-description">自动发送崩溃报告以帮助解决问题</span>
                  </el-form-item>
                  
                  <el-form-item label="使用情况分析">
                    <el-switch v-model="privacySettings.usageAnalytics"></el-switch>
                    <span class="setting-description">收集功能使用情况以优化用户体验</span>
                  </el-form-item>
                </el-form>
              </div>

              <div class="settings-group">
                <h5>数据保留</h5>
                <el-form :model="privacySettings" label-width="140px">
                  <el-form-item label="搜索历史">
                    <el-select v-model="privacySettings.searchHistoryRetention">
                      <el-option label="不保留" value="none"></el-option>
                      <el-option label="保留7天" value="7days"></el-option>
                      <el-option label="保留30天" value="30days"></el-option>
                      <el-option label="永久保留" value="forever"></el-option>
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="操作日志">
                    <el-select v-model="privacySettings.operationLogRetention">
                      <el-option label="保留30天" value="30days"></el-option>
                      <el-option label="保留90天" value="90days"></el-option>
                      <el-option label="保留1年" value="1year"></el-option>
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="缓存文件">
                    <el-select v-model="privacySettings.cacheRetention">
                      <el-option label="自动清理" value="auto"></el-option>
                      <el-option label="保留7天" value="7days"></el-option>
                      <el-option label="保留30天" value="30days"></el-option>
                    </el-select>
                  </el-form-item>
                </el-form>
              </div>

              <div class="settings-group">
                <h5>隐私控制</h5>
                <el-form :model="privacySettings" label-width="140px">
                  <el-form-item label="地理位置">
                    <el-switch v-model="privacySettings.locationServices"></el-switch>
                    <span class="setting-description">允许应用访问地理位置信息</span>
                  </el-form-item>
                  
                  <el-form-item label="相机访问">
                    <el-switch v-model="privacySettings.cameraAccess"></el-switch>
                    <span class="setting-description">允许应用访问相机进行截图功能</span>
                  </el-form-item>
                  
                  <el-form-item label="麦克风访问">
                    <el-switch v-model="privacySettings.microphoneAccess"></el-switch>
                    <span class="setting-description">允许应用访问麦克风（语音搜索）</span>
                  </el-form-item>
                  
                  <el-form-item label="文件系统访问">
                    <el-switch v-model="privacySettings.fileSystemAccess"></el-switch>
                    <span class="setting-description">允许应用访问本地文件系统</span>
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </el-tab-pane>

          <!-- 安全防护标签页 -->
          <el-tab-pane label="安全防护" name="security">
            <div class="tab-content">
              <div class="settings-group">
                <h5>访问控制</h5>
                <el-form :model="securitySettings" label-width="140px">
                  <el-form-item label="应用锁">
                    <el-switch v-model="securitySettings.appLock"></el-switch>
                    <span class="setting-description">启动应用时需要密码或生物识别</span>
                  </el-form-item>
                  
                  <el-form-item label="自动锁定">
                    <el-select v-model="securitySettings.autoLockTimeout">
                      <el-option label="立即" value="immediate"></el-option>
                      <el-option label="1分钟后" value="1min"></el-option>
                      <el-option label="5分钟后" value="5min"></el-option>
                      <el-option label="15分钟后" value="15min"></el-option>
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="双重验证">
                    <el-switch v-model="securitySettings.twoFactorAuth"></el-switch>
                    <span class="setting-description">登录时需要进行双重验证</span>
                  </el-form-item>
                </el-form>
              </div>

              <div class="settings-group">
                <h5>数据加密</h5>
                <el-form :model="securitySettings" label-width="140px">
                  <el-form-item label="本地加密">
                    <el-switch v-model="securitySettings.localEncryption"></el-switch>
                    <span class="setting-description">对本地存储的数据进行加密</span>
                  </el-form-item>
                  
                  <el-form-item label="传输加密">
                    <el-switch v-model="securitySettings.transportEncryption"></el-switch>
                    <span class="setting-description">对网络传输的数据进行加密</span>
                  </el-form-item>
                  
                  <el-form-item label="加密算法">
                    <el-select v-model="securitySettings.encryptionAlgorithm">
                      <el-option label="AES-256" value="aes256"></el-option>
                      <el-option label="RSA-2048" value="rsa2048"></el-option>
                      <el-option label="ChaCha20" value="chacha20"></el-option>
                    </el-select>
                  </el-form-item>
                  
                  <el-form-item label="密钥管理">
                    <el-button @click="manageKeys" size="small">管理密钥</el-button>
                    <el-button @click="backupKeys" size="small">备份密钥</el-button>
                  </el-form-item>
                </el-form>
              </div>

              <div class="settings-group">
                <h5>威胁防护</h5>
                <el-form :model="securitySettings" label-width="140px">
                  <el-form-item label="实时防护">
                    <el-switch v-model="securitySettings.realTimeProtection"></el-switch>
                    <span class="setting-description">实时监控和阻止潜在威胁</span>
                  </el-form-item>
                  
                  <el-form-item label="恶意软件扫描">
                    <el-switch v-model="securitySettings.malwareScanning"></el-switch>
                    <span class="setting-description">定期扫描文件中的恶意软件</span>
                  </el-form-item>
                  
                  <el-form-item label="网络防护">
                    <el-switch v-model="securitySettings.networkProtection"></el-switch>
                    <span class="setting-description">监控和阻止可疑网络活动</span>
                  </el-form-item>
                  
                  <el-form-item label="防火墙">
                    <el-switch v-model="securitySettings.firewall"></el-switch>
                    <span class="setting-description">启用应用级防火墙保护</span>
                  </el-form-item>
                </el-form>
              </div>
            </div>
          </el-tab-pane>

          <!-- 权限管理标签页 -->
          <el-tab-pane label="权限管理" name="permissions">
            <div class="tab-content">
              <div class="permissions-list">
                <div v-for="permission in permissions" :key="permission.id" class="permission-item">
                  <div class="permission-icon">
                    <el-icon>
                      <component :is="permission.icon" />
                    </el-icon>
                  </div>
                  <div class="permission-info">
                    <div class="permission-name">{{ permission.name }}</div>
                    <div class="permission-description">{{ permission.description }}</div>
                    <div class="permission-status">
                      <span>状态: </span>
                      <el-tag :type="permission.status === 'granted' ? 'success' : 'warning'" size="small">
                        {{ permission.status === 'granted' ? '已授权' : '未授权' }}
                      </el-tag>
                    </div>
                  </div>
                  <div class="permission-actions">
                    <el-button 
                      v-if="permission.status === 'granted'" 
                      @click="revokePermission(permission.id)"
                      type="danger" 
                      size="small"
                    >
                      撤销
                    </el-button>
                    <el-button 
                      v-else 
                      @click="grantPermission(permission.id)"
                      type="success" 
                      size="small"
                    >
                      授权
                    </el-button>
                  </div>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 安全日志标签页 -->
          <el-tab-pane label="安全日志" name="logs">
            <div class="tab-content">
              <div class="logs-header">
                <el-button @click="clearLogs" type="warning" size="small">清空日志</el-button>
                <el-button @click="refreshLogs" type="primary" size="small">刷新</el-button>
                <el-select v-model="logLevel" placeholder="日志级别" size="small" style="width: 120px;">
                  <el-option label="全部" value="all"></el-option>
                  <el-option label="信息" value="info"></el-option>
                  <el-option label="警告" value="warning"></el-option>
                  <el-option label="错误" value="error"></el-option>
                </el-select>
              </div>
              
              <div class="logs-content">
                <div v-for="log in filteredLogs" :key="log.id" class="log-entry" :class="log.level">
                  <div class="log-time">{{ log.timestamp }}</div>
                  <div class="log-level">
                    <el-tag :type="getLogLevelType(log.level)" size="small">
                      {{ getLogLevelText(log.level) }}
                    </el-tag>
                  </div>
                  <div class="log-message">{{ log.message }}</div>
                  <div class="log-source">{{ log.source }}</div>
                </div>
                
                <div v-if="filteredLogs.length === 0" class="empty-logs">
                  <el-icon><Document /></el-icon>
                  <p>暂无日志记录</p>
                </div>
              </div>
            </div>
          </el-tab-pane>
        </el-tabs>

        <div class="settings-actions">
          <el-button type="primary" @click="saveSettings">保存设置</el-button>
          <el-button @click="resetSettings">重置设置</el-button>
          <el-button @click="exportSettings">导出配置</el-button>
        </div>
      </div>

      <!-- 右侧威胁检测面板 -->
      <div class="threat-detection-panel">
        <div class="threat-section">
          <h4>威胁检测</h4>
          <div class="threat-list">
            <div v-for="threat in detectedThreats" :key="threat.id" class="threat-item">
              <div class="threat-icon" :class="threat.severity">
                <el-icon>
                  <WarningFilled v-if="threat.severity === 'high'" />
                  <Warning v-else-if="threat.severity === 'medium'" />
                  <InfoFilled v-else />
                </el-icon>
              </div>
              <div class="threat-info">
                <div class="threat-name">{{ threat.name }}</div>
                <div class="threat-description">{{ threat.description }}</div>
                <div class="threat-time">检测时间: {{ threat.detectedAt }}</div>
              </div>
              <div class="threat-actions">
                <el-button @click="resolveThreat(threat.id)" type="success" size="small">解决</el-button>
                <el-button @click="ignoreThreat(threat.id)" type="warning" size="small">忽略</el-button>
              </div>
            </div>
          </div>
          
          <div v-if="detectedThreats.length === 0" class="no-threats">
            <el-icon><SuccessFilled /></el-icon>
            <p>未检测到威胁</p>
            <span class="threat-hint">系统安全状态良好</span>
          </div>
        </div>

        <div class="threat-section">
          <h4>安全建议</h4>
          <div class="recommendations">
            <div v-for="recommendation in securityRecommendations" :key="recommendation.id" class="recommendation-item">
              <div class="recommendation-icon">
                <el-icon><Lightning /></el-icon>
              </div>
              <div class="recommendation-content">
                <div class="recommendation-title">{{ recommendation.title }}</div>
                <div class="recommendation-description">{{ recommendation.description }}</div>
                <el-button @click="applyRecommendation(recommendation.id)" type="text" size="small">立即应用</el-button>
              </div>
            </div>
          </div>
        </div>

        <div class="threat-section">
          <h4>安全资源</h4>
          <div class="security-resources">
            <el-button @click="openSecurityGuide" type="text" class="resource-link">
              <el-icon><Reading /></el-icon> 安全使用指南
            </el-button>
            <el-button @click="openPrivacyPolicy" type="text" class="resource-link">
              <el-icon><Document /></el-icon> 隐私政策
            </el-button>
            <el-button @click="openHelpCenter" type="text" class="resource-link">
              <el-icon><QuestionFilled /></el-icon> 帮助中心
            </el-button>
            <el-button @click="contactSupport" type="text" class="resource-link">
              <el-icon><ChatDotRound /></el-icon> 联系支持
            </el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 响应式数据
const activeTab = ref('privacy')
const securityScore = ref(85)
const lastScanTime = ref('2024-01-15 14:30:25')
const threatCount = ref(2)
const protectionStatus = ref('受保护')
const protectionStatusClass = ref('status-protected')

const systemStatus = ref([
  { name: 'CPU使用率', value: '45%', percentage: 45, status: 'success' },
  { name: '内存使用', value: '68%', percentage: 68, status: 'warning' },
  { name: '磁盘空间', value: '82%', percentage: 82, status: 'exception' },
  { name: '网络流量', value: '12 MB/s', percentage: 60, status: 'success' }
])

const privacySettings = reactive({
  anonymousStats: true,
  crashReports: true,
  usageAnalytics: false,
  searchHistoryRetention: '7days',
  operationLogRetention: '30days',
  cacheRetention: 'auto',
  locationServices: false,
  cameraAccess: true,
  microphoneAccess: false,
  fileSystemAccess: true
})

const securitySettings = reactive({
  appLock: false,
  autoLockTimeout: '5min',
  twoFactorAuth: false,
  localEncryption: true,
  transportEncryption: true,
  encryptionAlgorithm: 'aes256',
  realTimeProtection: true,
  malwareScanning: true,
  networkProtection: false,
  firewall: true
})

const permissions = ref([
  { id: 'camera', name: '相机访问', description: '允许应用使用相机进行截图', icon: 'Camera', status: 'granted' },
  { id: 'location', name: '地理位置', description: '允许应用访问地理位置信息', icon: 'Location', status: 'denied' },
  { id: 'files', name: '文件系统', description: '允许应用读写本地文件', icon: 'Folder', status: 'granted' },
  { id: 'network', name: '网络访问', description: '允许应用进行网络通信', icon: 'Connection', status: 'granted' },
  { id: 'notifications', name: '通知权限', description: '允许应用发送系统通知', icon: 'Bell', status: 'denied' }
])

const logLevel = ref('all')
const securityLogs = ref([
  { id: '1', timestamp: '14:30:25', level: 'info', message: '安全扫描完成', source: 'SecurityScanner' },
  { id: '2', timestamp: '14:25:10', level: 'warning', message: '检测到可疑文件', source: 'ThreatDetection' },
  { id: '3', timestamp: '14:20:05', level: 'error', message: '加密密钥验证失败', source: 'EncryptionService' },
  { id: '4', timestamp: '14:15:30', level: 'info', message: '隐私设置已更新', source: 'SettingsManager' }
])

const detectedThreats = ref([
  { id: '1', name: '未加密的敏感文件', description: '发现3个未加密的敏感文件', severity: 'medium', detectedAt: '14:25:10' },
  { id: '2', name: '弱密码检测', description: '检测到弱密码设置', severity: 'low', detectedAt: '14:20:05' }
])

const securityRecommendations = ref([
  { id: '1', title: '启用双重验证', description: '建议启用双重验证以增强账户安全' },
  { id: '2', title: '定期备份数据', description: '建议每周备份重要数据到安全位置' },
  { id: '3', title: '更新加密密钥', description: '加密密钥已使用超过90天，建议更新' }
])

// 计算属性
const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return securityLogs.value
  return securityLogs.value.filter(log => log.level === logLevel.value)
})

// 方法定义
const runSecurityScan = async () => {
  ElMessage.info('开始安全扫描...')
  
  // 模拟扫描过程
  setTimeout(() => {
    securityScore.value = 92
    threatCount.value = 1
    lastScanTime.value = new Date().toLocaleString()
    protectionStatus.value = '优秀'
    protectionStatusClass.value = 'status-excellent'
    
    ElMessage.success('安全扫描完成')
  }, 3000)
}

const exportSecurityReport = () => {
  ElMessage.info('导出安全报告功能开发中...')
}

const clearCache = async () => {
  try {
    await ElMessageBox.confirm('确定要清理缓存吗？', '确认清理', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    ElMessage.success('缓存清理完成')
  } catch {
    // 用户取消操作
  }
}

const encryptFiles = () => {
  ElMessage.info('文件加密功能开发中...')
}

const backupData = () => {
  ElMessage.info('数据备份功能开发中...')
}

const viewLogs = () => {
  activeTab.value = 'logs'
}

const manageKeys = () => {
  ElMessage.info('密钥管理功能开发中...')
}

const backupKeys = () => {
  ElMessage.info('密钥备份功能开发中...')
}

const grantPermission = (permissionId: string) => {
  const permission = permissions.value.find(p => p.id === permissionId)
  if (permission) {
    permission.status = 'granted'
    ElMessage.success(`已授权: ${permission.name}`)
  }
}

const revokePermission = (permissionId: string) => {
  const permission = permissions.value.find(p => p.id === permissionId)
  if (permission) {
    permission.status = 'denied'
    ElMessage.warning(`已撤销: ${permission.name}`)
  }
}

const clearLogs = async () => {
  try {
    await ElMessageBox.confirm('确定要清空所有日志吗？', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    securityLogs.value = []
    ElMessage.success('日志已清空')
  } catch {
    // 用户取消操作
  }
}

const refreshLogs = () => {
  ElMessage.info('刷新日志功能开发中...')
}

const getLogLevelType = (level: string) => {
  switch (level) {
    case 'error': return 'danger'
    case 'warning': return 'warning'
    default: return 'info'
  }
}

const getLogLevelText = (level: string) => {
  switch (level) {
    case 'error': return '错误'
    case 'warning': return '警告'
    default: return '信息'
  }
}

const resolveThreat = (threatId: string) => {
  detectedThreats.value = detectedThreats.value.filter(t => t.id !== threatId)
  threatCount.value = detectedThreats.value.length
  ElMessage.success('威胁已解决')
}

const ignoreThreat = (threatId: string) => {
  detectedThreats.value = detectedThreats.value.filter(t => t.id !== threatId)
  threatCount.value = detectedThreats.value.length
  ElMessage.warning('威胁已忽略')
}

const applyRecommendation = (recommendationId: string) => {
  const recommendation = securityRecommendations.value.find(r => r.id === recommendationId)
  if (recommendation) {
    securityRecommendations.value = securityRecommendations.value.filter(r => r.id !== recommendationId)
    ElMessage.success(`已应用建议: ${recommendation.title}`)
  }
}

const openSecurityGuide = () => {
  window.open('https://example.com/security-guide', '_blank')
}

const openPrivacyPolicy = () => {
  window.open('https://example.com/privacy-policy', '_blank')
}

const openHelpCenter = () => {
  window.open('https://example.com/help', '_blank')
}

const contactSupport = () => {
  ElMessage.info('联系支持功能开发中...')
}

const saveSettings = () => {
  localStorage.setItem('privacySettings', JSON.stringify(privacySettings))
  localStorage.setItem('securitySettings', JSON.stringify(securitySettings))
  ElMessage.success('设置已保存')
}

const resetSettings = async () => {
  try {
    await ElMessageBox.confirm('确定要重置所有设置吗？', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    Object.assign(privacySettings, {
      anonymousStats: true,
      crashReports: true,
      usageAnalytics: false,
      searchHistoryRetention: '7days',
      operationLogRetention: '30days',
      cacheRetention: 'auto',
      locationServices: false,
      cameraAccess: true,
      microphoneAccess: false,
      fileSystemAccess: true
    })
    
    Object.assign(securitySettings, {
      appLock: false,
      autoLockTimeout: '5min',
      twoFactorAuth: false,
      localEncryption: true,
      transportEncryption: true,
      encryptionAlgorithm: 'aes256',
      realTimeProtection: true,
      malwareScanning: true,
      networkProtection: false,
      firewall: true
    })
    
    ElMessage.success('设置已重置')
  } catch {
    // 用户取消操作
  }
}

const exportSettings = () => {
  ElMessage.info('导出配置功能开发中...')
}

// 生命周期钩子
onMounted(() => {
  // 加载保存的设置
  const savedPrivacySettings = localStorage.getItem('privacySettings')
  const savedSecuritySettings = localStorage.getItem('securitySettings')
  
  if (savedPrivacySettings) {
    Object.assign(privacySettings, JSON.parse(savedPrivacySettings))
  }
  
  if (savedSecuritySettings) {
    Object.assign(securitySettings, JSON.parse(savedSecuritySettings))
  }
})
</script>

<style scoped lang="scss">
.privacy-security {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  
  .security-toolbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 24px;
    background: #fff;
    border-bottom: 1px solid #e4e7ed;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    
    .toolbar-left h2 {
      margin: 0;
      font-size: 20px;
      font-weight: 600;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    
    .toolbar-right {
      display: flex;
      gap: 12px;
    }
  }
  
  .security-content {
    flex: 1;
    display: grid;
    grid-template-columns: 300px 1fr 320px;
    gap: 16px;
    padding: 16px;
    overflow: hidden;
    
    @media (max-width: 1400px) {
      grid-template-columns: 280px 1fr 300px;
    }
    
    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr auto;
    }
  }
  
  // 左侧安全概览面板
  .security-overview-panel {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    
    .overview-section {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
    
    .security-score {
      display: flex;
      align-items: center;
      gap: 20px;
      
      .score-circle {
        text-align: center;
        
        .score-value {
          font-size: 32px;
          font-weight: 700;
          color: #67c23a;
          line-height: 1;
        }
        
        .score-label {
          font-size: 12px;
          color: #909399;
          margin-top: 4px;
        }
      }
      
      .score-details {
        flex: 1;
        
        .detail-item {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;
          font-size: 14px;
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .threat-count {
            color: #e6a23c;
            font-weight: 600;
          }
        }
      }
    }
    
    .quick-actions {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      
      .el-button {
        width: 100%;
      }
    }
    
    .system-status {
      .status-item {
        margin-bottom: 16px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .status-info {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 4px;
          
          .status-name {
            font-size: 14px;
            color: #606266;
          }
          
          .status-value {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
          }
        }
      }
    }
  }
  
  // 中央安全设置面板
  .security-settings-panel {
    background: #fff;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    display: flex;
    flex-direction: column;
    
    :deep(.el-tabs) {
      flex: 1;
      display: flex;
      flex-direction: column;
      
      .el-tabs__header {
        margin: 0;
        padding: 0 20px;
        
        .el-tabs__nav-wrap::after {
          height: 1px;
          background-color: #e4e7ed;
        }
      }
      
      .el-tabs__content {
        flex: 1;
        padding: 0;
        
        .el-tab-pane {
          height: 100%;
          padding: 20px;
          overflow-y: auto;
        }
      }
    }
    
    .tab-content {
      height: 100%;
      overflow-y: auto;
      
      .settings-group {
        margin-bottom: 32px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        h5 {
          margin: 0 0 16px 0;
          font-size: 15px;
          font-weight: 600;
          color: #303133;
          padding-bottom: 8px;
          border-bottom: 1px solid #f0f2f5;
        }
        
        .setting-description {
          font-size: 12px;
          color: #909399;
          margin-left: 12px;
        }
      }
      
      .permissions-list {
        .permission-item {
          display: flex;
          align-items: center;
          padding: 16px;
          border: 1px solid #f0f2f5;
          border-radius: 6px;
          margin-bottom: 12px;
          transition: all 0.3s ease;
          
          &:hover {
            border-color: #409eff;
            box-shadow: 0 2px 8px rgba(64, 158, 255, 0.1);
          }
          
          &:last-child {
            margin-bottom: 0;
          }
          
          .permission-icon {
            margin-right: 16px;
            
            .el-icon {
              font-size: 24px;
              color: #409eff;
            }
          }
          
          .permission-info {
            flex: 1;
            
            .permission-name {
              font-size: 14px;
              font-weight: 600;
              color: #303133;
              margin-bottom: 4px;
            }
            
            .permission-description {
              font-size: 12px;
              color: #909399;
              margin-bottom: 8px;
            }
            
            .permission-status {
              font-size: 12px;
              color: #606266;
            }
          }
          
          .permission-actions {
            margin-left: 16px;
          }
        }
      }
      
      .logs-header {
        display: flex;
        justify-content: flex-end;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
        padding-bottom: 16px;
        border-bottom: 1px solid #f0f2f5;
      }
      
      .logs-content {
        max-height: 400px;
        overflow-y: auto;
        
        .log-entry {
          display: grid;
          grid-template-columns: 80px 80px 1fr 120px;
          gap: 12px;
          align-items: center;
          padding: 12px;
          margin-bottom: 8px;
          border-radius: 4px;
          font-size: 12px;
          
          &.error {
            background: #fef0f0;
            border-left: 3px solid #f56c6c;
          }
          
          &.warning {
            background: #fdf6ec;
            border-left: 3px solid #e6a23c;
          }
          
          &.info {
            background: #f4f4f5;
            border-left: 3px solid #909399;
          }
          
          .log-time {
            color: #909399;
            font-family: monospace;
          }
          
          .log-message {
            color: #303133;
            word-break: break-all;
          }
          
          .log-source {
            color: #606266;
            font-style: italic;
          }
        }
        
        .empty-logs {
          text-align: center;
          padding: 40px 20px;
          color: #909399;
          
          .el-icon {
            font-size: 48px;
            margin-bottom: 16px;
          }
          
          p {
            margin: 0;
            font-size: 14px;
          }
        }
      }
    }
    
    .settings-actions {
      padding: 20px;
      border-top: 1px solid #f0f2f5;
      text-align: center;
      
      .el-button {
        margin: 0 8px;
      }
    }
  }
  
  // 右侧威胁检测面板
  .threat-detection-panel {
    background: #fff;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    overflow-y: auto;
    
    .threat-section {
      margin-bottom: 24px;
      
      &:last-child {
        margin-bottom: 0;
      }
      
      h4 {
        margin: 0 0 16px 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
        padding-bottom: 8px;
        border-bottom: 1px solid #f0f2f5;
      }
    }
    
    .threat-list {
      .threat-item {
        display: flex;
        align-items: center;
        padding: 12px;
        margin-bottom: 12px;
        border: 1px solid #f0f2f5;
        border-radius: 6px;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: #e6a23c;
        }
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .threat-icon {
          margin-right: 12px;
          
          .el-icon {
            font-size: 20px;
            
            &.high {
              color: #f56c6c;
            }
            
            &.medium {
              color: #e6a23c;
            }
            
            &.low {
              color: #67c23a;
            }
          }
        }
        
        .threat-info {
          flex: 1;
          
          .threat-name {
            font-size: 14px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 4px;
          }
          
          .threat-description {
            font-size: 12px;
            color: #909399;
            margin-bottom: 4px;
          }
          
          .threat-time {
            font-size: 11px;
            color: #c0c4cc;
          }
        }
        
        .threat-actions {
          margin-left: 12px;
          
          .el-button {
            margin-left: 4px;
          }
        }
      }
    }
    
    .no-threats {
      text-align: center;
      padding: 20px;
      color: #67c23a;
      
      .el-icon {
        font-size: 48px;
        margin-bottom: 12px;
      }
      
      p {
        margin: 0 0 8px 0;
        font-size: 14px;
        font-weight: 600;
      }
      
      .threat-hint {
        font-size: 12px;
        color: #909399;
      }
    }
    
    .recommendations {
      .recommendation-item {
        display: flex;
        align-items: flex-start;
        padding: 12px;
        margin-bottom: 12px;
        background: #f0f9ff;
        border: 1px solid #91d5ff;
        border-radius: 6px;
        
        &:last-child {
          margin-bottom: 0;
        }
        
        .recommendation-icon {
          margin-right: 12px;
          
          .el-icon {
            font-size: 20px;
            color: #1890ff;
          }
        }
        
        .recommendation-content {
          flex: 1;
          
          .recommendation-title {
            font-size: 14px;
            font-weight: 600;
            color: #1890ff;
            margin-bottom: 4px;
          }
          
          .recommendation-description {
            font-size: 12px;
            color: #606266;
            margin-bottom: 8px;
          }
        }
      }
    }
    
    .security-resources {
      display: flex;
      flex-direction: column;
      gap: 8px;
      
      .resource-link {
        justify-content: flex-start;
        padding: 8px 12px;
        border: 1px solid #f0f2f5;
        border-radius: 4px;
        transition: all 0.3s ease;
        
        &:hover {
          border-color: #409eff;
          background: #f0f9ff;
        }
        
        .el-icon {
          margin-right: 8px;
        }
      }
    }
  }
  
  // 状态类
  .status-protected {
    color: #67c23a;
    font-weight: 600;
  }
  
  .status-excellent {
    color: #1890ff;
    font-weight: 600;
  }
  
  // 响应式设计
  @media (max-width: 1200px) {
    .security-content {
      .security-overview-panel,
      .threat-detection-panel {
        order: 1;
      }
      
      .security-settings-panel {
        order: 2;
        min-height: 400px;
      }
    }
  }
  
  @media (max-width: 768px) {
    .security-toolbar {
      flex-direction: column;
      gap: 16px;
      padding: 12px 16px;
      
      .toolbar-left h2 {
        font-size: 18px;
      }
    }
    
    .security-content {
      padding: 12px;
      gap: 12px;
    }
    
    .security-overview-panel,
    .security-settings-panel,
    .threat-detection-panel {
      padding: 16px;
    }
    
    .security-score {
      flex-direction: column;
      text-align: center;
      gap: 16px;
    }
    
    .quick-actions {
      grid-template-columns: 1fr;
    }
    
    .logs-content .log-entry {
      grid-template-columns: 1fr;
      gap: 8px;
      text-align: center;
    }
    
    .threat-item {
      flex-direction: column;
      text-align: center;
      gap: 12px;
      
      .threat-actions {
        margin-left: 0;
      }
    }
  }
}

// 动画效果
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

// 加载动画
.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

// 脉冲动画
.pulse {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.5; }
  100% { opacity: 1; }
}
</style>