import axios from 'axios'

export const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// Auth token interceptor
apiClient.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('mes_token')
    if (token) config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Error normalizer
apiClient.interceptors.response.use(
  (res) => res,
  (err) => {
    const message = err.response?.data?.detail ?? err.message
    return Promise.reject(new Error(message))
  }
)
