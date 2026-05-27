'use client'

import { useState, useEffect } from 'react'
import { BookOpen, Clock, Star, MessageSquare, Calendar, Activity } from 'lucide-react'
import { getDashboardData, type DashboardData } from '@/lib/api/dashboard'

function MetricCard({ icon: Icon, label, value, color }: { icon: React.ComponentType<{ className?: string }>; label: string; value: string | number; color: string }) {
  return (
    <div className={`rounded-xl border-l-4 ${color} bg-white dark:bg-gray-800 p-6 shadow-sm`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600 dark:text-gray-400">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-white mt-1">{value}</p>
        </div>
        <Icon className="w-10 h-10 opacity-20 text-gray-500" />
      </div>
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
      <div className="h-4 bg-gray-200 rounded w-24 mb-3 animate-pulse" />
      <div className="h-8 bg-gray-200 rounded w-16 animate-pulse" />
    </div>
  )
}

export default function RealTimeDashboard() {
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetch = async () => {
      try {
        const result = await getDashboardData()
        setData(result)
      } catch {
        setError('Не удалось загрузить данные dashboard')
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">Dashboard</h1>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => <SkeletonCard key={i} />)}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!data) return null

  const { courses, sessions, upcoming_sessions, recent_activities } = data

  const formatDateTime = (iso: string | null) => {
    if (!iso) return '—'
    const d = new Date(iso)
    return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' })
  }

  const activityIcon = (type: string) => {
    switch (type) {
      case 'progress': return <BookOpen className="w-4 h-4 text-blue-600" />
      case 'session': return <Calendar className="w-4 h-4 text-green-600" />
      case 'review': return <Star className="w-4 h-4 text-yellow-600" />
      default: return <Activity className="w-4 h-4 text-gray-600" />
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-10 px-4">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
          <p className="text-indigo-100">Обзор вашего прогресса и активности</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-8 px-4">
        {/* Metric Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard icon={BookOpen} label="Курсы" value={courses.total} color="border-blue-500 bg-blue-50" />
          <MetricCard icon={Clock} label="Сессии" value={sessions.total} color="border-green-500 bg-green-50" />
          <MetricCard icon={Calendar} label="Предстоящие" value={sessions.upcoming} color="border-purple-500 bg-purple-50" />
          <MetricCard icon={MessageSquare} label="Отзывы" value={recent_activities.filter(a => a.type === 'review').length} color="border-orange-500 bg-orange-50" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upcoming Sessions */}
          <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <Calendar size={20} className="text-indigo-600" />
              <span>Предстоящие сессии</span>
            </h3>
            {upcoming_sessions.length === 0 ? (
              <p className="text-gray-500 text-center py-6">Нет предстоящих сессий</p>
            ) : (
              <div className="space-y-3">
                {upcoming_sessions.map(session => (
                  <div key={session.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div>
                      <p className="font-medium text-gray-900 dark:text-white">Сессия #{session.id}</p>
                      <p className="text-sm text-gray-500">{formatDateTime(session.scheduled_at)} · {session.duration_minutes ?? '—'} мин</p>
                    </div>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      session.status === 'confirmed' ? 'bg-green-100 text-green-700' :
                      session.status === 'scheduled' ? 'bg-blue-100 text-blue-700' :
                      'bg-yellow-100 text-yellow-700'
                    }`}>
                      {session.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Recent Activities */}
          <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <Activity size={20} className="text-indigo-600" />
              <span>Последняя активность</span>
            </h3>
            {recent_activities.length === 0 ? (
              <p className="text-gray-500 text-center py-6">Нет активности</p>
            ) : (
              <div className="space-y-3">
                {recent_activities.map((activity, i) => (
                  <div key={i} className="flex items-start space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="mt-1">{activityIcon(activity.type)}</div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 dark:text-white text-sm">{activity.title}</p>
                      <p className="text-xs text-gray-500">{activity.detail}</p>
                    </div>
                    <span className="text-xs text-gray-400 whitespace-nowrap">{formatDateTime(activity.created_at)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Course & Session Breakdown */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mt-8">
          <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <BookOpen size={20} className="text-indigo-600" />
              <span>Курсы</span>
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Всего</span>
                <span className="font-semibold">{courses.total}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">В процессе</span>
                <span className="font-semibold text-blue-600">{courses.in_progress}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Завершено</span>
                <span className="font-semibold text-green-600">{courses.completed}</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border bg-white dark:bg-gray-800 p-6 shadow-sm">
            <h3 className="font-semibold text-gray-900 dark:text-white mb-4 flex items-center space-x-2">
              <Clock size={20} className="text-indigo-600" />
              <span>Сессии</span>
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-gray-600">Всего</span>
                <span className="font-semibold">{sessions.total}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Предстоящие</span>
                <span className="font-semibold text-purple-600">{sessions.upcoming}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Завершено</span>
                <span className="font-semibold text-green-600">{sessions.completed}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
