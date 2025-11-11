<template>
  <div class="user-preference-manager">
    <!-- 偏好列表 -->
    <div v-if="preferenceStore.preferences.length > 0" class="preferences-list">
      <div class="preferences-header">
        <h4>我的旅行偏好</h4>
        <el-button type="success" size="small" @click="showCreateForm = true">
          创建新偏好
        </el-button>
      </div>
      
      <div class="preferences-grid">
        <el-card 
          v-for="preference in preferenceStore.preferences" 
          :key="preference.id"
          class="preference-item"
        >
          <div class="preference-header">
            <h5>{{ preference.name || '未命名偏好' }}</h5>
            <el-tag size="small" type="info">
              {{ formatDate(preference.created_at, 'short') }}
            </el-tag>
          </div>
          
          <div class="preference-content">
            <div class="preference-field">
              <label>旅行偏好：</label>
              <span>{{ preference.travel_preferences || '未设置' }}</span>
            </div>
            <div class="preference-field">
              <label>特殊需求：</label>
              <span>{{ preference.special_requirements || '未设置' }}</span>
            </div>
          </div>
          
          <div class="preference-actions">
            <el-button type="primary" size="small" link @click="editPreference(preference)">
              编辑
            </el-button>
            <el-button type="danger" size="small" link @click="deletePreference(preference.id)">
              删除
            </el-button>
          </div>
        </el-card>
      </div>
    </div>
    
    <!-- 无偏好提示 -->
    <div v-else class="no-preference">
      <el-empty description="暂无偏好设置">
        <el-button type="primary" @click="showCreateForm = true">创建偏好</el-button>
      </el-empty>
    </div>
    
    <!-- 编辑偏好表单 -->
    <el-dialog 
      v-model="showEditForm" 
      :title="`编辑偏好：${currentPreference?.name || ''}`" 
      width="600px"
      :before-close="handleDialogClose"
    >
      <el-form :model="editForm" label-width="100px" ref="editFormRef">
        <el-form-item label="偏好名称" prop="name">
          <el-input
            v-model="editForm.name"
            placeholder="请输入偏好名称"
            maxlength="50"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="旅行偏好">
          <el-input
            v-model="editForm.travel_preferences"
            type="textarea"
            :rows="4"
            placeholder="请输入您的旅行偏好"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="特殊需求">
          <el-input
            v-model="editForm.special_requirements"
            type="textarea"
            :rows="3"
            placeholder="请输入特殊需求"
            maxlength="300"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showEditForm = false">取消</el-button>
        <el-button type="primary" :loading="loading" @click="handleUpdate">保存</el-button>
      </template>
    </el-dialog>
    
    <!-- 创建偏好表单 -->
    <el-dialog 
      v-model="showCreateForm" 
      title="创建旅行偏好" 
      width="600px"
      :before-close="handleDialogClose"
    >
      <UserPreferenceCreator @preference-created="handlePreferenceCreated" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useUserPreferenceStore } from '@/stores'
import { ElMessage, ElMessageBox } from 'element-plus'
import UserPreferenceCreator from './UserPreferenceCreator.vue'

const preferenceStore = useUserPreferenceStore()
const emit = defineEmits(['preference-updated', 'preference-created', 'preference-deleted'])

// 状态管理
const showEditForm = ref(false)
const showCreateForm = ref(false)
const loading = ref(false)
const currentPreference = ref<any>(null)

// 表单引用
const editFormRef = ref()

// 表单数据
const editForm = reactive({
  name: '',
  travel_preferences: '',
  special_requirements: ''
})

// 生命周期
onMounted(async () => {
  await loadPreferences()
})

// 方法
const loadPreferences = async () => {
  await preferenceStore.fetchUserPreferences()
}

const editPreference = (preference: any) => {
  currentPreference.value = preference
  editForm.name = preference.name || ''
  editForm.travel_preferences = preference.travel_preferences || ''
  editForm.special_requirements = preference.special_requirements || ''
  showEditForm.value = true
}

const deletePreference = async (preferenceId: string) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除这个旅行偏好吗？此操作不可恢复。',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    const result = await preferenceStore.deleteUserPreferences(preferenceId)
    if (result.success) {
      ElMessage.success('偏好删除成功')
      emit('preference-deleted', preferenceId)
    } else {
      ElMessage.error(result.message || '删除失败')
    }
  } catch (error) {
    // 用户取消删除
  }
}

const handleDialogClose = (done: () => void) => {
  done()
}

const handleUpdate = async () => {
  if (!currentPreference.value?.id) {
    ElMessage.error('无法识别要更新的偏好')
    return
  }

  if (!editForm.name.trim()) {
    ElMessage.warning('请输入偏好名称')
    return
  }

  loading.value = true
  try {
    const result = await preferenceStore.updateUserPreferences(
      currentPreference.value.id, 
      editForm
    )
    if (result.success) {
      showEditForm.value = false
      ElMessage.success('偏好更新成功')
      emit('preference-updated', result.data)
    } else {
      ElMessage.error(result.message || '更新失败')
    }
  } catch (error) {
    ElMessage.error('更新失败，请重试')
  } finally {
    loading.value = false
  }
}

const handlePreferenceCreated = (newPreference: any) => {
  showCreateForm.value = false
  emit('preference-created', newPreference)
}

const formatDate = (dateString: string | null, format: 'full' | 'short' = 'full') => {
  if (!dateString) return '未知'
  
  const date = new Date(dateString)
  if (format === 'short') {
    return date.toLocaleDateString('zh-CN')
  }
  
  return date.toLocaleString('zh-CN')
}
</script>

<style scoped>
.user-preference-manager {
  padding: 20px 0;
}

.current-preference h4 {
  margin-bottom: 15px;
  color: #333;
}

.preference-card {
  margin-bottom: 20px;
}

.preference-content {
  margin-bottom: 15px;
}

.preference-field {
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
}

.preference-field label {
  font-weight: bold;
  color: #606266;
  min-width: 80px;
  margin-right: 10px;
}

.preference-field span {
  flex: 1;
  color: #333;
  line-height: 1.5;
}

.preference-meta {
  margin-top: 15px;
  padding-top: 10px;
  border-top: 1px solid #f0f0f0;
}

.preference-meta small {
  color: #909399;
  margin-right: 15px;
}

.action-buttons {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.no-preference {
  text-align: center;
  padding: 40px 0;
}
</style>