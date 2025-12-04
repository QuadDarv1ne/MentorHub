'use client'

import { useEffect, useState, useCallback } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { refreshToken } from '@/lib/api/auth'

// Роуты, которые требуют авторизации
const PROTECTED_ROUTES = [
  '/dashboard',
  '/profile',
  '/settings',
  '/messages',
  '/notifications',
  '/sessions',
  '/booking',
  '/learning',
  '/stats',
  '/achievements',
  '/billing',
  '/payment'
]

// Интервал проверки токена (каждые 5 минут)
const TOKEN_CHECK_INTERVAL = 5 * 60 * 1000

// Время до истечения токена, когда нужно обновить (5 минут)
const REFRESH_THRESHOLD = 5 * 60

export function useAuth() {
  const router = useRouter()
  const pathname = usePathname()
  const [isRefreshing, setIsRefreshing] = useState(false)

  /**
   * Проверка истечения токена
   */
  const isTokenExpired = useCallback(() => {
    const expiresAt = localStorage.getItem('token_expires_at')
    if (!expiresAt) return true
    
    const expirationTime = parseInt(expiresAt, 10)
    const currentTime = Math.floor(Date.now() / 1000)
    
    return currentTime >= expirationTime
  }, [])

  /**
   * Проверка необходимости обновления токена
   */
  const shouldRefreshToken = useCallback(() => {
    const expiresAt = localStorage.getItem('token_expires_at')
    if (!expiresAt) return false
    
    const expirationTime = parseInt(expiresAt, 10)
    const currentTime = Math.floor(Date.now() / 1000)
    
    // Обновляем если осталось меньше 5 минут до истечения
    return expirationTime - currentTime <= REFRESH_THRESHOLD
  }, [])

  /**
   * Автоматическое обновление токена
   */
  const autoRefreshToken = useCallback(async () => {
    if (isRefreshing) return
    
    const refreshTokenValue = localStorage.getItem('refresh_token')
    if (!refreshTokenValue) return

    try {
      setIsRefreshing(true)
      const response = await refreshToken(refreshTokenValue)
      
      // Обновляем токены
      localStorage.setItem('access_token', response.access_token)
      localStorage.setItem('refresh_token', response.refresh_token)
      
      // Сохраняем время истечения
      const expiresAt = Math.floor(Date.now() / 1000) + response.expires_in
      localStorage.setItem('token_expires_at', expiresAt.toString())
      
      console.log('✅ Token автоматически обновлен')
    } catch (error) {
      console.error('❌ Ошибка обновления токена:', error)
      // При ошибке обновления - разлогиниваем
      logout()
    } finally {
      setIsRefreshing(false)
    }
  }, [isRefreshing])

  /**
   * Периодическая проверка токена
   */
  useEffect(() => {
    const checkToken = async () => {
      if (shouldRefreshToken()) {
        await autoRefreshToken()
      }
    }

    // Проверяем сразу при загрузке
    checkToken()

    // Устанавливаем периодическую проверку
    const interval = setInterval(checkToken, TOKEN_CHECK_INTERVAL)

    return () => clearInterval(interval)
  }, [shouldRefreshToken, autoRefreshToken])

  /**
   * Защита роутов
   */
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route))

    // Если пользователь не авторизован и пытается зайти на защищенный роут
    if (!token && isProtectedRoute) {
      router.push('/auth/login?redirect=' + encodeURIComponent(pathname))
    }

    // Если токен истек
    if (token && isTokenExpired()) {
      console.warn('⚠️ Токен истек, пытаемся обновить...')
      autoRefreshToken()
    }

    // Если пользователь авторизован и заходит на страницу логина
    if (token && !isTokenExpired() && pathname.startsWith('/auth/login')) {
      router.push('/dashboard')
    }
  }, [pathname, router, isTokenExpired, autoRefreshToken])

  const isAuthenticated = () => {
    const token = localStorage.getItem('access_token')
    return !!token && !isTokenExpired()
  }

  const login = (token: string, userData: Record<string, unknown>, expiresIn?: number, refreshToken?: string) => {
    // Сохраняем токен
    localStorage.setItem('access_token', token)
    
    // Сохраняем refresh token
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken)
    }
    
    // Сохраняем данные пользователя
    localStorage.setItem('user_data', JSON.stringify(userData))
    const userName = (userData.name as string) || (userData.email as string) || 'User'
    localStorage.setItem('user_name', userName)
    
    // Сохраняем время истечения токена
    if (expiresIn) {
      const expiresAt = Math.floor(Date.now() / 1000) + expiresIn
      localStorage.setItem('token_expires_at', expiresAt.toString())
    }
    
    // Добавляем защиту от CSRF
    const csrfToken = generateCSRFToken()
    localStorage.setItem('csrf_token', csrfToken)
  }

  const logout = () => {
    // Очищаем все данные
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('user_name')
    localStorage.removeItem('token_expires_at')
    localStorage.removeItem('csrf_token')
    
    // Перенаправляем на главную
    router.push('/')
  }

  const getUserData = () => {
    const data = localStorage.getItem('user_data')
    return data ? JSON.parse(data) : null
  }

  const getCSRFToken = () => {
    return localStorage.getItem('csrf_token') || ''
  }

  return {
    isAuthenticated,
    login,
    logout,
    getUserData,
    getCSRFToken,
    isRefreshing
  }
}

/**
 * Генерация CSRF токена
 */
function generateCSRFToken(): string {
  const array = new Uint8Array(32)
  crypto.getRandomValues(array)
  return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('')
}
