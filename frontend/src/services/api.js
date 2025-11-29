import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
})

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      // Only redirect if we're not already on the login page
      if (window.location.pathname !== '/login' && window.location.pathname !== '/signup') {
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  }
)

// Auth API
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (email, password) => {
    const formData = new FormData()
    formData.append('username', email)
    formData.append('password', password)
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },
  logout: () => api.post('/auth/logout'),
}

// Upload API
export const uploadAPI = {
  uploadCSV: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    // Don't set Content-Type header - let browser set it with boundary for FormData
    return api.post('/upload/csv', formData, {
      timeout: 60000, // 60 second timeout for large files
      maxContentLength: Infinity,
      maxBodyLength: Infinity,
    })
  },
}

// Subscriptions API
export const subscriptionsAPI = {
  getAll: () => api.get('/subscriptions'),
  getById: (id) => api.get(`/subscriptions/${id}`),
  cancel: (id) => api.patch(`/subscriptions/${id}/cancel`),
}

// Harvey API
export const harveyAPI = {
  getRecommendations: () => api.get('/harvey/recommendations'),
  getSavings: () => api.get('/harvey/savings'),
  getAnomalies: () => api.get('/harvey/anomalies'),
}

// Profile API
export const profileAPI = {
  get: () => api.get('/profile'),
  update: (data) => api.patch('/profile', data),
  delete: () => api.delete('/profile'),
  getCSVHistory: () => api.get('/profile/csv-history'),
}

// Notifications API
export const notificationsAPI = {
  sendWhatsApp: (message) => api.post('/notify/whatsapp', { message }),
}

export default api

