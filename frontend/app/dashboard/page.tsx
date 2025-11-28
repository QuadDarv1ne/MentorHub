'use client'

import React, { useState, useEffect } from 'react'
import { BookOpen, TrendingUp, Award, Clock, Calendar, ArrowRight, Star, Target, CheckCircle } from 'lucide-react'
import Link from 'next/link'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import StatCard from '@/components/ui/StatCard'
import Tabs from '@/components/ui/Tabs'
import Skeleton from '@/components/ui/Skeleton'
import { useAuth } from '@/lib/hooks/useAuth'
import { getMySessions } from '@/lib/api/sessions'
import { getMyCourses } from '@/lib/api/courses'
import { getMyAchievements } from '@/lib/api/achievements'

interface DashboardStats {
  total_courses: number
  in_progress: number
  completed: number
  total_sessions: number
  upcoming_sessions: number
  total_reviews: number
}

interface Course {
  id: number
  name: string
  progress: number
  category: string
  mentor: string
  nextLesson: string
}

interface Session {
  id: number
  mentor: string
  topic: string
  date: string
  time: string
  duration: string
  status: string
}

interface BackendSession {
  id: number
  mentor_id: number
  student_id: number
  mentor_name?: string
  student_name?: string
  topic: string
  scheduled_time: string
  duration: number
  price: number
  status: 'pending' | 'confirmed' | 'completed' | 'cancelled'
  meeting_link?: string
  notes?: string
  created_at?: string
  updated_at?: string
  mentor?: {
    full_name?: string
  }
  student?: {
    full_name?: string
  }
}

interface Achievement {
  id: number
  icon: string
  title: string
  description: string
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [userName, setUserName] = useState('')
  const [coursesData, setCoursesData] = useState<Course[]>([])
  const [upcomingSessions, setUpcomingSessions] = useState<Session[]>([])
  const [achievements, setAchievements] = useState<Achievement[]>([])
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token && isAuthenticated()) {
      // Fetch user data
      fetch('http://localhost:8000/api/v1/users/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          setUserName(data.full_name || data.email)
        })
        .catch(() => {})

      // Fetch dashboard data
      fetch('http://localhost:8000/api/v1/stats/dashboard', {
        headers: { 'Authorization': `Bearer ${token}` }
      })
        .then(res => res.json())
        .then(data => {
          setStats(data)
          setLoading(false)
        })
        .catch(() => {
          setLoading(false)
        })

      // Fetch real courses data
      getMyCourses()
        .then(data => {
          const formattedCourses = data.map(course => ({
            id: course.id,
            name: course.comment ? course.comment.substring(0, 50) + (course.comment.length > 50 ? '...' : '') : `Course ${course.course_id}`,
            progress: Math.floor(Math.random() * 100), // Temporary progress
            category: 'Programming', // Temporary category
            mentor: course.user_name || 'Ментор', // Use user_name from course data
            nextLesson: 'Next Lesson' // Temporary next lesson
          }))
          setCoursesData(formattedCourses)
        })
        .catch(err => {
          console.error('Failed to fetch courses:', err)
          // Fallback to mock data
          setCoursesData([
            { id: 1, name: 'JavaScript Advanced', progress: 75, category: 'Programming', mentor: 'Иван Петров', nextLesson: 'Async/Await patterns' },
            { id: 2, name: 'System Design', progress: 60, category: 'Architecture', mentor: 'Мария Сидорова', nextLesson: 'Scalability' },
            { id: 3, name: 'SQL Optimization', progress: 45, category: 'Database', mentor: 'Александр Иванов', nextLesson: 'Query optimization' },
            { id: 4, name: 'React Hooks', progress: 90, category: 'Frontend', mentor: 'Дарья Волкова', nextLesson: 'Custom hooks' }
          ])
        })

      // Fetch real sessions data
      getMySessions('upcoming')
        .then(data => {
          const formattedSessions = data.map(session => ({
            id: session.id,
            mentor: session.mentor_name || 'Ментор',
            topic: session.topic,
            date: new Date(session.scheduled_time).toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' }),
            time: new Date(session.scheduled_time).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' }),
            duration: `${session.duration} мин`,
            status: session.status
          }))
          setUpcomingSessions(formattedSessions)
        })
        .catch(err => {
          console.error('Failed to fetch sessions:', err)
          // Fallback to mock data
          setUpcomingSessions([
            { id: 1, mentor: 'Иван Петров', topic: 'Async/Await Deep Dive', date: '21 ноября', time: '14:00', duration: '60 мин', status: 'confirmed' },
            { id: 2, mentor: 'Мария Сидорова', topic: 'System Design Discussion', date: '22 ноября', time: '16:00', duration: '90 мин', status: 'pending' },
            { id: 3, mentor: 'Александр Иванов', topic: 'Query Review', date: '23 ноября', time: '15:30', duration: '45 мин', status: 'confirmed' }
          ])
        })

      // Fetch real achievements data
      getMyAchievements()
        .then(data => {
          setAchievements(data)
        })
        .catch(err => {
          console.error('Failed to fetch achievements:', err)
          // Fallback to mock data
          setAchievements([
            { id: 1, icon: '🏆', title: '7-дневная серия', description: 'Учитесь 7 дней подряд' },
            { id: 2, icon: '📚', title: '5 курсов', description: 'Завершено 5 курсов' },
            { id: 3, icon: '⭐', title: 'Отличник', description: '4.8+ рейтинг в тестах' },
            { id: 4, icon: '🚀', title: 'Быстрый старт', description: 'Первые 3 дня обучения' }
          ])
        })
    } else {
      setLoading(false)
    }
  }, [isAuthenticated])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-8">
            <Skeleton className="h-10 w-64 mb-3" />
            <Skeleton className="h-6 w-96" />
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {[...Array(4)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (!isAuthenticated()) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card padding="lg" className="max-w-md w-full text-center">
          <div className="text-4xl mb-4">🔒</div>
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Требуется авторизация</h2>
          <p className="text-gray-600 mb-6">Войдите в систему, чтобы просмотреть личный кабинет</p>
          <Link href="/auth/login">
            <Button variant="primary" fullWidth>
              Войти
            </Button>
          </Link>
        </Card>
      </div>
    )
  }

  // Define tabs content
  const tabsContent = [
    {
      id: 'courses',
      label: '📚 Мои курсы',
      content: (
        <div className="space-y-4">
          {coursesData.map((course) => (
            <Card key={course.id} padding="md" hover>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{course.name}</h3>
                    <Badge variant="info" size="sm">{course.category}</Badge>
                  </div>
                  <p className="text-sm text-gray-600">Ментор: {course.mentor}</p>
                </div>
                <Button variant="outline" size="sm">
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </div>
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm text-gray-600">Прогресс</span>
                  <span className="text-sm font-semibold text-indigo-600">{course.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all"
                    style={{ width: `${course.progress}%` }}
                  />
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Следующий урок: <span className="font-semibold">{course.nextLesson}</span>
              </p>
            </Card>
          ))}
          <Link href="/courses">
            <Button variant="primary" fullWidth>
              <BookOpen className="h-4 w-4 mr-2" />
              Открыть все курсы
            </Button>
          </Link>
        </div>
      )
    },
    {
      id: 'sessions',
      label: '📅 Сессии',
      content: (
        <div className="space-y-4">
          {upcomingSessions.map((session) => (
            <Card key={session.id} padding="md" hover>
              <div className="flex items-start justify-between mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">{session.topic}</h3>
                    <Badge
                      variant={session.status === 'confirmed' ? 'success' : 'warning'}
                      size="sm"
                    >
                      {session.status === 'confirmed' ? 'Подтверждена' : 'Ожидание'}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">Ментор: {session.mentor}</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-indigo-600" />
                  <span className="text-sm text-gray-600">{session.date}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-indigo-600" />
                  <span className="text-sm text-gray-600">{session.time}</span>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-indigo-600">{session.duration}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <Button variant="primary" size="sm">
                  Присоединиться
                </Button>
                <Button variant="outline" size="sm">
                  Отложить
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )
    },
    {
      id: 'achievements',
      label: '🏆 Достижения',
      content: (
        <div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {achievements.map((achievement) => (
              <Card key={achievement.id} padding="md" hover className="text-center">
                <div className="text-4xl mb-3">{achievement.icon}</div>
                <h3 className="font-semibold text-gray-900 mb-1">{achievement.title}</h3>
                <p className="text-sm text-gray-600">{achievement.description}</p>
              </Card>
            ))}
          </div>
        </div>
      )
    },
    {
      id: 'actions',
      label: '⚡ Действия',
      content: (
        <div className="space-y-4">
          <Link href="/courses">
            <Card padding="md" hover className="flex items-center justify-between cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="bg-blue-100 p-3 rounded-lg">
                  <BookOpen className="h-6 w-6 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Каталог курсов</h3>
                  <p className="text-sm text-gray-600">Начните новый курс</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </Card>
          </Link>

          <Link href="/mentors">
            <Card padding="md" hover className="flex items-center justify-between cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="bg-purple-100 p-3 rounded-lg">
                  <Star className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Найти ментора</h3>
                  <p className="text-sm text-gray-600">Забронируйте сессию</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </Card>
          </Link>

          <Link href="/profile">
            <Card padding="md" hover className="flex items-center justify-between cursor-pointer">
              <div className="flex items-center gap-4">
                <div className="bg-green-100 p-3 rounded-lg">
                  <CheckCircle className="h-6 w-6 text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Мой профиль</h3>
                  <p className="text-sm text-gray-600">Редактировать информацию</p>
                </div>
              </div>
              <ArrowRight className="h-5 w-5 text-gray-400" />
            </Card>
          </Link>

          <Card padding="md" className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200">
            <div className="flex items-start gap-3">
              <Target className="h-5 w-5 text-indigo-600 flex-shrink-0 mt-1" />
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">Совет дня</h4>
                <p className="text-sm text-gray-700">
                  Регулярные сессии с менторами значительно ускоряют ваш прогресс. Забронируйте первую сессию уже сегодня!
                </p>
              </div>
            </div>
          </Card>
        </div>
      )
    }
  ]

  return (
    <main className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white">
        <div className="container mx-auto max-w-7xl px-4 py-10">
          <h1 className="text-4xl font-bold mb-2">
            Добро пожаловать, {userName || 'пользователь'}! 👋
          </h1>
          <p className="text-indigo-100 text-lg">
            Продолжайте развивать свои навыки вместе с лучшими менторами
          </p>
        </div>
      </div>

      <div className="container mx-auto max-w-7xl px-4 py-10">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-10">
          <StatCard
            icon={<BookOpen className="h-6 w-6" />}
            value={stats?.total_courses || 0}
            title="Всего курсов"
            trend={{ value: 12, isPositive: true }}
          />
          <StatCard
            icon={<TrendingUp className="h-6 w-6" />}
            value={stats?.in_progress || 0}
            title="В процессе"
            trend={{ value: 8, isPositive: true }}
          />
          <StatCard
            icon={<Award className="h-6 w-6" />}
            value={stats?.completed || 0}
            title="Завершено"
            trend={{ value: 5, isPositive: true }}
          />
          <StatCard
            icon={<Calendar className="h-6 w-6" />}
            value={stats?.upcoming_sessions || 0}
            title="Предстоящие сессии"
            trend={{ value: 2, isPositive: true }}
          />
        </div>

        {/* Tabs with content */}
        <Tabs tabs={tabsContent} defaultTab="courses" />
      </div>
    </main>
  )
}