import { ref } from 'vue'

const API_BASE_URL = 'http://localhost:8000/api/v1'

// 地址解析（地理编码）
export const geocodeAddress = async (address: string, city?: string) => {
  try {
    const params = new URLSearchParams({ address })
    if (city) params.append('city', city)
    
    const response = await fetch(`${API_BASE_URL}/geocode?${params}`)
    const data = await response.json()
    
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.detail || '地址解析失败')
    }
  } catch (error) {
    console.error('地址解析错误:', error)
    throw error
  }
}

// 逆地理编码
export const reverseGeocode = async (location: string) => {
  try {
    const response = await fetch(`${API_BASE_URL}/reverse-geocode?location=${location}`)
    const data = await response.json()
    
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.detail || '逆地理编码失败')
    }
  } catch (error) {
    console.error('逆地理编码错误:', error)
    throw error
  }
}

// 路线规划
export const planRoute = async (origin: string, destination: string, strategy: number = 0) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/route?origin=${origin}&destination=${destination}&strategy=${strategy}`
    )
    const data = await response.json()
    
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.detail || '路线规划失败')
    }
  } catch (error) {
    console.error('路线规划错误:', error)
    throw error
  }
}

// POI搜索
export const searchPOI = async (keywords: string, city?: string, location?: string) => {
  try {
    const params = new URLSearchParams({ keywords })
    if (city) params.append('city', city)
    if (location) params.append('location', location)
    
    const response = await fetch(`${API_BASE_URL}/poi?${params}`)
    const data = await response.json()
    
    if (data.success) {
      return data.data
    } else {
      throw new Error(data.detail || 'POI搜索失败')
    }
  } catch (error) {
    console.error('POI搜索错误:', error)
    throw error
  }
}