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
          <el-form-item label="旅行需求" required>
            <div class="travel-requirements-input">
              <el-input 
                v-model="planForm.travelRequirements" 
                type="textarea"
                :rows="3"
                placeholder="请输入旅行的目的地、天数、预算、同行人数，例如：日本东京，7天，预算15000元，2人同行"
                :autosize="{ minRows: 3, maxRows: 6 }"
              />
              <!-- 语音输入按钮 -->
              <div class="voice-input-container">
                <el-button 
                  v-if="!isRecording" 
                  type="primary" 
                  circle 
                  size="small"
                  @click="startVoiceInput"
                  :disabled="isWebSocketConnected"
                  class="voice-btn"
                >
                  <el-icon><microphone /></el-icon>
                </el-button>
                
                <el-button 
                  v-else 
                  type="danger" 
                  circle 
                  size="small"
                  @click="stopVoiceInput"
                  class="voice-btn"
                >
                  <el-icon><video-pause /></el-icon>
                </el-button>
                
                <div v-if="isRecording" class="recording-status">
                  <span class="recording-dot"></span>
                  <span>正在录音...</span>
                </div>
              </div>
            </div>
          </el-form-item>
          
          <!-- 添加间距分隔符 -->
          <div class="section-divider"></div>
          
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
            </div>
            
            <!-- 显示选中偏好的详细信息 - 移动到下方 -->
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
              :disabled="!planForm.travelRequirements"
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
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores'
import { useUserPreferenceStore } from '@/stores'
import { ElMessage } from 'element-plus'
import MarkdownIt from 'markdown-it'
import UserPreferenceManager from '@/components/UserPreferenceManager.vue'
import { Microphone, VideoPause, InfoFilled } from '@element-plus/icons-vue'

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
  travelRequirements: '', // 合并后的旅行需求输入
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
const selectedPreferenceId = ref('')

// 语音输入相关状态
const isRecording = ref(false)
const isWebSocketConnected = ref(false)
const websocket = ref<WebSocket | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const audioContext = ref<AudioContext | null>(null)
const audioProcessor = ref<ScriptProcessorNode | null>(null)

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

onUnmounted(() => {
  // 清理语音输入资源
  stopVoiceInput()
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

// 语音输入功能
const startVoiceInput = async () => {
  try {
    // 获取麦克风权限
    mediaStream.value = await navigator.mediaDevices.getUserMedia({ 
      audio: {
        sampleRate: 16000,        // 16kHz采样率
        channelCount: 1,          // 单声道
        echoCancellation: true,   // 回声消除
        noiseSuppression: true    // 降噪
      } 
    })

    // 创建音频上下文
    audioContext.value = new AudioContext({ sampleRate: 16000 })
    
    // 创建音频源
    const source = audioContext.value.createMediaStreamSource(mediaStream.value)
    
    // 创建音频处理器（每32ms处理一次，512 samples at 16kHz）
    audioProcessor.value = audioContext.value.createScriptProcessor(512, 1, 1)
    
    // 设置音频处理回调
    audioProcessor.value.onaudioprocess = (event) => {
      if (websocket.value && websocket.value.readyState === WebSocket.OPEN) {
        // 获取音频数据
        const inputData = event.inputBuffer.getChannelData(0)
        
        // 转换为16位PCM格式
        const pcmData = float32ToPCM(inputData)
        
        // 发送音频数据
        websocket.value.send(pcmData)
      }
    }

    // 连接音频处理链
    source.connect(audioProcessor.value)
    audioProcessor.value.connect(audioContext.value.destination)
    
    // 创建WebSocket连接
    websocket.value = new WebSocket('ws://localhost:8000/api/v1/speech/transcribe')
    
    websocket.value.onopen = () => {
      isWebSocketConnected.value = true
      isRecording.value = true
      ElMessage.success('语音输入已开始，请开始说话...')
    }
    
    websocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        
        if (data.success && data.transcript) {
          // 将转录结果添加到输入框中
          planForm.travelRequirements = data.transcript
          
          if (data.is_final) {
            ElMessage.success('语音输入完成')
          }
        } else if (!data.success) {
          ElMessage.error(`语音识别错误: ${data.error}`)
        }
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket连接错误:', error)
      ElMessage.error('语音输入连接失败，请检查网络连接')
      stopVoiceInput()
    }
    
    websocket.value.onclose = () => {
      console.log('WebSocket连接关闭')
      isWebSocketConnected.value = false
      isRecording.value = false
    }
    
  } catch (error) {
    console.error('启动语音输入失败:', error)
    ElMessage.error('无法访问麦克风，请检查权限设置')
    stopVoiceInput()
  }
}

const stopVoiceInput = () => {
  // 关闭WebSocket连接
  if (websocket.value) {
    websocket.value.close()
    websocket.value = null
  }
  
  // 停止音频处理
  if (audioProcessor.value) {
    audioProcessor.value.disconnect()
    audioProcessor.value = null
  }
  
  // 关闭音频上下文
  if (audioContext.value) {
    audioContext.value.close()
    audioContext.value = null
  }
  
  // 停止媒体流
  if (mediaStream.value) {
    mediaStream.value.getTracks().forEach(track => track.stop())
    mediaStream.value = null
  }
  
  isRecording.value = false
  isWebSocketConnected.value = false
}

// 将Float32音频数据转换为16位PCM格式
const float32ToPCM = (input: Float32Array): ArrayBuffer => {
  const buffer = new ArrayBuffer(input.length * 2)
  const view = new DataView(buffer)
  
  for (let i = 0; i < input.length; i++) {
    const s = Math.max(-1, Math.min(1, input[i]))
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
  
  return buffer
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

// 解析旅行需求文本
const parseTravelRequirements = (text: string) => {
  const result = {
    destination: '',
    duration: 3,
    budget: 5000,
    travelers: 2,
    valid: false
  }
  
  if (!text.trim()) return result
  
  const textLower = text.toLowerCase()
  
  // 提取目的地（通常是最前面的部分）
  const destinationMatch = text.match(/^[^，,]+/)
  if (destinationMatch) {
    result.destination = destinationMatch[0].trim()
  }
  
  // 提取天数
  const daysMatch = text.match(/(\d+)\s*天/)
  if (daysMatch) {
    result.duration = parseInt(daysMatch[1])
  }
  
  // 提取预算
  const budgetMatch = text.match(/预算?\s*(\d+)/) || text.match(/(\d+)\s*元/)
  if (budgetMatch) {
    result.budget = parseInt(budgetMatch[1])
  }
  
  // 提取同行人数
  const peopleMatch = text.match(/(\d+)\s*人/) || text.match(/同行\s*(\d+)/)
  if (peopleMatch) {
    result.travelers = parseInt(peopleMatch[1])
  }
  
  // 验证是否至少包含目的地
  result.valid = result.destination.length > 0
  
  return result
}
// 生成旅行计划
const generatePlan = async () => {
  // 解析用户输入的旅行需求
  const parsedRequirements = parseTravelRequirements(planForm.travelRequirements)
  
  if (!parsedRequirements.valid) {
    ElMessage.warning('请输入有效的旅行需求，至少包含目的地信息')
    return
  }

  generating.value = true
  planResult.value = null

  try {
    // 构建请求数据，使用解析后的参数
    const requestData = {
      destination: parsedRequirements.destination,
      duration: parsedRequirements.duration,
      budget: parsedRequirements.budget,
      travelers: parsedRequirements.travelers,
      preferences: planForm.preferences,
      special_requirements: planForm.specialRequirements
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
  margin-bottom: 30px;
}

.input-section h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 18px;
}

.input-hint {
  margin-top: 8px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-radius: 4px;
  border-left: 4px solid #409EFF;
  width: 100%; /* 添加宽度100%使其与输入框同宽 */
  box-sizing: border-box; /* 确保padding和border包含在宽度内 */
}

.input-hint p {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

/* 添加间距分隔符样式 */
.section-divider {
  height: 20px; /* 增加间距 */
  margin: 20px 0; /* 上下各20px间距 */
  border-bottom: 1px solid #e4e7ed; /* 可选：添加分隔线 */
}

.result-section {
  margin-top: 30px;
}

.result-section h3 {
  color: #333;
  margin-bottom: 20px;
  font-size: 18px;
}

.plan-section {
  margin-bottom: 20px;
}

.section-title {
  font-weight: bold;
  font-size: 16px;
}

.itinerary-content {
  line-height: 1.6;
}

.budget-content,
.weather-content {
  padding: 10px 0;
}

.recommendations-content {
  padding: 10px 0;
}

.error-message {
  margin-top: 20px;
}

/* 偏好选择区域样式 */
.preference-loading,
.preference-error {
  margin-bottom: 15px;
}

.preference-selection {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.preference-details {
  width: 100%;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
  border-radius: 8px;
  padding: 15px;
  margin-top: 15px;
  border: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.preference-details:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.preference-info h4 {
  margin: 0 0 10px 0;
  color: #409EFF;
  font-size: 16px;
  font-weight: 600;
}

.preference-content {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.preference-item {
  display: flex;
  align-items: flex-start; /* 改为align-items: center让字段名和值在同一水平线 */
  gap: 8px;
}

.preference-item strong {
  min-width: 80px;
  color: #606266;
  font-weight: 600;
  line-height: 1.5; /* 添加行高确保垂直居中 */
}

.preference-item span {
  flex: 1;
  color: #303133;
  line-height: 1.5; /* 确保行高一致 */
}

.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 14px;
  line-height: 1.6;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body p {
  margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-body li {
  margin-bottom: 8px;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 6px;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body pre code {
  background: none;
  padding: 0;
}

/* 语音输入样式 */
.travel-requirements-input {
  position: relative;
}

.voice-input-container {
  position: absolute;
  right: 10px;
  top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.voice-btn {
  width: 32px;
  height: 32px;
}

.recording-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #f56c6c;
}

.recording-dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

/* 确保输入框有足够的右边距给语音按钮 */
:deep(.el-textarea__inner) {
  padding-right: 50px;
  width: calc(100% - 20px); /* 距离父组件右边缘20px */
  margin-right: 20px; /* 添加右边距 */
}

/* 语音输入样式 */
.travel-requirements-input {
  position: relative;
  width: 100%; /* 确保容器宽度为100% */
}

.voice-input-container {
  position: absolute;
  right: 30px; /* 调整位置，考虑右边距 */
  top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10; /* 确保按钮在输入框上方 */
}

.voice-btn {
  width: 32px;
  height: 32px;
}

.recording-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #f56c6c;
}

.recording-dot {
  width: 8px;
  height: 8px;
  background-color: #f56c6c;
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

/* 调整el-form-item的宽度 */
:deep(.el-form-item__content) {
  width: 100%;
}

/* 确保输入框容器宽度正确 */
:deep(.el-textarea) {
  width: 100%;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body pre code {
  background: none;
  padding: 0;
}
</style>