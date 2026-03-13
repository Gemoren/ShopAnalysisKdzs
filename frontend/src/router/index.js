import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: '主页',
    component: () => import('../layouts/MainLayout.vue'),
    redirect: '/statistics',
    children: [
      {
        path: '/statistics',
        name: '数据总览',
        component: () => import('../components/statistics.vue')
      },
      {
        path: '/shops',
        name: '商品',
        component: () => import('../components/shops.vue')
      },
      {
        path: '/order',
        name: '订单',
        component: () => import('../components/order.vue')
      },
      {
        path: '/promotion',
        name: '推广',
        component: () => import('../components/promotion.vue')
      }
    ]
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('../components/login.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router

