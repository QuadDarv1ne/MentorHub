'use client'

import { Code, ArrowRight } from 'lucide-react'
import Link from 'next/link'

const tasks = [
  { id: 12, title: 'Объединение интервалов', difficulty: 'Сложная', company: 'Яндекс', progress: 70 },
  { id: 78, title: 'Сумма двух', difficulty: 'Легкая', company: 'Яндекс', progress: 89 },
]

export default function CodingTasks() {
  return (
    <section className="section-padding bg-gray-50">
      <div className="container-custom">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Задачи на код
          </h2>
          <p className="text-gray-600">
            Решайте задачи на код в нашей песочнице и проверяйте свои навыки в программировании
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          {tasks.map((task) => (
            <div
              key={task.id}
              className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-start justify-between mb-3">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-1">
                    {task.id}. {task.title}
                  </h3>
                  <div className="flex items-center gap-3 text-sm text-gray-600">
                    <span className={`px-2 py-1 rounded ${
                      task.difficulty === 'Легкая' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-red-100 text-red-800'
                    }`}>
                      {task.difficulty}
                    </span>
                    <span>{task.company}</span>
                  </div>
                </div>
              </div>
              <div className="mb-4">
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-600">Прогресс</span>
                  <span className="text-gray-900 font-medium">{task.progress}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-primary-600 h-2 rounded-full transition-all"
                    style={{ width: `${task.progress}%` }}
                  />
                </div>
              </div>
              <Link
                href={`/tasks/${task.id}`}
                className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center group"
              >
                Перейти
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
            </div>
          ))}
        </div>

        <div className="text-center">
          <Link href="/tasks" className="btn-secondary inline-flex items-center">
            <Code className="mr-2 w-5 h-5" />
            Все задачи
          </Link>
        </div>
      </div>
    </section>
  )
}

