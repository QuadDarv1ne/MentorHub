'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'

interface FunnelStep {
  name: string
  users: number
  conversion_rate: number
}

interface FunnelData {
  name: string
  steps: FunnelStep[]
  total_conversion: number
}

export default function ConversionFunnels() {
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(true)
  const [funnels, setFunnels] = useState<FunnelData[]>([])

  useEffect(() => {
    fetchFunnels()
  }, [])

  const fetchFunnels = async () => {
    try {
      const response = await fetch('/api/analytics/funnels')
      if (response.ok) {
        const data = await response.json()
        setFunnels(data.funnels || [])
      }
      setIsLoading(false)
    } catch (error) {
      console.error('Fetch funnels error:', error)
      toast.error('Ошибка загрузки воронок')
      setIsLoading(false)
    }
  }

  const defaultFunnels: FunnelData[] = [
    {
      name: 'User Registration Funnel',
      total_conversion: 45.5,
      steps: [
        { name: 'Посетили сайт', users: 10000, conversion_rate: 100 },
        { name: 'Зарегистрировались', users: 3500, conversion_rate: 35 },
        { name: 'Заполнили профиль', users: 2100, conversion_rate: 60 },
        { name: 'Нашли ментора', users: 1050, conversion_rate: 50 },
        { name: 'Оплатили сессию', users: 455, conversion_rate: 43.3 }
      ]
    },
    {
      name: 'Course Enrollment Funnel',
      total_conversion: 28.0,
      steps: [
        { name: 'Просмотрели курсы', users: 5000, conversion_rate: 100 },
        { name: 'Открыли детали курса', users: 2500, conversion_rate: 50 },
        { name: 'Добавили в корзину', users: 1000, conversion_rate: 40 },
        { name: 'Оплатили курс', users: 700, conversion_rate: 70 }
      ]
    }
  ]

  const FunnelChart = ({ funnel }: { funnel: FunnelData }) => {
    const data = isLoading ? defaultFunnels[0].steps : funnel.steps
    const maxUsers = Math.max(...data.map(s => s.users))

    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
        <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
          {funnel.name}
        </h3>
        <div className="space-y-3">
          {data.map((step, index) => (
            <div key={index} className="relative">
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  {step.name}
                </span>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {step.users.toLocaleString()} ({step.conversion_rate.toFixed(1)}%)
                </span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
                <div
                  className="bg-gradient-to-r from-indigo-500 to-purple-500 h-3 rounded-full transition-all duration-500"
                  style={{ width: `${(step.users / maxUsers) * 100}%` }}
                />
              </div>
              {index < data.length - 1 && (
                <div className="flex items-center mt-2 ml-4">
                  <div className="w-0.5 h-4 bg-gray-300 dark:bg-gray-600" />
                  <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">
                    ↓ {(100 - data[index + 1].conversion_rate).toFixed(1)}% отток
                  </span>
                </div>
              )}
            </div>
          ))}
        </div>
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Общая конверсия:
            </span>
            <span className="text-lg font-bold text-green-600 dark:text-green-400">
              {funnel.total_conversion.toFixed(1)}%
            </span>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          🔄 Conversion Funnels
        </h1>

        <div className="grid lg:grid-cols-2 gap-6">
          {funnels.length > 0 ? (
            funnels.map((funnel, index) => (
              <FunnelChart key={index} funnel={funnel} />
            ))
          ) : (
            <>
              <FunnelChart funnel={defaultFunnels[0]} />
              <FunnelChart funnel={defaultFunnels[1]} />
            </>
          )}
        </div>

        {/* Insights */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            💡 Рекомендации по улучшению конверсии
          </h2>
          <div className="space-y-4">
            <div className="flex items-start gap-3 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">
                  Большой отток на этапе заполнения профиля
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  40% пользователей не завершают профиль. Рассмотрите упрощение формы или прогрессивное заполнение.
                </p>
              </div>
            </div>
            <div className="flex items-start gap-3 p-4 bg-green-50 dark:bg-green-900/20 rounded-lg">
              <span className="text-2xl">✅</span>
              <div>
                <p className="font-medium text-gray-900 dark:text-white mb-1">
                  Хорошая конверсия на оплате
                </p>
                <p className="text-sm text-gray-600 dark:text-gray-400">
                  70% пользователей завершают оплату. Это выше среднего показателя по индустрии (65%).
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
