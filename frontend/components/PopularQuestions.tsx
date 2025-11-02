'use client'

import { ArrowRight } from 'lucide-react'
import Link from 'next/link'

const popularTopics = [
  { name: 'Python', title: 'Часто задаваемые вопросы, ответы на которые обязан знать каждый Python разработчик' },
  { name: 'Java', title: 'Лучшие вопросы по Java для подготовки к собеседованиям и изучения.' },
  { name: 'Golang', title: 'Список популярных вопросов по Go для подготовки к техническим интервью.' },
  { name: 'C#', title: 'Топ вопросов по C# для подготовки и углубления знаний в программировании.' },
  { name: 'C++', title: 'Топ вопросов по C++ для быстрого освоения ключевых концепций.' },
  { name: 'Frontend', title: 'Подборка самых частых вопросов на собеседованиях фронтенд разработчикам' },
  { name: 'SQL', title: 'SQL — мощный язык запросов для работы с СУБД. Каждый бэкендер должен знать ответ на эти вопросы' },
  { name: 'Computer Science', title: 'Компьютерные науки помогают создавать, анализировать и оптимизировать технологии.' },
  { name: 'Docker', title: 'Топ вопросов для понимания Docker и ключевых концепций контейнеризации.' },
  { name: 'Git', title: 'Основные вопросы по Git для успешного прохождения технического собеседования.' },
]

export default function PopularQuestions() {
  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Повторяйте самые популярные вопросы на собеседованиях
          </h2>
          <p className="text-lg text-gray-600">
            Быстро освежайте знания, через наши подборки вопросов
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {popularTopics.map((topic) => (
            <Link
              key={topic.name}
              href={`/questions/${topic.name.toLowerCase()}`}
              className="bg-gray-50 border border-gray-200 rounded-lg p-6 hover:shadow-md hover:border-primary-300 transition-all group"
            >
              <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-primary-600 transition-colors">
                {topic.name}
              </h3>
              <p className="text-sm text-gray-600 mb-3">
                {topic.title}
              </p>
              <span className="text-primary-600 font-medium inline-flex items-center text-sm group-hover:text-primary-700">
                Перейти к вопросам
                <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </span>
            </Link>
          ))}
        </div>
      </div>
    </section>
  )
}

