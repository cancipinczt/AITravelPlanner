<template>
  <div class="speech-test">
    <h2>实时语音转录测试</h2>
    <p>测试科大讯飞实时语音转录API功能 - 真正的实时流处理</p>
    
    <el-row :gutter="20">
      <!-- 实时语音转录测试 -->
      <el-col :span="24">
        <el-card>
          <h3>实时语音转录测试</h3>
          <p>通过麦克风进行真正的实时语音转录</p>
          
          <div class="realtime-controls">
            <el-button 
              v-if="!isRecording" 
              type="success" 
              @click="startRealTimeTranscription"
              :disabled="isWebSocketConnected"
            >
              <el-icon><microphone /></el-icon>
              开始实时转录
            </el-button>
            
            <el-button 
              v-else 
              type="danger" 
              @click="stopRealTimeTranscription"
            >
              <el-icon><video-pause /></el-icon>
              停止转录
            </el-button>
            
            <el-button 
              v-if="isWebSocketConnected"
              type="warning" 
              @click="clearResults"
            >
              <el-icon><refresh /></el-icon>
              清空结果
            </el-button>
          </div>
          
          <div v-if="isWebSocketConnected" class="connection-status">
            <el-tag type="success">WebSocket已连接，正在实时转录中...</el-tag>
            <p class="audio-info">音频格式: 16kHz, 16位, 单声道PCM</p>
            <p class="audio-info">发送间隔: 32ms/块 (512 samples)</p>
          </div>
          
          <div class="result">
            <h4>实时转录结果:</h4>
            <el-input
              type="textarea"
              :rows="6"
              v-model="transcriptionText"
              readonly
              placeholder="实时转录结果将显示在这里..."
            ></el-input>
            <div class="result-info">
              <p v-if="currentConfidence > 0">当前置信度: {{ currentConfidence }}</p>
              <p v-if="isFinalResult" style="color: #67C23A;">✓ 最终结果</p>
              <p v-if="audioChunkCount > 0">已处理音频块: {{ audioChunkCount }}</p>
            </div>
          </div>
          
          <div v-if="errorMessage" class="error-message">
            <el-alert
              :title="errorMessage"
              type="error"
              show-icon
              :closable="false"
            />
          </div>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 测试状态信息 -->
    <el-alert
      v-if="testStatus"
      :title="testStatus"
      :type="testStatusType"
      show-icon
      style="margin-top: 20px;"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { useAuthStore } from '@/stores'
import { ElMessage } from 'element-plus'
import { Microphone, VideoPause, Refresh } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 实时语音转录相关状态
const isRecording = ref(false)
const isWebSocketConnected = ref(false)
const transcriptionText = ref('')
const currentConfidence = ref(0)
const isFinalResult = ref(false)
const audioChunkCount = ref(0)
const errorMessage = ref('')

// 音频处理相关
const websocket = ref<WebSocket | null>(null)
const mediaStream = ref<MediaStream | null>(null)
const audioContext = ref<AudioContext | null>(null)
const audioProcessor = ref<ScriptProcessorNode | null>(null)

// 测试状态
const testStatus = ref('')
const testStatusType = ref<'success' | 'warning' | 'info' | 'error'>('info')

// 开始实时语音转录
const startRealTimeTranscription = async () => {
  try {
    testStatus.value = '正在获取麦克风权限...'
    testStatusType.value = 'info'
    
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
        audioChunkCount.value++
      }
    }

    // 连接音频处理链
    source.connect(audioProcessor.value)
    audioProcessor.value.connect(audioContext.value.destination)
    
    // 创建WebSocket连接
    testStatus.value = '正在连接WebSocket...'
    websocket.value = new WebSocket('ws://localhost:8000/api/v1/speech/transcribe')
    
    websocket.value.onopen = () => {
      isWebSocketConnected.value = true
      isRecording.value = true
      testStatus.value = 'WebSocket连接成功，开始实时转录...'
      testStatusType.value = 'success'
      ElMessage.success('实时转录已开始')
    }
    
    websocket.value.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        console.log('收到WebSocket消息:', data)
        
        if (data.success) {
          if (data.transcript) {
            transcriptionText.value = data.transcript
            currentConfidence.value = data.confidence || 0.9
            isFinalResult.value = data.is_final || false
            
            if (data.is_final) {
              testStatus.value = '实时转录完成！'
              testStatusType.value = 'success'
              ElMessage.success('实时转录完成')
            } else {
              testStatus.value = '正在实时转录中...'
              testStatusType.value = 'info'
            }
          }
        } else {
          errorMessage.value = `转录错误: ${data.error}`
          testStatus.value = `转录错误: ${data.error}`
          testStatusType.value = 'error'
          ElMessage.error('转录过程中出现错误')
        }
      } catch (error) {
        console.error('解析WebSocket消息错误:', error)
        errorMessage.value = '解析转录结果时出错'
        testStatus.value = '解析转录结果时出错'
        testStatusType.value = 'error'
      }
    }
    
    websocket.value.onerror = (error) => {
      console.error('WebSocket错误详情:', error)
      errorMessage.value = 'WebSocket连接错误，请检查后端服务是否启动'
      testStatus.value = 'WebSocket连接错误，请检查后端服务是否启动'
      testStatusType.value = 'error'
      ElMessage.error('WebSocket连接失败，请检查网络连接和后端服务')
      stopRealTimeTranscription()
    }
    
    websocket.value.onclose = () => {
      console.log('WebSocket连接已关闭')
      isWebSocketConnected.value = false
      isRecording.value = false
      testStatus.value = 'WebSocket连接已关闭'
      testStatusType.value = 'info'
    }
    
  } catch (error: any) {
    console.error('实时转录错误:', error)
    errorMessage.value = `实时语音转录启动失败: ${error.message}`
    testStatus.value = `实时语音转录启动失败: ${error.message}`
    testStatusType.value = 'error'
    ElMessage.error('实时转录启动失败')
    stopRealTimeTranscription()
  }
}

// 停止实时转录
const stopRealTimeTranscription = () => {
  // 关闭WebSocket连接
  if (websocket.value) {
    if (websocket.value.readyState === WebSocket.OPEN) {
      // 发送结束标记
      websocket.value.send(JSON.stringify({ action: 'end' }))
    }
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
  testStatus.value = '实时转录已停止'
  testStatusType.value = 'info'
  ElMessage.info('实时转录已停止')
}

// 清空结果
const clearResults = () => {
  transcriptionText.value = ''
  currentConfidence.value = 0
  isFinalResult.value = false
  audioChunkCount.value = 0
  errorMessage.value = ''
  ElMessage.info('结果已清空')
}

// 将Float32音频数据转换为16位PCM
const float32ToPCM = (float32Array: Float32Array): Uint8Array => {
  const buffer = new ArrayBuffer(float32Array.length * 2) // 16位 = 2字节
  const view = new DataView(buffer)
  
  for (let i = 0; i < float32Array.length; i++) {
    const s = Math.max(-1, Math.min(1, float32Array[i]))
    view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true)
  }
  
  return new Uint8Array(buffer)
}

// 组件卸载时清理资源
onUnmounted(() => {
  if (isRecording.value) {
    stopRealTimeTranscription()
  }
})
</script>

<style scoped>
.speech-test {
  padding: 20px;
}

.el-row {
  margin-top: 30px;
}

.el-col {
  margin-bottom: 20px;
}

h2 {
  color: #409EFF;
  margin-bottom: 10px;
  text-align: center;
}

p {
  color: #666;
  margin-bottom: 30px;
  text-align: center;
}

.realtime-controls {
  margin: 20px 0;
  text-align: center;
}

.realtime-controls .el-button {
  margin: 0 10px;
}

.connection-status {
  margin: 10px 0;
  text-align: center;
}

.audio-info {
  font-size: 12px;
  color: #909399;
  margin: 5px 0;
}

.result {
  margin-top: 20px;
  padding: 15px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.result h4 {
  margin-bottom: 10px;
  color: #409EFF;
}

.result-info {
  margin-top: 10px;
}

.result-info p {
  margin: 5px 0;
  text-align: left;
  color: #606266;
}

.error-message {
  margin-top: 15px;
}
</style>