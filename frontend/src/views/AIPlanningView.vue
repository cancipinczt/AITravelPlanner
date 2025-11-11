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
              :loading="generating || parsing" 
              @click="generatePlan"
              :disabled="!planForm.travelRequirements"
            >
              {{ parsing ? '解析需求中...' : (generating ? 'AI规划中...' : '生成智能行程') }}
            </el-button>
          </el-form-item>

          <!-- 添加解析结果显示区域 -->
          <div v-if="parsedRequirements.destination" class="parsed-info">
            <el-alert
              title="解析结果"
              type="info"
              :closable="false"
              show-icon
            >
              <p>目的地：{{ parsedRequirements.destination }}</p>
              <p>旅行天数：{{ parsedRequirements.duration }}天</p>
              <p>预算：¥{{ parsedRequirements.budget }}</p>
              <p>同行人数：{{ parsedRequirements.travelers }}人</p>
            </el-alert>
          </div>
        </el-form>
      </div>

      <!-- 结果显示区域 -->
      <div v-if="planResult" class="result-section">
        <h3>AI生成的旅行计划</h3>
        
        <div v-if="planResult.status === 'success'" class="plan-details">
          <!-- 创建旅行计划按钮 -->
          <div class="create-trip-section">
            <div class="trip-name-input">
              <el-form-item label="计划名称">
                <el-input 
                  v-model="tripTitle" 
                  placeholder="为您的旅行计划取一个名字，例如：东京5日游"
                  style="width: 300px; margin-right: 10px;"
                />
              </el-form-item>
            </div>
            
            <el-button 
              type="success" 
              size="large" 
              @click="createTripFromPlan"
              :loading="creatingTrip"
              :disabled="!tripTitle"
            >
              💾 保存为旅行计划
            </el-button>
            <p class="create-trip-hint">将此计划保存到您的旅行计划列表中</p>
          </div>
      
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
const creatingTrip = ref(false)
const creatingPlan = ref(false)

// 添加解析相关状态
const parsing = ref(false)
const parsedRequirements = ref({
  destination: '',
  duration: 0,
  budget: 0,
  travelers: 0
})

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

// 创建旅行计划方法
// 在状态管理部分添加tripTitle
const tripTitle = ref('')

// 导入store中配置的api实例
import { api } from '@/stores'

// 修改createTripFromPlan函数，使用配置好的api实例
const createTripFromPlan = async () => {
  if (!tripTitle.value.trim()) {
    ElMessage.warning('请输入旅行计划名称')
    return
  }
  
  try {
    creatingTrip.value = true
    
    // 使用解析出的数据创建旅行计划
    const tripData = {
      title: tripTitle.value,
      destination: parsedRequirements.value.destination,
      budget: parsedRequirements.value.budget,
      travelers_count: parsedRequirements.value.travelers,
      days: parsedRequirements.value.duration,
      plan: planResult.value.itinerary,
      preference_id: selectedPreferenceId.value || null
    }
    
    // 使用配置好的api实例，它会自动添加认证token
    const response = await api.post('/trips', tripData)
    
    ElMessage.success('旅行计划创建成功！')
    tripTitle.value = ''
    planResult.value = null
    
    // 可选：跳转到旅行计划页面或刷新列表
  } catch (error: any) {
    console.error('创建旅行计划失败:', error)
    ElMessage.error('创建旅行计划失败：' + (error.response?.data?.detail || '未知错误'))
  } finally {
    creatingTrip.value = false
  }
}

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
const parseTravelRequirements = async () => {
  try {
    parsing.value = true
    // 使用配置好的api实例
    const response = await api.post('/ai/parse-requirements', {
      travel_requirements: planForm.travelRequirements
    })
    
    if (response.data.status === 'success') {
      // 使用解析出的数据填充表单
      parsedRequirements.value = {
        destination: response.data.destination,
        duration: response.data.duration,
        budget: response.data.budget,
        travelers: response.data.travelers
      }
      return parsedRequirements.value
    } else {
      ElMessage.error('解析旅行需求失败：' + (response.data.error || '未知错误'))
      return null
    }
  } catch (error: any) {
    console.error('解析旅行需求失败:', error)
    ElMessage.error('解析旅行需求失败，请检查网络连接或稍后重试')
    return null
  } finally {
    parsing.value = false
  }
}

// 修改generatePlan函数，使用配置好的api实例并确保传递偏好参数
const generatePlan = async () => {
  if (!planForm.travelRequirements.trim()) {
    ElMessage.warning('请输入旅行需求')
    return
  }
  
  try {
    generating.value = true
    
    // 第一步：解析旅行需求
    const parsedData = await parseTravelRequirements()
    if (!parsedData) {
      return // 解析失败，直接返回
    }
    
    // 第二步：使用解析出的数据调用AI生成计划
    // 确保正确传递旅行偏好
    const response = await api.post('/ai/plan', {
      destination: parsedData.destination,
      duration: parsedData.duration,
      budget: parsedData.budget,
      travelers: parsedData.travelers,
      preferences: selectedPreference.value ? selectedPreference.value.travel_preferences : '',
      special_requirements: selectedPreference.value ? selectedPreference.value.special_requirements : ''
    })
    
    if (response.data.status === 'success') {
      planResult.value = response.data
      ElMessage.success('AI旅行计划生成成功！')
    } else {
      ElMessage.error('生成旅行计划失败：' + (response.data.error || '未知错误'))
    }
  } catch (error: any) {
    console.error('生成旅行计划失败:', error)
    ElMessage.error('生成旅行计划失败，请检查网络连接或稍后重试')
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
  width: 100%;
  box-sizing: border-box;
}

.input-hint p {
  margin: 4px 0;
  font-size: 12px;
  color: #666;
}

.section-divider {
  height: 20px;
  margin: 20px 0;
  border-bottom: 1px solid #e4e7ed;
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
.weather-content,
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
  align-items: center;
  gap: 8px;
}

.preference-item strong {
  min-width: 80px;
  color: #606266;
  font-weight: 600;
  line-height: 1.5;
}

.preference-item span {
  flex: 1;
  color: #303133;
  line-height: 1.5;
}

/* Markdown样式 */
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
  width: 100%;
}

.voice-input-container {
  position: absolute;
  right: 30px;
  top: 10px;
  display: flex;
  align-items: center;
  gap: 8px;
  z-index: 10;
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

/* Element Plus组件样式覆盖 */
:deep(.el-textarea__inner) {
  padding-right: 50px;
  width: calc(100% - 20px);
  margin-right: 20px;
}

:deep(.el-form-item__content) {
  width: 100%;
}

:deep(.el-textarea) {
  width: 100%;
}

/* 创建旅行计划按钮样式 */
.create-trip-section {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background-color: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.create-trip-hint {
  margin-top: 10px;
  color: #666;
  font-size: 14px;
}
.parsed-info {
  margin: 20px 0;
  background-color: #f0f9ff;
  border: 1px solid #e1f5fe;
  border-radius: 4px;
  padding: 15px;
}

.parsed-info p {
  margin: 5px 0;
  font-size: 14px;
}

.trip-name-input {
  margin-bottom: 15px;
  text-align: center;
}

.trip-name-input .el-form-item {
  margin-bottom: 0;
}

.trip-name-input .el-form-item__label {
  font-weight: bold;
  color: #333;
}

</style>