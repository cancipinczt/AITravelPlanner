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
      this.user = null
      this.token = null
      this.isAuthenticated = false
      localStorage.removeItem('token')
    },
    
    async getUserProfile() {
      try {
        const response = await api.get('/user/profile')
        this.user = response.data
        return { success: true }
      } catch (error: any) {
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