import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/all',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/recent',
    component: () => import('../views/RecentView.vue')
  },
  {
    path: '/favorites',
    component: () => import('../views/FavoritesView.vue')
  },
  {
    path: '/untagged',
    component: () => import('../views/UntaggedView.vue')
  },
  {
    path: '/duplicates',
    component: () => import('../views/DuplicatesView.vue')
  },
  {
    path: '/folders',
    component: () => import('../views/FoldersView.vue')
  },
  {
    path: '/tags',
    component: () => import('../views/TagsView.vue')
  },
  {
    path: '/trash',
    component: () => import('../views/TrashView.vue')
  },
  
  // 智能场景路由
  {
    path: '/scene-landscape',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/scene-people',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/scene-animals',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/scene-food',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/scene-travel',
    component: () => import('../views/AllMaterialsView.vue')
  },
  
  // 相册功能路由
  {
    path: '/story-albums',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/smart-cleanup',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/photo-editor',
    component: () => import('../views/AllMaterialsView.vue')
  },
  
  // 文件管理路由
  {
    path: '/nas-connect',
    component: () => import('../views/AllMaterialsView.vue')
  },
  {
    path: '/sync-settings',
    component: () => import('../views/AllMaterialsView.vue')
  },
  
  {
    path: '/:pathMatch(.*)*',
    component: () => import('../views/AllMaterialsView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
