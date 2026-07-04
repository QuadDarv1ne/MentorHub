'use client'

import { useState, useEffect, useCallback } from 'react'
import { useToast } from '@/hooks/useToast'
import { useWebSocket } from '@/hooks/useWebSocket'
import { apiRequest } from '@/lib/api/client'
import { logger } from '@/lib/utils/logger'

interface Notification {
  id: number
  type: 'message' | 'session' | 'payment' | 'system' | 'achievement'
  title: string
  message: string
  read: boolean
  createdAt: string
  icon: string
}

export default function NotificationsPanel() {
  const toast = useToast()
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [isOpen, setIsOpen] = useState(false)

  const handleNotification = useCallback((data: Record<string, unknown>) => {
    if (data.type === 'notification') {
      const newNotification = data as unknown as Notification
      setNotifications(prev => [newNotification, ...prev])
      setUnreadCount(prev => prev + 1)
      toast.success(newNotification.title, newNotification.message)
    }
  }, [toast])

  const { connect } = useWebSocket({
    path: '/ws/notifications',
    onMessage: handleNotification,
  })

  useEffect(() => {
    fetchNotifications()
    connect()

    const interval = setInterval(fetchNotifications, 30000)
    return () => clearInterval(interval)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const fetchNotifications = async () => {
    try {
      const data = await apiRequest<Notification[]>('/notifications')
      setNotifications(data)
      setUnreadCount(data.filter((n) => !n.read).length)
    } catch (error) {
      logger.error('Fetch notifications error', error)
    }
  }

  const markAsRead = async (id: number) => {
    try {
      await apiRequest(`/notifications/${id}/read`, { method: 'POST' })
      setNotifications(prev =>
        prev.map(n => n.id === id ? { ...n, read: true } : n)
      )
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      logger.error('Mark as read error', error)
    }
  }

  const markAllAsRead = async () => {
    try {
      await apiRequest('/notifications/read-all', { method: 'POST' })
      setNotifications(prev => prev.map(n => ({ ...n, read: true })))
      setUnreadCount(0)
      toast.success('Все уведомления прочитаны')
    } catch (error) {
      logger.error('Mark all as read error', error)
    }
  }

  const getIcon = (type: string) => {
    const icons: Record<string, string> = {
      message: '💬',
      session: '📅',
      payment: '💰',
      system: '⚙️',
      achievement: '🏆'
    }
    return icons[type] || '📢'
  }

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMins / 60)
    const diffDays = Math.floor(diffHours / 24)

    if (diffMins < 1) return 'Только что'
    if (diffMins < 60) return `${diffMins}м назад`
    if (diffHours < 24) return `${diffHours}ч назад`
    return `${diffDays}д назад`
  }

  return (
    <div className="relative">
      {/* Bell Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-indigo-600 dark:text-gray-300 dark:hover:text-white transition-colors"
      >
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
        </svg>
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl border border-gray-200 dark:border-gray-700 z-50 max-h-[500px] overflow-hidden">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white">
                🔔 Уведомления
              </h3>
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-medium"
                >
                  Прочитать все
                </button>
              )}
            </div>

            {/* Notifications List */}
            <div className="overflow-y-auto max-h-[400px]">
              {notifications.length > 0 ? (
                notifications.map(notification => (
                  <div
                    key={notification.id}
                    onClick={() => markAsRead(notification.id)}
                    className={`p-4 border-b border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors ${
                      !notification.read ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                    }`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-2xl">{getIcon(notification.type)}</span>
                      <div className="flex-1">
                        <div className="flex items-center justify-between mb-1">
                          <h4 className={`font-semibold text-gray-900 dark:text-white ${
                            !notification.read ? 'text-indigo-600 dark:text-indigo-400' : ''
                          }`}>
                            {notification.title}
                          </h4>
                          {!notification.read && (
                            <span className="w-2 h-2 bg-indigo-500 rounded-full"></span>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                          {notification.message}
                        </p>
                        <span className="text-xs text-gray-500 dark:text-gray-500">
                          {getTimeAgo(notification.createdAt)}
                        </span>
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="p-8 text-center text-gray-500 dark:text-gray-400">
                  <span className="text-4xl mb-2 block">🎉</span>
                  <p>Нет новых уведомлений</p>
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-gray-200 dark:border-gray-700 text-center">
              <a
                href="/notifications"
                className="text-sm text-indigo-600 hover:text-indigo-700 dark:text-indigo-400 font-medium"
              >
                Показать все уведомления →
              </a>
            </div>
          </div>
        </>
      )}
    </div>
  )
}
