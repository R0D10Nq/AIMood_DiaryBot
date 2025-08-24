import { defineStore } from 'pinia'
import { api } from '../services/api'

export const useMoodStore = defineStore('mood', {
  state: () => ({
    // Current user
    currentUser: null,
    
    // Dashboard data
    dashboardData: null,
    loading: false,
    error: null,
    
    // Mood entries
    moodEntries: [],
    recentEntries: [],
    
    // Analytics
    moodStats: null,
    moodAnalytics: null,
    moodTrends: null,
    insights: null,
    recommendations: null,
    
    // UI state
    selectedPeriod: 'month',
    darkTheme: false,
    
    // Global stats
    globalStats: null
  }),

  getters: {
    // Calculate average mood from recent entries
    averageMood: (state) => {
      if (!state.recentEntries || state.recentEntries.length === 0) return 0
      const total = state.recentEntries.reduce((sum, entry) => sum + entry.mood_score, 0)
      return Math.round((total / state.recentEntries.length) * 10) / 10
    },

    // Get mood trend (improving/declining/stable)
    moodTrend: (state) => {
      if (!state.moodStats) return 'stable'
      return state.moodStats.mood_trend || 'stable'
    },

    // Check if user has entry today
    hasEntryToday: (state) => {
      if (!state.recentEntries || state.recentEntries.length === 0) return false
      const today = new Date().toISOString().split('T')[0]
      return state.recentEntries.some(entry => 
        entry.entry_date && entry.entry_date.startsWith(today)
      )
    },

    // Get current streak
    currentStreak: (state) => {
      return state.moodStats?.streak_days || 0
    },

    // Get formatted chart data for mood trends
    chartData: (state) => {
      if (!state.moodTrends || !state.moodTrends.mood_trend) return null
      
      return {
        labels: state.moodTrends.mood_trend.map(item => 
          new Date(item.date).toLocaleDateString('ru-RU', { 
            month: 'short', 
            day: 'numeric' 
          })
        ),
        datasets: [{
          label: 'Настроение',
          data: state.moodTrends.mood_trend.map(item => item.average_mood),
          borderColor: '#1976D2',
          backgroundColor: 'rgba(25, 118, 210, 0.1)',
          tension: 0.4
        }]
      }
    },

    // Get emotion trends data
    emotionTrendsData: (state) => {
      if (!state.moodTrends || !state.moodTrends.emotion_trends) return null
      
      const emotions = Object.keys(state.moodTrends.emotion_trends)
      const colors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
      
      return {
        labels: state.moodTrends.mood_trend?.map(item => 
          new Date(item.date).toLocaleDateString('ru-RU', { 
            month: 'short', 
            day: 'numeric' 
          })
        ) || [],
        datasets: emotions.map((emotion, index) => ({
          label: emotion,
          data: state.moodTrends.emotion_trends[emotion]?.map(item => item.value) || [],
          borderColor: colors[index % colors.length],
          backgroundColor: colors[index % colors.length] + '20',
          tension: 0.4
        }))
      }
    }
  },

  actions: {
    // Set current user
    setCurrentUser(user) {
      this.currentUser = user
      localStorage.setItem('currentUser', JSON.stringify(user))
    },

    // Load current user from localStorage
    loadCurrentUser() {
      const stored = localStorage.getItem('currentUser')
      if (stored) {
        this.currentUser = JSON.parse(stored)
      }
    },

    // Set loading state
    setLoading(loading) {
      this.loading = loading
    },

    // Set error
    setError(error) {
      this.error = error
    },

    // Clear error
    clearError() {
      this.error = null
    },

    // Fetch dashboard data
    async fetchDashboardData(userId) {
      try {
        this.setLoading(true)
        this.clearError()
        
        const response = await api.getDashboardData(userId)
        this.dashboardData = response.data
        
        // Update individual stores
        if (response.data.recent_entries) {
          this.recentEntries = response.data.recent_entries
        }
        if (response.data.stats) {
          this.moodStats = response.data.stats
        }
        if (response.data.recommendations) {
          this.recommendations = response.data.recommendations
        }
        if (response.data.monthly_analytics) {
          this.moodAnalytics = response.data.monthly_analytics
        }
        
      } catch (error) {
        console.error('Error fetching dashboard data:', error)
        this.setError('Не удалось загрузить данные дашборда')
      } finally {
        this.setLoading(false)
      }
    },

    // Fetch mood trends
    async fetchMoodTrends(userId, period = 'month') {
      try {
        this.setLoading(true)
        const response = await api.getMoodTrends(userId, period)
        this.moodTrends = response.data
        this.selectedPeriod = period
      } catch (error) {
        console.error('Error fetching mood trends:', error)
        this.setError('Не удалось загрузить тренды настроения')
      } finally {
        this.setLoading(false)
      }
    },

    // Fetch insights
    async fetchInsights(userId, days = 30) {
      try {
        const response = await api.generateInsights(userId, days)
        this.insights = response.data
      } catch (error) {
        console.error('Error fetching insights:', error)
        this.setError('Не удалось загрузить инсайты')
      }
    },

    // Create mood entry
    async createMoodEntry(entryData) {
      try {
        this.setLoading(true)
        this.clearError()
        
        // Mock API call - replace with actual API call
        const response = {
          success: true,
          data: {
            id: Date.now(),
            ...entryData,
            created_at: new Date().toISOString()
          },
          ai_analysis: 'Ваша запись показывает позитивное настроение. Продолжайте в том же духе!'
        }
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // Add to recent entries
        this.recentEntries.unshift(response.data)
        
        return {
          success: true,
          ai_analysis: response.ai_analysis
        }
      } catch (error) {
        console.error('Error creating mood entry:', error)
        this.setError('Не удалось создать запись настроения')
        return {
          success: false,
          error: error.message
        }
      } finally {
        this.setLoading(false)
      }
    },

    // Fetch recent entries
    async fetchRecentEntries(userId, limit = 10) {
      try {
        // Mock data - replace with actual API call
        const mockEntries = Array.from({ length: limit }, (_, i) => ({
          id: i + 1,
          user_id: userId,
          mood_score: Math.floor(Math.random() * 10) + 1,
          note: i % 3 === 0 ? `Заметка №${i + 1} о настроении` : null,
          emotions: ['радость', 'спокойствие'].slice(0, Math.floor(Math.random() * 2) + 1),
          activities: ['работа', 'спорт', 'чтение'].slice(0, Math.floor(Math.random() * 3) + 1),
          energy_level: Math.floor(Math.random() * 10) + 1,
          stress_level: Math.floor(Math.random() * 10) + 1,
          entry_date: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString(),
          created_at: new Date(Date.now() - i * 24 * 60 * 60 * 1000).toISOString()
        }))
        
        this.recentEntries = mockEntries
        return mockEntries
      } catch (error) {
        console.error('Error fetching recent entries:', error)
        this.setError('Не удалось загрузить последние записи')
        return []
      }
    },

    // Fetch global statistics
    async fetchGlobalStats() {
      try {
        const response = await api.getGlobalStats()
        this.globalStats = response.data
      } catch (error) {
        console.error('Error fetching global stats:', error)
      }
    },

    // Toggle theme
    toggleTheme() {
      this.darkTheme = !this.darkTheme
      localStorage.setItem('darkTheme', JSON.stringify(this.darkTheme))
    },

    // Load theme preference
    loadThemePreference() {
      const stored = localStorage.getItem('darkTheme')
      if (stored) {
        this.darkTheme = JSON.parse(stored)
      }
    },

    // Check API health
    async checkApiHealth() {
      try {
        await api.getHealth()
        return true
      } catch (error) {
        console.error('API health check failed:', error)
        return false
      }
    }
  }
})