<template>
  <div class="login-container">
    <el-card class="login-card">
      <h2>登录</h2>
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef">
        <el-form-item label="用户名" prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名" 
            :disabled="loading"
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码"
            :disabled="loading"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <div class="button-container">
            <el-button 
              type="primary" 
              @click="handleLogin" 
              :loading="loading"
              class="login-button"
            >
              {{ loading ? '登录中...' : '登录' }}
            </el-button>
            <el-button 
              @click="$router.push('/register')" 
              :disabled="loading"
              class="register-button"
            >
              注册新账号
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

const loginFormRef = ref()
const loading = ref(false)
const errorMessage = ref('')

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在3到20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6个字符', trigger: 'blur' }
  ]
}

// 清除错误信息
const clearError = () => {
  errorMessage.value = ''
}

const handleLogin = async () => {
  try {
    // 清除之前的错误信息
    clearError()
    
    // 验证表单
    await loginFormRef.value.validate()
    loading.value = true
    
    // 执行登录
    const result = await authStore.login(loginForm.username, loginForm.password)
    
    if (result.success) {
      ElMessage.success('登录成功！')
      router.push('/profile')
    } else {
      // 只显示后端返回的具体错误信息，不重复显示表单验证错误
      errorMessage.value = result.message
    }
  } catch (error: any) {
    // 表单验证失败时，不显示额外的错误信息，让Element Plus的表单验证规则自动显示
    if (error && error.fields) {
      // 表单验证错误由Element Plus自动处理，不需要额外显示
      return
    }
    // 其他异常情况
    errorMessage.value = '登录过程中发生未知错误，请稍后重试'
  } finally {
    loading.value = false
  }
}

// 监听表单变化时清除错误信息
watch([() => loginForm.username, () => loginForm.password], () => {
  if (errorMessage.value) {
    clearError()
  }
})
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.login-card {
  width: 400px;
  padding: 20px;
  position: relative;
}

.error-message {
  margin-top: 20px;
}

:deep(.el-alert) {
  margin-bottom: 0;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-button) {
  height: 40px;
}

/* 修复按钮布局 */
.button-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.login-button,
.register-button {
  width: 100% !important;
  margin-left: 0 !important;
  margin-right: 0 !important;
}

.register-button {
  margin-top: 10px !important;
}
</style>