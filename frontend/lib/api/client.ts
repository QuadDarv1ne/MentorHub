/**
 * Unified API client with retry logic, token management, and typed endpoints.
 *
 * All API modules (auth, sessions, dashboard, etc.) should import from this file
 * rather than duplicating fetch/token/URL boilerplate.
 */

import { TIMEOUTS, RETRY, STORAGE_KEYS } from '@/lib/constants'

/* ------------------------------------------------------------------ */
/*  Error types                                                       */
/* ------------------------------------------------------------------ */

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
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

export class AuthError extends Error {
  constructor(message: string) {
    super(message)
    this.name = 'AuthError'
  }
}

/* ------------------------------------------------------------------ */
/*  Configuration                                                     */
/* ------------------------------------------------------------------ */

/**
 * Returns the base URL for the API.
 * Throws if no environment variable is set — prevents silent localhost fallback.
 */
function getBaseUrl(): string {
  const url = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL
  if (!url) {
    throw new Error(
      'NEXT_PUBLIC_API_BASE_URL or NEXT_PUBLIC_API_URL environment variable is not set',
    )
  }
  return url.replace(/\/+$/, '') // strip trailing slash
}

/**
 * Reads the access token from localStorage.
 * Safe to call during SSR — returns null on the server.
 */
export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
}

/**
 * Requires a valid access token or throws AuthError.
 */
export function requireToken(): string {
  const token = getAccessToken()
  if (!token) throw new AuthError('Authentication required')
  return token
}

/* ------------------------------------------------------------------ */
/*  HTTP client                                                       */
/* ------------------------------------------------------------------ */

interface RetryConfig {
  maxRetries: number
  retryDelay: number
  retryStatusCodes: number[]
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxRetries: RETRY.MAX_ATTEMPTS > 3 ? 3 : RETRY.MAX_ATTEMPTS,
  retryDelay: RETRY.DELAY,
  retryStatusCodes: [408, 429, 500, 502, 503, 504],
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
      const timeoutId = setTimeout(() => controller.abort(), TIMEOUTS.API_TIMEOUT)

      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (response.ok) return response

      if (!config.retryStatusCodes.includes(response.status)) {
        const errorBody = await response.json().catch(() => null)
        throw new ApiError(
          errorBody?.detail || errorBody?.message || `HTTP ${response.status}: ${response.statusText}`,
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
        lastError = error.name === 'AbortError'
          ? new TimeoutError('Request timeout')
          : new NetworkError(error.message)
      } else {
        lastError = new NetworkError('Unknown error')
      }
    }

    attempts++
    if (attempts > config.maxRetries) throw lastError

    const delay = config.retryDelay * Math.pow(2, attempts - 1)
    await sleep(delay)
  }

  throw lastError
}

/* ------------------------------------------------------------------ */
/*  Public API                                                        */
/* ------------------------------------------------------------------ */

/**
 * Make an authenticated API request.
 *
 * @param endpoint  Path relative to /api/v1 (e.g. "/auth/login")
 * @param options   Standard fetch RequestInit
 * @param opts      Additional options (skipAuth for public endpoints)
 */
interface RequestOptions {
  skipAuth?: boolean
}

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  opts?: RequestOptions,
): Promise<T> {
  const baseUrl = getBaseUrl()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }

  if (!opts?.skipAuth) {
    const token = getAccessToken()
    if (token) headers['Authorization'] = `Bearer ${token}`
  }

  const response = await fetchWithRetry(`${baseUrl}/api/v1${endpoint}`, {
    ...options,
    headers,
  })

  // 204 No Content
  if (response.status === 204) return null as T

  const data = await response.json()
  return data as T
}

/**
 * Convenience wrapper for public endpoints (no auth header).
 */
export async function publicRequest<T>(
  endpoint: string,
  options: RequestInit = {},
): Promise<T> {
  return apiRequest<T>(endpoint, options, { skipAuth: true })
}
