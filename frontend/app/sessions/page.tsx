'use client'

import { useState, useEffect, useMemo, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { Calendar, Clock, Video, MessageSquare, Loader2, AlertCircle } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/ui/Modal'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/lib/hooks/useNotifications'
import { getMySessions, cancelSession, submitSessionRating, type Session } from '@/lib/api/sessions'

function formatDateTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long', year: 'numeric' })
}

function formatTime(iso: string): string {
  const d = new Date(iso)
  return d.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

function isUpcomingStatus(status: string): boolean {
  return ['scheduled', 'confirmed', 'pending'].includes(status)
}

export default function SessionsPage() {
  const router = useRouter()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [sessions, setSessions] = useState<Session[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [showRatingModal, setShowRatingModal] = useState(false)
  const [activeTab, setActiveTab] = useState<'upcoming' | 'completed'>('upcoming')
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [rating, setRating] = useState(5)
  const [feedback, setFeedback] = useState('')
  const [actionLoading, setActionLoading] = useState<number | null>(null)
  const { success, error } = useToast()

  const fetchSessions = useCallback(async () => {
    setIsLoading(true)
    setError(null)
    try {
      const data = await getMySessions()
      setSessions(data)
    } catch {
      setError('Не удалось загрузить сессии')
      setSessions([])
    } finally {
      setIsLoading(false)
    }
  }, [])

  // Проверка авторизации
  useEffect(() => {
    if (authLoading) return
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/sessions')
    } else {
      fetchSessions()
    }
  }, [isAuthenticated, authLoading, router, fetchSessions])

  const upcomingSessions = useMemo(
    () => sessions.filter(s => isUpcomingStatus(s.status)),
    [sessions]
  )
  const completedSessions = useMemo(
    () => sessions.filter(s => s.status === 'completed'),
    [sessions]
  )

  const nextSession = useMemo(() => {
    return upcomingSessions
      .slice()
      .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime())[0]
  }, [upcomingSessions])

  const handleCancelSession = async (id: number) => {
    setActionLoading(id)
    try {
      await cancelSession(id)
      success('Сессия отменена')
      await fetchSessions()
    } catch {
      setError('Не удалось отменить сессию')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSubmitRating = async () => {
    if (!selectedSession) return
    setActionLoading(-1)
    try {
      await submitSessionRating({
        reviewed_id: selectedSession.mentor_id,
        rating,
        comment: feedback || undefined,
        session_id: selectedSession.id,
      })
      success('Спасибо! Ваш отзыв отправлен')
      setRating(5)
      setFeedback('')
      setShowRatingModal(false)
      setSelectedSession(null)
    } catch {
      error('Не удалось отправить отзыв')
    } finally {
      setActionLoading(null)
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Загрузка сессий...</p>
        </div>
      </div>
    )
  }

  const SessionCard = ({ session, isUpcoming }: { session: Session; isUpcoming: boolean }) => {
    const mentorName = session.mentor?.full_name || 'Ментор'
    const mentorPhoto = session.mentor?.avatar_url || ''

    return (
      <Card padding="lg" className="mb-4">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="flex gap-4 flex-1">
            {mentorPhoto ? (
              <img src={mentorPhoto} alt={mentorName} className="w-14 h-14 rounded-full object-cover flex-shrink-0" />
            ) : (
              <div className="w-14 h-14 rounded-full bg-indigo-100 flex items-center justify-center flex-shrink-0">
                <span className="text-lg font-bold text-indigo-600">{mentorName[0]}</span>
              </div>
            )}
            <div className="flex-1">
              <h3 className="text-xl font-bold text-gray-900 mb-1">{mentorName}</h3>

              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4 text-indigo-600" />
                  <span>{formatDateTime(session.scheduled_at)}</span>
                </div>
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-indigo-600" />
                  <span>{formatTime(session.scheduled_at)} ({session.duration_minutes} мин)</span>
                </div>
                <div className="flex items-center gap-2">
                  <Video className="h-4 w-4 text-indigo-600" />
                  <span>{session.meeting_link ? 'Видеозвонок' : 'Не определено'}</span>
                </div>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-indigo-600" />
                  <span className="text-gray-900 font-semibold">{session.topic || 'Без темы'}</span>
                </div>
              </div>

              {isUpcoming && session.notes && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-900">
                  📝 {session.notes}
                </div>
              )}

              {isUpcoming && session.meeting_link && (
                <a
                  href={session.meeting_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block mt-2 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition-colors"
                >
                  Присоединиться к сессии
                </a>
              )}
            </div>
          </div>

          <div className="flex flex-col items-end justify-between md:w-48">
            <div className="text-right">
              <Badge variant={isUpcoming ? 'success' : 'info'}>
                {isUpcoming ? 'Предстоящая' : 'Завершена'}
              </Badge>
            </div>

            <div className="flex gap-2 w-full mt-4">
              {isUpcoming ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleCancelSession(session.id)}
                  disabled={actionLoading === session.id}
                >
                  {actionLoading === session.id ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    'Отмена'
                  )}
                </Button>
              ) : (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSelectedSession(session)
                    setShowRatingModal(true)
                  }}
                >
                  Оценить
                </Button>
              )}
            </div>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Мои сессии</h1>
        <p className="text-gray-600 text-lg">Управляйте вашими занятиями с менторами</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <p className="text-sm text-red-800">{error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-indigo-600 mb-1">{sessions.length}</div>
          <div className="text-sm text-gray-600">Всего сессий</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">{completedSessions.length}</div>
          <div className="text-sm text-gray-600">Завершено</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-blue-600 mb-1">{upcomingSessions.length}</div>
          <div className="text-sm text-gray-600">Предстоящие</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-lg font-bold text-purple-600 mb-1">Следующая</div>
          <div className="text-sm text-gray-600">
            {nextSession ? `${formatDateTime(nextSession.scheduled_at)} в ${formatTime(nextSession.scheduled_at)}` : '—'}
          </div>
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
          Предстоящие ({upcomingSessions.length})
        </button>
        <button
          onClick={() => setActiveTab('completed')}
          className={`px-4 py-3 font-semibold transition-all border-b-2 ${
            activeTab === 'completed'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}
        >
          Завершенные ({completedSessions.length})
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
        title={`Оценить сессию с ${selectedSession?.mentor?.full_name || 'Ментором'}`}
        size="md"
      >
        <div className="space-y-6">
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
