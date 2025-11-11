import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import SpeechTestView from '../views/SpeechTestView.vue'
import TravelPlansView from '../views/TravelPlansView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import MapDemoView from '../views/MapDemoView.vue'
import MapApiTestView from '../views/MapApiTestView.vue'
import AIPlanningView from '../views/AIPlanningView.vue'

const routes = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
    meta: { requiresGuest: true }
  },
  {
    path: '/register',
    name: 'register',
    component: RegisterView,
    meta: { requiresGuest: true }
  },
  {
    path: '/speech-test',
    name: 'speech-test',
    component: SpeechTestView,
    meta: { requiresAuth: true }
  },
  {
    path: '/travel-plans',
    name: 'travel-plans',
    component: TravelPlansView,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'profile',
    component: UserProfileView,
    meta: { requiresAuth: true }
  },
  {
    path: '/map-demo',
    name: 'map-demo',
    component: MapDemoView,
    meta: { requiresAuth: true }
  },
  {
    path: '/map-api-test',
    name: 'map-api-test',
    component: MapApiTestView,
    meta: { requiresAuth: true }
  },
  {
    path: '/ai-planning',
    name: 'ai-planning',
    component: AIPlanningView,
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 添加全局前置守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // 初始化认证状态检查
  await authStore.initializeAuth()
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 未登录且访问需要认证的页面，重定向到登录页
    next('/login')
    return
  }
  
  // 检查路由是否需要访客状态（已登录用户不能访问登录/注册页）
  if (to.meta.requiresGuest && authStore.isAuthenticated) {
    // 已登录用户访问登录/注册页，重定向到首页
    next('/')
    return
  }
  
  next()
})

export default router