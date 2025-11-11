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
          
          <!-- 偏好选择区域 -->
          <el-form-item label="旅行偏好">
            <!-- 加载状态 -->
            <div v-if="preferenceStore.loading" class="preference-loading">
              <el-skeleton :rows="2" animated />
            </div>
            
            <!-- 错误状态 -->
            <div v-else-if="preferenceStore.error" class="preference-error">
              <el-alert
                :title="`加载偏好失败: ${preferenceStore.error}`"
                type="error"
                show-icon
                :closable="false"
                size="small"
              />
              <el-button type="primary" size="small" @click="loadUserPreferences" style="margin-top: 10px;">
                重试加载
              </el-button>
            </div>
            
            <!-- 偏好选择 -->
            <div v-else class="preference-selection">
              <el-select 
                v-model="selectedPreferenceId" 
                placeholder="请选择旅行偏好"
                style="width: 300px; margin-right: 10px;"
                @change="handlePreferenceChange"
              >
                <el-option 
                  v-for="preference in userPreferences" 
                  :key="preference.id"
                  :label="preference.name" 
                  :value="preference.id"
                />
              </el-select>
              
              <el-button 
                type="primary" 
                link 
                @click="showPreferenceDialog = true"
              >
                管理偏好
              </el-button>
              <el-button 
                type="success" 
                link 
                @click="showCreateDialog = true"
              >
                创建新偏好
              </el-button>
            </div>
            
            <!-- 显示选中偏好的详细信息 -->
            <div v-if="selectedPreference" class="preference-details">
              <div class="preference-info">
                <h4>{{ selectedPreference.name }}</h4>
                <div class="preference-content">
                  <div v-if="selectedPreference.travel_preferences" class="preference-item">
                    <strong>旅行偏好：</strong>
                    <span>{{ selectedPreference.travel_preferences }}</span>
                  </div>
                  <div v-if="selectedPreference.special_requirements" class="preference-item">
                    <strong>特殊需求：</strong>
                    <span>{{ selectedPreference.special_requirements }}</span>
                  </div>
                </div>
              </div>
            </div>
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

    <!-- 偏好管理对话框 -->
    <el-dialog 
      v-model="showPreferenceDialog" 
      title="管理旅行偏好" 
      width="600px"
      :before-close="handleDialogClose"
    >
      <UserPreferenceManager 
        @preference-updated="handlePreferenceUpdated"
        @preference-created="handlePreferenceCreated"
        @preference-deleted="handlePreferenceDeleted"
      />
    </el-dialog>

    <!-- 创建偏好对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      title="创建旅行偏好" 
      width="500px"
      :before-close="handleDialogClose"
    >
      <UserPreferenceCreator 
        @preference-created="handlePreferenceCreated"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores'
import { useUserPreferenceStore } from '@/stores'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import UserPreferenceManager from '@/components/UserPreferenceManager.vue'
import UserPreferenceCreator from '@/components/UserPreferenceCreator.vue'

const router = useRouter()
const authStore = useAuthStore()
const preferenceStore = useUserPreferenceStore()

// 初始化Markdown解析器
const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true,
  breaks: true
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
const showPreferenceDialog = ref(false)
const showCreateDialog = ref(false)
const selectedPreferenceId = ref('')

// 计算属性
const userPreferences = computed(() => {
  return preferenceStore.preferences
})

const selectedPreference = computed(() => {
  if (!selectedPreferenceId.value) return null
  return preferenceStore.getPreferenceById(selectedPreferenceId.value)
})

// 生命周期
onMounted(async () => {
  await loadUserPreferences()
})

// 方法
const loadUserPreferences = async () => {
  try {
    await preferenceStore.fetchUserPreferences()
    console.log('偏好数据加载成功:', preferenceStore.preferences)
  } catch (error) {
    console.error('偏好数据加载失败:', error)
    ElMessage.error('加载偏好数据失败，请检查网络连接')
  }
}

const handlePreferenceChange = (preferenceId: string) => {
  const preference = preferenceStore.getPreferenceById(preferenceId)
  if (preference) {
    // 自动填充偏好信息到表单
    planForm.preferences = preference.travel_preferences || ''
    planForm.specialRequirements = preference.special_requirements || ''
  }
}

const handlePreferenceUpdated = async (updatedPreference: any) => {
  await loadUserPreferences()
  // 如果更新的是当前选中的偏好，更新表单
  if (selectedPreferenceId.value === updatedPreference.id) {
    handlePreferenceChange(updatedPreference.id)
  }
}

const handlePreferenceCreated = async (newPreference: any) => {
  await loadUserPreferences()
  // 自动选择新创建的偏好
  selectedPreferenceId.value = newPreference.id
  handlePreferenceChange(newPreference.id)
}

const handlePreferenceDeleted = async (preferenceId: string) => {
  await loadUserPreferences()
  // 如果删除的是当前选中的偏好，清空选择
  if (selectedPreferenceId.value === preferenceId) {
    selectedPreferenceId.value = ''
    planForm.preferences = ''
    planForm.specialRequirements = ''
  }
}

const handleDialogClose = (done: () => void) => {
  done()
}

// 生成旅行计划
const generatePlan = async () => {
  if (!planForm.destination) {
    ElMessage.warning('请输入目的地')
    return
  }

  generating.value = true
  planResult.value = null

  try {
    // 构建请求数据，包含偏好信息
    const requestData = {
      destination: planForm.destination,
      duration: planForm.duration,
      budget: planForm.budget,
      travelers: planForm.travelers,
      preferences: planForm.preferences,
      specialRequirements: planForm.specialRequirements
    }

    const response = await axios.post('http://localhost:8000/api/v1/ai/plan', requestData)
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

.preference-selection {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.preference-details {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409EFF;
}

.preference-info h4 {
  margin: 0 0 10px 0;
  color: #409EFF;
  font-size: 16px;
  font-weight: bold;
}

.preference-content {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preference-item {
  display: flex;
  align-items: flex-start;
}

.preference-item strong {
  min-width: 80px;
  color: #606266;
  font-weight: bold;
}

.preference-item span {
  flex: 1;
  color: #333;
  line-height: 1.5;
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

/* 偏好加载状态样式 */
.preference-loading {
  padding: 10px;
}

/* 偏好错误状态样式 */
.preference-error {
  padding: 10px;
  text-align: center;
}

/* 偏好详情样式 */
.preference-details {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #409EFF;
}

.preference-info h4 {
  margin: 0 0 10px 0;
  color: #303133;
}

.preference-content {
  display: grid;
  gap: 8px;
}

.preference-item {
  display: flex;
  align-items: flex-start;
}

.preference-item strong {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
  margin-right: 10px;
}

.preference-item span {
  color: #333;
  flex: 1;
}