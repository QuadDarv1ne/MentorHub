'use client'

import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import {
  ArrowLeft, Users, Calendar, BookOpen, Star,
  Activity, Clock, AlertCircle
} from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { getAdminUserStats, type AdminUserStats } from '@/lib/api/admin'

function getInitials(name: string | null): string {
  if (!name) return '?'
  const parts = name.trim().split(/\s+/)
  if (parts.length >= 2) return (parts[0][0] + parts[1][0]).toUpperCase()
  return name[0].toUpperCase()
}

function formatDate(iso: string | null): string {
  if (!iso) return '—'
  return new Date(iso).toLocaleDateString('ru-RU', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function engagementColor(score: number): string {
  if (score >= 70) return 'text-green-600'
  if (score >= 40) return 'text-yellow-600'
  return 'text-red-600'
}

function engagementBg(score: number): string {
  if (score >= 70) return 'bg-green-600'
  if (score >= 40) return 'bg-yellow-600'
  return 'bg-red-600'
}

function engagementLabel(score: number): string {
  if (score >= 70) return 'Высокая'
  if (score >= 40) return 'Средняя'
  return 'Низкая'
}

const roleLabel: Record<string, string> = {
  student: 'Студент',
  mentor: 'Ментор',
  admin: 'Администратор',
}

const roleColorMap: Record<string, 'success' | 'warning' | 'info'> = {
  student: 'info',
  mentor: 'success',
  admin: 'warning',
}

export default function StudentDetailPage() {
  const params = useParams()
  const router = useRouter()
  const userId = Number(params.id)

  const [stats, setStats] = useState<AdminUserStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetch = async () => {
      setLoading(true)
      setError(null)
      try {
        const data = await getAdminUserStats(userId)
        setStats(data)
      } catch {
        setError('Не удалось загрузить статистику пользователя')
        setStats(null)
      } finally {
        setLoading(false)
      }
    }
    fetch()
  }, [userId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-4xl font-bold mb-4">Детали студента</h1>
            <p className="text-indigo-100 text-lg">Загрузка...</p>
          </div>
        </div>
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white rounded-lg p-6 animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-24 mb-3" />
                <div className="h-8 bg-gray-200 rounded w-16" />
              </div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error || !stats) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <h1 className="text-4xl font-bold mb-4">Детали студента</h1>
          </div>
        </div>
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <Card>
            <div className="flex items-center space-x-3 text-red-600">
              <AlertCircle size={20} />
              <p>{error || 'Пользователь не найден'}</p>
            </div>
            <button
              onClick={() => router.push('/admin')}
              className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              Назад к пользователям
            </button>
          </Card>
        </div>
      </div>
    )
  }

  const user = stats.user
  const sessionCompletionRate = stats.total_sessions > 0
    ? ((stats.completed_sessions / stats.total_sessions) * 100).toFixed(0)
    : '0'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <button
            onClick={() => router.push('/admin')}
            className="flex items-center space-x-2 text-indigo-100 hover:text-white mb-6 transition-colors"
          >
            <ArrowLeft size={18} />
            <span>Назад к пользователям</span>
          </button>
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 rounded-full bg-white/20 flex items-center justify-center">
              <span className="text-2xl font-bold">
                {getInitials(user.full_name || user.username)}
              </span>
            </div>
            <div>
              <h1 className="text-4xl font-bold">
                {user.full_name || user.username || user.email}
              </h1>
              <p className="text-indigo-100 text-lg">{user.email}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* User info badges */}
        <div className="flex flex-wrap gap-3 mb-8">
          <Badge variant={roleColorMap[user.role] || 'info'}>
            {roleLabel[user.role] || user.role}
          </Badge>
          <Badge variant={user.is_active ? 'success' : 'danger'}>
            {user.is_active ? 'Активен' : 'Неактивен'}
          </Badge>
          {user.is_verified && <Badge variant="success">Верифицирован</Badge>}
          <span className="text-sm text-gray-500 flex items-center space-x-1">
            <Calendar size={14} />
            <span>Регистрация: {formatDate(user.created_at)}</span>
          </span>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="bg-blue-50 border-l-4 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Всего сессий</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_sessions}</p>
              </div>
              <Calendar className="text-blue-600 w-12 h-12 opacity-20" />
            </div>
          </Card>

          <Card className="bg-green-50 border-l-4 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Завершено</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.completed_sessions}</p>
                <p className="text-green-600 text-xs font-semibold mt-1">{sessionCompletionRate}% завершено</p>
              </div>
              <Users className="text-green-600 w-12 h-12 opacity-20" />
            </div>
          </Card>

          <Card className="bg-purple-50 border-l-4 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-600 text-sm font-medium">Предстоящие</p>
                <p className="text-3xl font-bold text-gray-900 mt-2">{stats.upcoming_sessions}</p>
              </div>
              <Clock className="text-purple-600 w-12 h-12 opacity-20" />
            </div>
          </Card>

          <Card className="bg-orange-50 border-l-4 border-orange-200">
            <div>
              <p className="text-gray-600 text-sm font-medium flex items-center space-x-2">
                <Activity size={16} />
                <span>Вовлечённость</span>
              </p>
              <div className="flex items-end space-x-3 mt-2">
                <p className={`text-3xl font-bold ${engagementColor(stats.engagement_score)}`}>
                  {stats.engagement_score}
                </p>
                <span className="text-sm text-gray-500 mb-1">/ 100</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${engagementBg(stats.engagement_score)}`}
                  style={{ width: `${stats.engagement_score}%` }}
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">{engagementLabel(stats.engagement_score)}</p>
            </div>
          </Card>
        </div>

        {/* Two column layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left column */}
          <div className="space-y-8">
            {/* Ratings */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <Star size={20} className="text-yellow-500" />
                <span>Рейтинги</span>
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-yellow-50 rounded-lg border border-yellow-200">
                  <p className="text-sm text-gray-600">Средний рейтинг (оставленные)</p>
                  <p className="text-2xl font-bold text-yellow-600 mt-1">
                    {stats.avg_rating_given.toFixed(1)} ⭐
                  </p>
                </div>
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-600">Средний рейтинг (полученные)</p>
                  <p className="text-2xl font-bold text-blue-600 mt-1">
                    {stats.avg_rating_received.toFixed(1)} ⭐
                  </p>
                </div>
              </div>
            </Card>

            {/* Last activity */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                <Clock size={20} className="text-gray-500" />
                <span>Последняя активность</span>
              </h3>
              <p className="text-gray-700">
                {stats.last_activity ? formatDate(stats.last_activity) : 'Нет данных'}
              </p>
            </Card>
          </div>

          {/* Right column — Course progress */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
              <BookOpen size={20} className="text-indigo-600" />
              <span>Курсы ({stats.courses_enrolled})</span>
            </h3>
            {stats.course_stats.length === 0 ? (
              <p className="text-gray-500 text-center py-8">Студент не записан на курсы</p>
            ) : (
              <div className="space-y-4">
                {stats.course_stats.map(course => (
                  <div key={course.course_id} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-900">{course.course_title}</span>
                      <Badge variant={course.completed ? 'success' : 'info'}>
                        {course.completed ? 'Завершён' : 'В процессе'}
                      </Badge>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all duration-500 ${
                          course.progress_percent >= 100
                            ? 'bg-green-600'
                            : course.progress_percent >= 50
                              ? 'bg-blue-600'
                              : 'bg-yellow-600'
                        }`}
                        style={{ width: `${Math.min(course.progress_percent, 100)}%` }}
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">{course.progress_percent.toFixed(0)}%</p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>
      </div>
    </div>
  )
}
