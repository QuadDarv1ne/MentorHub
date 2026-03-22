'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'

interface PlatformStats {
  total_users: number
  active_users: number
  total_sessions: number
  total_revenue: number
  conversion_rate: number
  user_growth: number
}

interface ChartData {
  label: string
  value: number
}

export default function AnalyticsDashboard() {
  const toast = useToast()
  const [isLoading, setIsLoading] = useState(true)
  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [userGrowth, setUserGrowth] = useState<ChartData[]>([])
  const [sessionData, setSessionData] = useState<ChartData[]>([])
  const [period, setPeriod] = useState(30)

  useEffect(() => {
    fetchAnalytics()
  }, [period])

  const fetchAnalytics = async () => {
    try {
      const [statsRes, growthRes, sessionsRes] = await Promise.all([
        fetch('/api/analytics/platform'),
        fetch(`/api/analytics/user-growth?days=${period}`),
        fetch(`/api/analytics/sessions?days=${period}`)
      ])

      if (statsRes.ok) {
        const data = await statsRes.json()
        setStats(data)
      }

      if (growthRes.ok) {
        const data = await growthRes.json()
        setUserGrowth(data.data || [])
      }

      if (sessionsRes.ok) {
        const data = await sessionsRes.json()
        setSessionData(data.data || [])
      }

      setIsLoading(false)
    } catch (error) {
      console.error('Analytics fetch error:', error)
      toast.error('Ошибка загрузки аналитики')
      setIsLoading(false)
    }
  }

  const StatCard = ({ title, value, change, icon }: { title: string; value: string | number; change?: number; icon: string }) => (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
          {change !== undefined && (
            <p className={`text-sm mt-2 ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}% за период
            </p>
          )}
        </div>
        <div className="text-4xl">{icon}</div>
      </div>
    </div>
  )

  const SimpleChart = ({ data, color }: { data: ChartData[]; color: string }) => {
    if (!data || data.length === 0) return null
    
    const maxValue = Math.max(...data.map(d => d.value))
    const height = 200
    const width = 100
    const barWidth = width / data.length - 2

    return (
      <div className="relative" style={{ height: `${height}px` }}>
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full" preserveAspectRatio="none">
          {data.map((d, i) => {
            const barHeight = (d.value / maxValue) * (height - 20)
            return (
              <rect
                key={i}
                x={i * (barWidth + 2) + 1}
                y={height - barHeight - 20}
                width={barWidth}
                height={barHeight}
                fill={color}
                rx="2"
              />
            )
          })}
        </svg>
        <div className="absolute bottom-0 left-0 right-0 flex justify-between text-xs text-gray-500">
          <span>{data[0]?.label}</span>
          <span>{data[data.length - 1]?.label}</span>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка аналитики...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            📊 Analytics Dashboard
          </h1>
          <select
            value={period}
            onChange={(e) => setPeriod(Number(e.target.value))}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          >
            <option value={7}>7 дней</option>
            <option value={30}>30 дней</option>
            <option value={90}>90 дней</option>
            <option value={365}>1 год</option>
          </select>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <StatCard
            title="Всего пользователей"
            value={stats?.total_users || 0}
            change={stats?.user_growth}
            icon="👥"
          />
          <StatCard
            title="Активных пользователей"
            value={stats?.active_users || 0}
            icon="✅"
          />
          <StatCard
            title="Всего сессий"
            value={stats?.total_sessions || 0}
            icon="📅"
          />
          <StatCard
            title="Доход"
            value={`$${stats?.total_revenue || 0}`}
            change={stats?.conversion_rate}
            icon="💰"
          />
        </div>

        {/* Charts */}
        <div className="grid lg:grid-cols-2 gap-6">
          {/* User Growth Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              📈 Рост пользователей
            </h2>
            <SimpleChart data={userGrowth} color="#4f46e5" />
          </div>

          {/* Sessions Chart */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              📅 Активность сессий
            </h2>
            <SimpleChart data={sessionData} color="#10b981" />
          </div>
        </div>

        {/* Additional Metrics */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
            📋 Детальная статистика
          </h2>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Конверсия</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.conversion_rate?.toFixed(2) || 0}%
              </p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Средний чек</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                ${stats?.total_revenue && stats?.total_sessions 
                  ? (stats.total_revenue / stats.total_sessions).toFixed(2) 
                  : 0}
              </p>
            </div>
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Активность</p>
              <p className="text-2xl font-bold text-gray-900 dark:text-white">
                {stats?.active_users && stats?.total_users
                  ? ((stats.active_users / stats.total_users) * 100).toFixed(1)
                  : 0}%
              </p>
            </div>
          </div>
        </div>

        {/* Export */}
        <div className="mt-6 flex justify-end">
          <button
            onClick={() => window.location.href = '/api/export?format=xlsx&type=analytics'}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-colors"
          >
            📥 Экспортировать отчёт
          </button>
        </div>
      </div>
    </div>
  )
}
