<template>
  <div class="home-container">
    <!-- 主界面 - 三栏布局 -->
    <div class="library-interface">
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
          <el-button type="primary" @click="selectFolder">
            <el-icon><FolderOpen /></el-icon>
            选择文件夹
          </el-button>
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

/* 空状态样式 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 60px 20px;
  text-align: center;
  background-color: #0a0b0f;
}

.empty-icon {
  font-size: 64px;
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 20px;
}

.empty-title {
  font-size: 18px;
  font-weight: 500;
  color: #ffffff;
  margin-bottom: 8px;
}

.empty-description {
  font-size: 14px;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 20px;
  max-width: 400px;
}

      <!-- 三栏布局 -->
        <div class="main-layout">
          <!-- 左侧侧边栏 -->
          <div class="sidebar-container">
            <div class="sidebar">
              <!-- 侧边栏导航 -->
              <div class="sidebar-nav">
                <div class="nav-section">
                  <div class="nav-title">分类</div>
                  <div class="nav-item active">
                    <el-icon><Collection /></el-icon>
                    <span>音频</span>
                    <span class="item-count">285</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Picture /></el-icon>
                    <span>图片</span>
                    <span class="item-count">143</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><VideoPlay /></el-icon>
                    <span>视频</span>
                    <span class="item-count">34</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Document /></el-icon>
                    <span>文档</span>
                    <span class="item-count">117</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Collection /></el-icon>
                    <span>收藏夹</span>
                    <span class="item-count">20</span>
                  </div>
                </div>
              </div>
              <div class="nav-section">
                  <div class="nav-title">标签</div>
                  <div class="nav-item">
                    <el-icon><Promotion /></el-icon>
                    <span>流行</span>
                    <span class="item-count">275</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Headset /></el-icon>
                    <span>背景音乐</span>
                    <span class="item-count">113</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Sunny /></el-icon>
                    <span>轻松</span>
                    <span class="item-count">117</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Mute /></el-icon>
                    <span>环境音</span>
                    <span class="item-count">129</span>
                  </div>
                  <div class="nav-item">
                    <el-icon><Star /></el-icon>
                    <span>标记 1</span>
                    <span class="item-count">108</span>
                  </div>
                </div>
            </div>
          </div>
          
          <!-- 中间内容区域 -->
          <div class="content-container">
            <!-- 素材展示 -->
            <div class="assets-container">
              <!-- 空状态 - 无素材库时显示 -->
              <div class="empty-state" v-if="!hasAssets">
                <div class="empty-icon">
                  <el-icon><Folder /></el-icon>
                </div>
                <h3 class="empty-title">选择素材库文件夹</h3>
                <p class="empty-description">
                  您还没有选择素材库文件夹。请点击上方的"选择文件夹"按钮，导入您的素材库。
                </p>
                <el-button type="primary" @click="selectFolder">
                  <el-icon><Folder /></el-icon> 选择文件夹
                </el-button>
              </div>
              <div v-else class="assets-grid">
                <div
                  v-for="asset in filteredAssets"
                  :key="asset.id"
                  class="asset-item"
                  :class="{ selected: selectedAsset && selectedAsset.id === asset.id }"
                  @click="selectAsset(asset)"
                  @dblclick="openAsset(asset)"
                >
                  <div class="asset-thumbnail-container">
                    <!-- 音频文件特殊处理 -->
                    <template v-if="asset.type === 'audio'">
                      <div class="audio-visualizer">
                        <div class="wave-container">
                          <div v-for="(bar, index) in generateWaveformBars(asset.id)" :key="index" 
                               class="waveform-bar" 
                               :style="{ height: bar + '%', animationDelay: index * 0.08 + 's' }"></div>
                        </div>
                      </div>
                    </template>
                    <!-- 图片类型文件 -->
                    <template v-else>
                      <img 
                        :src="asset.thumbnail" 
                        :alt="asset.name"
                        class="asset-thumbnail"
                      />
                    </template>
                    <div class="asset-overlay">
                      <div class="asset-actions">
                        <el-button size="small" circle @click.stop="previewAsset(asset)">
                          <el-icon><Play /></el-icon>
                        </el-button>
                        <el-button size="small" circle @click.stop="editAsset(asset)">
                          <el-icon><Edit /></el-icon>
                        </el-button>
                      </div>
                    </div>
                  </div>
                  
                  <div class="asset-info">
                    <div class="asset-name">{{ asset.name }}</div>
                    <!-- 音频元信息 -->
                    <div v-if="asset.type === 'audio'" class="asset-meta">
                      <span style="display: inline-block; min-width: 55px;">{{ asset.metadata.duration }}</span>
                      <span>{{ asset.metadata.format }}/BPM:{{ asset.metadata.bpm }}</span>
                    </div>
                    <!-- 图片元信息 -->
                    <div v-else class="asset-meta">
                      {{ asset.size }} • {{ asset.metadata.resolution }}
                    </div>
                    
                    <!-- 音频波形显示 - 详细波形 -->
                    <div v-if="asset.type === 'audio'" class="audio-waveform">
                      <div v-for="(bar, index) in generateDetailedWaveform(asset.id)" :key="index" 
                           class="detailed-waveform-bar" 
                           :style="{ height: bar + '%', animationDelay: index * 0.05 + 's' }"></div>
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
            </div>
          </div>
          
          <!-- 右侧详情面板 -->
          <div class="detail-panel" v-if="selectedAsset">
            <div class="detail-header">
              <h3>{{ selectedAsset.name }}</h3>
              <el-button size="small" type="text" @click="selectedAsset = null">
                <el-icon><Close /></el-icon>
              </el-button>
            </div>
            <div class="detail-content">
              <!-- 预览区域 -->
              <div class="detail-preview">
                <template v-if="selectedAsset.type === 'audio'">
                  <div class="audio-player">
                    <div class="audio-wave-container">
                      <div v-for="(bar, index) in generateWaveformBars(selectedAsset.id)" :key="index" 
                           class="waveform-bar large" 
                           :style="{ height: bar + '%', animationDelay: index * 0.08 + 's' }"></div>
                    </div>
                    <div class="player-controls">
                      <el-button size="large" circle>
                        <el-icon><Play /></el-icon>
                      </el-button>
                      <div class="progress-bar">
                        <div class="progress-fill" style="width: 30%"></div>
                      </div>
                      <span class="time-display">01:15 / {{ selectedAsset.metadata.duration }}</span>
                    </div>
                  </div>
                </template>
                <template v-else>
                  <img 
                    :src="selectedAsset.thumbnail" 
                    :alt="selectedAsset.name"
                    class="detail-image"
                  />
                </template>
              </div>
              
              <!-- 信息区域 -->
              <div class="detail-info">
                <div class="info-group">
                  <div class="info-label">类型</div>
                  <div class="info-value">{{ selectedAsset.type === 'audio' ? '音频' : '图片' }}</div>
                </div>
                <div class="info-group">
                  <div class="info-label">文件</div>
                  <div class="info-value">{{ selectedAsset.metadata.format }}</div>
                </div>
                <div class="info-group">
                  <div class="info-label">时长</div>
                  <div class="info-value">{{ selectedAsset.metadata.duration || '-' }}</div>
                </div>
                <div class="info-group">
                  <div class="info-label">尺寸</div>
                  <div class="info-value">{{ selectedAsset.metadata.resolution || '-' }}</div>
                </div>
                <div class="info-group">
                  <div class="info-label">BPM</div>
                  <div class="info-value">{{ selectedAsset.metadata.bpm || '-' }}</div>
                </div>
                <div class="info-group">
                  <div class="info-label">创建时间</div>
                  <div class="info-value">{{ selectedAsset.createdAt }}</div>
                </div>
                
                <!-- 标签编辑 -->
                <div class="tags-section">
                  <div class="section-header">
                    <span>标签</span>
                    <el-button size="small" type="primary" circle>
                      <el-icon><Plus /></el-icon>
                    </el-button>
                  </div>
                  <div class="tags-container">
                    <el-tag
                      v-for="tag in selectedAsset.tags"
                      :key="tag"
                      size="small"
                      closable
                      class="detail-tag"
                    >
                      {{ tag }}
                    </el-tag>
                  </div>
                </div>
                
                <!-- 评分 -->
                <div class="rating-section">
                  <div class="section-header">
                    <span>评分</span>
                  </div>
                  <div class="rating-stars">
                    <el-rate v-model="selectedAsset.rating" :max="5" show-score disabled />
                  </div>
                </div>
                
                <!-- 操作按钮 -->
                <div class="action-buttons">
                  <el-button type="primary" size="small">
                    <el-icon><Download /></el-icon>
                    下载
                  </el-button>
                  <el-button size="small">
                    <el-icon><Share /></el-icon>
                    分享
                  </el-button>
                </div>
              </div>
            </div>
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
import { ref, computed } from 'vue';
import {
  Collection,
  Document,
  Folder,
  Headset,
  Menu,
  Message,
  Mute,
  Promotion,
  Search,
  Settings,
  Star,
  Sunny,
  User,
  VideoPlay,
  Edit,
  Close,
  Download,
  Share,
  Plus,
  X
} from '@element-plus/icons-vue';

// 基本数据
const searchKeyword = ref('');
const selectedAsset = ref(null);
// 基本数据
const sidebarOpen = ref(true); // 侧边栏默认打开
const hasAssets = ref(true); // 默认显示模拟素材，实际项目中应根据是否有导入的素材库设置

// 切换侧边栏
function toggleSidebar() {
  sidebarOpen.value = !sidebarOpen.value;
}

// 选择文件夹函数
function selectFolder() {
  ElMessage.info('选择文件夹功能已触发');
  // 实际项目中这里会调用文件系统API选择文件夹
  // 选择成功后设置hasAssets.value = true
}

// 生成音频波形数据的函数 - 改进以更接近原型图的波形效果
function generateWaveformBars(assetId) {
  // 基于assetId生成伪随机但一致的波形数据
  const seed = parseInt(assetId) || 1;
  const bars = [];
  for (let i = 0; i < 20; i++) {
    // 调整算法以产生更自然的波形效果
    const value = ((Math.sin(seed + i * 0.3) * 0.7 + Math.sin(seed + i * 0.12) * 0.3 + 1) / 2) * 70 + 15;
    bars.push(Math.floor(value));
  }
  return bars;
}

// 生成详细波形数据 - 改进以更接近原型图的波形效果
function generateDetailedWaveform(assetId) {
  const seed = parseInt(assetId) || 1;
  const bars = [];
  for (let i = 0; i < 30; i++) {
    // 调整算法以产生更自然的波形效果
    const value = ((Math.sin(seed + i * 0.2) * 0.6 + Math.sin(seed + i * 0.08) * 0.4 + 1) / 2) * 60 + 10;
    bars.push(Math.floor(value));
  }
  return bars;
}

// 素材操作函数
function selectAsset(asset) {
  selectedAsset.value = asset;
}

function openAsset(asset) {
  // 打开素材的逻辑
  console.log('Open asset:', asset.name);
}

function previewAsset(asset) {
  // 预览素材的逻辑
  console.log('Preview asset:', asset.name);
}

function editAsset(asset) {
  // 编辑素材的逻辑
  console.log('Edit asset:', asset.name);
}

// 模拟音频素材数据，符合原型图要求
const filteredAssets = computed(() => {
  // 创建音频素材数据
  const audioAssets = [
    {
      id: '1',
      name: 'mp3/EP198_112.wav',
      type: 'audio',
      size: '8.5 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:22', bpm: 145, format: 'WAV' },
      tags: ['流行', '品牌主题曲'],
      rating: 5
    },
    {
      id: '2',
      name: 'mp3/EP198_113.wav',
      type: 'audio',
      size: '9.2 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:28', bpm: 148, format: 'WAV' },
      tags: ['轻松', '钢琴'],
      rating: 4
    },
    {
      id: '3',
      name: 'mp3/EP198_114.wav',
      type: 'audio',
      size: '7.8 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:15', bpm: 166, format: 'WAV' },
      tags: ['电子', '舞曲'],
      rating: 3
    },
    {
      id: '4',
      name: 'mp3/EP198_115.wav',
      type: 'audio',
      size: '10.1 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:35', bpm: 121, format: 'WAV' },
      tags: ['冥想', '舒缓'],
      rating: 5
    },
    {
      id: '5',
      name: 'mp3/EP198_116.wav',
      type: 'audio',
      size: '8.9 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:23', bpm: 164, format: 'WAV' },
      tags: ['环境音', '氛围'],
      rating: 4
    },
    {
      id: '6',
      name: 'mp3/EP198_117.wav',
      type: 'audio',
      size: '9.5 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:30', bpm: 193, format: 'WAV' },
      tags: ['动感', '吉他'],
      rating: 5
    },
    {
      id: '7',
      name: 'mp3/EP198_118.wav',
      type: 'audio',
      size: '8.3 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:20', bpm: 125, format: 'WAV' },
      tags: ['环境音', '睡眠'],
      rating: 4
    },
    {
      id: '8',
      name: 'mp3/EP198_119.wav',
      type: 'audio',
      size: '9.8 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:32', bpm: 151, format: 'WAV' },
      tags: ['电子', '科技'],
      rating: 5
    },
    {
      id: '9',
      name: 'mp3/EP198_120.wav',
      type: 'audio',
      size: '8.7 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:25', bpm: 164, format: 'WAV' },
      tags: ['古典', '弦乐'],
      rating: 3
    },
    {
      id: '10',
      name: 'mp3/EP198_121.wav',
      type: 'audio',
      size: '10.3 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:38', bpm: 169, format: 'WAV' },
      tags: ['摇滚', '现场'],
      rating: 4
    },
    {
      id: '11',
      name: 'mp3/EP198_122.wav',
      type: 'audio',
      size: '9.1 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:27', bpm: 107, format: 'WAV' },
      tags: ['爵士', '钢琴'],
      rating: 5
    },
    {
      id: '12',
      name: 'mp3/EP198_123.wav',
      type: 'audio',
      size: '8.6 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:24', bpm: 127, format: 'WAV' },
      tags: ['流行', '人声'],
      rating: 4
    },
    {
      id: '13',
      name: 'mp3/EP198_124.wav',
      type: 'audio',
      size: '9.4 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:29', bpm: 173, format: 'WAV' },
      tags: ['电子', '舞曲'],
      rating: 5
    },
    {
      id: '14',
      name: 'mp3/EP198_125.wav',
      type: 'audio',
      size: '9.7 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:31', bpm: 145, format: 'WAV' },
      tags: ['电影', '配乐'],
      rating: 4
    },
    {
      id: '15',
      name: '小岛上的星光.wav',
      type: 'audio',
      size: '12.5 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '04:11', bpm: 145, format: 'WAV' },
      tags: ['流行', '品牌主题曲', '钢琴', '弦乐'],
      rating: 5
    },
    {
      id: '16',
      name: '夏日海风.mp3',
      type: 'audio',
      size: '8.9 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '02:45', bpm: 148, format: 'MP3' },
      tags: ['轻松', '钢琴', '吉他'],
      rating: 4
    },
    {
      id: '17',
      name: 'mp3/EP198_126.wav',
      type: 'audio',
      size: '8.8 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:26', bpm: 151, format: 'WAV' },
      tags: ['嘻哈', '说唱'],
      rating: 3
    },
    {
      id: '18',
      name: 'mp3/EP198_127.wav',
      type: 'audio',
      size: '9.0 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:28', bpm: 142, format: 'WAV' },
      tags: ['民谣', '吉他'],
      rating: 4
    },
    {
      id: '19',
      name: 'mp3/EP198_128.wav',
      type: 'audio',
      size: '9.6 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:30', bpm: 129, format: 'WAV' },
      tags: ['环境音', '自然'],
      rating: 5
    },
    {
      id: '20',
      name: 'mp3/EP198_129.wav',
      type: 'audio',
      size: '9.2 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:29', bpm: 147, format: 'WAV' },
      tags: ['电子', '氛围'],
      rating: 4
    },
    {
      id: '21',
      name: 'mp3/EP198_130.wav',
      type: 'audio',
      size: '8.7 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:25', bpm: 164, format: 'WAV' },
      tags: ['电子', '节奏'],
      rating: 3
    },
    {
      id: '22',
      name: 'mp3/EP198_131.wav',
      type: 'audio',
      size: '9.4 MB',
      createdAt: '2024/02/25 15:42:31',
      metadata: { duration: '01:29', bpm: 145, format: 'WAV' },
      tags: ['钢琴', '弦乐'],
      rating: 5
    }
  ];

  // 创建图片素材数据
  const imageAssets = [
    {
      id: '23',
      name: 'Stylized_Human_1',
      type: 'image',
      size: '2.5 MB',
      createdAt: '2024/02/25 15:42:31',
      thumbnail: 'https://picsum.photos/id/64/400/400',
      metadata: { format: 'PNG', resolution: '1200×800' },
      tags: ['人物', '插画', '风格化'],
      rating: 5
    },
    {
      id: '24',
      name: 'Stylized_Human_2',
      type: 'image',
      size: '3.2 MB',
      createdAt: '2024/02/25 15:42:31',
      thumbnail: 'https://picsum.photos/id/65/400/400',
      metadata: { format: 'PNG', resolution: '1500×1000' },
      tags: ['人物', '插画', '风格化'],
      rating: 4
    },
    {
      id: '25',
      name: 'Stylized_Human_3',
      type: 'image',
      size: '2.8 MB',
      createdAt: '2024/02/25 15:42:31',
      thumbnail: 'https://picsum.photos/id/66/400/400',
      metadata: { format: 'PNG', resolution: '1400×900' },
      tags: ['人物', '插画', '风格化'],
      rating: 5
    },
    {
      id: '26',
      name: 'Stylized_Human_4',
      type: 'image',
      size: '1.9 MB',
      createdAt: '2024/02/25 15:42:31',
      thumbnail: 'https://picsum.photos/id/67/400/400',
      metadata: { format: 'PNG', resolution: '1000×800' },
      tags: ['静物', '插画', '风格化'],
      rating: 4
    },
    {
      id: '27',
      name: 'Stylized_Human_5',
      type: 'image',
      size: '3.5 MB',
      createdAt: '2024/02/25 15:42:31',
      thumbnail: 'https://picsum.photos/id/68/400/400',
      metadata: { format: 'PNG', resolution: '1600×1200' },
      tags: ['人物', '插画', '风格化'],
      rating: 5
    }
  ];

  // 根据搜索关键词过滤
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase();
    return [...audioAssets, ...imageAssets].filter(asset => 
      asset.name.toLowerCase().includes(keyword) ||
      asset.tags.some(tag => tag.toLowerCase().includes(keyword))
    );
  }

  // 默认显示音频素材（根据原型图）
  return audioAssets;
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
  background: #0a0b0f; /* 深色背景，与原型图匹配 */
}

.assets-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  padding: 20px;
  transition: all 0.3s ease;
}

/* 响应式网格布局 */
@media (min-width: 1600px) {
  .assets-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

@media (min-width: 1200px) and (max-width: 1599px) {
  .assets-grid {
    grid-template-columns: repeat(5, 1fr);
  }
}

@media (min-width: 992px) and (max-width: 1199px) {
  .assets-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

/* 网格视图 */
.grid-view {
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
  background: rgba(26, 28, 39, 1); /* 调整为不透明深色背景 */
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  position: relative;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
    border-color: var(--el-color-primary);
    background: rgba(30, 32, 44, 1);
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
  height: 100px; /* 与原型图一致的波形显示高度 */
  overflow: hidden;
  background: rgba(12, 13, 18, 1); /* 不透明背景 */
  
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
    color: #ffffff; /* 白色文本 */
    margin-bottom: 6px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .asset-meta {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  }
  
  /* 音频可视化样式 */
  .audio-visualizer {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 16px;
    background: rgba(12, 13, 18, 1);
  }
  
  .wave-container {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: space-around;
    gap: 2px;
  }
  
  .waveform-bar {
    flex: 1;
    background: linear-gradient(180deg, #4285f4 0%, #34a853 100%); /* 蓝色到绿色的渐变，与原型图匹配 */
    animation: wave 1.2s infinite ease-in-out;
    transform-origin: bottom;
    border-radius: 1px;
    box-shadow: 0 0 6px rgba(64, 158, 255, 0.4);
  }
  
  /* 详细波形样式 */
  .audio-waveform {
    height: 20px;
    display: flex;
    align-items: center;
    justify-content: space-around;
    gap: 1px;
    margin-bottom: 8px;
    position: relative;
    background: rgba(12, 13, 18, 0.5);
    padding: 2px 4px;
    border-radius: 4px;
  }
  
  .detailed-waveform-bar {
    flex: 1;
    background: linear-gradient(180deg, rgba(64, 158, 255, 0.9) 0%, rgba(64, 158, 255, 0.4) 100%);
    animation: detailedWave 1.5s infinite ease-in-out;
    transform-origin: bottom;
    border-radius: 1px;
    box-shadow: 0 0 3px rgba(64, 158, 255, 0.5);
  }
  
  @keyframes wave {
    0%, 100% { transform: scaleY(0.4); opacity: 0.8; }
    50% { transform: scaleY(1); opacity: 1; }
  }
  
  @keyframes detailedWave {
    0%, 100% { transform: scaleY(0.3); opacity: 0.7; }
    50% { transform: scaleY(1); opacity: 1; }
  }
  
  /* 音频文件特殊样式 */
  .asset-item.audio-item {
    border-color: rgba(64, 158, 255, 0.2);
    
    &:hover {
      border-color: var(--el-color-primary);
    }
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
  
  /* 默认在桌面视图下显示侧边栏 */
  @media (min-width: 769px) {
    .sidebar {
      left: 0 !important;
    }
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