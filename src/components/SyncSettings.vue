<template>
  <div class="sync-settings">
    <!-- 顶部工具栏 -->
    <div class="sync-toolbar">
      <div class="toolbar-left">
        <h2><el-icon><Connection /></el-icon> 多设备同步</h2>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" @click="syncNow">
          <el-icon><Refresh /></el-icon> 立即同步
        </el-button>
        <el-button @click="showSyncHistory">
          <el-icon><Clock /></el-icon> 同步历史
        </el-button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="sync-content">
      <!-- 左侧同步状态面板 -->
      <div class="sync-status-panel">
        <div class="status-section">
          <h4>同步状态</h4>
          <div class="status-card">
            <div class="status-indicator" :class="syncStatus">
              <el-icon v-if="syncStatus === 'connected'"><SuccessFilled /></el-icon>
              <el-icon v-else-if="syncStatus === 'syncing'"><Loading /></el-icon>
              <el-icon v-else-if="syncStatus === 'error'"><WarningFilled /></el-icon>
              <el-icon v-else><InfoFilled /></el-icon>
              <span>{{ getStatusText() }}</span>
            </div>
            <div class="status-details">
              <div class="detail-item">
                <span>最后同步时间:</span>
                <span>{{ lastSyncTime || '从未同步' }}</span>
              </div>
              <div class="detail-item">
                <span>同步设备数:</span>
                <span>{{ deviceCount }} 台</span>
              </div>
              <div class="detail-item">
                <span>同步文件数:</span>
                <span>{{ syncedFilesCount }} 个</span>
              </div>
            </div>
          </div>
        </div>

        <div class="status-section">
          <h4>同步统计</h4>
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-value">{{ totalAssets }}</div>
              <div class="stat-label">总素材数</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ syncedAssets }}</div>
              <div class="stat-label">已同步素材</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ pendingAssets }}</div>
              <div class="stat-label">待同步素材</div>
            </div>
            <div class="stat-item">
              <div class="stat-value">{{ syncProgress }}%</div>
              <div class="stat-label">同步进度</div>
            </div>
          </div>
        </div>

        <div class="status-section">
          <h4>网络状态</h4>
          <div class="network-status">
            <div class="network-item">
              <span>网络类型:</span>
              <span>{{ networkType }}</span>
            </div>
            <div class="network-item">
              <span>连接速度:</span>
              <span>{{ connectionSpeed }}</span>
            </div>
            <div class="network-item">
              <span>数据使用:</span>
              <span>{{ dataUsage }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 中央同步设置面板 -->
      <div class="sync-settings-panel">
        <div class="settings-section">
          <h4>同步服务配置</h4>
          <el-form :model="syncConfig" label-width="120px">
            <el-form-item label="同步服务">
              <el-radio-group v-model="syncConfig.service">
                <el-radio label="local">本地网络</el-radio>
                <el-radio label="cloud">云服务</el-radio>
                <el-radio label="custom">自定义服务器</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item v-if="syncConfig.service === 'cloud'" label="云服务商">
              <el-select v-model="syncConfig.cloudProvider" placeholder="请选择云服务商">
                <el-option label="阿里云 OSS" value="aliyun"></el-option>
                <el-option label="腾讯云 COS" value="tencent"></el-option>
                <el-option label="七牛云" value="qiniu"></el-option>
                <el-option label="AWS S3" value="aws"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item v-if="syncConfig.service === 'custom'" label="服务器地址">
              <el-input v-model="syncConfig.serverUrl" placeholder="请输入服务器地址"></el-input>
            </el-form-item>

            <el-form-item label="同步频率">
              <el-select v-model="syncConfig.frequency" placeholder="请选择同步频率">
                <el-option label="实时同步" value="realtime"></el-option>
                <el-option label="每15分钟" value="15min"></el-option>
                <el-option label="每小时" value="hourly"></el-option>
                <el-option label="每天" value="daily"></el-option>
                <el-option label="手动同步" value="manual"></el-option>
              </el-select>
            </el-form-item>

            <el-form-item label="同步内容">
              <el-checkbox-group v-model="syncConfig.contentTypes">
                <el-checkbox label="images">图片文件</el-checkbox>
                <el-checkbox label="videos">视频文件</el-checkbox>
                <el-checkbox label="documents">文档文件</el-checkbox>
                <el-checkbox label="metadata">元数据</el-checkbox>
                <el-checkbox label="settings">设置信息</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="文件大小限制">
              <el-input-number v-model="syncConfig.maxFileSize" :min="1" :max="1000"></el-input-number>
              <span style="margin-left: 8px;">MB</span>
            </el-form-item>

            <el-form-item label="网络限制">
              <el-checkbox v-model="syncConfig.wifiOnly">仅WiFi同步</el-checkbox>
              <el-checkbox v-model="syncConfig.batteryOptimize">电池优化模式</el-checkbox>
            </el-form-item>
          </el-form>
        </div>

        <div class="settings-section">
          <h4>冲突解决策略</h4>
          <el-form :model="syncConfig" label-width="120px">
            <el-form-item label="文件冲突">
              <el-radio-group v-model="syncConfig.conflictResolution">
                <el-radio label="keepNewer">保留较新版本</el-radio>
                <el-radio label="keepLocal">保留本地版本</el-radio>
                <el-radio label="keepRemote">保留远程版本</el-radio>
                <el-radio label="manual">手动解决</el-radio>
              </el-radio-group>
            </el-form-item>

            <el-form-item label="备份策略">
              <el-checkbox v-model="syncConfig.backupBeforeSync">同步前备份</el-checkbox>
              <el-checkbox v-model="syncConfig.keepBackups">保留备份文件</el-checkbox>
            </el-form-item>

            <el-form-item label="备份保留时间">
              <el-input-number v-model="syncConfig.backupRetention" :min="1" :max="365"></el-input-number>
              <span style="margin-left: 8px;">天</span>
            </el-form-item>
          </el-form>
        </div>

        <div class="settings-actions">
          <el-button type="primary" @click="saveSyncConfig">保存设置</el-button>
          <el-button @click="testConnection">测试连接</el-button>
          <el-button @click="resetSyncConfig">重置设置</el-button>
        </div>
      </div>

      <!-- 右侧设备管理面板 -->
      <div class="devices-panel">
        <div class="devices-section">
          <h4>已连接设备</h4>
          <div class="devices-list">
            <div v-for="device in connectedDevices" :key="device.id" class="device-item">
              <div class="device-icon">
                <el-icon v-if="device.type === 'desktop'"><Monitor /></el-icon>
                <el-icon v-else-if="device.type === 'laptop'"><Laptop /></el-icon>
                <el-icon v-else><Mobile /></el-icon>
              </div>
              <div class="device-info">
                <div class="device-name">{{ device.name }}</div>
                <div class="device-details">
                  <span>{{ device.os }}</span>
                  <span>最后在线: {{ device.lastSeen }}</span>
                </div>
              </div>
              <div class="device-status" :class="device.status">
                <el-tooltip :content="getDeviceStatusText(device.status)" placement="top">
                  <el-icon>
                    <SuccessFilled v-if="device.status === 'online'" />
                    <Clock v-else-if="device.status === 'syncing'" />
                    <WarningFilled v-else />
                  </el-icon>
                </el-tooltip>
              </div>
            </div>
          </div>
          <div v-if="connectedDevices.length === 0" class="empty-devices">
            <el-icon><Connection /></el-icon>
            <p>暂无已连接设备</p>
          </div>
        </div>

        <div class="devices-section">
          <h4>设备管理</h4>
          <div class="device-actions">
            <el-button @click="addDevice" type="primary" size="small">
              <el-icon><Plus /></el-icon> 添加设备
            </el-button>
            <el-button @click="scanDevices" size="small">
              <el-icon><Search /></el-icon> 扫描设备
            </el-button>
          </div>
          <div class="device-stats">
            <div class="stat-row">
              <span>设备容量:</span>
              <span>{{ deviceStorage.used }}/{{ deviceStorage.total }}</span>
            </div>
            <div class="stat-row">
              <span>同步配额:</span>
              <span>{{ syncQuota.used }}/{{ syncQuota.total }}</span>
            </div>
            <div class="stat-row">
              <span>设备权限:</span>
              <span>{{ devicePermissions }}</span>
            </div>
          </div>
        </div>

        <div class="devices-section">
          <h4>安全设置</h4>
          <div class="security-settings">
            <el-switch v-model="securitySettings.encryption" active-text="数据加密"></el-switch>
            <el-switch v-model="securitySettings.twoFactor" active-text="双重验证"></el-switch>
            <el-switch v-model="securitySettings.autoLock" active-text="自动锁定"></el-switch>
          </div>
          <div class="security-actions">
            <el-button @click="changePassword" size="small">修改密码</el-button>
            <el-button @click="viewSecurityLog" size="small">安全日志</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 同步历史对话框 -->
    <el-dialog v-model="showHistoryDialog" title="同步历史" width="800px">
      <div class="sync-history">
        <el-timeline>
          <el-timeline-item
            v-for="record in syncHistory"
            :key="record.id"
            :timestamp="record.timestamp"
            :type="getTimelineType(record.status)"
            placement="top"
          >
            <el-card>
              <div class="history-item">
                <div class="history-status">
                  <el-tag :type="getStatusType(record.status)" size="small">
                    {{ getStatusText(record.status) }}
                  </el-tag>
                </div>
                <div class="history-details">
                  <p>{{ record.description }}</p>
                  <div class="history-meta">
                    <span>设备: {{ record.device }}</span>
                    <span>文件数: {{ record.fileCount }}</span>
                    <span>耗时: {{ record.duration }}</span>
                  </div>
                </div>
              </div>
            </el-card>
          </el-timeline-item>
        </el-timeline>
      </div>
    </el-dialog>

    <!-- 添加设备对话框 -->
    <el-dialog v-model="showAddDeviceDialog" title="添加设备" width="500px">
      <el-form :model="newDevice" label-width="80px">
        <el-form-item label="设备名称">
          <el-input v-model="newDevice.name" placeholder="请输入设备名称"></el-input>
        </el-form-item>
        <el-form-item label="设备类型">
          <el-select v-model="newDevice.type" placeholder="请选择设备类型">
            <el-option label="台式机" value="desktop"></el-option>
            <el-option label="笔记本" value="laptop"></el-option>
            <el-option label="手机" value="mobile"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="连接方式">
          <el-radio-group v-model="newDevice.connection">
            <el-radio label="qrcode">二维码扫描</el-radio>
            <el-radio label="manual">手动输入</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="newDevice.connection === 'manual'" label="设备代码">
          <el-input v-model="newDevice.code" placeholder="请输入设备配对代码"></el-input>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDeviceDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmAddDevice">确认添加</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'

// 同步状态类型定义
interface SyncConfig {
  service: string
  cloudProvider: string
  serverUrl: string
  frequency: string
  contentTypes: string[]
  maxFileSize: number
  wifiOnly: boolean
  batteryOptimize: boolean
  conflictResolution: string
  backupBeforeSync: boolean
  keepBackups: boolean
  backupRetention: number
}

interface Device {
  id: string
  name: string
  type: string
  os: string
  status: string
  lastSeen: string
}

interface SyncRecord {
  id: string
  timestamp: string
  status: string
  description: string
  device: string
  fileCount: number
  duration: string
}

// 响应式数据
const syncStatus = ref('disconnected') // disconnected, connecting, connected, syncing, error
const lastSyncTime = ref('')
const deviceCount = ref(0)
const syncedFilesCount = ref(0)
const totalAssets = ref(0)
const syncedAssets = ref(0)
const pendingAssets = ref(0)
const syncProgress = ref(0)
const networkType = ref('WiFi')
const connectionSpeed = ref('100 Mbps')
const dataUsage = ref('2.5 GB')

const syncConfig = reactive<SyncConfig>({
  service: 'local',
  cloudProvider: 'aliyun',
  serverUrl: '',
  frequency: 'hourly',
  contentTypes: ['images', 'videos', 'documents', 'metadata'],
  maxFileSize: 100,
  wifiOnly: true,
  batteryOptimize: false,
  conflictResolution: 'keepNewer',
  backupBeforeSync: true,
  keepBackups: true,
  backupRetention: 30
})

const connectedDevices = ref<Device[]>([
  {
    id: '1',
    name: '我的台式机',
    type: 'desktop',
    os: 'Windows 11',
    status: 'online',
    lastSeen: '2分钟前'
  },
  {
    id: '2',
    name: '工作笔记本',
    type: 'laptop',
    os: 'macOS',
    status: 'syncing',
    lastSeen: '5分钟前'
  }
])

const deviceStorage = reactive({
  used: '128 GB',
  total: '512 GB'
})

const syncQuota = reactive({
  used: '45 GB',
  total: '100 GB'
})

const devicePermissions = ref('读写权限')

const securitySettings = reactive({
  encryption: true,
  twoFactor: false,
  autoLock: true
})

const showHistoryDialog = ref(false)
const syncHistory = ref<SyncRecord[]>([
  {
    id: '1',
    timestamp: '2024-01-15 14:30:25',
    status: 'success',
    description: '自动同步完成',
    device: '我的台式机',
    fileCount: 45,
    duration: '2分15秒'
  },
  {
    id: '2',
    timestamp: '2024-01-15 13:15:10',
    status: 'error',
    description: '网络连接中断',
    device: '工作笔记本',
    fileCount: 12,
    duration: '45秒'
  }
])

const showAddDeviceDialog = ref(false)
const newDevice = reactive({
  name: '',
  type: 'desktop',
  connection: 'qrcode',
  code: ''
})

// 方法定义
const getStatusText = (status?: string) => {
  const currentStatus = status || syncStatus.value
  switch (currentStatus) {
    case 'connected':
      return '已连接'
    case 'syncing':
      return '同步中'
    case 'error':
      return '连接错误'
    case 'connecting':
      return '连接中'
    default:
      return '未连接'
  }
}

const getDeviceStatusText = (status: string) => {
  switch (status) {
    case 'online':
      return '在线'
    case 'syncing':
      return '同步中'
    case 'offline':
      return '离线'
    default:
      return '未知'
  }
}

const getTimelineType = (status: string) => {
  switch (status) {
    case 'success':
      return 'primary'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

const getStatusType = (status: string) => {
  switch (status) {
    case 'success':
      return 'success'
    case 'error':
      return 'danger'
    default:
      return 'info'
  }
}

const syncNow = async () => {
  syncStatus.value = 'syncing'
  ElMessage.info('开始同步...')
  
  // 模拟同步过程
  setTimeout(() => {
    syncStatus.value = 'connected'
    lastSyncTime.value = new Date().toLocaleString()
    syncedFilesCount.value += 25
    syncProgress.value = 100
    ElMessage.success('同步完成')
  }, 3000)
}

const showSyncHistory = () => {
  showHistoryDialog.value = true
}

const saveSyncConfig = async () => {
  try {
    // 保存配置到本地存储
    localStorage.setItem('syncConfig', JSON.stringify(syncConfig))
    ElMessage.success('同步设置已保存')
  } catch (error) {
    ElMessage.error('保存失败')
  }
}

const testConnection = async () => {
  ElMessage.info('正在测试连接...')
  
  // 模拟连接测试
  setTimeout(() => {
    ElMessage.success('连接测试成功')
  }, 2000)
}

const resetSyncConfig = async () => {
  try {
    await ElMessageBox.confirm('确定要重置同步设置吗？', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    Object.assign(syncConfig, {
      service: 'local',
      cloudProvider: 'aliyun',
      serverUrl: '',
      frequency: 'hourly',
      contentTypes: ['images', 'videos', 'documents', 'metadata'],
      maxFileSize: 100,
      wifiOnly: true,
      batteryOptimize: false,
      conflictResolution: 'keepNewer',
      backupBeforeSync: true,
      keepBackups: true,
      backupRetention: 30
    })
    
    ElMessage.success('同步设置已重置')
  } catch {
    // 用户取消操作
  }
}

const addDevice = () => {
  showAddDeviceDialog.value = true
}

const scanDevices = async () => {
  ElMessage.info('正在扫描设备...')
  
  // 模拟设备扫描
  setTimeout(() => {
    ElMessage.success('扫描完成，发现 2 个可用设备')
  }, 3000)
}

const confirmAddDevice = async () => {
  if (!newDevice.name.trim()) {
    ElMessage.error('请输入设备名称')
    return
  }
  
  const device: Device = {
    id: Date.now().toString(),
    name: newDevice.name,
    type: newDevice.type,
    os: getDefaultOS(newDevice.type),
    status: 'online',
    lastSeen: '刚刚'
  }
  
  connectedDevices.value.push(device)
  deviceCount.value = connectedDevices.value.length
  
  showAddDeviceDialog.value = false
  ElMessage.success('设备添加成功')
  
  // 重置表单
  Object.assign(newDevice, {
    name: '',
    type: 'desktop',
    connection: 'qrcode',
    code: ''
  })
}

const getDefaultOS = (type: string) => {
  switch (type) {
    case 'desktop':
      return 'Windows 11'
    case 'laptop':
      return 'macOS'
    case 'mobile':
      return 'Android'
    default:
      return 'Unknown'
  }
}

const changePassword = () => {
  ElMessage.info('密码修改功能开发中...')
}

const viewSecurityLog = () => {
  ElMessage.info('安全日志功能开发中...')
}

// 生命周期钩子
onMounted(() => {
  // 加载保存的配置
  const savedConfig = localStorage.getItem('syncConfig')
  if (savedConfig) {
    Object.assign(syncConfig, JSON.parse(savedConfig))
  }
  
  // 初始化统计数据
  deviceCount.value = connectedDevices.value.length
  totalAssets.value = 1567
  syncedAssets.value = 1342
  pendingAssets.value = totalAssets.value - syncedAssets.value
  syncProgress.value = Math.round((syncedAssets.value / totalAssets.value) * 100)
  
  // 模拟连接状态检查
  setTimeout(() => {
    syncStatus.value = 'connected'
    lastSyncTime.value = new Date().toLocaleString()
  }, 1000)
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.sync-settings {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.sync-toolbar {
  padding: 12px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  
  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 12px;
    
    h2 {
      margin: 0;
      color: var(--el-text-color-primary);
      font-size: 18px;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 8px;
  }
}

.sync-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sync-status-panel {
  width: 300px;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
  
  .status-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
      font-weight: 600;
    }
    
    .status-card {
      background: var(--el-bg-color-page);
      border-radius: 8px;
      padding: 16px;
      border: 1px solid var(--el-border-color-light);
      
      .status-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        font-weight: 500;
        
        &.connected {
          color: var(--el-color-success);
        }
        
        &.syncing {
          color: var(--el-color-warning);
        }
        
        &.error {
          color: var(--el-color-error);
        }
        
        &.disconnected {
          color: var(--el-text-color-secondary);
        }
      }
      
      .status-details {
        .detail-item {
          display: flex;
          justify-content: space-between;
          margin-bottom: 6px;
          font-size: 14px;
          
          span:first-child {
            color: var(--el-text-color-secondary);
          }
          
          span:last-child {
            color: var(--el-text-color-primary);
            font-weight: 500;
          }
        }
      }
    }
    
    .stats-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
      
      .stat-item {
        text-align: center;
        padding: 16px;
        background: var(--el-bg-color-page);
        border-radius: 8px;
        border: 1px solid var(--el-border-color-light);
        
        .stat-value {
          font-size: 24px;
          font-weight: 600;
          color: var(--el-color-primary);
          margin-bottom: 4px;
        }
        
        .stat-label {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
      }
    }
    
    .network-status {
      .network-item {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;
        
        span:first-child {
          color: var(--el-text-color-secondary);
        }
        
        span:last-child {
          color: var(--el-text-color-primary);
          font-weight: 500;
        }
      }
    }
  }
}

.sync-settings-panel {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  background: var(--el-bg-color-page);
  
  .settings-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
      font-weight: 600;
    }
    
    :deep(.el-form) {
      .el-form-item {
        margin-bottom: 20px;
        
        .el-form-item__label {
          color: var(--el-text-color-primary);
          font-weight: 500;
        }
        
        .el-checkbox-group {
          display: flex;
          flex-wrap: wrap;
          gap: 12px;
        }
        
        .el-input-number {
          width: 120px;
        }
      }
    }
  }
  
  .settings-actions {
    display: flex;
    gap: 12px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-light);
  }
}

.devices-panel {
  width: 320px;
  border-left: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
  
  .devices-section {
    margin-bottom: 32px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
      font-size: 16px;
      font-weight: 600;
    }
    
    .devices-list {
      .device-item {
        display: flex;
        align-items: center;
        padding: 12px;
        border-radius: 8px;
        border: 1px solid var(--el-border-color-light);
        margin-bottom: 8px;
        transition: all 0.3s ease;
        cursor: pointer;
        
        &:hover {
          background: var(--el-fill-color-light);
          border-color: var(--el-color-primary-light-5);
        }
        
        .device-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          background: var(--el-color-primary-light-9);
          display: flex;
          align-items: center;
          justify-content: center;
          margin-right: 12px;
          flex-shrink: 0;
          
          .el-icon {
            font-size: 20px;
            color: var(--el-color-primary);
          }
        }
        
        .device-info {
          flex: 1;
          
          .device-name {
            font-weight: 500;
            color: var(--el-text-color-primary);
            margin-bottom: 4px;
          }
          
          .device-details {
            display: flex;
            flex-direction: column;
            gap: 2px;
            font-size: 12px;
            color: var(--el-text-color-secondary);
          }
        }
        
        .device-status {
          &.online {
            color: var(--el-color-success);
          }
          
          &.syncing {
            color: var(--el-color-warning);
          }
          
          &.offline {
            color: var(--el-text-color-secondary);
          }
        }
      }
    }
    
    .empty-devices {
      text-align: center;
      padding: 40px 20px;
      color: var(--el-text-color-secondary);
      
      .el-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
      }
      
      p {
        margin: 0;
        font-size: 14px;
      }
    }
    
    .device-actions {
      display: flex;
      gap: 8px;
      margin-bottom: 16px;
    }
    
    .device-stats {
      .stat-row {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;
        font-size: 14px;
        
        span:first-child {
          color: var(--el-text-color-secondary);
        }
        
        span:last-child {
          color: var(--el-text-color-primary);
          font-weight: 500;
        }
      }
    }
    
    .security-settings {
      display: flex;
      flex-direction: column;
      gap: 12px;
      margin-bottom: 16px;
      
      :deep(.el-switch) {
        .el-switch__label {
          color: var(--el-text-color-primary);
          font-weight: 500;
        }
      }
    }
    
    .security-actions {
      display: flex;
      gap: 8px;
    }
  }
}

.sync-history {
  max-height: 400px;
  overflow-y: auto;
  
  .history-item {
    .history-status {
      margin-bottom: 8px;
    }
    
    .history-details {
      p {
        margin: 0 0 8px;
        color: var(--el-text-color-primary);
      }
      
      .history-meta {
        display: flex;
        gap: 16px;
        font-size: 12px;
        color: var(--el-text-color-secondary);
      }
    }
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .sync-status-panel {
    width: 280px;
  }
  
  .devices-panel {
    width: 280px;
  }
}

@media (max-width: 992px) {
  .sync-content {
    flex-direction: column;
  }
  
  .sync-status-panel {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
    max-height: 300px;
  }
  
  .devices-panel {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--el-border-color-light);
    max-height: 300px;
  }
}

@media (max-width: 768px) {
  .sync-toolbar {
    padding: 8px 16px;
    flex-wrap: wrap;
    gap: 8px;
    
    .toolbar-left {
      order: 1;
      flex: 1;
    }
    
    .toolbar-right {
      order: 2;
      flex: 100%;
      justify-content: flex-end;
      margin-top: 8px;
    }
  }
  
  .sync-settings-panel {
    padding: 16px;
    
    .settings-section {
      :deep(.el-form) {
        .el-checkbox-group {
          flex-direction: column;
          gap: 8px;
        }
      }
    }
  }
  
  .devices-panel {
    padding: 16px;
    
    .devices-section {
      .device-actions {
        flex-direction: column;
      }
      
      .security-actions {
        flex-direction: column;
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

// 加载状态
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

// 状态指示器动画
.status-indicator {
  .el-icon {
    animation: pulse 2s infinite;
  }
  
  &.syncing .el-icon {
    animation: spin 1s linear infinite;
  }
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>