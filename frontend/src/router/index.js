import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Analytics from '../views/Analytics.vue'
import MoodEntry from '../views/MoodEntry.vue'
import Settings from '../views/Settings.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: Dashboard,
      meta: {
        title: 'Dashboard - AI Mood Diary'
      }
    },
    {
      path: '/analytics',
      name: 'analytics',
      component: Analytics,
      meta: {
        title: 'Analytics - AI Mood Diary'
      }
    },
    {
      path: '/mood-entry',
      name: 'mood-entry',
      component: MoodEntry,
      meta: {
        title: 'Add Mood Entry - AI Mood Diary'
      }
    },
    {
      path: '/settings',
      name: 'settings',
      component: Settings,
      meta: {
        title: 'Settings - AI Mood Diary'
      }
    },
    {
      path: '/user/:userId',
      name: 'user-dashboard',
      component: Dashboard,
      props: true,
      meta: {
        title: 'User Dashboard - AI Mood Diary'
      }
    }
  ]
})

router.beforeEach((to, from, next) => {
  // Update page title
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router