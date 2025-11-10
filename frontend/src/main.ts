import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'

const app = createApp(App)

// 注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

app.mount('#app')

// 添加全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue应用错误:', err)
  console.error('组件实例:', instance)
  console.error('错误信息:', info)
}

// 添加未捕获的Promise错误处理
window.addEventListener('unhandledrejection', (event) => {
  console.error('未处理的Promise错误:', event.reason)
  event.preventDefault()
})