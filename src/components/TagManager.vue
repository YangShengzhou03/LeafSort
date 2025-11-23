<template>
  <div class="tag-manager">
    <!-- 标签列表 -->
    <div class="tags-container">
      <div
        v-for="tag in tags"
        :key="tag.id"
        :class="['tag-item', { 'selected': selectedTags.includes(tag.id) }]"
        :style="{ backgroundColor: tag.color + '20', borderColor: tag.color }"
        @click="toggleTagSelection(tag.id)"
      >
        <span class="tag-name">{{ tag.name }}</span>
        <span class="tag-count">{{ getTagCount(tag.id) }}</span>
        <div class="tag-actions">
          <el-button
            type="text"
            size="small"
            icon="Edit"
            @click.stop="editTag(tag)"
            title="编辑标签"
          />
          <el-button
            type="text"
            size="small"
            icon="Delete"
            @click.stop="confirmDeleteTag(tag.id)"
            title="删除标签"
          />
        </div>
      </div>

      <!-- 添加标签按钮 -->
      <div class="add-tag-btn" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        添加标签
      </div>
    </div>

    <!-- 创建/编辑标签对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingTag ? '编辑标签' : '创建标签'"
      width="400px"
      destroy-on-close
    >
      <el-form :model="tagForm" label-width="80px">
        <el-form-item label="标签名称" required>
          <el-input v-model="tagForm.name" placeholder="请输入标签名称" />
        </el-form-item>
        <el-form-item label="标签颜色" required>
          <el-color-picker v-model="tagForm.color" show-alpha />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateDialog = false">取消</el-button>
          <el-button type="primary" @click="saveTag">确定</el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog
      v-model="showDeleteDialog"
      title="删除标签"
      width="300px"
      destroy-on-close
    >
      <p>确定要删除标签"{{ getTagNameToDelete }}"吗？</p>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showDeleteDialog = false">取消</el-button>
          <el-button type="danger" @click="deleteTag">删除</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

// Props
const props = defineProps<{
  tags: Array<{ id: string; name: string; color: string }>
  selectedTags?: string[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'update:selectedTags', tags: string[]): void
  (e: 'create', tag: { name: string; color: string }): void
  (e: 'update', tag: { id: string; name: string; color: string }): void
  (e: 'delete', tagId: string): void
}>()

// 响应式数据
const selectedTags = ref<string[]>(props.selectedTags || [])
const showCreateDialog = ref(false)
const showDeleteDialog = ref(false)
const editingTag = ref<{ id: string; name: string; color: string } | null>(null)
const tagForm = ref({
  name: '',
  color: '#409eff'
})
const tagToDelete = ref('')

// 计算属性
const getTagNameToDelete = computed(() => {
  const tag = props.tags.find(t => t.id === tagToDelete.value)
  return tag ? tag.name : ''
})

// 监听props变化
watch(() => props.selectedTags, (newVal) => {
  if (newVal) {
    selectedTags.value = [...newVal]
  }
}, { deep: true })

// 方法
const toggleTagSelection = (tagId: string) => {
  const index = selectedTags.value.indexOf(tagId)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tagId)
  }
  emit('update:selectedTags', [...selectedTags.value])
}

const editTag = (tag: { id: string; name: string; color: string }) => {
  editingTag.value = { ...tag }
  tagForm.value = { ...tag }
  showCreateDialog.value = true
}

const confirmDeleteTag = (tagId: string) => {
  tagToDelete.value = tagId
  showDeleteDialog.value = true
}

const saveTag = () => {
  if (!tagForm.value.name.trim()) {
    ElMessage.warning('标签名称不能为空')
    return
  }

  if (editingTag.value) {
    // 更新标签
    emit('update', {
      id: editingTag.value.id,
      name: tagForm.value.name.trim(),
      color: tagForm.value.color
    })
    ElMessage.success('标签更新成功')
  } else {
    // 创建新标签
    emit('create', {
      name: tagForm.value.name.trim(),
      color: tagForm.value.color
    })
    ElMessage.success('标签创建成功')
  }

  // 重置表单并关闭对话框
  resetForm()
  showCreateDialog.value = false
}

const deleteTag = () => {
  emit('delete', tagToDelete.value)
  ElMessage.success('标签删除成功')
  showDeleteDialog.value = false
  
  // 如果删除的标签在选中列表中，移除它
  const index = selectedTags.value.indexOf(tagToDelete.value)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
    emit('update:selectedTags', [...selectedTags.value])
  }
  
  tagToDelete.value = ''
}

const resetForm = () => {
  tagForm.value = {
    name: '',
    color: '#409eff'
  }
  editingTag.value = null
}

// 获取标签使用次数（需要在父组件中实现实际的计数逻辑）
const getTagCount = (tagId: string): number => {
  // 这里返回模拟数据，实际应该从父组件传入或通过store获取
  return Math.floor(Math.random() * 20) + 1
}
</script>

<style scoped>
.tag-manager {
  width: 100%;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 15px;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 13px;
  position: relative;
}

.tag-item:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.tag-item.selected {
  transform: scale(0.98);
}

.tag-name {
  font-weight: 500;
}

.tag-count {
  margin-left: 6px;
  font-size: 11px;
  opacity: 0.8;
  background-color: rgba(0, 0, 0, 0.1);
  padding: 1px 6px;
  border-radius: 10px;
}

.tag-actions {
  display: none;
  margin-left: 6px;
}

.tag-item:hover .tag-actions {
  display: flex;
  gap: 4px;
}

.add-tag-btn {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  border: 1px dashed #409eff;
  color: #409eff;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.add-tag-btn:hover {
  background-color: #ecf5ff;
}

.add-tag-btn .el-icon {
  margin-right: 4px;
}
</style>