<template>
  <div class="tag-editor">
    <div class="editor-header">
      <h3>标签</h3>
      <el-button type="primary" size="small" @click="showTagManager = true">
        管理标签
      </el-button>
    </div>
    
    <!-- 当前资产的标签 -->
    <div class="asset-tags" v-if="assetTags.length > 0">
      <div
        v-for="tag in assetTags"
        :key="tag.id"
        :class="['tag-chip']"
        :style="{ backgroundColor: tag.color + '20', borderColor: tag.color }"
      >
        <span class="tag-name">{{ tag.name }}</span>
        <el-button
          type="text"
          size="small"
          icon="Close"
          @click="removeTag(tag.id)"
          class="remove-tag-btn"
          title="移除标签"
        />
      </div>
    </div>
    <div v-else class="no-tags">
      <p>暂无标签，点击下方添加</p>
    </div>
    
    <!-- 可用标签选择器 -->
    <div class="available-tags">
      <div
        v-for="tag in availableTags"
        :key="tag.id"
        :class="['tag-option', { 'selected': assetTagIds.includes(tag.id) }]"
        :style="{ backgroundColor: tag.color + '20', borderColor: tag.color }"
        @click="toggleTag(tag.id)"
      >
        <el-icon v-if="assetTagIds.includes(tag.id)"><Check /></el-icon>
        <span class="tag-name">{{ tag.name }}</span>
      </div>
    </div>
    
    <!-- 标签管理对话框 -->
    <el-dialog
      v-model="showTagManager"
      title="标签管理"
      width="600px"
      destroy-on-close
    >
      <TagManager
        :tags="allTags"
        @create="handleCreateTag"
        @update="handleUpdateTag"
        @delete="handleDeleteTag"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ElMessage } from 'element-plus'
import TagManager from './TagManager.vue'
import type { Tag } from '../types'

// Props
const props = defineProps<{
  assetId: string
  assetTags: Tag[]
  allTags: Tag[]
}>()

// Emits
const emit = defineEmits<{
  (e: 'addTag', assetId: string, tagId: string): void
  (e: 'removeTag', assetId: string, tagId: string): void
  (e: 'createTag', tag: Omit<Tag, 'id'>): void
  (e: 'updateTag', tag: Tag): void
  (e: 'deleteTag', tagId: string): void
}>()

// 响应式数据
const showTagManager = ref(false)

// 计算属性
const assetTagIds = computed(() => props.assetTags.map(tag => tag.id))

// 可用标签（排除已添加到当前资产的标签）
const availableTags = computed(() => {
  return props.allTags.filter(tag => !assetTagIds.value.includes(tag.id))
})

// 方法
const toggleTag = (tagId: string) => {
  if (assetTagIds.value.includes(tagId)) {
    removeTag(tagId)
  } else {
    addTag(tagId)
  }
}

const addTag = (tagId: string) => {
  emit('addTag', props.assetId, tagId)
  ElMessage.success('标签添加成功')
}

const removeTag = (tagId: string) => {
  emit('removeTag', props.assetId, tagId)
  ElMessage.success('标签移除成功')
}

const handleCreateTag = (tag: Omit<Tag, 'id'>) => {
  emit('createTag', tag)
}

const handleUpdateTag = (tag: Tag) => {
  emit('updateTag', tag)
}

const handleDeleteTag = (tagId: string) => {
  emit('deleteTag', tagId)
}
</script>

<style scoped>
.tag-editor {
  padding: 16px 0;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.editor-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 500;
}

.asset-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 16px;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: 16px;
  border: 1px solid #e0e0e0;
  font-size: 13px;
  transition: all 0.2s ease;
}

.tag-chip:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.remove-tag-btn {
  margin-left: 4px;
  padding: 0;
  font-size: 12px;
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-tags {
  margin-bottom: 16px;
  padding: 12px;
  background-color: rgba(0, 0, 0, 0.02);
  border-radius: 4px;
  text-align: center;
  color: #606266;
  font-size: 14px;
}

.available-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-option {
  display: inline-flex;
  align-items: center;
  padding: 6px 12px;
  border-radius: 16px;
  border: 1px dashed #e0e0e0;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.2s ease;
}

.tag-option:hover {
  background-color: rgba(0, 0, 0, 0.04);
}

.tag-option.selected {
  border-style: solid;
  background-color: rgba(0, 0, 0, 0.06);
}

.tag-option .el-icon {
  margin-right: 4px;
  font-size: 12px;
}
</style>