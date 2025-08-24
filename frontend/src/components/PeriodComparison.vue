<template>
  <div>
    <!-- Period Selection -->
    <v-row class="mb-4">
      <v-col cols="12" md="6">
        <v-card variant="outlined">
          <v-card-title class="text-subtitle-1">
            <v-icon class="me-2">mdi-calendar-clock</v-icon>
            Первый период
          </v-card-title>
          <v-card-text>
            <v-select
              v-model="firstPeriod"
              :items="periodOptions"
              label="Выберите период"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              @update:model-value="onPeriodChange"
            ></v-select>
            
            <v-date-input
              v-if="firstPeriod === 'custom'"
              v-model="firstCustomDate"
              label="Дата начала"
              variant="outlined"
              density="compact"
              class="mt-2"
              @update:model-value="onPeriodChange"
            ></v-date-input>
          </v-card-text>
        </v-card>
      </v-col>

      <v-col cols="12" md="6">
        <v-card variant="outlined">
          <v-card-title class="text-subtitle-1">
            <v-icon class="me-2">mdi-calendar-check</v-icon>
            Второй период
          </v-card-title>
          <v-card-text>
            <v-select
              v-model="secondPeriod"
              :items="periodOptions"
              label="Выберите период"
              item-title="text"
              item-value="value"
              variant="outlined"
              density="compact"
              @update:model-value="onPeriodChange"
            ></v-select>
            
            <v-date-input
              v-if="secondPeriod === 'custom'"
              v-model="secondCustomDate"
              label="Дата начала"
              variant="outlined"
              density="compact"
              class="mt-2"
              @update:model-value="onPeriodChange"
            ></v-date-input>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Comparison Results -->
    <v-row v-if="comparisonData">
      <!-- Summary Comparison -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-chart-line-variant</v-icon>
            Сравнение ключевых показателей
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col cols="12" sm="6" md="3">
                <div class="text-center">
                  <v-icon 
                    :color="getMoodChangeColor(comparisonData.averageMoodChange)"
                    :icon="getMoodChangeIcon(comparisonData.averageMoodChange)"
                    size="32"
                    class="mb-2"
                  ></v-icon>
                  <div class="text-h6 font-weight-bold">
                    {{ formatChange(comparisonData.averageMoodChange) }}
                  </div>
                  <div class="text-caption">Среднее настроение</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ comparisonData.firstPeriodAvg.toFixed(1) }} → {{ comparisonData.secondPeriodAvg.toFixed(1) }}
                  </div>
                </div>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <div class="text-center">
                  <v-icon 
                    :color="getEntriesChangeColor(comparisonData.entriesChange)"
                    icon="mdi-calendar-multiple-check"
                    size="32"
                    class="mb-2"
                  ></v-icon>
                  <div class="text-h6 font-weight-bold">
                    {{ formatChange(comparisonData.entriesChange) }}
                  </div>
                  <div class="text-caption">Количество записей</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ comparisonData.firstPeriodEntries }} → {{ comparisonData.secondPeriodEntries }}
                  </div>
                </div>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <div class="text-center">
                  <v-icon 
                    :color="getVariabilityChangeColor(comparisonData.variabilityChange)"
                    icon="mdi-pulse"
                    size="32"
                    class="mb-2"
                  ></v-icon>
                  <div class="text-h6 font-weight-bold">
                    {{ formatChange(comparisonData.variabilityChange, true) }}
                  </div>
                  <div class="text-caption">Стабильность</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ comparisonData.firstPeriodVariability.toFixed(2) }} → {{ comparisonData.secondPeriodVariability.toFixed(2) }}
                  </div>
                </div>
              </v-col>

              <v-col cols="12" sm="6" md="3">
                <div class="text-center">
                  <v-icon 
                    color="info"
                    icon="mdi-emoticon-happy"
                    size="32"
                    class="mb-2"
                  ></v-icon>
                  <div class="text-h6 font-weight-bold">
                    {{ comparisonData.dominantEmotionChange ? '✓' : '—' }}
                  </div>
                  <div class="text-caption">Доминирующая эмоция</div>
                  <div class="text-caption text-medium-emphasis">
                    {{ comparisonData.firstDominantEmotion }} → {{ comparisonData.secondDominantEmotion }}
                  </div>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Chart Comparison -->
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-chart-line</v-icon>
            Сравнение трендов
          </v-card-title>
          <v-card-text>
            <div style="height: 400px;">
              <Line
                :data="comparisonChartData"
                :options="chartOptions"
                style="max-height: 400px;"
              />
            </div>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Detailed Analysis -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>Анализ изменений</v-card-title>
          <v-card-text>
            <v-list>
              <v-list-item
                v-for="(insight, index) in comparisonInsights"
                :key="index"
                :prepend-icon="insight.icon"
              >
                <v-list-item-title>{{ insight.title }}</v-list-item-title>
                <v-list-item-subtitle>{{ insight.description }}</v-list-item-subtitle>
              </v-list-item>
            </v-list>
          </v-card-text>
        </v-card>
      </v-col>

      <!-- Recommendations -->
      <v-col cols="12" md="6">
        <v-card>
          <v-card-title>
            <v-icon class="me-2">mdi-lightbulb</v-icon>
            Рекомендации
          </v-card-title>
          <v-card-text>
            <v-alert
              v-for="(recommendation, index) in recommendations"
              :key="index"
              :type="recommendation.type"
              variant="tonal"
              class="mb-2"
            >
              <div class="font-weight-medium mb-1">{{ recommendation.title }}</div>
              <div class="text-caption">{{ recommendation.text }}</div>
            </v-alert>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- Loading State -->
    <v-row v-else-if="loading">
      <v-col cols="12">
        <v-card>
          <v-card-text class="text-center py-8">
            <v-progress-circular indeterminate color="primary" size="64"></v-progress-circular>
            <p class="text-h6 mt-4">Загрузка данных для сравнения...</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <!-- No Data State -->
    <v-row v-else>
      <v-col cols="12">
        <v-card>
          <v-card-text class="text-center py-8">
            <v-icon size="64" color="grey-lighten-2">mdi-chart-timeline-variant</v-icon>
            <p class="text-h6 text-medium-emphasis mt-4">Выберите периоды для сравнения</p>
            <p class="text-caption">Данные будут загружены автоматически после выбора периодов</p>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { Line } from 'vue-chartjs'
import { useMoodStore } from '../stores/mood'

const props = defineProps({
  userId: {
    type: Number,
    required: true
  }
})

const moodStore = useMoodStore()

// Reactive data
const firstPeriod = ref('last_month')
const secondPeriod = ref('current_month')
const firstCustomDate = ref(null)
const secondCustomDate = ref(null)
const loading = ref(false)
const comparisonData = ref(null)

// Period options
const periodOptions = [
  { text: 'Текущий месяц', value: 'current_month' },
  { text: 'Прошлый месяц', value: 'last_month' },
  { text: 'Текущая неделя', value: 'current_week' },
  { text: 'Прошлая неделя', value: 'last_week' },
  { text: 'Последние 30 дней', value: 'last_30_days' },
  { text: 'Последние 7 дней', value: 'last_7_days' },
  { text: 'Пользовательский', value: 'custom' }
]

// Computed properties
const comparisonChartData = computed(() => {
  if (!comparisonData.value) return null

  return {
    labels: comparisonData.value.chartLabels,
    datasets: [
      {
        label: getDisplayPeriodName(firstPeriod.value),
        data: comparisonData.value.firstPeriodData,
        borderColor: '#1976D2',
        backgroundColor: 'rgba(25, 118, 210, 0.1)',
        fill: false,
        tension: 0.4
      },
      {
        label: getDisplayPeriodName(secondPeriod.value),
        data: comparisonData.value.secondPeriodData,
        borderColor: '#388E3C',
        backgroundColor: 'rgba(56, 142, 60, 0.1)',
        fill: false,
        tension: 0.4
      }
    ]
  }
})

const comparisonInsights = computed(() => {
  if (!comparisonData.value) return []

  const insights = []
  const data = comparisonData.value

  // Mood change insight
  if (Math.abs(data.averageMoodChange) > 0.5) {
    insights.push({
      icon: data.averageMoodChange > 0 ? 'mdi-trending-up' : 'mdi-trending-down',
      title: `Настроение ${data.averageMoodChange > 0 ? 'улучшилось' : 'ухудшилось'}`,
      description: `На ${Math.abs(data.averageMoodChange).toFixed(1)} балла`
    })
  }

  // Entries frequency insight
  if (data.entriesChange !== 0) {
    insights.push({
      icon: data.entriesChange > 0 ? 'mdi-plus-circle' : 'mdi-minus-circle',
      title: `${data.entriesChange > 0 ? 'Увеличение' : 'Снижение'} активности`,
      description: `${Math.abs(data.entriesChange)} записей`
    })
  }

  // Variability insight
  if (Math.abs(data.variabilityChange) > 0.3) {
    insights.push({
      icon: data.variabilityChange < 0 ? 'mdi-heart-pulse' : 'mdi-pulse',
      title: `${data.variabilityChange < 0 ? 'Повышение' : 'Снижение'} стабильности`,
      description: `Изменение на ${Math.abs(data.variabilityChange).toFixed(2)}`
    })
  }

  return insights
})

const recommendations = computed(() => {
  if (!comparisonData.value) return []

  const recommendations = []
  const data = comparisonData.value

  if (data.averageMoodChange < -1) {
    recommendations.push({
      type: 'warning',
      title: 'Обратите внимание',
      text: 'Заметно снижение настроения. Рассмотрите возможность изменения рутины или консультации со специалистом.'
    })
  }

  if (data.averageMoodChange > 1) {
    recommendations.push({
      type: 'success',
      title: 'Отличный прогресс!',
      text: 'Ваше настроение значительно улучшилось. Продолжайте в том же духе!'
    })
  }

  if (data.entriesChange < -5) {
    recommendations.push({
      type: 'info',
      title: 'Ведите записи регулярно',
      text: 'Количество записей снизилось. Регулярный мониторинг поможет лучше понять паттерны настроения.'
    })
  }

  if (data.variabilityChange > 0.5) {
    recommendations.push({
      type: 'warning',
      title: 'Стабилизация настроения',
      text: 'Повышенная нестабильность настроения. Попробуйте техники релаксации или медитации.'
    })
  }

  return recommendations
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      position: 'top'
    },
    tooltip: {
      mode: 'index',
      intersect: false
    }
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'Дни'
      }
    },
    y: {
      min: 1,
      max: 10,
      title: {
        display: true,
        text: 'Оценка настроения'
      }
    }
  },
  interaction: {
    mode: 'nearest',
    axis: 'x',
    intersect: false
  }
}

// Methods
const getDisplayPeriodName = (period) => {
  const option = periodOptions.find(opt => opt.value === period)
  return option ? option.text : period
}

const getMoodChangeColor = (change) => {
  if (change > 0.5) return 'success'
  if (change < -0.5) return 'error'
  return 'warning'
}

const getMoodChangeIcon = (change) => {
  if (change > 0.5) return 'mdi-trending-up'
  if (change < -0.5) return 'mdi-trending-down'
  return 'mdi-trending-neutral'
}

const getEntriesChangeColor = (change) => {
  return change >= 0 ? 'success' : 'warning'
}

const getVariabilityChangeColor = (change) => {
  return change < 0 ? 'success' : 'warning'
}

const formatChange = (change, reverse = false) => {
  const sign = (reverse ? -change : change) >= 0 ? '+' : ''
  return `${sign}${(reverse ? -change : change).toFixed(1)}`
}

const loadComparisonData = async () => {
  if (!props.userId) return

  loading.value = true
  try {
    // Mock data generation for demonstration
    // In real implementation, this would call API endpoints
    const mockData = generateMockComparisonData()
    comparisonData.value = mockData
  } catch (error) {
    console.error('Error loading comparison data:', error)
  } finally {
    loading.value = false
  }
}

const generateMockComparisonData = () => {
  // Generate mock comparison data
  const firstPeriodData = Array.from({ length: 30 }, (_, i) => {
    return Math.random() * 3 + 5 + Math.sin(i / 5) * 1.5
  })
  
  const secondPeriodData = Array.from({ length: 30 }, (_, i) => {
    return Math.random() * 3 + 6 + Math.sin(i / 4) * 1.2
  })

  const firstAvg = firstPeriodData.reduce((a, b) => a + b, 0) / firstPeriodData.length
  const secondAvg = secondPeriodData.reduce((a, b) => a + b, 0) / secondPeriodData.length

  const firstVariability = calculateVariability(firstPeriodData)
  const secondVariability = calculateVariability(secondPeriodData)

  return {
    firstPeriodData,
    secondPeriodData,
    chartLabels: Array.from({ length: 30 }, (_, i) => `День ${i + 1}`),
    firstPeriodAvg: firstAvg,
    secondPeriodAvg: secondAvg,
    averageMoodChange: secondAvg - firstAvg,
    firstPeriodEntries: firstPeriodData.length,
    secondPeriodEntries: secondPeriodData.length,
    entriesChange: secondPeriodData.length - firstPeriodData.length,
    firstPeriodVariability: firstVariability,
    secondPeriodVariability: secondVariability,
    variabilityChange: secondVariability - firstVariability,
    firstDominantEmotion: 'Спокойствие',
    secondDominantEmotion: 'Радость',
    dominantEmotionChange: true
  }
}

const calculateVariability = (data) => {
  const mean = data.reduce((a, b) => a + b, 0) / data.length
  const variance = data.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / data.length
  return Math.sqrt(variance)
}

const onPeriodChange = () => {
  if (firstPeriod.value && secondPeriod.value) {
    loadComparisonData()
  }
}

// Watchers
watch([firstPeriod, secondPeriod, firstCustomDate, secondCustomDate], () => {
  onPeriodChange()
})

watch(() => props.userId, (newUserId) => {
  if (newUserId) {
    onPeriodChange()
  }
})

// Lifecycle
onMounted(() => {
  if (props.userId) {
    loadComparisonData()
  }
})
</script>

<style scoped>
.v-card {
  border-radius: 12px;
}

.v-alert {
  border-radius: 8px;
}

.text-caption {
  line-height: 1.2;
}
</style>