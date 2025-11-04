<template>
  <div class="home">
    <h2>欢迎使用AI旅行规划师</h2>
    <el-card>
      <p>这是一个基于AI的智能旅行规划应用</p>
      <el-button type="primary" @click="$router.push('/travel-plans')">
        查看旅行计划
      </el-button>
      <el-button @click="testBackendConnection">
        测试后端连接
      </el-button>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import axios from 'axios'

const testResult = ref('')

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
}
</style>