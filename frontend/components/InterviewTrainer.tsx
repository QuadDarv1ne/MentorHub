'use client'

import { MessageSquare, ArrowRight } from 'lucide-react'
import Link from 'next/link'

const interviews = [
  {
    id: 12,
    category: 'Frontend',
    technology: 'JavaScript',
    answered: 7,
    total: 14,
  },
  {
    id: 7,
    category: 'Backend',
    technology: 'Python',
    answered: 7,
    total: 14,
  },
]

export default function InterviewTrainer() {
  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Тренажер собеседований
          </h2>
          <p className="text-gray-600">
            Отвечайте на вопросы и получайте аналитику по собеседованию. Найдите свои слабые и сильные места
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {interviews.map((interview) => (
            <div
              key={interview.id}
              className="bg-gray-50 border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="mb-4">
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Собеседование #{interview.id}
                </h3>
                <div className="flex items-center gap-3 text-sm mb-3">
                  <span className="px-2 py-1 bg-primary-100 text-primary-800 rounded">
                    {interview.category}
                  </span>
                  <span className="px-2 py-1 bg-secondary-100 text-secondary-800 rounded">
                    {interview.technology}
                  </span>
                </div>
                <div className="text-gray-600">
                  Отвечено {interview.answered}/{interview.total} вопросов
                </div>
              </div>
              <div className="mb-4">
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full"
                    style={{ width: `${(interview.answered / interview.total) * 100}%` }}
                  />
                </div>
              </div>
              <Link
                href={`/interview/${interview.id}`}
                className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center group"
              >
                Пройти собеседование
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}

