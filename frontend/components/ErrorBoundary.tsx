'use client'

import React from 'react'
import { AlertTriangle, RefreshCw, Home, Bug, Server, WifiOff } from 'lucide-react'
import Link from 'next/link'

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void
}

interface ErrorBoundaryState {
  hasError: boolean
  error: Error | null
  errorInfo: React.ErrorInfo | null
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null,
    }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    this.setState({ errorInfo })
    this.props.onError?.(error, errorInfo)
    
    if (process.env.NODE_ENV === 'production') {
      // Можно отправить в Sentry или другой сервис мониторинга
    }
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null, errorInfo: null })
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      // Determine error type for better UX
      const error = this.state.error
      let errorType = 'generic'
      let errorTitle = 'Что-то пошло не так'
      let errorDescription = 'Произошла ошибка при загрузке этого компонента. Мы уже работаем над исправлением.'
      
      if (error?.message?.includes('NetworkError') || error?.message?.includes('Failed to fetch')) {
        errorType = 'network'
        errorTitle = 'Проблемы с соединением'
        errorDescription = 'Проверьте подключение к интернету и попробуйте снова.'
      } else if (error?.message?.includes('ChunkLoadError')) {
        errorType = 'chunk'
        errorTitle = 'Ошибка загрузки ресурсов'
        errorDescription = 'Не удалось загрузить необходимые файлы. Попробуйте обновить страницу.'
      } else if (error?.message?.includes('500') || error?.message?.includes('Internal Server Error')) {
        errorType = 'server'
        errorTitle = 'Серверная ошибка'
        errorDescription = 'На сервере произошла ошибка. Мы уже работаем над её устранением.'
      }

      const getErrorIcon = () => {
        switch (errorType) {
          case 'network':
            return <WifiOff className="h-8 w-8 text-amber-600" />
          case 'server':
            return <Server className="h-8 w-8 text-red-600" />
          case 'chunk':
            return <Bug className="h-8 w-8 text-purple-600" />
          default:
            return <AlertTriangle className="h-8 w-8 text-red-600" />
        }
      }

      return (
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8 text-center border border-gray-200">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
              {getErrorIcon()}
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-3">
              {errorTitle}
            </h1>
            
            <p className="text-gray-600 mb-6">
              {errorDescription}
            </p>

            {process.env.NODE_ENV === 'development' && this.state.error && (
              <details className="mb-6 text-left bg-gray-50 rounded-lg p-4">
                <summary className="cursor-pointer text-sm font-medium text-gray-700 mb-2">
                  Детали ошибки (только для разработки)
                </summary>
                <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-40 border">
                  {this.state.error.toString()}
                  {'\n\n'}
                  {this.state.error.stack}
                </pre>
                {this.state.errorInfo?.componentStack && (
                  <pre className="text-xs bg-white p-3 rounded overflow-auto max-h-40 border mt-2">
                    Component stack:
                    {this.state.errorInfo.componentStack}
                  </pre>
                )}
              </details>
            )}

            <div className="flex flex-col sm:flex-row gap-3">
              <button
                onClick={this.handleReset}
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

            <div className="mt-6 text-center">
              <p className="text-xs text-gray-500">
                Если ошибка повторяется,{' '}
                <Link href="/support" className="text-indigo-600 hover:text-indigo-500 underline">
                  сообщите нам об этом
                </Link>
              </p>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

// Специализированные Error Boundaries для разных секций

export function AuthErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8 text-center border border-indigo-200">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-3">
              Ошибка авторизации
            </h1>
            
            <p className="text-gray-600 mb-6">
              Не удалось загрузить форму авторизации. Пожалуйста, обновите страницу или попробуйте позже.
            </p>

            <div className="flex flex-col gap-3">
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              >
                <RefreshCw className="mr-2 h-5 w-5" />
                Обновить страницу
              </button>
              
              <Link
                href="/"
                className="inline-flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50"
              >
                <Home className="mr-2 h-5 w-5" />
                Вернуться на главную
              </Link>
            </div>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  )
}

export function DashboardErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-xl shadow-xl p-8 text-center border border-gray-200">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-6">
              <AlertTriangle className="h-8 w-8 text-red-600" />
            </div>
            
            <h1 className="text-2xl font-bold text-gray-900 mb-3">
              Ошибка загрузки данных
            </h1>
            
            <p className="text-gray-600 mb-6">
              Не удалось загрузить вашу панель управления. Данные могут быть временно недоступны.
            </p>

            <div className="flex flex-col gap-3">
              <button
                onClick={() => window.location.reload()}
                className="inline-flex items-center justify-center px-4 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700"
              >
                <RefreshCw className="mr-2 h-5 w-5" />
                Обновить
              </button>
              
              <Link
                href="/support"
                className="text-sm text-indigo-600 hover:text-indigo-500 underline"
              >
                Обратиться в поддержку
              </Link>
            </div>
          </div>
        </div>
      }
    >
      {children}
    </ErrorBoundary>
  )
}

// Enhanced global error boundary for app/error.tsx
export function EnhancedAppError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  // Determine error type for better UX
  let errorType = 'generic'
  let errorTitle = 'Произошла ошибка'
  let errorDescription = 'Что-то пошло не так при обработке вашего запроса'
  
  if (error?.message?.includes('NetworkError') || error?.message?.includes('Failed to fetch')) {
    errorType = 'network'
    errorTitle = 'Проблемы с соединением'
    errorDescription = 'Проверьте подключение к интернету и попробуйте снова.'
  } else if (error?.message?.includes('ChunkLoadError')) {
    errorType = 'chunk'
    errorTitle = 'Ошибка загрузки ресурсов'
    errorDescription = 'Не удалось загрузить необходимые файлы. Попробуйте обновить страницу.'
  } else if (error?.message?.includes('500') || error?.message?.includes('Internal Server Error')) {
    errorType = 'server'
    errorTitle = 'Серверная ошибка'
    errorDescription = 'На сервере произошла ошибка. Мы уже работаем над её устранением.'
  }

  const getErrorIcon = () => {
    switch (errorType) {
      case 'network':
        return <WifiOff className="text-amber-600" size={64} />
      case 'server':
        return <Server className="text-red-600" size={64} />
      case 'chunk':
        return <Bug className="text-purple-600" size={64} />
      default:
        return <AlertTriangle className="text-red-600" size={64} />
    }
  }

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
              {getErrorIcon()}
            </div>
          </div>
          <h1 className="mt-6 text-4xl font-bold text-gray-900">
            {errorTitle}
          </h1>
          <p className="mt-2 text-lg text-gray-600">
            {errorDescription}
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
            className="inline-flex items-center justify-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-base font-medium text-white bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 transition-all"
          >
            <RefreshCw className="mr-2" size={20} />
            Попробовать снова
          </button>
          
          <Link
            href="/"
            className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 rounded-lg shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 transition-all"
          >
            <Home className="mr-2" size={20} />
            На главную
          </Link>
        </div>

        {/* Help Section */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-sm font-semibold text-blue-900 mb-3 flex items-center justify-center">
            <Bug className="mr-2" size={18} />
            Нужна помощь?
          </h3>
          <p className="text-sm text-blue-800 mb-4">
            Если ошибка повторяется, пожалуйста, сообщите нам об этом
          </p>
          <Link
            href="/contact"
            className="inline-flex items-center justify-center px-4 py-2 border border-blue-300 rounded-lg text-sm font-medium text-blue-700 bg-white hover:bg-blue-50 transition-all"
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

export default ErrorBoundary