<template>
  <div class="map-api-test">
    <h2>地图API测试</h2>
    
    <el-tabs v-model="activeTab" type="card">
      <!-- 地理编码测试 -->
      <el-tab-pane label="地理编码测试" name="geocode">
        <div class="test-section">
          <el-form :model="geocodeForm" label-width="120px">
            <el-form-item label="地址">
              <el-input v-model="geocodeForm.address" placeholder="请输入地址，如：北京市朝阳区"></el-input>
            </el-form-item>
            <el-form-item label="城市（可选）">
              <el-input v-model="geocodeForm.city" placeholder="请输入城市，如：北京"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testGeocode" :loading="loading.geocode">
                测试地理编码
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="geocodeResult" class="result-section">
            <h4>测试结果：</h4>
            <pre>{{ JSON.stringify(geocodeResult, null, 2) }}</pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 逆地理编码测试 -->
      <el-tab-pane label="逆地理编码测试" name="reverse">
        <div class="test-section">
          <el-form :model="reverseForm" label-width="120px">
            <el-form-item label="经纬度坐标">
              <el-input v-model="reverseForm.location" placeholder="格式：经度,纬度，如：116.397428,39.90923"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testReverseGeocode" :loading="loading.reverse">
                测试逆地理编码
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="reverseResult" class="result-section">
            <h4>测试结果：</h4>
            <pre>{{ JSON.stringify(reverseResult, null, 2) }}</pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 路径规划测试 -->
      <el-tab-pane label="路径规划测试" name="route">
        <div class="test-section">
          <el-form :model="routeForm" label-width="120px">
            <el-form-item label="起点地址">
              <el-input v-model="routeForm.origin" placeholder="请输入起点地址，如：北京市朝阳区"></el-input>
            </el-form-item>
            <el-form-item label="终点地址">
              <el-input v-model="routeForm.destination" placeholder="请输入终点地址，如：北京市海淀区"></el-input>
            </el-form-item>
            <el-form-item label="路径策略">
              <el-select v-model="routeForm.strategy" placeholder="请选择路径策略">
                <el-option label="速度优先" :value="0"></el-option>
                <el-option label="费用优先" :value="1"></el-option>
                <el-option label="距离优先" :value="2"></el-option>
                <el-option label="不走高速" :value="3"></el-option>
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testRoutePlanning" :loading="loading.route">
                测试路径规划
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="routeResult" class="result-section">
            <h4>测试结果：</h4>
            <pre>{{ JSON.stringify(routeResult, null, 2) }}</pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- POI搜索测试 -->
      <el-tab-pane label="POI搜索测试" name="poi">
        <div class="test-section">
          <el-form :model="poiForm" label-width="120px">
            <el-form-item label="搜索关键词">
              <el-input v-model="poiForm.keywords" placeholder="请输入关键词，如：餐厅、酒店"></el-input>
            </el-form-item>
            <el-form-item label="城市（可选）">
              <el-input v-model="poiForm.city" placeholder="请输入城市，如：北京"></el-input>
            </el-form-item>
            <el-form-item label="中心点坐标（可选）">
              <el-input v-model="poiForm.location" placeholder="格式：经度,纬度"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testPoiSearch" :loading="loading.poi">
                测试POI搜索
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="poiResult" class="result-section">
            <h4>测试结果：</h4>
            <pre>{{ JSON.stringify(poiResult, null, 2) }}</pre>
          </div>
        </div>
      </el-tab-pane>

      <!-- 静态地图测试 -->
      <el-tab-pane label="静态地图测试" name="static">
        <div class="test-section">
          <el-form :model="staticForm" label-width="120px">
            <el-form-item label="中心点坐标">
              <el-input v-model="staticForm.location" placeholder="格式：经度,纬度，如：116.397428,39.90923"></el-input>
            </el-form-item>
            <el-form-item label="缩放级别">
              <el-input-number v-model="staticForm.zoom" :min="1" :max="18"></el-input-number>
            </el-form-item>
            <el-form-item label="图片尺寸">
              <el-input v-model="staticForm.size" placeholder="格式：宽*高，如：400*300"></el-input>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="testStaticMap" :loading="loading.static">
                测试静态地图
              </el-button>
            </el-form-item>
          </el-form>
          
          <div v-if="staticResult" class="result-section">
            <h4>测试结果：</h4>
            <div v-if="staticResult.success && staticResult.data.status === 'success'">
              <p>地图图片URL：</p>
              <a :href="staticResult.data.image_url" target="_blank">{{ staticResult.data.image_url }}</a>
              <div class="map-image">
                <img :src="staticResult.data.image_url" alt="静态地图" style="max-width: 100%; border: 1px solid #ddd; border-radius: 4px;">
              </div>
            </div>
            <div v-else>
              <pre>{{ JSON.stringify(staticResult, null, 2) }}</pre>
            </div>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const activeTab = ref('geocode')

// 表单数据
const geocodeForm = ref({
  address: '北京市朝阳区',
  city: ''
})

const reverseForm = ref({
  location: '116.397428,39.90923'
})

const routeForm = ref({
  origin: '北京市朝阳区',
  destination: '北京市海淀区',
  strategy: 0
})

const poiForm = ref({
  keywords: '餐厅',
  city: '北京',
  location: '',
  types: '',
  radius: 3000
})

const staticForm = ref({
  location: '116.397428,39.90923',
  zoom: 15,
  size: '400*300',
  markers: '',
  labels: ''
})

// 加载状态
const loading = ref({
  geocode: false,
  reverse: false,
  route: false,
  poi: false,
  static: false
})

// 测试结果
const geocodeResult = ref(null)
const reverseResult = ref(null)
const routeResult = ref(null)
const poiResult = ref(null)
const staticResult = ref(null)

// API基础URL
const API_BASE = 'http://localhost:8000/api/v1/maps'

// 测试方法
const testGeocode = async () => {
  loading.value.geocode = true
  try {
    const params = new URLSearchParams()
    params.append('address', geocodeForm.value.address)
    if (geocodeForm.value.city) {
      params.append('city', geocodeForm.value.city)
    }
    
    const response = await axios.get(`${API_BASE}/geocode?${params}`)
    geocodeResult.value = response.data
    ElMessage.success('地理编码测试成功')
  } catch (error: any) {
    console.error('地理编码测试失败:', error)
    geocodeResult.value = { error: error.response?.data || error.message }
    ElMessage.error('地理编码测试失败')
  } finally {
    loading.value.geocode = false
  }
}

const testReverseGeocode = async () => {
  loading.value.reverse = true
  try {
    const params = new URLSearchParams()
    params.append('location', reverseForm.value.location)
    
    const response = await axios.get(`${API_BASE}/reverse-geocode?${params}`)
    reverseResult.value = response.data
    ElMessage.success('逆地理编码测试成功')
  } catch (error: any) {
    console.error('逆地理编码测试失败:', error)
    reverseResult.value = { error: error.response?.data || error.message }
    ElMessage.error('逆地理编码测试失败')
  } finally {
    loading.value.reverse = false
  }
}

const testRoutePlanning = async () => {
  loading.value.route = true
  try {
    const params = new URLSearchParams()
    params.append('origin', routeForm.value.origin)
    params.append('destination', routeForm.value.destination)
    params.append('strategy', routeForm.value.strategy.toString())
    
    const response = await axios.get(`${API_BASE}/route?${params}`)
    routeResult.value = response.data
    ElMessage.success('路径规划测试成功')
  } catch (error: any) {
    console.error('路径规划测试失败:', error)
    routeResult.value = { error: error.response?.data || error.message }
    ElMessage.error('路径规划测试失败')
  } finally {
    loading.value.route = false
  }
}

const testPoiSearch = async () => {
  loading.value.poi = true
  try {
    const params = new URLSearchParams()
    params.append('keywords', poiForm.value.keywords)
    if (poiForm.value.city) {
      params.append('city', poiForm.value.city)
    }
    if (poiForm.value.location) {
      params.append('location', poiForm.value.location)
    }
    
    const response = await axios.get(`${API_BASE}/poi?${params}`)
    poiResult.value = response.data
    ElMessage.success('POI搜索测试成功')
  } catch (error: any) {
    console.error('POI搜索测试失败:', error)
    poiResult.value = { error: error.response?.data || error.message }
    ElMessage.error('POI搜索测试失败')
  } finally {
    loading.value.poi = false
  }
}

const testStaticMap = async () => {
  loading.value.static = true
  try {
    const params = new URLSearchParams()
    params.append('location', staticForm.value.location)
    params.append('zoom', staticForm.value.zoom.toString())
    params.append('size', staticForm.value.size)
    
    const response = await axios.get(`${API_BASE}/static-map?${params}`)
    staticResult.value = response.data
    ElMessage.success('静态地图测试成功')
  } catch (error: any) {
    console.error('静态地图测试失败:', error)
    staticResult.value = { error: error.response?.data || error.message }
    ElMessage.error('静态地图测试失败')
  } finally {
    loading.value.static = false
  }
}
</script>

<style scoped>
.map-api-test {
  max-width: 1000px;
  margin: 0 auto;
  padding: 20px;
}

.test-section {
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
  margin-bottom: 20px;
}

.result-section {
  margin-top: 20px;
  padding: 15px;
  background: white;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.result-section pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.map-image {
  margin-top: 15px;
  text-align: center;
}
</style>