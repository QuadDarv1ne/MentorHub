'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Input from '@/components/ui/Input'
import Select from '@/components/ui/Select'
import { Star, MapPin, Clock, DollarSign, ArrowRight, Search } from 'lucide-react'

interface Mentor {
  id: number
  name: string
  specialty: string
  rating: number
  reviews: number
  hourRate: number
  location: string
  experience: string
  photo: string
  bio: string
  tags: string[]
  availability: string
}

const mentors: Mentor[] = [
  {
    id: 1,
    name: 'Иван Петров',
    specialty: 'JavaScript / React',
    rating: 4.9,
    reviews: 152,
    hourRate: 1500,
    location: 'Москва',
    experience: '8 лет',
    photo: '👨‍💼',
    bio: 'Опытный Full-Stack разработчик. Специализируюсь на JavaScript, React и Node.js',
    tags: ['JavaScript', 'React', 'Node.js', 'TypeScript'],
    availability: 'Доступен каждый день'
  },
  {
    id: 2,
    name: 'Мария Сидорова',
    specialty: 'System Design',
    rating: 4.8,
    reviews: 98,
    hourRate: 2000,
    location: 'Санкт-Петербург',
    experience: '10 лет',
    photo: '👩‍💼',
    bio: 'Архитектор ПО с опытом в масштабируемых системах',
    tags: ['Architecture', 'System Design', 'AWS', 'Database'],
    availability: 'Выходные и вечера'
  },
  {
    id: 3,
    name: 'Александр Иванов',
    specialty: 'SQL / Database',
    rating: 4.7,
    reviews: 87,
    hourRate: 1200,
    location: 'Казань',
    experience: '12 лет',
    photo: '👨‍💻',
    bio: 'DBA специалист. Помогу оптимизировать ваши запросы',
    tags: ['SQL', 'PostgreSQL', 'Performance', 'Optimization'],
    availability: 'По договоренности'
  },
  {
    id: 4,
    name: 'Дарья Волкова',
    specialty: 'Frontend / CSS',
    rating: 4.9,
    reviews: 143,
    hourRate: 1300,
    location: 'Москва',
    experience: '6 лет',
    photo: '👩‍🎨',
    bio: 'UI/UX разработчик с фокусом на производительность',
    tags: ['React', 'CSS', 'Design', 'Accessibility'],
    availability: 'Гибкий график'
  },
  {
    id: 5,
    name: 'Сергей Смирнов',
    specialty: 'Python / Backend',
    rating: 4.6,
    reviews: 76,
    hourRate: 1400,
    location: 'Москва',
    experience: '7 лет',
    photo: '👨‍💻',
    bio: 'Django и FastAPI специалист',
    tags: ['Python', 'Django', 'FastAPI', 'DevOps'],
    availability: 'Рабочие дни, вечера'
  },
  {
    id: 6,
    name: 'Елена Морозова',
    specialty: 'Data Science',
    rating: 4.8,
    reviews: 101,
    hourRate: 1800,
    location: 'Санкт-Петербург',
    experience: '9 лет',
    photo: '👩‍🔬',
    bio: 'ML инженер с опытом в Deep Learning',
    tags: ['Python', 'Machine Learning', 'TensorFlow', 'Statistics'],
    availability: 'Выходные предпочтительно'
  }
]

export default function MentorsPage() {
  const [searchQuery, setSearchQuery] = useState('')
  const [filterSpecialty, setFilterSpecialty] = useState('all')
  const [filterRating, setFilterRating] = useState('all')
  const [sortBy, setSortBy] = useState('rating')

  const specialties = ['all', ...new Set(mentors.map(m => m.specialty))]
  const ratings = [
    { value: 'all', label: 'Все рейтинги' },
    { value: '4.9', label: '⭐ 4.9+' },
    { value: '4.7', label: '⭐ 4.7+' },
    { value: '4.5', label: '⭐ 4.5+' }
  ]

  const filtered = mentors.filter(mentor => {
    const matchesSearch =
      mentor.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.specialty.toLowerCase().includes(searchQuery.toLowerCase()) ||
      mentor.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesSpecialty =
      filterSpecialty === 'all' || mentor.specialty === filterSpecialty

    const matchesRating =
      filterRating === 'all' || mentor.rating >= parseFloat(filterRating)

    return matchesSearch && matchesSpecialty && matchesRating
  })

  const sorted = [...filtered].sort((a, b) => {
    if (sortBy === 'rating') return b.rating - a.rating
    if (sortBy === 'price-low') return a.hourRate - b.hourRate
    if (sortBy === 'price-high') return b.hourRate - a.hourRate
    return 0
  })

  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Найдите идеального ментора</h1>
        <p className="text-xl text-gray-600">
          {sorted.length} профессионалов готовы помочь вам достичь целей
        </p>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
          {/* Search */}
          <div className="lg:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
              <Input
                placeholder="Поиск по имени, специальности или навыкам..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>

          {/* Specialty Filter */}
          <Select
            label="Специальность"
            options={specialties.map(s => ({
              value: s,
              label: s === 'all' ? 'Все специальности' : s
            }))}
            value={filterSpecialty}
            onChange={(e) => setFilterSpecialty(e.target.value)}
          />

          {/* Rating Filter */}
          <Select
            label="Рейтинг"
            options={ratings}
            value={filterRating}
            onChange={(e) => setFilterRating(e.target.value)}
          />
        </div>

        <div className="flex items-center justify-between">
          <Select
            label="Сортировка"
            options={[
              { value: 'rating', label: 'По рейтингу (выше)' },
              { value: 'price-low', label: 'По цене (дешевле)' },
              { value: 'price-high', label: 'По цене (дороже)' }
            ]}
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
          />
          <span className="text-sm text-gray-600">Найдено: {sorted.length}</span>
        </div>
      </div>

      {/* Mentors Grid */}
      {sorted.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sorted.map((mentor) => (
            <Card key={mentor.id} padding="md" hover>
              <div className="text-center mb-4">
                <div className="text-5xl mb-3">{mentor.photo}</div>
                <h3 className="text-lg font-bold text-gray-900">{mentor.name}</h3>
                <p className="text-sm text-indigo-600 font-semibold">{mentor.specialty}</p>
              </div>

              {/* Rating */}
              <div className="flex items-center justify-center gap-2 mb-4">
                <div className="flex items-center">
                  {[...Array(5)].map((_, i) => (
                    <Star
                      key={i}
                      className={`h-4 w-4 ${
                        i < Math.floor(mentor.rating)
                          ? 'fill-yellow-400 text-yellow-400'
                          : 'text-gray-300'
                      }`}
                    />
                  ))}
                </div>
                <span className="text-sm font-semibold text-gray-900">{mentor.rating}</span>
                <span className="text-sm text-gray-600">({mentor.reviews})</span>
              </div>

              {/* Bio */}
              <p className="text-sm text-gray-600 mb-4 line-clamp-2">{mentor.bio}</p>

              {/* Info */}
              <div className="space-y-2 mb-4 pb-4 border-b">
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <DollarSign className="h-4 w-4 text-indigo-600" />
                  <span className="font-semibold">{mentor.hourRate}₽/час</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <Clock className="h-4 w-4 text-indigo-600" />
                  <span>{mentor.experience} опыта</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-gray-600">
                  <MapPin className="h-4 w-4 text-indigo-600" />
                  <span>{mentor.location}</span>
                </div>
              </div>

              {/* Tags */}
              <div className="flex flex-wrap gap-2 mb-4">
                {mentor.tags.map((tag) => (
                  <Badge key={tag} variant="primary" size="sm">
                    {tag}
                  </Badge>
                ))}
              </div>

              {/* Availability */}
              <p className="text-xs text-gray-500 mb-4">{mentor.availability}</p>

              {/* Actions */}
              <Button variant="primary" fullWidth>
                <ArrowRight className="h-4 w-4 mr-2" />
                Забронировать сессию
              </Button>
            </Card>
          ))}
        </div>
      ) : (
        <Card padding="lg" className="text-center">
          <div className="text-4xl mb-3">🔍</div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Менторы не найдены</h3>
          <p className="text-gray-600 mb-4">
            Попробуйте изменить фильтры или поисковый запрос
          </p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchQuery('')
              setFilterSpecialty('all')
              setFilterRating('all')
              setSortBy('rating')
            }}
          >
            Сбросить фильтры
          </Button>
        </Card>
      )}

      {/* Tips */}
      <Card padding="lg" className="mt-12 bg-gradient-to-r from-blue-50 to-indigo-50 border border-indigo-200">
        <h3 className="text-lg font-bold text-gray-900 mb-4">💡 Советы по выбору ментора</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-2xl mb-2">⭐</div>
            <h4 className="font-semibold text-gray-900 mb-1">Смотрите отзывы</h4>
            <p className="text-sm text-gray-600">
              Рейтинг и количество отзывов показывают качество работы ментора
            </p>
          </div>
          <div>
            <div className="text-2xl mb-2">🎯</div>
            <h4 className="font-semibold text-gray-900 mb-1">Выбирайте по специальности</h4>
            <p className="text-sm text-gray-600">
              Ищите менторов, чьи навыки совпадают с вашими целями обучения
            </p>
          </div>
          <div>
            <div className="text-2xl mb-2">📅</div>
            <h4 className="font-semibold text-gray-900 mb-1">Проверьте доступность</h4>
            <p className="text-sm text-gray-600">
              Убедитесь, что график ментора соответствует вашему времени
            </p>
          </div>
        </div>
      </Card>
    </main>
  )
}