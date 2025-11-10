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
          <el-button 
            type="primary" 
            @click="handleRegister" 
            :loading="loading"
            style="width: 100%;"
          >
            {{ loading ? '注册中...' : '注册' }}
          </el-button>
          <el-button 
            @click="$router.push('/login')" 
            :disabled="loading"
            style="width: 100%; margin-top: 10px;"
          >
            返回登录
          </el-button>
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
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.register-card {
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
</style>