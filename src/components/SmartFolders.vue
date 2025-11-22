<template>
  <div class="smart-folders">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <h2>智能文件夹</h2>
        <el-button @click="showCreateDialog = true">
          <el-icon><Plus /></el-icon>
          新建智能文件夹
        </el-button>
        <el-button @click="refreshSmartFolders">
          <el-icon><Refresh /></el-icon>
          刷新
        </el-button>
      </div>
      
      <div class="toolbar-right">
        <el-input
          v-model="searchQuery"
          placeholder="搜索智能文件夹..."
          prefix-icon="Search"
          style="width: 200px"
        />
        <el-button @click="showSettings = true">
          <el-icon><Setting /></el-icon>
          设置
        </el-button>
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="content">
      <!-- 智能文件夹列表 -->
      <div class="smart-folders-list">
        <div 
          v-for="folder in filteredSmartFolders" 
          :key="folder.id"
          class="smart-folder-card"
          :class="{ active: activeFolderId === folder.id }"
          @click="selectFolder(folder)"
        >
          <div class="folder-header">
            <div class="folder-icon">
              <el-icon size="20">
                <component :is="getFolderIcon(folder.type)" />
              </el-icon>
            </div>
            <div class="folder-info">
              <h3>{{ folder.name }}</h3>
              <div class="folder-stats">
                <span>{{ folder.assets.length }} 个素材</span>
                <span class="update-time">更新于 {{ formatTime(folder.updatedAt) }}</span>
              </div>
            </div>
            <div class="folder-actions">
              <el-dropdown trigger="click">
                <el-button size="small" circle>
                  <el-icon><More /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="editFolder(folder)">
                      <el-icon><Edit /></el-icon>
                      编辑规则
                    </el-dropdown-item>
                    <el-dropdown-item @click="duplicateFolder(folder)">
                      <el-icon><CopyDocument /></el-icon>
                      复制
                    </el-dropdown-item>
                    <el-dropdown-item @click="exportFolder(folder)">
                      <el-icon><Download /></el-icon>
                      导出
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="deleteFolder(folder)" class="danger">
                      <el-icon><Delete /></el-icon>
                      删除
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
          
          <div class="folder-rules">
            <div class="rules-preview">
              <el-tag 
                v-for="rule in folder.rules.slice(0, 3)" 
                :key="rule.id" 
                size="small"
                :type="getRuleType(rule.operator)"
              >
                {{ formatRule(rule) }}
              </el-tag>
              <span v-if="folder.rules.length > 3" class="more-rules">
                +{{ folder.rules.length - 3 }} 条规则
              </span>
            </div>
            <div class="rule-logic">
              <el-tag size="small" effect="plain">
                {{ folder.logic === 'and' ? '且' : '或' }}
              </el-tag>
            </div>
          </div>
          
          <div class="folder-thumbnails">
            <div 
              v-for="asset in folder.assets.slice(0, 6)" 
              :key="asset.id"
              class="thumbnail"
              :style="{ backgroundImage: `url(${asset.thumbnail})` }"
              @click.stop="previewAsset(asset)"
            ></div>
            <div v-if="folder.assets.length > 6" class="thumbnail-more">
              +{{ folder.assets.length - 6 }}
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-if="filteredSmartFolders.length === 0" class="empty-state">
          <el-icon size="64" color="var(--el-text-color-placeholder)">
            <FolderOpened />
          </el-icon>
          <p>暂无智能文件夹</p>
          <span>点击"新建智能文件夹"开始创建基于规则的自动分类</span>
          <el-button type="primary" @click="showCreateDialog = true">
            创建第一个智能文件夹
          </el-button>
        </div>
      </div>
      
      <!-- 右侧详情面板 -->
      <div v-if="activeFolder" class="folder-details">
        <div class="details-header">
          <h3>{{ activeFolder.name }}</h3>
          <div class="header-actions">
            <el-button @click="editFolder(activeFolder)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button type="primary" @click="applyToLibrary">
              <el-icon><Check /></el-icon>
              应用到素材库
            </el-button>
          </div>
        </div>
        
        <!-- 规则详情 -->
        <div class="rules-section">
          <h4>分类规则</h4>
          <div class="rules-list">
            <div 
              v-for="rule in activeFolder.rules" 
              :key="rule.id"
              class="rule-item"
            >
              <div class="rule-content">
                <span class="rule-field">{{ getFieldLabel(rule.field) }}</span>
                <span class="rule-operator">{{ getOperatorLabel(rule.operator) }}</span>
                <span class="rule-value">{{ formatRuleValue(rule) }}</span>
              </div>
              <div class="rule-actions">
                <el-button size="small" circle @click="editRule(rule)">
                  <el-icon><Edit /></el-icon>
                </el-button>
                <el-button size="small" circle @click="deleteRule(rule)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <el-button class="add-rule-btn" @click="addRule">
              <el-icon><Plus /></el-icon>
              添加规则
            </el-button>
          </div>
          
          <div class="logic-selector">
            <span>规则逻辑：</span>
            <el-radio-group v-model="activeFolder.logic" size="small">
              <el-radio label="and">且 (所有规则都满足)</el-radio>
              <el-radio label="or">或 (任一规则满足)</el-radio>
            </el-radio-group>
          </div>
        </div>
        
        <!-- 匹配素材 -->
        <div class="assets-section">
          <div class="section-header">
            <h4>匹配素材 ({{ activeFolder.assets.length }})</h4>
            <el-button size="small" @click="refreshMatchingAssets">
              <el-icon><Refresh /></el-icon>
              重新匹配
            </el-button>
          </div>
          
          <div class="matching-assets">
            <div 
              v-for="asset in activeFolder.assets" 
              :key="asset.id"
              class="matching-asset"
              @click="previewAsset(asset)"
            >
              <div class="asset-thumb">
                <img :src="asset.thumbnail" :alt="asset.name" />
              </div>
              <div class="asset-info">
                <div class="asset-name">{{ asset.name }}</div>
                <div class="asset-details">
                  <span>{{ formatFileSize(asset.size) }}</span>
                  <span>{{ formatDate(asset.createdAt) }}</span>
                </div>
                <div class="asset-tags">
                  <el-tag 
                    v-for="tag in asset.tags.slice(0, 2)" 
                    :key="tag" 
                    size="small"
                  >
                    {{ tag }}
                  </el-tag>
                </div>
              </div>
            </div>
            
            <div v-if="activeFolder.assets.length === 0" class="no-matching">
              <el-icon size="48" color="var(--el-text-color-placeholder)">
                <Search />
              </el-icon>
              <p>暂无匹配素材</p>
              <span>调整规则条件或检查素材库内容</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 创建/编辑智能文件夹对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingFolder ? '编辑智能文件夹' : '新建智能文件夹'"
      width="700px"
    >
      <div class="create-folder-dialog">
        <el-form :model="folderForm" label-width="100px">
          <el-form-item label="文件夹名称" required>
            <el-input v-model="folderForm.name" placeholder="请输入文件夹名称" />
          </el-form-item>
          
          <el-form-item label="文件夹类型">
            <el-select v-model="folderForm.type" placeholder="请选择类型">
              <el-option label="时间分类" value="time"></el-option>
              <el-option label="类型分类" value="type"></el-option>
              <el-option label="标签分类" value="tag"></el-option>
              <el-option label="颜色分类" value="color"></el-option>
              <el-option label="AI智能分类" value="ai"></el-option>
              <el-option label="自定义规则" value="custom"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="描述">
            <el-input 
              v-model="folderForm.description" 
              type="textarea" 
              :rows="3"
              placeholder="请输入文件夹描述（可选）"
            />
          </el-form-item>
          
          <el-form-item label="封面图片">
            <el-upload
              action="#"
              :show-file-list="false"
              :before-upload="beforeCoverUpload"
              accept="image/*"
            >
              <el-button>
                <el-icon><Upload /></el-icon>
                选择封面
              </el-button>
            </el-upload>
            <div v-if="folderForm.cover" class="cover-preview">
              <img :src="folderForm.cover" alt="封面预览" />
              <el-button size="small" @click="folderForm.cover = ''">移除</el-button>
            </div>
          </el-form-item>
        </el-form>
        
        <div class="rules-section">
          <h4>分类规则</h4>
          <div class="rules-list">
            <div 
              v-for="rule in folderForm.rules" 
              :key="rule.id"
              class="rule-item"
            >
              <div class="rule-content">
                <el-select v-model="rule.field" placeholder="字段" size="small">
                  <el-option 
                    v-for="field in availableFields" 
                    :key="field.value" 
                    :label="field.label" 
                    :value="field.value"
                  />
                </el-select>
                
                <el-select v-model="rule.operator" placeholder="操作符" size="small">
                  <el-option 
                    v-for="op in getAvailableOperators(rule.field)" 
                    :key="op.value" 
                    :label="op.label" 
                    :value="op.value"
                  />
                </el-select>
                
                <el-input 
                  v-model="rule.value" 
                  placeholder="值" 
                  size="small"
                  style="width: 120px"
                />
              </div>
              
              <div class="rule-actions">
                <el-button size="small" circle @click="removeRule(rule)">
                  <el-icon><Delete /></el-icon>
                </el-button>
              </div>
            </div>
            
            <el-button @click="addNewRule" class="add-rule-btn">
              <el-icon><Plus /></el-icon>
              添加规则
            </el-button>
          </div>
          
          <div class="logic-selector">
            <span>规则逻辑：</span>
            <el-radio-group v-model="folderForm.logic" size="small">
              <el-radio label="and">且 (所有规则都满足)</el-radio>
              <el-radio label="or">或 (任一规则满足)</el-radio>
            </el-radio-group>
          </div>
        </div>
        
        <template #footer>
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveFolder"
            :disabled="!folderForm.name.trim()"
          >
            {{ editingFolder ? '保存' : '创建' }}
          </el-button>
        </template>
      </div>
    </el-dialog>

    <!-- 规则编辑对话框 -->
    <el-dialog
      v-model="showRuleDialog"
      title="编辑规则"
      width="500px"
    >
      <div class="rule-edit-dialog">
        <el-form :model="ruleForm" label-width="80px">
          <el-form-item label="字段">
            <el-select v-model="ruleForm.field" placeholder="请选择字段">
              <el-option 
                v-for="field in availableFields" 
                :key="field.value" 
                :label="field.label" 
                :value="field.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="操作符">
            <el-select v-model="ruleForm.operator" placeholder="请选择操作符">
              <el-option 
                v-for="op in getAvailableOperators(ruleForm.field)" 
                :key="op.value" 
                :label="op.label" 
                :value="op.value"
              />
            </el-select>
          </el-form-item>
          
          <el-form-item label="值">
            <el-input v-model="ruleForm.value" placeholder="请输入值" />
          </el-form-item>
        </el-form>
        
        <template #footer>
          <el-button @click="showRuleDialog = false">取消</el-button>
          <el-button type="primary" @click="saveRule">保存</el-button>
        </template>
      </div>
    </el-dialog>

    <!-- 设置抽屉 -->
    <el-drawer
      v-model="showSettings"
      title="智能文件夹设置"
      direction="rtl"
      size="400px"
    >
      <div class="settings-content">
        <el-form label-width="120px">
          <el-form-item label="自动更新">
            <el-switch v-model="settings.autoUpdate" />
          </el-form-item>
          
          <el-form-item label="更新频率">
            <el-select v-model="settings.updateFrequency">
              <el-option label="实时更新" value="realtime"></el-option>
              <el-option label="每小时" value="hourly"></el-option>
              <el-option label="每天" value="daily"></el-option>
              <el-option label="手动更新" value="manual"></el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item label="最大数量">
            <el-input-number 
              v-model="settings.maxAssets" 
              :min="100" 
              :max="10000" 
              :step="100"
            />
            <span class="form-tip">每个智能文件夹最多包含的素材数量</span>
          </el-form-item>
          
          <el-form-item label="缓存时间">
            <el-input-number 
              v-model="settings.cacheTime" 
              :min="1" 
              :max="24" 
              :step="1"
            />
            <span class="form-tip">匹配结果缓存时间（小时）</span>
          </el-form-item>
          
          <el-form-item label="显示预览">
            <el-switch v-model="settings.showPreview" />
          </el-form-item>
          
          <el-form-item label="默认逻辑">
            <el-radio-group v-model="settings.defaultLogic">
              <el-radio label="and">且</el-radio>
              <el-radio label="or">或</el-radio>
            </el-radio-group>
          </el-form-item>
        </el-form>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useLibraryStore } from '@/stores/library'

// 图标导入
import {
  Plus,
  Refresh,
  Setting,
  Search,
  More,
  Edit,
  CopyDocument,
  Download,
  Delete,
  FolderOpened,
  Upload,
  Check
} from '@element-plus/icons-vue'

const libraryStore = useLibraryStore()

// 响应式数据
const showCreateDialog = ref(false)
const showRuleDialog = ref(false)
const showSettings = ref(false)
const searchQuery = ref('')
const activeFolderId = ref('')
const editingFolder = ref<any>(null)
const editingRule = ref<any>(null)

// 智能文件夹数据
const smartFolders = ref<any[]>([])

// 表单数据
const folderForm = reactive({
  id: '',
  name: '',
  type: 'custom',
  description: '',
  cover: '',
  logic: 'and',
  rules: [] as any[]
})

const ruleForm = reactive({
  id: '',
  field: '',
  operator: '',
  value: ''
})

// 设置
const settings = reactive({
  autoUpdate: true,
  updateFrequency: 'realtime',
  maxAssets: 1000,
  cacheTime: 1,
  showPreview: true,
  defaultLogic: 'and'
})

// 可用字段和操作符
const availableFields = ref([
  { value: 'name', label: '文件名' },
  { value: 'type', label: '文件类型' },
  { value: 'size', label: '文件大小' },
  { value: 'createdAt', label: '创建时间' },
  { value: 'modifiedAt', label: '修改时间' },
  { value: 'tags', label: '标签' },
  { value: 'folder', label: '所在文件夹' },
  { value: 'extension', label: '文件扩展名' },
  { value: 'width', label: '图片宽度' },
  { value: 'height', label: '图片高度' },
  { value: 'duration', label: '视频时长' }
])

const operators = ref({
  string: [
    { value: 'contains', label: '包含' },
    { value: 'notContains', label: '不包含' },
    { value: 'equals', label: '等于' },
    { value: 'startsWith', label: '开头为' },
    { value: 'endsWith', label: '结尾为' }
  ],
  number: [
    { value: 'equals', label: '等于' },
    { value: 'notEquals', label: '不等于' },
    { value: 'greaterThan', label: '大于' },
    { value: 'lessThan', label: '小于' },
    { value: 'between', label: '介于' }
  ],
  date: [
    { value: 'equals', label: '等于' },
    { value: 'before', label: '之前' },
    { value: 'after', label: '之后' },
    { value: 'between', label: '介于' },
    { value: 'lastDays', label: '最近几天' }
  ],
  array: [
    { value: 'contains', label: '包含' },
    { value: 'notContains', label: '不包含' },
    { value: 'empty', label: '为空' },
    { value: 'notEmpty', label: '不为空' }
  ]
})

// 计算属性
const activeFolder = computed(() => {
  return smartFolders.value.find(f => f.id === activeFolderId.value)
})

const filteredSmartFolders = computed(() => {
  if (!searchQuery.value.trim()) {
    return smartFolders.value
  }
  
  const query = searchQuery.value.toLowerCase()
  return smartFolders.value.filter(folder => 
    folder.name.toLowerCase().includes(query) ||
    folder.description.toLowerCase().includes(query)
  )
})

// 方法
const getFolderIcon = (type: string) => {
  const icons: Record<string, string> = {
    time: 'Clock',
    type: 'Folder',
    tag: 'PriceTag',
    color: 'Brush',
    ai: 'Cpu',
    custom: 'FolderOpened'
  }
  return icons[type] || 'FolderOpened'
}

const getRuleType = (operator: string) => {
  if (['contains', 'equals', 'startsWith', 'endsWith'].includes(operator)) {
    return 'success'
  } else if (['notContains', 'notEquals'].includes(operator)) {
    return 'danger'
  } else {
    return 'info'
  }
}

const formatRule = (rule: any) => {
  const fieldLabel = getFieldLabel(rule.field)
  const operatorLabel = getOperatorLabel(rule.operator)
  return `${fieldLabel} ${operatorLabel} ${rule.value}`
}

const getFieldLabel = (field: string) => {
  const fieldObj = availableFields.value.find(f => f.value === field)
  return fieldObj?.label || field
}

const getOperatorLabel = (operator: string) => {
  for (const type in operators.value) {
    const opObj = operators.value[type as keyof typeof operators.value]
      .find((op: any) => op.value === operator)
    if (opObj) return opObj.label
  }
  return operator
}

const getAvailableOperators = (field: string) => {
  const fieldType = getFieldType(field)
  return operators.value[fieldType as keyof typeof operators.value] || []
}

const getFieldType = (field: string) => {
  const numberFields = ['size', 'width', 'height', 'duration']
  const dateFields = ['createdAt', 'modifiedAt']
  const arrayFields = ['tags']
  
  if (numberFields.includes(field)) return 'number'
  if (dateFields.includes(field)) return 'date'
  if (arrayFields.includes(field)) return 'array'
  return 'string'
}

const formatRuleValue = (rule: any) => {
  if (rule.field === 'createdAt' || rule.field === 'modifiedAt') {
    return new Date(rule.value).toLocaleDateString()
  }
  if (rule.field === 'size') {
    return formatFileSize(parseInt(rule.value))
  }
  return rule.value
}

const formatTime = (date: Date) => {
  return new Date(date).toLocaleString()
}

const formatFileSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date: Date) => {
  return new Date(date).toLocaleDateString()
}

const selectFolder = (folder: any) => {
  activeFolderId.value = folder.id
}

const createFolder = () => {
  editingFolder.value = null
  Object.assign(folderForm, {
    id: '',
    name: '',
    type: 'custom',
    description: '',
    cover: '',
    logic: 'and',
    rules: []
  })
  showCreateDialog.value = true
}

const editFolder = (folder: any) => {
  editingFolder.value = folder
  Object.assign(folderForm, {
    id: folder.id,
    name: folder.name,
    type: folder.type,
    description: folder.description || '',
    cover: folder.cover || '',
    logic: folder.logic,
    rules: [...folder.rules]
  })
  showCreateDialog.value = true
}

const saveFolder = async () => {
  try {
    const folderData = {
      ...folderForm,
      updatedAt: new Date(),
      assets: []
    }
    
    if (editingFolder.value) {
      // 更新现有文件夹
      const index = smartFolders.value.findIndex(f => f.id === editingFolder.value.id)
      if (index >= 0) {
        smartFolders.value[index] = folderData
      }
    } else {
      // 创建新文件夹
      folderData.id = generateId()
      folderData.createdAt = new Date()
      smartFolders.value.push(folderData)
    }
    
    // 保存到本地存储
    await saveSmartFoldersToStorage()
    
    ElMessage.success(editingFolder.value ? '文件夹已更新' : '文件夹已创建')
    showCreateDialog.value = false
    
    // 刷新匹配的素材
    await refreshMatchingAssetsForFolder(folderData.id)
  } catch (error) {
    console.error('保存文件夹失败:', error)
    ElMessage.error('保存失败')
  }
}

const deleteFolder = async (folder: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除智能文件夹"${folder.name}"吗？此操作不可撤销。`,
      '确认删除',
      { type: 'warning' }
    )
    
    smartFolders.value = smartFolders.value.filter(f => f.id !== folder.id)
    await saveSmartFoldersToStorage()
    
    if (activeFolderId.value === folder.id) {
      activeFolderId.value = ''
    }
    
    ElMessage.success('文件夹已删除')
  } catch (error) {
    console.error('删除文件夹失败:', error)
  }
}

const duplicateFolder = (folder: any) => {
  const duplicated = {
    ...folder,
    id: generateId(),
    name: `${folder.name} - 副本`,
    createdAt: new Date(),
    updatedAt: new Date()
  }
  
  smartFolders.value.push(duplicated)
  saveSmartFoldersToStorage()
  ElMessage.success('文件夹已复制')
}

const exportFolder = (folder: any) => {
  // 导出文件夹配置
  const config = {
    name: folder.name,
    type: folder.type,
    rules: folder.rules,
    logic: folder.logic,
    exportTime: new Date().toISOString()
  }
  
  const blob = new Blob([JSON.stringify(config, null, 2)], { 
    type: 'application/json' 
  })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${folder.name}.json`
  a.click()
  URL.revokeObjectURL(url)
  
  ElMessage.success('文件夹配置已导出')
}

const addNewRule = () => {
  folderForm.rules.push({
    id: generateId(),
    field: 'name',
    operator: 'contains',
    value: ''
  })
}

const removeRule = (rule: any) => {
  const index = folderForm.rules.findIndex(r => r.id === rule.id)
  if (index >= 0) {
    folderForm.rules.splice(index, 1)
  }
}

const editRule = (rule: any) => {
  editingRule.value = rule
  Object.assign(ruleForm, { ...rule })
  showRuleDialog.value = true
}

const saveRule = () => {
  if (editingRule.value) {
    Object.assign(editingRule.value, { ...ruleForm })
  }
  showRuleDialog.value = false
  ElMessage.success('规则已更新')
}

const deleteRule = async (rule: any) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这条规则吗？',
      '确认删除',
      { type: 'warning' }
    )
    
    if (activeFolder.value) {
      activeFolder.value.rules = activeFolder.value.rules.filter((r: any) => r.id !== rule.id)
      await saveSmartFoldersToStorage()
      await refreshMatchingAssetsForFolder(activeFolder.value.id)
    }
    
    ElMessage.success('规则已删除')
  } catch (error) {
    console.error('删除规则失败:', error)
  }
}

const addRule = () => {
  if (activeFolder.value) {
    activeFolder.value.rules.push({
      id: generateId(),
      field: 'name',
      operator: 'contains',
      value: ''
    })
    saveSmartFoldersToStorage()
  }
}

const refreshSmartFolders = async () => {
  // 刷新所有智能文件夹的匹配结果
  for (const folder of smartFolders.value) {
    await refreshMatchingAssetsForFolder(folder.id)
  }
  ElMessage.success('所有智能文件夹已刷新')
}

const refreshMatchingAssets = async () => {
  if (activeFolder.value) {
    await refreshMatchingAssetsForFolder(activeFolder.value.id)
    ElMessage.success('匹配结果已刷新')
  }
}

const refreshMatchingAssetsForFolder = async (folderId: string) => {
  const folder = smartFolders.value.find(f => f.id === folderId)
  if (!folder) return
  
  // 根据规则匹配素材
  const matchingAssets = libraryStore.assets.filter(asset => {
    return evaluateRules(asset, folder.rules, folder.logic)
  })
  
  folder.assets = matchingAssets.slice(0, settings.maxAssets)
  folder.updatedAt = new Date()
  
  await saveSmartFoldersToStorage()
}

const evaluateRules = (asset: any, rules: any[], logic: string) => {
  if (rules.length === 0) return true
  
  const results = rules.map(rule => evaluateRule(asset, rule))
  
  if (logic === 'and') {
    return results.every(result => result)
  } else {
    return results.some(result => result)
  }
}

const evaluateRule = (asset: any, rule: any) => {
  const assetValue = asset[rule.field]
  
  switch (rule.operator) {
    case 'contains':
      return assetValue?.toString().toLowerCase().includes(rule.value.toLowerCase())
    case 'notContains':
      return !assetValue?.toString().toLowerCase().includes(rule.value.toLowerCase())
    case 'equals':
      return assetValue?.toString().toLowerCase() === rule.value.toLowerCase()
    case 'notEquals':
      return assetValue?.toString().toLowerCase() !== rule.value.toLowerCase()
    case 'startsWith':
      return assetValue?.toString().toLowerCase().startsWith(rule.value.toLowerCase())
    case 'endsWith':
      return assetValue?.toString().toLowerCase().endsWith(rule.value.toLowerCase())
    case 'greaterThan':
      return parseFloat(assetValue) > parseFloat(rule.value)
    case 'lessThan':
      return parseFloat(assetValue) < parseFloat(rule.value)
    case 'before':
      return new Date(assetValue) < new Date(rule.value)
    case 'after':
      return new Date(assetValue) > new Date(rule.value)
    case 'empty':
      return !assetValue || assetValue.length === 0
    case 'notEmpty':
      return assetValue && assetValue.length > 0
    default:
      return false
  }
}

const applyToLibrary = async () => {
  if (!activeFolder.value) return
  
  try {
    // 创建实际文件夹
    const folder = await libraryStore.createFolder(activeFolder.value.name)
    
    // 将匹配的素材移动到新文件夹
    for (const asset of activeFolder.value.assets) {
      await libraryStore.moveAssetToFolder(asset.id, folder.id)
    }
    
    ElMessage.success(`已将 ${activeFolder.value.assets.length} 个素材移动到新文件夹`)
  } catch (error) {
    console.error('应用到素材库失败:', error)
    ElMessage.error('应用失败')
  }
}

const beforeCoverUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2
  
  if (!isImage) {
    ElMessage.error('只能上传图片文件！')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB！')
    return false
  }
  
  // 预览图片
  const reader = new FileReader()
  reader.onload = (e) => {
    folderForm.cover = e.target?.result as string
  }
  reader.readAsDataURL(file)
  
  return false // 阻止自动上传
}

const previewAsset = (asset: any) => {
  // 预览素材
  window.electronAPI.previewImage(asset.thumbnail)
}

const generateId = () => {
  return Date.now().toString(36) + Math.random().toString(36).substr(2)
}

const saveSmartFoldersToStorage = async () => {
  try {
    localStorage.setItem('smartFolders', JSON.stringify(smartFolders.value))
  } catch (error) {
    console.error('保存智能文件夹失败:', error)
  }
}

const loadSmartFoldersFromStorage = () => {
  try {
    const stored = localStorage.getItem('smartFolders')
    if (stored) {
      smartFolders.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('加载智能文件夹失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadSmartFoldersFromStorage()
  
  // 如果有智能文件夹，刷新匹配结果
  if (smartFolders.value.length > 0) {
    refreshSmartFolders()
  }
})
</script>

<style scoped lang="scss">
@import '@/styles/index.scss';

.smart-folders {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

.toolbar {
  padding: 16px 24px;
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
  
  .toolbar-left {
    display: flex;
    align-items: center;
    gap: 16px;
    
    h2 {
      margin: 0;
      color: var(--el-text-color-primary);
    }
  }
  
  .toolbar-right {
    display: flex;
    gap: 12px;
    align-items: center;
  }
}

.content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.smart-folders-list {
  width: 400px;
  border-right: 1px solid var(--el-border-color-light);
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 20px;
}

.smart-folder-card {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--el-color-primary);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }
  
  &.active {
    border-color: var(--el-color-primary);
    background: var(--el-color-primary-light-9);
  }
  
  .folder-header {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
    
    .folder-icon {
      flex-shrink: 0;
      width: 40px;
      height: 40px;
      background: var(--el-color-primary-light-8);
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      color: var(--el-color-primary);
    }
    
    .folder-info {
      flex: 1;
      
      h3 {
        margin: 0 0 4px;
        color: var(--el-text-color-primary);
        font-size: 16px;
        line-height: 1.2;
      }
      
      .folder-stats {
        display: flex;
        justify-content: space-between;
        align-items: center;
        
        span {
          font-size: 12px;
          color: var(--el-text-color-secondary);
        }
        
        .update-time {
          font-size: 11px;
          color: var(--el-text-color-placeholder);
        }
      }
    }
    
    .folder-actions {
      flex-shrink: 0;
    }
  }
  
  .folder-rules {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 12px;
    
    .rules-preview {
      flex: 1;
      display: flex;
      flex-wrap: wrap;
      gap: 4px;
      
      .more-rules {
        font-size: 11px;
        color: var(--el-text-color-placeholder);
        align-self: center;
      }
    }
    
    .rule-logic {
      flex-shrink: 0;
      margin-left: 8px;
    }
  }
  
  .folder-thumbnails {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 4px;
    
    .thumbnail {
      aspect-ratio: 1;
      background-size: cover;
      background-position: center;
      border-radius: 4px;
      border: 1px solid var(--el-border-color);
      cursor: pointer;
      
      &:hover {
        transform: scale(1.05);
      }
    }
    
    .thumbnail-more {
      aspect-ratio: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--el-bg-color-overlay);
      border-radius: 4px;
      border: 1px dashed var(--el-border-color);
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin: 16px 0 8px;
    font-size: 16px;
  }
  
  span {
    display: block;
    margin-bottom: 16px;
    font-size: 14px;
  }
}

.folder-details {
  flex: 1;
  background: var(--el-bg-color);
  overflow-y: auto;
  padding: 24px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
  
  h3 {
    margin: 0;
    color: var(--el-text-color-primary);
    font-size: 20px;
  }
  
  .header-actions {
    display: flex;
    gap: 8px;
  }
}

.rules-section {
  margin-bottom: 32px;
  
  h4 {
    margin: 0 0 16px;
    color: var(--el-text-color-primary);
    font-size: 16px;
  }
}

.rules-list {
  .rule-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px;
    background: var(--el-bg-color-overlay);
    border-radius: 6px;
    margin-bottom: 8px;
    
    .rule-content {
      flex: 1;
      display: flex;
      align-items: center;
      gap: 8px;
      
      .rule-field,
      .rule-operator,
      .rule-value {
        padding: 4px 8px;
        background: var(--el-bg-color);
        border-radius: 4px;
        font-size: 14px;
      }
      
      .rule-field {
        color: var(--el-color-primary);
        font-weight: 500;
      }
      
      .rule-operator {
        color: var(--el-text-color-regular);
      }
      
      .rule-value {
        color: var(--el-text-color-secondary);
      }
    }
    
    .rule-actions {
      flex-shrink: 0;
      display: flex;
      gap: 4px;
    }
  }
  
  .add-rule-btn {
    width: 100%;
    margin-top: 8px;
  }
}

.logic-selector {
  margin-top: 16px;
  padding: 12px;
  background: var(--el-bg-color-overlay);
  border-radius: 6px;
  
  span {
    margin-right: 12px;
    color: var(--el-text-color-regular);
  }
}

.assets-section {
  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    
    h4 {
      margin: 0;
      color: var(--el-text-color-primary);
      font-size: 16px;
    }
  }
}

.matching-assets {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.matching-asset {
  background: var(--el-bg-color-overlay);
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    border-color: var(--el-color-primary);
    transform: translateY(-2px);
  }
  
  .asset-thumb {
    width: 100%;
    aspect-ratio: 1;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 8px;
    
    img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
  }
  
  .asset-info {
    .asset-name {
      font-size: 12px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    
    .asset-details {
      display: flex;
      justify-content: space-between;
      font-size: 10px;
      color: var(--el-text-color-secondary);
      margin-bottom: 4px;
    }
    
    .asset-tags {
      display: flex;
      gap: 2px;
      flex-wrap: wrap;
      
      .el-tag {
        height: 16px;
        line-height: 14px;
      }
    }
  }
}

.no-matching {
  grid-column: 1 / -1;
  text-align: center;
  padding: 40px 20px;
  color: var(--el-text-color-placeholder);
  
  p {
    margin: 16px 0 8px;
    font-size: 16px;
  }
  
  span {
    font-size: 14px;
  }
}

.create-folder-dialog {
  .cover-preview {
    margin-top: 8px;
    
    img {
      width: 100px;
      height: 100px;
      object-fit: cover;
      border-radius: 6px;
      border: 1px solid var(--el-border-color);
    }
    
    .el-button {
      margin-top: 8px;
    }
  }
  
  .rules-section {
    margin-top: 24px;
    
    h4 {
      margin: 0 0 16px;
      color: var(--el-text-color-primary);
    }
    
    .rule-item {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      
      .rule-content {
        flex: 1;
        display: flex;
        gap: 8px;
      }
    }
  }
}

.rule-edit-dialog {
  .el-form-item {
    margin-bottom: 16px;
  }
}

.settings-content {
  padding: 20px;
  
  .el-form-item {
    margin-bottom: 20px;
  }
  
  .form-tip {
    display: block;
    font-size: 12px;
    color: var(--el-text-color-placeholder);
    margin-top: 4px;
  }
}

// 响应式设计
@media (max-width: 1200px) {
  .smart-folders-list {
    width: 350px;
  }
  
  .matching-assets {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  }
}

@media (max-width: 768px) {
  .content {
    flex-direction: column;
  }
  
  .smart-folders-list {
    width: 100%;
    border-right: none;
    border-bottom: 1px solid var(--el-border-color-light);
  }
  
  .matching-assets {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  }
}
</style>