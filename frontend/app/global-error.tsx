'use client'

import ErrorBoundary from '@/components/ErrorBoundary'
import { AlertTriangle, RefreshCw, Home } from 'lucide-react'
import Link from 'next/link'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <ErrorBoundary
      onError={() => {
        console.error('Global error:', error)
      }}
    >
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center px-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8 text-center border border-gray-200">
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
            <AlertTriangle className="h-8 w-8 text-red-600" />
          </div>

          <h1 className="text-2xl font-bold text-gray-900 mb-3">
            Что-то пошло не так
          </h1>

          <p className="text-gray-600 mb-6">
            Произошла ошибка при загрузке страницы. Мы уже работаем над исправлением.
          </p>

          {process.env.NODE_ENV === 'development' && (
            <details className="mb-6 text-left bg-gray-50 rounded-lg p-4">
              <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                Детали ошибки (только для разработки)
              </summary>
              <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-40 border">
                {error.toString()}
                {'\n\n'}
                {error.stack}
              </pre>
            </details>
          )}

          <div className="flex flex-col sm:flex-row gap-3">
            <button
              onClick={reset}
              className="flex-1 inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all"
            >
              <RefreshCw className="mr-2 h-5 w-5" />
              Попробовать снова
            </button>

            <Link
              href="/"
              className="flex-1 inline-flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all"
            >
              <Home className="mr-2 h-5 w-5" />
              На главную
            </Link>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  )
}