<template>
  <div class="register-container">
    <el-card class="register-card">
      <h2>注册</h2>
      <el-form :model="registerForm" :rules="registerRules" ref="registerFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="registerForm.username" 
            placeholder="请输入用户名（3-20个字符）"
            :disabled="loading"
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="registerForm.password" 
            type="password" 
            placeholder="请输入密码（至少6个字符）"
            :disabled="loading"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input 
            v-model="registerForm.confirmPassword" 
            type="password" 
            placeholder="请再次输入密码"
            :disabled="loading"
            show-password
            @keyup.enter="handleRegister"
          />
        </el-form-item>
        <el-form-item>
          <div class="button-container">
            <el-button 
              type="primary" 
              :loading="loading" 
              @click="handleRegister"
              class="register-button"
            >
              注册
            </el-button>
            <el-button 
              @click="goToLogin"
              class="back-button"
            >
              返回登录
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      
      <!-- 错误提示区域 -->
      <div v-if="errorMessage" class="error-message">
        <el-alert 
          :title="errorMessage" 
          type="error" 
          show-icon 
          :closable="true"
          @close="clearError"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()

const registerFormRef = ref()
const loading = ref(false)
const errorMessage = ref('')

const registerForm = reactive({
  username: '',
  password: '',
  confirmPassword: ''
})

const validateConfirmPassword = (rule: any, value: any, callback: any) => {
  if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const registerRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

const handleRegister = async () => {
  if (!registerFormRef.value) return
  
  try {
    // 清除之前的错误信息
    clearError()
    
    await registerFormRef.value.validate()
    loading.value = true
    
    const result = await authStore.register(registerForm.username, registerForm.password)
    if (result.success) {
      ElMessage.success('注册成功！欢迎使用AI旅行规划系统')
      router.push('/profile')
    } else {
      // 显示详细的错误信息
      errorMessage.value = result.message
      ElMessage.error(result.message)
    }
  } catch (error: any) {
    // 表单验证失败
    if (error && error.fields) {
      errorMessage.value = '请检查表单填写是否正确'
      ElMessage.warning('请检查表单填写是否正确')
    } else {
      errorMessage.value = '注册过程中发生未知错误，请稍后重试'
      ElMessage.error('注册过程中发生未知错误，请稍后重试')
    }
  } finally {
    loading.value = false
  }
}

// 监听表单变化时清除错误信息
watch([() => registerForm.username, () => registerForm.password, () => registerForm.confirmPassword], () => {
  if (errorMessage.value) {
    clearError()
  }
})

// 添加返回登录函数
const goToLogin = () => {
  router.push('/login')
}
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}

.register-card {
  width: 420px;
  border-radius: 20px;
  border: none;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(15px);
  background: rgba(255, 255, 255, 0.95);
  padding: 40px;
  position: relative;
  overflow: hidden;
}

.register-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
}

.register-card h2 {
  text-align: center;
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

:deep(.el-form-item) {
  margin-bottom: 24px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 8px;
}

:deep(.el-input) {
  border-radius: 10px;
}

:deep(.el-input__wrapper) {
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
  border-color: rgba(102, 126, 234, 0.4);
}

:deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  border-color: #667eea;
}

.button-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 8px;
  width: 100%;
}

.register-button {
  height: 48px;
  border-radius: 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
  transition: all 0.3s ease;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.back-button {
  height: 48px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.back-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
  transform: translateY(-1px);
}

/* 删除错误的 .login-button 样式 */
.register-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(82, 196, 26, 0.4);
}

.login-button {
  height: 48px;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.login-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
  transform: translateY(-1px);
}

.error-message {
  margin-top: 20px;
}

:deep(.el-alert) {
  border-radius: 10px;
  border: none;
}

:deep(.el-alert--error) {
  background: rgba(245, 108, 108, 0.1);
  color: #f56c6c;
}

/* 响应式设计 */
@media (max-width: 480px) {
  .register-container {
    padding: 16px;
  }
  
  .register-card {
    width: 100%;
    max-width: 360px;
    padding: 32px 24px;
  }
  
  .register-card h2 {
    font-size: 28px;
    margin-bottom: 24px;
  }
}
</style>