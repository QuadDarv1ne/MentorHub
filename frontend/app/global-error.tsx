'use client'

import { useEffect } from 'react'
import { AlertTriangle, RefreshCw } from 'lucide-react'

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    // Log критических ошибок
    console.error('Critical application error:', error)
  }, [error])

  return (
    <html lang="ru">
      <body>
        <div className="min-h-screen bg-gradient-to-br from-red-100 via-white to-orange-100 flex items-center justify-center px-4">
          <div className="max-w-lg w-full text-center">
            <div className="mb-8">
              <div className="relative inline-block">
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-40 h-40 bg-red-200 rounded-full opacity-30 animate-ping"></div>
                </div>
                <div className="relative w-40 h-40 bg-red-100 rounded-full flex items-center justify-center mx-auto shadow-2xl">
                  <AlertTriangle className="text-red-600" size={80} />
                </div>
              </div>
              <h1 className="mt-8 text-5xl font-bold text-gray-900">
                Критическая ошибка
              </h1>
              <p className="mt-4 text-xl text-gray-600">
                Приложение столкнулось с неожиданной проблемой
              </p>
            </div>

            <div className="bg-white rounded-2xl shadow-2xl p-8 border border-red-200 mb-8">
              <div className="text-left">
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Информация об ошибке:
                </h3>
                <div className="bg-red-50 border-2 border-red-300 rounded-lg p-4">
                  <p className="text-sm text-red-900 font-mono break-all">
                    {error.message || 'Неизвестная критическая ошибка'}
                  </p>
                  {error.digest && (
                    <p className="text-xs text-red-700 mt-3 pt-3 border-t border-red-200">
                      Error ID: <code className="bg-red-100 px-2 py-1 rounded">{error.digest}</code>
                    </p>
                  )}
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <button
                onClick={reset}
                className="w-full inline-flex items-center justify-center px-8 py-4 border border-transparent rounded-xl shadow-lg text-lg font-semibold text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all transform hover:scale-105"
              >
                <RefreshCw className="mr-3" size={24} />
                Перезагрузить приложение
              </button>

              <button
                onClick={() => window.location.href = '/'}
                className="w-full inline-flex items-center justify-center px-8 py-4 border-2 border-gray-300 rounded-xl shadow-lg text-lg font-semibold text-gray-700 bg-white hover:bg-gray-50 transition-all"
              >
                Вернуться на главную
              </button>
            </div>

            <div className="mt-8 p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-800">
                <strong>Что делать:</strong>
              </p>
              <ul className="mt-2 text-xs text-yellow-700 text-left space-y-1">
                <li>• Попробуйте обновить страницу</li>
                <li>• Очистите кэш браузера</li>
                <li>• Проверьте подключение к интернету</li>
                <li>• Если проблема сохраняется, свяжитесь с поддержкой</li>
              </ul>
            </div>

            <p className="mt-6 text-sm text-gray-500">
              Приносим извинения за неудобства. Наша команда уже работает над решением проблемы.
            </p>
          </div>
        </div>
      </body>
    </html>
  )
}
