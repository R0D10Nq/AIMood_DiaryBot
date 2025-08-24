<template>
  <v-app>
    <!-- Navigation Drawer -->
    <v-navigation-drawer
      v-model="drawer"
      :rail="rail"
      permanent
      app
    >
      <v-list-item
        :prepend-avatar="avatarUrl"
        :title="currentUser?.first_name || 'Пользователь'"
        :subtitle="currentUser?.username || 'Гость'"
      >
        <template v-slot:append>
          <v-btn
            variant="text"
            icon="mdi-chevron-left"
            @click.stop="rail = !rail"
          ></v-btn>
        </template>
      </v-list-item>

      <v-divider></v-divider>

      <v-list density="compact" nav>
        <v-list-item
          v-for="item in navigationItems"
          :key="item.value"
          :prepend-icon="item.icon"
          :title="item.title"
          :value="item.value"
          :to="item.to"
          color="primary"
        ></v-list-item>
      </v-list>

      <template v-slot:append>
        <div class="pa-2">
          <v-btn
            block
            :prepend-icon="darkTheme ? 'mdi-brightness-7' : 'mdi-brightness-4'"
            @click="toggleTheme"
            variant="outlined"
          >
            {{ darkTheme ? 'Светлая' : 'Темная' }}
          </v-btn>
        </div>
      </template>
    </v-navigation-drawer>

    <!-- App Bar -->
    <v-app-bar
      color="primary"
      prominent
      app
    >
      <v-app-bar-nav-icon
        variant="text"
        @click.stop="drawer = !drawer"
      ></v-app-bar-nav-icon>

      <v-toolbar-title>
        <v-icon class="me-2">mdi-brain</v-icon>
        AI Mood Diary
      </v-toolbar-title>

      <v-spacer></v-spacer>

      <!-- API Status Indicator -->
      <v-chip
        :color="apiHealthy ? 'success' : 'error'"
        :prepend-icon="apiHealthy ? 'mdi-check-circle' : 'mdi-alert-circle'"
        variant="outlined"
        class="me-4"
      >
        {{ apiHealthy ? 'API Подключен' : 'API Недоступен' }}
      </v-chip>

      <!-- User Menu -->
      <v-menu>
        <template v-slot:activator="{ props }">
          <v-btn
            icon="mdi-account-circle"
            v-bind="props"
          ></v-btn>
        </template>
        <v-list>
          <v-list-item
            title="Профиль"
            prepend-icon="mdi-account"
            @click="openProfile"
          ></v-list-item>
          <v-list-item
            title="Настройки"
            prepend-icon="mdi-cog"
            to="/settings"
          ></v-list-item>
          <v-divider></v-divider>
          <v-list-item
            title="О проекте"
            prepend-icon="mdi-information"
            @click="showAbout = true"
          ></v-list-item>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Main Content -->
    <v-main>
      <v-container fluid>
        <!-- Error Alert -->
        <v-alert
          v-if="error"
          type="error"
          variant="tonal"
          closable
          @click:close="clearError"
          class="mb-4"
        >
          {{ error }}
        </v-alert>

        <!-- Loading Overlay -->
        <v-overlay
          :model-value="loading"
          class="align-center justify-center"
        >
          <v-progress-circular
            color="primary"
            indeterminate
            size="64"
          ></v-progress-circular>
        </v-overlay>

        <!-- Router View -->
        <router-view />
      </v-container>
    </v-main>

    <!-- About Dialog -->
    <v-dialog v-model="showAbout" max-width="600">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon class="me-2">mdi-brain</v-icon>
          О проекте AI Mood Diary
        </v-card-title>
        <v-card-text>
          <p class="mb-4">
            <strong>AI Mood Diary Bot</strong> - интеллектуальная система для отслеживания 
            эмоционального состояния с использованием искусственного интеллекта.
          </p>
          
          <v-list density="compact">
            <v-list-subheader>Технологии:</v-list-subheader>
            <v-list-item title="FastAPI + Python" prepend-icon="mdi-language-python"></v-list-item>
            <v-list-item title="Vue.js 3 + Vuetify" prepend-icon="mdi-vuejs"></v-list-item>
            <v-list-item title="Google Gemini AI" prepend-icon="mdi-robot"></v-list-item>
            <v-list-item title="Telegram Bot API" prepend-icon="mdi-telegram"></v-list-item>
            <v-list-item title="SQLite Database" prepend-icon="mdi-database"></v-list-item>
          </v-list>

          <p class="mt-4 text-caption text-medium-emphasis">
            Версия: 1.0.0<br>
            Разработано как демонстрация навыков middle-разработчика
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="primary"
            @click="showAbout = false"
          >
            Закрыть
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Snackbar for notifications -->
    <v-snackbar
      v-model="snackbar.show"
      :color="snackbar.color"
      :timeout="snackbar.timeout"
    >
      {{ snackbar.text }}
      <template v-slot:actions>
        <v-btn
          variant="text"
          @click="snackbar.show = false"
        >
          Закрыть
        </v-btn>
      </template>
    </v-snackbar>
  </v-app>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useTheme } from 'vuetify'
import { useMoodStore } from './stores/mood'
import { storeToRefs } from 'pinia'

const router = useRouter()
const theme = useTheme()
const moodStore = useMoodStore()

// Reactive refs from store
const { currentUser, loading, error, darkTheme } = storeToRefs(moodStore)

// Local reactive data
const drawer = ref(true)
const rail = ref(false)
const showAbout = ref(false)
const apiHealthy = ref(true)
const snackbar = ref({
  show: false,
  text: '',
  color: 'success',
  timeout: 4000
})

// Navigation items
const navigationItems = ref([
  {
    title: 'Дашборд',
    value: 'dashboard',
    icon: 'mdi-view-dashboard',
    to: '/'
  },
  {
    title: 'Аналитика',
    value: 'analytics', 
    icon: 'mdi-chart-line',
    to: '/analytics'
  },
  {
    title: 'Добавить запись',
    value: 'mood-entry',
    icon: 'mdi-plus-circle',
    to: '/mood-entry'
  },
  {
    title: 'Настройки',
    value: 'settings',
    icon: 'mdi-cog',
    to: '/settings'
  }
])

// Computed properties
const avatarUrl = computed(() => {
  return currentUser.value?.first_name 
    ? `https://ui-avatars.com/api/?name=${encodeURIComponent(currentUser.value.first_name)}&background=1976D2&color=fff`
    : 'https://ui-avatars.com/api/?name=User&background=1976D2&color=fff'
})

// Methods
const toggleTheme = () => {
  moodStore.toggleTheme()
  theme.global.name.value = darkTheme.value ? 'dark' : 'light'
}

const clearError = () => {
  moodStore.clearError()
}

const openProfile = () => {
  if (currentUser.value) {
    router.push(`/user/${currentUser.value.id}`)
  }
}

const checkApiHealth = async () => {
  apiHealthy.value = await moodStore.checkApiHealth()
  
  if (!apiHealthy.value) {
    showNotification('API недоступен. Некоторые функции могут не работать.', 'warning', 6000)
  }
}

const showNotification = (text, color = 'success', timeout = 4000) => {
  snackbar.value = {
    show: true,
    text,
    color,
    timeout
  }
}

// Lifecycle hooks
onMounted(async () => {
  // Load user preferences
  moodStore.loadCurrentUser()
  moodStore.loadThemePreference()
  
  // Apply theme
  theme.global.name.value = darkTheme.value ? 'dark' : 'light'
  
  // Check API health
  await checkApiHealth()
  
  // Set up a demo user if none exists
  if (!currentUser.value) {
    moodStore.setCurrentUser({
      id: 1,
      telegram_id: 123456789,
      first_name: 'Demo User',
      username: 'demo_user'
    })
  }
  
  // Check API health periodically
  setInterval(checkApiHealth, 30000) // Every 30 seconds
})

// Provide snackbar function globally
window.showNotification = showNotification
</script>

<style scoped>
.v-app-bar .v-toolbar-title {
  font-weight: 600;
}

.v-navigation-drawer .v-list-item {
  border-radius: 8px;
  margin: 4px 8px;
}
</style>