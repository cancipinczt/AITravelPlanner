import { defineStore } from 'pinia'
import axios from 'axios'

interface User {
  id: string
  username: string
  created_at: string
  updated_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json'
  }
})

// 添加请求拦截器，自动添加token
// 如果已有axios拦截器，添加logout请求的特殊处理
api.interceptors.request.use((config) => {
  // 如果是logout请求，不添加Authorization头
  if (config.url?.includes('/auth/logout')) {
    return config
  }
  
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 添加响应拦截器，处理认证错误
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      // 清除本地存储的token
      localStorage.removeItem('token')
      // 可以在这里添加重定向到登录页的逻辑
    }
    return Promise.reject(error)
  }
)

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: !!localStorage.getItem('token')
  }),
  actions: {
    // 修改登录方法
    async login(username: string, password: string) {
      try {
        const response = await api.post('/auth/login', {
          username,
          password
        })
        
        const { access_token, user } = response.data
        this.token = access_token
        this.user = user
        this.isAuthenticated = true
        
        localStorage.setItem('token', access_token)
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.detail || '登录失败' 
        }
      }
    },
    
    // 修改注册方法
    async register(username: string, password: string) {
      try {
        const response = await api.post('/auth/register', {
          username,
          password
        })
        
        const { access_token, user } = response.data
        this.token = access_token
        this.user = user
        this.isAuthenticated = true
        
        localStorage.setItem('token', access_token)
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.detail || '注册失败' 
        }
      }
    },
    
    async logout() {
      try {
        // 先调用后端logout接口
        if (this.token) {
          try {
            await api.post('/auth/logout', {}, {
              headers: {
                'Authorization': `Bearer ${this.token}`
              }
            })
          } catch (error) {
            // 网络错误不影响前端登出逻辑
            console.warn('后端登出请求失败，继续执行前端登出:', error)
          }
        }
      } finally {
        // 确保前端登出逻辑执行
        this.user = null
        this.token = null
        this.isAuthenticated = false
        localStorage.removeItem('token')
      }
    },
    
    // 修改getUserProfile方法，确保在获取用户信息前token已设置
    async getUserProfile() {
      try {
        // 确保token已添加到请求头
        const token = localStorage.getItem('token')
        if (token && !this.token) {
          this.token = token
        }
        
        const response = await api.get('/user/profile')
        this.user = response.data
        return { success: true }
      } catch (error: any) {
        // 如果认证失败，清除本地状态
        if (error.response?.status === 401 || error.response?.status === 403) {
          this.logout()
        }
        return { 
          success: false, 
          message: error.response?.data?.detail || '获取用户信息失败' 
        }
      }
    },
    
    async updateUserProfile(userData: Partial<User>) {
      try {
        const response = await api.put('/user/profile', userData)
        this.user = response.data
        return { success: true }
      } catch (error: any) {
        return { 
          success: false, 
          message: error.response?.data?.detail || '更新用户信息失败' 
        }
      }
    }
  }
})

export const useAppStore = defineStore('app', {
  state: () => ({
    travelPlans: []
  }),
  actions: {
    // 存储操作
  }
})