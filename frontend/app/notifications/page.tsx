'use client'

import { useState } from 'react'
import { Bell, Trash2, CheckCircle, AlertCircle, Info, MessageSquare } from 'lucide-react'
import Card from '@/components/ui/Card'
import Button from '@/components/ui/Button'
import Badge from '@/components/ui/Badge'

interface NotificationItem {
  id: number
  type: 'success' | 'warning' | 'info' | 'error'
  title: string
  message: string
  timestamp: string
  icon: React.ReactNode
  read: boolean
  action?: { label: string; href: string }
}

const notifications: NotificationItem[] = [
  {
    id: 1,
    type: 'success',
    title: 'Сессия подтверждена',
    message: 'Ваша сессия с Иваном Петровым на 21 ноября в 14:00 подтверждена',
    timestamp: '2 часа назад',
    icon: <CheckCircle className="h-5 w-5 text-green-600" />,
    read: false,
    action: { label: 'Посмотреть', href: '/sessions' }
  },
  {
    id: 2,
    type: 'info',
    title: 'Новый ответ от ментора',
    message: 'Иван Петров ответил на ваше сообщение в чате',
    timestamp: '3 часа назад',
    icon: <MessageSquare className="h-5 w-5 text-blue-600" />,
    read: false,
    action: { label: 'Открыть чат', href: '/messages' }
  },
  {
    id: 3,
    type: 'warning',
    title: 'Ваша сессия через 1 час',
    message: 'Напоминание: Сессия с Марией Сидоровой начинается через час',
    timestamp: '1 час назад',
    icon: <Bell className="h-5 w-5 text-yellow-600" />,
    read: false
  },
  {
    id: 4,
    type: 'info',
    title: 'Скидка 20% на пакет сессий',
    message: 'Вам доступна специальная скидка на покупку пакета из 10 сессий',
    timestamp: '1 день назад',
    icon: <Info className="h-5 w-5 text-blue-600" />,
    read: true,
    action: { label: 'Узнать больше', href: '/pricing' }
  },
  {
    id: 5,
    type: 'success',
    title: 'Новая статья в блоге',
    message: 'Опубликована новая статья: "Advanced TypeScript"',
    timestamp: '2 дня назад',
    icon: <Info className="h-5 w-5 text-green-600" />,
    read: true,
    action: { label: 'Прочитать', href: '/blog' }
  },
  {
    id: 6,
    type: 'error',
    title: 'Ошибка платежа',
    message: 'Не удалось обработать ваш платеж. Пожалуйста, проверьте способ оплаты',
    timestamp: '3 дня назад',
    icon: <AlertCircle className="h-5 w-5 text-red-600" />,
    read: true,
    action: { label: 'Повторить', href: '/billing' }
  }
]

export default function NotificationsPage() {
  const [notificationList, setNotificationList] = useState(notifications)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')

  const unreadCount = notificationList.filter(n => !n.read).length
  const filteredNotifications = filter === 'unread' 
    ? notificationList.filter(n => !n.read)
    : notificationList

  const markAsRead = (id: number) => {
    setNotificationList(notificationList.map(n => 
      n.id === id ? { ...n, read: true } : n
    ))
  }

  const markAllAsRead = () => {
    setNotificationList(notificationList.map(n => ({ ...n, read: true })))
  }

  const deleteNotification = (id: number) => {
    setNotificationList(notificationList.filter(n => n.id !== id))
  }

  const clearAll = () => {
    setNotificationList([])
  }

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'success':
        return 'bg-green-50 border-green-200'
      case 'warning':
        return 'bg-yellow-50 border-yellow-200'
      case 'error':
        return 'bg-red-50 border-red-200'
      case 'info':
      default:
        return 'bg-blue-50 border-blue-200'
    }
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Уведомления</h1>
          <p className="text-gray-600">
            {unreadCount > 0 
              ? `У вас ${unreadCount} новых уведомлений` 
              : 'Нет новых уведомлений'}
          </p>
        </div>
        <div className="text-5xl">🔔</div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-indigo-600 mb-1">{notificationList.length}</div>
          <div className="text-sm text-gray-600">Всего уведомлений</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-yellow-600 mb-1">{unreadCount}</div>
          <div className="text-sm text-gray-600">Не прочитано</div>
        </Card>
        <Card padding="md" className="text-center">
          <div className="text-3xl font-bold text-green-600 mb-1">{notificationList.filter(n => n.read).length}</div>
          <div className="text-sm text-gray-600">Прочитано</div>
        </Card>
      </div>

      {/* Filters and Actions */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filter === 'all'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Все
          </button>
          <button
            onClick={() => setFilter('unread')}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              filter === 'unread'
                ? 'bg-indigo-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Не прочитаны ({unreadCount})
          </button>
        </div>

        {notificationList.length > 0 && (
          <div className="flex gap-2">
            {unreadCount > 0 && (
              <Button variant="outline" size="sm" onClick={markAllAsRead}>
                Отметить все как прочитано
              </Button>
            )}
            <Button
              variant="outline"
              size="sm"
              onClick={clearAll}
              className="text-red-600 hover:text-red-700"
            >
              <Trash2 className="h-4 w-4 mr-1" />
              Очистить все
            </Button>
          </div>
        )}
      </div>

      {/* Notifications List */}
      <div className="space-y-4">
        {filteredNotifications.length > 0 ? (
          filteredNotifications.map(notification => (
            <Card
              key={notification.id}
              padding="lg"
              className={`border ${getTypeColor(notification.type)} ${
                !notification.read ? 'bg-opacity-100' : 'bg-opacity-50'
              }`}
              hover
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                <div className="flex-shrink-0 pt-1">
                  {notification.icon}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-semibold text-gray-900 text-lg mb-1">
                        {notification.title}
                      </h3>
                      <p className="text-gray-700 mb-3">
                        {notification.message}
                      </p>
                      <p className="text-sm text-gray-500">
                        {notification.timestamp}
                      </p>
                    </div>

                    {/* Badge */}
                    {!notification.read && (
                      <div className="flex-shrink-0">
                        <Badge variant="info">Новое</Badge>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-2 mt-4">
                    {notification.action && (
                      <Button variant="secondary" size="sm">
                        {notification.action.label}
                      </Button>
                    )}
                    {!notification.read && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => markAsRead(notification.id)}
                      >
                        Отметить как прочитано
                      </Button>
                    )}
                    <button
                      onClick={() => deleteNotification(notification.id)}
                      className="ml-auto p-2 text-gray-400 hover:text-gray-600 transition-colors"
                      title="Удалить уведомление"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </Card>
          ))
        ) : (
          <Card padding="lg" className="text-center">
            <div className="text-5xl mb-3">✨</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {filter === 'unread' ? 'Все прочитано!' : 'Нет уведомлений'}
            </h3>
            <p className="text-gray-600 mb-4">
              {filter === 'unread'
                ? 'У вас нет непрочитанных уведомлений. Отличная работа!'
                : 'У вас нет уведомлений'}
            </p>
            {notificationList.length > 0 && filter === 'unread' && (
              <Button variant="secondary" onClick={() => setFilter('all')}>
                Посмотреть все уведомления
              </Button>
            )}
          </Card>
        )}
      </div>

      {/* Notification Preferences */}
      <Card padding="lg" className="mt-12 bg-indigo-50 border border-indigo-200">
        <h3 className="text-lg font-semibold text-indigo-900 mb-4">⚙️ Управление уведомлениями</h3>
        <p className="text-indigo-800 mb-4">
          Настройте, какие уведомления вы хотите получать
        </p>
        <Button variant="secondary">
          Перейти в настройки уведомлений
        </Button>
      </Card>
    </main>
  )
}
