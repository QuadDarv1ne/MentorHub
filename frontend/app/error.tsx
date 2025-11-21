'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { AlertTriangle, Home, RefreshCw, Mail } from 'lucide-react'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log ошибки в сервис мониторинга (например, Sentry)
    console.error('Application error:', error)
  }, [error])

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full text-center">
        {/* Error Icon */}
        <div className="mb-8">
          <div className="relative inline-block">
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-32 h-32 bg-red-100 rounded-full opacity-20 animate-pulse"></div>
            </div>
            <div className="relative w-32 h-32 bg-red-100 rounded-full flex items-center justify-center mx-auto">
              <AlertTriangle className="text-red-600" size={64} />
            </div>
          </div>
          <h1 className="mt-6 text-4xl font-bold text-gray-900">
            Произошла ошибка
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            Что-то пошло не так при обработке вашего запроса
          </p>
        </div>

        {/* Error Details */}
        <div className="bg-white rounded-2xl shadow-xl p-6 border border-gray-100 mb-8">
          <div className="text-left">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">
              Детали ошибки:
            </h3>
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-sm text-red-800 font-mono break-all">
                {error.message || 'Неизвестная ошибка'}
              </p>
              {error.digest && (
                <p className="text-xs text-red-600 mt-2">
                  Error ID: {error.digest}
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
          <button
            onClick={reset}
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-indigo-600 hover:bg-indigo-700 transition-colors"
          >
            <RefreshCw className="mr-2" size={20} />
            Попробовать снова
          </button>
          
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-colors"
          >
            <Home className="mr-2" size={20} />
            На главную
          </Link>
        </div>

        {/* Help Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center justify-center">
            <Mail className="mr-2" size={18} />
            Нужна помощь?
          </h3>
          <p className="text-sm text-blue-800 mb-4">
            Если ошибка повторяется, пожалуйста, сообщите нам об этом
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center justify-center px-4 py-2 border border-blue-300 rounded-lg text-sm font-medium text-blue-700 bg-white hover:bg-blue-50 transition-colors"
          >
            Связаться с поддержкой
          </Link>
        </div>

        {/* Additional Info */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
            <p className="text-2xl font-bold text-indigo-600">24/7</p>
            <p className="text-xs text-gray-600 mt-1">Поддержка</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
            <p className="text-2xl font-bold text-green-600">&lt;5 мин</p>
            <p className="text-xs text-gray-600 mt-1">Время ответа</p>
          </div>
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-100">
            <p className="text-2xl font-bold text-purple-600">99.9%</p>
            <p className="text-xs text-gray-600 mt-1">Uptime</p>
          </div>
        </div>

        <p className="mt-8 text-xs text-gray-500">
          Команда MentorHub работает над тем, чтобы такие ошибки не повторялись
        </p>
      </div>
    </div>
  )
}
