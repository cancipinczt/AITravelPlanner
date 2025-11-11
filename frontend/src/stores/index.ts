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
  
  getters: {
    // 添加api实例的getter
    api: () => api
  },
  
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
    
    // 修改获取用户信息的方法，返回统一格式的结果
    async getUserProfile() {
      if (!this.token) {
        return { success: false, message: 'No token available' }
      }
      
      try {
        const response = await api.get('/auth/me')
        // 后端返回的是UserResponse对象，直接赋值给user
        this.user = response.data
        return { success: true, data: this.user }
      } catch (error: any) {
        console.error('获取用户信息失败:', error)
        return { 
          success: false, 
          message: error.response?.data?.detail || '获取用户信息失败' 
        }
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
          const result = await this.getUserProfile()
          if (!result.success) {
            console.warn('获取用户信息失败:', result.message)
            // 如果获取用户信息失败，检查错误类型
            if (result.message?.includes('401') || result.message?.includes('403')) {
              this.logout()
            }
          }
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

// 用户偏好接口
interface UserPreference {
  id: string
  user_id: string
  travel_preferences: string | null
  special_requirements: string | null
  created_at: string | null
  updated_at: string | null
}

export const useUserPreferenceStore = defineStore('userPreference', {
  state: () => ({
    preferences: [] as UserPreference[],
    loading: false,
    error: null as string | null
  }),

  getters: {
    getUserPreferences: (state) => state.preferences,
    getPreferenceById: (state) => (id: string) => {
      return state.preferences.find(pref => pref.id === id)
    },
    hasPreferences: (state) => state.preferences.length > 0,
    preferencesCount: (state) => state.preferences.length
  },

  actions: {
    // 获取用户所有偏好 - 重命名为fetchUserPreferences以避免命名冲突
    async fetchUserPreferences() {
      this.loading = true
      this.error = null
      try {
        console.log('开始调用后端API获取偏好数据...')
        const response = await api.get('/user/preferences')
        console.log('后端API响应状态:', response.status)
        console.log('后端返回的完整响应:', response)
        console.log('后端返回的数据:', response.data)
        
        // 修复：后端返回的是UserPreferenceListResponse对象，包含preferences字段
        if (response.data && response.data.preferences) {
          this.preferences = response.data.preferences
          console.log('✅ 成功加载偏好数据，数量:', this.preferences.length)
          console.log('偏好数据详情:', this.preferences)
        } else {
          this.preferences = []
          console.warn('⚠️ 后端返回的偏好数据格式不正确，期望包含preferences字段:', response.data)
        }
      } catch (error: any) {
        this.error = error.response?.data?.detail || '获取偏好失败'
        console.error('❌ 获取用户偏好失败:', error)
        
        // 添加详细的错误信息
        if (error.response) {
          console.error('HTTP状态码:', error.response.status)
          console.error('响应数据:', error.response.data)
          console.error('响应头:', error.response.headers)
        } else if (error.request) {
          console.error('请求未收到响应，可能是网络问题或后端服务未启动')
          console.error('请求详情:', error.request)
        } else {
          console.error('请求配置错误:', error.message)
        }
        
        this.preferences = []
      } finally {
        this.loading = false
      }
    },

    // 创建新偏好 - 修复参数传递
    async createUserPreferences(preferenceData: { 
      name: string; 
      travel_preferences?: string; 
      special_requirements?: string 
    }) {
      this.loading = true
      this.error = null
      try {
        const response = await api.post('/user/preferences', preferenceData)
        if (response.data) {
          // 将新偏好添加到列表中
          this.preferences.unshift(response.data)
          return { success: true, data: response.data }
        }
        return { success: false, message: '创建偏好失败' }
      } catch (error: any) {
        this.error = error.response?.data?.detail || '创建偏好失败'
        console.error('创建用户偏好失败:', error)
        return { success: false, message: this.error }
      } finally {
        this.loading = false
      }
    },

    // 更新特定偏好 - 修复参数传递
    async updateUserPreferences(preferenceId: string, preferenceData: { 
      name?: string; 
      travel_preferences?: string; 
      special_requirements?: string 
    }) {
      this.loading = true
      this.error = null
      try {
        const response = await api.put(`/user/preferences/${preferenceId}`, preferenceData)
        if (response.data) {
          // 更新列表中的偏好
          const index = this.preferences.findIndex(pref => pref.id === preferenceId)
          if (index !== -1) {
            this.preferences[index] = response.data
          }
          return { success: true, data: response.data }
        }
        return { success: false, message: '更新偏好失败' }
      } catch (error: any) {
        this.error = error.response?.data?.detail || '更新偏好失败'
        console.error('更新用户偏好失败:', error)
        return { success: false, message: this.error }
      } finally {
        this.loading = false
      }
    },

    // 删除特定偏好 - 修复参数传递
    async deleteUserPreferences(preferenceId: string) {
      this.loading = true
      this.error = null
      try {
        const response = await api.delete(`/user/preferences/${preferenceId}`)
        if (response.data) {
          // 从列表中移除偏好
          this.preferences = this.preferences.filter(pref => pref.id !== preferenceId)
          return { success: true, message: '删除偏好成功' }
        }
        return { success: false, message: '删除偏好失败' }
      } catch (error: any) {
        this.error = error.response?.data?.detail || '删除偏好失败'
        console.error('删除用户偏好失败:', error)
        return { success: false, message: this.error }
      } finally {
        this.loading = false
      }
    },

    clearPreferences() {
      this.preferences = []
      this.error = null
      this.loading = false
    }
  }
})

// 在文件末尾添加api实例的导出
export { api }

// 删除重复的导出语句
// export { useAuthStore, useAppStore, useUserPreferenceStore }