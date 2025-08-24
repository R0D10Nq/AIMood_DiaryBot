<template>
  <div class="emotion-correlation-matrix">
    <h4 class="text-subtitle-1 mb-4">Корреляция между эмоциями</h4>
    
    <v-table density="compact" class="correlation-table">
      <thead>
        <tr>
          <th></th>
          <th 
            v-for="emotion in data.emotions" 
            :key="emotion"
            class="text-center text-caption"
          >
            {{ emotion }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(emotion, rowIndex) in data.emotions" :key="emotion">
          <td class="font-weight-bold text-caption">{{ emotion }}</td>
          <td 
            v-for="(correlation, colIndex) in data.correlations[rowIndex]"
            :key="colIndex"
            class="text-center correlation-cell"
            :class="getCorrelationClass(correlation)"
          >
            <v-chip
              :color="getCorrelationColor(correlation)"
              size="small"
              variant="flat"
            >
              {{ correlation.toFixed(2) }}
            </v-chip>
          </td>
        </tr>
      </tbody>
    </v-table>

    <div class="mt-4">
      <h5 class="text-subtitle-2 mb-2">Интерпретация:</h5>
      <v-row>
        <v-col cols="12" sm="4">
          <v-chip color="success" size="small" class="me-2">0.7 - 1.0</v-chip>
          <span class="text-caption">Сильная корреляция</span>
        </v-col>
        <v-col cols="12" sm="4">
          <v-chip color="warning" size="small" class="me-2">0.3 - 0.7</v-chip>
          <span class="text-caption">Умеренная корреляция</span>
        </v-col>
        <v-col cols="12" sm="4">
          <v-chip color="error" size="small" class="me-2">-1.0 - 0.3</v-chip>
          <span class="text-caption">Слабая/обратная корреляция</span>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script setup>
import { defineProps } from 'vue'

const props = defineProps({
  data: {
    type: Object,
    required: true,
    default: () => ({
      emotions: [],
      correlations: []
    })
  }
})

const getCorrelationColor = (correlation) => {
  const abs = Math.abs(correlation)
  if (abs >= 0.7) return 'success'
  if (abs >= 0.3) return 'warning'
  return 'error'
}

const getCorrelationClass = (correlation) => {
  const abs = Math.abs(correlation)
  if (abs >= 0.7) return 'strong-correlation'
  if (abs >= 0.3) return 'moderate-correlation'
  return 'weak-correlation'
}
</script>

<style scoped>
.correlation-table {
  max-width: 100%;
  overflow-x: auto;
}

.correlation-cell {
  padding: 8px 4px;
}

.strong-correlation {
  background-color: rgba(76, 175, 80, 0.1);
}

.moderate-correlation {
  background-color: rgba(255, 152, 0, 0.1);
}

.weak-correlation {
  background-color: rgba(244, 67, 54, 0.1);
}
</style>