import { createApp } from 'vue'
import App from './App.vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import router from './router'
import { handleError } from './utils/errorHandler'

// 设置页面标题
document.title = 'LeafView - 您的专属相册管家'

const app = createApp(App)

app.config.errorHandler = handleError

app.use(ElementPlus)
app.use(router)

app.mount('#app')
