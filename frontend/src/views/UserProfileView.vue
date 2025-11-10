<template>
  <div class="user-profile">
    <div class="profile-header">
      <h2>个人中心</h2>
      <p class="welcome-text">欢迎回来，{{ user?.username }}</p>
    </div>
    
    <!-- 加载状态 -->
    <div v-loading="loading" element-loading-text="加载中...">
      <div v-if="user" class="profile-content">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="info-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <i class="el-icon-user"></i>
                  <span>基本信息</span>
                </div>
              </template>
              <div class="info-item">
                <label>用户名：</label>
                <span>{{ user.username }}</span>
              </div>
              <div class="info-item">
                <label>注册时间：</label>
                <span>{{ formatDate(user.created_at) }}</span>
              </div>
              <div class="info-item">
                <label>最后更新：</label>
                <span>{{ formatDate(user.updated_at) }}</span>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="12">
            <el-card class="actions-card" shadow="hover">
              <template #header>
                <div class="card-header">
                  <i class="el-icon-setting"></i>
                  <span>操作</span>
                </div>
              </template>
              <div class="action-buttons">
                <el-button type="danger" @click="handleLogout">
                  <i class="el-icon-switch-button"></i>
                  退出登录
                </el-button>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <div v-else class="no-user">
        <el-result icon="warning" title="未获取到用户信息" sub-title="请尝试重新登录">
          <template #extra>
            <el-button type="primary" @click="router.push('/login')">重新登录</el-button>
          </template>
        </el-result>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { ElMessage, ElMessageBox } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()
const loading = ref(false)

const user = ref(authStore.user)

const formatDate = (dateString: string) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 获取用户信息
const getUserProfile = async () => {
  loading.value = true
  try {
    const result = await authStore.getUserProfile()
    user.value = authStore.user
    
    if (!result.success) {
      ElMessage.error(result.message || '获取用户信息失败')
    }
  } catch (error) {
    console.error('获取用户信息异常:', error)
    ElMessage.error('获取用户信息时发生异常')
  } finally {
    loading.value = false
  }
}

const handleLogout = async () => {
  try {
    await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    // 用户取消操作
  }
}

onMounted(() => {
  if (!authStore.user) {
    getUserProfile()
  } else {
    user.value = authStore.user
  }
})
</script>

<style scoped>
.user-profile {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.profile-header {
  text-align: center;
  margin-bottom: 30px;
}

.profile-header h2 {
  margin: 0;
  color: #303133;
  font-size: 28px;
}

.welcome-text {
  margin: 10px 0 0 0;
  color: #606266;
  font-size: 16px;
}

.profile-content {
  margin-top: 20px;
}

.info-card, .actions-card {
  height: 100%;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}

.card-header i {
  font-size: 18px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item label {
  font-weight: 500;
  color: #606266;
}

.info-item span {
  color: #303133;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 10px 0;
}

.action-buttons .el-button {
  width: 100%;
  justify-content: flex-start;
}

.no-user {
  margin-top: 50px;
}
</style>