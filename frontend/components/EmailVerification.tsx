/**
 * Email Verification Component
 * Handles email verification flow with token validation
 */

'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader, Mail, Shield } from 'lucide-react'
import { useSearchParams, useRouter } from 'next/navigation'
import { useToast } from '@/lib/hooks/useNotifications'

interface VerificationResult {
  success: boolean
  message: string
}

export function EmailVerification() {
  const [status, setStatus] = useState<'idle' | 'verifying' | 'success' | 'error'>('idle')
  const [result, setResult] = useState<VerificationResult | null>(null)
  const searchParams = useSearchParams()
  const router = useRouter()
  const { success, error } = useToast()

  const token = searchParams.get('token')

  useEffect(() => {
    if (token) {
      verifyEmail(token)
    } else {
      setStatus('error')
      setResult({
        success: false,
        message: 'Токен верификации не найден в URL'
      })
    }
  }, [token])

  const verifyEmail = async (verificationToken: string) => {
    setStatus('verifying')
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/email/verify-email`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ token: verificationToken }),
      })

      const data = await response.json()

      if (response.ok) {
        setStatus('success')
        setResult({
          success: true,
          message: 'Email успешно подтвержден! Теперь вы можете войти в систему.'
        })
        success('Email подтвержден! Теперь вы можете войти в свой аккаунт')
        
        // Redirect to login after 3 seconds
        setTimeout(() => {
          router.push('/auth/login')
        }, 3000)
      } else {
        setStatus('error')
        setResult({
          success: false,
          message: data.detail || 'Ошибка при подтверждении email'
        })
        error('Ошибка верификации: ' + (data.detail || 'Неверный или просроченный токен'))
      }
    } catch {
      setStatus('error')
      setResult({
        success: false,
        message: 'Ошибка сети. Пожалуйста, попробуйте позже.'
      })
      error('Ошибка сети: Проверьте подключение к интернету')
    }
  }

  const resendVerification = async () => {
    try {
      const email = localStorage.getItem('pending_verification_email')
      
      if (!email) {
        error('Ошибка: Email не найден')
        return
      }

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/email/send-verification`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      })

      if (response.ok) {
        success('Письмо отправлено! Проверьте вашу почту для подтверждения')
      } else {
        const data = await response.json()
        error('Ошибка: ' + (data.detail || 'Не удалось отправить письмо'))
      }
    } catch {
      error('Ошибка сети: Проверьте подключение к интернету')
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-2xl shadow-xl overflow-hidden">
        <div className="p-8">
          <div className="text-center">
            {/* Icon */}
            <div className="mx-auto flex items-center justify-center w-16 h-16 rounded-full mb-6">
              {status === 'idle' && (
                <Mail className="w-10 h-10 text-blue-600" />
              )}
              {status === 'verifying' && (
                <Loader className="w-10 h-10 text-blue-600 animate-spin" />
              )}
              {status === 'success' && (
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-10 h-10 text-green-600" />
                </div>
              )}
              {status === 'error' && (
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <XCircle className="w-10 h-10 text-red-600" />
                </div>
              )}
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold text-gray-900 mb-2">
              {status === 'idle' && 'Подтверждение email'}
              {status === 'verifying' && 'Проверка...'}
              {status === 'success' && 'Email подтвержден!'}
              {status === 'error' && 'Ошибка верификации'}
            </h1>

            {/* Message */}
            <p className="text-gray-600 mb-8">
              {status === 'idle' && 'Проверяем ваш email...'}
              {status === 'verifying' && 'Подтверждаем ваш email адрес'}
              {status === 'success' && result?.message}
              {status === 'error' && result?.message}
            </p>

            {/* Actions */}
            {status === 'error' && (
              <div className="space-y-4">
                <button
                  onClick={() => window.location.reload()}
                  className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Повторить попытку
                </button>
                
                <button
                  onClick={resendVerification}
                  className="w-full bg-gray-100 text-gray-700 py-3 px-4 rounded-lg font-medium hover:bg-gray-200 transition-colors"
                >
                  Отправить новое письмо
                </button>
                
                <button
                  onClick={() => router.push('/auth/login')}
                  className="w-full text-blue-600 font-medium hover:text-blue-700 transition-colors"
                >
                  Вернуться к входу
                </button>
              </div>
            )}

            {status === 'success' && (
              <div className="text-center">
                <p className="text-gray-500 mb-4">Перенаправляем на страницу входа...</p>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div className="bg-blue-600 h-2 rounded-full animate-progress" style={{ width: '100%' }}></div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="bg-gray-50 px-8 py-6 border-t border-gray-100">
          <div className="flex items-center justify-center gap-2 text-sm text-gray-500">
            <Shield className="w-4 h-4" />
            <span>Ваши данные защищены</span>
          </div>
        </div>
      </div>

      <style jsx>{`
        @keyframes progress {
          0% { width: 0%; }
          100% { width: 100%; }
        }
        .animate-progress {
          animation: progress 3s linear;
        }
      `}</style>
    </div>
  )
}