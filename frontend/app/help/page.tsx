'use client'

import { useState } from 'react'
import { Search, Book, Video, Keyboard, FileText, ChevronRight, ExternalLink } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface Article {
  id: number
  title: string
  description: string
  category: 'getting-started' | 'features' | 'advanced' | 'troubleshooting'
  readTime: number
  iconType: 'book' | 'file'
}

interface VideoTutorial {
  id: number
  title: string
  duration: string
  thumbnail: string
  category: string
  views: number
}

interface Shortcut {
  keys: string[]
  description: string
  category: string
}

export default function HelpCenter() {
  const [activeTab, setActiveTab] = useState('articles')
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const articles: Article[] = [
    {
      id: 1,
      title: 'Начало работы с MentorHub',
      description: 'Полное руководство по первым шагам на платформе: регистрация, настройка профиля и поиск менторов.',
      category: 'getting-started',
      readTime: 5,
      iconType: 'book'
    },
    {
      id: 2,
      title: 'Как забронировать сессию с ментором',
      description: 'Пошаговая инструкция по бронированию времени с ментором, выбору даты и подтверждению встречи.',
      category: 'getting-started',
      readTime: 3,
      iconType: 'file'
    },
    {
      id: 3,
      title: 'Система достижений и сертификатов',
      description: 'Узнайте, как зарабатывать баллы, получать достижения и сертификаты за завершение курсов.',
      category: 'features',
      readTime: 4,
      iconType: 'book'
    },
    {
      id: 4,
      title: 'Управление подпиской и платежами',
      description: 'Все о тарифных планах, способах оплаты, управлении подпиской и возврате средств.',
      category: 'features',
      readTime: 6,
      iconType: 'file'
    },
    {
      id: 5,
      title: 'Продвинутые фильтры поиска менторов',
      description: 'Используйте расширенные фильтры для поиска идеального ментора по навыкам, рейтингу и цене.',
      category: 'advanced',
      readTime: 7,
      iconType: 'book'
    },
    {
      id: 6,
      title: 'Интеграция с календарем',
      description: 'Синхронизируйте сессии с Google Calendar, Outlook и другими календарями.',
      category: 'advanced',
      readTime: 5,
      iconType: 'file'
    },
    {
      id: 7,
      title: 'Решение проблем с видеосвязью',
      description: 'Типичные проблемы с WebRTC, настройка микрофона, камеры и устранение задержек.',
      category: 'troubleshooting',
      readTime: 8,
      iconType: 'book'
    },
    {
      id: 8,
      title: 'Проблемы с оплатой',
      description: 'Что делать, если платеж не прошел, как вернуть деньги или изменить способ оплаты.',
      category: 'troubleshooting',
      readTime: 4,
      iconType: 'file'
    },
    {
      id: 9,
      title: 'Оптимизация профиля ментора',
      description: 'Советы по заполнению профиля для привлечения большего количества учеников.',
      category: 'advanced',
      readTime: 10,
      iconType: 'book'
    },
    {
      id: 10,
      title: 'Безопасность аккаунта',
      description: 'Двухфакторная аутентификация, смена пароля и защита персональных данных.',
      category: 'features',
      readTime: 5,
      iconType: 'file'
    }
  ]

  const videos: VideoTutorial[] = [
    {
      id: 1,
      title: 'Обзор платформы MentorHub - Полный гайд для новичков',
      duration: '12:34',
      thumbnail: '🎥',
      category: 'Начало работы',
      views: 15400
    },
    {
      id: 2,
      title: 'Как найти идеального ментора за 5 минут',
      duration: '5:12',
      thumbnail: '🔍',
      category: 'Поиск менторов',
      views: 8900
    },
    {
      id: 3,
      title: 'Настройка вашего первого курса',
      duration: '8:45',
      thumbnail: '📚',
      category: 'Курсы',
      views: 6700
    },
    {
      id: 4,
      title: 'Секреты эффективных сессий 1 на 1',
      duration: '15:20',
      thumbnail: '💬',
      category: 'Сессии',
      views: 12300
    },
    {
      id: 5,
      title: 'Аналитика прогресса: как отслеживать результаты',
      duration: '10:05',
      thumbnail: '📊',
      category: 'Прогресс',
      views: 4500
    },
    {
      id: 6,
      title: 'Монетизация знаний: стать ментором',
      duration: '18:30',
      thumbnail: '💰',
      category: 'Для менторов',
      views: 9800
    }
  ]

  const shortcuts: Shortcut[] = [
    { keys: ['Ctrl', 'K'], description: 'Открыть глобальный поиск', category: 'Навигация' },
    { keys: ['Ctrl', 'M'], description: 'Открыть сообщения', category: 'Навигация' },
    { keys: ['Ctrl', 'N'], description: 'Создать новую сессию', category: 'Действия' },
    { keys: ['Ctrl', 'S'], description: 'Сохранить изменения', category: 'Действия' },
    { keys: ['Ctrl', '/'], description: 'Показать все горячие клавиши', category: 'Справка' },
    { keys: ['Esc'], description: 'Закрыть модальное окно', category: 'Навигация' },
    { keys: ['G', 'D'], description: 'Перейти на Dashboard', category: 'Навигация' },
    { keys: ['G', 'M'], description: 'Перейти к менторам', category: 'Навигация' },
    { keys: ['G', 'C'], description: 'Перейти к курсам', category: 'Навигация' },
    { keys: ['?'], description: 'Открыть справку', category: 'Справка' }
  ]

  const categories = [
    { id: 'all', label: 'Все категории' },
    { id: 'getting-started', label: 'Начало работы' },
    { id: 'features', label: 'Функции' },
    { id: 'advanced', label: 'Продвинутое' },
    { id: 'troubleshooting', label: 'Решение проблем' }
  ]

  const filteredArticles = articles.filter(article => {
    const matchesSearch = article.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         article.description.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = selectedCategory === 'all' || article.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const groupedShortcuts = shortcuts.reduce((acc, shortcut) => {
    if (!acc[shortcut.category]) {
      acc[shortcut.category] = []
    }
    acc[shortcut.category].push(shortcut)
    return acc
  }, {} as Record<string, Shortcut[]>)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl font-bold mb-4">Центр помощи</h1>
          <p className="text-indigo-100 text-lg mb-8">
            Найдите ответы на вопросы и изучите возможности платформы
          </p>
          
          {/* Поиск */}
          <div className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                title="Поиск по документации"
                placeholder="Поиск по статьям, гайдам и видео..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-12 pr-4 py-4 rounded-lg border-none focus:outline-none focus:ring-2 focus:ring-indigo-300 text-gray-900"
              />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Быстрые ссылки */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <Book className="text-blue-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Документация</h3>
                <p className="text-sm text-gray-600">{articles.length} статей</p>
              </div>
            </div>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                <Video className="text-green-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Видеоуроки</h3>
                <p className="text-sm text-gray-600">{videos.length} видео</p>
              </div>
            </div>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                <Keyboard className="text-purple-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">Горячие клавиши</h3>
                <p className="text-sm text-gray-600">{shortcuts.length} комбинаций</p>
              </div>
            </div>
          </Card>

          <Card className="hover:shadow-lg transition-shadow cursor-pointer">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center">
                <FileText className="text-orange-600" size={24} />
              </div>
              <div>
                <h3 className="font-semibold text-gray-900">API Docs</h3>
                <p className="text-sm text-gray-600">Для разработчиков</p>
              </div>
            </div>
          </Card>
        </div>

        {/* Вкладки */}
        <div className="mb-8 border-b border-gray-200">
          <div className="flex flex-wrap gap-4">
            {[
              { id: 'articles', label: 'Статьи', icon: Book },
              { id: 'videos', label: 'Видео', icon: Video },
              { id: 'shortcuts', label: 'Горячие клавиши', icon: Keyboard }
            ].map(tab => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-2 border-b-2 font-medium transition-colors flex items-center space-x-2 ${
                    activeTab === tab.id
                      ? 'border-indigo-600 text-indigo-600'
                      : 'border-transparent text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon size={20} />
                  <span>{tab.label}</span>
                </button>
              )
            })}
          </div>
        </div>

        {/* Статьи */}
        {activeTab === 'articles' && (
          <div>
            {/* Фильтр категорий */}
            <div className="mb-6 flex flex-wrap gap-2">
              {categories.map(cat => (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`px-4 py-2 rounded-lg font-medium transition-all ${
                    selectedCategory === cat.id
                      ? 'bg-indigo-600 text-white'
                      : 'bg-white text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  {cat.label}
                </button>
              ))}
            </div>

            {/* Список статей */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {filteredArticles.map(article => {
                const Icon = article.iconType === 'book' ? Book : FileText
                return (
                  <Card key={article.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                        <Icon className="text-indigo-600" size={24} />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-gray-900 hover:text-indigo-600 transition-colors">
                            {article.title}
                          </h3>
                          <ChevronRight size={20} className="text-gray-400 flex-shrink-0 ml-2" />
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{article.description}</p>
                        <div className="flex items-center space-x-3">
                          <Badge variant="info">
                            {article.category === 'getting-started' ? 'Начало' :
                             article.category === 'features' ? 'Функции' :
                             article.category === 'advanced' ? 'Продвинутое' : 'Проблемы'}
                          </Badge>
                          <span className="text-xs text-gray-500">{article.readTime} мин чтения</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                )
              })}
            </div>

            {filteredArticles.length === 0 && (
              <div className="text-center py-12">
                <p className="text-gray-600">Статей не найдено. Попробуйте изменить поисковый запрос.</p>
              </div>
            )}
          </div>
        )}

        {/* Видео */}
        {activeTab === 'videos' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {videos.map(video => (
              <Card key={video.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <div className="aspect-video bg-gradient-to-br from-indigo-100 to-purple-100 rounded-lg mb-4 flex items-center justify-center text-6xl">
                  {video.thumbnail}
                </div>
                <h3 className="font-semibold text-gray-900 mb-2 hover:text-indigo-600 transition-colors">
                  {video.title}
                </h3>
                <div className="flex items-center justify-between">
                  <Badge variant="success">{video.category}</Badge>
                  <span className="text-sm text-gray-600">{video.duration}</span>
                </div>
                <div className="mt-3 pt-3 border-t border-gray-200 flex items-center justify-between text-sm text-gray-600">
                  <span>{video.views.toLocaleString()} просмотров</span>
                  <ExternalLink size={16} className="text-gray-400" />
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Горячие клавиши */}
        {activeTab === 'shortcuts' && (
          <div className="space-y-8">
            {Object.entries(groupedShortcuts).map(([category, categoryShortcuts]) => (
              <div key={category}>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">{category}</h3>
                <Card>
                  <div className="divide-y divide-gray-200">
                    {categoryShortcuts.map((shortcut, index) => (
                      <div key={index} className="py-4 flex items-center justify-between">
                        <span className="text-gray-700">{shortcut.description}</span>
                        <div className="flex items-center space-x-2">
                          {shortcut.keys.map((key, keyIndex) => (
                            <div key={keyIndex} className="flex items-center">
                              {keyIndex > 0 && <span className="text-gray-400 mx-2">+</span>}
                              <kbd className="px-3 py-1.5 bg-gray-100 border border-gray-300 rounded-md text-sm font-mono font-semibold text-gray-900 shadow-sm">
                                {key}
                              </kbd>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              </div>
            ))}
          </div>
        )}

        {/* Нужна помощь? */}
        <Card className="mt-12 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
          <div className="text-center">
            <h3 className="text-xl font-bold text-gray-900 mb-2">Не нашли ответ?</h3>
            <p className="text-gray-600 mb-6">
              Свяжитесь с нашей службой поддержки, и мы поможем вам решить любую проблему
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors">
                Связаться с поддержкой
              </button>
              <button className="px-6 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-100 font-medium transition-colors border border-gray-300">
                Скачать PDF-руководство
              </button>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
