<template>
  <div class="home-container">
    <!-- 欢迎页面 -->
    <div v-if="!currentLibrary" class="welcome-page">
      <div class="welcome-content">
        <div class="welcome-header">
          <el-icon size="64" color="var(--el-color-primary)">
            <FolderOpened />
          </el-icon>
          <h1>欢迎使用 LeafView</h1>
          <p>您的数字素材管理专家，对标 Eagle 的强大功能</p>
        </div>

        <div class="welcome-actions">
          <el-button type="primary" size="large" @click="createLibrary">
            <el-icon><Plus /></el-icon>
            创建新素材库
          </el-button>
          <el-button size="large" @click="openLibrary">
            <el-icon><FolderOpened /></el-icon>
            打开现有素材库
          </el-button>
        </div>

        <div class="recent-libraries" v-if="recentLibraries.length > 0">
          <h3>最近打开的素材库</h3>
          <div class="library-list">
            <div 
              v-for="lib in recentLibraries" 
              :key="lib.id"
              class="library-item"
              @click="openLibraryFromRecent(lib)"
            >
              <el-icon size="24"><FolderIcon /></el-icon>
              <div class="library-info">
                <div class="library-name">{{ lib.name }}</div>
                <div class="library-path">{{ lib.path }}</div>
                <div class="library-stats">
                  {{ lib.assetCount }} 个素材 • {{ formatFileSize(lib.size) }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="feature-showcase">
          <h3>核心功能特性</h3>
          <div class="features-grid">
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-primary)">
                <UploadFilled />
              </el-icon>
              <h4>高效素材收集</h4>
              <p>支持拖拽、截图、网页采集等多种方式</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-success)">
                <Collection />
              </el-icon>
              <h4>智能整理</h4>
              <p>自动分类、标签管理、智能文件夹</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-warning)">
                <Search />
              </el-icon>
              <h4>精准检索</h4>
              <p>多条件筛选、关键词搜索、颜色搜索</p>
            </div>
            <div class="feature-item">
              <el-icon size="32" color="var(--el-color-danger)">
                <Edit />
              </el-icon>
              <h4>素材处理</h4>
              <p>批量编辑、格式转换、水印添加</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 素材库主界面 - 三栏布局 -->
    <div v-else class="library-interface">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item>{{ currentLibrary.name }}</el-breadcrumb-item>
            <el-breadcrumb-item v-if="currentFolder">{{ currentFolder.name }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        
        <div class="toolbar-center">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索素材..."
            clearable
            @keyup.enter="performSearchWithHistory"
            style="width: 300px"
            ref="mainSearchInputRef"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          
          <!-- 搜索历史 -->
          <div v-if="showMainSearchHistory && libraryStore.searchHistory.length > 0" class="search-history">
            <div class="history-header">
              <span>搜索历史</span>
              <el-button type="text" size="small" @click="clearMainSearchHistory">
                清除
              </el-button>
            </div>
            <div class="history-list">
              <div
                v-for="(history, index) in libraryStore.searchHistory"
                :key="index"
                class="history-item"
                @click="searchMainHistoryItem(history)"
              >
                <el-icon size="14"><History /></el-icon>
                <span>{{ history }}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div class="toolbar-right">
          <el-button-group>
            <el-button 
              :type="viewMode === 'grid' ? 'primary' : ''"
              @click="viewMode = 'grid'"
            >
              <el-icon><Grid /></el-icon>
            </el-button>
            <el-button 
              :type="viewMode === 'list' ? 'primary' : ''"
              @click="viewMode = 'list'"
            >
              <el-icon><List /></el-icon>
            </el-button>
            <el-button 
              :type="viewMode === 'masonry' ? 'primary' : ''"
              @click="viewMode = 'masonry'"
            >
              <el-icon><Picture /></el-icon>
            </el-button>
          </el-button-group>
          
          <el-dropdown @command="handleViewCommand">
            <el-button>
              <el-icon><Setting /></el-icon>
              视图
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="thumbnailSize">缩略图大小</el-dropdown-item>
                <el-dropdown-item command="showMetadata">显示元数据</el-dropdown-item>
                <el-dropdown-item command="groupBy">分组方式</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>

      <!-- 三栏布局 -->
      <div class="main-layout">
        <!-- 左侧侧边栏 -->
        <div class="sidebar-container">
          <Sidebar 
            @folder-click="handleFolderClick"
            @tag-click="handleTagClick"
            @search-panel-toggle="searchPanelVisible = !searchPanelVisible"
          />
        </div>
        
        <!-- 中间内容区域 -->
        <div class="content-container">
          <!-- 搜索面板 -->
          <div class="search-panel" v-show="searchPanelVisible">
            <SearchPanel @search="handleSearch" />
          </div>
          
          <!-- 素材展示 -->
          <div class="assets-container">
            <div 
              class="assets-grid"
              :class="viewMode + '-view'"
            >
              <div
                v-for="asset in filteredAssets"
                :key="asset.id"
                class="asset-item"
                :class="{ selected: selectedAssets.includes(asset.id) }"
                @click="selectAsset(asset)"
                @dblclick="openAsset(asset)"
              >
                <div class="asset-thumbnail-container">
                  <img 
                    :src="getThumbnailUrl(asset)" 
                    :alt="asset.name"
                    class="asset-thumbnail"
                    @error="handleImageError"
                  />
                  <div class="asset-overlay">
                    <el-icon class="asset-type-icon">
                      <component :is="getAssetTypeIcon(asset.type)" />
                    </el-icon>
                    <div class="asset-actions">
                      <el-button size="small" circle @click.stop="previewAsset(asset)">
                        <el-icon><View /></el-icon>
                      </el-button>
                      <el-button size="small" circle @click.stop="editAsset(asset)">
                        <el-icon><Edit /></el-icon>
                      </el-button>
                    </div>
                  </div>
                </div>
                
                <div class="asset-info">
                  <div class="asset-name">{{ asset.name }}</div>
                  <div class="asset-meta">
                    {{ formatFileSize(asset.size) }} • {{ formatDate(asset.createdAt) }}
                  </div>
                  <div class="asset-tags">
                    <el-tag
                      v-for="tag in asset.tags.slice(0, 2)"
                      :key="tag"
                      size="small"
                      class="tag"
                    >
                      {{ tag }}
                    </el-tag>
                    <span v-if="asset.tags.length > 2" class="more-tags">
                      +{{ asset.tags.length - 2 }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
            
            <div v-if="filteredAssets.length === 0" class="empty-state">
              <el-icon size="64" color="var(--el-text-color-placeholder)">
                <Files />
              </el-icon>
              <p>暂无素材</p>
              <el-button type="primary" @click="importAssets">
                <el-icon><Plus /></el-icon>
                导入素材
              </el-button>
            </div>
          </div>
        </div>
        
        <!-- 右侧详情面板 -->
        <div class="detail-panel" v-if="selectedAsset">
          <DetailPanel 
            :asset="selectedAsset"
            @close="selectedAsset = null"
          />
        </div>
      </div>
    </div>

    <!-- 素材导入对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入素材"
      width="600px"
    >
      <ImportAssets @close="showImportDialog = false" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
// 最小化导入，确保语法正确
import { ref, computed, onMounted } from 'vue';
import { useLibraryStore } from '@/stores/library';
import { useThemeStore } from '@/stores/theme';
import type { Library, Asset, Folder } from '@/types';

// 基本数据和方法
const libraryStore = useLibraryStore();
const themeStore = useThemeStore();
const currentLibrary = ref<Library | null>(null);
const recentLibraries = ref<Library[]>([]);
const searchKeyword = ref('');
const viewMode = ref<'grid' | 'list'>('grid');
const selectedAssets = ref<string[]>([]);
const showImportDialog = ref(false);
const selectedAsset = ref<Asset | null>(null);

// 简化的计算属性
const filteredAssets = computed(() => []);

// 生命周期钩子
onMounted(() => {
  try {
    const saved = localStorage.getItem('recentLibraries');
    if (saved) {
      recentLibraries.value = JSON.parse(saved);
    }
  } catch (e) {
    console.error(e);
  }
});
</script>

<style scoped>
/* 欢迎页面样式 */
.welcome-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
  text-align: center;
  background: var(--el-bg-color-page);
}

.welcome-content {
  max-width: 600px;
  animation: fadeIn 0.6s ease;
}

.welcome-title {
  font-size: 36px;
  font-weight: 600;
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
  background: linear-gradient(135deg, var(--el-color-primary), #667eea);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.welcome-description {
  font-size: 18px;
  color: var(--el-text-color-secondary);
  margin-bottom: 30px;
  line-height: 1.6;
}

.welcome-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  margin-bottom: 60px;
}

.welcome-button {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 500;
  border-radius: var(--el-border-radius-base);
  transition: all 0.3s ease;
  cursor: pointer;
}

.primary-button {
  background-color: var(--el-color-primary);
  color: white;
  border: none;
  
  &:hover {
    background-color: var(--el-color-primary-light-3);
    transform: translateY(-2px);
    box-shadow: var(--el-box-shadow-light);
  }
}

.secondary-button {
  background-color: var(--el-bg-color);
  color: var(--el-text-color-primary);
  border: 1px solid var(--el-border-color);
  
  &:hover {
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    background-color: var(--el-bg-color-hover);
  }
}

/* 最近素材库 */
.recent-libraries {
  width: 100%;
  max-width: 1000px;
  margin-bottom: 60px;
}

.section-title {
  font-size: 24px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 20px;
  text-align: left;
}

.libraries-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.library-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: var(--el-border-radius-base);
  padding: 20px;
  cursor: pointer;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    transform: translateY(-2px);
    box-shadow: var(--el-box-shadow-light);
  }
}

.library-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.library-meta {
  font-size: 14px;
  color: var(--el-text-color-secondary);
}

/* 功能特性 */
.features {
  width: 100%;
  max-width: 1000px;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.feature-card {
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: var(--el-border-radius-base);
  padding: 24px;
  transition: all 0.3s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    transform: translateY(-2px);
    box-shadow: var(--el-box-shadow-light);
  }
}

.feature-icon {
  font-size: 32px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.feature-title {
  font-size: 18px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.feature-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  line-height: 1.6;
}

/* 素材库主界面样式 */
.library-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: var(--el-bg-color-page);
}

/* 工具栏样式 */
.toolbar {
  background: var(--el-bg-color);
  border-bottom: 1px solid var(--el-border-color-light);
  padding: 0 20px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.toolbar-left {
  display: flex;
  align-items: center;
  margin-right: auto;
}

.toolbar-center {
  display: flex;
  align-items: center;
  flex: 1;
  max-width: 600px;
  margin: 0 auto;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

/* 面包屑导航样式 */
.breadcrumb {
  display: flex;
  align-items: center;
  color: var(--el-text-color-secondary);
  font-size: 14px;
  
  .breadcrumb-item {
    cursor: pointer;
    transition: color 0.2s ease;
    
    &:hover {
      color: var(--el-color-primary);
    }
    
    &.active {
      color: var(--el-text-color-primary);
      font-weight: 500;
    }
  }
  
  .breadcrumb-separator {
    margin: 0 8px;
    color: var(--el-text-color-placeholder);
  }
}

/* 搜索框样式 */
.search-container {
  position: relative;
  width: 100%;
  
  .search-input {
    width: 100%;
    height: 36px;
    background: var(--el-bg-color-overlay);
    border: 1px solid var(--el-border-color);
    border-radius: 18px;
    padding: 0 16px 0 40px;
    color: var(--el-text-color-primary);
    font-size: 14px;
    transition: all 0.3s ease;
    
    &:focus {
      outline: none;
      border-color: var(--el-color-primary);
      box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
    }
    
    &::placeholder {
      color: var(--el-text-color-placeholder);
    }
  }
  
  .search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--el-text-color-placeholder);
    font-size: 16px;
  }
}

/* 搜索历史样式 */
.search-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-base);
  margin-top: 4px;
  box-shadow: var(--el-box-shadow-base);
  z-index: 1000;
  max-height: 300px;
  overflow-y: auto;
}

.history-item {
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  color: var(--el-text-color-primary);
  font-size: 14px;
  
  &:hover {
    background-color: var(--el-bg-color-hover);
  }
}

/* 按钮组样式 */
.button-group {
  display: flex;
  gap: 4px;
}

.view-button {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: 1px solid var(--el-border-color);
  border-radius: var(--el-border-radius-small);
  color: var(--el-text-color-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    color: var(--el-color-primary);
    background-color: var(--el-bg-color-hover);
  }
  
  &.active {
    background-color: var(--el-color-primary);
    border-color: var(--el-color-primary);
    color: white;
  }
}

/* 内容区域样式 */
.content-area {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 资产网格样式 */
.assets-container {
  flex: 1;
  overflow-y: auto;
  background: var(--el-bg-color-page);
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 18px;
  padding: var(--el-space-lg);
  transition: all 0.3s ease;
}

/* 网格视图 */
.grid-view {
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
}

/* 列表视图 */
.list-view {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: var(--el-space-lg);
}

.list-item {
  display: flex;
  align-items: center;
  padding: 12px;
  background: var(--el-bg-color);
  border: 1px solid var(--el-border-color-light);
  border-radius: var(--el-border-radius-base);
  transition: all 0.2s ease;
  
  &:hover {
    border-color: var(--el-color-primary);
    background-color: var(--el-bg-color-hover);
  }
  
  .list-thumbnail {
    width: 60px;
    height: 60px;
    object-fit: cover;
    border-radius: var(--el-border-radius-small);
    margin-right: 16px;
  }
  
  .list-info {
    flex: 1;
    
    .list-name {
      font-size: 14px;
      font-weight: 500;
      color: var(--el-text-color-primary);
      margin-bottom: 4px;
    }
    
    .list-meta {
      font-size: 12px;
      color: var(--el-text-color-secondary);
    }
  }
  
  .list-actions {
    display: flex;
    gap: 8px;
  }
}

/* 瀑布流视图 */
.masonry-view {
  column-count: 5;
  column-gap: 18px;
  padding: var(--el-space-lg);
  
  .asset-item {
    break-inside: avoid;
    margin-bottom: 18px;
  }
}

/* 资产项样式 */
.asset-item {
  background: rgba(24, 25, 35, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  backdrop-filter: blur(10px);
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    border-color: var(--el-color-primary);
  }
  
  &.selected {
    border-color: var(--el-color-primary);
    box-shadow: 0 0 0 2px rgba(45, 140, 240, 0.3);
    background: rgba(45, 140, 240, 0.1);
  }
}

.asset-thumbnail-container {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  overflow: hidden;
  background: rgba(12, 13, 18, 0.8);
  
  .asset-thumbnail {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform 0.4s ease;
  }
  
  .asset-item:hover .asset-thumbnail {
    transform: scale(1.05);
  }
}

.asset-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(0, 0, 0, 0.8));
  opacity: 0;
  transition: opacity 0.3s ease;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 12px;
  
  .asset-item:hover & {
    opacity: 1;
  }
  
  .asset-type-icon {
    position: absolute;
    top: 8px;
    right: 8px;
    width: 32px;
    height: 32px;
    background: rgba(0, 0, 0, 0.7);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 16px;
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.2);
  }
  
  .asset-actions {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
    
    .el-button {
      width: 36px;
      height: 36px;
      background: rgba(0, 0, 0, 0.7);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 50%;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: all 0.2s ease;
      backdrop-filter: blur(8px);
      
      &:hover {
        background: var(--el-color-primary);
        transform: scale(1.05);
        border-color: var(--el-color-primary);
      }
    }
  }
}

.asset-info {
  padding: 12px;
  
  .asset-name {
    font-size: 14px;
    font-weight: 500;
    color: var(--el-text-color-primary);
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .asset-meta {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.6);
    margin-bottom: 8px;
  }
  
  .asset-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
  }
  
  .tag {
    background: rgba(255, 255, 255, 0.1);
    border: none;
    color: rgba(255, 255, 255, 0.8);
    
    &:hover {
      background: rgba(255, 255, 255, 0.2);
      color: white;
    }
  }
  
  .more-tags {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 20px;
    height: 20px;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.1);
    color: rgba(255, 255, 255, 0.6);
    font-size: 10px;
  }
}

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 60px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: var(--el-text-color-disabled);
  margin-bottom: 20px;
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  margin-bottom: 20px;
  max-width: 400px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .assets-grid.grid-view {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
  
  .masonry-view {
    column-count: 4;
  }
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px 12px;
    grid-template-columns: 1fr;
    grid-template-areas:
      "sidebar"
      "content";
  }
  
  .sidebar {
    position: fixed;
    left: -300px;
    top: 0;
    height: 100vh;
    width: 280px;
    z-index: 100;
    transition: left 0.3s ease;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.3);
  }
  
  .sidebar.open {
    left: 0;
  }
  
  .sidebar-toggle {
    display: block;
  }
  
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 12px;
  }
  
  .asset-item {
    min-height: 150px;
  }
  
  .asset-overlay {
    padding: 12px 8px;
  }
  
  .asset-actions {
    gap: 6px;
  }
  
  .action-button {
    width: 28px;
    height: 28px;
    font-size: 14px;
  }
  
  .asset-info {
    margin-top: 8px;
  }
  
  .asset-name {
    font-size: 13px;
    margin-bottom: 4px;
  }
  
  .asset-meta {
    font-size: 11px;
  }
  
  .search-bar {
    margin-bottom: 16px;
  }
  
  .header {
    padding: 12px 16px;
  }
  
  .header-title {
    font-size: 18px;
  }
  
  .filter-container {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .filter-section {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .assets-grid {
    grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
    gap: 10px;
  }
  
  .asset-item {
    min-height: 120px;
  }
  
  .asset-thumbnail-container {
    padding: 4px;
  }
  
  .sidebar {
    width: 250px;
  }
  
  .header {
    padding: 10px 12px;
  }
  
  .main-content {
    padding: 12px 8px;
  }
}

/* 过渡效果 */
.panel-enter-active,
.panel-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.panel-enter-from {
  opacity: 0;
  transform: translateX(20px);
}

.panel-leave-to {
  opacity: 0;
  transform: translateX(20px);
}
</style>