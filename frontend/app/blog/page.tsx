'use client'

import { useState } from 'react'
import { Search, Filter, TrendingUp, Clock, Eye, Heart } from 'lucide-react'
import Link from 'next/link'
import Badge from '@/components/ui/Badge'

interface Article {
  id: string
  title: string
  excerpt: string
  category: string
  views: number
  likes: number
  timeToRead: number
  author: { name: string; avatar: string }
  publishDate: string
  trending: boolean
  slug: string
}

export default function BlogPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [sortBy, setSortBy] = useState<'latest' | 'trending' | 'popular'>('latest')

  const articles: Article[] = [
    {
      id: '1',
      slug: 'kak-podgotsya-k-sobesedovaniyu',
      title: 'Как подготовиться к собеседованию разработчика',
      excerpt: 'Полное руководство по подготовке к техническому собеседованию: от алгоритмов до soft skills.',
      category: 'Career',
      views: 2541,
      likes: 342,
      timeToRead: 12,
      author: { name: 'Иван Петров', avatar: '👨‍💻' },
      publishDate: '2024-11-15',
      trending: true
    },
    {
      id: '2',
      slug: 'react-19-novyye-vozmozhnosti',
      title: 'React 19: Новые хуки и возможности',
      excerpt: 'Обзор новых хуков React 19, которые упростят разработку и повысят производительность.',
      category: 'React',
      views: 1832,
      likes: 287,
      timeToRead: 8,
      author: { name: 'Мария Сидорова', avatar: '👩‍💻' },
      publishDate: '2024-11-13',
      trending: true
    },
    {
      id: '3',
      slug: 'typescript-best-practices',
      title: 'TypeScript лучшие практики в 2024',
      excerpt: 'Узнайте о лучших практиках использования TypeScript для написания безопасного кода.',
      category: 'TypeScript',
      views: 1564,
      likes: 215,
      timeToRead: 10,
      author: { name: 'Алексей Иванов', avatar: '👨‍🔬' },
      publishDate: '2024-11-10',
      trending: false
    },
    {
      id: '4',
      slug: 'kak-vybrat-mentora',
      title: 'Как выбрать ментора: 7 критериев',
      excerpt: 'Руководство по выбору идеального ментора для вашего карьерного развития.',
      category: 'Career',
      views: 1243,
      likes: 198,
      timeToRead: 14,
      author: { name: 'Екатерина Петрова', avatar: '👩‍💼' },
      publishDate: '2024-11-08',
      trending: false
    }
  ]

  const categories = ['all', 'Career', 'React', 'TypeScript', 'Node.js', 'Backend']

  const filteredArticles = articles
    .filter(article => {
      const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           article.excerpt.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory
      return matchesSearch && matchesCategory
    })
    .sort((a, b) => {
      if (sortBy === 'latest') {
        return new Date(b.publishDate).getTime() - new Date(a.publishDate).getTime()
      } else if (sortBy === 'trending') {
        return (b.trending ? 1 : 0) - (a.trending ? 1 : 0)
      } else {
        return b.views - a.views
      }
    })

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-6xl mx-auto">
        {/* Заголовок */}
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Блог MentorHub</h1>
          <p className="text-xl text-gray-600">Статьи, советы и рекомендации для разработчиков</p>
        </div>

        {/* Поиск и фильтры */}
        <div className="mb-8 space-y-4">
          {/* Поиск */}
          <div className="relative">
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
            <input
              type="text"
              placeholder="Поиск статей..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              title="Введите поисковый запрос"
              className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>

          {/* Фильтры и сортировка */}
          <div className="flex flex-col sm:flex-row gap-4">
            {/* Категории */}
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-2">
                <Filter size={18} className="text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Категория:</span>
              </div>
              <div className="flex flex-wrap gap-2">
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setSelectedCategory(cat)}
                    title={`Фильтр по категории ${cat}`}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      selectedCategory === cat
                        ? 'bg-indigo-600 text-white'
                        : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
                    }`}
                  >
                    {cat === 'all' ? 'Все' : cat}
                  </button>
                ))}
              </div>
            </div>

            {/* Сортировка */}
            <div className="flex-shrink-0">
              <label className="text-sm font-medium text-gray-700 mb-2 block">Сортировка:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                title="Выберите способ сортировки"
                className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="latest">Новые</option>
                <option value="trending">Популярные</option>
                <option value="popular">По просмотрам</option>
              </select>
            </div>
          </div>
        </div>

        {/* Статьи */}
        <div className="space-y-6">
          {filteredArticles.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-12 text-center">
              <p className="text-gray-500">Статей не найдено</p>
            </div>
          ) : (
            filteredArticles.map(article => (
              <Link key={article.id} href={`/blog/${article.slug}`}>
                <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 cursor-pointer group">
                  <div className="flex flex-col sm:flex-row gap-6">
                    {/* Контент */}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <Badge variant="info">{article.category}</Badge>
                        {article.trending && (
                          <Badge variant="danger">
                            <TrendingUp size={14} className="inline mr-1" />
                            Популярно
                          </Badge>
                        )}
                      </div>
                      <h3 className="text-xl font-semibold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">
                        {article.title}
                      </h3>
                      <p className="text-gray-600 mb-4 line-clamp-2">{article.excerpt}</p>

                      {/* Метаинформация */}
                      <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center space-x-1">
                          <span>{article.author.avatar}</span>
                          <span>{article.author.name}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Clock size={16} />
                          <span>{article.timeToRead} мин</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Eye size={16} />
                          <span>{article.views.toLocaleString('ru-RU')}</span>
                        </div>
                        <span>{new Date(article.publishDate).toLocaleDateString('ru-RU')}</span>
                      </div>
                    </div>

                    {/* Действия */}
                    <div className="flex-shrink-0 flex flex-col items-end justify-between sm:w-32">
                      <button
                        className="text-gray-400 hover:text-red-500 transition-colors"
                        onClick={(e) => e.preventDefault()}
                        title="Нравится"
                      >
                        <Heart size={24} />
                      </button>
                      <span className="text-sm text-gray-500">{article.likes}</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  )
}
