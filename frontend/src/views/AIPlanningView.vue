<template>
  <div class="ai-planning">
    <div class="page-header">
      <h2>智能行程规划</h2>
      <p>AI为您生成个性化旅行路线</p>
    </div>
    
    <el-card class="content-card">
      <!-- 输入区域 -->
      <div class="input-section">
        <h3>输入旅行需求</h3>
        <el-form :model="planForm" label-width="100px">
          <el-form-item label="目的地">
            <el-input v-model="planForm.destination" placeholder="例如：日本东京" />
          </el-form-item>
          
          <el-form-item label="旅行天数">
            <el-input-number v-model="planForm.duration" :min="1" :max="30" />
          </el-form-item>
          
          <el-form-item label="预算(元)">
            <el-input-number v-model="planForm.budget" :min="1000" :step="1000" />
          </el-form-item>
          
          <el-form-item label="同行人数">
            <el-input-number v-model="planForm.travelers" :min="1" :max="10" />
          </el-form-item>
          
          <el-form-item label="旅行偏好">
            <el-input 
              v-model="planForm.preferences" 
              type="textarea" 
              :rows="3"
              placeholder="例如：喜欢美食、购物、历史文化、自然风光等" 
            />
          </el-form-item>
          
          <el-form-item label="特殊需求">
            <el-input 
              v-model="planForm.specialRequirements" 
              type="textarea" 
              :rows="2"
              placeholder="例如：带孩子、有老人、需要无障碍设施等" 
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              :loading="generating" 
              @click="generatePlan"
              :disabled="!planForm.destination"
            >
              {{ generating ? 'AI规划中...' : '生成智能行程' }}
            </el-button>
          </el-form-item>
        </el-form>
      </div>
      
      <!-- 结果显示区域 -->
      <div v-if="planResult" class="result-section">
        <h3>AI生成的旅行计划</h3>
        
        <div v-if="planResult.status === 'success'" class="plan-details">
          <!-- 行程安排 -->
          <el-card class="plan-section">
            <template #header>
              <span class="section-title">📅 行程安排</span>
            </template>
            <div class="itinerary-content markdown-body" v-html="renderMarkdown(planResult.itinerary)"></div>
          </el-card>
          
          <!-- 预算使用 -->
          <el-card v-if="Object.keys(planResult.budget_usage).length > 0" class="plan-section">
            <template #header>
              <span class="section-title">💰 预算分配</span>
            </template>
            <div class="budget-content">
              <el-descriptions :column="2" border>
                <el-descriptions-item 
                  v-for="(amount, category) in planResult.budget_usage" 
                  :key="category"
                  :label="category"
                >
                  ¥{{ amount }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
          
          <!-- 推荐信息 -->
          <el-card v-if="planResult.recommendations && planResult.recommendations.length > 0" class="plan-section">
            <template #header>
              <span class="section-title">⭐ 推荐信息</span>
            </template>
            <div class="recommendations-content">
              <el-timeline>
                <el-timeline-item 
                  v-for="(rec, index) in planResult.recommendations" 
                  :key="index"
                  :timestamp="rec.time || '全天'"
                  placement="top"
                >
                  <el-card>
                    <h4>{{ rec.name }}</h4>
                    <p>{{ rec.description }}</p>
                    <el-tag v-if="rec.type" :type="getTagType(rec.type)">
                      {{ rec.type }}
                    </el-tag>
                  </el-card>
                </el-timeline-item>
              </el-timeline>
            </div>
          </el-card>
          
          <!-- 天气信息 -->
          <el-card v-if="planResult.weather_info && Object.keys(planResult.weather_info).length > 0" class="plan-section">
            <template #header>
              <span class="section-title">🌤️ 天气信息</span>
            </template>
            <div class="weather-content">
              <el-descriptions :column="1" border>
                <el-descriptions-item 
                  v-for="(value, key) in planResult.weather_info" 
                  :key="key"
                  :label="formatWeatherKey(key)"
                >
                  {{ value }}
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-card>
        </div>
        
        <div v-else class="error-message">
          <el-alert
            title="生成失败"
            :description="planResult.error || '未知错误'"
            type="error"
            show-icon
          />
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'

const router = useRouter()
const authStore = useAuthStore()

// 初始化Markdown解析器
const md = new MarkdownIt({
  html: true,        // 允许HTML标签
  linkify: true,     // 自动转换URL为链接
  typographer: true, // 启用一些语言替换和引号美化
  breaks: true       // 将换行符转换为<br>
})

// 表单数据
const planForm = reactive({
  destination: '',
  duration: 3,
  budget: 5000,
  travelers: 2,
  preferences: '',
  specialRequirements: ''
})

// 状态管理
const generating = ref(false)
const planResult = ref<any>(null)

// 生成旅行计划
const generatePlan = async () => {
  if (!planForm.destination) {
    ElMessage.warning('请输入目的地')
    return
  }

  generating.value = true
  planResult.value = null

  try {
    const response = await axios.post('http://localhost:8000/api/v1/ai/plan', planForm)
    planResult.value = response.data
    ElMessage.success('旅行计划生成成功！')
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    planResult.value = {
      status: 'error',
      error: error.response?.data?.detail || '生成失败，请重试'
    }
    ElMessage.error('生成旅行计划失败')
  } finally {
    generating.value = false
  }
}

// 渲染Markdown内容
const renderMarkdown = (text: string) => {
  if (!text) return ''
  return md.render(text)
}

// 格式化天气键名
const formatWeatherKey = (key: string) => {
  const map: Record<string, string> = {
    'temperature': '温度',
    'weather': '天气',
    'humidity': '湿度',
    'forecast': '预报'
  }
  return map[key] || key
}

// 获取标签类型
const getTagType = (type: string) => {
  const typeMap: Record<string, any> = {
    'attraction': 'success',
    'food': 'warning',
    'accommodation': 'info',
    'transport': 'primary'
  }
  return typeMap[type] || 'default'
}
</script>

<style scoped>
.ai-planning {
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
  padding: 30px;
}

.input-section {
  margin-bottom: 40px;
}

.input-section h3 {
  color: #333;
  margin-bottom: 20px;
  border-left: 4px solid #409EFF;
  padding-left: 10px;
}

.result-section {
  margin-top: 30px;
}

.plan-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: bold;
  font-size: 16px;
}

/* Markdown内容样式 */
.itinerary-content {
  line-height: 1.6;
}

.itinerary-content :deep(h1) {
  color: #409EFF;
  border-bottom: 2px solid #409EFF;
  padding-bottom: 10px;
  margin: 20px 0 15px 0;
}

.itinerary-content :deep(h2) {
  color: #67C23A;
  margin: 15px 0 10px 0;
}

.itinerary-content :deep(h3) {
  color: #E6A23C;
  margin: 10px 0 8px 0;
}

.itinerary-content :deep(p) {
  margin: 8px 0;
}

.itinerary-content :deep(ul),
.itinerary-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.itinerary-content :deep(li) {
  margin: 4px 0;
}

.itinerary-content :deep(blockquote) {
  border-left: 4px solid #409EFF;
  background-color: #f0f7ff;
  padding: 10px 15px;
  margin: 10px 0;
  border-radius: 4px;
}

.itinerary-content :deep(code) {
  background-color: #f4f4f5;
  padding: 2px 6px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
}

.itinerary-content :deep(pre) {
  background-color: #f4f4f5;
  padding: 15px;
  border-radius: 6px;
  overflow-x: auto;
  margin: 10px 0;
}

.itinerary-content :deep(pre code) {
  background: none;
  padding: 0;
}

.itinerary-content :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

.itinerary-content :deep(th),
.itinerary-content :deep(td) {
  border: 1px solid #dcdfe6;
  padding: 8px 12px;
  text-align: left;
}

.itinerary-content :deep(th) {
  background-color: #f5f7fa;
  font-weight: bold;
}

.itinerary-content :deep(a) {
  color: #409EFF;
  text-decoration: none;
}

.itinerary-content :deep(a:hover) {
  text-decoration: underline;
}

.budget-content,
.weather-content {
  max-width: 600px;
}

.recommendations-content {
  max-width: 800px;
}

.error-message {
  margin-top: 20px;
}
</style>