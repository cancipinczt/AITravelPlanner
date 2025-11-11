import { apiClient } from './apiClient'

export interface Trip {
  id: string
  title: string
  destination: string
  budget?: number
  travelers_count: number
  days: number
  preference_name?: string
  created_at: string
}

export interface TotalBudgetSummary {
  total_budget: number
  budget_trip_count: number
}

export const tripService = {
  // 获取旅行计划列表
  async getTrips(): Promise<Trip[]> {
    const response = await apiClient.get('/trips')
    return response.data
  },

  // 获取单个旅行计划详情
  async getTrip(tripId: string): Promise<Trip> {
    const response = await apiClient.get(`/trips/${tripId}`)
    return response.data
  },

  // 获取用户总预算统计
  async getUserBudgetSummary(userId: string): Promise<TotalBudgetSummary> {
    const response = await apiClient.get(`/users/${userId}/budget/summary`)
    return response.data
  },

  // 创建旅行计划
  async createTrip(tripData: any): Promise<Trip> {
    const response = await apiClient.post('/trips', tripData)
    return response.data
  },

  // 更新旅行计划
  async updateTrip(tripId: string, tripData: any): Promise<Trip> {
    const response = await apiClient.put(`/trips/${tripId}`, tripData)
    return response.data
  },

  // 删除旅行计划
  async deleteTrip(tripId: string): Promise<void> {
    await apiClient.delete(`/trips/${tripId}`)
  }
}