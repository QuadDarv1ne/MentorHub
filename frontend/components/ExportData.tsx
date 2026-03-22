'use client'

import { useState } from 'react'
import { useToast } from '@/hooks/useToast'

type ExportFormat = 'json' | 'csv' | 'xlsx' | 'pdf'
type ExportType = 'users' | 'courses' | 'sessions' | 'payments' | 'analytics'

interface ExportOptions {
  type: ExportType
  format: ExportFormat
  dateFrom?: string
  dateTo?: string
  userIds?: number[]
  courseIds?: number[]
}

export default function ExportData() {
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(false)
  const [options, setOptions] = useState<ExportOptions>({
    type: 'users',
    format: 'xlsx'
  })

  const exportTypes: { value: ExportType; label: string }[] = [
    { value: 'users', label: 'Пользователи' },
    { value: 'courses', label: 'Курсы' },
    { value: 'sessions', label: 'Сессии' },
    { value: 'payments', label: 'Платежи' },
    { value: 'analytics', label: 'Аналитика' }
  ]

  const exportFormats: { value: ExportFormat; label: string }[] = [
    { value: 'json', label: 'JSON' },
    { value: 'csv', label: 'CSV' },
    { value: 'xlsx', label: 'Excel' },
    { value: 'pdf', label: 'PDF' }
  ]

  const handleExport = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({
        format: options.format,
        type: options.type
      })

      if (options.dateFrom) params.append('date_from', options.dateFrom)
      if (options.dateTo) params.append('date_to', options.dateTo)

      const response = await fetch(`/api/export?${params}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          date_from: options.dateFrom,
          date_to: options.dateTo,
          user_ids: options.userIds,
          course_ids: options.courseIds
        })
      })

      if (!response.ok) {
        throw new Error('Export failed')
      }

      // Получаем файл
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      
      const filename = getFilename(options.type, options.format)
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)

      toast.success(`Файл ${filename} загружен`)
    } catch (error) {
      console.error('Export error:', error)
      toast.error('Ошибка экспорта')
    } finally {
      setIsLoading(false)
    }
  }

  const getFilename = (type: ExportType, format: ExportFormat): string => {
    const date = new Date().toISOString().split('T')[0]
    const extensions: Record<ExportFormat, string> = {
      json: 'json',
      csv: 'csv',
      xlsx: 'xlsx',
      pdf: 'pdf'
    }
    return `mentorhub_${type}_${date}.${extensions[format]}`
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
        Экспорт данных
      </h2>

      <div className="space-y-6">
        {/* Type selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Тип данных
          </label>
          <select
            value={options.type}
            onChange={(e) => setOptions({ ...options, type: e.target.value as ExportType })}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          >
            {exportTypes.map((type) => (
              <option key={type.value} value={type.value}>
                {type.label}
              </option>
            ))}
          </select>
        </div>

        {/* Format selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Формат файла
          </label>
          <div className="grid grid-cols-4 gap-3">
            {exportFormats.map((format) => (
              <button
                key={format.value}
                onClick={() => setOptions({ ...options, format: format.value })}
                className={`py-3 px-4 rounded-lg font-medium transition-colors ${
                  options.format === format.value
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white hover:bg-gray-200 dark:hover:bg-gray-600'
                }`}
              >
                {format.label.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Date range */}
        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Дата от
            </label>
            <input
              type="date"
              value={options.dateFrom || ''}
              onChange={(e) => setOptions({ ...options, dateFrom: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Дата до
            </label>
            <input
              type="date"
              value={options.dateTo || ''}
              onChange={(e) => setOptions({ ...options, dateTo: e.target.value })}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              min={options.dateFrom || undefined}
            />
          </div>
        </div>

        {/* Export button */}
        <button
          onClick={handleExport}
          disabled={isLoading}
          className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
            isLoading
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-indigo-600 hover:bg-indigo-700 text-white'
          }`}
        >
          {isLoading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              Подготовка...
            </span>
          ) : (
            '📥 Экспортировать'
          )}
        </button>

        {/* Info */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex items-start gap-3">
            <svg className="w-5 h-5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="text-sm text-blue-800 dark:text-blue-200">
              <p className="font-medium mb-1">Информация</p>
              <p>
                Экспорт включает все данные выбранного типа за указанный период. 
                Большие объёмы данных могут обрабатываться несколько секунд.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
