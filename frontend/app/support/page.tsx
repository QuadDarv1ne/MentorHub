'use client'

import { useState } from 'react'
import { Search, Send, Clock, CheckCircle, AlertCircle, MessageSquare, ChevronDown } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'

const faqs = [
  {
    id: 1,
    category: 'Общие вопросы',
    question: 'Что такое MentorHub?',
    answer: 'MentorHub - это платформа, которая соединяет опытных менторов с людьми, желающими развиваться. Здесь вы можете найти ментора в нужной области, забронировать сессию и получить персональную помощь.'
  },
  {
    id: 2,
    category: 'Общие вопросы',
    question: 'Как зарегистрироваться на платформе?',
    answer: 'Нажмите на кнопку "Регистрация" в главном меню, заполните форму с вашими данными и подтвердите адрес электронной почты. После этого вы сможете искать менторов и бронировать сессии.'
  },
  {
    id: 3,
    category: 'Сессии',
    question: 'Как забронировать сессию?',
    answer: 'Перейдите на страницу менторов, выберите подходящего ментора, нажмите "Забронировать сессию" и выберите удобную для вас дату и время. После подтверждения бронирования вы получите подробности сессии.'
  },
  {
    id: 4,
    category: 'Сессии',
    question: 'Что делать, если я хочу отменить сессию?',
    answer: 'Вы можете отменить сессию за 24 часа до её начала без штрафных санкций. Перейдите в раздел "Мои сессии", найдите нужную сессию и нажмите кнопку "Отмена".'
  },
  {
    id: 5,
    category: 'Оплата',
    question: 'Какие методы оплаты доступны?',
    answer: 'Мы принимаем платежи через банковские карты (Visa, MasterCard), Яндекс.Касса, PayPal и другие электронные кошельки. Все платежи защищены и обрабатываются защищённым сервером.'
  },
  {
    id: 6,
    category: 'Оплата',
    question: 'Есть ли возврат денег?',
    answer: 'Да, если вы отмените сессию за 24 часа до её начала, деньги будут возвращены на ваш счёт. При отмене позже 24 часов возврат не производится.'
  }
]

const supportTickets = [
  {
    id: 'TKT-001',
    subject: 'Проблема с платежом',
    status: 'open',
    createdAt: '2 часа назад',
    priority: 'high'
  },
  {
    id: 'TKT-002',
    subject: 'Вопрос о сертификате',
    status: 'waiting',
    createdAt: '1 день назад',
    priority: 'normal'
  },
  {
    id: 'TKT-003',
    subject: 'Спасибо за помощь!',
    status: 'closed',
    createdAt: '3 дня назад',
    priority: 'low'
  }
]

const getStatusInfo = (status: string) => {
  switch (status) {
    case 'open':
      return { label: 'Открыт', color: 'bg-blue-100 text-blue-700', icon: MessageSquare }
    case 'waiting':
      return { label: 'Ожидает ответа', color: 'bg-yellow-100 text-yellow-700', icon: Clock }
    case 'closed':
      return { label: 'Закрыт', color: 'bg-green-100 text-green-700', icon: CheckCircle }
    default:
      return { label: 'Неизвестно', color: 'bg-gray-100 text-gray-700', icon: AlertCircle }
  }
}

export default function SupportPage() {
  const [expandedFaq, setExpandedFaq] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)
  const [showTicketForm, setShowTicketForm] = useState(false)
  const [subject, setSubject] = useState('')
  const [message, setMessage] = useState('')

  const categories = ['Все', ...Array.from(new Set(faqs.map(f => f.category)))]

  const filteredFaqs = faqs.filter(faq => {
    const matchesSearch = faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesCategory = !selectedCategory || selectedCategory === 'Все' || faq.category === selectedCategory
    return matchesSearch && matchesCategory
  })

  const handleSubmitTicket = () => {
    if (subject && message) {
      alert(`Тикет создан! Номер: TKT-${Math.floor(Math.random() * 1000).toString().padStart(3, '0')}`)
      setSubject('')
      setMessage('')
      setShowTicketForm(false)
    }
  }

  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      {/* Header */}
      <div className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Справочный центр</h1>
        <p className="text-gray-600 text-lg">Найдите ответы на вопросы или обратитесь в поддержку</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Content */}
        <div className="lg:col-span-2">
          {/* FAQ Section */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Часто задаваемые вопросы</h2>

            {/* Search */}
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск вопроса..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2 mb-8">
              {categories.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-full font-medium transition-all ${
                    selectedCategory === cat
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>

            {/* FAQs List */}
            <div className="space-y-4">
              {filteredFaqs.length > 0 ? (
                filteredFaqs.map(faq => (
                  <Card key={faq.id} padding="md" hover>
                    <button
                      onClick={() => setExpandedFaq(expandedFaq === faq.id ? null : faq.id)}
                      className="w-full text-left flex items-start justify-between gap-4"
                    >
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">{faq.question}</h3>
                        <p className="text-sm text-gray-600 mt-1">{faq.category}</p>
                      </div>
                      <ChevronDown
                        className={`h-5 w-5 text-gray-400 flex-shrink-0 transition-transform ${
                          expandedFaq === faq.id ? 'rotate-180' : ''
                        }`}
                      />
                    </button>

                    {expandedFaq === faq.id && (
                      <div className="mt-4 pt-4 border-t border-gray-200">
                        <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                      </div>
                    )}
                  </Card>
                ))
              ) : (
                <Card padding="lg" className="text-center">
                  <p className="text-gray-600 mb-2">Вопросы не найдены</p>
                  <p className="text-gray-500">Попробуйте изменить поисковый запрос</p>
                </Card>
              )}
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div>
          {/* Support Tickets */}
          <Card padding="lg" className="mb-6">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Ваши тикеты</h3>
            <div className="space-y-3 mb-6">
              {supportTickets.map(ticket => {
                const statusInfo = getStatusInfo(ticket.status)
                const StatusIcon = statusInfo.icon
                return (
                  <div key={ticket.id} className="pb-3 border-b border-gray-200 last:border-0">
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="font-mono text-sm text-gray-600">{ticket.id}</p>
                        <p className="text-sm text-gray-900 font-medium">{ticket.subject}</p>
                      </div>
                      <Badge variant={
                        ticket.priority === 'high' ? 'danger' :
                        ticket.priority === 'normal' ? 'warning' :
                        'default'
                      }>
                        {ticket.priority === 'high' ? 'Срочно' :
                         ticket.priority === 'normal' ? 'Обычно' :
                         'Низко'}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className={`inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full ${statusInfo.color}`}>
                        <StatusIcon className="h-3 w-3" />
                        {statusInfo.label}
                      </span>
                      <span className="text-xs text-gray-500">{ticket.createdAt}</span>
                    </div>
                  </div>
                )
              })}
            </div>
            <Button
              variant="secondary"
              fullWidth
              onClick={() => setShowTicketForm(true)}
            >
              <Send className="h-4 w-4 mr-2" />
              Создать тикет
            </Button>
          </Card>

          {/* Contact Info */}
          <Card padding="lg" className="bg-indigo-50 border border-indigo-200">
            <h3 className="text-lg font-bold text-indigo-900 mb-4">📞 Связитесь с нами</h3>
            <div className="space-y-3 mb-4">
              <div>
                <p className="text-sm text-indigo-800 mb-1">Email поддержки:</p>
                <p className="text-indigo-600 font-semibold">support@mentorhub.ru</p>
              </div>
              <div>
                <p className="text-sm text-indigo-800 mb-1">Телефон:</p>
                <p className="text-indigo-600 font-semibold">+7 915 048-02-49</p>
              </div>
              <div>
                <p className="text-sm text-indigo-800 mb-1">Часы работы:</p>
                <p className="text-indigo-600 text-sm">Пн-Пт: 9:00 - 18:00 (UTC+3)</p>
              </div>
            </div>
            <Button variant="outline" fullWidth>
              Отправить email
            </Button>
          </Card>
        </div>
      </div>

      {/* Ticket Form Modal */}
      {showTicketForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card padding="lg" className="w-full max-w-md">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">Создать тикет поддержки</h3>

            <div className="space-y-4 mb-6">
              <div>
                <label htmlFor="subject" className="block text-sm font-semibold text-gray-900 mb-2">
                  Тема
                </label>
                <input
                  id="subject"
                  type="text"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  placeholder="Краткое описание проблемы"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="message" className="block text-sm font-semibold text-gray-900 mb-2">
                  Сообщение
                </label>
                <textarea
                  id="message"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Подробное описание вашей проблемы..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  rows={5}
                />
              </div>
            </div>

            <div className="flex gap-3">
              <Button
                variant="secondary"
                fullWidth
                onClick={handleSubmitTicket}
                disabled={!subject || !message}
              >
                Отправить
              </Button>
              <Button
                variant="outline"
                fullWidth
                onClick={() => setShowTicketForm(false)}
              >
                Отмена
              </Button>
            </div>
          </Card>
        </div>
      )}
    </main>
  )
}
