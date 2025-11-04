import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    user: null,
    travelPlans: []
  }),
  actions: {
    // 存储操作
  }
})