'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'

interface SearchResult {
  id: number
  type: 'user' | 'course' | 'session' | 'mentor'
  title: string
  description: string
  image?: string
  rating?: number
  price?: number
}

interface SearchFilters {
  type: string
  minPrice: number
  maxPrice: number
  minRating: number
  sortBy: 'relevance' | 'rating' | 'price' | 'newest'
}

export default function AdvancedSearch() {
  const toast = useToast()
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [filters, setFilters] = useState<SearchFilters>({
    type: 'all',
    minPrice: 0,
    maxPrice: 1000,
    minRating: 0,
    sortBy: 'relevance'
  })

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (query.length > 2) {
        performSearch()
      }
    }, 300)

    return () => clearTimeout(delayDebounce)
  }, [query, filters])

  const performSearch = async () => {
    setIsLoading(true)
    try {
      const params = new URLSearchParams({
        q: query,
        type: filters.type,
        min_price: filters.minPrice.toString(),
        max_price: filters.maxPrice.toString(),
        min_rating: filters.minRating.toString(),
        sort: filters.sortBy
      })

      const response = await fetch(`/api/search?${params}`)
      if (response.ok) {
        const data = await response.json()
        setResults(data.results || [])
      }
    } catch (error) {
      console.error('Search error:', error)
      toast.error('Ошибка поиска')
    } finally {
      setIsLoading(false)
    }
  }

  const ResultCard = ({ result }: { result: SearchResult }) => {
    const icons = {
      user: '👤',
      course: '📚',
      session: '📅',
      mentor: '🎓'
    }

    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
        <div className="flex items-start gap-4">
          <div className="text-4xl">{icons[result.type]}</div>
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
              {result.title}
            </h3>
            <p className="text-gray-600 dark:text-gray-400 text-sm mb-2">
              {result.description}
            </p>
            <div className="flex items-center gap-4">
              {result.rating && (
                <span className="text-yellow-600 dark:text-yellow-400 font-medium">
                  ⭐ {result.rating.toFixed(1)}
                </span>
              )}
              {result.price && (
                <span className="text-green-600 dark:text-green-400 font-medium">
                  ${result.price}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Search Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">
            🔍 Поиск
          </h1>
          
          {/* Search Input */}
          <div className="relative">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Поиск менторов, курсов, сессий..."
              className="w-full px-6 py-4 pl-12 text-lg border border-gray-300 dark:border-gray-600 rounded-xl bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <svg
              className="absolute left-4 top-1/2 -translate-y-1/2 w-6 h-6 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            {isLoading && (
              <div className="absolute right-4 top-1/2 -translate-y-1/2">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
              </div>
            )}
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-8">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            🎯 Фильтры
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-4">
            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Тип
              </label>
              <select
                value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="all">Все</option>
                <option value="mentor">Менторы</option>
                <option value="course">Курсы</option>
                <option value="session">Сессии</option>
                <option value="user">Пользователи</option>
              </select>
            </div>

            {/* Price Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Цена до
              </label>
              <input
                type="number"
                value={filters.maxPrice}
                onChange={(e) => setFilters({ ...filters, maxPrice: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              />
            </div>

            {/* Rating Filter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Рейтинг от
              </label>
              <select
                value={filters.minRating}
                onChange={(e) => setFilters({ ...filters, minRating: Number(e.target.value) })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value={0}>Любой</option>
                <option value={3}>3+ ⭐</option>
                <option value={4}>4+ ⭐</option>
                <option value={4.5}>4.5+ ⭐</option>
              </select>
            </div>

            {/* Sort By */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Сортировка
              </label>
              <select
                value={filters.sortBy}
                onChange={(e) => setFilters({ ...filters, sortBy: e.target.value as SearchFilters['sortBy'] })}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                <option value="relevance">По релевантности</option>
                <option value="rating">По рейтингу</option>
                <option value="price">По цене</option>
                <option value="newest">По новизне</option>
              </select>
            </div>

            {/* Reset Filters */}
            <div className="flex items-end">
              <button
                onClick={() => setFilters({
                  type: 'all',
                  minPrice: 0,
                  maxPrice: 1000,
                  minRating: 0,
                  sortBy: 'relevance'
                })}
                className="w-full px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
              >
                🔄 Сброс
              </button>
            </div>
          </div>
        </div>

        {/* Results */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
              Результаты: {results.length}
            </h2>
          </div>

          {results.length > 0 ? (
            <div className="space-y-4">
              {results.map((result) => (
                <ResultCard key={result.id} result={result} />
              ))}
            </div>
          ) : query.length > 2 && !isLoading ? (
            <div className="text-center py-12 bg-white dark:bg-gray-800 rounded-xl">
              <p className="text-gray-500 dark:text-gray-400 text-lg">
                Ничего не найдено по запросу "{query}"
              </p>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}
