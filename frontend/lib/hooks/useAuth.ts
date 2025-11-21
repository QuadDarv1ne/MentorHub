'use client'

import { useEffect } from 'react'
import { useRouter, usePathname } from 'next/navigation'

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

export function useAuth() {
  const router = useRouter()
  const pathname = usePathname()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const isProtectedRoute = PROTECTED_ROUTES.some(route => pathname.startsWith(route))

    // Если пользователь не авторизован и пытается зайти на защищенный роут
    if (!token && isProtectedRoute) {
      router.push('/auth/login?redirect=' + encodeURIComponent(pathname))
    }

    // Если пользователь авторизован и заходит на страницу логина
    if (token && pathname.startsWith('/auth/login')) {
      router.push('/dashboard')
    }
  }, [pathname, router])

  const isAuthenticated = () => {
    return !!localStorage.getItem('access_token')
  }

  const login = (token: string, userData: Record<string, unknown>) => {
    localStorage.setItem('access_token', token)
    localStorage.setItem('user_data', JSON.stringify(userData))
    const userName = (userData.name as string) || (userData.email as string) || 'User'
    localStorage.setItem('user_name', userName)
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_data')
    localStorage.removeItem('user_name')
    router.push('/')
  }

  const getUserData = () => {
    const data = localStorage.getItem('user_data')
    return data ? JSON.parse(data) : null
  }

  return {
    isAuthenticated,
    login,
    logout,
    getUserData
  }
}
