/**
 * API клиент для взаимодействия с backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

/**
 * Базовый fetch wrapper с обработкой ошибок
 */
async function fetchAPI<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`
  
  // Получаем токен из localStorage
  const token = typeof window !== 'undefined' 
    ? localStorage.getItem('access_token') 
    : null

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(url, {
      ...options,
      headers,
    })

    if (!response.ok) {
      let errorData
      try {
        errorData = await response.json()
      } catch {
        errorData = null
      }

      throw new ApiError(
        errorData?.message || `HTTP error ${response.status}`,
        response.status,
        errorData
      )
    }

    // Если нет контента (204 No Content)
    if (response.status === 204) {
      return null as T
    }

    return await response.json()
  } catch (error) {
    if (error instanceof ApiError) {
      throw error
    }
    
    throw new ApiError(
      'Network error. Please check your connection.',
      0,
      error
    )
  }
}

/**
 * API методы
 */
export const api = {
  // Auth
  auth: {
    login: (email: string, password: string) =>
      fetchAPI<{ access_token: string; user: unknown }>('/api/v1/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),

    register: (data: { email: string; username: string; password: string }) =>
      fetchAPI<{ access_token: string; user: unknown }>('/api/v1/auth/register', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    logout: () =>
      fetchAPI('/api/v1/auth/logout', {
        method: 'POST',
      }),

    refreshToken: () =>
      fetchAPI<{ access_token: string }>('/api/v1/auth/refresh', {
        method: 'POST',
      }),

    forgotPassword: (email: string) =>
      fetchAPI('/api/v1/auth/forgot-password', {
        method: 'POST',
        body: JSON.stringify({ email }),
      }),

    resetPassword: (token: string, password: string) =>
      fetchAPI('/api/v1/auth/reset-password', {
        method: 'POST',
        body: JSON.stringify({ token, password }),
      }),
  },

  // Users
  users: {
    me: () => fetchAPI<unknown>('/api/v1/users/me'),
    
    update: (data: unknown) =>
      fetchAPI<unknown>('/api/v1/users/me', {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    get: (id: number) => fetchAPI<unknown>(`/api/v1/users/${id}`),
  },

  // Mentors
  mentors: {
    list: (params?: { specialization?: string; minRating?: number }) => {
      const query = new URLSearchParams(params as Record<string, string>)
      return fetchAPI<unknown[]>(`/api/v1/mentors?${query}`)
    },

    get: (id: number) => fetchAPI<unknown>(`/api/v1/mentors/${id}`),

    apply: (data: unknown) =>
      fetchAPI<unknown>('/api/v1/mentors/apply', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    update: (id: number, data: unknown) =>
      fetchAPI<unknown>(`/api/v1/mentors/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    reviews: (id: number) =>
      fetchAPI<unknown[]>(`/api/v1/mentors/${id}/reviews`),
  },

  // Sessions
  sessions: {
    list: () => fetchAPI<unknown[]>('/api/v1/sessions'),

    create: (data: unknown) =>
      fetchAPI<unknown>('/api/v1/sessions', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    get: (id: number) => fetchAPI<unknown>(`/api/v1/sessions/${id}`),

    update: (id: number, data: unknown) =>
      fetchAPI<unknown>(`/api/v1/sessions/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),

    cancel: (id: number) =>
      fetchAPI(`/api/v1/sessions/${id}`, {
        method: 'DELETE',
      }),

    complete: (id: number) =>
      fetchAPI(`/api/v1/sessions/${id}/complete`, {
        method: 'POST',
      }),
  },

  // Courses
  courses: {
    list: () => fetchAPI<unknown[]>('/api/v1/courses'),

    get: (id: number) => fetchAPI<unknown>(`/api/v1/courses/${id}`),

    enroll: (id: number) =>
      fetchAPI(`/api/v1/courses/${id}/enroll`, {
        method: 'POST',
      }),

    progress: (id: number) =>
      fetchAPI<unknown>(`/api/v1/courses/${id}/progress`),
  },

  // Messages
  messages: {
    chats: () => fetchAPI<unknown[]>('/api/v1/messages/chats'),

    chatHistory: (chatId: number) =>
      fetchAPI<unknown[]>(`/api/v1/messages/chats/${chatId}`),

    send: (data: { recipientId: number; content: string }) =>
      fetchAPI('/api/v1/messages', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
  },

  // Payments
  payments: {
    create: (data: unknown) =>
      fetchAPI<unknown>('/api/v1/payments/create', {
        method: 'POST',
        body: JSON.stringify(data),
      }),

    history: () => fetchAPI<unknown[]>('/api/v1/payments/history'),
  },
}

/**
 * WebSocket клиент для real-time коммуникации
 */
export class WebSocketClient {
  private ws: WebSocket | null = null
  private url: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000

  constructor(endpoint: string) {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsHost = API_BASE_URL.replace(/^https?:\/\//, '')
    this.url = `${wsProtocol}//${wsHost}${endpoint}`
  }

  connect(onMessage: (data: unknown) => void, onError?: (error: Event) => void) {
    this.ws = new WebSocket(this.url)

    this.ws.onopen = () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('Error parsing WebSocket message:', error)
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error)
      if (onError) onError(error)
    }

    this.ws.onclose = () => {
      console.log('WebSocket disconnected')
      this.reconnect(onMessage, onError)
    }
  }

  private reconnect(onMessage: (data: unknown) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`)
      
      setTimeout(() => {
        this.connect(onMessage, onError)
      }, this.reconnectDelay * this.reconnectAttempts)
    }
  }

  send(data: unknown) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.error('WebSocket is not connected')
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}
