<template>
  <el-container class="layout">
    <el-aside :class="['aside', { 'aside-collapsed': isCollapsed }]" :width="asideWidth">
      <div class="aside-header">
        <div class="header-btn collapse-btn" @click="isCollapsed = !isCollapsed">
          <el-icon>
            <Fold v-if="!isCollapsed" />
            <Expand v-else />
          </el-icon>
        </div>
        <template v-if="!isCollapsed">
          <div class="header-btn right-btn">
            <el-icon>
              <More />
            </el-icon>
          </div>
        </template>
      </div>

      <div class="menu-container">
        <div class="menu-item" :class="{ active: activeRoute === '/' }" @click="$router.push('/')">
          <el-icon>
            <House />
          </el-icon>
          <span class="menu-text" v-show="!isCollapsed">首页</span>
        </div>

        <div class="menu-section">
          <div class="section-title menu-text" v-show="!isCollapsed">相册</div>
          <div class="menu-item" :class="{ active: activeRoute === '/gallery/people' }"
            @click="$router.push('/gallery/people')">
            <el-icon>
              <User />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">人物相册</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/gallery/places' }"
            @click="$router.push('/gallery/places')">
            <el-icon>
              <Location />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">地点相册</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/gallery/events' }"
            @click="$router.push('/gallery/events')">
            <el-icon>
              <Calendar />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">事件相册</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/gallery/emotions' }"
            @click="$router.push('/gallery/emotions')">
            <el-icon>
              <Star />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">情感相册</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/gallery/colors' }"
            @click="$router.push('/gallery/colors')">
            <el-icon>
              <PictureRounded />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">色彩相册</span>
          </div>
        </div>

        <div class="menu-section">
          <div class="section-title menu-text" v-show="!isCollapsed">工具</div>
          <div class="menu-item" :class="{ active: activeRoute === '/search/smart' }"
            @click="$router.push('/search/smart')">
            <el-icon>
              <Search />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">智能搜索</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/media/smart-arrange' }"
            @click="$router.push('/media/smart-arrange')">
            <el-icon>
              <Operation />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">智能整理</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/media/deduplication' }"
            @click="$router.push('/media/deduplication')">
            <el-icon>
              <Files />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">文件去重</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/media/exif-edit' }"
            @click="$router.push('/media/exif-edit')">
            <el-icon>
              <Edit />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">EXIF编辑</span>
          </div>
          <div class="menu-item" :class="{ active: activeRoute === '/media/batch-process' }"
            @click="$router.push('/media/batch-process')">
            <el-icon>
              <List />
            </el-icon>
            <span class="menu-text" v-show="!isCollapsed">批量处理</span>
          </div>
        </div>
      </div>
    </el-aside>

    <el-container class="main-container">
      <TitleBar />

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  House, User, Location, Calendar, Star, PictureRounded,
  Search, Operation, Files, Edit, List, Fold, Expand, More
} from '@element-plus/icons-vue'
import TitleBar from '@/components/TitleBar.vue'

const route = useRoute()
const isCollapsed = ref(false)

const activeRoute = computed(() => route.path)
const asideWidth = computed(() => isCollapsed.value ? '60px' : '180px')
</script>

<style scoped>
.layout {
  height: 100vh;
  width: 100vw;
  display: flex;
  overflow: hidden;
  background: #f5f7fa;
}

.aside {
  background: #ffffff;
  border-right: 1px solid #e5e6eb;
  transition: width 0.2s ease;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  height: 100vh;
}

.aside-header {
  height: 36px;
  display: flex;
  align-items: center;
  padding: 0 12px;
  border-bottom: 1px solid #f2f3f5;
  flex-shrink: 0;
}

.header-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  color: #606266;
  transition: all 0.15s ease;
  flex-shrink: 0;
}

.right-btn {
  margin-left: auto;
}

.header-btn:hover {
  background: #f5f7fa;
  color: #409eff;
}

.header-btn .el-icon {
  font-size: 18px;
}

.menu-container {
  flex: 1;
  overflow-y: auto;
  padding: 8px 0;
}

.menu-section {
  margin-bottom: 8px;
}

.section-title {
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #909399;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  margin: 2px 8px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
  color: #606266;
  font-size: 14px;
}

.menu-item:hover {
  background: #f5f7fa;
  color: #409eff;
}

.menu-item.active {
  background: #409eff;
  color: white;
}

.menu-item .el-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.menu-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.aside-collapsed .menu-text {
  opacity: 0;
  transform: translateX(-10px);
  pointer-events: none;
}

.aside-collapsed {
  width: 60px !important;
}

.aside-collapsed .menu-item {
  justify-content: center;
  padding: 10px;
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  height: 100vh;
}

.main {
  flex: 1;
  overflow: auto;
  overflow-x: hidden;
  background: #f5f7fa;
  padding: 0;
  min-width: 0;
}
</style>
