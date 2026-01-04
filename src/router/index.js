import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomePage.vue'),
    meta: { 
      title: '首页',
      keepAlive: true
    }
  },
  {
    path: '/gallery/people',
    name: 'PeopleGallery',
    component: () => import('../views/gallery/PeopleGallery.vue'),
    meta: { 
      title: '人物相册',
      keepAlive: true
    }
  },
  {
    path: '/gallery/places',
    name: 'PlacesGallery',
    component: () => import('../views/gallery/PlacesGallery.vue'),
    meta: { 
      title: '地点相册',
      keepAlive: true
    }
  },
  {
    path: '/gallery/events',
    name: 'EventsGallery',
    component: () => import('../views/gallery/EventsGallery.vue'),
    meta: { 
      title: '事件相册',
      keepAlive: true
    }
  },
  {
    path: '/gallery/emotions',
    name: 'EmotionsGallery',
    component: () => import('../views/gallery/EmotionsGallery.vue'),
    meta: { 
      title: '情感相册',
      keepAlive: true
    }
  },
  {
    path: '/gallery/colors',
    name: 'ColorsGallery',
    component: () => import('../views/gallery/ColorsGallery.vue'),
    meta: { 
      title: '色彩相册',
      keepAlive: true
    }
  },
  {
    path: '/search/smart',
    name: 'SmartSearch',
    component: () => import('../views/tools/SmartSearch.vue'),
    meta: { 
      title: '自然语言搜索',
      keepAlive: false
    }
  },
  {
    path: '/media/smart-arrange',
    name: 'SmartArrange',
    component: () => import('../views/tools/SmartArrange.vue'),
    meta: { 
      title: '智能整理',
      keepAlive: false
    }
  },
  {
    path: '/media/deduplication',
    name: 'Deduplication',
    component: () => import('../views/tools/DeduplicationPage.vue'),
    meta: { 
      title: '文件去重',
      keepAlive: false
    }
  },
  {
    path: '/media/exif-edit',
    name: 'ExifEdit',
    component: () => import('../views/tools/ExifEdit.vue'),
    meta: { 
      title: 'EXIF编辑',
      keepAlive: false
    }
  },
  {
    path: '/media/batch-process',
    name: 'BatchProcess',
    component: () => import('../views/tools/BatchProcess.vue'),
    meta: { 
      title: '批量处理',
      keepAlive: false
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFoundView.vue'),
    meta: { 
      title: '页面未找到',
      keepAlive: false
    }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    }
    if (to.hash) {
      return {
        el: to.hash,
        behavior: 'smooth'
      }
    }
    return { top: 0, behavior: 'smooth' }
  }
})

router.beforeEach((to, from, next) => {
  if (to.meta && to.meta.title) {
    document.title = `${to.meta.title} - LeafSort Pro`
  } else {
    document.title = 'LeafSort Pro'
  }
  next()
})

router.onError((error) => {
  if (error.message.includes('Failed to fetch dynamically imported module')) {
    window.location.reload()
  }
})

export default router
