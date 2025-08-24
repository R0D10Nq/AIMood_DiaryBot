import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'

// Vuetify
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import * as components from 'vuetify/components'
import * as directives from 'vuetify/directives'
import { mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

// Chart.js
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
)

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: 'mdi',
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: 'light',
    themes: {
      light: {
        colors: {
          primary: '#1976D2',
          secondary: '#424242',
          accent: '#82B1FF',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
      dark: {
        colors: {
          primary: '#2196F3',
          secondary: '#424242',
          accent: '#FF4081',
          error: '#FF5252',
          info: '#2196F3',
          success: '#4CAF50',
          warning: '#FB8C00',
        },
      },
    },
  },
})

const app = createApp(App)
const pinia = createPinia()

// Global notification system
app.config.globalProperties.$notify = (message, type = 'info') => {
  console.log(`[${type.toUpperCase()}] ${message}`)
  // In a real implementation, this would show a toast/snackbar
}

// Add global notification function to window for easy access
window.showNotification = (message, type = 'info') => {
  console.log(`[${type.toUpperCase()}] ${message}`)
  // In a real implementation, this would show a toast/snackbar
  // For now, using browser notification API as fallback
  if (Notification.permission === 'granted') {
    new Notification(message, {
      icon: '/favicon.ico',
      badge: '/favicon.ico'
    })
  }
}

// Request notification permission
if ('Notification' in window && Notification.permission === 'default') {
  Notification.requestPermission()
}

app.use(pinia)
app.use(router)
app.use(vuetify)

app.mount('#app')