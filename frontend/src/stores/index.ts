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
  async (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      const authStore = useAuthStore()
      
      // 清除本地存储的token
      localStorage.removeItem('token')
      authStore.token = null
      authStore.isAuthenticated = false
      authStore.user = null
      
      // 重定向到登录页
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
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
    // 添加token检查方法
    checkTokenValidity() {
      if (!this.token) {
        this.isAuthenticated = false
        return false
      }
      
      // 检查token是否过期（简单检查）
      try {
        const payload = JSON.parse(atob(this.token.split('.')[1]))
        const exp = payload.exp * 1000 // 转换为毫秒
        if (Date.now() >= exp) {
          // Token已过期
          this.logout()
          return false
        }
        return true
      } catch (error) {
        console.error('Token检查失败:', error)
        this.logout()
        return false
      }
    },
    
    // 修改登录方法，添加token存储时间
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
        localStorage.setItem('token_timestamp', Date.now().toString())
        
        return { success: true }
      } catch (error: any) {
        // 优先使用后端返回的具体错误信息
        if (error.response?.data?.detail) {
          return { 
            success: false, 
            message: error.response.data.detail 
          }
        }
        
        // 网络错误和其他异常
        let errorMessage = '登录失败'
        if (error.code === 'NETWORK_ERROR') {
          errorMessage = '网络连接失败，请检查网络连接'
        } else if (error.code === 'ECONNABORTED') {
          errorMessage = '请求超时，请稍后重试'
        } else if (error.response?.status === 500) {
          errorMessage = '服务器内部错误，请稍后重试'
        }
        
        return { 
          success: false, 
          message: errorMessage 
        }
      }
    },
    
    // 修改注册方法，优化错误信息处理
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
        let errorMessage = '注册失败'
        
        if (error.response?.data?.detail) {
          const detail = error.response.data.detail
          
          // 将后端英文错误信息转换为中文
          if (detail.includes('Username already taken')) {
            errorMessage = '用户名已被使用，请选择其他用户名'
          } else if (detail.includes('Failed to create user')) {
            errorMessage = '创建用户失败，请稍后重试'
          } else if (detail.includes('username')) {
            errorMessage = '用户名格式不正确（长度3-20个字符）'
          } else if (detail.includes('password')) {
            errorMessage = '密码格式不正确（至少6个字符）'
          } else if (detail.includes('Registration failed')) {
            errorMessage = '注册失败，请检查输入信息'
          } else {
            errorMessage = detail
          }
        } else if (error.code === 'NETWORK_ERROR') {
          errorMessage = '网络连接失败，请检查网络连接'
        } else if (error.code === 'ECONNABORTED') {
          errorMessage = '请求超时，请稍后重试'
        } else if (error.response?.status === 400) {
          errorMessage = '请求参数错误，请检查输入信息'
        } else if (error.response?.status === 500) {
          errorMessage = '服务器内部错误，请稍后重试'
        }
        
        return { 
          success: false, 
          message: errorMessage 
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
        localStorage.removeItem('token_timestamp')
      }
    },
    
    // 添加获取用户信息的方法
    async getUserProfile() {
      if (!this.token) {
        throw new Error('No token available')
      }
      
      try {
        const response = await api.get('/auth/me')
        // 后端返回的是UserResponse对象，直接赋值给user
        this.user = response.data
        return this.user
      } catch (error) {
        console.error('获取用户信息失败:', error)
        throw error
      }
    },
    
    // 修改初始化检查方法，优化错误处理
    async initializeAuth() {
      if (!this.token) {
        this.isAuthenticated = false
        return
      }
      
      // 检查token有效性
      if (!this.checkTokenValidity()) {
        return
      }
      
      // 如果token有效但用户信息为空，获取用户信息
      if (this.isAuthenticated && !this.user) {
        try {
          await this.getUserProfile()
        } catch (error) {
          console.error('初始化用户信息失败:', error)
          // 如果获取用户信息失败，不立即登出，而是检查错误类型
          // 如果是网络错误或服务器暂时不可用，保持登录状态
          if (error.code === 'NETWORK_ERROR' || error.code === 'ECONNABORTED' || 
              error.response?.status >= 500) {
            console.warn('服务器暂时不可用，保持登录状态')
            // 保持当前状态，不执行登出
            return
          }
          // 只有明确是认证错误时才执行登出
          if (error.response?.status === 401 || error.response?.status === 403) {
            this.logout()
          }
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