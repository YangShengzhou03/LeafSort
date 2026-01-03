<template>
  <div class="home-page">
    <el-carousel :interval="5000" arrow="hover" height="200px" indicator-position="outside">
      <el-carousel-item v-for="(item, index) in carouselItems" :key="index">
        <div class="carousel-item" :style="{ background: item.background }" @click="item.action">
          <el-icon :size="32">
            <component :is="item.icon" />
          </el-icon>
          <h2 class="carousel-title">{{ item.title }}</h2>
          <p class="carousel-desc">{{ item.desc }}</p>
        </div>
      </el-carousel-item>
    </el-carousel>

    <div class="quick-access">
      <h3 class="section-title">快速访问</h3>
      <div class="quick-grid">
        <div class="quick-item" v-for="(item, index) in quickItems" :key="index" @click="item.action">
          <el-icon :size="24">
            <component :is="item.icon" />
          </el-icon>
          <span>{{ item.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { 
  User, Location, Calendar, Star, PictureRounded, ChatDotRound, 
  Search, Operation, Files, List
} from '@element-plus/icons-vue'

const router = useRouter()

const carouselItems = [
  {
    icon: User,
    title: '轻松管理您的人物照片',
    desc: 'AI智能识别和分类照片中的人物',
    background: '#1a237e',
    action: () => router.push('/gallery/people')
  },
  {
    icon: Location,
    title: '按地理位置整理美好回忆',
    desc: '基于地理位置信息自动整理照片',
    background: '#b71c1c',
    action: () => router.push('/gallery/places')
  },
  {
    icon: Calendar,
    title: '记录生活中的重要时刻',
    desc: 'AI智能识别和整理生活中的重要事件',
    background: '#006064',
    action: () => router.push('/gallery/events')
  },
  {
    icon: ChatDotRound,
    title: '用自然语言快速找到照片',
    desc: '智能搜索 - 用日常语言描述您想要找的照片',
    background: '#1b5e20',
    action: () => router.push('/search/smart')
  }
]

const quickItems = [
  { icon: Star, name: '情感相册', action: () => router.push('/gallery/emotions') },
  { icon: PictureRounded, name: '色彩相册', action: () => router.push('/gallery/colors') },
  { icon: Search, name: '智能搜索', action: () => router.push('/search/smart') },
  { icon: Operation, name: '智能整理', action: () => router.push('/media/smart-arrange') },
  { icon: Files, name: '文件去重', action: () => router.push('/media/deduplication') },
  { icon: List, name: '批量处理', action: () => router.push('/media/batch-process') }
]
</script>

<style scoped>
.home-page {
  padding: 24px;
  height: 100%;
  overflow-y: auto;
  background: #f5f7fa;
}

.carousel-item {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  color: white;
  padding: 20px;
}

.carousel-item:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
}

.carousel-item .el-icon {
  width: 60px;
  height: 60px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 12px;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.carousel-item:hover .el-icon {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

.carousel-item h2 {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 8px 0;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.carousel-item p {
  font-size: 13px;
  margin: 0 0 12px 0;
  opacity: 0.9;
  text-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);
}

.quick-access {
  max-width: 1200px;
  margin: 32px auto 0;
}

.section-title {
  font-size: 20px;
  font-weight: 600;
  color: #303133;
  margin: 0 0 20px 0;
}

.quick-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 16px;
}

.quick-item {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.quick-item:hover {
  background: #fafafa;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
}

.quick-item .el-icon {
  color: #409eff;
  transition: color 0.2s ease;
}

.quick-item:hover .el-icon {
  color: #66b1ff;
}

.quick-item span {
  font-size: 14px;
  font-weight: 500;
  color: #606266;
}

:deep(.el-carousel__indicator) {
  padding: 12px 4px;
}

:deep(.el-carousel__button) {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: rgba(255, 255, 255, 0.5);
}

:deep(.el-carousel__indicator.is-active .el-carousel__button) {
  background-color: white;
  width: 24px;
  border-radius: 4px;
}
</style>
