'use client'

import { useState } from 'react'
import { Search, Filter, Star, Users, Clock, BarChart3, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface Course {
  id: number
  title: string
  description: string
  instructor: string
  price: number
  rating: number
  reviews: number
  students: number
  level: 'Начинающий' | 'Средний' | 'Продвинутый'
  duration: string
  modules: number
  image?: string
  tags: string[]
}

export default function CoursesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [sortBy, setSortBy] = useState<string>('popular')

  const mockCourses: Course[] = [
    {
      id: 1,
      title: 'React для профессионалов',
      description: 'Полный курс по современному React 18. Хуки, контекст, оптимизация производительности и лучшие практики.',
      instructor: 'Иван Петров',
      price: 2999,
      rating: 4.9,
      reviews: 842,
      students: 15420,
      level: 'Средний',
      duration: '40 часов',
      modules: 12,
      tags: ['React', 'JavaScript', 'Frontend']
    },
    {
      id: 2,
      title: 'TypeScript с нуля до мастера',
      description: 'Глубокое изучение TypeScript. Типы, интерфейсы, дженерики, типизация и промышленные практики.',
      instructor: 'Мария Сидорова',
      price: 1999,
      rating: 4.8,
      reviews: 623,
      students: 11230,
      level: 'Начинающий',
      duration: '35 часов',
      modules: 10,
      tags: ['TypeScript', 'JavaScript', 'Frontend']
    },
    {
      id: 3,
      title: 'Node.js и базы данных',
      description: 'Создание серверов на Node.js. Express, MongoDB, PostgreSQL, масштабирование приложений.',
      instructor: 'Алексей Иванов',
      price: 2499,
      rating: 4.7,
      reviews: 534,
      students: 9856,
      level: 'Средний',
      duration: '45 часов',
      modules: 14,
      tags: ['Node.js', 'Backend', 'Database']
    },
    {
      id: 4,
      title: 'Продвинутые паттерны React',
      description: 'Архитектурные паттерны, оптимизация кода, работа с большими приложениями и экосистемой.',
      instructor: 'Иван Петров',
      price: 3499,
      rating: 4.9,
      reviews: 421,
      students: 7640,
      level: 'Продвинутый',
      duration: '48 часов',
      modules: 15,
      tags: ['React', 'Advanced', 'Architecture']
    },
    {
      id: 5,
      title: 'Система дизайна в React',
      description: 'Создание масштабируемых компонентных библиотек. Storybook, темизация, документация.',
      instructor: 'Екатерина Лебедева',
      price: 2299,
      rating: 4.6,
      reviews: 312,
      students: 5421,
      level: 'Средний',
      duration: '32 часов',
      modules: 9,
      tags: ['React', 'Design Systems', 'UI/UX']
    },
    {
      id: 6,
      title: 'REST API и микросервисы',
      description: 'Проектирование и разработка REST API. Docker, микросервисная архитектура, мониторинг.',
      instructor: 'Дмитрий Волков',
      price: 2699,
      rating: 4.8,
      reviews: 289,
      students: 6234,
      level: 'Продвинутый',
      duration: '38 часов',
      modules: 11,
      tags: ['Backend', 'API', 'DevOps']
    },
    {
      id: 7,
      title: 'Next.js полный курс',
      description: 'Фреймворк Next.js для production-приложений. SSR, SSG, API роуты, деплой на Vercel.',
      instructor: 'Игорь Сметанин',
      price: 2799,
      rating: 4.7,
      reviews: 456,
      students: 8923,
      level: 'Средний',
      duration: '42 часов',
      modules: 13,
      tags: ['Next.js', 'React', 'Frontend']
    },
    {
      id: 8,
      title: 'GraphQL в production',
      description: 'Изучение GraphQL. Apollo Server, клиенты, оптимизация запросов, кеширование.',
      instructor: 'Ольга Русанова',
      price: 2399,
      rating: 4.5,
      reviews: 178,
      students: 3891,
      level: 'Продвинутый',
      duration: '36 часов',
      modules: 10,
      tags: ['GraphQL', 'Backend', 'API']
    },
    {
      id: 9,
      title: 'Тестирование на Jest и React Testing Library',
      description: 'Unit тесты, интеграционные тесты, E2E тестирование. Лучшие практики тестирования.',
      instructor: 'Павел Морозов',
      price: 1899,
      rating: 4.6,
      reviews: 267,
      students: 4156,
      level: 'Средний',
      duration: '28 часов',
      modules: 8,
      tags: ['Testing', 'JavaScript', 'Quality']
    },
    {
      id: 10,
      title: 'AWS и облачные технологии',
      description: 'Деплой приложений на AWS. EC2, S3, Lambda, RDS, мониторинг и масштабирование.',
      instructor: 'Станислав Кузнецов',
      price: 2899,
      rating: 4.7,
      reviews: 298,
      students: 5672,
      level: 'Продвинутый',
      duration: '44 часов',
      modules: 12,
      tags: ['AWS', 'DevOps', 'Cloud']
    },
    {
      id: 11,
      title: 'Vanilla JavaScript для фронтенда',
      description: 'Фундамент веб-разработки. DOM, события, асинхронность, прототипы и классы.',
      instructor: 'Евгений Рыжов',
      price: 1499,
      rating: 4.8,
      reviews: 1203,
      students: 22341,
      level: 'Начинающий',
      duration: '30 часов',
      modules: 9,
      tags: ['JavaScript', 'Frontend', 'Basics']
    },
    {
      id: 12,
      title: 'Vue.js 3 - полный путь',
      description: 'Полный курс по Vue 3. Composition API, Pinia, Vue Router, интеграция с бэкендом.',
      instructor: 'Юлия Козлова',
      price: 2199,
      rating: 4.6,
      reviews: 389,
      students: 6789,
      level: 'Начинающий',
      duration: '38 часов',
      modules: 11,
      tags: ['Vue.js', 'JavaScript', 'Frontend']
    }
  ]

  // Фильтрация
  const filteredCourses = mockCourses.filter(course => {
    const matchSearch = course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       course.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchLevel = selectedLevel === 'all' || course.level === selectedLevel
    const matchCategory = selectedCategory === 'all' || course.tags.includes(selectedCategory)
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
        return b.students - a.students
      default:
        return b.students - a.students
    }
  })

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'Начинающий':
        return 'success'
      case 'Средний':
        return 'info'
      case 'Продвинутый':
        return 'danger'
      default:
        return 'default'
    }
  }

  const categories = ['React', 'Node.js', 'JavaScript', 'TypeScript', 'Frontend', 'Backend']
  const levels = ['Начинающий', 'Средний', 'Продвинутый']

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Каталог курсов</h1>
          <p className="text-indigo-100 text-lg max-w-2xl">
            Более {mockCourses.length} качественных курсов от опытных менторов. Изучайте в своем темпе.
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
                  <option key={level} value={level}>{level}</option>
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
                <option value="students">По количеству студентов</option>
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
                    <Badge variant={getLevelColor(course.level)}>
                      {course.level}
                    </Badge>
                  </div>

                  {/* Заголовок */}
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {course.title}
                  </h3>

                  {/* Инструктор */}
                  <p className="text-sm text-gray-600 mb-3">
                    👨‍🏫 {course.instructor}
                  </p>

                  {/* Описание */}
                  <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                    {course.description}
                  </p>

                  {/* Теги */}
                  <div className="flex flex-wrap gap-1 mb-4">
                    {course.tags.slice(0, 3).map((tag: string) => (
                      <span
                        key={tag}
                        className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>

                  {/* Информация */}
                  <div className="grid grid-cols-2 gap-3 mb-4 py-4 border-y border-gray-200">
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Clock size={16} />
                      <span>{course.duration}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <BarChart3 size={16} />
                      <span>{course.modules} модулей</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Star size={16} className="fill-amber-400 text-amber-400" />
                      <span className="font-semibold">{course.rating}</span>
                      <span className="text-gray-500">({course.reviews})</span>
                    </div>
                    <div className="flex items-center space-x-2 text-sm text-gray-600">
                      <Users size={16} />
                      <span>{(course.students / 1000).toFixed(1)}k студентов</span>
                    </div>
                  </div>

                  {/* Цена и кнопка */}
                  <div className="flex items-center justify-between">
                    <p className="text-2xl font-bold text-indigo-600">
                      {course.price.toLocaleString('ru-RU')}₽
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