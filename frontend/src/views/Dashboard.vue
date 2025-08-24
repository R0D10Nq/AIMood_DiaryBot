<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">
          <v-icon class="me-2">mdi-view-dashboard</v-icon>
          Дашборд настроения
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Добро пожаловать! Отслеживайте свое эмоциональное состояние с помощью ИИ
        </p>
      </v-col>
    </v-row>

    <!-- Quick Stats Cards -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" color="primary" class="mb-2">mdi-heart</v-icon>
            <div class="text-h4 font-weight-bold">{{ averageMood || '0' }}</div>
            <div class="text-caption text-medium-emphasis">Среднее настроение</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon 
              size="48" 
              :color="trendColor" 
              class="mb-2"
            >{{ trendIcon }}</v-icon>
            <div class="text-h6 font-weight-bold">{{ moodTrendText }}</div>
            <div class="text-caption text-medium-emphasis">Тренд настроения</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" color="success" class="mb-2">mdi-fire</v-icon>
            <div class="text-h4 font-weight-bold">{{ currentStreak }}</div>
            <div class="text-caption text-medium-emphasis">Дней подряд</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" color="info" class="mb-2">mdi-chart-line</v-icon>
            <div class="text-h4 font-weight-bold">{{ totalEntries }}</div>
            <div class="text-caption text-medium-emphasis">Всего записей</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Charts Row -->
    <v-row class="mb-6">
      <!-- Mood Trends Chart -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-chart-line</v-icon>
            Тренды настроения
            
            <v-spacer></v-spacer>
            
            <v-btn-toggle
              v-model="selectedPeriod"
              @update:model-value="onPeriodChange"
              mandatory
              density="compact"
              variant="outlined"
            >
              <v-btn value="week" size="small">Неделя</v-btn>
              <v-btn value="month" size="small">Месяц</v-btn>
              <v-btn value="quarter" size="small">Квартал</v-btn>
            </v-btn-toggle>
          </v-card-title>
          <v-card-text>
            <div v-if="chartData" style="height: 300px;">
              <Line
                :data="chartData"
                :options="chartOptions"
                style="max-height: 300px;"
              />
            </div>
            <div v-else class="text-center py-12">
              <v-icon size="64" color="grey-lighten-2">mdi-chart-line-variant</v-icon>
              <p class="text-h6 text-medium-emphasis mt-4">Недостаточно данных для отображения</p>
              <p class="text-caption">Начните вести дневник для просмотра графиков</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Mood Distribution -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-chart-donut</v-icon>
            Распределение настроения
          </v-card-title>
          <v-card-text>
            <div v-if="moodDistributionData" style="height: 300px;">
              <Doughnut
                :data="moodDistributionData"
                :options="doughnutOptions"
                style="max-height: 300px;"
              />
            </div>
            <div v-else class="text-center py-12">
              <v-icon size="64" color="grey-lighten-2">mdi-chart-donut</v-icon>
              <p class="text-caption mt-2">Нет данных</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Recent Entries and Recommendations -->
    <v-row class="mb-6">
      <!-- Recent Mood Entries -->
      <v-col cols="12" lg="7">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-history</v-icon>
            Последние записи
            
            <v-spacer></v-spacer>
            
            <v-btn
              color="primary"
              prepend-icon="mdi-plus"
              to="/mood-entry"
              size="small"
            >
              Добавить
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="recentEntries && recentEntries.length > 0">
              <v-timeline density="compact">
                <v-timeline-item
                  v-for="entry in recentEntries.slice(0, 5)"
                  :key="entry.id"
                  :dot-color="getMoodColor(entry.mood_score)"
                  size="small"
                >
                  <template v-slot:opposite>
                    <span class="text-caption">
                      {{ formatDate(entry.entry_date) }}
                    </span>
                  </template>
                  
                  <v-card variant="outlined" class="mb-2">
                    <v-card-text class="py-2">
                      <div class="d-flex align-center mb-2">
                        <v-chip
                          :color="getMoodColor(entry.mood_score)"
                          size="small"
                          class="me-2"
                        >
                          {{ entry.mood_score }}/10
                        </v-chip>
                        <span class="text-caption text-medium-emphasis">
                          {{ getMoodEmoji(entry.mood_score) }} {{ getMoodText(entry.mood_score) }}
                        </span>
                      </div>
                      <p class="text-body-2 mb-2">{{ entry.mood_text.substring(0, 100) }}...</p>
                      
                      <div v-if="entry.ai_analysis" class="mt-2">
                        <v-chip
                          v-if="entry.ai_analysis.dominant_emotion"
                          size="x-small"
                          variant="outlined"
                          class="me-1"
                        >
                          {{ entry.ai_analysis.dominant_emotion }}
                        </v-chip>
                        <v-chip
                          v-if="entry.ai_analysis.sentiment_label"
                          size="x-small"
                          variant="outlined"
                          :color="getSentimentColor(entry.ai_analysis.sentiment_label)"
                        >
                          {{ getSentimentText(entry.ai_analysis.sentiment_label) }}
                        </v-chip>
                      </div>
                    </v-card-text>
                  </v-card>
                </v-timeline-item>
              </v-timeline>
            </div>
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">mdi-emoticon-outline</v-icon>
              <p class="text-h6 text-medium-emphasis mt-4">Нет записей</p>
              <p class="text-caption">Создайте первую запись настроения</p>
              <v-btn
                color="primary"
                prepend-icon="mdi-plus"
                to="/mood-entry"
                class="mt-4"
              >
                Добавить запись
              </v-btn>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- AI Recommendations -->
      <v-col cols="12" lg="5">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-lightbulb</v-icon>
            Рекомендации ИИ
          </v-card-title>
          <v-card-text>
            <div v-if="recommendations">
              <div v-if="recommendations.ai_recommendations && recommendations.ai_recommendations.length > 0">
                <v-alert
                  v-for="(rec, index) in recommendations.ai_recommendations.slice(0, 3)"
                  :key="index"
                  type="info"
                  variant="tonal"
                  class="mb-3"
                >
                  <v-icon slot="prepend">mdi-robot</v-icon>
                  {{ rec }}
                </v-alert>
              </div>

              <div v-if="recommendations.general_recommendations && recommendations.general_recommendations.length > 0">
                <h4 class="text-subtitle-1 mb-2">Общие рекомендации:</h4>
                <v-list density="compact">
                  <v-list-item
                    v-for="(rec, index) in recommendations.general_recommendations"
                    :key="index"
                    :prepend-icon="getRecommendationIcon(rec)"
                  >
                    <v-list-item-title class="text-body-2">{{ rec }}</v-list-item-title>
                  </v-list-item>
                </v-list>
              </div>
            </div>
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">mdi-lightbulb-outline</v-icon>
              <p class="text-caption mt-2">Рекомендации появятся после анализа записей</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Emotion Trends Chart -->
    <v-row v-if="emotionTrendsData">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-emotion-happy</v-icon>
            Тренды эмоций
          </v-card-title>
          <v-card-text>
            <div style="height: 300px;">
              <Line
                :data="emotionTrendsData"
                :options="emotionChartOptions"
                style="max-height: 300px;"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Quick Actions FAB -->
    <v-fab
      location="bottom end"
      size="large"
      color="primary"
      icon="mdi-plus"
      @click="$router.push('/mood-entry')"
    ></v-fab>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useMoodStore } from '../stores/mood'
import { storeToRefs } from 'pinia'
import { Line, Doughnut } from 'vue-chartjs'

const router = useRouter()
const moodStore = useMoodStore()

const { 
  currentUser, 
  dashboardData, 
  recentEntries, 
  moodStats,
  moodTrends,
  recommendations,
  averageMood,
  currentStreak,
  moodTrend,
  chartData,
  emotionTrendsData
} = storeToRefs(moodStore)

const selectedPeriod = ref('month')

// Computed properties
const trendColor = computed(() => {
  switch (moodTrend.value) {
    case 'improving': return 'success'
    case 'declining': return 'error'
    default: return 'info'
  }
})

const trendIcon = computed(() => {
  switch (moodTrend.value) {
    case 'improving': return 'mdi-trending-up'
    case 'declining': return 'mdi-trending-down'
    default: return 'mdi-trending-neutral'
  }
})

const moodTrendText = computed(() => {
  switch (moodTrend.value) {
    case 'improving': return 'Улучшается'
    case 'declining': return 'Ухудшается'
    default: return 'Стабильно'
  }
})

const totalEntries = computed(() => {
  return moodStats.value?.total_entries || 0
})

const moodDistributionData = computed(() => {
  if (!dashboardData.value?.monthly_analytics?.mood_distribution) return null
  
  const distribution = dashboardData.value.monthly_analytics.mood_distribution
  return {
    labels: ['Позитивное', 'Нейтральное', 'Негативное'],
    datasets: [{
      data: [distribution.positive, distribution.neutral, distribution.negative],
      backgroundColor: ['#4CAF50', '#FF9800', '#F44336'],
      borderWidth: 2,
      borderColor: '#fff'
    }]
  }
})

// Chart options
const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    x: {
      display: true,
      title: {
        display: true,
        text: 'Дата'
      }
    },
    y: {
      display: true,
      title: {
        display: true,
        text: 'Настроение (1-10)'
      },
      min: 1,
      max: 10
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

const emotionChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 1
    }
  }
}

const doughnutOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'bottom'
    }
  }
}

// Methods
const getMoodColor = (score) => {
  if (score >= 7) return 'success'
  if (score >= 4) return 'warning'
  return 'error'
}

const getMoodEmoji = (score) => {
  if (score >= 9) return '😄'
  if (score >= 7) return '😊'
  if (score >= 5) return '😐'
  if (score >= 3) return '😔'
  return '😢'
}

const getMoodText = (score) => {
  if (score >= 9) return 'Отлично'
  if (score >= 7) return 'Хорошо'
  if (score >= 5) return 'Нормально'
  if (score >= 3) return 'Плохо'
  return 'Очень плохо'
}

const getSentimentColor = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'success'
    case 'negative': return 'error'
    default: return 'info'
  }
}

const getSentimentText = (sentiment) => {
  switch (sentiment) {
    case 'positive': return 'Позитивное'
    case 'negative': return 'Негативное'
    default: return 'Нейтральное'
  }
}

const getRecommendationIcon = (recommendation) => {
  if (recommendation.includes('физическ')) return 'mdi-run'
  if (recommendation.includes('сон') || recommendation.includes('отдых')) return 'mdi-sleep'
  if (recommendation.includes('общен') || recommendation.includes('друз')) return 'mdi-account-group'
  if (recommendation.includes('медитац') || recommendation.includes('релакс')) return 'mdi-meditation'
  return 'mdi-lightbulb'
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  const date = new Date(dateStr)
  return date.toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const onPeriodChange = async (period) => {
  if (currentUser.value?.id) {
    await moodStore.fetchMoodTrends(currentUser.value.id, period)
  }
}

// Lifecycle
onMounted(async () => {
  if (currentUser.value?.id) {
    await moodStore.fetchDashboardData(currentUser.value.id)
    await moodStore.fetchMoodTrends(currentUser.value.id, selectedPeriod.value)
  }
})

// Watch for user changes
watch(currentUser, async (newUser) => {
  if (newUser?.id) {
    await moodStore.fetchDashboardData(newUser.id)
    await moodStore.fetchMoodTrends(newUser.id, selectedPeriod.value)
  }
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-timeline {
  padding-left: 0;
}

.v-fab {
  z-index: 1000;
}
</style>