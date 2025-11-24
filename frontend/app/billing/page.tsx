'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { CreditCard, Download, Lock, Plus, Trash2, CheckCircle } from 'lucide-react'
import Badge from '@/components/ui/Badge'
import { useAuth } from '@/hooks/useAuth'

interface PaymentMethod {
  id: string
  cardNumber: string
  holderName: string
  expiryDate: string
  isDefault: boolean
  type: 'credit' | 'debit'
}

interface Invoice {
  id: string
  date: string
  amount: number
  status: 'paid' | 'pending' | 'overdue'
  description: string
}

interface Subscription {
  plan: string
  price: number
  period: string
  features: string[]
  status: 'active' | 'canceled'
}

export default function BillingPage() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [activeTab, setActiveTab] = useState<'subscription' | 'payments' | 'invoices' | 'billing'>('subscription')
  const [showAddCard, setShowAddCard] = useState(false)

  // Проверка авторизации
  useEffect(() => {
    if (!isAuthenticated()) {
      router.push('/auth/login?redirect=/billing')
    } else {
      setIsLoading(true)
      setTimeout(() => setIsLoading(false), 300)
    }
  }, [isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Загрузка платёжной информации...</p>
        </div>
      </div>
    )
  }

  const subscription: Subscription = {
    plan: 'Pro Mentor',
    price: 999,
    period: 'месяц',
    features: [
      'Неограниченные сессии',
      'Приоритетная поддержка',
      'Расширенная аналитика',
      'Сертификаты',
      'Видеозвонки HD'
    ],
    status: 'active'
  }

  const paymentMethods: PaymentMethod[] = [
    {
      id: '1',
      cardNumber: '•••• •••• •••• 4242',
      holderName: 'Максим Дуплей',
      expiryDate: '12/26',
      isDefault: true,
      type: 'credit'
    },
    {
      id: '2',
      cardNumber: '•••• •••• •••• 5555',
      holderName: 'Максим Дуплей',
      expiryDate: '08/25',
      isDefault: false,
      type: 'debit'
    }
  ]

  const invoices: Invoice[] = [
    {
      id: 'INV-001',
      date: '2025-11-20',
      amount: 999,
      status: 'paid',
      description: 'Подписка Pro Mentor (ноябрь 2025)'
    },
    {
      id: 'INV-002',
      date: '2025-10-20',
      amount: 999,
      status: 'paid',
      description: 'Подписка Pro Mentor (октябрь 2025)'
    },
    {
      id: 'INV-003',
      date: '2025-09-20',
      amount: 999,
      status: 'paid',
      description: 'Подписка Pro Mentor (сентябрь 2025)'
    }
  ]

  const billingAddress = {
    name: 'Максим Игоревич Дуплей',
    email: 'maksimqwe42@mail.ru',
    address: 'Москва, Россия',
    phone: '+7 915 048-02-49'
  }

  const getStatusBadgeVariant = (status: Invoice['status']) => {
    switch (status) {
      case 'paid':
        return 'success'
      case 'pending':
        return 'warning'
      case 'overdue':
        return 'danger'
      default:
        return 'default'
    }
  }

  const getStatusText = (status: Invoice['status']) => {
    switch (status) {
      case 'paid':
        return '✓ Оплачено'
      case 'pending':
        return '⏳ Ожидает'
      case 'overdue':
        return '⚠️ Просрочено'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-5xl mx-auto">
        {/* Заголовок */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Платежи и Биллинг</h1>
          <p className="text-gray-600 mt-2">Управляйте подпиской, способами оплаты и счётами</p>
        </div>

        {/* Вкладки */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setActiveTab('subscription')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'subscription'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            Подписка
          </button>
          <button
            onClick={() => setActiveTab('payments')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'payments'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            <CreditCard size={18} className="inline mr-2" />
            Способы оплаты
          </button>
          <button
            onClick={() => setActiveTab('invoices')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'invoices'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            Счета
          </button>
          <button
            onClick={() => setActiveTab('billing')}
            className={`px-6 py-3 rounded-lg font-medium transition-colors ${
              activeTab === 'billing'
                ? 'bg-indigo-600 text-white'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            Адрес биллинга
          </button>
        </div>

        {/* Вкладка: Подписка */}
        {activeTab === 'subscription' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-8">
              <div className="flex items-start justify-between mb-6">
                <div>
                  <div className="flex items-center space-x-3 mb-2">
                    <h2 className="text-2xl font-bold text-gray-900">{subscription.plan}</h2>
                    <Badge variant="success">Активна</Badge>
                  </div>
                  <p className="text-gray-600">Следующее списание: 20 декабря 2025</p>
                </div>
                <div className="text-right">
                  <p className="text-4xl font-bold text-indigo-600">{subscription.price}₽</p>
                  <p className="text-gray-600">в {subscription.period}</p>
                </div>
              </div>

              <div className="border-t border-gray-200 pt-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Что входит в подписку:</h3>
                <ul className="space-y-3">
                  {subscription.features.map((feature, idx) => (
                    <li key={idx} className="flex items-center space-x-3">
                      <CheckCircle size={20} className="text-green-500 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div className="border-t border-gray-200 mt-6 pt-6 flex space-x-3">
                <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  Обновить план
                </button>
                <button className="flex-1 bg-red-50 hover:bg-red-100 text-red-700 font-medium py-2 px-4 rounded-lg transition-colors">
                  Отменить подписку
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Вкладка: Способы оплаты */}
        {activeTab === 'payments' && (
          <div className="space-y-4">
            {paymentMethods.map(method => (
              <div key={method.id} className="bg-white rounded-lg shadow p-6 flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-lg p-4 text-white">
                    <CreditCard size={24} />
                  </div>
                  <div>
                    <p className="font-semibold text-gray-900">{method.cardNumber}</p>
                    <p className="text-sm text-gray-600">{method.holderName} • Истекает {method.expiryDate}</p>
                    {method.isDefault && (
                      <Badge variant="info" className="mt-2 inline-block">
                        По умолчанию
                      </Badge>
                    )}
                  </div>
                </div>
                <div className="flex items-center space-x-3">
                  {!method.isDefault && (
                    <button className="px-4 py-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors">
                      Сделать основной
                    </button>
                  )}
                  <button className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Удалить">
                    <Trash2 size={20} />
                  </button>
                </div>
              </div>
            ))}

            {!showAddCard && (
              <button
                onClick={() => setShowAddCard(true)}
                className="w-full bg-gray-50 hover:bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg py-8 transition-colors flex items-center justify-center space-x-2 text-gray-700 font-medium"
              >
                <Plus size={20} />
                <span>Добавить способ оплаты</span>
              </button>
            )}

            {showAddCard && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Добавить новую карту</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Номер карты</label>
                    <input
                      type="text"
                      title="Номер карты"
                      placeholder="1234 5678 9012 3456"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Срок действия</label>
                      <input
                        type="text"
                        title="Срок действия"
                        placeholder="MM/YY"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">CVC</label>
                      <div className="relative">
                        <input
                          type="password"
                          title="CVC код"
                          placeholder="123"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                        <Lock size={18} className="absolute right-3 top-2.5 text-gray-400" />
                      </div>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Имя держателя</label>
                    <input
                      type="text"
                      title="Имя держателя"
                      placeholder="Максим Дуплей"
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                    />
                  </div>
                  <div className="flex space-x-3">
                    <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                      Добавить карту
                    </button>
                    <button
                      onClick={() => setShowAddCard(false)}
                      className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-lg transition-colors"
                    >
                      Отмена
                    </button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Вкладка: Счета */}
        {activeTab === 'invoices' && (
          <div className="space-y-4">
            {invoices.map(invoice => (
              <div key={invoice.id} className="bg-white rounded-lg shadow p-6 flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-2">
                    <p className="font-semibold text-gray-900">{invoice.description}</p>
                    <Badge variant={getStatusBadgeVariant(invoice.status)}>
                      {getStatusText(invoice.status)}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600">
                    {invoice.id} • {new Date(invoice.date).toLocaleDateString('ru-RU')}
                  </p>
                </div>
                <div className="flex items-center space-x-6">
                  <p className="text-lg font-semibold text-gray-900">{invoice.amount}₽</p>
                  <button className="p-2 text-indigo-600 hover:bg-indigo-50 rounded-lg transition-colors" title="Скачать счёт">
                    <Download size={20} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Вкладка: Адрес биллинга */}
        {activeTab === 'billing' && (
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-6">Адрес для биллинга</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Полное имя</label>
                <input
                  type="text"
                  title="Полное имя"
                  defaultValue={billingAddress.name}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
                  <input
                    type="email"
                    title="Email"
                    defaultValue={billingAddress.email}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Телефон</label>
                  <input
                    type="tel"
                    title="Телефон"
                    defaultValue={billingAddress.phone}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Адрес</label>
                <input
                  type="text"
                  title="Адрес"
                  defaultValue={billingAddress.address}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
              <div className="flex space-x-3 pt-4">
                <button className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                  Сохранить адрес
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
