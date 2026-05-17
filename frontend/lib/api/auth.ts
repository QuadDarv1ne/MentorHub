/**
 * Auth API — login, register, token refresh, user profile.
 */

import { publicRequest, apiRequest } from './client'

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

/** Login user */
export async function login(credentials: LoginCredentials): Promise<TokenResponse> {
  return publicRequest<TokenResponse>('/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  })
}

/** Register new user */
export async function register(userData: RegisterData): Promise<User> {
  return publicRequest<User>('/auth/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  })
}

/** Refresh access token */
export async function refreshToken(refreshToken: string): Promise<TokenResponse> {
  return publicRequest<TokenResponse>('/auth/refresh', {
    method: 'POST',
    body: JSON.stringify({ refresh_token: refreshToken }),
  })
}

/** Logout user */
export async function logout(): Promise<void> {
  return Promise.resolve()
}

/** Get current user profile */
export async function getCurrentUser(): Promise<User> {
  return apiRequest<User>('/users/me')
}
