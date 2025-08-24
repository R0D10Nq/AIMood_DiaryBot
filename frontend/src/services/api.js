import axios from 'axios'

// Create axios instance with base configuration
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  }
})

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken')
      // Redirect to login if needed
    }
    return Promise.reject(error)
  }
)

export const api = {
  // Health check
  async getHealth() {
    return await apiClient.get('/health')
  },

  // Users
  async getUsers(params = {}) {
    return await apiClient.get('/users', { params })
  },

  async getUser(userId) {
    return await apiClient.get(`/users/${userId}`)
  },

  async getUserByTelegramId(telegramId) {
    return await apiClient.get(`/users/telegram/${telegramId}`)
  },

  async createUser(userData) {
    return await apiClient.post('/users', userData)
  },

  async updateUser(userId, userData) {
    return await apiClient.put(`/users/${userId}`, userData)
  },

  async deleteUser(userId) {
    return await apiClient.delete(`/users/${userId}`)
  },

  async getUsersStats() {
    return await apiClient.get('/users/stats/summary')
  },

  // Mood Entries
  async getMoodEntries(params = {}) {
    return await apiClient.get('/mood-entries', { params })
  },

  async getMoodEntry(entryId) {
    return await apiClient.get(`/mood-entries/${entryId}`)
  },

  async createMoodEntry(entryData, userId, analyze = true) {
    return await apiClient.post('/mood-entries', entryData, {
      params: { user_id: userId, analyze }
    })
  },

  async updateMoodEntry(entryId, entryData, reanalyze = false) {
    return await apiClient.put(`/mood-entries/${entryId}`, entryData, {
      params: { reanalyze }
    })
  },

  async deleteMoodEntry(entryId) {
    return await apiClient.delete(`/mood-entries/${entryId}`)
  },

  async getUserRecentEntries(userId, days = 7) {
    return await apiClient.get(`/mood-entries/user/${userId}/recent`, {
      params: { days }
    })
  },

  async getUserMoodStats(userId) {
    return await apiClient.get(`/mood-entries/user/${userId}/stats`)
  },

  async getUserMoodAnalytics(userId, period = 'month') {
    return await apiClient.get(`/mood-entries/user/${userId}/analytics`, {
      params: { period }
    })
  },

  async getUserMoodSummary(userId, days = 7) {
    return await apiClient.get(`/mood-entries/user/${userId}/summary`, {
      params: { days }
    })
  },

  async getUserRecommendations(userId) {
    return await apiClient.get(`/mood-entries/user/${userId}/recommendations`)
  },

  async checkTodayEntry(userId) {
    return await apiClient.get(`/mood-entries/user/${userId}/check-today`)
  },

  // Analytics
  async getDashboardData(userId) {
    return await apiClient.get(`/analytics/dashboard/${userId}`)
  },

  async getMoodTrends(userId, period = 'month') {
    return await apiClient.get(`/analytics/trends/${userId}`, {
      params: { period }
    })
  },

  async generateInsights(userId, days = 30) {
    return await apiClient.get(`/analytics/insights/${userId}`, {
      params: { days }
    })
  },

  async comparePeriods(userId, currentDays = 30, previousDays = 30) {
    return await apiClient.get(`/analytics/compare-periods/${userId}`, {
      params: { current_days: currentDays, previous_days: previousDays }
    })
  },

  async getGlobalStats() {
    return await apiClient.get('/analytics/global-stats')
  }
}

export default api