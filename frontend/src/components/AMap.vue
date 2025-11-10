<template>
  <div class="amap-container">
    <div id="map-container" ref="mapContainer"></div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-text">正在加载地图...</div>
    </div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="error-overlay">
      <div class="error-text">{{ error }}</div>
      <button @click="initMap" class="retry-btn">重试</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { loadAMapWithPlugins } from '@/utils/amapLoader' // 修复导入路径

// Props
interface Props {
  center?: [number, number]
  zoom?: number
}

const props = withDefaults(defineProps<Props>(), {
  center: () => [116.397428, 39.90923], // 北京天安门
  zoom: 13
})

// Emits
const emit = defineEmits<{
  mapReady: [map: any]
}>()

// Refs
const mapContainer = ref<HTMLElement>()
const map = ref<any>(null)
const loading = ref(true)
const error = ref('')

// 初始化地图
const initMap = async () => {
  if (!mapContainer.value) {
    error.value = '地图容器未找到'
    return
  }

  loading.value = true
  error.value = ''

  try {
    // 等待高德地图API加载完成
    console.log('🚀 加载高德地图API...')
    await loadAMapWithPlugins() // 使用正确的加载函数
    
    // 检查AMap对象是否可用
    if (typeof window.AMap === 'undefined') {
      throw new Error('高德地图API加载失败，AMap对象未定义')
    }
    
    // 创建地图实例
    map.value = new window.AMap.Map(mapContainer.value, {
      viewMode: '2D', // 使用2D模式
      zoom: props.zoom,
      center: props.center,
      mapStyle: 'amap://styles/normal' // 标准地图样式
    })
    
    console.log('✅ 地图初始化成功')
    loading.value = false
    
    // 触发地图就绪事件
    emit('mapReady', map.value)
    
  } catch (err: any) {
    console.error('❌ 地图初始化失败:', err)
    error.value = `地图初始化失败: ${err.message}`
    loading.value = false
    
    // 提供更友好的错误信息
    if (err.message.includes('PlaceSearch插件未加载')) {
      error.value = '地图功能加载中，插件将在需要时自动加载...'
      // 延迟重试
      setTimeout(() => initMap(), 2000)
    }
  }
}

// 监听props变化
watch(() => props.center, (newCenter) => {
  if (map.value && newCenter) {
    map.value.setCenter(newCenter)
  }
})

watch(() => props.zoom, (newZoom) => {
  if (map.value && newZoom) {
    map.value.setZoom(newZoom)
  }
})

// 生命周期
onMounted(() => {
  initMap()
})

onUnmounted(() => {
  if (map.value) {
    map.value.destroy()
  }
})
</script>

<style scoped>
.amap-container {
  position: relative;
  width: 100%;
  height: 100%; /* 改为100%自适应 */
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  overflow: hidden;
}

#map-container {
  width: 100%;
  height: 100%;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.loading-text {
  font-size: 16px;
  color: #666;
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(255, 255, 255, 0.9);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 10;
}

.error-text {
  font-size: 16px;
  color: #f56c6c;
  margin-bottom: 15px;
  text-align: center;
}

.retry-btn {
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #66b1ff;
}
</style>