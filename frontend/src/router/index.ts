import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import UserProfileView from '../views/UserProfileView.vue'
import AIPlanningView from '../views/AIPlanningView.vue'
import MapDemoView from '../views/MapDemoView.vue'
import ExpenseManagementView from '../views/ExpenseManagementView.vue'
import TripExpensesView from '../views/TripExpensesView.vue'
import { useAuthStore } from '@/stores'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: AIPlanningView,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView
    },
    {
      path: '/profile',
      name: 'profile',
      component: UserProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/ai-planning',
      name: 'ai-planning',
      component: AIPlanningView,
      meta: { requiresAuth: true }
    },
    {
      path: '/map-demo',
      name: 'map-demo',
      component: MapDemoView,
      meta: { requiresAuth: true }
    },
    {
      path: '/expense-management',
      name: 'expense-management',
      component: ExpenseManagementView,
      meta: { requiresAuth: true }
    },
    {
      path: '/trip-expenses/:tripId',
      name: 'trip-expenses',
      component: TripExpensesView,
      meta: { requiresAuth: true }
    }
  ]
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router