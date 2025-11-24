'use client'

import { useState } from 'react'
import { Search, Filter, BookOpen, FileText, Video, Headphones, Star, Download, Share2 } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface Resource {
  id: number
  title: string
  description: string
  category: 'book' | 'article' | 'video' | 'podcast'
  author: string
  rating: number
  reviews: number
  downloads?: number
  duration?: string
  language: string
  level: string
  tags: string[]
  url?: string
}

export default function ResourcesPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  const [selectedLevel, setSelectedLevel] = useState<string>('all')

  const mockResources: Resource[] = [
    // Книги
    {
      id: 1,
      title: 'You Don\'t Know JS Yet',
      description: 'Глубокое погружение в JavaScript. Полное руководство для профессионалов.',
      category: 'book',
      author: 'Kyle Simpson',
      rating: 4.9,
      reviews: 2341,
      downloads: 15420,
      language: 'English',
      level: 'Средний',
      tags: ['JavaScript', 'Web Development', 'Best Practice']
    },
    {
      id: 2,
      title: 'Чистый код',
      description: 'Как писать красивый и поддерживаемый код. Советы от лучшего разработчика.',
      category: 'book',
      author: 'Robert C. Martin',
      rating: 4.8,
      reviews: 1823,
      downloads: 12300,
      language: 'Русский',
      level: 'Продвинутый',
      tags: ['Code Quality', 'Best Practice', 'Architecture']
    },
    {
      id: 3,
      title: 'The Pragmatic Programmer',
      description: 'Практические советы по программированию. Инструменты и техники опытных разработчиков.',
      category: 'book',
      author: 'Andrew Hunt',
      rating: 4.7,
      reviews: 1645,
      downloads: 9876,
      language: 'English',
      level: 'Продвинутый',
      tags: ['Programming', 'Best Practice', 'Career']
    },
    {
      id: 4,
      title: 'Структуры данных и алгоритмы',
      description: 'Полное руководство по алгоритмам и структурам данных для решения сложных задач.',
      category: 'book',
      author: 'Mark Allen Weiss',
      rating: 4.6,
      reviews: 1456,
      downloads: 8234,
      language: 'Русский',
      level: 'Продвинутый',
      tags: ['Algorithms', 'Data Structures', 'Interview']
    },
    {
      id: 5,
      title: 'Design Patterns',
      description: 'Паттерны проектирования. 23 проверенных решения для архитектуры.',
      category: 'book',
      author: 'Gang of Four',
      rating: 4.5,
      reviews: 1234,
      downloads: 7654,
      language: 'English',
      level: 'Продвинутый',
      tags: ['Design Patterns', 'Architecture', 'OOP']
    },
    {
      id: 6,
      title: 'React in Action',
      description: 'Практическое руководство по созданию приложений на React. Реальные примеры.',
      category: 'book',
      author: 'Mark Thomas',
      rating: 4.7,
      reviews: 987,
      downloads: 6543,
      language: 'English',
      level: 'Средний',
      tags: ['React', 'JavaScript', 'Frontend']
    },
    // Статьи
    {
      id: 7,
      title: 'Как оптимизировать производительность React',
      description: 'Детальное руководство по оптимизации производительности React приложений.',
      category: 'article',
      author: 'Dan Abramov',
      rating: 4.8,
      reviews: 2145,
      language: 'Русский',
      level: 'Средний',
      tags: ['React', 'Performance', 'Optimization']
    },
    {
      id: 8,
      title: 'SOLID принципы в JavaScript',
      description: 'Применение SOLID принципов при разработке JavaScript приложений.',
      category: 'article',
      author: 'Uncle Bob',
      rating: 4.6,
      reviews: 1876,
      language: 'Русский',
      level: 'Продвинутый',
      tags: ['JavaScript', 'SOLID', 'Best Practice']
    },
    {
      id: 9,
      title: 'TypeScript для начинающих',
      description: 'Полное введение в TypeScript для разработчиков JavaScript.',
      category: 'article',
      author: 'Boris Cherny',
      rating: 4.7,
      reviews: 1654,
      language: 'Русский',
      level: 'Начинающий',
      tags: ['TypeScript', 'JavaScript', 'Type Safety']
    },
    {
      id: 10,
      title: 'Асинхронное программирование в JavaScript',
      description: 'Глубокое изучение Promises, async/await и Event Loop.',
      category: 'article',
      author: 'Jake Archibald',
      rating: 4.8,
      reviews: 1532,
      language: 'Русский',
      level: 'Средний',
      tags: ['JavaScript', 'Async', 'Advanced']
    },
    {
      id: 11,
      title: 'Что нового в ES2024',
      description: 'Обзор новых возможностей ECMAScript 2024.',
      category: 'article',
      author: 'Axel Rauschmayer',
      rating: 4.5,
      reviews: 1123,
      language: 'Русский',
      level: 'Средний',
      tags: ['JavaScript', 'ES2024', 'New Features']
    },
    {
      id: 12,
      title: 'API Design Best Practices',
      description: 'Как проектировать правильные REST и GraphQL API.',
      category: 'article',
      author: 'Kin Lane',
      rating: 4.7,
      reviews: 987,
      language: 'English',
      level: 'Продвинутый',
      tags: ['API', 'REST', 'GraphQL']
    },
    // Видео
    {
      id: 13,
      title: 'JavaScript в одном видео',
      description: 'Полный курс JavaScript за один час. От основ до продвинутых тем.',
      category: 'video',
      author: 'Traversy Media',
      rating: 4.9,
      reviews: 5432,
      duration: '1h 15m',
      language: 'English',
      level: 'Начинающий',
      tags: ['JavaScript', 'Tutorial', 'Beginner']
    },
    {
      id: 14,
      title: 'Web Performance Optimization',
      description: 'Видеоурок по оптимизации производительности веб-приложений.',
      category: 'video',
      author: 'Steve Souders',
      rating: 4.8,
      reviews: 3421,
      duration: '45m',
      language: 'English',
      level: 'Продвинутый',
      tags: ['Performance', 'Web', 'Optimization']
    },
    {
      id: 15,
      title: 'React Hooks в глубину',
      description: 'Детальное объяснение всех React Hooks с примерами.',
      category: 'video',
      author: 'Kent C. Dodds',
      rating: 4.9,
      reviews: 4123,
      duration: '2h 30m',
      language: 'English',
      level: 'Средний',
      tags: ['React', 'Hooks', 'Advanced']
    },
    {
      id: 16,
      title: 'CSS Grid и Flexbox мастер-класс',
      description: 'Освоите современные техники layout с CSS Grid и Flexbox.',
      category: 'video',
      author: 'Wes Bos',
      rating: 4.8,
      reviews: 2876,
      duration: '1h 45m',
      language: 'English',
      level: 'Начинающий',
      tags: ['CSS', 'Layout', 'Frontend']
    },
    {
      id: 17,
      title: 'Node.js для начинающих',
      description: 'Полное введение в Node.js и Express. Создание серверов.',
      category: 'video',
      author: 'The Net Ninja',
      rating: 4.7,
      reviews: 3654,
      duration: '3h',
      language: 'English',
      level: 'Начинающий',
      tags: ['Node.js', 'Backend', 'Express']
    },
    {
      id: 18,
      title: 'Docker для разработчиков',
      description: 'Видеокурс по Docker для упаковки и развертывания приложений.',
      category: 'video',
      author: 'Sanjeev Thakur',
      rating: 4.6,
      reviews: 1987,
      duration: '2h 20m',
      language: 'English',
      level: 'Продвинутый',
      tags: ['Docker', 'DevOps', 'Deployment']
    },
    // Подкасты
    {
      id: 19,
      title: 'The Changelog Podcast',
      description: 'Еженедельный подкаст о новом в мире open-source и разработки.',
      category: 'podcast',
      author: 'Changelog Media',
      rating: 4.7,
      reviews: 876,
      duration: '1h 20m',
      language: 'English',
      level: 'Средний',
      tags: ['Podcast', 'News', 'Open Source']
    },
    {
      id: 20,
      title: 'JavaScript Jabber',
      description: 'Подкаст для JavaScript разработчиков. Обсуждение тенденций и инструментов.',
      category: 'podcast',
      author: 'DevChat.tv',
      rating: 4.6,
      reviews: 654,
      duration: '1h',
      language: 'English',
      level: 'Средний',
      tags: ['JavaScript', 'Podcast', 'Discussion']
    },
    {
      id: 21,
      title: 'Software Engineering Daily',
      description: 'Ежедневные интервью с инженерами о новых технологиях.',
      category: 'podcast',
      author: 'Jeff Meyerson',
      rating: 4.8,
      reviews: 1234,
      duration: '45m',
      language: 'English',
      level: 'Продвинутый',
      tags: ['Technology', 'Podcast', 'Interview']
    },
    {
      id: 22,
      title: 'Syntax - веб-разработка',
      description: 'Подкаст о веб-разработке, фреймворках и лучших практиках.',
      category: 'podcast',
      author: 'Wes Bos & Scott Tolinski',
      rating: 4.9,
      reviews: 2456,
      duration: '50m',
      language: 'English',
      level: 'Начинающий',
      tags: ['Web Development', 'Podcast', 'Tutorial']
    },
    {
      id: 23,
      title: 'React Podcast',
      description: 'Подкаст, посвященный React, его экосистеме и сообществу.',
      category: 'podcast',
      author: 'Chantastic',
      rating: 4.7,
      reviews: 876,
      duration: '1h 10m',
      language: 'English',
      level: 'Средний',
      tags: ['React', 'Podcast', 'Community']
    },
    {
      id: 24,
      title: 'The Backend Engineering Show',
      description: 'Подкаст о backend разработке, архитектуре и масштабировании.',
      category: 'podcast',
      author: 'Hussein Nasser',
      rating: 4.8,
      reviews: 1123,
      duration: '55m',
      language: 'English',
      level: 'Продвинутый',
      tags: ['Backend', 'Podcast', 'Architecture']
    }
  ]

  // Фильтрация
  const filteredResources = mockResources.filter(resource => {
    const matchSearch = resource.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                       resource.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchCategory = selectedCategory === 'all' || resource.category === selectedCategory
    const matchLevel = selectedLevel === 'all' || resource.level === selectedLevel
    return matchSearch && matchCategory && matchLevel
  })

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'book':
        return 'info'
      case 'article':
        return 'success'
      case 'video':
        return 'danger'
      case 'podcast':
        return 'warning'
      default:
        return 'default'
    }
  }

  const getCategoryLabel = (category: string) => {
    switch (category) {
      case 'book':
        return '📚 Книга'
      case 'article':
        return '📝 Статья'
      case 'video':
        return '🎥 Видео'
      case 'podcast':
        return '🎧 Подкаст'
      default:
        return 'Ресурс'
    }
  }

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'book':
        return <BookOpen size={20} />
      case 'article':
        return <FileText size={20} />
      case 'video':
        return <Video size={20} />
      case 'podcast':
        return <Headphones size={20} />
      default:
        return <BookOpen size={20} />
    }
  }

  const categories = [
    { id: 'all', label: 'Все' },
    { id: 'book', label: '📚 Книги' },
    { id: 'article', label: '📝 Статьи' },
    { id: 'video', label: '🎥 Видео' },
    { id: 'podcast', label: '🎧 Подкасты' }
  ]

  const levels = ['Начинающий', 'Средний', 'Продвинутый']

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Ресурсы обучения</h1>
          <p className="text-indigo-100 text-lg">
            Книги, статьи, видео и подкасты для улучшения ваших навыков
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Поиск и фильтры */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          {/* Поиск */}
          <div className="mb-6">
            <div className="relative">
              <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
              <input
                type="text"
                title="Поиск ресурсов"
                placeholder="Поиск по названию или описанию..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Фильтры */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Категория */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Тип ресурса</label>
              <div className="flex flex-wrap gap-2">
                {categories.map(cat => (
                  <button
                    key={cat.id}
                    onClick={() => setSelectedCategory(cat.id)}
                    title={cat.label}
                    className={`px-3 py-2 text-xs font-medium rounded-lg transition-colors ${
                      selectedCategory === cat.id
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {cat.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Уровень */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-2">Уровень сложности</label>
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
          </div>

          {/* Результаты */}
          <div className="mt-4 text-sm text-gray-600">
            Найдено ресурсов: <span className="font-semibold text-gray-900">{filteredResources.length}</span>
          </div>
        </div>

        {/* Сетка ресурсов */}
        {filteredResources.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredResources.map(resource => (
              <Card key={resource.id} className="hover:shadow-lg transition-shadow">
                {/* Категория */}
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2 text-indigo-600">
                    {getCategoryIcon(resource.category)}
                    <Badge variant={getCategoryColor(resource.category)}>
                      {getCategoryLabel(resource.category)}
                    </Badge>
                  </div>
                  {resource.level && (
                    <Badge variant={resource.level === 'Продвинутый' ? 'danger' : resource.level === 'Средний' ? 'info' : 'success'}>
                      {resource.level}
                    </Badge>
                  )}
                </div>

                {/* Заголовок и автор */}
                <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                  {resource.title}
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  👤 {resource.author}
                </p>

                {/* Описание */}
                <p className="text-sm text-gray-600 mb-4 line-clamp-2">
                  {resource.description}
                </p>

                {/* Мета информация */}
                <div className="space-y-2 mb-4 pb-4 border-b border-gray-200">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">Язык:</span>
                    <span className="font-medium text-gray-900">{resource.language}</span>
                  </div>
                  {resource.duration && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Длительность:</span>
                      <span className="font-medium text-gray-900">{resource.duration}</span>
                    </div>
                  )}
                  {resource.downloads && (
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Загрузок:</span>
                      <span className="font-medium text-gray-900">{(resource.downloads / 1000).toFixed(1)}k</span>
                    </div>
                  )}
                </div>

                {/* Теги */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {resource.tags.slice(0, 3).map(tag => (
                    <span key={tag} className="px-2 py-1 bg-indigo-50 text-indigo-600 text-xs font-medium rounded">
                      {tag}
                    </span>
                  ))}
                </div>

                {/* Рейтинг и действия */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="flex items-center space-x-1">
                    <Star size={16} className="fill-amber-400 text-amber-400" />
                    <span className="font-semibold text-gray-900">{resource.rating}</span>
                    <span className="text-xs text-gray-500">({resource.reviews})</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      title="Поделиться"
                      className="p-2 text-gray-400 hover:text-indigo-600 transition-colors"
                    >
                      <Share2 size={16} />
                    </button>
                    <button
                      title="Скачать/Открыть"
                      className="p-2 text-gray-400 hover:text-indigo-600 transition-colors"
                    >
                      <Download size={16} />
                    </button>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-12 text-center">
            <Filter size={48} className="mx-auto text-gray-300 mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Ресурсы не найдены</h3>
            <p className="text-gray-600">
              Попробуйте изменить фильтры или поисковый запрос
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
