/**
 * Auth API — login, register, token refresh, user profile.
 */

import { publicRequest, apiRequest, setRefreshTokenCallback, getAccessToken, STORAGE_KEYS } from './client'

export interface LoginCredentials {
  email: string
  password: string
}

export interface RegisterData {
  email: string
  username: string
  full_name?: string
  password: string
  role?: 'student' | 'mentor'
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  expires_in: number
}

export interface User {
  id: number
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  role: 'student' | 'mentor' | 'admin'
  is_active: boolean
  is_verified: boolean
  created_at: string
}

/** Login user — stores tokens in localStorage */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  const data = await publicRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
  if (typeof window !== 'undefined') {
    localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token)
    localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token)
  }
  return data
}

/** Register new user */
export async function register(userData: RegisterData): Promise<User> {
  return publicRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
}

/** Refresh access token — backend reads refresh token from httpOnly cookie */
export async function refreshToken(_refreshTokenValue: string): Promise<TokenResponse> {
  // The refresh_token is now stored in an httpOnly cookie on the backend.
  // The refreshTokenValue parameter is kept for backward compatibility but
  // is no longer sent in the request body for security.
  return publicRequest<TokenResponse>('/auth/refresh', {
    method: 'POST',
    credentials: 'include',
  })
}

/** Logout user — call backend and clear local tokens */
export async function logout(): Promise<void> {
  const token = getAccessToken()
  try {
    await apiRequest<void>('/auth/logout', {
      method: 'POST',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
  } catch {
    // Ignore errors — we still want to clear local tokens
  }
  if (typeof window !== 'undefined') {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN)
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN)
    localStorage.removeItem('user_name')
    localStorage.removeItem('user_role')
  }
}

/** Get current user profile */
export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/users/me')
}

/**
 * Register the token refresh callback with the API client.
 * This enables automatic 401 handling (token refresh + retry).
 * Called once during app initialization.
 */
export function initAuthClient(): void {
  setRefreshTokenCallback(async (storedRefreshToken: string): Promise<string | null> => {
    try {
      const data = await refreshToken(storedRefreshToken)
      if (typeof window !== 'undefined') {
        localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token)
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token)
      }
      return data.access_token
    } catch {
      return null
    }
  })
}
