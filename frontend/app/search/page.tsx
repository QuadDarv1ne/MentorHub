'use client'

import { useState, useEffect, useMemo } from 'react'
import { Search, X, Filter, ChevronRight } from 'lucide-react'
import Link from 'next/link'
import Badge from '@/components/ui/Badge'

interface SearchResult {
  id: string
  title: string
  description: string
  type: 'mentor' | 'course' | 'article' | 'question'
  rating?: number
  price?: number
  tags?: string[]
  url: string
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [filterType, setFilterType] = useState<'all' | 'mentor' | 'course' | 'article' | 'question'>('all')

  const mockData = useMemo<SearchResult[]>(() => [
    {
      id: '1',
      title: 'Иван Петров - React Expert',
      description: 'Опытный фронтенд разработчик с 8+ годами опыта. Специализируется на React и современном стеке.',
      type: 'mentor',
      rating: 4.9,
      price: 1500,
      tags: ['React', 'JavaScript', 'Web Development'],
      url: '/mentors/1'
    },
    {
      id: '2',
      title: 'Advanced React Patterns',
      description: 'Полный курс по продвинутым паттернам React. Включает хуки, контекст и оптимизацию производительности.',
      type: 'course',
      tags: ['React', 'Frontend'],
      url: '/courses/1'
    },
    {
      id: '3',
      title: 'Как подготовиться к собеседованию',
      description: 'Практический гайд по подготовке к техническому интервью. Советы по алгоритмам и системному дизайну.',
      type: 'article',
      tags: ['Interview', 'Career'],
      url: '/blog/interview-prep'
    },
    {
      id: '4',
      title: 'Мария Сидорова - Node.js Mentor',
      description: 'Бэкенд разработчик специалист по Node.js и базам данных. 6+ лет опыта.',
      type: 'mentor',
      rating: 4.8,
      price: 1200,
      tags: ['Node.js', 'Backend', 'MongoDB'],
      url: '/mentors/2'
    },
    {
      id: '5',
      title: 'TypeScript для профессионалов',
      description: 'Глубокое погружение в TypeScript. Типы, интерфейсы, дженерики и типизация.',
      type: 'course',
      tags: ['TypeScript', 'JavaScript'],
      url: '/courses/2'
    },
    {
      id: '6',
      title: 'SQL оптимизация: практическое руководство',
      description: 'Узнайте как писать эффективные SQL запросы. Индексы, запросы, транзакции.',
      type: 'question',
      tags: ['SQL', 'Database'],
      url: '/sql-questions/1'
    },
    {
      id: '7',
      title: 'Алексей Иванов - Full Stack Developer',
      description: 'Full stack разработчик с опытом в React, Node.js и облачных технологиях. 7+ лет в IT.',
      type: 'mentor',
      rating: 4.7,
      price: 1800,
      tags: ['React', 'Node.js', 'AWS'],
      url: '/mentors/3'
    },
    {
      id: '8',
      title: 'Система дизайн практика в React',
      description: 'Создание масштабируемых систем дизайна с React. Компоненты, темы, документация.',
      type: 'course',
      tags: ['React', 'Design', 'Frontend'],
      url: '/courses/3'
    }
  ]
  , [])

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      return
    }

    setLoading(true)
    const timer = setTimeout(() => {
      const filtered = mockData.filter((item: SearchResult) => {
        const matchQuery = item.title.toLowerCase().includes(query.toLowerCase()) ||
                          item.description.toLowerCase().includes(query.toLowerCase())
        const matchType = filterType === 'all' || item.type === filterType
        return matchQuery && matchType
      })
      setResults(filtered)
      setLoading(false)
    }, 300)

    return () => clearTimeout(timer)
  }, [query, filterType, mockData])

  const getTypeColor = (type: SearchResult['type']) => {
    switch (type) {
      case 'mentor':
        return 'info'
      case 'course':
        return 'success'
      case 'article':
        return 'warning'
      case 'question':
        return 'danger'
      default:
        return 'default'
    }
  }

  const getTypeLabel = (type: SearchResult['type']) => {
    switch (type) {
      case 'mentor':
        return '👨‍💼 Ментор'
      case 'course':
        return '📚 Курс'
      case 'article':
        return '📝 Статья'
      case 'question':
        return '❓ Вопрос'
      default:
        return 'Неизвестно'
    }
  }

  const resultsCount = results.length
  const categoryStats = {
    mentors: mockData.filter((r: SearchResult) => r.type === 'mentor').length,
    courses: mockData.filter((r: SearchResult) => r.type === 'course').length,
    articles: mockData.filter((r: SearchResult) => r.type === 'article').length,
    questions: mockData.filter((r: SearchResult) => r.type === 'question').length
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Поисковая шапка */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-4xl font-bold mb-6">Поиск на MentorHub</h1>
          
          <div className="relative mb-6">
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-300" />
            <input
              type="text"
              title="Поиск"
              placeholder="Поиск менторов, курсов, статей..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="w-full pl-12 pr-12 py-3 rounded-lg text-gray-900 focus:outline-none focus:ring-2 focus:ring-indigo-400"
            />
            {query && (
              <button
                onClick={() => setQuery('')}
                title="Очистить поиск"
                className="absolute right-4 top-3.5 text-gray-500 hover:text-gray-700"
              >
                <X size={20} />
              </button>
            )}
          </div>

          {!query && (
            <div className="text-indigo-100 text-sm">
              Найдите менторов, курсы и статьи. В базе {mockData.length} ресурсов.
            </div>
          )}
        </div>
      </div>

      <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Фильтры */}
        <div className="bg-white rounded-lg shadow p-4 mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <Filter size={20} className="text-gray-600" />
            <span className="font-semibold text-gray-900">Фильтр по типу:</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {(['all', 'mentor', 'course', 'article', 'question'] as const).map(type => (
              <button
                key={type}
                onClick={() => setFilterType(type)}
                title={type === 'all' ? 'Все' : type === 'mentor' ? 'Менторы' : type === 'course' ? 'Курсы' : type === 'article' ? 'Статьи' : 'Вопросы'}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  filterType === type
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                {type === 'all' && 'Все'}
                {type === 'mentor' && '👨‍💼 Менторы'}
                {type === 'course' && '📚 Курсы'}
                {type === 'article' && '📝 Статьи'}
                {type === 'question' && '❓ Вопросы'}
              </button>
            ))}
          </div>
        </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-2xl font-bold text-indigo-600">{categoryStats.mentors}</p>
              <p className="text-sm text-gray-600 mt-1">Менторов</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-2xl font-bold text-green-600">{categoryStats.courses}</p>
              <p className="text-sm text-gray-600 mt-1">Курсов</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-2xl font-bold text-amber-600">{categoryStats.articles}</p>
              <p className="text-sm text-gray-600 mt-1">Статей</p>
            </div>
            <div className="bg-white rounded-lg shadow p-4 text-center">
              <p className="text-2xl font-bold text-red-600">{categoryStats.questions}</p>
              <p className="text-sm text-gray-600 mt-1">Вопросов</p>
            </div>
          </div>

        {/* Результаты */}
        {query && (
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {loading ? 'Поиск...' : `Найдено ${resultsCount} результатов`}
            </h2>
          </div>
        )}

            {results.map((result: SearchResult) => (
              <Link
                key={result.id}
                href={result.url}
              >
                <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-900">{result.title}</h3>
                        <Badge variant={getTypeColor(result.type)}>
                          {getTypeLabel(result.type)}
                        </Badge>
                      </div>
                      <p className="text-gray-600 mb-4 line-clamp-2">{result.description}</p>
                      {result.tags && (
                        <div className="flex flex-wrap gap-2">
                          {result.tags.map((tag: string) => (
                            <span
                              key={tag}
                              className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex flex-col items-end space-y-2 flex-shrink-0">
                      {result.rating && (
                        <div className="flex items-center space-x-1">
                          <span className="text-sm font-semibold text-amber-500">★</span>
                          <span className="text-sm font-semibold text-gray-900">{result.rating}</span>
                        </div>
                      )}
                      {result.price && (
                        <p className="text-lg font-bold text-indigo-600">{result.price}₽/ч</p>
                      )}
                      <ChevronRight size={20} className="text-gray-400" />
                    </div>
                  </div>
                </div>
              </Link>
            ))}

        {/* Популярные запросы */}
        {!query && (
          <div className="mt-12">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">Популярные запросы</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[
                'React разработчик',
                'Node.js ментор',
                'TypeScript обучение',
                'SQL оптимизация',
                'Frontend интервью',
                'Системный дизайн'
              ].map(q => (
                <button
                  key={q}
                  onClick={() => setQuery(q)}
                  title={`Поиск: ${q}`}
                  className="bg-white rounded-lg shadow p-4 text-left hover:shadow-lg hover:bg-indigo-50 transition-all"
                >
                  <p className="font-medium text-gray-900">{q}</p>
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
