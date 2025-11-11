<template>
  <div class="travel-plans">
    <div class="page-header">
      <h2>旅行计划管理</h2>
      <p>管理您的所有旅行计划</p>
    </div>
    
    <el-card class="content-card">
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" @click="fetchTravelPlans" :loading="loading">
          <el-icon><refresh /></el-icon>
          刷新列表
        </el-button>
        <el-button type="success" @click="goToAIPlanning">
          <el-icon><plus /></el-icon>
          创建新计划
        </el-button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <el-alert
          :title="`加载失败: ${error}`"
          type="error"
          show-icon
          :closable="false"
        />
        <el-button type="primary" @click="fetchTravelPlans" style="margin-top: 10px;">
          重试加载
        </el-button>
      </div>
      
      <!-- 旅行计划列表 -->
      <div v-else-if="travelPlans.length > 0" class="plans-container">
        <el-table :data="travelPlans" style="width: 100%">
          <el-table-column prop="title" label="计划标题" min-width="200">
            <template #default="scope">
              <strong>{{ scope.row.title }}</strong>
            </template>
          </el-table-column>
          
          <el-table-column prop="destination" label="目的地" width="120">
            <template #default="scope">
              <el-tag type="primary">{{ scope.row.destination }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="days" label="天数" width="80" align="center">
            <template #default="scope">
              <span>{{ scope.row.days }}天</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="travelers_count" label="人数" width="80" align="center">
            <template #default="scope">
              <span>{{ scope.row.travelers_count }}人</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="budget" label="预算" width="120" align="right">
            <template #default="scope">
              <span v-if="scope.row.budget" class="budget-amount">
                ¥{{ scope.row.budget }}
              </span>
              <span v-else class="no-budget">未设置</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="preference_name" label="偏好" width="120">
            <template #default="scope">
              <span>{{ scope.row.preference_name }}</span>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="empty-state">
        <p>暂无旅行计划数据</p>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { api } from '@/stores'  // 直接导入api实例
import { Refresh, Plus } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const travelPlans = ref([])
const loading = ref(false)
const error = ref('')

// 页面加载时检查认证状态
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchTravelPlans()
})

const fetchTravelPlans = async () => {
  try {
    loading.value = true
    error.value = ''
    // 直接使用导入的api实例，路径不需要包含/api/v1前缀
    const response = await api.get('/trips')
    travelPlans.value = response.data
  } catch (err) {
    console.error('获取旅行计划失败:', err)
    error.value = err.response?.data?.detail || '网络错误'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.travel-plans {
  padding: 20px;
  max-width: 1200px;
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

.content-card {
  padding: 20px;
}

.plans-container {
  margin-top: 20px;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.plan-card {
  padding: 15px;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
}
</style>