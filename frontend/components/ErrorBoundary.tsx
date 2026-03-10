'use client'

import React from 'react'
import { AlertTriangle, RefreshCw, Home, WifiOff, Server, Bug } from 'lucide-react'
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

export default ErrorBoundary