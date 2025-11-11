<template>
  <div class="preference-creator">
    <el-form 
      ref="formRef" 
      :model="form" 
      :rules="rules" 
      label-width="120px"
      @submit.prevent="handleCreate"
    >
      <el-form-item label="偏好名称" prop="name">
        <el-input 
          v-model="form.name" 
          placeholder="请输入偏好名称，如：商务出行、家庭旅行等"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="旅行偏好" prop="travel_preferences">
        <el-input
          v-model="form.travel_preferences"
          type="textarea"
          :rows="3"
          placeholder="请输入您的旅行偏好，如：喜欢文化古迹、偏好自然风光、注重美食体验等"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item label="特殊需求" prop="special_requirements">
        <el-input
          v-model="form.special_requirements"
          type="textarea"
          :rows="3"
          placeholder="请输入您的特殊需求，如：饮食禁忌、行动不便、过敏情况等"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <el-form-item>
        <div class="form-actions">
          <el-button type="primary" @click="handleCreate" :loading="loading">
            创建偏好
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </div>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useUserPreferenceStore } from '@/stores'

const preferenceStore = useUserPreferenceStore()
const emit = defineEmits(['preference-created'])

// 表单引用和状态
const formRef = ref<FormInstance>()
const loading = ref(false)

// 表单数据
const form = reactive({
  name: '',
  travel_preferences: '',
  special_requirements: ''
})

// 表单验证规则
const rules: FormRules = {
  name: [
    { required: true, message: '请输入偏好名称', trigger: 'blur' },
    { min: 1, max: 50, message: '偏好名称长度在 1 到 50 个字符', trigger: 'blur' }
  ],
  travel_preferences: [
    { 
      validator: (rule: any, value: string, callback: any) => {
        if (!value && !form.special_requirements) {
          callback(new Error('请至少填写旅行偏好或特殊需求中的一项'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ],
  special_requirements: [
    { 
      validator: (rule: any, value: string, callback: any) => {
        if (!value && !form.travel_preferences) {
          callback(new Error('请至少填写旅行偏好或特殊需求中的一项'))
        } else {
          callback()
        }
      }, 
      trigger: 'blur' 
    }
  ]
}

// 处理方法
const handleCreate = async () => {
  if (!formRef.value) return
  
  try {
    const valid = await formRef.value.validate()
    if (!valid) return
    
    loading.value = true
    
    const result = await preferenceStore.createUserPreferences({
      name: form.name,
      travel_preferences: form.travel_preferences || undefined,
      special_requirements: form.special_requirements || undefined
    })
    
    if (result.success) {
      ElMessage.success('偏好创建成功')
      emit('preference-created', result.data)
      handleReset()
    } else {
      ElMessage.error(result.message || '创建失败')
    }
  } catch (error) {
    console.error('创建偏好失败:', error)
  } finally {
    loading.value = false
  }
}

const handleReset = () => {
  if (formRef.value) {
    formRef.value.resetFields()
  }
}
</script>

<style scoped>
.preference-creator {
  padding: 20px 0;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

:deep(.el-form-item__label) {
  font-weight: bold;
}

:deep(.el-textarea .el-input__count) {
  background: transparent;
}
</style>