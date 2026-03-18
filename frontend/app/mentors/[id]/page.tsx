/**
 * Mentor Profile Page
 * Detailed mentor information with chat functionality
 */

'use client'

import { useState } from 'react'
import { useParams } from 'next/navigation'
import { Star, MapPin, Clock, DollarSign, Calendar, CheckCircle, MessageCircle, ArrowLeft } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'
import Link from 'next/link'
import { ChatButton } from '@/components/ChatButton'

// Mock data - в реальности будет загружаться из API
const mentorData = {
  id: 1,
  name: 'Иван Петров',
  specialty: 'JavaScript / React',
  rating: 4.9,
  reviews: 152,
  hourRate: 1500,
  location: 'Москва',
  experience: '8 лет',
  avatar: '👨‍💼',
  bio: 'Опытный Full-Stack разработчик с более чем 8-летним опытом работы в коммерческой разработке. Специализируюсь на JavaScript, React и Node.js. Провёл более 500 успешных менторских сессий.',
  tags: ['JavaScript', 'React', 'Node.js', 'TypeScript', 'Next.js', 'GraphQL'],
  availability: 'Доступен каждый день',
  languages: ['Русский', 'English'],
  about: `
Я начал свой путь в IT в 2015 году и за это время работал в различных компаниях - от небольших стартапов до крупных корпораций. 

Моя специализация:
• Frontend: React, Next.js, TypeScript, Redux
• Backend: Node.js, Express, NestJS
• Databases: PostgreSQL, MongoDB
• Tools: Git, Docker, AWS

Я помогаю студентам:
✓ Освоить современные технологии
✓ Подготовиться к собеседованиям
✓ Создать портфолио проектов
✓ Начать карьеру в IT
  `,
  achievements: [
    '500+ успешных сессий',
    '95% положительных отзывов',
    'Senior Developer в крупной компании',
    'Автор технических статей'
  ]
}

export default function MentorProfilePage() {
  const params = useParams()
  const mentorId = params?.id ? parseInt(params.id as string) : 1
  const [showChat, setShowChat] = useState(false)

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
            <div className="w-32 h-32 bg-gradient-to-br from-indigo-400 to-purple-500 rounded-full flex items-center justify-center text-6xl">
              {mentorData.avatar}
            </div>
          </div>

          {/* Info */}
          <div className="flex-1">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{mentorData.name}</h1>
                <p className="text-lg text-indigo-600 font-semibold">{mentorData.specialty}</p>
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
                      i < Math.floor(mentorData.rating)
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-gray-300'
                    }`}
                  />
                ))}
              </div>
              <span className="text-lg font-semibold text-gray-900">{mentorData.rating}</span>
              <span className="text-gray-600">({mentorData.reviews} отзывов)</span>
            </div>

            {/* Meta Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-2 text-gray-600">
                <DollarSign className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500">Ставка</p>
                  <p className="font-semibold">{mentorData.hourRate}₽/час</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <Clock className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500">Опыт</p>
                  <p className="font-semibold">{mentorData.experience}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <MapPin className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500">Локация</p>
                  <p className="font-semibold">{mentorData.location}</p>
                </div>
              </div>
              <div className="flex items-center gap-2 text-gray-600">
                <CheckCircle className="w-5 h-5 text-indigo-600" />
                <div>
                  <p className="text-sm text-gray-500">Статус</p>
                  <p className="font-semibold">Доступен</p>
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
            <h2 className="text-xl font-bold text-gray-900 mb-4">О менторе</h2>
            <p className="text-gray-700 whitespace-pre-line leading-relaxed">
              {mentorData.about}
            </p>
          </Card>

          {/* Achievements */}
          <Card padding="lg">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Достижения</h2>
            <ul className="space-y-2">
              {mentorData.achievements.map((achievement, index) => (
                <li key={index} className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{achievement}</span>
                </li>
              ))}
            </ul>
          </Card>

          {/* Reviews */}
          <Card padding="lg">
            <h2 className="text-xl font-bold text-gray-900 mb-4">Отзывы</h2>
            <div className="space-y-4">
              {/* Mock reviews */}
              {[1, 2].map((review) => (
                <div key={review} className="border-b border-gray-200 pb-4 last:border-0">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                      <span className="text-sm font-semibold">A</span>
                    </div>
                    <div>
                      <p className="font-semibold text-gray-900">Анонимный студент</p>
                      <div className="flex items-center gap-1">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                        ))}
                      </div>
                    </div>
                  </div>
                  <p className="text-gray-700 text-sm">
                    Отличный ментор! Очень помогло в подготовке к собеседованию.
                  </p>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          {/* Skills */}
          <Card padding="lg">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Навыки</h2>
            <div className="flex flex-wrap gap-2">
              {mentorData.tags.map((tag) => (
                <Badge key={tag} variant="default" size="sm">
                  {tag}
                </Badge>
              ))}
            </div>
          </Card>

          {/* Languages */}
          <Card padding="lg">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Языки</h2>
            <div className="space-y-2">
              {mentorData.languages.map((lang) => (
                <div key={lang} className="flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  <span className="text-gray-700">{lang}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Availability */}
          <Card padding="lg">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Доступность</h2>
            <div className="flex items-center gap-3 text-gray-700">
              <Calendar className="w-5 h-5 text-indigo-600" />
              <span>{mentorData.availability}</span>
            </div>
          </Card>

          {/* CTA */}
          <Card padding="lg" className="bg-gradient-to-br from-indigo-50 to-purple-50 border-indigo-200">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Готовы начать?</h3>
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
          recipientId={mentorId}
          recipientName={mentorData.name}
        />
      )}
    </main>
  )
}
