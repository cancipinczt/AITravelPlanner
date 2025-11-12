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
      
      <!-- 旅行计划管理卡片 -->
      <el-card class="trips-card">
        <template #header>
          <div class="card-header">
            <span>旅行计划管理</span>
            <el-button 
              type="primary" 
size="small" 
              @click="goToAIPlanning"
            >
              创建新计划
            </el-button>
          </div>
        </template>
        
        <!-- 加载状态 -->
        <div v-if="tripsLoading" class="loading-state">
          <el-skeleton :rows="3" animated />
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="tripsError" class="error-state">
          <el-alert
            :title="`加载旅行计划失败: ${tripsError}`"
            type="error"
            show-icon
            :closable="false"
          />
          <el-button type="primary" @click="loadTrips" style="margin-top: 10px;">
            重试加载
          </el-button>
        </div>
        
        <!-- 旅行计划列表 -->
        <div v-else-if="trips.length > 0" class="trips-list">
          <el-table :data="trips" style="width: 100%">
            <el-table-column prop="title" label="标题" min-width="120" />
            <el-table-column prop="destination" label="目的地" min-width="100" />
            <el-table-column prop="budget" label="预算" min-width="100">
              <template #default="scope">
                {{ scope.row.budget ? `¥${scope.row.budget}` : '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="travelers_count" label="同行人数" min-width="100" />
            <el-table-column prop="days" label="天数" min-width="80" />
            <el-table-column prop="preference_name" label="偏好" min-width="120">
              <template #default="scope">
                {{ scope.row.preference_name || '未设置' }}
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" min-width="120">
              <template #default="scope">
                {{ formatDate(scope.row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="操作" min-width="120" fixed="right">
              <template #default="scope">
                <el-button size="small" @click="editTrip(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteTrip(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <!-- 无旅行计划提示 -->
        <div v-else class="no-trips">
          <el-empty description="暂无旅行计划" :image-size="80">
            <p class="empty-text">您还没有创建任何旅行计划</p>
            <el-button type="primary" @click="goToAIPlanning">立即创建</el-button>
          </el-empty>
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
    
    <!-- 编辑旅行计划对话框 -->
    <el-dialog 
      v-model="showTripEditDialog" 
      :title="`编辑旅行计划 - ${editingTrip?.title}`" 
      width="1000px"
      top="5vh"
    >
      <el-form :model="editingTrip" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="editingTrip.title" />
        </el-form-item>
        <el-form-item label="目的地">
          <el-input v-model="editingTrip.destination" />
        </el-form-item>
        <el-form-item label="预算">
          <el-input-number v-model="editingTrip.budget" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="同行人数">
          <el-input-number v-model="editingTrip.travelers_count" :min="1" />
        </el-form-item>
        <el-form-item label="天数">
          <el-input-number v-model="editingTrip.days" :min="1" />
        </el-form-item>
        <!-- 添加计划内容编辑 -->
        <el-form-item label="行程计划">
          <el-input 
            v-model="editingTrip.plan" 
            type="textarea" 
            :rows="20"
            placeholder="请输入详细的行程计划内容"
            style="width: 100%;"
          />
        </el-form-item>
      </el-form>
      
<template #footer>
        <el-button @click="showTripEditDialog = false">取消</el-button>
        <el-button type="primary" @click="updateTrip">保存</el-button>
      </template>
    </el-dialog>
    
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
import { ElMessage, ElMessageBox } from 'element-plus'
import UserPreferenceManager from '@/components/UserPreferenceManager.vue'
import UserPreferenceCreator from '@/components/UserPreferenceCreator.vue'

const router = useRouter()
const authStore = useAuthStore()
const preferenceStore = useUserPreferenceStore()

// 状态管理
const showPreferenceManager = ref(false)
const showPreferenceCreator = ref(false)
const showTripEditDialog = ref(false)
const trips = ref([])
const tripsLoading = ref(false)
const tripsError = ref('')
const editingTrip = ref(null)

// 生命周期
onMounted(async () => {
  await loadUserPreferences()
  await loadTrips()
})

// 方法
const loadTrips = async () => {
  tripsLoading.value = true
  tripsError.value = ''
  try {
    const response = await fetch('http://localhost:8000/api/v1/trips', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const data = await response.json()
    trips.value = data
  } catch (error) {
    console.error('加载旅行计划失败:', error)
    tripsError.value = error.message
    ElMessage.error('加载旅行计划失败')
  } finally {
    tripsLoading.value = false
  }
}

const loadUserPreferences = async () => {
  try {
    await preferenceStore.fetchUserPreferences()
  } catch (error) {
    console.error('偏好数据加载失败:', error)
    ElMessage.error('加载偏好数据失败，请检查网络连接或联系管理员')
  }
}

const goToAIPlanning = () => {
  router.push('/ai-planning')
}

const editTrip = async (trip) => {
  try {
    // 先获取该旅行计划的完整信息（包含plan字段）
    const response = await fetch(`http://localhost:8000/api/v1/trips/${trip.id}`, {
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const fullTripData = await response.json()
    editingTrip.value = { ...fullTripData }
    showTripEditDialog.value = true
  } catch (error) {
    console.error('获取旅行计划详情失败:', error)
    ElMessage.error('获取旅行计划详情失败，使用基本信息编辑')
    // 如果获取详情失败，使用基本信息进行编辑
    editingTrip.value = { ...trip }
    showTripEditDialog.value = true
  }
}

const updateTrip = async () => {
  try {
    const response = await fetch(`http://localhost:8000/api/v1/trips/${editingTrip.value.id}`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        title: editingTrip.value.title,
        destination: editingTrip.value.destination,
        budget: editingTrip.value.budget,
        travelers_count: editingTrip.value.travelers_count,
        days: editingTrip.value.days,
        plan: editingTrip.value.plan // 添加plan字段的更新
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    ElMessage.success('旅行计划更新成功')
    showTripEditDialog.value = false
    await loadTrips()
  } catch (error) {
    console.error('更新旅行计划失败:', error)
    ElMessage.error('更新旅行计划失败')
  }
}

const deleteTrip = async (trip) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除旅行计划"${trip.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    
    const response = await fetch(`http://localhost:8000/api/v1/trips/${trip.id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`,
      }
    })
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    ElMessage.success('旅行计划删除成功')
    await loadTrips()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除旅行计划失败:', error)
      ElMessage.error('删除旅行计划失败')
    }
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
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  backdrop-filter: blur(10px);
}

.page-header h2 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  background: linear-gradient(45deg, #fff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 18px;
  opacity: 0.9;
  font-weight: 500;
}

.profile-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
  padding: 32px;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid rgba(102, 126, 234, 0.1);
}

.avatar-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.user-avatar {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  font-size: 32px;
  font-weight: 700;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.3);
}

.user-info {
  flex: 1;
}

.user-name {
  font-size: 28px;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 8px;
}

.user-email {
  font-size: 16px;
  color: #666;
  margin-bottom: 12px;
}

.user-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-top: 4px;
}

.profile-form {
  max-width: 500px;
}

.form-section {
  margin-bottom: 32px;
}

.form-section h3 {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.form-section h3::before {
  content: "👤";
  font-size: 18px;
}

:deep(.el-form-item) {
  margin-bottom: 20px;
}

:deep(.el-form-item__label) {
  font-weight: 600;
  color: #2c3e50;
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

.action-buttons {
  display: flex;
  gap: 16px;
  margin-top: 24px;
}

.save-button {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  border: none;
  border-radius: 10px;
  height: 44px;
  font-weight: 600;
  box-shadow: 0 4px 16px rgba(82, 196, 26, 0.3);
  transition: all 0.3s ease;
}

.save-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(82, 196, 26, 0.4);
}

.cancel-button {
  background: rgba(255, 255, 255, 0.9);
  border: 2px solid rgba(102, 126, 234, 0.3);
  color: #667eea;
  border-radius: 10px;
  height: 44px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.cancel-button:hover {
  background: rgba(102, 126, 234, 0.1);
  border-color: #667eea;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .user-profile {
    padding: 16px;
  }
  
  .page-header {
    padding: 24px 0;
    margin-bottom: 24px;
  }
  
  .page-header h2 {
    font-size: 28px;
  }
  
  .profile-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }
  
  .user-stats {
    justify-content: center;
  }
  
  .action-buttons {
    flex-direction: column;
  }
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
.trips-card,
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

.trips-list {
  margin-top: 15px;
}

.no-trips {
  text-align: center;
  padding: 30px 0;
}

.current-preference {
  padding: 15px 0;
}

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

.plan-field {
  display: flex;
  align-items: center;
}

.plan-field label {
  font-weight: bold;
  color: #606266;
  min-width: 60px;
  margin-right: 8px;
}

.plan-field span {
  color: #333;
}

.plan-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.more-plans {
  text-align: center;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #e4e7ed;
}
.no-plans {
  text-align: center;
  padding: 30px 0;
}
</style>