'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { Calendar, Clock, Video, MessageSquare } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/ui/Modal'
import { useAuth } from '@/hooks/useAuth'

const sessions = [
  {
    id: 1,
    mentorName: 'Иван Петров',
    mentorPhoto: '👨‍💼',
    specialty: 'JavaScript / React',
    date: '21 ноября 2025',
    time: '14:00',
    duration: '60 минут',
    status: 'upcoming',
    price: 1500,
    topic: 'React Hooks в деталях',
    format: 'Видеозвонок',
    notes: 'Будем разбирать useState, useEffect, useContext с примерами'
  },
  {
    id: 2,
    mentorName: 'Мария Сидорова',
    mentorPhoto: '👩‍💼',
    specialty: 'Node.js / Backend',
    date: '18 ноября 2025',
    time: '16:00',
    duration: '90 минут',
    status: 'completed',
    price: 2250,
    topic: 'Архитектура REST API',
    format: 'Видеозвонок',
    rating: 5,
    feedback: 'Отличная сессия! Очень помогла разобраться с микросервисами.'
  },
  {
    id: 3,
    mentorName: 'Сергей Новиков',
    mentorPhoto: '👨‍🏫',
    specialty: 'TypeScript / Fullstack',
    date: '15 ноября 2025',
    time: '10:00',
    duration: '60 минут',
    status: 'completed',
    price: 1500,
    topic: 'Advanced TypeScript',
    format: 'Видеозвонок',
    rating: 4,
    feedback: 'Хороший ментор, но хотелось бы больше практики.'
  },
  {
    id: 4,
    mentorName: 'Иван Петров',
    mentorPhoto: '👨‍💼',
    specialty: 'JavaScript / React',
    date: '25 ноября 2025',
    time: '18:00',
    duration: '60 минут',
    status: 'upcoming',
    price: 1500,
    topic: 'Next.js и SSR',
    format: 'Видеозвонок',
    notes: 'Обсудим Server-Side Rendering и оптимизацию'
  }
]

const stats = {
  totalSessions: 12,
  completedSessions: 10,
  totalSpent: 15000,
  nextSession: '21 ноября 2025 в 14:00'
}

export default function SessionsPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [showRatingModal, setShowRatingModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'upcoming' | 'completed'>('upcoming')
  const [selectedSession, setSelectedSession] = useState<typeof sessions[0] | null>(null)
  const [rating, setRating] = useState(5)
  const [feedback, setFeedback] = useState('')

  // Проверка авторизации
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/sessions')
    } else {
      setIsLoading(true)
      setTimeout(() => setIsLoading(false), 300)
    }
  }, [isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Загрузка сессий...</p>
        </div>
      </div>
    )
  }

  const upcomingSessions = sessions.filter(s => s.status === 'upcoming')
  const completedSessions = sessions.filter(s => s.status === 'completed')

  const handleSubmitRating = () => {
    alert(`Спасибо за рейтинг ${rating}⭐! Ваш отзыв: ${feedback}`)
    setShowRatingModal(false)
  }

  const handleCancelSession = (id: number) => {
    alert(`Сессия #${id} отменена`)
  }

  const SessionCard = ({ session, isUpcoming }: { session: typeof sessions[0]; isUpcoming: boolean }) => (
    <Card padding="lg" className="mb-4">
      <div className="flex flex-col md:flex-row gap-6">
        {/* Mentor Info */}
        <div className="flex gap-4 flex-1">
          <div className="text-5xl flex-shrink-0">{session.mentorPhoto}</div>
          <div className="flex-1">
            <h3 className="text-xl font-bold text-gray-900 mb-1">{session.mentorName}</h3>
            <p className="text-indigo-600 font-semibold mb-3">{session.specialty}</p>

            {/* Details Grid */}
            <div className="space-y-2 text-sm text-gray-600 mb-4">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-indigo-600" />
                <span>{session.date}</span>
              </div>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-indigo-600" />
                <span>{session.time} ({session.duration})</span>
              </div>
              <div className="flex items-center gap-2">
                <Video className="h-4 w-4 text-indigo-600" />
                <span>{session.format}</span>
              </div>
              <div className="flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-indigo-600" />
                <span className="text-gray-900 font-semibold">{session.topic}</span>
              </div>
            </div>

            {/* Notes or Feedback */}
            {isUpcoming && session.notes && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-900">
                📝 {session.notes}
              </div>
            )}

            {!isUpcoming && session.feedback && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-900">
                ✓ {session.feedback}
              </div>
            )}
          </div>
        </div>

        {/* Price and Actions */}
        <div className="flex flex-col items-end justify-between md:w-48">
          <div className="text-right">
            <div className="text-2xl font-bold text-indigo-600 mb-1">{session.price}₽</div>
            {isUpcoming && <Badge variant="success">Предстоящая</Badge>}
            {!isUpcoming && session.rating && (
              <div className="flex items-center justify-end gap-1 mb-3">
                {[...Array(5)].map((_, i) => (
                  <span key={i} className={i < session.rating ? 'text-yellow-400' : 'text-gray-300'}>
                    ⭐
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 w-full">
            {isUpcoming ? (
              <>
                <Button variant="secondary" fullWidth size="sm">
                  Присоединиться
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCancelSession(session.id)}
                >
                  Отмена
                </Button>
              </>
            ) : (
              <>
                {!session.rating && (
                  <Button
                    variant="secondary"
                    fullWidth
                    size="sm"
                    onClick={() => {
                      setSelectedSession(session)
                      setShowRatingModal(true)
                    }}
                  >
                    Оценить
                  </Button>
                )}
                {session.rating && (
                  <Button variant="outline" fullWidth size="sm" disabled>
                    Уже оценено
                  </Button>
                )}
                <Button variant="outline" size="sm">
                  Ещё раз
                </Button>
              </>
            )}
          </div>
        </div>
      </div>
    </Card>
  )

  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Мои сессии</h1>
        <p className="text-gray-600 text-lg">Управляйте вашими занятиями с менторами</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-indigo-600 mb-1">{stats.totalSessions}</div>
          <div className="text-sm text-gray-600">Всего сессий</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">{stats.completedSessions}</div>
          <div className="text-sm text-gray-600">Завершено</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-blue-600 mb-1">{stats.totalSpent}₽</div>
          <div className="text-sm text-gray-600">Потрачено</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-lg font-bold text-purple-600 mb-1">Следующая</div>
          <div className="text-sm text-gray-600">{stats.nextSession}</div>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-4 mb-8 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('upcoming')}
          className={`px-4 py-3 font-semibold transition-all border-b-2 ${
            activeTab === 'upcoming'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          📅 Предстоящие ({upcomingSessions.length})
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-3 font-semibold transition-all border-b-2 ${
            activeTab === 'completed'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          ✅ Завершенные ({completedSessions.length})
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'upcoming' && (
        <div>
          {upcomingSessions.length > 0 ? (
            upcomingSessions.map(session => (
              <SessionCard key={session.id} session={session} isUpcoming={true} />
            ))
          ) : (
            <Card padding="lg" className="text-center">
              <p className="text-gray-600 mb-4">У вас нет предстоящих сессий</p>
              <Button variant="secondary">Забронировать сессию</Button>
            </Card>
          )}
        </div>
      )}

      {activeTab === 'completed' && (
        <div>
          {completedSessions.length > 0 ? (
            completedSessions.map(session => (
              <SessionCard key={session.id} session={session} isUpcoming={false} />
            ))
          ) : (
            <Card padding="lg" className="text-center">
              <p className="text-gray-600">Нет завершенных сессий</p>
            </Card>
          )}
        </div>
      )}

      {/* Rating Modal */}
      <Modal
        isOpen={showRatingModal}
        onClose={() => setShowRatingModal(false)}
        title={`Оценить сессию с ${selectedSession?.mentorName}`}
        size="md"
      >
        <div className="space-y-6">
          {/* Rating */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Как вам сессия?
            </label>
            <div className="flex gap-2 justify-center mb-4">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  onClick={() => setRating(star)}
                  title={`Оценить ${star} звёзд`}
                  className={`text-4xl transition-transform hover:scale-110 ${
                    star <= rating ? 'text-yellow-400' : 'text-gray-300'
                  }`}
                >
                  ⭐
                </button>
              ))}
            </div>
            <p className="text-center text-gray-600">
              {rating === 5 && 'Отлично! 🎉'}
              {rating === 4 && 'Хорошо! 👍'}
              {rating === 3 && 'Нормально'}
              {rating === 2 && 'Не очень'}
              {rating === 1 && 'Плохо'}
            </p>
          </div>

          {/* Feedback */}
          <div>
            <label htmlFor="feedback" className="block text-sm font-semibold text-gray-900 mb-3">
              Ваши комментарии
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Расскажите о своем опыте..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={4}
            />
          </div>

          {/* Buttons */}
          <div className="flex gap-3">
            <Button variant="secondary" fullWidth onClick={handleSubmitRating}>
              Отправить оценку
            </Button>
            <Button variant="outline" fullWidth onClick={() => setShowRatingModal(false)}>
              Отмена
            </Button>
          </div>
        </div>
      </Modal>
    </main>
  )
}
