<template>
  <div class="smart-tag-panel">
    <div class="tag-search-section">
      <el-input
        v-model="searchQuery"
        placeholder="搜索或添加标签..."
        @keyup.enter="addNewTag"
        clearable
      >
        <template #append>
          <el-button @click="addNewTag">添加</el-button>
        </template>
      </el-input>
    </div>

    <div v-if="showSmartSuggestions" class="smart-suggestions">
      <div class="suggestion-header">
        <span class="suggestion-title">智能推荐</span>
        <el-button type="text" @click="applyAllSuggestions">全部应用</el-button>
      </div>
      <div class="suggestion-tags">
        <el-tag
          v-for="suggestion in smartSuggestions"
          :key="suggestion.tag"
          :type="getSuggestionType(suggestion.source)"
          closable
          @close="removeSuggestion(suggestion.tag)"
          @click="toggleTag(suggestion.tag)"
          :class="{ active: selectedTags.includes(suggestion.tag) }"
        >
          {{ suggestion.tag }}
          <el-tooltip :content="`置信度: ${(suggestion.confidence * 100).toFixed(0)}%`">
            <el-icon style="margin-left: 4px;"><InfoFilled /></el-icon>
          </el-tooltip>
        </el-tag>
      </div>
    </div>

    <div class="selected-tags-section">
      <div class="section-header">
        <span>已选标签</span>
        <span class="tag-count">{{ selectedTags.length }}</span>
      </div>
      <div class="selected-tags">
        <el-tag
          v-for="tag in selectedTags"
          :key="tag"
          type="primary"
          closable
          @close="removeTag(tag)"
        >
          {{ tag }}
        </el-tag>
        <div v-if="selectedTags.length === 0" class="empty-tags">
          暂无标签，请输入或选择标签
        </div>
      </div>
    </div>

    <div v-if="popularTags.length > 0" class="popular-tags-section">
      <div class="section-header">
        <span>热门标签</span>
      </div>
      <div class="popular-tags">
        <el-tag
          v-for="tag in popularTags"
          :key="tag.tag"
          :type="selectedTags.includes(tag.tag) ? 'primary' : 'info'"
          @click="toggleTag(tag.tag)"
        >
          {{ tag.tag }}
          <span class="tag-frequency">({{ tag.frequency }})</span>
        </el-tag>
      </div>
    </div>

    <div v-if="selectedMaterials.length > 1" class="batch-actions">
      <el-divider />
      <div class="batch-info">
        <span>批量操作: {{ selectedMaterials.length }} 个素材</span>
      </div>
      <div class="batch-buttons">
        <el-button type="primary" size="small" @click="applyToAll">
          应用到所有选中素材
        </el-button>
        <el-button type="success" size="small" @click="mergeTags">
          合并标签
        </el-button>
      </div>
    </div>

    <div class="action-buttons">
      <el-button type="primary" @click="saveTags">保存</el-button>
      <el-button @click="resetTags">重置</el-button>
      <el-button type="text" @click="generateSmartTags">重新生成推荐</el-button>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import tagManager from '../utils/tagManager'

export default {
  name: 'SmartTagPanel',
  components: {
    InfoFilled
  },
  props: {
    materials: {
      type: Array,
      default: () => []
    },
    selectedMaterials: {
      type: Array,
      default: () => []
    }
  },
  emits: ['tags-updated'],
  setup(props, { emit }) {
    const searchQuery = ref('')
    const selectedTags = ref([])
    const smartSuggestions = ref([])
    const popularTags = ref([])

    const showSmartSuggestions = computed(() => {
      return smartSuggestions.value.length > 0 && props.materials.length > 0
    })

    watch(() => props.selectedMaterials, (newMaterials) => {
      if (newMaterials.length > 0) {
        loadTagsForSelectedMaterials()
        generateSmartTags()
      }
    }, { immediate: true })

    onMounted(() => {
      loadPopularTags()
    })

    const loadTagsForSelectedMaterials = () => {
      if (props.selectedMaterials.length === 1) {
        const material = props.selectedMaterials[0]
        selectedTags.value = tagManager.getTags(material.id)
      } else {
        const commonTags = findCommonTags()
        selectedTags.value = commonTags
      }
    }

    const findCommonTags = () => {
      if (props.selectedMaterials.length === 0) return []
      
      const tagSets = props.selectedMaterials.map(material => 
        new Set(tagManager.getTags(material.id))
      )
      
      const commonTags = Array.from(tagSets[0]).filter(tag =>
        tagSets.every(tagSet => tagSet.has(tag))
      )
      
      return commonTags
    }

    const generateSmartTags = () => {
      if (props.materials.length === 0) return
      
      const material = props.materials[0]
      const existingTags = tagManager.getTags(material.id)
      
      smartSuggestions.value = tagManager.predictTags(
        material.name,
        material.type,
        existingTags
      )
    }

    const loadPopularTags = () => {
      popularTags.value = tagManager.getPopularTags(15)
    }

    const getSuggestionType = (source) => {
      const typeMap = {
        'filename': 'success',
        'filetype': 'warning',
        'similarity': 'info'
      }
      return typeMap[source] || 'info'
    }

    const toggleTag = (tag) => {
      const index = selectedTags.value.indexOf(tag)
      if (index > -1) {
        selectedTags.value.splice(index, 1)
      } else {
        selectedTags.value.push(tag)
      }
    }

    const addNewTag = () => {
      const tag = searchQuery.value.trim()
      if (tag && !selectedTags.value.includes(tag)) {
        selectedTags.value.push(tag)
        searchQuery.value = ''
      }
    }

    const removeTag = (tag) => {
      const index = selectedTags.value.indexOf(tag)
      if (index > -1) {
        selectedTags.value.splice(index, 1)
      }
    }

    const removeSuggestion = (tag) => {
      smartSuggestions.value = smartSuggestions.value.filter(s => s.tag !== tag)
    }

    const applyAllSuggestions = () => {
      smartSuggestions.value.forEach(suggestion => {
        if (!selectedTags.value.includes(suggestion.tag)) {
          selectedTags.value.push(suggestion.tag)
        }
      })
    }

    const applyToAll = () => {
      if (props.selectedMaterials.length === 0) return
      
      const materialIds = props.selectedMaterials.map(m => m.id)
      tagManager.addTagsBatch(selectedTags.value, materialIds)
      
      ElMessage.success(`已为 ${materialIds.length} 个素材添加标签`)
      emit('tags-updated')
    }

    const mergeTags = () => {
      ElMessage.info('标签合并功能开发中')
    }

    const saveTags = () => {
      if (props.selectedMaterials.length === 0) return
      
      const materialIds = props.selectedMaterials.map(m => m.id)
      materialIds.forEach(materialId => {
        const currentTags = tagManager.getTags(materialId)
        currentTags.forEach(tag => {
          tagManager.removeTag(tag, materialId)
        })
        
        selectedTags.value.forEach(tag => {
          tagManager.addTag(tag, materialId)
        })
      })
      
      ElMessage.success('标签保存成功')
      emit('tags-updated')
    }

    const resetTags = () => {
      selectedTags.value = []
      if (props.selectedMaterials.length === 1) {
        const material = props.selectedMaterials[0]
        selectedTags.value = tagManager.getTags(material.id)
      }
    }

    return {
      searchQuery,
      selectedTags,
      smartSuggestions,
      popularTags,
      showSmartSuggestions,
      getSuggestionType,
      toggleTag,
      addNewTag,
      removeTag,
      removeSuggestion,
      applyAllSuggestions,
      applyToAll,
      mergeTags,
      saveTags,
      resetTags,
      generateSmartTags
    }
  }
}
</script>

<style scoped>
.smart-tag-panel {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.tag-search-section {
  margin-bottom: 16px;
}

.smart-suggestions {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.suggestion-title {
  font-weight: 600;
  color: var(--text-primary);
}

.suggestion-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestion-tags .el-tag {
  cursor: pointer;
  transition: all 0.3s;
}

.suggestion-tags .el-tag.active {
  transform: scale(1.05);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.selected-tags-section,
.popular-tags-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 600;
  color: var(--text-primary);
}

.tag-count {
  background: var(--primary-color);
  color: var(--text-primary);
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 12px;
}

.selected-tags,
.popular-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  min-height: 32px;
}

.empty-tags {
  color: var(--text-tertiary);
  font-style: italic;
}

.tag-frequency {
  font-size: 12px;
  opacity: 0.7;
}

.batch-actions {
  margin: 16px 0;
}

.batch-info {
  margin-bottom: 12px;
  font-weight: 600;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}

.action-buttons {
  display: flex;
  gap: 8px;
  margin-top: 16px;
}

@media (max-width: 768px) {
  .smart-tag-panel {
    padding: var(--space-3);
    max-height: 350px;
  }
  
  .tag-search-section {
    margin-bottom: var(--space-3);
  }
  
  .smart-suggestions {
    margin-bottom: var(--space-3);
    padding: var(--space-3);
  }
  
  .suggestion-tags,
  .selected-tags,
  .popular-tags {
    gap: var(--space-2);
  }
  
  .batch-buttons {
    flex-direction: column;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}

@media (max-width: 480px) {
  .smart-tag-panel {
    padding: var(--space-2);
    max-height: 300px;
  }
  
  .suggestion-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }
  
  .section-header {
    font-size: var(--font-size-sm);
  }
}
</style>