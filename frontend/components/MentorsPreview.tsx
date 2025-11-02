'use client'

import { Users, Star, ArrowRight } from 'lucide-react'
import Link from 'next/link'

const mentors = [
  {
    id: 1,
    name: 'Артём Тарасов',
    role: 'Senior Software Engineer',
    experience: '5+ лет',
    rating: 5.0,
    specialties: ['Python', 'Highload', 'DevOps'],
    price: 'от 7,000 ₽',
    description: 'Ментор, который помогает инженерам расти в доходе и уровне. За 5+ лет прошёл и провёл 200+ собеседований.',
  },
  {
    id: 2,
    name: 'Сергей Филичкин',
    role: 'Python-ментор',
    experience: 'Много лет',
    rating: 5.0,
    specialties: ['Python', 'SQL', 'PostgreSQL'],
    price: 'от 2,827 ₽',
    description: 'Python-ментор, который доводит до оффера от 200К+ за 45 дней после выпуска',
  },
  {
    id: 3,
    name: 'Мария Григорьева',
    role: 'Senior Аналитик',
    experience: '4+ года',
    rating: 5.0,
    specialties: ['Python', 'SQL', 'Анализ данных'],
    price: 'от 2,000 ₽',
    description: 'Продуктовый аналитик с опытом в Учи.ру. Помогу выстроить карьерный план в IT.',
  },
]

export default function MentorsPreview() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Менторы
          </h2>
          <p className="text-gray-600">
            Наши менторы помогут вам подготовиться к собеседованию в топовых компаниях
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
          {mentors.map((mentor) => (
            <div
              key={mentor.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <div className="mb-4">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-3">
                  <Users className="w-8 h-8 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-1">
                  {mentor.name}
                </h3>
                <p className="text-sm text-gray-600 mb-2">
                  {mentor.role}
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <div className="flex items-center">
                    {[...Array(5)].map((_, i) => (
                      <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                    ))}
                  </div>
                  <span className="text-sm text-gray-600">{mentor.rating}</span>
                </div>
              </div>

              <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                {mentor.description}
              </p>

              <div className="mb-4">
                <div className="flex flex-wrap gap-2 mb-2">
                  {mentor.specialties.slice(0, 3).map((spec) => (
                    <span
                      key={spec}
                      className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
                    >
                      {spec}
                    </span>
                  ))}
                  {mentor.specialties.length > 3 && (
                    <span className="px-2 py-1 text-xs text-gray-600">...</span>
                  )}
                </div>
                <div className="text-lg font-semibold text-gray-900">
                  {mentor.price}
                </div>
              </div>

              <Link
                href={`/mentors/${mentor.id}`}
                className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center text-sm group"
              >
                Подробнее
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link href="/mentors" className="btn-primary inline-flex items-center">
            <Users className="mr-2 w-5 h-5" />
            Все менторы
          </Link>
        </div>
      </div>
    </section>
  )
}

