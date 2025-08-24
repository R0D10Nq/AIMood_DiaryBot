<template>
  <div>
    <!-- Header -->
    <v-row class="mb-6">
      <v-col cols="12">
        <h1 class="text-h4 font-weight-bold">
          <v-icon class="me-2">mdi-chart-line</v-icon>
          Аналитика настроения
        </h1>
        <p class="text-subtitle-1 text-medium-emphasis">
          Подробный анализ эмоциональных паттернов и трендов
        </p>
      </v-col>
    </v-row>

    <!-- Period Selector -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card variant="outlined">
          <v-card-text class="d-flex align-center">
            <v-icon class="me-2">mdi-calendar-range</v-icon>
            <span class="text-subtitle-1 me-4">Период анализа:</span>
            
            <v-btn-toggle
              v-model="selectedPeriod"
              @update:model-value="onPeriodChange"
              mandatory
              variant="outlined"
            >
              <v-btn value="week">
                <v-icon class="me-1">mdi-calendar-week</v-icon>
                Неделя
              </v-btn>
              <v-btn value="month">
                <v-icon class="me-1">mdi-calendar-month</v-icon>
                Месяц
              </v-btn>
              <v-btn value="quarter">
                <v-icon class="me-1">mdi-calendar-multiple</v-icon>
                Квартал
              </v-btn>
              <v-btn value="year">
                <v-icon class="me-1">mdi-calendar</v-icon>
                Год
              </v-btn>
            </v-btn-toggle>

            <v-spacer></v-spacer>

            <v-btn
              color="primary"
              prepend-icon="mdi-refresh"
              @click="refreshData"
              :loading="loading"
            >
              Обновить
            </v-btn>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Summary Statistics -->
    <v-row class="mb-6">
      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-progress-circular
              :model-value="(averageMood / 10) * 100"
              :size="80"
              :width="8"
              color="primary"
              class="mb-2"
            >
              <span class="text-h6">{{ averageMood }}</span>
            </v-progress-circular>
            <div class="text-h6 font-weight-bold">Среднее настроение</div>
            <div class="text-caption text-medium-emphasis">за выбранный период</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" :color="variabilityColor" class="mb-2">
              mdi-pulse
            </v-icon>
            <div class="text-h6 font-weight-bold">{{ moodVariability }}</div>
            <div class="text-caption text-medium-emphasis">Стабильность</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" color="info" class="mb-2">mdi-calendar-check</v-icon>
            <div class="text-h6 font-weight-bold">{{ totalDays }}</div>
            <div class="text-caption text-medium-emphasis">Дней с записями</div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" sm="6" md="3">
        <v-card class="text-center">
          <v-card-text>
            <v-icon size="48" color="success" class="mb-2">mdi-emoticon-happy</v-icon>
            <div class="text-h6 font-weight-bold">{{ dominantEmotion }}</div>
            <div class="text-caption text-medium-emphasis">Доминирующая эмоция</div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Main Charts -->
    <v-row class="mb-6">
      <!-- Detailed Mood Trends -->
      <v-col cols="12" lg="8">
        <v-card>
          <v-card-title>
            Детальные тренды настроения
            <v-spacer></v-spacer>
            <v-menu>
              <template v-slot:activator="{ props }">
                <v-btn
                  icon="mdi-dots-vertical"
                  v-bind="props"
                  variant="text"
                ></v-btn>
              </template>
              <v-list>
                <v-list-item @click="exportChart('mood-trends')">
                  <v-list-item-title>Экспорт графика</v-list-item-title>
                </v-list-item>
                <v-list-item @click="shareChart('mood-trends')">
                  <v-list-item-title>Поделиться</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </v-card-title>
          <v-card-text>
            <div v-if="chartData" style="height: 400px;">
              <Line
                :data="enhancedChartData"
                :options="enhancedChartOptions"
                style="max-height: 400px;"
              />
            </div>
            <div v-else class="text-center py-12">
              <v-icon size="64" color="grey-lighten-2">mdi-chart-line-variant</v-icon>
              <p class="text-h6 text-medium-emphasis mt-4">Нет данных для анализа</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Mood Distribution -->
      <v-col cols="12" lg="4">
        <v-card>
          <v-card-title>Распределение оценок</v-card-title>
          <v-card-text>
            <div v-if="moodScoreDistribution" style="height: 400px;">
              <Bar
                :data="moodScoreDistribution"
                :options="barChartOptions"
                style="max-height: 400px;"
              />
            </div>
            <div v-else class="text-center py-12">
              <v-icon size="64" color="grey-lighten-2">mdi-chart-bar</v-icon>
              <p class="text-caption mt-2">Нет данных</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Emotions Analysis -->
    <v-row class="mb-6" v-if="emotionTrendsData">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-emotion-happy</v-icon>
            Анализ эмоций
          </v-card-title>
          <v-card-text>
            <v-tabs v-model="emotionTab">
              <v-tab value="trends">Тренды эмоций</v-tab>
              <v-tab value="correlation">Корреляция</v-tab>
              <v-tab value="patterns">Паттерны</v-tab>
            </v-tabs>

            <v-tabs-window v-model="emotionTab">
              <v-tabs-window-item value="trends">
                <div style="height: 300px;" class="mt-4">
                  <Line
                    :data="emotionTrendsData"
                    :options="emotionChartOptions"
                    style="max-height: 300px;"
                  />
                </div>
              </v-tabs-window-item>

              <v-tabs-window-item value="correlation">
                <div class="mt-4">
                  <EmotionCorrelationMatrix :data="emotionCorrelationData" />
                </div>
              </v-tabs-window-item>

              <v-tabs-window-item value="patterns">
                <div class="mt-4">
                  <EmotionPatterns :data="emotionPatternsData" />
                </div>
              </v-tabs-window-item>
            </v-tabs-window>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Time Analysis -->
    <v-row class="mb-6">
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Анализ по времени</v-card-title>
          <v-card-text>
            <div v-if="timeAnalysisData" style="height: 300px;">
              <Radar
                :data="timeAnalysisData"
                :options="radarOptions"
                style="max-height: 300px;"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Еженедельные паттерны</v-card-title>
          <v-card-text>
            <div v-if="weeklyPatternData" style="height: 300px;">
              <Bar
                :data="weeklyPatternData"
                :options="weeklyBarOptions"
                style="max-height: 300px;"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- AI Insights Section -->
    <v-row class="mb-6">
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-robot</v-icon>
            ИИ Инсайты
            <v-spacer></v-spacer>
            <v-btn
              color="primary"
              prepend-icon="mdi-auto-fix"
              @click="generateInsights"
              :loading="insightsLoading"
              variant="outlined"
            >
              Генерировать инсайты
            </v-btn>
          </v-card-title>
          <v-card-text>
            <div v-if="insights">
              <v-alert
                type="info"
                variant="tonal"
                class="mb-4"
              >
                <div class="text-h6 mb-2">📊 Анализ за {{ insights.period_days }} дней</div>
                <p>{{ insights.ai_insights }}</p>
              </v-alert>

              <v-row>
                <v-col cols="12" md="6">
                  <h4 class="text-subtitle-1 mb-2">Ключевые моменты:</h4>
                  <v-list density="compact">
                    <v-list-item
                      v-for="(insight, index) in parsedInsights"
                      :key="index"
                      :prepend-icon="insight.icon"
                    >
                      <v-list-item-title>{{ insight.text }}</v-list-item-title>
                    </v-list-item>
                  </v-list>
                </v-col>

                <v-col cols="12" md="6">
                  <h4 class="text-subtitle-1 mb-2">Статистика анализа:</h4>
                  <v-table density="compact">
                    <tbody>
                      <tr>
                        <td>Записей проанализировано:</td>
                        <td class="font-weight-bold">{{ insights.entries_analyzed }}</td>
                      </tr>
                      <tr>
                        <td>Средняя оценка:</td>
                        <td class="font-weight-bold">{{ insights.summary?.average_mood || 'N/A' }}</td>
                      </tr>
                      <tr>
                        <td>Тренд:</td>
                        <td class="font-weight-bold">{{ insights.summary?.mood_trend || 'N/A' }}</td>
                      </tr>
                    </tbody>
                  </v-table>
                </v-col>
              </v-row>
            </div>
            <div v-else class="text-center py-8">
              <v-icon size="64" color="grey-lighten-2">mdi-robot-outline</v-icon>
              <p class="text-h6 text-medium-emphasis mt-4">Нет инсайтов</p>
              <p class="text-caption">Нажмите "Генерировать инсайты" для получения анализа от ИИ</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Comparison Section -->
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-compare</v-icon>
            Сравнение периодов
          </v-card-title>
          <v-card-text>
            <PeriodComparison :userId="currentUser?.id" />
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useMoodStore } from '../stores/mood'
import { storeToRefs } from 'pinia'
import { Line, Bar, Doughnut, Radar } from 'vue-chartjs'
import EmotionCorrelationMatrix from '../components/EmotionCorrelationMatrix.vue'
import EmotionPatterns from '../components/EmotionPatterns.vue'
import PeriodComparison from '../components/PeriodComparison.vue'

const moodStore = useMoodStore()

const { 
  currentUser, 
  moodTrends,
  insights,
  averageMood,
  chartData,
  emotionTrendsData,
  loading
} = storeToRefs(moodStore)

const selectedPeriod = ref('month')
const emotionTab = ref('trends')
const insightsLoading = ref(false)

// Computed properties for analytics
const moodVariability = computed(() => {
  if (!moodTrends.value?.mood_trend) return 'N/A'
  
  const scores = moodTrends.value.mood_trend.map(item => item.average_mood)
  if (scores.length < 2) return 'N/A'
  
  const variance = scores.reduce((acc, score, index, arr) => {
    const mean = arr.reduce((sum, s) => sum + s, 0) / arr.length
    return acc + Math.pow(score - mean, 2)
  }, 0) / scores.length
  
  const stdDev = Math.sqrt(variance)
  
  if (stdDev < 1) return 'Высокая'
  if (stdDev < 2) return 'Средняя'
  return 'Низкая'
})

const variabilityColor = computed(() => {
  switch (moodVariability.value) {
    case 'Высокая': return 'success'
    case 'Средняя': return 'warning'
    case 'Низкая': return 'error'
    default: return 'grey'
  }
})

const totalDays = computed(() => {
  return moodTrends.value?.mood_trend?.length || 0
})

const dominantEmotion = computed(() => {
  if (!emotionTrendsData.value?.datasets) return 'N/A'
  
  // Calculate average emotion values
  const emotionAverages = {}
  emotionTrendsData.value.datasets.forEach(dataset => {
    const average = dataset.data.reduce((sum, val) => sum + val, 0) / dataset.data.length
    emotionAverages[dataset.label] = average
  })
  
  // Find emotion with highest average
  const dominant = Object.entries(emotionAverages).reduce((max, [emotion, avg]) => 
    avg > max.avg ? { emotion, avg } : max, { emotion: 'N/A', avg: 0 })
  
  return dominant.emotion
})

const enhancedChartData = computed(() => {
  if (!chartData.value) return null
  
  return {
    ...chartData.value,
    datasets: [
      {
        ...chartData.value.datasets[0],
        fill: true,
        pointBackgroundColor: '#1976D2',
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 6,
        pointHoverRadius: 8
      }
    ]
  }
})

const moodScoreDistribution = computed(() => {
  if (!moodTrends.value?.mood_trend) return null
  
  const scores = moodTrends.value.mood_trend.map(item => item.average_mood)
  const distribution = Array(10).fill(0)
  
  scores.forEach(score => {
    const index = Math.floor(score) - 1
    if (index >= 0 && index < 10) distribution[index]++
  })
  
  return {
    labels: ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10'],
    datasets: [{
      label: 'Количество дней',
      data: distribution,
      backgroundColor: distribution.map((_, index) => {
        const score = index + 1
        if (score >= 7) return '#4CAF50'
        if (score >= 4) return '#FF9800'
        return '#F44336'
      }),
      borderWidth: 1
    }]
  }
})

const timeAnalysisData = computed(() => {
  // Mock data for time analysis (would be calculated from actual data)
  return {
    labels: ['Утро', 'День', 'Вечер', 'Ночь'],
    datasets: [{
      label: 'Среднее настроение',
      data: [7.2, 6.8, 7.5, 6.5],
      borderColor: '#1976D2',
      backgroundColor: 'rgba(25, 118, 210, 0.2)',
      pointBackgroundColor: '#1976D2'
    }]
  }
})

const weeklyPatternData = computed(() => {
  // Mock weekly pattern data
  return {
    labels: ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс'],
    datasets: [{
      label: 'Среднее настроение',
      data: [6.5, 7.0, 6.8, 7.2, 7.5, 8.0, 7.8],
      backgroundColor: [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
        '#FECA57', '#FF9FF3', '#54A0FF'
      ],
      borderWidth: 1
    }]
  }
})

const emotionCorrelationData = computed(() => {
  // Mock correlation data
  return {
    emotions: ['радость', 'грусть', 'тревога', 'спокойствие'],
    correlations: [
      [1.0, -0.7, -0.5, 0.6],
      [-0.7, 1.0, 0.4, -0.8],
      [-0.5, 0.4, 1.0, -0.6],
      [0.6, -0.8, -0.6, 1.0]
    ]
  }
})

const emotionPatternsData = computed(() => {
  // Mock patterns data
  return [
    { pattern: 'Утренняя тревожность', frequency: 65, description: 'Повышенная тревога в утренние часы' },
    { pattern: 'Вечернее спокойствие', frequency: 78, description: 'Улучшение настроения к вечеру' },
    { pattern: 'Выходные радость', frequency: 82, description: 'Повышенное настроение в выходные' }
  ]
})

const parsedInsights = computed(() => {
  if (!insights.value?.ai_insights) return []
  
  // Simple parsing of insights text
  const text = insights.value.ai_insights
  const sentences = text.split('.').filter(s => s.trim().length > 0)
  
  return sentences.slice(0, 5).map(sentence => ({
    text: sentence.trim(),
    icon: getInsightIcon(sentence)
  }))
})

// Chart options
const enhancedChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    },
    tooltip: {
      mode: 'index',
      intersect: false,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      titleColor: '#fff',
      bodyColor: '#fff',
      borderColor: '#1976D2',
      borderWidth: 1
    }
  },
  scales: {
    x: {
      grid: {
        display: false
      }
    },
    y: {
      min: 1,
      max: 10,
      grid: {
        color: 'rgba(0, 0, 0, 0.1)'
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

const barChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true
    }
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
      max: 1,
      title: {
        display: true,
        text: 'Интенсивность эмоции'
      }
    }
  }
}

const radarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    r: {
      beginAtZero: true,
      max: 10
    }
  }
}

const weeklyBarOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false
    }
  },
  scales: {
    y: {
      beginAtZero: true,
      max: 10
    }
  }
}

// Methods
const onPeriodChange = async (period) => {
  if (currentUser.value?.id) {
    await moodStore.fetchMoodTrends(currentUser.value.id, period)
  }
}

const refreshData = async () => {
  if (currentUser.value?.id) {
    await moodStore.fetchDashboardData(currentUser.value.id)
    await moodStore.fetchMoodTrends(currentUser.value.id, selectedPeriod.value)
  }
}

const generateInsights = async () => {
  if (!currentUser.value?.id) return
  
  insightsLoading.value = true
  try {
    await moodStore.fetchInsights(currentUser.value.id, 30)
  } finally {
    insightsLoading.value = false
  }
}

const getInsightIcon = (sentence) => {
  if (sentence.includes('улучш') || sentence.includes('позитив')) return 'mdi-trending-up'
  if (sentence.includes('ухудш') || sentence.includes('негатив')) return 'mdi-trending-down'
  if (sentence.includes('стабиль')) return 'mdi-trending-neutral'
  if (sentence.includes('рекоменд')) return 'mdi-lightbulb'
  return 'mdi-information'
}

const exportChart = (chartType) => {
  // Implementation for chart export
  console.log('Exporting chart:', chartType)
  window.showNotification('Функция экспорта в разработке', 'info')
}

const shareChart = (chartType) => {
  // Implementation for chart sharing
  console.log('Sharing chart:', chartType)
  window.showNotification('Функция "Поделиться" в разработке', 'info')
}

// Lifecycle
onMounted(async () => {
  if (currentUser.value?.id) {
    await refreshData()
  }
})

watch(currentUser, async (newUser) => {
  if (newUser?.id) {
    await refreshData()
  }
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-btn-toggle {
  border-radius: 8px;
}

.v-progress-circular {
  font-weight: bold;
}
</style>