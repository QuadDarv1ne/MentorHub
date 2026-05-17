'use client'

import { useState, useEffect } from 'react'
import {
  BookOpen, CheckCircle, Clock, BarChart3, PlayCircle, Lock,
  ChevronDown, Award, Target, TrendingUp
} from 'lucide-react'
import Link from 'next/link'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import { apiRequest } from '@/lib/api/client'

interface Module {
  id: number
  title: string
  duration: number
  lessons: number
  completed: number
  locked: boolean
}

interface EnrolledCourse {
  id: number
  title: string
  description: string | null
  category: string | null
  difficulty: string | null
  duration_hours: number
  instructor?: { full_name?: string } | null
  rating: number
  progress?: number
  completed_modules?: number
  total_modules?: number
  next_lesson?: string
  certificate?: boolean
  modules?: Module[]
}

export default function LearningPage() {
  const [expandedCourse, setExpandedCourse] = useState<number | null>(null)
  const [courseTab, setCourseTab] = useState<'active' | 'completed'>('active')
  const [courses, setCourses] = useState<EnrolledCourse[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadCourses()
  }, [])

  const loadCourses = async () => {
    try {
      setLoading(true)
      const data = await apiRequest<EnrolledCourse[]>('/courses/my')
      setCourses(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load courses')
    } finally {
      setLoading(false)
    }
  }

  const completedCourses = courses.filter(c => (c.progress ?? 0) >= 100)
  const activeCourses = courses.filter(c => (c.progress ?? 0) < 100)
  const displayCourses = courseTab === 'completed' ? completedCourses : activeCourses

  const totalHours = courses.reduce((sum, c) => sum + (c.duration_hours || 0), 0)
  const certificatesCount = completedCourses.filter(c => c.certificate).length

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка курсов...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Моё обучение</h1>
          <p className="text-indigo-100 text-lg">
            Продолжайте учиться и достигайте новых навыков
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Error banner */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-4 mb-6">
            <p className="text-red-800 dark:text-red-300 text-sm">{error}</p>
            <button onClick={loadCourses} className="text-red-600 dark:text-red-400 underline text-sm mt-1">
              Повторить
            </button>
          </div>
        )}

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-indigo-500 text-white">
                  <BookOpen size={24} />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Активных курсов</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{activeCourses.length}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-green-500 text-white">
                  <CheckCircle size={24} />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Завершено</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{completedCourses.length}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-purple-500 text-white">
                  <Award size={24} />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Сертификатов</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{certificatesCount}</p>
              </div>
            </div>
          </Card>

          <Card>
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <div className="flex items-center justify-center h-12 w-12 rounded-md bg-amber-500 text-white">
                  <TrendingUp size={24} />
                </div>
              </div>
              <div>
                <p className="text-sm text-gray-600 dark:text-gray-400">Часов обучения</p>
                <p className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(totalHours)}</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Табы */}
        <div className="mb-8 border-b border-gray-200 dark:border-gray-700">
          <div className="flex space-x-8">
            <button
              onClick={() => setCourseTab('active')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                courseTab === 'active'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              Активные ({activeCourses.length})
            </button>
            <button
              onClick={() => setCourseTab('completed')}
              className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                courseTab === 'completed'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300'
              }`}
            >
              Завершенные ({completedCourses.length})
            </button>
          </div>
        </div>

        {/* Курсы */}
        <div className="space-y-6">
          {displayCourses.map(course => {
            const progress = course.progress ?? 0
            const completed = course.completed_modules ?? 0
            const total = course.total_modules ?? 0
            const modules = course.modules ?? []

            return (
              <div key={course.id} className="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
                {/* Заголовок курса */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{course.title}</h2>
                        {course.certificate && (
                          <Badge variant="success">✓ Сертификат получен</Badge>
                        )}
                      </div>

                      {/* Прогресс */}
                      {total > 0 && (
                        <div className="max-w-xl">
                          <div className="flex justify-between items-center mb-2">
                            <span className="text-sm text-gray-600 dark:text-gray-400">Прогресс: {completed}/{total} модулей</span>
                            <span className="text-sm font-semibold text-indigo-600 dark:text-indigo-400">{progress}%</span>
                          </div>
                          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2 overflow-hidden">
                            <div
                              className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all progress-width"
                              style={{ '--progress-width': `${progress}%` } as React.CSSProperties}
                            />
                          </div>
                        </div>
                      )}

                      {/* Следующий урок */}
                      <div className="mt-4 text-sm text-gray-600 dark:text-gray-400">
                        {progress >= 100 ? (
                          <div className="flex items-center space-x-2">
                            <CheckCircle size={18} className="text-green-500" />
                            <span>Курс завершен!</span>
                          </div>
                        ) : course.next_lesson ? (
                          <>
                            <span>Следующий урок:</span>
                            <span className="font-semibold text-gray-900 dark:text-white"> {course.next_lesson}</span>
                          </>
                        ) : null}
                      </div>
                    </div>

                    {/* Действия */}
                    <div className="flex flex-col space-y-2">
                      {progress < 100 && (
                        <Button variant="secondary" size="sm">
                          <PlayCircle size={16} className="mr-2" />
                          Продолжить
                        </Button>
                      )}
                      {modules.length > 0 && (
                        <button
                          onClick={() => setExpandedCourse(expandedCourse === course.id ? null : course.id)}
                          className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors flex items-center justify-center space-x-2"
                        >
                          <span>Модули</span>
                          <ChevronDown
                            size={16}
                            className={`transition-transform ${expandedCourse === course.id ? 'rotate-180' : ''}`}
                          />
                        </button>
                      )}
                    </div>
                  </div>
                </div>

                {/* Модули */}
                {expandedCourse === course.id && modules.length > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-700">
                    <div className="p-6 space-y-4">
                      {modules.map(module => (
                        <div
                          key={module.id}
                          className={`p-4 rounded-lg border-2 transition-all ${
                            module.completed === module.lessons
                              ? 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-800'
                              : module.locked
                              ? 'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600'
                              : 'bg-indigo-50 dark:bg-indigo-900/10 border-indigo-200 dark:border-indigo-800'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-3">
                                {module.locked ? (
                                  <Lock size={20} className="text-gray-400" />
                                ) : module.completed === module.lessons ? (
                                  <CheckCircle size={20} className="text-green-500" />
                                ) : (
                                  <Target size={20} className="text-indigo-500" />
                                )}
                                <h3 className="font-semibold text-gray-900 dark:text-white">{module.title}</h3>
                              </div>
                              <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600 dark:text-gray-400">
                                <span className="flex items-center space-x-1">
                                  <Clock size={14} />
                                  <span>{module.duration}ч</span>
                                </span>
                                <span className="flex items-center space-x-1">
                                  <BarChart3 size={14} />
                                  <span>{module.lessons} уроков</span>
                                </span>
                                <span className="font-medium text-gray-900 dark:text-white">
                                  {module.completed}/{module.lessons} завершено
                                </span>
                              </div>
                            </div>

                            {!module.locked && module.lessons > 0 && (
                              <div className="ml-4">
                                <div className="w-16 h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                                  <div
                                    className="bg-green-500 h-full rounded-full transition-all progress-width"
                                    style={{ '--progress-width': `${(module.completed / module.lessons) * 100}%` } as React.CSSProperties}
                                  />
                                </div>
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )
          })}

          {displayCourses.length === 0 && (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-12 text-center">
              <BookOpen size={48} className="mx-auto text-gray-300 dark:text-gray-600 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                {courseTab === 'active' ? 'Нет активных курсов' : 'Нет завершенных курсов'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-6">
                {courseTab === 'active'
                  ? 'Начните изучение нового курса из нашего каталога'
                  : 'Вы пока не завершили ни одного курса'}
              </p>
              <Link href="/courses">
                <Button variant="secondary">
                  Просмотреть курсы
                </Button>
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
