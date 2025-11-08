<template>
  <div class="profile-container">
    <el-card class="profile-card" v-loading="loading">
      <h2>个人中心</h2>
      <el-form>
        <el-form-item label="用户名">
          <el-input :value="authStore.user?.username" disabled />
        </el-form-item>
        <el-form-item label="注册时间">
          <el-input :value="formatDate(authStore.user?.created_at)" disabled />
        </el-form-item>
        <el-form-item label="最后更新">
          <el-input :value="formatDate(authStore.user?.updated_at)" disabled />
        </el-form-item>
      </el-form>
      <div class="profile-actions">
        <el-button @click="handleLogout">退出登录</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('已退出登录')
    // 添加页面跳转逻辑
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    ElMessage.error('登出失败')
  }
}

onMounted(async () => {
  loading.value = true
  try {
    const result = await authStore.getUserProfile()
    if (!result.success) {
      ElMessage.error(result.message || '获取用户信息失败')
    }
  } catch (error) {
    ElMessage.error('获取用户信息失败')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.profile-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;
  padding: 20px;
}

.profile-card {
  width: 500px;
  padding: 20px;
}

.profile-actions {
  text-align: center;
  margin-top: 20px;
}
</style>