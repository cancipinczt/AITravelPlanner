<template>
  <div class="trip-expenses">
    <div class="page-header">
      <el-button type="text" @click="goBack" class="back-button">
        <el-icon><arrow-left /></el-icon>
        返回费用管理
      </el-button>
      <h2>{{ tripInfo.title }} - 费用管理</h2>
      <p>目的地：{{ tripInfo.destination }}</p>
    </div>
    
    <el-card class="content-card">
      <!-- 当前旅行计划预算和花销统计 -->
      <div class="budget-summary">
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><money /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">预算</div>
                  <div class="stat-value">¥{{ tripInfo.budget || 0 }}</div>
                </div>
              </div>
            </el-card>
          </el-col>
          <el-col :span="8">
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
          <el-col :span="8">
            <el-card class="stat-card" shadow="hover">
              <div class="stat-content">
                <div class="stat-icon">
                  <el-icon><wallet /></el-icon>
                </div>
                <div class="stat-info">
                  <div class="stat-label">剩余预算</div>
                  <div class="stat-value" :class="{ 'negative': remainingBudget < 0 }">
                    ¥{{ remainingBudget }}
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
      
      <!-- 操作栏 -->
      <div class="action-bar">
        <el-button type="primary" @click="fetchExpenses" :loading="loading">
          <el-icon><refresh /></el-icon>
          刷新列表
        </el-button>
        <el-button type="success" @click="showCreateDialog = true">
          <el-icon><plus /></el-icon>
          添加费用
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
        <el-button type="primary" @click="fetchExpenses" style="margin-top: 10px;">
          重试加载
        </el-button>
      </div>
      
      <!-- 费用列表 -->
      <div v-else-if="expenses.length > 0" class="expenses-container">
        <el-table :data="expenses" style="width: 100%">
          <el-table-column prop="amount" label="金额" width="120">
            <template #default="{ row }">
              ¥{{ row.amount }}
            </template>
          </el-table-column>
          
          <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
          <el-table-column prop="expense_date" label="消费日期" width="120" >
            <template #default="scope">
              <span>{{ formatDate(scope.row.expense_date) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column prop="created_at" label="创建时间" width="160">
            <template #default="scope">
              <span>{{ formatDateTime(scope.row.created_at) }}</span>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" align="center">
            <template #default="scope">
              <el-button 
                type="primary" 
                size="small" 
                @click="editExpense(scope.row)"
              >
                编辑
              </el-button>
              <el-button 
                type="danger" 
                size="small" 
                @click="deleteExpense(scope.row.id)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
      
      <div v-else class="empty-state">
        <p>暂无费用记录</p>
        <p class="empty-tip">点击"添加费用"按钮开始记录您的旅行支出</p>
      </div>
    </el-card>
    
    <!-- 添加/编辑费用对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      :title="editingExpense ? '编辑费用' : '添加费用'"
      width="500px"
    >
      <el-form :model="expenseForm" label-width="80px">
        <el-form-item label="金额" prop="amount" :rules="[{ required: true, message: '请输入金额', trigger: 'blur' }]">
          <el-input-number v-model="expenseForm.amount" :min="0" :precision="2" placeholder="请输入金额" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input v-model="expenseForm.description" type="textarea" :rows="2" placeholder="请输入费用描述（可选）" />
        </el-form-item>
        
        <el-form-item label="消费日期" prop="expense_date" :rules="[{ required: true, message: '请选择消费日期', trigger: 'change' }]">
          <el-date-picker v-model="expenseForm.expense_date" type="date" placeholder="选择日期" value-format="YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button type="primary" @click="saveExpense" :loading="saving">
          {{ editingExpense ? '更新' : '保存' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '@/stores'
import { api } from '@/stores'  // 直接导入api实例
import { Money, ShoppingCart, Wallet, Refresh, Plus, ArrowLeft } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const tripId = ref(route.params.tripId as string)
const tripInfo = ref({
  title: '',
  destination: '',
  budget: 0
})
const expenses = ref([])
const totalExpenses = ref(0)
const loading = ref(false)
const error = ref('')
const showCreateDialog = ref(false)
const saving = ref(false)
const editingExpense = ref(null)

const expenseForm = ref({
  amount: '',
  description: '',
  expense_date: ''
})

// 计算剩余预算
const remainingBudget = computed(() => {
  const budget = tripInfo.value.budget || 0
  return (budget - totalExpenses.value).toFixed(2)
})

// 页面加载时初始化
onMounted(() => {
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  fetchTripInfo()
  fetchExpenses()
})

// 获取旅行计划信息
const fetchTripInfo = async () => {
  try {
    // 使用api实例，路径不需要包含/api/v1前缀
    const response = await api.get(`/trips/${tripId.value}`)
    tripInfo.value = response.data
  } catch (err) {
    console.error('获取旅行计划信息失败:', err)
    error.value = '无法获取旅行计划信息'
    ElMessage.error('获取旅行计划信息失败')
  }
}

// 获取费用列表
const fetchExpenses = async () => {
  try {
    loading.value = true
    error.value = ''
    // 使用api实例，路径不需要包含/api/v1前缀
    const response = await api.get(`/trips/${tripId.value}/expenses`)
    expenses.value = response.data
    calculateTotalExpenses()
  } catch (err) {
    console.error('获取费用列表失败:', err)
    error.value = err.response?.data?.detail || '网络错误'
    ElMessage.error('获取费用列表失败')
  } finally {
    loading.value = false
  }
}

// 计算总花销
const calculateTotalExpenses = () => {
  totalExpenses.value = expenses.value.reduce((total, expense) => {
    return total + parseFloat(expense.amount || 0)
  }, 0)
}

// 添加费用
const saveExpense = async () => {
  try {
    saving.value = true
    const formData = {
      ...expenseForm.value,
      trip_id: tripId.value
    }
    
    if (editingExpense.value) {
      // 更新费用 - 使用api实例
      await api.put(`/trips/${tripId.value}/expenses/${editingExpense.value.id}`, formData)
      ElMessage.success('费用更新成功')
    } else {
      // 创建费用 - 使用api实例
      await api.post(`/trips/${tripId.value}/expenses`, formData)
      ElMessage.success('费用添加成功')
    }
    
    showCreateDialog.value = false
    fetchExpenses()
    resetForm()
  } catch (err) {
    console.error('保存费用失败:', err)
    error.value = err.response?.data?.detail || '保存失败'
    ElMessage.error('保存费用失败')
  } finally {
    saving.value = false
  }
}

// 编辑费用
const editExpense = (expense) => {
  editingExpense.value = expense
  expenseForm.value = {
    amount: parseFloat(expense.amount),
    description: expense.description,
    expense_date: new Date(expense.expense_date)
  }
  showCreateDialog.value = true
}

// 删除费用
const deleteExpense = async (expenseId) => {
  try {
    await ElMessageBox.confirm('确定要删除这笔费用吗？', '确认删除', {
      type: 'warning'
    })
    
    // 删除费用 - 使用api实例
    await api.delete(`/trips/${tripId.value}/expenses/${expenseId}`)
    ElMessage.success('删除成功')
    fetchExpenses()
  } catch (err) {
    if (err !== 'cancel') {
      console.error('删除费用失败:', err)
      ElMessage.error('删除失败')
    }
  }
}

// 重置表单
const resetForm = () => {
  expenseForm.value = {
    amount: 0,
    description: '',
    expense_date: new Date()
  }
  editingExpense.value = null
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化日期时间
const formatDateTime = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 返回费用管理页面
const goBack = () => {
  router.push('/expense-management')
}
</script>

<style scoped>
.trip-expenses {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 30px;
}

.back-button {
  margin-bottom: 10px;
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
  padding: 20px;
}

.budget-summary {
  margin-bottom: 30px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  padding: 10px;
}

.stat-icon {
  font-size: 36px;
  color: #409EFF;
  margin-right: 15px;
}

.stat-info {
  flex: 1;
}

.stat-label {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 20px;
  font-weight: bold;
  color: #333;
}

.stat-value.negative {
  color: #F56C6C;
}

.action-bar {
  margin-bottom: 20px;
}

.expenses-container {
  margin-top: 20px;
}

.amount {
  color: #E6A23C;
  font-weight: bold;
}

.description {
  line-height: 1.4;
}

.empty-state {
  text-align: center;
  padding: 40px 0;
  color: #999;
}

.empty-tip {
  font-size: 14px;
  margin-top: 10px;
}
</style>