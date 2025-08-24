<template>
  <div class="emotion-patterns">
    <h4 class="text-subtitle-1 mb-4">Обнаруженные эмоциональные паттерны</h4>
    
    <v-row>
      <v-col 
        v-for="(pattern, index) in data" 
        :key="index"
        cols="12" 
        md="4"
      >
        <v-card variant="outlined" class="pattern-card">
          <v-card-text>
            <div class="d-flex align-center mb-2">
              <v-icon 
                :color="getPatternColor(pattern.frequency)"
                class="me-2"
              >
                {{ getPatternIcon(pattern.pattern) }}
              </v-icon>
              <h5 class="text-subtitle-2">{{ pattern.pattern }}</h5>
            </div>
            
            <v-progress-linear
              :model-value="pattern.frequency"
              :color="getPatternColor(pattern.frequency)"
              height="8"
              rounded
              class="mb-2"
            >
              <template v-slot:default="{ value }">
                <strong>{{ Math.ceil(value) }}%</strong>
              </template>
            </v-progress-linear>
            
            <p class="text-caption text-medium-emphasis mb-2">
              {{ pattern.description }}
            </p>
            
            <v-chip
              :color="getPatternColor(pattern.frequency)"
              size="small"
              variant="outlined"
            >
              {{ getPatternStrength(pattern.frequency) }}
            </v-chip>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-alert
      type="info"
      variant="tonal"
      class="mt-4"
    >
      <v-icon slot="prepend">mdi-information</v-icon>
      <strong>Как читать паттерны:</strong> Процент показывает, как часто данный паттерн 
      встречается в ваших записях. Высокий процент означает устойчивый паттерн поведения.
    </v-alert>

    <!-- Pattern Details -->
    <v-expansion-panels class="mt-4">
      <v-expansion-panel
        v-for="(pattern, index) in data"
        :key="index"
      >
        <v-expansion-panel-title>
          <v-icon class="me-2">{{ getPatternIcon(pattern.pattern) }}</v-icon>
          Подробности: {{ pattern.pattern }}
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <v-row>
            <v-col cols="12" md="6">
              <h6 class="text-subtitle-2 mb-2">Характеристики паттерна:</h6>
              <v-list density="compact">
                <v-list-item>
                  <v-list-item-title>Частота проявления</v-list-item-title>
                  <v-list-item-subtitle>{{ pattern.frequency }}% от всех записей</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Уровень значимости</v-list-item-title>
                  <v-list-item-subtitle>{{ getPatternStrength(pattern.frequency) }}</v-list-item-subtitle>
                </v-list-item>
                <v-list-item>
                  <v-list-item-title>Тип паттерна</v-list-item-title>
                  <v-list-item-subtitle>{{ getPatternType(pattern.pattern) }}</v-list-item-subtitle>
                </v-list-item>
              </v-list>
            </v-col>
            <v-col cols="12" md="6">
              <h6 class="text-subtitle-2 mb-2">Рекомендации:</h6>
              <p class="text-body-2">
                {{ getPatternRecommendation(pattern.pattern) }}
              </p>
            </v-col>
          </v-row>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  data: {
    type: Array,
    required: true,
    default: () => []
  }
})

const getPatternColor = (frequency) => {
  if (frequency >= 75) return 'success'
  if (frequency >= 50) return 'warning'
  if (frequency >= 25) return 'info'
  return 'error'
}

const getPatternStrength = (frequency) => {
  if (frequency >= 75) return 'Очень сильный'
  if (frequency >= 50) return 'Сильный'
  if (frequency >= 25) return 'Умеренный'
  return 'Слабый'
}

const getPatternIcon = (pattern) => {
  if (pattern.includes('утр')) return 'mdi-weather-sunrise'
  if (pattern.includes('вечер')) return 'mdi-weather-sunset'
  if (pattern.includes('выходн')) return 'mdi-calendar-weekend'
  if (pattern.includes('тревог')) return 'mdi-alert-circle'
  if (pattern.includes('спокой')) return 'mdi-meditation'
  if (pattern.includes('радость')) return 'mdi-emoticon-happy'
  return 'mdi-chart-timeline-variant'
}

const getPatternType = (pattern) => {
  if (pattern.includes('утр') || pattern.includes('вечер')) return 'Временной паттерн'
  if (pattern.includes('выходн')) return 'Недельный паттерн'
  if (pattern.includes('тревог') || pattern.includes('спокой') || pattern.includes('радость')) return 'Эмоциональный паттерн'
  return 'Поведенческий паттерн'
}

const getPatternRecommendation = (pattern) => {
  if (pattern.includes('утр') && pattern.includes('тревог')) {
    return 'Рассмотрите утренние техники релаксации, медитацию или легкую физическую активность для снижения утренней тревожности.'
  }
  if (pattern.includes('вечер') && pattern.includes('спокой')) {
    return 'Отличный паттерн! Поддерживайте вечерние ритуалы, которые способствуют расслаблению.'
  }
  if (pattern.includes('выходн') && pattern.includes('радость')) {
    return 'Попробуйте интегрировать элементы выходных дней в будни для поддержания позитивного настроения.'
  }
  return 'Продолжайте отслеживать этот паттерн для лучшего понимания своих эмоциональных циклов.'
}
</script>

<style scoped>
.pattern-card {
  height: 100%;
  transition: transform 0.2s ease;
}

.pattern-card:hover {
  transform: translateY(-2px);
}

.v-progress-linear {
  border-radius: 8px;
}
</style>