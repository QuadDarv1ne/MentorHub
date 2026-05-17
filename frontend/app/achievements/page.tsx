'use client'

import { useState } from 'react'
import { Award, Trophy, Star, Share2, Download, Filter } from 'lucide-react'
import Badge from '@/components/ui/Badge'

interface Certificate {
  id: string
  title: string
  issuer: string
  dateIssued: string
  expiryDate?: string
  credentialId: string
  credentialUrl: string
  image: string
  skills: string[]
}

interface Achievement {
  id: string
  title: string
  description: string
  icon: string
  date: string
  category: string
  points: number
}

export default function AchievementsPage() {
  const [activeTab, setActiveTab] = useState<'certificates' | 'achievements'>('certificates')
  const [filterCategory, setFilterCategory] = useState('all')

  const certificates: Certificate[] = [
    {
      id: '1',
      title: 'React Advanced Patterns',
      issuer: 'Coursera',
      dateIssued: '2024-10-15',
      expiryDate: '2026-10-15',
      credentialId: 'UC123456',
      credentialUrl: 'https://coursera.org/verify/UC123456',
      image: '⚛️',
      skills: ['React', 'JavaScript', 'Web Development']
    },
    {
      id: '2',
      title: 'Node.js Backend Development',
      issuer: 'Udemy',
      dateIssued: '2024-08-20',
      credentialId: 'UD789012',
      credentialUrl: 'https://udemy.com/certificate/UD789012',
      image: '🚀',
      skills: ['Node.js', 'Express', 'MongoDB']
    },
    {
      id: '3',
      title: 'TypeScript Professional',
      issuer: 'LinkedIn Learning',
      dateIssued: '2024-07-10',
      credentialId: 'LI345678',
      credentialUrl: 'https://linkedin.com/learning/certificates/LI345678',
      image: '📘',
      skills: ['TypeScript', 'JavaScript', 'OOP']
    },
    {
      id: '4',
      title: 'AWS Solutions Architect',
      issuer: 'Amazon Web Services',
      dateIssued: '2024-05-30',
      expiryDate: '2027-05-30',
      credentialId: 'AWS654321',
      credentialUrl: 'https://aws.amazon.com/verification/AWS654321',
      image: '☁️',
      skills: ['AWS', 'Cloud Architecture', 'DevOps']
    }
  ]

  const achievements: Achievement[] = [
    {
      id: '1',
      title: 'Первая сессия',
      description: 'Провел первую менторскую сессию',
      icon: '🎓',
      date: '2024-01-15',
      category: 'milestone',
      points: 10
    },
    {
      id: '2',
      title: 'Отличный ментор',
      description: 'Получил 100 положительных отзывов',
      icon: '⭐',
      date: '2024-03-20',
      category: 'reviews',
      points: 50
    },
    {
      id: '3',
      title: 'Друг всегда на связи',
      description: 'Провел 50 сессий',
      icon: '🤝',
      date: '2024-05-10',
      category: 'sessions',
      points: 100
    },
    {
      id: '4',
      title: 'Мастер менторства',
      description: 'Провел 150 сессий',
      icon: '👑',
      date: '2024-09-25',
      category: 'sessions',
      points: 200
    },
    {
      id: '5',
      title: 'Экспертное знание',
      description: 'Помогал в 5 разных специализациях',
      icon: '🔬',
      date: '2024-06-15',
      category: 'expertise',
      points: 75
    },
    {
      id: '6',
      title: 'Спешу на помощь',
      description: 'Ответил на вопрос за 5 минут',
      icon: '⚡',
      date: '2024-10-01',
      category: 'speed',
      points: 25
    }
  ]

  const totalPoints = achievements.reduce((sum, a) => sum + a.points, 0)
  const categories = ['all', 'milestone', 'reviews', 'sessions', 'expertise', 'speed']
  const filteredAchievements = filterCategory === 'all' 
    ? achievements 
    : achievements.filter(a => a.category === filterCategory)

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Заголовок */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h1 className="text-3xl font-bold text-gray-900">Мои достижения</h1>
            <div className="text-center bg-white rounded-lg shadow p-4">
              <p className="text-3xl font-bold text-indigo-600">{totalPoints}</p>
              <p className="text-sm text-gray-600">Всего очков</p>
            </div>
          </div>
          <p className="text-gray-600">Сертификаты, значки и достижения на платформе MentorHub</p>
        </div>

        {/* Вкладки */}
        <div className="mb-6 flex space-x-2">
          <button
            onClick={() => setActiveTab('certificates')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
              activeTab === 'certificates'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            <Award size={20} />
            <span>Сертификаты ({certificates.length})</span>
          </button>
          <button
            onClick={() => setActiveTab('achievements')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors flex items-center space-x-2 ${
              activeTab === 'achievements'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            <Trophy size={20} />
            <span>Достижения ({achievements.length})</span>
          </button>
        </div>

        {/* Вкладка: Сертификаты */}
        {activeTab === 'certificates' && (
          <div className="space-y-4">
            {certificates.length === 0 ? (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Award size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Нет сертификатов</h3>
                <p className="text-gray-600">Получайте сертификаты, проходя курсы и обучение</p>
              </div>
            ) : (
              certificates.map(cert => (
                <div key={cert.id} className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start space-x-4 flex-1">
                      <div className="text-5xl">{cert.image}</div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-2">
                          <h3 className="text-xl font-semibold text-gray-900">{cert.title}</h3>
                          <span className="text-sm text-gray-600">{cert.issuer}</span>
                        </div>
                        <p className="text-gray-600 text-sm mb-3">
                          Выдан: {new Date(cert.dateIssued).toLocaleDateString('ru-RU')}
                          {cert.expiryDate && (
                            <span> • Действителен до: {new Date(cert.expiryDate).toLocaleDateString('ru-RU')}</span>
                          )}
                        </p>
                        <div className="flex flex-wrap gap-2 mb-3">
                          {cert.skills.map(skill => (
                            <Badge key={skill} variant="info" className="text-xs">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                        <p className="text-xs text-gray-500">ID: {cert.credentialId}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2 ml-4">
                      <a
                        href={cert.credentialUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors"
                        title="Перейти к сертификату"
                      >
                        <Star size={20} />
                      </a>
                      <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="Поделиться">
                        <Share2 size={20} />
                      </button>
                      <button className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="Загрузить">
                        <Download size={20} />
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {/* Вкладка: Достижения */}
        {activeTab === 'achievements' && (
          <div>
            {/* Фильтр категорий */}
            <div className="mb-6 bg-white rounded-lg shadow p-4">
              <div className="flex items-center space-x-2 flex-wrap gap-2">
                <Filter size={20} className="text-gray-600" />
                {categories.map(cat => (
                  <button
                    key={cat}
                    onClick={() => setFilterCategory(cat)}
                    className={`px-4 py-1 rounded-full text-sm font-medium transition-colors ${
                      filterCategory === cat
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {cat === 'all' && 'Все'}
                    {cat === 'milestone' && '📍 Вехи'}
                    {cat === 'reviews' && '⭐ Отзывы'}
                    {cat === 'sessions' && '🤝 Сессии'}
                    {cat === 'expertise' && '🔬 Экспертиза'}
                    {cat === 'speed' && '⚡ Скорость'}
                  </button>
                ))}
              </div>
            </div>

            {/* Сетка достижений */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAchievements.map(achievement => (
                <div
                  key={achievement.id}
                  className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6 relative overflow-hidden group"
                >
                  {/* Background gradient */}
                  <div className="absolute inset-0 bg-gradient-to-br from-indigo-50 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />

                  {/* Content */}
                  <div className="relative z-10">
                    <div className="text-4xl mb-3">{achievement.icon}</div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">{achievement.title}</h3>
                    <p className="text-gray-600 text-sm mb-3">{achievement.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        {new Date(achievement.date).toLocaleDateString('ru-RU')}
                      </span>
                      <span className="bg-indigo-100 text-indigo-700 text-xs font-semibold px-3 py-1 rounded-full">
                        +{achievement.points} pts
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {filteredAchievements.length === 0 && (
              <div className="bg-white rounded-lg shadow p-12 text-center">
                <Trophy size={48} className="mx-auto text-gray-300 mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Нет достижений в этой категории</h3>
                <p className="text-gray-600">Продолжайте менторить, чтобы получить достижения!</p>
              </div>
            )}
          </div>
        )}

        {/* Бонусная информация */}
        <div className="mt-12 bg-gradient-to-r from-indigo-600 to-indigo-700 rounded-lg shadow-lg p-8 text-white">
          <h2 className="text-2xl font-bold mb-4">Прогресс к следующему уровню</h2>
          <div className="space-y-4">
            <div>
              <div className="flex justify-between items-center mb-2">
                <span>Очки мастерства</span>
                <span className="font-semibold">{totalPoints} / 500</span>
              </div>
              <div className="bg-white/20 rounded-full h-3 overflow-hidden">
                <div
                  className="bg-white h-full rounded-full transition-all duration-500 progress-width"
                  style={{ '--progress-width': `${Math.min((totalPoints / 500) * 100, 100)}%` } as React.CSSProperties}
                />
              </div>
            </div>
            <p className="text-sm text-indigo-100">
              До уровня &ldquo;Легендарный ментор&rdquo; осталось {Math.max(0, 500 - totalPoints)} очков
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
