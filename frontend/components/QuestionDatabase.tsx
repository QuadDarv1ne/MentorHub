'use client'

import { BookOpen, ArrowRight } from 'lucide-react'
import Link from 'next/link'

const technologies = [
  { name: 'Python', description: 'Широко используется для веб-разработки, анализа данных, автоматизации, искусственного интеллекта и многих других областей', count: 100 },
  { name: 'JavaScript', description: 'Язык для создания интерактивных веб-страниц', count: 75 },
  { name: 'C#', description: 'Мощный и гибкий язык программирования, который позволяет создавать высокопроизводительные приложения', count: 54 },
]

export default function QuestionDatabase() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            База вопросов
          </h2>
          <p className="text-gray-600">
            Изучайте нужные вам технологии. Отвечайте на вопросы и отслеживайте свой прогресс
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {technologies.map((tech) => (
            <div
              key={tech.name}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="mb-4">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {tech.name}
                </h3>
                <p className="text-gray-600 text-sm mb-4">
                  {tech.description}
                </p>
                <div className="text-2xl font-bold text-primary-600">
                  {tech.count}
                </div>
              </div>
              <Link
                href={`/questions/${tech.name.toLowerCase()}`}
                className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center group"
              >
                Перейти
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          ))}
        </div>

        <div className="text-center mt-8">
          <Link href="/questions" className="btn-secondary inline-flex items-center">
            <BookOpen className="mr-2 w-5 h-5" />
            Все технологии
          </Link>
        </div>
      </div>
    </section>
  )
}

