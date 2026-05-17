/**
 * Mentor Profile Page
 * Detailed mentor information with chat functionality
 */

'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import { Star, MapPin, Clock, DollarSign, Calendar, CheckCircle, MessageCircle, ArrowLeft } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Link from 'next/link'
import { ChatButton } from '@/components/ChatButton'
import { getMentorById, Mentor } from '@/lib/api/mentors'

interface Review {
  id: number
  author_name: string
  rating: number
  comment: string
  created_at: string
}

export default function MentorProfilePage() {
  const params = useParams()
  const mentorId = params?.id ? parseInt(params.id as string) : 0
  const [mentor, setMentor] = useState<Mentor | null>(null)
  const [reviews, setReviews] = useState<Review[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showChat, setShowChat] = useState(false)

  useEffect(() => {
    if (!mentorId) return
    loadMentor()
  }, [mentorId])

  const loadMentor = async () => {
    try {
      setLoading(true)
      const data = await getMentorById(mentorId)
      setMentor(data)
      setError(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load mentor')
    } finally {
      setLoading(false)
    }
  }

  // Generate mock reviews (until backend provides reviews API)
  useEffect(() => {
    if (mentor) {
      setReviews([
        {
          id: 1,
          author_name: 'Алексей М.',
          rating: 5,
          comment: 'Отличный ментор! Очень помогло в подготовке к собеседованию. Объясняет сложные вещи простым языком.',
          created_at: '2025-04-10',
        },
        {
          id: 2,
          author_name: 'Мария К.',
          rating: 5,
          comment: 'Профессиональный подход к обучению. Помог разобраться с архитектурой React-приложений.',
          created_at: '2025-03-28',
        },
      ])
    }
  }, [mentor])

  if (loading) {
    return (
      <main className="container mx-auto max-w-5xl px-4 py-10">
        <div className="flex flex-col items-center justify-center py-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка профиля ментора...</p>
        </div>
      </main>
    )
  }

  if (error || !mentor) {
    return (
      <main className="container mx-auto max-w-5xl px-4 py-10">
        <Link
          href="/mentors"
          className="inline-flex items-center text-gray-600 hover:text-indigo-600 mb-6 transition-colors"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к менторам
        </Link>
        <Card padding="lg" className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error || 'Ментор не найден'}</p>
          <Button variant="primary" onClick={loadMentor}>Повторить</Button>
        </Card>
      </main>
    )
  }

  const skills = mentor.specialization
    ? mentor.specialization.split(',').map(s => s.trim()).filter(Boolean)
    : []

  return (
    <main className="container mx-auto max-w-5xl px-4 py-10">
      {/* Back Button */}
      <Link
        href="/mentors"
        className="inline-flex items-center text-gray-600 hover:text-indigo-600 mb-6 transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-2" />
        Назад к менторам
      </Link>

      {/* Header */}
      <Card padding="lg" className="mb-6">
        <div className="flex flex-col md:flex-row gap-6 items-start">
          {/* Avatar */}
          <div className="flex-shrink-0">
            {mentor.user?.avatar_url ? (
              <img
                src={mentor.user.avatar_url}
                alt={mentor.user.full_name}
                className="w-32 h-32 rounded-full object-cover"
              />
            ) : (
              <div className="w-32 h-32 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center text-6xl">
                {mentor.user?.full_name?.charAt(0) || '👤'}
              </div>
            )}
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
                  {mentor.user?.full_name || 'Ментор'}
                </h1>
                <p className="text-lg text-indigo-600 dark:text-indigo-400 font-semibold">
                  {mentor.specialization || mentor.user?.role || 'Ментор'}
                </p>
              </div>
              <Button
                variant="primary"
                onClick={() => setShowChat(!showChat)}
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Написать
              </Button>
            </div>

            {/* Rating */}
            <div className="flex items-center gap-4 mb-4">
              <div className="flex items-center">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className={`w-5 h-5 ${
                      i < Math.floor(mentor.rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300 dark:text-gray-600'
                    }`}
                  />
                ))}
              </div>
              <span className="text-lg font-semibold text-gray-900 dark:text-white">
                {mentor.rating.toFixed(1)}
              </span>
              <span className="text-gray-600 dark:text-gray-400">
                ({mentor.total_reviews} отзывов)
              </span>
            </div>

            {/* Meta Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <DollarSign className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Ставка</p>
                  <p className="font-semibold text-gray-900 dark:text-white">{mentor.hourly_rate}₽/час</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Clock className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Опыт</p>
                  <p className="font-semibold text-gray-900 dark:text-white">{mentor.experience_years} лет</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <CheckCircle className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Статус</p>
                  <p className="font-semibold text-green-600">
                    {mentor.is_available ? 'Доступен' : 'Недоступен'}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600 dark:text-gray-400">
                <Calendar className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500 dark:text-gray-500">Обновлено</p>
                  <p className="font-semibold text-gray-900 dark:text-white">
                    {new Date(mentor.updated_at).toLocaleDateString('ru-RU')}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Main Content */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="md:col-span-2 space-y-6">
          {/* About */}
          <Card padding="lg">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">О менторе</h2>
            <p className="text-gray-700 dark:text-gray-300 whitespace-pre-line leading-relaxed">
              {mentor.bio || 'Информация о менторе пока не добавлена.'}
            </p>
          </Card>

          {/* Reviews */}
          <Card padding="lg">
            <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
              Отзывы ({reviews.length})
            </h2>
            {reviews.length === 0 ? (
              <p className="text-gray-500 dark:text-gray-400 text-center py-8">Отзывов пока нет</p>
            ) : (
              <div className="space-y-4">
                {reviews.map(review => (
                  <div key={review.id} className="border-b border-gray-200 dark:border-gray-700 pb-4 last:border-0">
                    <div className="flex items-center gap-3 mb-2">
                      <div className="w-10 h-10 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center">
                        <span className="text-sm font-semibold text-white">
                          {review.author_name.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-white">{review.author_name}</p>
                        <div className="flex items-center gap-1">
                          {[...Array(5)].map((_, i) => (
                            <Star
                              key={i}
                              className={`w-4 h-4 ${
                                i < review.rating
                                  ? 'fill-yellow-400 text-yellow-400'
                                  : 'text-gray-300 dark:text-gray-600'
                              }`}
                            />
                          ))}
                        </div>
                      </div>
                    </div>
                    <p className="text-gray-700 dark:text-gray-300 text-sm">{review.comment}</p>
                    <p className="text-xs text-gray-400 mt-1">
                      {new Date(review.created_at).toLocaleDateString('ru-RU')}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Skills */}
          {skills.length > 0 && (
            <Card padding="lg">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Навыки</h2>
              <div className="flex flex-wrap gap-2">
                {skills.map(tag => (
                  <Badge key={tag} variant="default" size="sm">
                    {tag}
                  </Badge>
                ))}
              </div>
            </Card>
          )}

          {/* Languages */}
          <Card padding="lg">
            <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Информация</h2>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">
                  Email: {mentor.user?.email || 'Не указан'}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span className="text-gray-700 dark:text-gray-300">
                  На платформе с {new Date(mentor.created_at).toLocaleDateString('ru-RU')}
                </span>
              </div>
            </div>
          </Card>

          {/* CTA */}
          <Card padding="lg" className="bg-gradient-to-br from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 border-indigo-200 dark:border-indigo-800">
            <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">Готовы начать?</h3>
            <div className="space-y-3">
              <Button variant="primary" fullWidth>
                <Calendar className="w-4 h-4 mr-2" />
                Забронировать сессию
              </Button>
              <Button
                variant="outline"
                fullWidth
                onClick={() => setShowChat(!showChat)}
              >
                <MessageCircle className="w-4 h-4 mr-2" />
                Написать сообщение
              </Button>
            </div>
          </Card>
        </div>
      </div>

      {/* Chat Widget */}
      {showChat && (
        <ChatButton
          recipientId={mentor.user_id}
          recipientName={mentor.user?.full_name || 'Ментор'}
        />
      )}
    </main>
  )
}
