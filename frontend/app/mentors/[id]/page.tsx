'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Modal from '@/components/ui/Modal'
import Tabs from '@/components/ui/Tabs'
import { Star, MapPin, Clock, DollarSign, Calendar, MessageCircle, Award, Users, BookOpen, ArrowRight, Send } from 'lucide-react'

const mentorData = {
  id: 1,
  name: 'Иван Петров',
  photo: '👨‍💼',
  specialty: 'JavaScript / React',
  rating: 4.9,
  reviews: 152,
  hourRate: 1500,
  location: 'Москва',
  experience: '8 лет',
  bio: 'Опытный Full-Stack разработчик. Специализируюсь на JavaScript, React и Node.js. Помог более 150 людям подготовиться к собеседованиям и улучшить свои навыки.',
  description: 'Я помогаю разработчикам разных уровней - от новичков до middle разработчиков. Мой подход основан на практике: мы разбираем реальные задачи, пишем код, делаем code reviews.',
  tags: ['JavaScript', 'React', 'Node.js', 'TypeScript', 'Next.js', 'REST API'],
  availability: 'Доступен каждый день, 10:00-22:00',
  portfolio: [
    { title: 'E-commerce платформа', description: 'React + Node.js', link: '#' },
    { title: 'Real-time chat', description: 'WebSocket + Next.js', link: '#' },
    { title: 'Analytics Dashboard', description: 'React + TypeScript', link: '#' }
  ],
  successStories: 5,
  totalSessions: 152,
  responseTime: '< 1 часа'
}

const reviews = [
  {
    id: 1,
    author: 'Алексей М.',
    rating: 5,
    date: '2 недели назад',
    text: 'Отличный ментор! Помог подготовиться к собеседованию на React. Понятно объяснял сложные концепции. Очень рекомендую!',
    avatar: '👨'
  },
  {
    id: 2,
    author: 'Мария К.',
    rating: 5,
    date: '1 месяц назад',
    text: 'Прошли с Иваном несколько сессий по Node.js. Очень профессиональный подход, уделяет внимание деталям. Спасибо за помощь!',
    avatar: '👩'
  },
  {
    id: 3,
    author: 'Сергей Н.',
    rating: 4,
    date: '2 месяца назад',
    text: 'Хороший ментор, знает материал. Было полезно, но нужна была еще больше практики.',
    avatar: '👨'
  }
]

const timeSlots = [
  { time: '10:00', available: true },
  { time: '11:00', available: true },
  { time: '14:00', available: false },
  { time: '15:00', available: true },
  { time: '16:00', available: true },
  { time: '18:00', available: true },
  { time: '19:00', available: true },
  { time: '20:00', available: true }
]

export default function MentorDetailPage() {
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [selectedDate, setSelectedDate] = useState('')
  const [selectedTime, setSelectedTime] = useState('')
  const [selectedDuration, setSelectedDuration] = useState('60')
  const [message, setMessage] = useState('')

  const handleBooking = () => {
    if (selectedDate && selectedTime) {
      alert(`Сессия забронирована на ${selectedDate} в ${selectedTime}`)
      setShowBookingModal(false)
    }
  }

  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      {/* Header */}
      <div className="mb-8">
        <div className="flex flex-col md:flex-row items-start gap-6 mb-6">
          {/* Profile */}
          <div className="flex-1">
            <div className="flex items-start gap-4 mb-6">
              <div className="text-7xl">{mentorData.photo}</div>
              <div className="flex-1">
                <h1 className="text-4xl font-bold text-gray-900 mb-2">{mentorData.name}</h1>
                <p className="text-xl text-indigo-600 font-semibold mb-3">{mentorData.specialty}</p>
                
                {/* Rating */}
                <div className="flex items-center gap-4 mb-4">
                  <div className="flex items-center gap-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-5 w-5 ${
                          i < Math.floor(mentorData.rating)
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <span className="text-lg font-bold text-gray-900">{mentorData.rating}</span>
                  <span className="text-gray-600">({mentorData.reviews} отзывов)</span>
                </div>

                {/* Info Grid */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="flex items-center gap-2">
                    <DollarSign className="h-5 w-5 text-indigo-600" />
                    <span className="text-sm text-gray-600">{mentorData.hourRate}₽/час</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-indigo-600" />
                    <span className="text-sm text-gray-600">{mentorData.experience}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-indigo-600" />
                    <span className="text-sm text-gray-600">{mentorData.location}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <MessageCircle className="h-5 w-5 text-indigo-600" />
                    <span className="text-sm text-gray-600">{mentorData.responseTime}</span>
                  </div>
                </div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex gap-3">
              <Button variant="primary" size="lg" onClick={() => setShowBookingModal(true)}>
                <Calendar className="h-5 w-5 mr-2" />
                Забронировать сессию
              </Button>
              <Button variant="outline" size="lg">
                <MessageCircle className="h-5 w-5 mr-2" />
                Отправить сообщение
              </Button>
            </div>
          </div>

          {/* Stats */}
          <div className="w-full md:w-64 space-y-3">
            <Card padding="md" className="text-center">
              <div className="text-3xl font-bold text-indigo-600 mb-1">{mentorData.totalSessions}</div>
              <div className="text-sm text-gray-600">Проведено сессий</div>
            </Card>
            <Card padding="md" className="text-center">
              <div className="text-3xl font-bold text-green-600 mb-1">{mentorData.successStories}</div>
              <div className="text-sm text-gray-600">История успеха</div>
            </Card>
            <Card padding="md" className="text-center">
              <div className="text-2xl mb-1">🎯</div>
              <div className="text-sm text-gray-600">Специалист</div>
            </Card>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <Tabs
        tabs={[
          { id: 'about', label: '📝 О менторе', icon: BookOpen },
          { id: 'skills', label: '🎯 Навыки', icon: Award },
          { id: 'portfolio', label: '💼 Портфолио', icon: Users },
          { id: 'reviews', label: '⭐ Отзывы', icon: Star }
        ]}
        defaultTab={0}
      >
        {/* Tab 1: About */}
        <div className="space-y-6">
          <Card padding="lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">О себе</h3>
            <p className="text-lg text-gray-700 leading-relaxed mb-4">
              {mentorData.description}
            </p>
            <p className="text-gray-700 leading-relaxed">
              {mentorData.bio}
            </p>
          </Card>

          <Card padding="lg" className="bg-blue-50 border border-blue-200">
            <h4 className="font-semibold text-blue-900 mb-3">📅 Доступность</h4>
            <p className="text-blue-800">{mentorData.availability}</p>
          </Card>
        </div>

        {/* Tab 2: Skills */}
        <div>
          <Card padding="lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Компетенции</h3>
            <div className="flex flex-wrap gap-3">
              {mentorData.tags.map((tag) => (
                <Badge key={tag} variant="primary" size="md">
                  {tag}
                </Badge>
              ))}
            </div>
          </Card>
        </div>

        {/* Tab 3: Portfolio */}
        <div className="space-y-4">
          {mentorData.portfolio.map((project, idx) => (
            <Card key={idx} padding="md" hover>
              <div className="flex items-start justify-between">
                <div>
                  <h4 className="text-lg font-semibold text-gray-900 mb-1">{project.title}</h4>
                  <p className="text-gray-600 mb-3">{project.description}</p>
                </div>
                <ArrowRight className="h-5 w-5 text-indigo-600 flex-shrink-0" />
              </div>
            </Card>
          ))}
        </div>

        {/* Tab 4: Reviews */}
        <div className="space-y-4">
          {reviews.map((review) => (
            <Card key={review.id} padding="md">
              <div className="flex items-start gap-4">
                <div className="text-3xl flex-shrink-0">{review.avatar}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">{review.author}</h4>
                    <span className="text-sm text-gray-500">{review.date}</span>
                  </div>
                  <div className="flex items-center gap-1 mb-2">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`h-4 w-4 ${
                          i < review.rating
                            ? 'fill-yellow-400 text-yellow-400'
                            : 'text-gray-300'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-gray-700">{review.text}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </Tabs>

      {/* Booking Modal */}
      <Modal
        isOpen={showBookingModal}
        onClose={() => setShowBookingModal(false)}
        title="Забронировать сессию"
        size="lg"
      >
        <div className="space-y-6">
          {/* Date Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Выберите дату
            </label>
            <div className="grid grid-cols-3 gap-2 mb-4">
              {[1, 2, 3, 4, 5, 6, 7].map((day) => (
                <button
                  key={day}
                  onClick={() => setSelectedDate(`21 ноября`)}
                  className={`p-2 rounded-lg text-sm font-medium transition-all ${
                    selectedDate === `21 ноября`
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}
                >
                  {20 + day} нояб.
                </button>
              ))}
            </div>
          </div>

          {/* Time Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-3">
              Выберите время
            </label>
            <div className="grid grid-cols-4 gap-2 mb-4">
              {timeSlots.map((slot) => (
                <button
                  key={slot.time}
                  onClick={() => slot.available && setSelectedTime(slot.time)}
                  disabled={!slot.available}
                  className={`p-2 rounded-lg text-sm font-medium transition-all ${
                    slot.available
                      ? selectedTime === slot.time
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                      : 'bg-gray-50 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  {slot.time}
                </button>
              ))}
            </div>
          </div>

          {/* Duration */}
          <div>
            <label htmlFor="duration" className="block text-sm font-semibold text-gray-900 mb-3">
              Длительность сессии
            </label>
            <select
              id="duration"
              value={selectedDuration}
              onChange={(e) => setSelectedDuration(e.target.value)}
              title="Выберите длительность сессии"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="30">30 минут (750₽)</option>
              <option value="60">60 минут (1500₽)</option>
              <option value="90">90 минут (2250₽)</option>
            </select>
          </div>

          {/* Message */}
          <div>
            <label htmlFor="message" className="block text-sm font-semibold text-gray-900 mb-3">
              Сообщение ментору (опционально)
            </label>
            <textarea
              id="message"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Расскажите о себе и целях обучения..."
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              rows={4}
            />
          </div>

          {/* Summary */}
          {selectedDate && selectedTime && (
            <Card padding="md" className="bg-indigo-50 border border-indigo-200">
              <h4 className="font-semibold text-indigo-900 mb-2">Сводка бронирования</h4>
              <div className="space-y-1 text-sm text-indigo-800">
                <p>📅 Дата: {selectedDate}</p>
                <p>⏰ Время: {selectedTime}</p>
                <p>⏱️ Длительность: {selectedDuration} минут</p>
                <p className="font-semibold mt-2">
                  Стоимость: {(parseInt(selectedDuration) / 60) * 1500}₽
                </p>
              </div>
            </Card>
          )}

          {/* Buttons */}
          <div className="flex gap-3 pt-4">
            <Button variant="primary" fullWidth onClick={handleBooking} disabled={!selectedDate || !selectedTime}>
              <Send className="h-4 w-4 mr-2" />
              Забронировать сессию
            </Button>
            <Button variant="outline" fullWidth onClick={() => setShowBookingModal(false)}>
              Отмена
            </Button>
          </div>
        </div>
      </Modal>
    </main>
  )
}
