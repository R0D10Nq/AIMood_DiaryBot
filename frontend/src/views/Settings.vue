<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">
          <v-icon class="me-2">mdi-cog</v-icon>
          Настройки
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Персонализируйте ваш опыт использования дневника настроения
        </p>
      </v-col>
    </v-row>

    <v-row>
      <!-- User Profile -->
      <v-col cols="12" lg="8">
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-account</v-icon>
            Профиль пользователя
          </v-card-title>
          
          <v-card-text>
            <v-form v-model="profileFormValid">
              <v-row>
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userProfile.first_name"
                    label="Имя"
                    variant="outlined"
                    prepend-inner-icon="mdi-account"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userProfile.last_name"
                    label="Фамилия"
                    variant="outlined"
                    prepend-inner-icon="mdi-account"
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userProfile.username"
                    label="Имя пользователя"
                    variant="outlined"
                    prepend-inner-icon="mdi-at"
                    readonly
                  ></v-text-field>
                </v-col>
                
                <v-col cols="12" md="6">
                  <v-text-field
                    v-model="userProfile.timezone"
                    label="Часовой пояс"
                    variant="outlined"
                    prepend-inner-icon="mdi-clock"
                  ></v-text-field>
                </v-col>
              </v-row>
              
              <v-btn
                color="primary"
                @click="saveProfile"
                :loading="profileSaving"
                prepend-icon="mdi-content-save"
                class="mt-3"
              >
                Сохранить профиль
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>

        <!-- Notifications Settings -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-bell</v-icon>
            Уведомления
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="notifications.daily_reminder"
                    color="primary"
                    @change="saveNotificationSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Ежедневные напоминания</v-list-item-title>
                <v-list-item-subtitle>
                  Получать напоминания о записи настроения
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="notifications.weekly_summary"
                    color="primary"
                    @change="saveNotificationSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Еженедельная сводка</v-list-item-title>
                <v-list-item-subtitle>
                  Получать анализ настроения за неделю
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="notifications.ai_insights"
                    color="primary"
                    @change="saveNotificationSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>AI инсайты</v-list-item-title>
                <v-list-item-subtitle>
                  Получать персональные рекомендации от ИИ
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <!-- Reminder Time -->
            <div v-if="notifications.daily_reminder" class="mt-4">
              <v-divider class="mb-4"></v-divider>
              <v-row>
                <v-col cols="12" md="6">
                  <v-time-picker
                    v-model="notifications.reminder_time"
                    title="Время напоминания"
                    format="24hr"
                    @update:model-value="saveNotificationSettings"
                  ></v-time-picker>
                </v-col>
              </v-row>
            </div>
          </v-card-text>
        </v-card>

        <!-- Privacy Settings -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-shield-account</v-icon>
            Приватность и безопасность
          </v-card-title>
          
          <v-card-text>
            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="privacy.share_anonymous_data"
                    color="primary"
                    @change="savePrivacySettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Анонимные данные</v-list-item-title>
                <v-list-item-subtitle>
                  Разрешить использование анонимных данных для улучшения сервиса
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="privacy.ai_analysis"
                    color="primary"
                    @change="savePrivacySettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>AI анализ</v-list-item-title>
                <v-list-item-subtitle>
                  Разрешить анализ записей с помощью ИИ
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="privacy.data_export"
                    color="primary"
                    @change="savePrivacySettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Экспорт данных</v-list-item-title>
                <v-list-item-subtitle>
                  Разрешить экспорт личных данных
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>

            <v-divider class="my-4"></v-divider>

            <v-btn
              color="warning"
              variant="outlined"
              prepend-icon="mdi-download"
              @click="exportData"
              :loading="exporting"
              class="me-3"
            >
              Экспорт данных
            </v-btn>

            <v-btn
              color="error"
              variant="outlined"
              prepend-icon="mdi-delete"
              @click="confirmDelete = true"
            >
              Удалить аккаунт
            </v-btn>
          </v-card-text>
        </v-card>

        <!-- App Preferences -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-palette</v-icon>
            Настройки приложения
          </v-card-title>
          
          <v-card-text>
            <v-row>
              <v-col cols="12" md="6">
                <v-select
                  v-model="appSettings.theme"
                  :items="themeOptions"
                  label="Тема"
                  variant="outlined"
                  prepend-inner-icon="mdi-theme-light-dark"
                  @update:model-value="saveAppSettings"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="appSettings.language"
                  :items="languageOptions"
                  label="Язык"
                  variant="outlined"
                  prepend-inner-icon="mdi-translate"
                  @update:model-value="saveAppSettings"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="appSettings.dateFormat"
                  :items="dateFormatOptions"
                  label="Формат даты"
                  variant="outlined"
                  prepend-inner-icon="mdi-calendar"
                  @update:model-value="saveAppSettings"
                ></v-select>
              </v-col>
              
              <v-col cols="12" md="6">
                <v-select
                  v-model="appSettings.defaultView"
                  :items="viewOptions"
                  label="Стартовая страница"
                  variant="outlined"
                  prepend-inner-icon="mdi-home"
                  @update:model-value="saveAppSettings"
                ></v-select>
              </v-col>
            </v-row>

            <v-divider class="my-4"></v-divider>

            <v-list>
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="appSettings.autoSave"
                    color="primary"
                    @change="saveAppSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Автосохранение</v-list-item-title>
                <v-list-item-subtitle>
                  Автоматически сохранять черновики записей
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="appSettings.showTips"
                    color="primary"
                    @change="saveAppSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Подсказки</v-list-item-title>
                <v-list-item-subtitle>
                  Показывать полезные советы
                </v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <template v-slot:prepend>
                  <v-switch
                    v-model="appSettings.animations"
                    color="primary"
                    @change="saveAppSettings"
                  ></v-switch>
                </template>
                
                <v-list-item-title>Анимации</v-list-item-title>
                <v-list-item-subtitle>
                  Включить анимации интерфейса
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Sidebar -->
      <v-col cols="12" lg="4">
        <!-- Account Info -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-information</v-icon>
            Информация об аккаунте
          </v-card-title>
          
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>ID пользователя</v-list-item-title>
                <v-list-item-subtitle>{{ currentUser?.id || 'N/A' }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Telegram ID</v-list-item-title>
                <v-list-item-subtitle>{{ currentUser?.telegram_id || 'N/A' }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Дата регистрации</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(currentUser?.created_at) }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Записей создано</v-list-item-title>
                <v-list-item-subtitle>{{ currentUser?.mood_entries_count || 0 }}</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Последняя активность</v-list-item-title>
                <v-list-item-subtitle>{{ formatDate(currentUser?.last_activity) }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Support -->
        <v-card class="mb-6">
          <v-card-title>
            <v-icon class="me-2">mdi-help-circle</v-icon>
            Поддержка
          </v-card-title>
          
          <v-card-text>
            <v-list density="compact">
              <v-list-item prepend-icon="mdi-book-open" @click="openHelp">
                <v-list-item-title>Руководство пользователя</v-list-item-title>
              </v-list-item>
              
              <v-list-item prepend-icon="mdi-frequently-asked-questions" @click="openFAQ">
                <v-list-item-title>Часто задаваемые вопросы</v-list-item-title>
              </v-list-item>
              
              <v-list-item prepend-icon="mdi-email" @click="contactSupport">
                <v-list-item-title>Связаться с поддержкой</v-list-item-title>
              </v-list-item>
              
              <v-list-item prepend-icon="mdi-bug" @click="reportBug">
                <v-list-item-title>Сообщить об ошибке</v-list-item-title>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- App Version -->
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-information-outline</v-icon>
            О приложении
          </v-card-title>
          
          <v-card-text>
            <v-list density="compact">
              <v-list-item>
                <v-list-item-title>Версия</v-list-item-title>
                <v-list-item-subtitle>1.0.0</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item>
                <v-list-item-title>Последнее обновление</v-list-item-title>
                <v-list-item-subtitle>{{ new Date().toLocaleDateString('ru-RU') }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
            
            <v-btn
              color="primary"
              variant="outlined"
              block
              class="mt-3"
              @click="checkUpdates"
              :loading="checkingUpdates"
            >
              Проверить обновления
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="confirmDelete" max-width="400">
      <v-card>
        <v-card-title class="text-h5">
          <v-icon color="error" class="me-2">mdi-alert</v-icon>
          Удалить аккаунт?
        </v-card-title>
        
        <v-card-text>
          <p>Это действие нельзя отменить. Все ваши данные будут безвозвратно удалены.</p>
          
          <v-text-field
            v-model="deleteConfirmText"
            label="Введите 'УДАЛИТЬ' для подтверждения"
            variant="outlined"
            class="mt-3"
          ></v-text-field>
        </v-card-text>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn @click="confirmDelete = false">Отмена</v-btn>
          <v-btn
            color="error"
            :disabled="deleteConfirmText !== 'УДАЛИТЬ'"
            @click="deleteAccount"
            :loading="deleting"
          >
            Удалить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useMoodStore } from '../stores/mood'
import { storeToRefs } from 'pinia'

const router = useRouter()
const moodStore = useMoodStore()

const { currentUser } = storeToRefs(moodStore)

// Form validation
const profileFormValid = ref(false)

// Loading states
const profileSaving = ref(false)
const exporting = ref(false)
const deleting = ref(false)
const checkingUpdates = ref(false)

// Dialog states
const confirmDelete = ref(false)
const deleteConfirmText = ref('')

// User profile
const userProfile = ref({
  first_name: '',
  last_name: '',
  username: '',
  timezone: 'UTC+3'
})

// Notification settings
const notifications = ref({
  daily_reminder: true,
  weekly_summary: true,
  ai_insights: true,
  reminder_time: '19:00'
})

// Privacy settings
const privacy = ref({
  share_anonymous_data: false,
  ai_analysis: true,
  data_export: true
})

// App settings
const appSettings = ref({
  theme: 'auto',
  language: 'ru',
  dateFormat: 'dd.mm.yyyy',
  defaultView: 'dashboard',
  autoSave: true,
  showTips: true,
  animations: true
})

// Options
const themeOptions = [
  { title: 'Автоматически', value: 'auto' },
  { title: 'Светлая', value: 'light' },
  { title: 'Темная', value: 'dark' }
]

const languageOptions = [
  { title: 'Русский', value: 'ru' },
  { title: 'English', value: 'en' }
]

const dateFormatOptions = [
  { title: 'ДД.ММ.ГГГГ', value: 'dd.mm.yyyy' },
  { title: 'ММ/ДД/ГГГГ', value: 'mm/dd/yyyy' },
  { title: 'ГГГГ-ММ-ДД', value: 'yyyy-mm-dd' }
]

const viewOptions = [
  { title: 'Дашборд', value: 'dashboard' },
  { title: 'Аналитика', value: 'analytics' },
  { title: 'Новая запись', value: 'mood-entry' }
]

// Methods
const loadUserData = () => {
  if (currentUser.value) {
    userProfile.value = {
      first_name: currentUser.value.first_name || '',
      last_name: currentUser.value.last_name || '',
      username: currentUser.value.username || '',
      timezone: currentUser.value.timezone || 'UTC+3'
    }
  }
}

const saveProfile = async () => {
  profileSaving.value = true
  try {
    // Implementation for saving profile
    await new Promise(resolve => setTimeout(resolve, 1000)) // Mock delay
    window.showNotification('Профиль сохранен', 'success')
  } catch (error) {
    console.error('Error saving profile:', error)
    window.showNotification('Ошибка сохранения профиля', 'error')
  } finally {
    profileSaving.value = false
  }
}

const saveNotificationSettings = async () => {
  try {
    // Implementation for saving notification settings
    localStorage.setItem('moodDiary_notifications', JSON.stringify(notifications.value))
    window.showNotification('Настройки уведомлений сохранены', 'success')
  } catch (error) {
    console.error('Error saving notification settings:', error)
    window.showNotification('Ошибка сохранения настроек', 'error')
  }
}

const savePrivacySettings = async () => {
  try {
    // Implementation for saving privacy settings
    localStorage.setItem('moodDiary_privacy', JSON.stringify(privacy.value))
    window.showNotification('Настройки приватности сохранены', 'success')
  } catch (error) {
    console.error('Error saving privacy settings:', error)
    window.showNotification('Ошибка сохранения настроек', 'error')
  }
}

const saveAppSettings = async () => {
  try {
    // Implementation for saving app settings
    localStorage.setItem('moodDiary_appSettings', JSON.stringify(appSettings.value))
    
    // Apply theme change
    if (appSettings.value.theme !== 'auto') {
      // Theme application logic would go here
    }
    
    window.showNotification('Настройки приложения сохранены', 'success')
  } catch (error) {
    console.error('Error saving app settings:', error)
    window.showNotification('Ошибка сохранения настроек', 'error')
  }
}

const exportData = async () => {
  exporting.value = true
  try {
    // Implementation for data export
    await new Promise(resolve => setTimeout(resolve, 2000)) // Mock delay
    
    // Create and download a mock JSON file
    const data = {
      user: currentUser.value,
      settings: {
        notifications: notifications.value,
        privacy: privacy.value,
        app: appSettings.value
      },
      export_date: new Date().toISOString()
    }
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `mood_diary_export_${new Date().toISOString().split('T')[0]}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    window.showNotification('Данные экспортированы', 'success')
  } catch (error) {
    console.error('Error exporting data:', error)
    window.showNotification('Ошибка экспорта данных', 'error')
  } finally {
    exporting.value = false
  }
}

const deleteAccount = async () => {
  deleting.value = true
  try {
    // Implementation for account deletion
    await new Promise(resolve => setTimeout(resolve, 2000)) // Mock delay
    
    window.showNotification('Аккаунт удален', 'success')
    router.push('/login')
  } catch (error) {
    console.error('Error deleting account:', error)
    window.showNotification('Ошибка удаления аккаунта', 'error')
  } finally {
    deleting.value = false
    confirmDelete.value = false
  }
}

const checkUpdates = async () => {
  checkingUpdates.value = true
  try {
    await new Promise(resolve => setTimeout(resolve, 1500)) // Mock delay
    window.showNotification('У вас установлена последняя версия', 'info')
  } catch (error) {
    window.showNotification('Ошибка проверки обновлений', 'error')
  } finally {
    checkingUpdates.value = false
  }
}

const openHelp = () => {
  window.open('/help', '_blank')
}

const openFAQ = () => {
  window.open('/faq', '_blank')
}

const contactSupport = () => {
  window.open('mailto:support@mooddiary.app', '_blank')
}

const reportBug = () => {
  window.open('https://github.com/mooddiary/issues', '_blank')
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

const loadSettings = () => {
  // Load settings from localStorage
  try {
    const savedNotifications = localStorage.getItem('moodDiary_notifications')
    if (savedNotifications) {
      notifications.value = { ...notifications.value, ...JSON.parse(savedNotifications) }
    }
    
    const savedPrivacy = localStorage.getItem('moodDiary_privacy')
    if (savedPrivacy) {
      privacy.value = { ...privacy.value, ...JSON.parse(savedPrivacy) }
    }
    
    const savedAppSettings = localStorage.getItem('moodDiary_appSettings')
    if (savedAppSettings) {
      appSettings.value = { ...appSettings.value, ...JSON.parse(savedAppSettings) }
    }
  } catch (error) {
    console.error('Error loading settings:', error)
  }
}

// Lifecycle
onMounted(() => {
  loadUserData()
  loadSettings()
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-list-item {
  cursor: pointer;
}

.v-time-picker {
  margin: 0 auto;
}
</style>