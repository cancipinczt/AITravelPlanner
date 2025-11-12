<template>
  <div id="app">
    <el-container>
      <el-header v-if="authStore.isAuthenticated">
        <div class="header-content">
          <div class="header-title-section">
            <div class="logo-icon">✈️</div>
            <h1 class="header-title">AI旅行规划师</h1>
          </div>
          <div class="nav-menu">
            <router-link to="/" class="nav-link">
              <span class="nav-icon">🏠</span>
              <span class="nav-text">首页</span>
            </router-link>
            <router-link to="/map-demo" class="nav-link">
              <span class="nav-icon">🗺️</span>
              <span class="nav-text">地图导航</span>
            </router-link>
            <router-link to="/expense-management" class="nav-link">
              <span class="nav-icon">💰</span>
              <span class="nav-text">费用管理</span>
            </router-link>
            <div class="user-menu">
              <el-dropdown>
                <span class="user-info">
                  <el-avatar :size="36" class="user-avatar">
                    {{ authStore.user?.username?.charAt(0) }}
                  </el-avatar>
                  <span class="username">{{ authStore.user?.username }}</span>
                  <el-icon class="dropdown-arrow"><arrow-down /></el-icon>
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item @click="$router.push('/profile')">
                      <el-icon><user /></el-icon>
                      个人中心
                    </el-dropdown-item>
                    <el-dropdown-item @click="handleLogout">
                      <el-icon><switch-button /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores'
import { ArrowDown, User, SwitchButton } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = async () => {
  try {
    await authStore.logout()
    ElMessage.success('已退出登录')
    router.push('/login')
  } catch (error) {
    console.error('登出失败:', error)
    ElMessage.error('登出失败')
  }
}

onMounted(async () => {
  // 应用启动时初始化认证状态
  await authStore.initializeAuth()
})
</script>

<style scoped>
#app {
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.el-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  line-height: 64px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
  height: 100%;
}

.header-title-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 28px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.header-title {
  margin: 0;
  font-size: 26px;
  font-weight: 700;
  background: linear-gradient(45deg, #fff, #e3f2fd);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
  letter-spacing: 0.5px;
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 16px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
  text-decoration: none;
  padding: 4px 12px;
  border-radius: 6px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  font-weight: 500;
  position: relative;
  overflow: hidden;
  line-height: 1.2;
  height: auto;
}

.nav-link::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.nav-link:hover::before {
  left: 100%;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.12);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.nav-link.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.25);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.nav-icon {
  font-size: 14px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.nav-text {
  font-size: 13px;
  font-weight: 600;
}

.user-menu {
  margin-left: 16px;
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 6px;
  color: white;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 6px;
  transition: all 0.3s ease;
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  line-height: 1.2;
  height: auto;
  align-self: center;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.18);
  transform: translateY(-1px);
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.12);
}

.user-avatar {
  background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
  font-weight: 600;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
}

.username {
  font-weight: 600;
  font-size: 12px;
}

.dropdown-arrow {
  transition: transform 0.3s ease;
  font-size: 10px;
}

.user-info:hover .dropdown-arrow {
  transform: rotate(180deg);
}

.el-dropdown-menu {
  border-radius: 8px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.15);
  border: 1px solid rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.el-dropdown-menu__item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  transition: all 0.2s ease;
}

.el-dropdown-menu__item:hover {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.el-main {
  padding: 0;
  min-height: calc(100vh - 64px);
  background: #f8fafc;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .header-content {
    padding: 0 16px;
    flex-direction: column;
    height: auto;
    line-height: 1.5;
  }
  
  .nav-menu {
    gap: 8px;
    margin-top: 8px;
  }
  
  .nav-link {
    padding: 3px 8px;
    font-size: 12px;
  }
  
  .header-title {
    font-size: 22px;
  }
}
</style>