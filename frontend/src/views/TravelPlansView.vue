<template>
  <div class="travel-plans">
    <div class="page-header">
      <h2>旅行计划</h2>
      <p>管理您的旅行计划</p>
    </div>
    
    <el-card class="content-card">
      <el-button type="primary" @click="fetchTravelPlans">获取旅行计划</el-button>
      
      <div v-if="travelPlans.length > 0" class="plans-container">
        <el-card v-for="plan in travelPlans" :key="plan.id" class="plan-card">
          <h3>{{ plan.destination }}</h3>
          <p>时长: {{ plan.duration }}</p>
          <p>预算: ¥{{ plan.budget }}</p>
          <p>季节: {{ plan.season }}</p>
        </el-card>
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
import axios from 'axios'
import { useAuthStore } from '@/stores'

const router = useRouter()
const authStore = useAuthStore()
const travelPlans = ref([])

// 页面加载时检查认证状态
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
})

const fetchTravelPlans = async () => {
  try {
    const response = await axios.get('http://localhost:8000/api/v1/travel/travel-plans')
    travelPlans.value = response.data.travel_plans
  } catch (error) {
    console.error('获取旅行计划失败:', error)
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