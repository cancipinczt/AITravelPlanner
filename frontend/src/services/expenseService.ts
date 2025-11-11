import { apiClient } from './apiClient'

export interface Expense {
  id: string
  trip_id: string
  amount: number
  description?: string
  expense_date: string
  created_at: string
  updated_at?: string
}

export interface ExpenseSummary {
  total_amount: number
  expense_count: number
}

export const expenseService = {
  // 获取费用列表
  async getExpenses(tripId: string, params?: any): Promise<Expense[]> {
    const response = await apiClient.get(`/trips/${tripId}/expenses`, { params })
    return response.data
  },

  // 获取单个费用详情
  async getExpense(tripId: string, expenseId: string): Promise<Expense> {
    const response = await apiClient.get(`/trips/${tripId}/expenses/${expenseId}`)
    return response.data
  },

  // 创建费用记录
  async createExpense(tripId: string, expenseData: any): Promise<Expense> {
    const response = await apiClient.post(`/trips/${tripId}/expenses`, expenseData)
    return response.data
  },

  // 更新费用记录
  async updateExpense(tripId: string, expenseId: string, expenseData: any): Promise<Expense> {
    const response = await apiClient.put(`/trips/${tripId}/expenses/${expenseId}`, expenseData)
    return response.data
  },

  // 删除费用记录
  async deleteExpense(tripId: string, expenseId: string): Promise<void> {
    await apiClient.delete(`/trips/${tripId}/expenses/${expenseId}`)
  },

  // 获取旅行计划费用统计
  async getTripExpenseSummary(tripId: string): Promise<ExpenseSummary> {
    const response = await apiClient.get(`/trips/${tripId}/expenses/summary`)
    return response.data
  },

  // 获取用户所有旅行计划费用统计
  async getUserExpenseSummary(userId: string): Promise<ExpenseSummary> {
    const response = await apiClient.get(`/users/${userId}/expenses/summary`)
    return response.data
  }
}