import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/HomeView.vue')
  },
  {
    path: '/travel-plans',
    name: 'TravelPlans',
    component: () => import('../views/TravelPlansView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router