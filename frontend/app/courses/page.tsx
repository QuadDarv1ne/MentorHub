'use client'

import { useState, useEffect } from 'react'
import { Search, Filter, Star, Users, Clock, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { getCourses, type Course } from '@/lib/api/courses'

export default function CoursesPage() {
  const [courses, setCourses] = useState<Course[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('popular')

  // Fetch courses from API
  useEffect(() => {
    const fetchCourses = async () => {
      try {
        const data = await getCourses(0, 100)
        setCourses(data)
        setLoading(false)
      } catch (err) {
        console.error('Failed to fetch courses:', err)
        setError('Не удалось загрузить курсы. Пожалуйста, попробуйте позже.')
        setLoading(false)
      }
    }

    fetchCourses()
  }, [])

  // Фильтрация
  const filteredCourses = courses.filter(course => {
    const matchSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       (course.description && course.description.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchLevel = selectedLevel === 'all' || (course.difficulty && course.difficulty === selectedLevel)
    const matchCategory = selectedCategory === 'all' || (course.category && course.category === selectedCategory)
    return matchSearch && matchLevel && matchCategory
  })

  // Сортировка
  const sortedCourses = [...filteredCourses].sort((a, b) => {
    switch (sortBy) {
      case 'price-low':
        return a.price - b.price
      case 'price-high':
        return b.price - a.price
      case 'rating':
        return b.rating - a.rating
      case 'students':
        return b.total_reviews - a.total_reviews
      default:
        return b.total_reviews - a.total_reviews
    }
  })

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'success'
      case 'intermediate':
        return 'info'
      case 'advanced':
        return 'danger'
      default:
        return 'default'
    }
  }

  const getLevelLabel = (level: string) => {
    switch (level) {
      case 'beginner':
        return 'Начинающий'
      case 'intermediate':
        return 'Средний'
      case 'advanced':
        return 'Продвинутый'
      default:
        return level
    }
  }

  const categories = Array.from(new Set(courses.map(course => course.category).filter(Boolean))) as string[]
  const levels = Array.from(new Set(courses.map(course => course.difficulty).filter(Boolean))) as string[]

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
          <div className="max-w-7xl mx-auto">
            <div className="h-10 bg-white/20 rounded animate-pulse mb-4"></div>
            <div className="h-6 bg-white/20 rounded animate-pulse w-2/3"></div>
          </div>
        </div>
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="h-12 bg-gray-200 rounded-lg animate-pulse mb-6"></div>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-16 bg-gray-200 rounded-lg animate-pulse"></div>
              ))}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-white rounded-lg shadow animate-pulse h-96"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow p-8 max-w-md text-center">
          <div className="text-red-500 text-5xl mb-4">⚠️</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Ошибка загрузки</h3>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
          >
            Повторить попытку
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Каталог курсов</h1>
          <p className="text-indigo-100 text-lg max-w-2xl">
            Более {courses.length} качественных курсов от опытных менторов. Изучайте в своем темпе.
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Поиск и фильтры */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          {/* Поисковая строка */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                title="Поиск курсов"
                placeholder="Поиск по названию или описанию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Фильтры и сортировка */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            {/* Уровень */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Уровень</label>
              <select
                title="Выберите уровень"
                value={selectedLevel}
                onChange={(e) => setSelectedLevel(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Все уровни</option>
                {levels.map(level => (
                  <option key={level} value={level}>{getLevelLabel(level)}</option>
                ))}
              </select>
            </div>

            {/* Категория */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Категория</label>
              <select
                title="Выберите категорию"
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="all">Все категории</option>
                {categories.map(cat => (
                  <option key={cat} value={cat}>{cat}</option>
                ))}
              </select>
            </div>

            {/* Сортировка */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Сортировка</label>
              <select
                title="Выберите сортировку"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="popular">По популярности</option>
                <option value="price-low">Цена: от меньшей к большей</option>
                <option value="price-high">Цена: от большей к меньшей</option>
                <option value="rating">По рейтингу</option>
                <option value="students">По количеству отзывов</option>
              </select>
            </div>
          </div>

          {/* Результаты */}
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>Найдено курсов: <span className="font-semibold text-gray-900">{sortedCourses.length}</span></span>
          </div>
        </div>

        {/* Сетка курсов */}
        {sortedCourses.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {sortedCourses.map((course: Course) => (
              <Link key={course.id} href={`/courses/${course.id}`}>
                <Card className="h-full hover:shadow-lg transition-shadow cursor-pointer">
                  {/* Уровень */}
                  <div className="mb-3">
                    {course.difficulty && (
                      <Badge variant={getLevelColor(course.difficulty)}>
                        {getLevelLabel(course.difficulty)}
                      </Badge>
                    )}
                  </div>

                  {/* Заголовок */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {course.title}
                  </h3>

                  {/* Инструктор */}
                  <p className="text-sm text-gray-600 mb-3">
                    👨‍🏫 {course.instructor?.full_name || 'Инструктор'}
                  </p>

                  {/* Описание */}
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {course.description || 'Описание курса отсутствует'}
                  </p>

                  {/* Категория */}
                  {course.category && (
                    <div className="flex flex-wrap gap-1 mb-4">
                      <span className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded">
                        {course.category}
                      </span>
                    </div>
                  )}

                  {/* Информация */}
                  <div className="grid grid-cols-2 gap-3 mb-4 py-4 border-y border-gray-200">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock size={16} />
                      <span>{course.duration_hours} часов</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Star size={16} className="fill-amber-400 text-amber-400" />
                      <span className="font-semibold">{course.rating.toFixed(1)}</span>
                      <span className="text-gray-500">({course.total_reviews})</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Users size={16} />
                      <span>{course.total_reviews} отзывов</span>
                    </div>
                  </div>

                  {/* Цена и кнопка */}
                  <div className="flex items-center justify-between">
                    <p className="text-2xl font-bold text-indigo-600">
                      {(course.price / 100).toLocaleString('ru-RU')}₽
                    </p>
                    <ChevronRight size={20} className="text-gray-400" />
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Filter size={48} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Курсы не найдены</h3>
            <p className="text-gray-600">
              Попробуйте изменить фильтры или поисковый запрос
            </p>
          </div>
        )}
      </div>
    </div>
  )
}