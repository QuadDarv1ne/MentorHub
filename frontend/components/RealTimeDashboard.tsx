'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'

interface DashboardStats {
  totalUsers: number
  activeSessions: number
  revenue: number
  newUsers: number
  conversionRate: number
  avgSessionRating: number
}

interface RecentActivity {
  id: number
  type: 'user' | 'session' | 'payment' | 'course'
  description: string
  timestamp: string
  status: 'success' | 'pending' | 'failed'
}

export default function RealTimeDashboard() {
  const toast = useToast()
  const [stats, setStats] = useState<DashboardStats>({
    totalUsers: 0,
    activeSessions: 0,
    revenue: 0,
    newUsers: 0,
    conversionRate: 0,
    avgSessionRating: 0
  })
  const [activities, setActivities] = useState<RecentActivity[]>([])
  const [isLive, setIsLive] = useState(true)
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date())

  useEffect(() => {
    if (!isLive) return

    // Fetch initial data
    fetchDashboardData()

    // Real-time updates every 5 seconds
    const interval = setInterval(() => {
      fetchDashboardData()
      setLastUpdate(new Date())
    }, 5000)

    return () => clearInterval(interval)
  }, [isLive])

  const fetchDashboardData = async () => {
    try {
      const [statsRes, activitiesRes] = await Promise.all([
        fetch('/api/dashboard/stats'),
        fetch('/api/dashboard/activities')
      ])

      if (statsRes.ok) {
        const data = await statsRes.json()
        setStats(data)
      }

      if (activitiesRes.ok) {
        const data = await activitiesRes.json()
        setActivities(data)
      }
    } catch (error) {
      console.error('Dashboard fetch error:', error)
    }
  }

  interface StatCardProps {
    title: string
    value: string | number
    change?: number
    icon: string
    color: string
  }

  const StatCard = ({ title, value, change, icon, color }: StatCardProps) => (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-500 dark:text-gray-400 text-sm font-medium mb-1">{title}</p>
          <p className="text-3xl font-bold text-gray-900 dark:text-white">{value}</p>
          {change && (
            <p className={`text-sm mt-2 font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? '↑' : '↓'} {Math.abs(change)}% за 24ч
            </p>
          )}
        </div>
        <div className={`w-16 h-16 rounded-2xl flex items-center justify-center text-3xl ${color}`}>
          {icon}
        </div>
      </div>
    </div>
  )

  const ActivityItem = ({ activity }: { activity: RecentActivity }) => {
    const icons = {
      user: '👤',
      session: '📅',
      payment: '💰',
      course: '📚'
    }

    const statusColors = {
      success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      failed: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
    }

    return (
      <div className="flex items-center gap-4 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
        <div className="text-2xl">{icons[activity.type]}</div>
        <div className="flex-1">
          <p className="font-medium text-gray-900 dark:text-white">{activity.description}</p>
          <p className="text-sm text-gray-500 dark:text-gray-400">{activity.timestamp}</p>
        </div>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusColors[activity.status]}`}>
          {activity.status === 'success' ? '✓' : activity.status === 'pending' ? '⏳' : '✗'}
        </span>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              📊 Real-time Dashboard
            </h1>
            <p className="text-gray-500 dark:text-gray-400">
              Последнее обновление: {lastUpdate.toLocaleTimeString()}
            </p>
          </div>
          <button
            onClick={() => setIsLive(!isLive)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              isLive
                ? 'bg-green-600 text-white hover:bg-green-700'
                : 'bg-gray-600 text-white hover:bg-gray-700'
            }`}
          >
            {isLive ? '🔴 Live' : '⏸ Paused'}
          </button>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          <StatCard
            title="Всего пользователей"
            value={stats.totalUsers.toLocaleString()}
            change={12.5}
            icon="👥"
            color="bg-indigo-100 dark:bg-indigo-900"
          />
          <StatCard
            title="Активные сессии"
            value={stats.activeSessions}
            change={8.3}
            icon="📅"
            color="bg-blue-100 dark:bg-blue-900"
          />
          <StatCard
            title="Доход (24ч)"
            value={`$${stats.revenue.toLocaleString()}`}
            change={15.2}
            icon="💰"
            color="bg-green-100 dark:bg-green-900"
          />
          <StatCard
            title="Новые пользователи"
            value={stats.newUsers}
            change={5.7}
            icon="🆕"
            color="bg-purple-100 dark:bg-purple-900"
          />
          <StatCard
            title="Конверсия"
            value={`${stats.conversionRate.toFixed(1)}%`}
            change={2.1}
            icon="📈"
            color="bg-yellow-100 dark:bg-yellow-900"
          />
          <StatCard
            title="Средний рейтинг"
            value={`${stats.avgSessionRating.toFixed(1)} ⭐`}
            change={0.5}
            icon="⭐"
            color="bg-pink-100 dark:bg-pink-900"
          />
        </div>

        {/* Recent Activity */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-100 dark:border-gray-700">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              🕐 Активность в реальном времени
            </h2>
            <button
              onClick={fetchDashboardData}
              className="text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-medium"
            >
              🔄 Обновить
            </button>
          </div>
          <div className="space-y-3">
            {activities.length > 0 ? (
              activities.map((activity) => (
                <ActivityItem key={activity.id} activity={activity} />
              ))
            ) : (
              <div className="text-center py-12 text-gray-500 dark:text-gray-400">
                Загрузка активности...
              </div>
            )}
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8 grid md:grid-cols-4 gap-4">
          <a
            href="/analytics"
            className="bg-indigo-600 hover:bg-indigo-700 text-white p-4 rounded-xl text-center font-medium transition-colors"
          >
            📈 Аналитика
          </a>
          <a
            href="/funnels"
            className="bg-purple-600 hover:bg-purple-700 text-white p-4 rounded-xl text-center font-medium transition-colors"
          >
            🔄 Воронки
          </a>
          <a
            href="/export"
            className="bg-green-600 hover:bg-green-700 text-white p-4 rounded-xl text-center font-medium transition-colors"
          >
            📥 Экспорт
          </a>
          <a
            href="/settings"
            className="bg-gray-600 hover:bg-gray-700 text-white p-4 rounded-xl text-center font-medium transition-colors"
          >
            ⚙️ Настройки
          </a>
        </div>
      </div>
    </div>
  )
}
