<template>
  <div class="expense-management">
    <div class="page-header">
      <h2>费用管理</h2>
      <p>管理您的旅行费用</p>
    </div>
    
    <el-card class="content-card">
      <!-- 总预算和总花销统计 -->
      <div class="budget-summary">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><money /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">总预算</div>
                  <div class="stat-value">¥{{ totalBudget }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="12">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><shopping-cart /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">总花销</div>
                  <div class="stat-value">¥{{ totalExpenses }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" @click="fetchTravelPlans" :loading="loading">
          <el-icon><refresh /></el-icon>
          刷新列表
        </el-button>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>
      
      <!-- 错误状态 -->
      <div v-else-if="error" class="error-state">
        <el-alert
          :title="`加载失败: ${error}`"
          type="error"
          show-icon
          :closable="false"
        />
        <el-button type="primary" @click="fetchTravelPlans" style="margin-top: 10px;">
          重试加载
        </el-button>
      </div>
      
      <!-- 旅行计划列表 -->
      <div v-else-if="travelPlans.length > 0" class="plans-container">
        <el-table :data="travelPlans" style="width: 100%" :header-cell-style="{ textAlign: 'center' }" :cell-style="{ textAlign: 'center' }">
          <el-table-column prop="title" label="旅行计划" min-width="120" align="center">
            <template #default="scope">
              <strong>{{ scope.row.title }}</strong>
            </template>
          </el-table-column>
          
          <el-table-column prop="destination" label="目的地" width="140" align="center">
            <template #default="scope">
              <el-tag type="primary">{{ scope.row.destination }}</el-tag>
            </template>
          </el-table-column>
          
          <el-table-column prop="budget" label="预算" width="140" align="center">
            <template #default="scope">
              <span v-if="scope.row.budget" class="budget-amount">
                ¥{{ scope.row.budget }}
              </span>
              <span v-else class="no-budget">未设置</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="140" align="center">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="goToTripExpenses(scope.row.id)"
              >
                管理费用
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="empty-state">
        <p>暂无旅行计划数据</p>
        <el-button type="success" @click="goToAIPlanning" style="margin-top: 10px;">
          创建旅行计划
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores'
import { api } from '@/stores'  // 直接导入api实例
import { Money, ShoppingCart, Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const authStore = useAuthStore()
const travelPlans = ref([])
const totalBudget = ref(0)
const totalExpenses = ref(0)
const budgetSummary = ref(null) // 添加budgetSummary变量定义
const loading = ref(false)
const error = ref('')

// 页面加载时检查认证状态
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchTravelPlans()
})

// 获取旅行计划列表
const fetchTravelPlans = async () => {
  try {
    loading.value = true
    error.value = ''
    // 直接使用导入的api实例，路径不需要包含/api/v1前缀
    const response = await api.get('/trips')
    travelPlans.value = response.data
    
    // 获取到旅行计划后，计算总预算和总花销
    await calculateBudgetAndExpenses()
  } catch (err) {
    console.error('获取旅行计划失败:', err)
    error.value = err.response?.data?.detail || '网络错误'
    ElMessage.error('获取旅行计划失败')
  } finally {
    loading.value = false
  }
}

// 计算总预算和总花销
const calculateBudgetAndExpenses = async () => {
  try {
    // 重置统计值
    totalBudget.value = 0
    totalExpenses.value = 0
    
    // 遍历每个旅行计划，获取预算和费用信息
    for (const plan of travelPlans.value) {
      // 累加预算
      if (plan.budget) {
        totalBudget.value += parseFloat(plan.budget)
      }
      
      // 获取该旅行计划的费用列表
      try {
        const expensesResponse = await api.get(`/trips/${plan.id}/expenses`)
        if (expensesResponse.data) {
          // 累加该旅行计划的所有费用
          const planExpenses = expensesResponse.data.reduce((sum: number, expense: any) => {
            return sum + parseFloat(expense.amount || 0)
          }, 0)
          totalExpenses.value += planExpenses
        }
      } catch (expenseError) {
        console.warn(`获取旅行计划 ${plan.title} 的费用失败:`, expenseError)
        // 单个旅行计划费用获取失败不影响整体统计
      }
    }
    
    ElMessage.success('预算统计更新成功')
  } catch (error) {
    console.error('计算预算和花销失败:', error)
    ElMessage.warning('预算统计更新失败')
  }
}

// 跳转到旅行计划费用管理页面
const goToTripExpenses = (tripId: string) => {
  router.push(`/trip-expenses/${tripId}`)
}

// 跳转到AI规划页面
const goToAIPlanning = () => {
  router.push('/ai-planning')
}
</script>

<style scoped>
.expense-management {
  min-height: calc(100vh - 64px);
  background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
  padding: 24px;
}

.page-header {
  text-align: center;
  margin-bottom: 32px;
  padding: 40px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  color: white;
  box-shadow: 0 8px 32px rgba(102, 126, 234, 0.2);
  backdrop-filter: blur(10px);
}

.page-header h2 {
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  background: linear-gradient(45deg, #fff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-header p {
  font-size: 18px;
  opacity: 0.9;
  font-weight: 500;
}

.content-card {
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  background: rgba(255, 255, 255, 0.95);
}

.budget-summary {
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 12px;
  border: none;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #f8fafc 0%, #e3f2fd 100%);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #2c3e50;
}

.action-bar {
  margin-bottom: 24px;
  display: flex;
  justify-content: flex-end;
}

.plans-container {
  margin-top: 16px;
}

:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  table-layout: fixed; /* 确保固定布局 */
}

:deep(.el-table th),
:deep(.el-table td) {
  text-align: center !important;
}

:deep(.el-table th) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
}

:deep(.el-table td) {
  background: rgba(255, 255, 255, 0.9);
  word-break: break-word;
}

.budget-amount {
  font-weight: 600;
  color: #52c41a;
}

.no-budget {
  color: #faad14;
  font-style: italic;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: #666;
}

.empty-state p {
  font-size: 16px;
  margin-bottom: 16px;
}

.loading-state,
.error-state {
  padding: 40px 20px;
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .expense-management {
    padding: 16px;
  }
  
  .page-header {
    padding: 24px 0;
    margin-bottom: 24px;
  }
  
  .page-header h2 {
    font-size: 28px;
  }
  
  .stat-content {
    flex-direction: column;
    text-align: center;
    gap: 12px;
  }
  
  .action-bar {
    justify-content: center;
  }
}
</style>