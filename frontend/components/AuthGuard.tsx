'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { Shield, AlertTriangle } from 'lucide-react'

interface AuthGuardProps {
  children: React.ReactNode
  redirectTo?: string
  requireAuth?: boolean
}

/**
 * Компонент защиты страниц от неавторизованного доступа
 * Используйте этот компонент для оборачивания приватных страниц
 */
export default function AuthGuard({ 
  children, 
  redirectTo = '/auth/login',
  requireAuth = true 
}: AuthGuardProps) {
  const router = useRouter()
  const [isChecking, setIsChecking] = useState(true)
  const [isAuthorized, setIsAuthorized] = useState(false)

  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('access_token')
      const hasAuth = !!token

      if (requireAuth && !hasAuth) {
        // Сохраняем текущий URL для редиректа после входа
        const currentPath = window.location.pathname
        router.push(`${redirectTo}?redirect=${encodeURIComponent(currentPath)}`)
        setIsAuthorized(false)
      } else {
        setIsAuthorized(true)
      }
      
      setIsChecking(false)
    }

    checkAuth()
  }, [requireAuth, redirectTo, router])

  if (isChecking) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Shield className="w-16 h-16 text-indigo-600 mx-auto mb-4 animate-pulse" />
          <p className="text-gray-600 text-lg">Проверка доступа...</p>
        </div>
      </div>
    )
  }

  if (!isAuthorized && requireAuth) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <AlertTriangle className="w-16 h-16 text-amber-500 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-gray-900 mb-2">
            Требуется авторизация
          </h2>
          <p className="text-gray-600 mb-6">
            Для доступа к этой странице необходимо войти в систему
          </p>
          <button
            onClick={() => router.push(redirectTo)}
            className="w-full px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
          >
            Войти в систему
          </button>
        </div>
      </div>
    )
  }

  return <>{children}</>
}
