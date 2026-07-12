'use client'

import { useState, useEffect, Suspense } from 'react'
import { useRouter, useSearchParams } from 'next/navigation'
import { Eye, EyeOff, Mail, Lock, AlertCircle, CheckCircle, Loader2 } from 'lucide-react'
import Link from 'next/link'
import { login, getCurrentUser } from '@/lib/api/auth'
import { STORAGE_KEYS, LIMITS } from '@/lib/constants'
import ErrorBoundary from '@/components/ErrorBoundary'
import OAuthButtons from '@/components/OAuthButtons'

function LoginForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  })

  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  useEffect(() => {
    // Проверка, если пользователь уже авторизован
    const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN)
    if (token) {
      router.push('/dashboard')
    }
  }, [router])

  // Перемещено выше чтобы избежать Temporal Dead Zone

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    // Валидация
    if (!formData.email || !formData.password) {
      setError('Пожалуйста, заполните все поля')
      setLoading(false)
      return
    }

    if (!formData.email.includes('@')) {
      setError('Введите корректный email адрес')
      setLoading(false)
      return
    }

    if (formData.password.length < LIMITS.MIN_PASSWORD_LENGTH) {
      setError(`Пароль должен быть не менее ${LIMITS.MIN_PASSWORD_LENGTH} символов`)
      setLoading(false)
      return
    }

    try {
      // Real API authentication
      const authResponse = await login({
        email: formData.email,
        password: formData.password
      })

      // Store access token so getCurrentUser can use it
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, authResponse.access_token)
      if (formData.rememberMe && authResponse.refresh_token) {
        localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, authResponse.refresh_token)
      }

      // Get user profile via API client
      const user = await getCurrentUser()

      // User data is stored via localStorage below

      localStorage.setItem(STORAGE_KEYS.USER_NAME, user.full_name || user.email)
      localStorage.setItem(STORAGE_KEYS.USER_ROLE, user.role)
      localStorage.setItem(STORAGE_KEYS.USER_ID, String(user.id))
      setSuccess('Вход выполнен успешно!')

      setTimeout(() => {
        const redirect = searchParams.get('redirect') || '/dashboard'
        router.push(redirect)
      }, 1000)
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message || 'Ошибка при входе в систему')
      } else {
        setError('Ошибка при входе в систему')
      }
      setLoading(false)
    }
  }

  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-md">
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Войти в аккаунт
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Или{' '}
            <Link href="/auth/register" className="font-medium text-indigo-600 hover:text-indigo-500">
              создайте новый аккаунт
            </Link>
          </p>
        </div>

        <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
          <div className="bg-white py-8 px-4 shadow-xl sm:rounded-lg sm:px-10 border border-gray-100">
            {/* Уведомления */}
            {error && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-3">
                <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-sm text-red-800">{error}</p>
              </div>
            )}

            {success && (
              <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start space-x-3">
                <CheckCircle className="text-green-600 flex-shrink-0 mt-0.5" size={20} />
                <p className="text-sm text-green-800">{success}</p>
              </div>
            )}

            <form className="space-y-6" onSubmit={handleSubmit}>
              {/* Email */}
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                  Email адрес
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Mail className="text-gray-400" size={20} />
                  </div>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="appearance-none block w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                    placeholder="ваш@email.com"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                  Пароль
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <Lock className="text-gray-400" size={20} />
                  </div>
                  <input
                    id="password"
                    name="password"
                    type={showPassword ? 'text' : 'password'}
                    autoComplete="current-password"
                    required
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    className="appearance-none block w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition-colors"
                    placeholder="••••••••"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3 flex items-center"
                  >
                    {showPassword ? (
                      <EyeOff className="text-gray-400 hover:text-gray-600" size={20} />
                    ) : (
                      <Eye className="text-gray-400 hover:text-gray-600" size={20} />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember me & Forgot password */}
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <input
                    id="remember-me"
                    name="remember-me"
                    type="checkbox"
                    checked={formData.rememberMe}
                    onChange={(e) => setFormData({ ...formData, rememberMe: e.target.checked })}
                    className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded cursor-pointer"
                  />
                  <label htmlFor="remember-me" className="ml-2 block text-sm text-gray-900 cursor-pointer">
                    Запомнить меня
                  </label>
                </div>

                <div className="text-sm">
                  <Link href="/auth/forgot-password" className="font-medium text-indigo-600 hover:text-indigo-500">
                    Забыли пароль?
                  </Link>
                </div>
              </div>

              {/* Submit button */}
              <div>
                <button
                  type="submit"
                  disabled={loading}
                  className="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <div className="flex items-center space-x-2">
                      <Loader2 className="w-5 h-5 animate-spin" />
                      <span>Вход...</span>
                    </div>
                  ) : (
                    'Войти'
                  )}
                </button>
              </div>
            </form>

            {/* Social login */}
            <div className="mt-6">
              <OAuthButtons onOAuthStart={() => setError('')} />
            </div>

            {/* Demo credentials — dev only */}
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <p className="text-xs text-yellow-800 mb-2">
                  <strong>Демо-режим:</strong> Используйте любой email и пароль (мин. 6 символов)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}

export default function LoginPage() {
  return (
    <Suspense fallback={<div>Загрузка...</div>}>
      <LoginForm />
    </Suspense>
  )
}