'use client'

import { useState } from 'react'
import {
  BookOpen, CheckCircle, Clock, BarChart3, PlayCircle, Lock,
  ChevronDown, Award, Target, TrendingUp
} from 'lucide-react'
import Link from 'next/link'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Tabs from '@/components/ui/Tabs'

interface Module {
  id: number
  title: string
  duration: number
  lessons: number
  completed: number
  locked: boolean
}

interface Course {
  id: number
  title: string
  progress: number
  completed: number
  total: number
  modules: Module[]
  completedAt?: string
  nextLesson?: string
  certificate?: boolean
}

export default function LearningPage() {
  const [activeTab, setActiveTab] = useState('active')
  const [expandedCourse, setExpandedCourse] = useState<number | null>(null)

  const mockCourses: Course[] = [
    {
      id: 1,
      title: 'React для профессионалов',
      progress: 65,
      completed: 8,
      total: 12,
      nextLesson: 'Продвинутые хуки',
      modules: [
        { id: 1, title: 'Введение в React', duration: 3.5, lessons: 5, completed: 5, locked: false },
        { id: 2, title: 'JSX и компоненты', duration: 4.2, lessons: 6, completed: 5, locked: false },
        { id: 3, title: 'Состояние и пропсы', duration: 3.8, lessons: 5, completed: 3, locked: false },
        { id: 4, title: 'Хуки', duration: 5.0, lessons: 7, completed: 0, locked: true },
        { id: 5, title: 'Context API', duration: 4.5, lessons: 6, completed: 0, locked: true }
      ]
    },
    {
      id: 2,
      title: 'TypeScript с нуля до мастера',
      progress: 42,
      completed: 4,
      total: 10,
      nextLesson: 'Дженерики',
      modules: [
        { id: 1, title: 'Основы типизации', duration: 3.0, lessons: 4, completed: 4, locked: false },
        { id: 2, title: 'Типы и интерфейсы', duration: 4.0, lessons: 5, completed: 0, locked: true },
        { id: 3, title: 'Классы и дженерики', duration: 5.0, lessons: 7, completed: 0, locked: true }
      ]
    },
    {
      id: 3,
      title: 'Node.js и базы данных',
      progress: 100,
      completed: 14,
      total: 14,
      completedAt: '2025-11-15',
      certificate: true,
      nextLesson: 'Завершено!',
      modules: [
        { id: 1, title: 'Основы Node.js', duration: 4.0, lessons: 5, completed: 5, locked: false },
        { id: 2, title: 'Express.js', duration: 5.0, lessons: 7, completed: 7, locked: false },
        { id: 3, title: 'MongoDB', duration: 4.5, lessons: 6, completed: 6, locked: false }
      ]
    }
  ]

  const completedCourses = mockCourses.filter(c => c.progress === 100)
  const activeCourses = mockCourses.filter(c => c.progress < 100)

  const displayCourses = activeTab === 'active' ? activeCourses : completedCourses

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Мои обучение</h1>
          <p className="text-indigo-100 text-lg">
            Продолжайте учиться и достигайте новых навыков
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
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
                <p className="text-sm text-gray-600">Активных курсов</p>
                <p className="text-2xl font-bold text-gray-900">{activeCourses.length}</p>
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
                <p className="text-sm text-gray-600">Завершено</p>
                <p className="text-2xl font-bold text-gray-900">{completedCourses.length}</p>
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
                <p className="text-sm text-gray-600">Сертификатов</p>
                <p className="text-2xl font-bold text-gray-900">{completedCourses.filter(c => c.certificate).length}</p>
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
                <p className="text-sm text-gray-600">Часов обучения</p>
                <p className="text-2xl font-bold text-gray-900">126</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Табы */}
        <Tabs
          tabs={[
            { id: 'active', label: `Активные (${activeCourses.length})`, count: activeCourses.length },
            { id: 'completed', label: `Завершенные (${completedCourses.length})`, count: completedCourses.length }
          ]}
          activeTab={activeTab}
          onChange={setActiveTab}
          className="mb-8"
        />

        {/* Курсы */}
        <div className="space-y-6">
          {displayCourses.map(course => (
            <div key={course.id} className="bg-white rounded-lg shadow overflow-hidden">
              {/* Заголовок курса */}
              <div className="p-6 border-b border-gray-200">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <h2 className="text-2xl font-bold text-gray-900">{course.title}</h2>
                      {course.certificate && (
                        <Badge variant="success">✓ Сертификат получен</Badge>
                      )}
                    </div>

                    {/* Прогресс */}
                    <div className="max-w-xl">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-sm text-gray-600">Прогресс: {course.completed}/{course.total} модулей</span>
                        <span className="text-sm font-semibold text-indigo-600">{course.progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden">
                        <div
                          className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all progress-width"
                          style={{ '--progress-width': `${course.progress}%` } as React.CSSProperties}
                        />
                      </div>
                    </div>

                    {/* Следующий урок */}
                    <div className="mt-4 text-sm text-gray-600">
                      {course.nextLesson === 'Завершено!' ? (
                        <div className="flex items-center space-x-2">
                          <CheckCircle size={18} className="text-green-500" />
                          <span>Курс завершен!</span>
                        </div>
                      ) : (
                        <>
                          <span>Следующий урок:</span>
                          <span className="font-semibold text-gray-900"> {course.nextLesson}</span>
                        </>
                      )}
                    </div>
                  </div>

                  {/* Действия */}
                  <div className="flex flex-col space-y-2">
                    {course.progress < 100 && (
                      <Button variant="primary" size="sm">
                        <PlayCircle size={16} className="mr-2" />
                        Продолжить
                      </Button>
                    )}
                    <button
                      onClick={() => setExpandedCourse(expandedCourse === course.id ? null : course.id)}
                      className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors flex items-center justify-center space-x-2"
                    >
                      <span>Модули</span>
                      <ChevronDown
                        size={16}
                        className={`transition-transform ${expandedCourse === course.id ? 'rotate-180' : ''}`}
                      />
                    </button>
                  </div>
                </div>
              </div>

              {/* Модули */}
              {expandedCourse === course.id && (
                <div className="border-t border-gray-200">
                  <div className="p-6 space-y-4">
                    {course.modules.map(module => (
                      <div
                        key={module.id}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          module.completed === module.lessons
                            ? 'bg-green-50 border-green-200'
                            : module.locked
                            ? 'bg-gray-50 border-gray-200'
                            : 'bg-indigo-50 border-indigo-200'
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
                              <h3 className="font-semibold text-gray-900">{module.title}</h3>
                            </div>
                            <div className="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                              <span className="flex items-center space-x-1">
                                <Clock size={14} />
                                <span>{module.duration}ч</span>
                              </span>
                              <span className="flex items-center space-x-1">
                                <BarChart3 size={14} />
                                <span>{module.lessons} уроков</span>
                              </span>
                              <span className="font-medium text-gray-900">
                                {module.completed}/{module.lessons} завершено
                              </span>
                            </div>
                          </div>

                          {!module.locked && (
                            <div className="ml-4">
                              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
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
          ))}

          {displayCourses.length === 0 && (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <BookOpen size={48} className="mx-auto text-gray-300 mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {activeTab === 'active' ? 'Нет активных курсов' : 'Нет завершенных курсов'}
              </h3>
              <p className="text-gray-600 mb-6">
                {activeTab === 'active'
                  ? 'Начните изучение нового курса из нашего каталога'
                  : 'Завершите курсы для получения сертификатов'}
              </p>
              <Link href="/courses">
                <Button variant="primary">
                  Просмотреть курсы
                </Button>
              </Link>
            </div>
          )}
        </div>

        {/* Рекомендации */}
        {activeTab === 'active' && (
          <div className="mt-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Рекомендованные курсы</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {[
                {
                  title: 'Advanced React Patterns',
                  description: 'Углубленное изучение паттернов React',
                  level: 'Продвинутый'
                },
                {
                  title: 'Web Performance',
                  description: 'Оптимизация производительности веб-приложений',
                  level: 'Продвинутый'
                },
                {
                  title: 'Testing Best Practices',
                  description: 'Лучшие практики тестирования кода',
                  level: 'Средний'
                }
              ].map((rec, i) => (
                <Card key={i}>
                  <Badge variant="info" className="mb-3">Рекомендуется</Badge>
                  <h3 className="font-semibold text-gray-900 mb-2">{rec.title}</h3>
                  <p className="text-sm text-gray-600 mb-4">{rec.description}</p>
                  <div className="flex items-center justify-between">
                    <Badge variant={rec.level === 'Продвинутый' ? 'danger' : 'success'}>
                      {rec.level}
                    </Badge>
                    <Button variant="primary" size="sm">
                      Подробнее
                    </Button>
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}