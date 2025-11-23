import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    children: [
      {
        path: '/library',
        name: 'Library',
        component: () => import('@/views/Library.vue'),
        meta: { title: '素材库' }
      },
      {
        path: '/collection',
        name: 'Collection',
        component: () => import('@/views/Collection.vue'),
        meta: { title: '收集' }
      },
      {
        path: '/organize',
        name: 'Organize',
        component: () => import('@/views/Organize.vue'),
        meta: { title: '整理' }
      },
      {
        path: '/search',
        name: 'Search',
        component: () => import('@/views/Search.vue'),
        meta: { title: '搜索' }
      },
      {
        path: '/settings',
        name: 'Settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 可以在这里添加权限验证等逻辑
  next()
})

export default router