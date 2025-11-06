<template>
  <div class="profile-container">
    <el-card class="profile-card">
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
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'
import dayjs from 'dayjs'

const router = useRouter()
const authStore = useAuthStore()

const formatDate = (dateString: string | undefined) => {
  if (!dateString) return ''
  return dayjs(dateString).format('YYYY-MM-DD HH:mm:ss')
}

const handleLogout = async () => {
  await authStore.logout()
  ElMessage.success('已退出登录')
  router.push('/login')
}

onMounted(async () => {
  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.getUserProfile()
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