<template>
  <div class="travel-plans">
    <h2>旅行计划</h2>
    <el-button @click="fetchTravelPlans">获取旅行计划</el-button>
    <div v-if="travelPlans.length > 0">
      <el-card v-for="plan in travelPlans" :key="plan.id" class="plan-card">
        <h3>{{ plan.destination }}</h3>
        <p>时长: {{ plan.duration }}</p>
        <p>预算: ¥{{ plan.budget }}</p>
        <p>季节: {{ plan.season }}</p>
      </el-card>
    </div>
    <p v-else>暂无旅行计划数据</p>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const travelPlans = ref([])

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
.plan-card {
  margin: 10px 0;
  max-width: 300px;
}
</style>