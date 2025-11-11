<template>
  <div class="user-profile">
    <div class="page-header">
      <h2>个人中心</h2>
      <p>管理您的账户信息和旅行偏好</p>
    </div>
    
    <div class="profile-content">
      <!-- 基本信息卡片 -->
      <el-card class="profile-card">
        <template #header>
          <div class="card-header">
            <span>基本信息</span>
          </div>
        </template>
        
        <div class="user-info">
          <div class="info-item">
            <label>用户名：</label>
            <span>{{ authStore.user?.username || '未设置' }}</span>
          </div>
          <!-- 移除用户ID显示 -->
          <div class="info-item">
            <label>注册时间：</label>
            <span>{{ formatDate(authStore.user?.created_at) }}</span>
          </div>
        </div>
      </el-card>
      
      <!-- 旅行偏好管理卡片 -->
      <el-card class="preference-card">
        <template #header>
          <div class="card-header">
            <span>旅行偏好管理</span>
            <el-button 
              type="primary" 
              size="small" 
              @click="showPreferenceManager = true"
            >
              管理偏好
            </el-button>
          </div>
        </template>
        
        <!-- 加载状态 -->
        <div v-if="preferenceStore.loading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="preferenceStore.error" class="error-state">
          <el-alert
            :title="`加载偏好失败: ${preferenceStore.error}`"
            type="error"
            show-icon
            :closable="false"
          />
          <el-button type="primary" @click="loadUserPreferences" style="margin-top: 10px;">
            重试加载
          </el-button>
        </div>
        
        <!-- 当前偏好信息 -->
        <div v-else-if="preferenceStore.preferences.length > 0" class="current-preference">
          <div class="preferences-list">
            <div v-for="preference in preferenceStore.preferences" :key="preference.id" class="preference-item">
              <div class="preference-header">
                <h4>{{ preference.name || '未命名偏好' }}</h4>
                <el-tag size="small" type="info">
                  {{ formatDate(preference.created_at) }}
                </el-tag>
              </div>
              
              <div class="preference-content">
                <div v-if="preference.travel_preferences" class="preference-field">
                  <label>旅行偏好：</label>
                  <span>{{ preference.travel_preferences }}</span>
                </div>
                <div v-if="preference.special_requirements" class="preference-field">
                  <label>特殊需求：</label>
                  <span>{{ preference.special_requirements }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 无偏好提示 -->
        <div v-else class="no-preference">
          <el-empty description="暂无偏好设置" :image-size="80">
            <p class="empty-text">您还没有设置旅行偏好</p>
            <el-button type="primary" @click="showPreferenceCreator = true">立即创建</el-button>
          </el-empty>
        </div>
      </el-card>
      
      <!-- 操作卡片 -->
      <el-card class="action-card">
        <template #header>
          <div class="card-header">
            <span>账户操作</span>
          </div>
        </template>
        
        <div class="action-buttons">
          <el-button type="danger" @click="handleLogout">退出登录</el-button>
        </div>
      </el-card>
    </div>
    
    <!-- 偏好管理对话框 -->
    <el-dialog 
      v-model="showPreferenceManager" 
      title="管理旅行偏好" 
      width="700px"
      :before-close="handleDialogClose"
    >
      <UserPreferenceManager 
        @preference-updated="handlePreferenceUpdated"
        @preference-created="handlePreferenceCreated"
        @preference-deleted="handlePreferenceDeleted"
      />
    </el-dialog>
    
    <!-- 偏好创建对话框 -->
    <el-dialog 
      v-model="showPreferenceCreator" 
      title="创建旅行偏好" 
      width="600px"
      :before-close="handleDialogClose"
    >
      <UserPreferenceCreator 
        @preference-created="handlePreferenceCreated"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { useUserPreferenceStore } from '@/stores'
import { ElMessage } from 'element-plus'
import UserPreferenceManager from '@/components/UserPreferenceManager.vue'
import UserPreferenceCreator from '@/components/UserPreferenceCreator.vue'

const router = useRouter()
const authStore = useAuthStore()
const preferenceStore = useUserPreferenceStore()

// 状态管理
const showPreferenceManager = ref(false)
const showPreferenceCreator = ref(false)

// 生命周期
onMounted(async () => {
  await loadUserPreferences()
})

// 方法
const loadUserPreferences = async () => {
  try {
    console.log('🚀 开始加载偏好数据...')
    console.log('当前用户ID:', authStore.user?.id)
    console.log('认证状态:', authStore.isAuthenticated)
    console.log('Token:', authStore.token ? '存在' : '不存在')
    
    await preferenceStore.fetchUserPreferences()
    console.log('偏好数据加载完成，状态:', {
      loading: preferenceStore.loading,
      error: preferenceStore.error,
      preferencesCount: preferenceStore.preferences.length,
      preferences: preferenceStore.preferences
    })
    
    if (preferenceStore.preferences.length === 0) {
      console.log('用户没有偏好设置，显示空状态')
    }
  } catch (error) {
    console.error('❌ 偏好数据加载失败:', error)
    // 添加更详细的错误信息
    if (error.response) {
      console.error('HTTP错误状态码:', error.response.status)
      console.error('错误响应数据:', error.response.data)
      console.error('错误响应头:', error.response.headers)
    } else if (error.request) {
      console.error('请求未收到响应，可能是网络问题或后端服务未启动')
      console.error('请检查:')
      console.error('1. 后端服务是否运行 (python main.py)')
      console.error('2. 网络连接是否正常')
      console.error('3. CORS配置是否正确')
    } else {
      console.error('请求配置错误:', error.message)
    }
    ElMessage.error('加载偏好数据失败，请检查网络连接或联系管理员')
  }
}

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('退出登录成功')
    router.push('/login')
  } catch (error) {
    ElMessage.error('退出登录失败')
  }
}

const handlePreferenceUpdated = async (updatedPreference: any) => {
  showPreferenceManager.value = false
  await loadUserPreferences()
  ElMessage.success('偏好更新成功')
}

const handlePreferenceCreated = async (newPreference: any) => {
  showPreferenceCreator.value = false
  await loadUserPreferences()
  ElMessage.success('偏好创建成功')
}

const handlePreferenceDeleted = async () => {
  showPreferenceManager.value = false
  await loadUserPreferences()
  ElMessage.success('偏好删除成功')
}

const handleDialogClose = (done: () => void) => {
  done()
}

const formatDate = (dateString: string | null) => {
  if (!dateString) return '未知'
  return new Date(dateString).toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-profile {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
}

.page-header h2 {
  color: #409EFF;
  margin-bottom: 10px;
}

.page-header p {
  color: #666;
  margin: 0;
}

.profile-content {
  display: grid;
  gap: 20px;
}

.profile-card,
.preference-card,
.action-card {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header span {
  font-weight: bold;
  font-size: 16px;
}

.user-info {
  display: grid;
  gap: 15px;
}

.info-item {
  display: flex;
  align-items: center;
}

.info-item label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
  margin-right: 10px;
}

.info-item span {
  color: #333;
}

.current-preference {
  padding: 15px 0;
}

.preference-section {
  margin-bottom: 20px;
}

.preference-section h4 {
  color: #333;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: bold;
}

.preference-content {
  color: #666;
  line-height: 1.6;
  margin: 0;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
}

.preference-meta {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.preference-meta small {
  color: #909399;
  margin-right: 15px;
}

.no-preference {
  text-align: center;
  padding: 30px 0;
}

.empty-text {
  margin-bottom: 15px;
  color: #666;
}

.action-buttons {
  display: flex;
  justify-content: center;
}

/* 加载状态样式 */
.loading-state {
  padding: 20px;
}

/* 错误状态样式 */
.error-state {
  padding: 20px;
  text-align: center;
}

/* 偏好列表样式 */
.preferences-list {
  display: grid;
  gap: 15px;
}

.preference-item {
  padding: 15px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  background-color: #fafafa;
}

.preference-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.preference-header h4 {
  margin: 0;
  color: #303133;
}

.preference-content {
  display: grid;
  gap: 8px;
}

.preference-field {
  display: flex;
  align-items: flex-start;
}

.preference-field label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
  margin-right: 10px;
}

.preference-field span {
  color: #333;
  flex: 1;
}
</style>