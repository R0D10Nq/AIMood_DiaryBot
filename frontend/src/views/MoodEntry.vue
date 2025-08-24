<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">
          <v-icon class="me-2">mdi-emoticon-plus</v-icon>
          Добавить запись настроения
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Поделитесь своим настроением и получите AI анализ
        </p>
      </v-col>
    </v-row>

    <!-- Entry Form -->
    <v-row>
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-heart</v-icon>
            Новая запись
          </v-card-title>
          
          <v-card-text>
            <v-form v-model="formValid" @submit.prevent="submitEntry">
              <!-- Date Selection -->
              <v-row>
                <v-col cols="12" md="6">
                  <v-date-input
                    v-model="entryData.entry_date"
                    label="Дата записи"
                    variant="outlined"
                    :max="new Date()"
                    required
                    prepend-inner-icon="mdi-calendar"
                  ></v-date-input>
                </v-col>
              </v-row>

              <!-- Mood Score -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined" class="pa-4">
                    <div class="text-subtitle-1 mb-4">
                      <v-icon class="me-2">mdi-numeric</v-icon>
                      Оценка настроения (1-10)
                    </div>
                    
                    <div class="text-center mb-4">
                      <div class="text-h2 font-weight-bold" :style="{ color: getMoodColor(entryData.mood_score) }">
                        {{ entryData.mood_score }}
                      </div>
                      <div class="text-subtitle-2 text-medium-emphasis">
                        {{ getMoodLabel(entryData.mood_score) }}
                      </div>
                    </div>

                    <v-slider
                      v-model="entryData.mood_score"
                      :min="1"
                      :max="10"
                      :step="1"
                      :color="getMoodColor(entryData.mood_score)"
                      thumb-label
                      class="mood-slider"
                    >
                      <template v-slot:prepend>
                        <v-icon color="error">mdi-emoticon-sad</v-icon>
                      </template>
                      <template v-slot:append>
                        <v-icon color="success">mdi-emoticon-happy</v-icon>
                      </template>
                    </v-slider>

                    <!-- Mood Icons -->
                    <div class="d-flex justify-space-between mt-2">
                      <v-btn
                        v-for="mood in moodIcons"
                        :key="mood.value"
                        :color="entryData.mood_score === mood.value ? mood.color : 'grey-lighten-2'"
                        :variant="entryData.mood_score === mood.value ? 'flat' : 'text'"
                        size="small"
                        icon
                        @click="entryData.mood_score = mood.value"
                      >
                        <v-icon>{{ mood.icon }}</v-icon>
                      </v-btn>
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Note -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-textarea
                    v-model="entryData.note"
                    label="Заметки (необязательно)"
                    placeholder="Опишите ваше настроение, события дня или мысли..."
                    variant="outlined"
                    rows="4"
                    counter="500"
                    prepend-inner-icon="mdi-note-text"
                  ></v-textarea>
                </v-col>
              </v-row>

              <!-- Emotions -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined" class="pa-4">
                    <div class="text-subtitle-1 mb-4">
                      <v-icon class="me-2">mdi-emotion-happy</v-icon>
                      Ваши эмоции (можно выбрать несколько)
                    </div>
                    
                    <div class="d-flex flex-wrap gap-2">
                      <v-chip
                        v-for="emotion in availableEmotions"
                        :key="emotion.name"
                        :color="entryData.emotions.includes(emotion.name) ? emotion.color : 'grey-lighten-2'"
                        :variant="entryData.emotions.includes(emotion.name) ? 'flat' : 'outlined'"
                        :prepend-icon="emotion.icon"
                        clickable
                        @click="toggleEmotion(emotion.name)"
                      >
                        {{ emotion.name }}
                      </v-chip>
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Activities -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined" class="pa-4">
                    <div class="text-subtitle-1 mb-4">
                      <v-icon class="me-2">mdi-run</v-icon>
                      Активности дня
                    </div>
                    
                    <div class="d-flex flex-wrap gap-2">
                      <v-chip
                        v-for="activity in availableActivities"
                        :key="activity.name"
                        :color="entryData.activities.includes(activity.name) ? 'primary' : 'grey-lighten-2'"
                        :variant="entryData.activities.includes(activity.name) ? 'flat' : 'outlined'"
                        :prepend-icon="activity.icon"
                        clickable
                        @click="toggleActivity(activity.name)"
                      >
                        {{ activity.name }}
                      </v-chip>
                    </div>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Energy Level -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined" class="pa-4">
                    <div class="text-subtitle-1 mb-4">
                      <v-icon class="me-2">mdi-battery</v-icon>
                      Уровень энергии
                    </div>
                    
                    <v-slider
                      v-model="entryData.energy_level"
                      :min="1"
                      :max="10"
                      :step="1"
                      color="orange"
                      thumb-label
                      tick-size="4"
                    >
                      <template v-slot:prepend>
                        <v-icon color="grey">mdi-battery-outline</v-icon>
                      </template>
                      <template v-slot:append>
                        <v-icon color="orange">mdi-battery</v-icon>
                      </template>
                    </v-slider>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Stress Level -->
              <v-row class="mt-4">
                <v-col cols="12">
                  <v-card variant="outlined" class="pa-4">
                    <div class="text-subtitle-1 mb-4">
                      <v-icon class="me-2">mdi-brain</v-icon>
                      Уровень стресса
                    </div>
                    
                    <v-slider
                      v-model="entryData.stress_level"
                      :min="1"
                      :max="10"
                      :step="1"
                      color="red"
                      thumb-label
                      tick-size="4"
                    >
                      <template v-slot:prepend>
                        <v-icon color="green">mdi-meditation</v-icon>
                      </template>
                      <template v-slot:append>
                        <v-icon color="red">mdi-lightning-bolt</v-icon>
                      </template>
                    </v-slider>
                  </v-card>
                </v-col>
              </v-row>

              <!-- Submit Button -->
              <v-row class="mt-6">
                <v-col cols="12">
                  <div class="d-flex gap-3">
                    <v-btn
                      type="submit"
                      color="primary"
                      size="large"
                      :loading="submitting"
                      :disabled="!formValid"
                      prepend-icon="mdi-content-save"
                    >
                      Сохранить запись
                    </v-btn>
                    
                    <v-btn
                      color="grey"
                      variant="outlined"
                      size="large"
                      @click="resetForm"
                      :disabled="submitting"
                    >
                      Очистить
                    </v-btn>
                  </div>
                </v-col>
              </v-row>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Quick Tips -->
      <v-col cols="12" lg="4">
        <v-card class="mb-4">
          <v-card-title>
            <v-icon class="me-2">mdi-lightbulb</v-icon>
            Советы
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item prepend-icon="mdi-clock-outline">
                <v-list-item-title>Ведите записи регулярно</v-list-item-title>
                <v-list-item-subtitle>Лучше всего в одно и то же время</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item prepend-icon="mdi-heart">
                <v-list-item-title>Будьте честны с собой</v-list-item-title>
                <v-list-item-subtitle>Искренность поможет лучше понять себя</v-list-item-subtitle>
              </v-list-item>
              
              <v-list-item prepend-icon="mdi-note-text">
                <v-list-item-title>Добавляйте детали</v-list-item-title>
                <v-list-item-subtitle>Заметки помогут в анализе</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>

        <!-- Recent Entries -->
        <v-card v-if="recentEntries.length > 0">
          <v-card-title>
            <v-icon class="me-2">mdi-history</v-icon>
            Последние записи
          </v-card-title>
          <v-card-text>
            <v-list density="compact">
              <v-list-item
                v-for="entry in recentEntries.slice(0, 5)"
                :key="entry.id"
                @click="loadEntryAsTemplate(entry)"
                class="cursor-pointer"
              >
                <template v-slot:prepend>
                  <v-chip 
                    :color="getMoodColor(entry.mood_score)" 
                    size="small"
                    variant="flat"
                  >
                    {{ entry.mood_score }}
                  </v-chip>
                </template>
                
                <v-list-item-title>
                  {{ formatDate(entry.entry_date) }}
                </v-list-item-title>
                <v-list-item-subtitle>
                  {{ entry.note ? entry.note.substring(0, 50) + '...' : 'Без заметок' }}
                </v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Success Dialog -->
    <v-dialog v-model="successDialog" max-width="400">
      <v-card>
        <v-card-title class="text-center">
          <v-icon color="success" size="48" class="mb-2">mdi-check-circle</v-icon>
          <div>Запись сохранена!</div>
        </v-card-title>
        <v-card-text class="text-center">
          <p>Ваша запись настроения успешно добавлена.</p>
          <p v-if="aiAnalysisResult" class="mt-2">
            <strong>AI Анализ:</strong> {{ aiAnalysisResult }}
          </p>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" @click="successDialog = false">Понятно</v-btn>
          <v-btn color="grey" variant="outlined" @click="goToDashboard">К дашборду</v-btn>
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

const { currentUser, recentEntries } = storeToRefs(moodStore)

// Form data
const formValid = ref(false)
const submitting = ref(false)
const successDialog = ref(false)
const aiAnalysisResult = ref('')

const entryData = ref({
  entry_date: new Date(),
  mood_score: 5,
  note: '',
  emotions: [],
  activities: [],
  energy_level: 5,
  stress_level: 5
})

// Available options
const availableEmotions = [
  { name: 'радость', icon: 'mdi-emoticon-happy', color: 'success' },
  { name: 'грусть', icon: 'mdi-emoticon-sad', color: 'blue' },
  { name: 'тревога', icon: 'mdi-emoticon-confused', color: 'warning' },
  { name: 'спокойствие', icon: 'mdi-emoticon-neutral', color: 'teal' },
  { name: 'злость', icon: 'mdi-emoticon-angry', color: 'error' },
  { name: 'удивление', icon: 'mdi-emoticon-excited', color: 'purple' },
  { name: 'страх', icon: 'mdi-emoticon-frown', color: 'deep-orange' },
  { name: 'отвращение', icon: 'mdi-emoticon-sick', color: 'brown' },
  { name: 'надежда', icon: 'mdi-emoticon-cool', color: 'light-blue' },
  { name: 'благодарность', icon: 'mdi-heart', color: 'pink' }
]

const availableActivities = [
  { name: 'работа', icon: 'mdi-briefcase' },
  { name: 'спорт', icon: 'mdi-run' },
  { name: 'чтение', icon: 'mdi-book-open' },
  { name: 'музыка', icon: 'mdi-music' },
  { name: 'готовка', icon: 'mdi-chef-hat' },
  { name: 'прогулка', icon: 'mdi-walk' },
  { name: 'медитация', icon: 'mdi-meditation' },
  { name: 'общение', icon: 'mdi-account-group' },
  { name: 'игры', icon: 'mdi-gamepad-variant' },
  { name: 'творчество', icon: 'mdi-palette' },
  { name: 'учеба', icon: 'mdi-school' },
  { name: 'отдых', icon: 'mdi-sleep' }
]

const moodIcons = [
  { value: 1, icon: 'mdi-emoticon-dead', color: 'error' },
  { value: 2, icon: 'mdi-emoticon-cry', color: 'deep-orange' },
  { value: 3, icon: 'mdi-emoticon-sad', color: 'orange' },
  { value: 4, icon: 'mdi-emoticon-frown', color: 'amber' },
  { value: 5, icon: 'mdi-emoticon-neutral', color: 'yellow' },
  { value: 6, icon: 'mdi-emoticon', color: 'lime' },
  { value: 7, icon: 'mdi-emoticon-happy', color: 'light-green' },
  { value: 8, icon: 'mdi-emoticon-excited', color: 'green' },
  { value: 9, icon: 'mdi-emoticon-cool', color: 'teal' },
  { value: 10, icon: 'mdi-emoticon-kiss', color: 'success' }
]

// Computed properties
const getMoodColor = (score) => {
  if (score >= 8) return '#4CAF50'
  if (score >= 6) return '#8BC34A'
  if (score >= 4) return '#FFC107'
  if (score >= 2) return '#FF9800'
  return '#F44336'
}

const getMoodLabel = (score) => {
  if (score >= 9) return 'Отличное'
  if (score >= 7) return 'Хорошее'
  if (score >= 5) return 'Нормальное'
  if (score >= 3) return 'Плохое'
  return 'Ужасное'
}

// Methods
const toggleEmotion = (emotion) => {
  const index = entryData.value.emotions.indexOf(emotion)
  if (index > -1) {
    entryData.value.emotions.splice(index, 1)
  } else {
    entryData.value.emotions.push(emotion)
  }
}

const toggleActivity = (activity) => {
  const index = entryData.value.activities.indexOf(activity)
  if (index > -1) {
    entryData.value.activities.splice(index, 1)
  } else {
    entryData.value.activities.push(activity)
  }
}

const submitEntry = async () => {
  if (!formValid.value || !currentUser.value?.id) return

  submitting.value = true
  try {
    // Prepare entry data
    const entryPayload = {
      ...entryData.value,
      user_id: currentUser.value.id,
      entry_date: entryData.value.entry_date.toISOString()
    }

    // Submit via store
    const result = await moodStore.createMoodEntry(entryPayload)
    
    if (result.success) {
      aiAnalysisResult.value = result.ai_analysis || 'Анализ будет доступен позже'
      successDialog.value = true
      resetForm()
      
      // Refresh recent entries
      await moodStore.fetchRecentEntries(currentUser.value.id)
    } else {
      throw new Error(result.error || 'Ошибка сохранения')
    }
  } catch (error) {
    console.error('Error submitting entry:', error)
    window.showNotification('Ошибка при сохранении записи', 'error')
  } finally {
    submitting.value = false
  }
}

const resetForm = () => {
  entryData.value = {
    entry_date: new Date(),
    mood_score: 5,
    note: '',
    emotions: [],
    activities: [],
    energy_level: 5,
    stress_level: 5
  }
}

const loadEntryAsTemplate = (entry) => {
  entryData.value = {
    entry_date: new Date(),
    mood_score: entry.mood_score,
    note: '',
    emotions: entry.emotions || [],
    activities: entry.activities || [],
    energy_level: entry.energy_level || 5,
    stress_level: entry.stress_level || 5
  }
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    year: 'numeric'
  })
}

const goToDashboard = () => {
  successDialog.value = false
  router.push('/')
}

// Lifecycle
onMounted(async () => {
  if (currentUser.value?.id) {
    await moodStore.fetchRecentEntries(currentUser.value.id, 10)
  }
})
</script>

<style scoped>
.mood-slider {
  margin: 16px 0;
}

.cursor-pointer {
  cursor: pointer;
}

.v-card {
  border-radius: 12px;
}

.v-chip {
  margin: 2px;
}

.gap-2 {
  gap: 8px;
}

.gap-3 {
  gap: 12px;
}
</style>