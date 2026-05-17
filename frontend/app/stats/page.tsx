'use client'

import { useState, useEffect, useCallback } from 'react'
import { TrendingUp, Award, Clock, BookOpen, Target, Calendar, Star, Loader2, AlertCircle } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { getDashboardData, type DashboardData } from '@/lib/api/dashboard'
import { getMyEngagement, type UserEngagement } from '@/lib/api/analytics'

interface Achievement {
  id: number
  title: string
  description: string
  earned: boolean
  earnedDate?: string
  icon: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

export default function UserStatistics() {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null)
  const [engagement, setEngagement] = useState<UserEngagement | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const [dash, eng] = await Promise.all([
        getDashboardData(),
        getMyEngagement(),
      ])
      setDashboardData(dash)
      setEngagement(eng)
    } catch {
      setError('Не удалось загрузить статистику')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchData()
  }, [fetchData])

  const achievements: Achievement[] = [
    {
      id: 1,
      title: 'Первые шаги',
      description: 'Завершите свой первый курс',
      earned: true,
      earnedDate: '2025-01-15',
      icon: '🎯',
      rarity: 'common'
    },
    {
      id: 2,
      title: 'Марафонец',
      description: 'Учитесь 7 дней подряд',
      earned: true,
      earnedDate: '2025-02-10',
      icon: '🏃',
      rarity: 'rare'
    },
    {
      id: 3,
      title: 'Профессионал',
      description: 'Завершите 10 курсов',
      earned: (dashboardData?.courses.completed ?? 0) >= 10,
      icon: '⭐',
      rarity: 'epic'
    },
    {
      id: 4,
      title: 'Мастер времени',
      description: 'Накопите 100 часов обучения',
      earned: false,
      icon: '⏰',
      rarity: 'epic'
    },
    {
      id: 5,
      title: 'Легенда',
      description: 'Получите рейтинг 5.0 от менторов',
      earned: false,
      icon: '👑',
      rarity: 'legendary'
    },
    {
      id: 6,
      title: 'Социальная бабочка',
      description: 'Посетите 50 сессий с менторами',
      earned: (dashboardData?.sessions.total ?? 0) >= 50,
      icon: '🦋',
      rarity: 'rare'
    }
  ]

  const getRarityColor = (rarity: Achievement['rarity']) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 border-gray-300'
      case 'rare': return 'bg-blue-100 border-blue-300'
      case 'epic': return 'bg-purple-100 border-purple-300'
      case 'legendary': return 'bg-yellow-100 border-yellow-300'
    }
  }

  const getRarityBadge = (rarity: Achievement['rarity']) => {
    switch (rarity) {
      case 'common': return <Badge variant="default">Обычное</Badge>
      case 'rare': return <Badge variant="info">Редкое</Badge>
      case 'epic': return <Badge variant="warning">Эпическое</Badge>
      case 'legendary': return <Badge variant="danger">Легендарное</Badge>
    }
  }

  const engagementColor = (score: number) => {
    if (score >= 70) return 'text-green-600'
    if (score >= 40) return 'text-yellow-600'
    return 'text-red-600'
  }

  const engagementBg = (score: number) => {
    if (score >= 70) return 'from-green-500 to-green-600'
    if (score >= 40) return 'from-yellow-500 to-yellow-600'
    return 'from-red-500 to-red-600'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="w-12 h-12 animate-spin text-indigo-600 mx-auto mb-4" />
          <p className="text-gray-600">Загрузка статистики...</p>
        </div>
      </div>
    )
  }

  const courses = dashboardData?.courses ?? { total: 0, in_progress: 0, completed: 0 }
  const sessions = dashboardData?.sessions ?? { total: 0, upcoming: 0, completed: 0 }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Моя статистика</h1>
          <p className="text-indigo-100 text-lg">
            Отслеживайте свой прогресс и достижения в обучении
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium mb-1">Курсы</p>
                <p className="text-4xl font-bold text-blue-900">{courses.total}</p>
                <p className="text-xs text-blue-600 mt-2">{courses.in_progress} в процессе</p>
              </div>
              <BookOpen className="text-blue-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium mb-1">Завершено курсов</p>
                <p className="text-4xl font-bold text-green-900">{courses.completed}</p>
              </div>
              <Award className="text-green-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-50 to-indigo-100 border-indigo-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-600 text-sm font-medium mb-1">Всего сессий</p>
                <p className="text-4xl font-bold text-indigo-900">{sessions.total}</p>
                <p className="text-xs text-indigo-600 mt-2">{sessions.upcoming} предстоящих</p>
              </div>
              <Calendar className="text-indigo-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium mb-1">Предстоящие сессии</p>
                <p className="text-4xl font-bold text-orange-900">{sessions.upcoming}</p>
              </div>
              <Clock className="text-orange-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium mb-1">Вовлечённость</p>
                <p className={`text-4xl font-bold ${engagementColor(engagement?.engagement_score ?? 0)}`}>
                  {engagement?.engagement_score ?? 0}
                </p>
                <p className="text-xs text-gray-500 mt-2">/ 100</p>
              </div>
              <Target className="text-yellow-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium mb-1">Завершено сессий</p>
                <p className="text-4xl font-bold text-purple-900">{sessions.completed}</p>
              </div>
              <Star className="text-purple-400" size={48} />
            </div>
          </Card>
        </div>

        {/* Engagement score bar */}
        {engagement && (
          <Card className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Уровень вовлечённости</h2>
            <div className="flex items-center space-x-6">
              <div className="flex-1">
                <div className="w-full bg-gray-200 rounded-full h-4">
                  <div
                    className={`h-4 rounded-full bg-gradient-to-r ${engagementBg(engagement.engagement_score)} transition-all duration-500`}
                    style={{ width: `${engagement.engagement_score}%` }}
                  />
                </div>
              </div>
              <span className="text-2xl font-bold">{engagement.engagement_score}/100</span>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <p className="text-2xl font-bold text-blue-600">{engagement.sessions_attended}</p>
                <p className="text-xs text-gray-500">Сессий посещено</p>
              </div>
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <p className="text-2xl font-bold text-green-600">{engagement.courses_enrolled}</p>
                <p className="text-xs text-gray-500">Курсов записано</p>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <p className="text-2xl font-bold text-purple-600">{engagement.avg_progress.toFixed(0)}%</p>
                <p className="text-xs text-gray-500">Средний прогресс</p>
              </div>
              <div className="text-center p-3 bg-yellow-50 rounded-lg">
                <p className="text-2xl font-bold text-yellow-600">{engagement.reviews_written}</p>
                <p className="text-xs text-gray-500">Отзывов написано</p>
              </div>
            </div>
          </Card>
        )}

        {/* Recent activities */}
        {dashboardData?.recent_activities && dashboardData.recent_activities.length > 0 && (
          <Card className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Последняя активность</h2>
            <div className="space-y-3">
              {dashboardData.recent_activities.slice(0, 8).map((activity, idx) => {
                const iconMap: Record<string, React.ReactNode> = {
                  progress: <BookOpen size={16} className="text-blue-500" />,
                  session: <Calendar size={16} className="text-green-500" />,
                  review: <Star size={16} className="text-yellow-500" />,
                }
                return (
                  <div key={idx} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                    {iconMap[activity.type] || <TrendingUp size={16} className="text-gray-500" />}
                    <div className="flex-1">
                      <p className="text-sm font-medium text-gray-900">{activity.title}</p>
                      <p className="text-xs text-gray-500">{activity.detail}</p>
                    </div>
                    <span className="text-xs text-gray-400">
                      {activity.created_at ? new Date(activity.created_at).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }) : ''}
                    </span>
                  </div>
                )
              })}
            </div>
          </Card>
        )}

        {/* Course summary */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Обзор курсов</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="text-center bg-blue-50 border-blue-200">
              <BookOpen size={32} className="text-blue-500 mx-auto mb-3" />
              <p className="text-3xl font-bold text-blue-900">{courses.total}</p>
              <p className="text-sm text-blue-600">Всего курсов</p>
            </Card>
            <Card className="text-center bg-yellow-50 border-yellow-200">
              <Clock size={32} className="text-yellow-500 mx-auto mb-3" />
              <p className="text-3xl font-bold text-yellow-900">{courses.in_progress}</p>
              <p className="text-sm text-yellow-600">В процессе</p>
            </Card>
            <Card className="text-center bg-green-50 border-green-200">
              <Award size={32} className="text-green-500 mx-auto mb-3" />
              <p className="text-3xl font-bold text-green-900">{courses.completed}</p>
              <p className="text-sm text-green-600">Завершено</p>
            </Card>
          </div>
        </div>

        {/* Достижения */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Достижения</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {achievements.map(achievement => (
              <Card
                key={achievement.id}
                className={`transition-all ${
                  achievement.earned
                    ? `${getRarityColor(achievement.rarity)} border-2 hover:shadow-lg`
                    : 'bg-gray-50 opacity-60'
                }`}
              >
                <div className="text-center">
                  <div
                    className={`text-6xl mb-4 ${
                      achievement.earned ? '' : 'grayscale opacity-50'
                    }`}
                  >
                    {achievement.icon}
                  </div>
                  <h3 className="font-bold text-gray-900 mb-2">{achievement.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{achievement.description}</p>

                  <div className="flex items-center justify-center space-x-2">
                    {getRarityBadge(achievement.rarity)}
                    {achievement.earned && achievement.earnedDate && (
                      <Badge variant="success">
                        Получено {new Date(achievement.earnedDate).toLocaleDateString('ru-RU', {
                          day: 'numeric',
                          month: 'short'
                        })}
                      </Badge>
                    )}
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* CTA */}
        <Card className="mt-12 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <div className="text-center">
            <TrendingUp className="mx-auto text-indigo-600 mb-4" size={48} />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Продолжайте в том же духе!</h3>
            <p className="text-gray-600 mb-6">
              {engagement && engagement.engagement_score < 100
                ? `До максимальной вовлечённости осталось ${100 - engagement.engagement_score} баллов!`
                : 'Вы достигли максимального уровня вовлечённости!'}
            </p>
            <div className="flex justify-center gap-4">
              <a href="/sessions" className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors">
                Мои сессии
              </a>
              <a href="/courses" className="px-6 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-100 font-medium transition-colors border border-gray-300">
                Каталог курсов
              </a>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
