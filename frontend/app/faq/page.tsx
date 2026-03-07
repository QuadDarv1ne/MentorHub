'use client'

import { useState } from 'react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import { ChevronDown, Search, MessageCircle } from 'lucide-react'

const faqs = [
  {
    id: 1,
    category: 'Общие вопросы',
    question: 'Что такое MentorHub?',
    answer: 'MentorHub - это платформа для профессионального менторства в IT. Мы соединяем опытных специалистов с теми, кто стремится развивать свои навыки и построить карьеру в технологиях.'
  },
  {
    id: 2,
    category: 'Общие вопросы',
    question: 'Как начать работать на платформе?',
    answer: 'Зарегистрируйтесь на сайте, создайте профиль, укажите свои цели. Если вы ищете ментора, просмотрите каталог и выберите подходящего специалиста.'
  },
  {
    id: 3,
    category: 'Обучение',
    question: 'Какие курсы доступны на платформе?',
    answer: 'У нас есть курсы по программированию (JavaScript, Python, Java), фронтенд-разработке (React, Vue), бэкенду (Node.js, Django, FastAPI), DevOps и Data Science.'
  },
  {
    id: 4,
    category: 'Обучение',
    question: 'Как долго длится обучение?',
    answer: 'Длительность зависит от выбранного курса и вашего темпа. Обычно курсы занимают от 4 недель до 3 месяцев при регулярных занятиях.'
  },
  {
    id: 5,
    category: 'Менторство',
    question: 'Как выбрать ментора?',
    answer: 'Посмотрите профили менторов, их рейтинги и отзывы. Ищите специалиста с опытом в интересующей вас области и обратите внимание на доступность.'
  },
  {
    id: 6,
    category: 'Менторство',
    question: 'Сколько стоит менторская сессия?',
    answer: 'Цена зависит от опыта ментора и сложности темы. В среднем сессии стоят от 1000 до 2500 рублей за час.'
  },
  {
    id: 7,
    category: 'Оплата',
    question: 'Какие способы оплаты вы принимаете?',
    answer: 'Мы принимаем платежи через банковские карты (VISA, MasterCard), Яндекс.Касса, А-Банк и другие системы. Все платежи защищены.'
  },
  {
    id: 8,
    category: 'Оплата',
    question: 'Есть ли бесплатный пробный период?',
    answer: 'Да, все новые пользователи получают 3 дня бесплатного доступа. За это время вы можете изучить курсы и пообщаться с менторами.'
  },
  {
    id: 9,
    category: 'Поддержка',
    question: 'Как связаться со службой поддержки?',
    answer: 'Email: maksimqwe42@mail.ru | Telegram: @quadd4rv1n7 | Телефон: +7 915 048-02-49. Ответ в течение 2-4 часов.'
  },
  {
    id: 10,
    category: 'Поддержка',
    question: 'Что делать, если я забыл пароль?',
    answer: 'На странице входа нажмите "Забыли пароль?", введите email. Мы отправим ссылку для восстановления пароля.'
  },
  {
    id: 11,
    category: 'Сертификаты',
    question: 'Выдаются ли сертификаты?',
    answer: 'Да, после успешного завершения курса вы получите сертификат MentorHub для добавления в LinkedIn и резюме.'
  },
  {
    id: 12,
    category: 'Сертификаты',
    question: 'Признаются ли сертификаты работодателями?',
    answer: 'Сертификаты MentorHub признаются многими IT-компаниями. Рекомендуем сочетать обучение с практическими проектами.'
  }
]

const categories = ['Все', ...Array.from(new Set(faqs.map(f => f.category)))]

export default function FAQPage() {
  const [expandedId, setExpandedId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('Все')

  const filtered = faqs.filter(faq => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
      faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    
    const matchesCategory = selectedCategory === 'Все' || faq.category === selectedCategory
    
    return matchesSearch && matchesCategory
  })

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <div className="mb-10 text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-3">Часто задаваемые вопросы</h1>
        <p className="text-xl text-gray-600">Найдите ответы на вопросы о MentorHub</p>
      </div>

      <div className="mb-8">
        <div className="relative">
          <Search className="absolute left-4 top-4 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder="Поиск по вопросам..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-8">
        {categories.map((category) => (
          <button
            key={category}
            onClick={() => setSelectedCategory(category)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              selectedCategory === category
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
            }`}
          >
            {category}
          </button>
        ))}
      </div>

      <div className="space-y-4 mb-10">
        {filtered.map((faq) => (
          <Card
            key={faq.id}
            padding="md"
            hover
            onClick={() => setExpandedId(expandedId === faq.id ? null : faq.id)}
            className="cursor-pointer"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">{faq.question}</h3>
                <p className="text-sm text-indigo-600 font-medium">{faq.category}</p>
              </div>
              <ChevronDown
                className={`h-6 w-6 text-gray-400 transition-transform flex-shrink-0 ${
                  expandedId === faq.id ? 'rotate-180' : ''
                }`}
              />
            </div>

            {expandedId === faq.id && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
              </div>
            )}
          </Card>
        ))}

        {filtered.length === 0 && (
          <Card padding="lg" className="text-center">
            <MessageCircle className="h-12 w-12 text-gray-300 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Вопросы не найдены</h3>
            <p className="text-gray-600 mb-4">Попробуйте изменить поисковый запрос</p>
            <Button
              variant="outline"
              onClick={() => {
                setSearchQuery('')
                setSelectedCategory('Все')
              }}
            >
              Сбросить фильтры
            </Button>
          </Card>
        )}
      </div>

      <Card padding="lg" className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200">
        <div className="text-center">
          <MessageCircle className="h-8 w-8 text-indigo-600 mx-auto mb-3" />
          <h3 className="text-lg font-bold text-gray-900 mb-2">Не нашли ответ?</h3>
          <p className="text-gray-700 mb-6">Свяжитесь с нашей командой поддержки!</p>
          <div className="flex flex-wrap justify-center gap-3">
            <a href="mailto:maksimqwe42@mail.ru">
              <Button variant="secondary">📧 maksimqwe42@mail.ru</Button>
            </a>
            <a href="https://t.me/quadd4rv1n7">
              <Button variant="secondary">📱 @quadd4rv1n7</Button>
            </a>
            <a href="tel:+79150480249">
              <Button variant="secondary">☎️ +7 915 048-02-49</Button>
            </a>
          </div>
        </div>
      </Card>
    </main>
  )
}
