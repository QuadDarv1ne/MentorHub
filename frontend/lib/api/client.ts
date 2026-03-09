/**
 * HTTP client с retry logic и обработкой ошибок
 */

interface RetryConfig {
  maxRetries: number
  retryDelay: number
  retryStatusCodes: number[]
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: 3,
  retryDelay: 1000,
  retryStatusCodes: [408, 429, 500, 502, 503, 504],
}

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'NetworkError'
  }
}

export class TimeoutError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'TimeoutError'
  }
}

async function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms))
}

export async function fetchWithRetry(
  url: string,
  options: RequestInit = {},
  config: RetryConfig = DEFAULT_RETRY_CONFIG,
): Promise<Response> {
  let lastError: Error | null = null
  let attempts = 0

  while (attempts <= config.maxRetries) {
    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 30000) // 30s timeout

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      // Если статус успешный - возвращаем ответ
      if (response.ok) {
        return response
      }

      // Если статус не требует retry - выбрасываем ошибку сразу
      if (!config.retryStatusCodes.includes(response.status)) {
        throw new ApiError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
        )
      }

      lastError = new ApiError(
        `HTTP ${response.status}: ${response.statusText}`,
        response.status,
      )

    } catch (error) {
      if (error instanceof ApiError) {
        lastError = error
      } else if (error instanceof Error) {
        if (error.name === 'AbortError') {
          lastError = new TimeoutError('Request timeout')
        } else {
          lastError = new NetworkError(error.message)
        }
      } else {
        lastError = new NetworkError('Unknown error')
      }
    }

    attempts++

    // Если это была последняя попытка - выбрасываем ошибку
    if (attempts > config.maxRetries) {
      throw lastError
    }

    // Ждём перед следующей попыткой (exponential backoff)
    const delay = config.retryDelay * Math.pow(2, attempts - 1)
    await sleep(delay)
  }

  throw lastError
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetchWithRetry(`/api/v1${endpoint}`, {
    ...options,
    headers,
  })

  const data = await response.json()
  return data as T
}
