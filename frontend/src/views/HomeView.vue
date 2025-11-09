<template>
  <div class="home">
    <h2>欢迎使用AI旅行规划师</h2>
    <p>开始规划您的智能旅行吧！</p>
    
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <h3>旅行计划</h3>
          <p>查看和管理您的旅行计划</p>
          <el-button type="primary" @click="$router.push('/travel-plans')">
            查看旅行计划
          </el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <h3>个人中心</h3>
          <p>管理您的个人信息和设置</p>
          <el-button @click="$router.push('/profile')">
            查看个人中心
          </el-button>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <h3>系统状态</h3>
          <p>检查后端服务连接状态</p>
          <el-button @click="testBackendConnection">
            测试后端连接
          </el-button>
          <p v-if="testResult" style="margin-top: 10px; font-size: 12px;">
            {{ testResult }}
          </p>
        </el-card>
      </el-col>
    </el-row>

    <!-- 添加语音识别测试入口 -->
    <el-row :gutter="20" style="margin-top: 30px;">
      <el-col :span="24">
        <el-card>
          <h3>语音识别功能测试</h3>
          <p>测试科大讯飞语音识别API的两个接口功能</p>
          <el-button type="primary" @click="$router.push('/speech-test')">
            前往语音识别测试
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()
const testResult = ref('')

// 页面加载时检查用户认证状态
onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // 如果已登录但用户信息为空，获取用户信息
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.getUserProfile()
  }
})

const testBackendConnection = async () => {
  try {
    const response = await axios.get('http://localhost:8000/health')
    testResult.value = `后端连接成功: ${JSON.stringify(response.data)}`
  } catch (error) {
    testResult.value = `后端连接失败: ${error}`
  }
}
</script>

<style scoped>
.home {
  text-align: center;
  padding: 20px;
}

.el-row {
  margin-top: 30px;
}

.el-col {
  margin-bottom: 20px;
}

h2 {
  color: #409EFF;
  margin-bottom: 10px;
}

p {
  color: #666;
  margin-bottom: 30px;
}
</style>