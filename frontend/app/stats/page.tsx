'use client'

import { useState } from 'react'
import { TrendingUp, Award, Clock, BookOpen, Target, Calendar, Star, ChevronRight } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface CourseProgress {
  id: number
  title: string
  progress: number
  hoursSpent: number
  lastActivity: string
  status: 'active' | 'completed' | 'paused'
}

interface Achievement {
  id: number
  title: string
  description: string
  earned: boolean
  earnedDate?: string
  icon: string
  rarity: 'common' | 'rare' | 'epic' | 'legendary'
}

interface MonthlyStats {
  month: string
  hoursLearned: number
  coursesCompleted: number
  sessionsAttended: number
}

export default function UserStatistics() {
  const [selectedPeriod, setSelectedPeriod] = useState('month')

  const overallStats = {
    totalHours: 147,
    coursesCompleted: 12,
    certificatesEarned: 8,
    currentStreak: 23,
    averageRating: 4.8,
    totalSessions: 45
  }

  const courseProgress: CourseProgress[] = [
    {
      id: 1,
      title: 'React Advanced Patterns',
      progress: 85,
      hoursSpent: 24,
      lastActivity: '2 часа назад',
      status: 'active'
    },
    {
      id: 2,
      title: 'Node.js Deep Dive',
      progress: 100,
      hoursSpent: 32,
      lastActivity: '3 дня назад',
      status: 'completed'
    },
    {
      id: 3,
      title: 'System Design Interview Prep',
      progress: 45,
      hoursSpent: 18,
      lastActivity: '1 день назад',
      status: 'active'
    },
    {
      id: 4,
      title: 'TypeScript Fundamentals',
      progress: 100,
      hoursSpent: 16,
      lastActivity: '1 неделя назад',
      status: 'completed'
    },
    {
      id: 5,
      title: 'GraphQL Mastery',
      progress: 30,
      hoursSpent: 12,
      lastActivity: '5 дней назад',
      status: 'paused'
    }
  ]

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
      earned: true,
      earnedDate: '2025-03-05',
      icon: '⭐',
      rarity: 'epic'
    },
    {
      id: 4,
      title: 'Мастер времени',
      description: 'Накопите 100 часов обучения',
      earned: true,
      earnedDate: '2025-04-01',
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
      earned: false,
      icon: '🦋',
      rarity: 'rare'
    }
  ]

  const monthlyStats: MonthlyStats[] = [
    { month: 'Янв', hoursLearned: 28, coursesCompleted: 2, sessionsAttended: 8 },
    { month: 'Фев', hoursLearned: 35, coursesCompleted: 3, sessionsAttended: 10 },
    { month: 'Мар', hoursLearned: 42, coursesCompleted: 4, sessionsAttended: 12 },
    { month: 'Апр', hoursLearned: 42, coursesCompleted: 3, sessionsAttended: 15 }
  ]

  const maxHours = Math.max(...monthlyStats.map(s => s.hoursLearned))

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

  return (
    <div className="min-h-screen bg-gray-50">
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
        {/* Основные метрики */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium mb-1">Всего часов</p>
                <p className="text-4xl font-bold text-blue-900">{overallStats.totalHours}</p>
                <p className="text-xs text-blue-600 mt-2">+12 за последнюю неделю</p>
              </div>
              <Clock className="text-blue-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium mb-1">Завершено курсов</p>
                <p className="text-4xl font-bold text-green-900">{overallStats.coursesCompleted}</p>
                <p className="text-xs text-green-600 mt-2">+3 в этом месяце</p>
              </div>
              <BookOpen className="text-green-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium mb-1">Сертификатов</p>
                <p className="text-4xl font-bold text-purple-900">{overallStats.certificatesEarned}</p>
                <p className="text-xs text-purple-600 mt-2">Топ 15% учеников</p>
              </div>
              <Award className="text-purple-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-orange-600 text-sm font-medium mb-1">Текущая серия</p>
                <p className="text-4xl font-bold text-orange-900">{overallStats.currentStreak}</p>
                <p className="text-xs text-orange-600 mt-2">дней подряд 🔥</p>
              </div>
              <Target className="text-orange-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-yellow-600 text-sm font-medium mb-1">Средний рейтинг</p>
                <p className="text-4xl font-bold text-yellow-900">{overallStats.averageRating}</p>
                <p className="text-xs text-yellow-600 mt-2">от менторов ⭐</p>
              </div>
              <Star className="text-yellow-400" size={48} />
            </div>
          </Card>

          <Card className="bg-gradient-to-br from-indigo-50 to-indigo-100 border-indigo-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-indigo-600 text-sm font-medium mb-1">Всего сессий</p>
                <p className="text-4xl font-bold text-indigo-900">{overallStats.totalSessions}</p>
                <p className="text-xs text-indigo-600 mt-2">с менторами</p>
              </div>
              <Calendar className="text-indigo-400" size={48} />
            </div>
          </Card>
        </div>

        {/* График активности */}
        <Card className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Активность по месяцам</h2>
            <div className="flex gap-2">
              {['month', 'quarter', 'year'].map(period => (
                <button
                  key={period}
                  onClick={() => setSelectedPeriod(period)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    selectedPeriod === period
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {period === 'month' ? 'Месяц' : period === 'quarter' ? 'Квартал' : 'Год'}
                </button>
              ))}
            </div>
          </div>

          <div className="space-y-6">
            {monthlyStats.map(stat => (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">{stat.month}</span>
                  <div className="flex items-center space-x-4 text-sm text-gray-600">
                    <span>{stat.hoursLearned} часов</span>
                    <span>•</span>
                    <span>{stat.coursesCompleted} курсов</span>
                    <span>•</span>
                    <span>{stat.sessionsAttended} сессий</span>
                  </div>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 h-3 rounded-full transition-all progress-dynamic"
                    style={{ '--progress-width': `${(stat.hoursLearned / maxHours) * 100}%` } as React.CSSProperties}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>

        {/* Прогресс курсов */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Прогресс по курсам</h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {courseProgress.map(course => (
              <Card key={course.id} className="hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900 mb-2">{course.title}</h3>
                    <div className="flex items-center space-x-3 text-sm text-gray-600">
                      <span className="flex items-center space-x-1">
                        <Clock size={14} />
                        <span>{course.hoursSpent}ч</span>
                      </span>
                      <span>•</span>
                      <span>{course.lastActivity}</span>
                    </div>
                  </div>
                  <Badge
                    variant={
                      course.status === 'completed'
                        ? 'success'
                        : course.status === 'active'
                        ? 'info'
                        : 'warning'
                    }
                  >
                    {course.status === 'completed'
                      ? 'Завершен'
                      : course.status === 'active'
                      ? 'Активен'
                      : 'Пауза'}
                  </Badge>
                </div>

                <div className="mb-2">
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">Прогресс</span>
                    <span className="font-semibold text-gray-900">{course.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-indigo-600 h-2 rounded-full transition-all progress-dynamic"
                      style={{ '--progress-width': `${course.progress}%` } as React.CSSProperties}
                    />
                  </div>
                </div>

                {course.status === 'active' && (
                  <button className="w-full mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors font-medium flex items-center justify-center space-x-2">
                    <span>Продолжить обучение</span>
                    <ChevronRight size={18} />
                  </button>
                )}
              </Card>
            ))}
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

        {/* Цели */}
        <Card className="mt-12 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <div className="text-center">
            <TrendingUp className="mx-auto text-indigo-600 mb-4" size={48} />
            <h3 className="text-xl font-bold text-gray-900 mb-2">Продолжайте в том же духе!</h3>
            <p className="text-gray-600 mb-6">
              Вы на пути к следующему достижению. Осталось всего 5 сессий до &ldquo;Социальной бабочки&rdquo;!
            </p>
            <div className="flex justify-center gap-4">
              <button className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors">
                Забронировать сессию
              </button>
              <button className="px-6 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-100 font-medium transition-colors border border-gray-300">
                Посмотреть курсы
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
