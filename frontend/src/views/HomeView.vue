<template>
  <div class="home-container">
    <h1>AI旅行规划师</h1>
    <p class="welcome-text">欢迎使用智能旅行规划系统</p>
    
    <div class="nav-grid">
      <!-- 旅行计划 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-location-outline card-icon"></i>
          <h3>旅行计划</h3>
          <p>创建和管理您的旅行计划</p>
          <el-button type="primary" @click="$router.push('/travel-plans')">
            开始规划
          </el-button>
        </div>
      </el-card>

      <!-- 个人中心 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-user card-icon"></i>
          <h3>个人中心</h3>
          <p>查看和管理个人信息</p>
          <el-button type="primary" @click="$router.push('/profile')">
            进入个人中心
          </el-button>
        </div>
      </el-card>

      <!-- 系统状态 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-monitor card-icon"></i>
          <h3>系统状态</h3>
          <p>检查后端服务状态</p>
          <el-button type="primary" @click="testBackendConnection">
            测试连接
          </el-button>
        </div>
      </el-card>

      <!-- 语音识别测试 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-microphone card-icon"></i>
          <h3>语音识别测试</h3>
          <p>测试语音识别功能</p>
          <el-button type="primary" @click="$router.push('/speech-test')">
            开始测试
          </el-button>
        </div>
      </el-card>

      <!-- 地图演示 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-map-location card-icon"></i>
          <h3>地图演示</h3>
          <p>查看地图功能演示</p>
          <el-button type="primary" @click="$router.push('/map-demo')">
            查看演示
          </el-button>
        </div>
      </el-card>

      <!-- 地图API测试 -->
      <el-card class="nav-card" shadow="hover">
        <div class="card-content">
          <i class="el-icon-data-analysis card-icon"></i>
          <h3>地图API测试</h3>
          <p>测试地图相关接口</p>
          <el-button type="primary" @click="$router.push('/map-api-test')">
            开始测试
          </el-button>
        </div>
      </el-card>
    </div>

    <!-- 连接状态显示 -->
    <div v-if="connectionStatus" class="connection-status">
      <el-alert 
        :title="connectionStatus.title" 
        :type="connectionStatus.type" 
        :closable="false"
        show-icon>
      </el-alert>
    </div>
    <el-row :gutter="20">
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="feature-card" @click="navigateTo('/ai-planning')">
          <div class="feature-icon">🤖</div>
          <h3>智能行程规划</h3>
          <p>AI为您生成个性化旅行路线</p>
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

// 在methods中添加导航方法
const navigateTo = (path: string) => {
  router.push(path)
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