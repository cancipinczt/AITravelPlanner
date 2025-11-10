<template>
  <div class="map-demo-container">
    <h2>地图演示</h2>
    
    <!-- 地图板块（上方） -->
    <div class="map-section">
<AMap 
        :center="mapCenter" 
        :zoom="mapZoom"
        @mapReady="onMapReady"
/>
    </div>
    
    <!-- 功能板块（下方分为左右两部分） -->
    <div class="function-section">
      <!-- 左边：地点搜索 -->
      <div class="left-panel">
        <el-card class="search-card">
          <template #header>
            <div class="card-header">
              <span>地点搜索</span>
            </div>
          </template>
          
          <div class="search-form">
            <el-input
              v-model="searchKeyword"
              placeholder="请输入地点名称"
              class="search-input"
@keyup.enter="handleSearch"
            >
              <template #append>
                <el-button 
                  :disabled="!isSearchReady" 
                  @click="handleSearch"
                  :loading="searching"
                >
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
              </template>
            </el-input>
            
            <!-- 搜索状态提示 -->
            <div v-if="!isSearchReady" class="status-info">
              <el-alert
                title="搜索功能正在初始化..."
                type="info"
:closable="false"
                show-icon
              />
            </div>
            
            <div v-if="searchError" class="status-error">
<el-alert
                :title="searchError"
                type="error"
                :closable="true"
                show-icon
                @close="searchError = ''"
              />
            </div>
          </div>
          
          <!-- 搜索结果 -->
          <div v-if="searchResults.length > 0" class="search-results">
            <h4>搜索结果 ({{ searchResults.length }})</h4>
            <div class="result-list">
              <div
                v-for="(result, index) in searchResults"
                :key="index"
                class="result-item"
                @click="selectResult(result)"
              >
                <div class="result-name">{{ result.name }}</div>
                <div class="result-address">{{ result.address }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
      
      <!-- 右边：路径规划 -->
      <div class="right-panel">
        <el-card class="route-card">
          <template #header>
            <div class="card-header">
              <span>路径规划</span>
            </div>
          </template>
          
          <div class="route-form">
            <!-- 起点输入 -->
            <div class="route-input-group">
              <label class="route-label">起点：</label>
              <el-input
                v-model="routeStart"
                placeholder="请输入起点位置"
                class="route-input"
                @focus="setRouteInputFocus('start')"
              >
                <template #append>
                  <el-button @click="useCurrentLocation('start')" title="使用当前位置">
                    <el-icon><Location /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </div>
            
            <!-- 终点输入 -->
            <div class="route-input-group">
              <label class="route-label">终点：</label>
              <el-input
                v-model="routeEnd"
                placeholder="请输入终点位置"
                class="route-input"
                @focus="setRouteInputFocus('end')"
              >
                <template #append>
                  <el-button @click="useCurrentLocation('end')" title="使用当前位置">
                    <el-icon><Location /></el-icon>
                  </el-button>
                </template>
              </el-input>
            </div>
            
            <!-- 路径规划按钮 -->
            <div class="route-actions">
              <el-button 
                type="primary" 
                @click="calculateRoute"
                :disabled="!isRouteReady || !routeStart || !routeEnd"
                :loading="routeCalculating"
                class="route-button"
              >
                <el-icon><Promotion /></el-icon>
                开始规划
              </el-button>
              
              <el-button 
                @click="clearRoute"
                :disabled="!hasRoute"
                class="clear-button"
              >
                <el-icon><Delete /></el-icon>
                清除路线
              </el-button>
            </div>
            
            <!-- 路径规划状态提示 -->
            <div v-if="!isRouteReady" class="status-info">
              <el-alert
                title="路径规划功能正在初始化..."
                type="info"
                :closable="false"
                show-icon
              />
            </div>
            
            <div v-if="routeError" class="status-error">
              <el-alert
                :title="routeError"
                type="error"
                :closable="true"
                show-icon
                @close="routeError = ''"
              />
            </div>
            
            <!-- 路径规划结果 -->
            <div v-if="routeResult" class="route-result">
              <h4>规划结果</h4>
              <div class="route-info">
                <div class="route-item">
                  <span class="route-label">距离：</span>
                  <span class="route-value">{{ routeResult.distance }} 公里</span>
                </div>
                <div class="route-item">
                  <span class="route-label">预计时间：</span>
                  <span class="route-value">{{ routeResult.duration }} 分钟</span>
                </div>
                <div class="route-item">
                  <span class="route-label">路线策略：</span>
                  <span class="route-value">{{ routeResult.strategy }}</span>
                </div>
              </div>
              
              <!-- 路线步骤 -->
              <div v-if="routeResult.steps && routeResult.steps.length > 0" class="route-steps">
                <h5>路线指引</h5>
                <div class="steps-list">
                  <div
                    v-for="(step, index) in routeResult.steps"
                    :key="index"
                    class="step-item"
                  >
                    <div class="step-number">{{ index + 1 }}</div>
                    <div class="step-content">
                      <div class="step-instruction">{{ step.instruction }}</div>
                      <div class="step-distance">{{ step.distance }}米</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Search, Location, Promotion, Delete } from '@element-plus/icons-vue'
import AMap from '@/components/AMap.vue'
import { loadPlaceSearchPlugin, isPlaceSearchPluginLoaded } from '@/utils/amapLoader'
// 新增：导入Driving插件加载函数
import { loadDrivingPlugin, isDrivingPluginLoaded } from '@/utils/amapLoader'

// 地图相关
const mapCenter = ref<[number, number]>([116.397428, 39.90923])
const mapZoom = ref(13)
const mapInstance = ref<any>(null)

// 搜索相关
const searchKeyword = ref('')
const searching = ref(false)
const searchResults = ref<any[]>([])
const placeSearch = ref<any>(null)
const markers = ref<any[]>([])
const isSearchReady = ref(false)
const searchError = ref('')

// 路径规划相关
const routeStart = ref('')
const routeEnd = ref('')
const routeCalculating = ref(false)
const isRouteReady = ref(false)
const routeError = ref('')
const routeResult = ref<any>(null)
const hasRoute = ref(false)
const driving = ref<any>(null)
const currentRouteInputFocus = ref<'start' | 'end'>('start')

// 组件挂载时预加载插件
onMounted(async () => {
  try {
    // 移除预加载插件的逻辑，因为插件已经在地图加载时一次性加载了
    console.log('🚀 地图组件已挂载，等待地图初始化...')
  } catch (error) {
    console.error('❌ 地图组件初始化失败:', error)
    searchError.value = '功能初始化失败，请刷新页面重试'
  }
})

// 地图就绪回调
const onMapReady = async (map: any) => {
  console.log('地图已就绪:', map)
  mapInstance.value = map
  
  // 初始化地点搜索插件
  await initPlaceSearch()
  
  // 初始化路径规划插件
  await initRoutePlanning()
}

// 初始化地点搜索
const initPlaceSearch = async (retryCount = 0) => {
  const maxRetries = 3;
  
  try {
    if (!mapInstance.value) {
      throw new Error('地图实例未就绪')
    }

    console.log(`🔄 初始化地点搜索插件... (重试次数: ${retryCount})`)

    // 检查插件是否可用
    if (typeof window.AMap.PlaceSearch === 'undefined') {
      if (retryCount < maxRetries) {
        console.warn(`⚠️ PlaceSearch插件可能仍在加载中，将延迟初始化 (重试 ${retryCount + 1}/${maxRetries})`)
        // 设置重试机制
        setTimeout(() => initPlaceSearch(retryCount + 1), 2000)
        return
      } else {
        throw new Error('PlaceSearch插件加载超时，请刷新页面重试')
      }
    }

    // 创建地点搜索实例
    placeSearch.value = new window.AMap.PlaceSearch({
      map: mapInstance.value,
      pageSize: 20,
      pageIndex: 1,
      city: '全国',
      panel: undefined
    })
    
    isSearchReady.value = true
    searchError.value = ''
    console.log('✅ 地点搜索插件初始化成功')
    
  } catch (error: any) {
    console.error('❌ 地点搜索插件初始化失败:', error)
    searchError.value = `搜索功能初始化失败: ${error.message}`
    isSearchReady.value = false
    
    if (retryCount < maxRetries) {
      console.log(`🔄 将在2秒后重试 (重试 ${retryCount + 1}/${maxRetries})`)
      setTimeout(() => initPlaceSearch(retryCount + 1), 2000)
    } else {
      console.error('❌ 搜索功能初始化失败，已达到最大重试次数')
      searchError.value = '搜索功能初始化失败，请刷新页面重试'
    }
  }
}

// 初始化路径规划
const initRoutePlanning = async (retryCount = 0) => {
  const maxRetries = 3;
  
  try {
    if (!mapInstance.value) {
      throw new Error('地图实例未就绪')
    }

    console.log(`🔄 初始化路径规划插件... (重试次数: ${retryCount})`)

    // 检查插件是否可用
    if (typeof window.AMap.Driving === 'undefined') {
      if (retryCount < maxRetries) {
        console.warn(`⚠️ Driving插件可能仍在加载中，将延迟初始化 (重试 ${retryCount + 1}/${maxRetries})`)
        // 设置重试机制
        setTimeout(() => initRoutePlanning(retryCount + 1), 2000)
        return
      } else {
        throw new Error('Driving插件加载超时，请刷新页面重试')
      }
    }

    // 创建驾车路径规划实例
    driving.value = new window.AMap.Driving({
      map: mapInstance.value,
      policy: window.AMap.DrivingPolicy.LEAST_TIME, // 默认使用最快路线
      hideMarkers: false, // 显示标记
      showTraffic: true, // 显示实时交通
    })
    
    console.log('✅ 路径规划插件初始化成功')
    isRouteReady.value = true
    routeError.value = ''
    
  } catch (error: any) {
    console.error('❌ 路径规划插件初始化失败:', error)
    routeError.value = `路径规划功能初始化失败: ${error.message}`
    isRouteReady.value = false
    
    if (retryCount < maxRetries) {
      console.log(`🔄 将在2秒后重试 (重试 ${retryCount + 1}/${maxRetries})`)
      setTimeout(() => initRoutePlanning(retryCount + 1), 2000)
    } else {
      console.error('❌ 路径规划功能初始化失败，已达到最大重试次数')
      routeError.value = '路径规划功能初始化失败，请刷新页面重试'
    }
  }
}

// 设置当前输入框焦点
const setRouteInputFocus = (type: 'start' | 'end') => {
  currentRouteInputFocus.value = type
}

// 使用当前位置
const useCurrentLocation = (type: 'start' | 'end') => {
  if (!navigator.geolocation) {
    ElMessage.error('浏览器不支持地理位置功能')
    return
  }

  ElMessage.info('正在获取当前位置...')
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const { latitude, longitude } = position.coords
      
      // 使用逆地理编码获取地址
      const geocoder = new window.AMap.Geocoder()
      geocoder.getAddress([longitude, latitude], (status: string, result: any) => {
        if (status === 'complete' && result.regeocode) {
          const address = result.regeocode.formattedAddress
          if (type === 'start') {
            routeStart.value = address
          } else {
            routeEnd.value = address
          }
          ElMessage.success('当前位置已设置')
        } else {
          ElMessage.error('获取地址失败')
        }
      })
    },
    (error) => {
      console.error('获取位置失败:', error)
      ElMessage.error('获取当前位置失败')
    }
  )
}

// 计算路径
const calculateRoute = async () => {
  if (!routeStart.value.trim() || !routeEnd.value.trim()) {
    ElMessage.warning('请输入起点和终点')
    return
  }

  if (!driving.value || !isRouteReady.value) {
    ElMessage.error('路径规划功能未就绪')
    return
  }

  routeCalculating.value = true
  routeResult.value = null
  hasRoute.value = false

  try {
    // 清除之前的路线
    driving.value.clear()

    // 执行路径规划
    driving.value.search([
      { keyword: routeStart.value },
      { keyword: routeEnd.value }
    ], (status: string, result: any) => {
      routeCalculating.value = false
      
      if (status === 'complete') {
        if (result.routes && result.routes.length > 0) {
          const route = result.routes[0]
          
          // 解析路线结果
          routeResult.value = {
            distance: (route.distance / 1000).toFixed(1), // 转换为公里
            duration: Math.round(route.time / 60), // 转换为分钟
            strategy: getStrategyText(route.policy),
            steps: route.steps.map((step: any) => ({
              instruction: step.instruction.replace(/<[^>]*>/g, ''), // 移除HTML标签
              distance: step.distance
            }))
          }
          
          hasRoute.value = true
          ElMessage.success('路径规划完成')
        } else {
          ElMessage.warning('未找到可行路线')
        }
      } else {
        console.error('路径规划状态异常:', status, result)
        ElMessage.error('路径规划失败，请检查起点终点是否正确')
      }
    })
  } catch (error) {
    routeCalculating.value = false
    console.error('路径规划出错:', error)
    ElMessage.error('路径规划过程中出现错误')
  }
}

// 获取策略文本
const getStrategyText = (policy: string) => {
  const strategies = {
    'LEAST_TIME': '最快路线',
    'LEAST_FEE': '最经济路线',
    'LEAST_DISTANCE': '最短距离',
    'REAL_TRAFFIC': '实时路况'
  }
  return strategies[policy] || '默认路线'
}

// 清除路线
const clearRoute = () => {
  if (driving.value) {
    driving.value.clear()
  }
  routeResult.value = null
  hasRoute.value = false
  ElMessage.info('路线已清除')
}

// 处理搜索
const handleSearch = async () => {
  if (!searchKeyword.value.trim()) {
    ElMessage.warning('请输入搜索关键词')
    return
  }

  if (!placeSearch.value || !isSearchReady.value) {
    ElMessage.error('搜索功能未就绪，请稍后重试')
    return
  }

  searching.value = true
  searchResults.value = []

  try {
    clearMarkers()

    placeSearch.value.search(searchKeyword.value, (status: string, result: any) => {
      searching.value = false
      
      if (status === 'complete' && result.poiList && result.poiList.pois) {
        const pois = result.poiList.pois
        searchResults.value = pois.map((poi: any) => ({
          id: poi.id,
          name: poi.name,
          address: poi.address,
          location: poi.location,
          distance: poi.distance,
          type: poi.type,
          tel: poi.tel
        }))
        
        addMarkersToMap(pois)
        ElMessage.success(`找到 ${pois.length} 个结果`)
      } else if (status === 'no_data') {
        ElMessage.warning('未找到相关地点')
      } else {
        console.error('搜索状态异常:', status, result)
        ElMessage.error('搜索失败，请重试')
      }
    })
  } catch (error) {
    searching.value = false
    console.error('搜索出错:', error)
    ElMessage.error('搜索过程中出现错误')
  }
}

// 在地图上添加标记
const addMarkersToMap = (pois: any[]) => {
  if (!mapInstance.value) return

  pois.forEach((poi) => {
    if (poi.location) {
      const [lng, lat] = poi.location.split(',').map(Number)
      
      const marker = new window.AMap.Marker({
        position: new window.AMap.LngLat(lng, lat),
        title: poi.name,
        content: `
          <div style="background: #fff; padding: 5px 10px; border-radius: 4px; 
                     border: 1px solid #409EFF; color: #409EFF; font-size: 12px;">
            ${poi.name}
          </div>
        `,
        offset: new window.AMap.Pixel(-25, -10)
      })
      
      marker.setMap(mapInstance.value)
      markers.value.push(marker)
      
      marker.on('click', () => {
        mapInstance.value.setCenter([lng, lat])
        mapInstance.value.setZoom(16)
      })
    }
  })
}

// 清除所有标记
const clearMarkers = () => {
  markers.value.forEach(marker => {
    marker.setMap(null)
  })
  markers.value = []
}

// 选择搜索结果
const selectResult = (result: any) => {
  if (result.location && mapInstance.value) {
    const [lng, lat] = result.location.split(',').map(Number)
    mapInstance.value.setCenter([lng, lat])
    mapInstance.value.setZoom(16)
  }
}

// 组件卸载时清理
onUnmounted(() => {
  clearMarkers()
  if (placeSearch.value) {
    placeSearch.value.clear()
  }
  if (driving.value) {
    driving.value.clear()
  }
})
</script>
<style scoped>
.map-demo-container {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #409EFF;
}

/* 地图板块样式 */
.map-section {
  margin-bottom: 30px;
  height: 500px; /* 添加固定高度 */
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

/* 功能板块样式 */
.function-section {
  display: flex;
  gap: 20px;
  margin-top: 20px;
}
.left-panel, .right-panel {
  flex: 1;
}

.search-card, .route-card {
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  height: 100%;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 搜索表单样式 */
.search-form {
  margin-bottom: 20px;
}
.search-input {
  margin-bottom: 15px;
}

/* 路径规划表单样式 */
.route-form {
  margin-bottom: 20px;
}

.route-input-group {
  margin-bottom: 15px;
}

.route-label {
  display: block;
  margin-bottom: 5px;
  font-weight: 500;
  color: #606266;
}

.route-input {
  width: 100%;
}

.route-actions {
  display: flex;
  gap: 10px;
  margin-top: 20px;
}

.route-button, .clear-button {
  flex: 1;
}

/* 状态提示样式 */
.status-info,
.status-error {
  margin-top: 10px;
}

/* 搜索结果样式 */
.search-results {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.search-results h4 {
  margin-bottom: 15px;
  color: #606266;
}

.result-list {
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  padding: 12px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s;
}

.result-item:hover {
  border-color: #409EFF;
  background-color: #f5f7fa;
}

.result-name {
  font-weight: bold;
  color: #303133;
  margin-bottom: 5px;
}

.result-address {
  font-size: 12px;
  color: #909399;
}

/* 路径规划结果样式 */
.route-result {
  margin-top: 20px;
  border-top: 1px solid #e4e7ed;
  padding-top: 15px;
}

.route-result h4 {
  margin-bottom: 15px;
  color: #606266;
}

.route-info {
  margin-bottom: 15px;
}

.route-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.route-label {
  font-weight: 500;
  color: #606266;
}

.route-value {
  color: #303133;
  font-weight: bold;
}

.route-steps {
  margin-top: 15px;
}

.route-steps h5 {
  margin-bottom: 10px;
  color: #606266;
}

.steps-list {
  max-height: 200px;
  overflow-y: auto;
}

.step-item {
  display: flex;
  align-items: flex-start;
  margin-bottom: 10px;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
  background-color: #fafafa;
}

.step-number {
  background: #409EFF;
  color: white;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  margin-right: 10px;
  flex-shrink: 0;
}

.step-content {
  flex: 1;
}

.step-instruction {
  font-size: 14px;
  color: #303133;
  margin-bottom: 4px;
}

.step-distance {
  font-size: 12px;
  color: #909399;
}
</style>