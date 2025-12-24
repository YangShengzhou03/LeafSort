<template>
  <div class="page-container">
    <div class="header-section">
      <h2>{{ title }}</h2>
      <div class="subtitle" v-if="subtitle">{{ subtitle }}</div>
    </div>

    <div class="materials-section">
      <div v-if="isLoading" class="loading-state">
        <el-skeleton :rows="6" animated />
      </div>

      <div v-else-if="error" class="error-state">
        <el-empty description="加载失败">
          <el-button type="primary" @click="$emit('retry')">重试</el-button>
        </el-empty>
      </div>

      <div v-else-if="materials.length === 0" class="empty-state">
        <div class="empty-container">
          <div class="empty-icon">
            <el-icon class="icon-large"><FolderChecked /></el-icon>
          </div>
          <h3 class="empty-title">暂无内容</h3>
          <p class="empty-description">{{ emptyText }}</p>
          <div class="empty-actions">
            <el-button v-if="emptyActionText" type="primary" @click="$emit('empty-action')">
              {{ emptyActionText }}
            </el-button>
            <el-button v-if="$slots.extra-actions" type="default">
              <slot name="extra-actions"></slot>
            </el-button>
          </div>
        </div>
      </div>

      <div v-else class="materials-grid">
        <MaterialCard
          v-for="material in materials"
          :key="material.id"
          :material="material"
          @favorite="$emit('favorite', material)"
          @preview="$emit('preview', material)"
          @edit="$emit('edit', material)"
        />
      </div>
    </div>
  </div>
</template>

<script>
import MaterialCard from './MaterialCard.vue'
import { FolderChecked } from '@element-plus/icons-vue'

export default {
  name: 'MaterialsGridPage',
  components: {
    MaterialCard,
    FolderChecked
  },
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    },
    emptyText: {
      type: String,
      default: '暂无素材'
    },
    emptyActionText: {
      type: String,
      default: ''
    },
    materials: {
      type: Array,
      default: () => []
    },
    isLoading: {
      type: Boolean,
      default: false
    },
    error: {
      type: [Object, String],
      default: null
    }
  },
  emits: ['favorite', 'preview', 'edit', 'retry', 'empty-action']
}
</script>

<style scoped>
.page-container {
  padding: 2rem;
  min-height: 100vh;
  background-color: var(--color-background);
}

.header-section {
  margin-bottom: 2rem;
}

.header-section h2 {
  color: var(--color-text-primary);
  margin: 0 0 0.5rem 0;
  font-size: 1.8rem;
  font-weight: 600;
}

.subtitle {
  color: var(--color-text-secondary);
  font-size: 1rem;
}

.materials-section {
  min-height: 400px;
}

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1.5rem;
}

.loading-state,
.error-state,
.empty-state {
  padding: 4rem 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-container {
  text-align: center;
  padding: 3rem 2rem;
  max-width: 420px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  border: 1px solid var(--border-light);
  box-shadow: var(--shadow-sm);
}

.empty-icon {
  margin-bottom: 1.5rem;
}

.icon-large {
  font-size: 64px;
  color: var(--text-tertiary);
  opacity: 0.6;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.empty-description {
  font-size: 1rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.empty-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}
</style>

