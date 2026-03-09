'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { CreditCard, Lock, Check, AlertCircle } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import { useAuth } from '@/hooks/useAuth'

interface PaymentMethod {
  id: string
  type: 'card' | 'paypal' | 'bank'
  last4?: string
  brand?: string
  expiryMonth?: number
  expiryYear?: number
  isDefault: boolean
}

interface Subscription {
  id: string
  plan: string
  amount: number
  currency: string
  interval: 'month' | 'year'
  status: 'active' | 'cancelled' | 'past_due'
  currentPeriodEnd: string
}

export default function PaymentIntegration() {
  const router = useRouter()
  const { isAuthenticated } = useAuth()
  const [isLoading, setIsLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [paymentSuccess, setPaymentSuccess] = useState(false)
  const [showAddCard, setShowAddCard] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [paymentMethods, setPaymentMethods] = useState<PaymentMethod[]>([
    {
      id: 'pm_1',
      type: 'card',
      last4: '4242',
      brand: 'Visa',
      expiryMonth: 12,
      expiryYear: 2026,
      isDefault: true
    },
    {
      id: 'pm_2',
      type: 'card',
      last4: '5555',
      brand: 'Mastercard',
      expiryMonth: 8,
      expiryYear: 2025,
      isDefault: false
    }
  ])

  const [subscription, setSubscription] = useState<Subscription>({
    id: 'sub_123',
    plan: 'Pro',
    amount: 1999,
    currency: 'RUB',
    interval: 'month',
    status: 'active',
    currentPeriodEnd: '2025-12-21'
  })

  // Проверка авторизации
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/payment')
    } else {
      setIsLoading(true)
      setTimeout(() => setIsLoading(false), 500)
    }
  }, [isAuthenticated, router])

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  const plans = [
    {
      id: 'basic',
      name: 'Базовый',
      price: 999,
      interval: 'month',
      features: [
        '5 сессий в месяц',
        'Доступ к базовым курсам',
        'Email поддержка',
        'Сертификаты'
      ]
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 1999,
      interval: 'month',
      features: [
        'Неограниченные сессии',
        'Все курсы и ресурсы',
        'Приоритетная поддержка 24/7',
        'Сертификаты премиум',
        'Аналитика и статистика',
        'Персональный ментор'
      ],
      popular: true
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 4999,
      interval: 'month',
      features: [
        'Все из Pro',
        'Командный доступ (до 10 человек)',
        'Индивидуальная программа',
        'Выделенный менеджер',
        'API доступ',
        'Custom брендинг'
      ]
    }
  ]

  const handlePayment = async (planId: string) => {
    // Проверка авторизации перед оплатой
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/payment')
      return
    }

    setProcessing(true)
    setSelectedPlan(planId)

    // Mock payment processing
    await new Promise(resolve => setTimeout(resolve, 2000))

    // Simulate successful payment
    const plan = plans.find(p => p.id === planId)
    if (plan) {
      setSubscription({
        id: 'sub_new_' + Date.now(),
        plan: plan.name,
        amount: plan.price,
        currency: 'RUB',
        interval: plan.interval as 'month',
        status: 'active',
        currentPeriodEnd: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
      })
      setPaymentSuccess(true)
      setTimeout(() => setPaymentSuccess(false), 3000)
    }

    setProcessing(false)
    setSelectedPlan(null)
  }

  const handleAddCard = async (e: React.FormEvent) => {
    e.preventDefault()

    // Проверка авторизации перед добавлением карты
    if (!isAuthenticated) {
      router.push('/auth/login?redirect=/payment')
      return
    }
    
    setProcessing(true)

    // Mock card adding
    await new Promise(resolve => setTimeout(resolve, 1500))

    const newCard: PaymentMethod = {
      id: 'pm_' + Date.now(),
      type: 'card',
      last4: '1234',
      brand: 'Visa',
      expiryMonth: 12,
      expiryYear: 2027,
      isDefault: paymentMethods.length === 0
    }

    setPaymentMethods([...paymentMethods, newCard])
    setShowAddCard(false)
    setProcessing(false)
  }

  const handleSetDefault = (id: string) => {
    setPaymentMethods(
      paymentMethods.map(pm => ({
        ...pm,
        isDefault: pm.id === id
      }))
    )
  }

  const handleRemoveCard = (id: string) => {
    setPaymentMethods(paymentMethods.filter(pm => pm.id !== id))
  }

  const getCardIcon = (brand?: string) => {
    switch (brand?.toLowerCase()) {
      case 'visa':
        return '💳'
      case 'mastercard':
        return '💳'
      case 'amex':
        return '💳'
      default:
        return '💳'
    }
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Success notification */}
      {paymentSuccess && (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-6 py-4 rounded-lg shadow-lg z-50 flex items-center space-x-3">
          <Check size={24} />
          <span className="font-medium">Платеж успешно обработан!</span>
        </div>
      )}

      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Оплата и подписка</h1>
          <p className="text-indigo-100 text-lg">
            Управляйте платежами и выберите подходящий тариф
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Текущая подписка */}
        {subscription && (
          <Card className="mb-12 bg-gradient-to-r from-indigo-50 to-purple-50 border-indigo-200">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">
                  Текущая подписка: {subscription.plan}
                </h2>
                <p className="text-gray-600 mb-4">
                  {subscription.amount} {subscription.currency}/{subscription.interval === 'month' ? 'месяц' : 'год'}
                </p>
                <div className="flex items-center space-x-4">
                  <Badge variant={subscription.status === 'active' ? 'success' : 'danger'}>
                    {subscription.status === 'active' ? 'Активна' : 'Неактивна'}
                  </Badge>
                  <span className="text-sm text-gray-600">
                    Следующее списание: {new Date(subscription.currentPeriodEnd).toLocaleDateString('ru-RU')}
                  </span>
                </div>
              </div>
              <button className="px-6 py-3 bg-white text-gray-700 rounded-lg hover:bg-gray-100 font-medium transition-colors border border-gray-300">
                Отменить подписку
              </button>
            </div>
          </Card>
        )}

        {/* Способы оплаты */}
        <div className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Способы оплаты</h2>
            <button
              onClick={() => setShowAddCard(!showAddCard)}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors"
            >
              Добавить карту
            </button>
          </div>

          {/* Форма добавления карты */}
          {showAddCard && (
            <Card className="mb-6">
              <form onSubmit={handleAddCard}>
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
                  <CreditCard size={20} className="text-indigo-600" />
                  <span>Новая карта</span>
                </h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Номер карты</label>
                    <input
                      type="text"
                      title="Введите номер карты"
                      placeholder="1234 5678 9012 3456"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      maxLength={19}
                      required
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Срок действия</label>
                      <input
                        type="text"
                        title="MM/YY"
                        placeholder="MM/YY"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        maxLength={5}
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">CVV</label>
                      <input
                        type="text"
                        title="CVV"
                        placeholder="123"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        maxLength={4}
                        required
                      />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Имя владельца</label>
                    <input
                      type="text"
                      title="Имя на карте"
                      placeholder="IVAN IVANOV"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      required
                    />
                  </div>
                </div>
                <div className="flex items-center space-x-3 mt-6">
                  <button
                    type="submit"
                    disabled={processing}
                    className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {processing ? 'Добавление...' : 'Добавить карту'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAddCard(false)}
                    className="px-6 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 font-medium transition-colors"
                  >
                    Отмена
                  </button>
                </div>
              </form>
            </Card>
          )}

          {/* Список карт */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {paymentMethods.map(method => (
              <Card key={method.id} className={method.isDefault ? 'border-2 border-indigo-600' : ''}>
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-4">
                    <div className="text-4xl">{getCardIcon(method.brand)}</div>
                    <div>
                      <div className="flex items-center space-x-2 mb-1">
                        <p className="font-semibold text-gray-900">{method.brand}</p>
                        {method.isDefault && <Badge variant="success">По умолчанию</Badge>}
                      </div>
                      <p className="text-gray-600">•••• {method.last4}</p>
                      <p className="text-sm text-gray-500">
                        Действительна до {method.expiryMonth}/{method.expiryYear}
                      </p>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2 mt-4 pt-4 border-t border-gray-200">
                  {!method.isDefault && (
                    <button
                      onClick={() => handleSetDefault(method.id)}
                      className="text-sm text-indigo-600 hover:text-indigo-700 font-medium"
                    >
                      Сделать основной
                    </button>
                  )}
                  <button
                    onClick={() => handleRemoveCard(method.id)}
                    className="text-sm text-red-600 hover:text-red-700 font-medium"
                  >
                    Удалить
                  </button>
                </div>
              </Card>
            ))}
          </div>
        </div>

        {/* Тарифные планы */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Доступные тарифы</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {plans.map(plan => (
              <Card
                key={plan.id}
                className={`relative ${
                  plan.popular ? 'border-2 border-indigo-600 shadow-xl' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute top-0 right-0 -mt-4 -mr-4">
                    <Badge variant="warning">Популярный</Badge>
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <div className="flex items-baseline justify-center space-x-1">
                    <span className="text-4xl font-bold text-indigo-600">{plan.price}</span>
                    <span className="text-gray-600">₽/{plan.interval === 'month' ? 'мес' : 'год'}</span>
                  </div>
                </div>

                <ul className="space-y-3 mb-6">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <Check size={20} className="text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>

                <button
                  onClick={() => handlePayment(plan.id)}
                  disabled={processing && selectedPlan === plan.id}
                  className={`w-full px-6 py-3 rounded-lg font-medium transition-colors ${
                    plan.popular
                      ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {processing && selectedPlan === plan.id ? 'Обработка...' : 'Выбрать план'}
                </button>
              </Card>
            ))}
          </div>
        </div>

        {/* Безопасность */}
        <Card className="mt-12 bg-gray-50">
          <div className="flex items-start space-x-4">
            <Lock className="text-green-600 flex-shrink-0" size={24} />
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Безопасные платежи</h3>
              <p className="text-sm text-gray-600 mb-3">
                Все платежи обрабатываются через защищенное соединение. Мы используем современные технологии 
                шифрования и не храним данные вашей карты на наших серверах.
              </p>
              <div className="flex items-center space-x-4 text-xs text-gray-500">
                <span className="flex items-center space-x-1">
                  <Lock size={14} />
                  <span>SSL шифрование</span>
                </span>
                <span>•</span>
                <span>PCI DSS сертификация</span>
                <span>•</span>
                <span>3D Secure</span>
              </div>
            </div>
          </div>
        </Card>

        {/* Mock payment notice */}
        <Card className="mt-6 bg-yellow-50 border-yellow-200">
          <div className="flex items-start space-x-3">
            <AlertCircle className="text-yellow-600 flex-shrink-0" size={20} />
            <div>
              <p className="text-sm text-yellow-800">
                <strong>Демо-режим:</strong> Это mock-интеграция для демонстрации. 
                Реальные платежи не производятся. Используйте любые данные для тестирования.
              </p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
