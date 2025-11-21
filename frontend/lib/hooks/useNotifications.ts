import { useState, useEffect, useCallback } from 'react'

export interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
  action?: {
    label: string
    onClick: () => void
  }
}

/**
 * Хук для управления уведомлениями
 */
export function useNotifications() {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState(0)

  useEffect(() => {
    // Загрузка уведомлений из localStorage
    const stored = localStorage.getItem('notifications')
    if (stored) {
      try {
        const parsed = JSON.parse(stored)
        setNotifications(parsed.map((n: Notification) => ({
          ...n,
          timestamp: new Date(n.timestamp)
        })))
      } catch (error) {
        console.error('Error loading notifications:', error)
      }
    }
  }, [])

  useEffect(() => {
    // Подсчет непрочитанных
    const count = notifications.filter(n => !n.read).length
    setUnreadCount(count)

    // Сохранение в localStorage
    localStorage.setItem('notifications', JSON.stringify(notifications))
  }, [notifications])

  const addNotification = useCallback((notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => {
    const newNotification: Notification = {
      ...notification,
      id: Date.now().toString(),
      timestamp: new Date(),
      read: false
    }

    setNotifications(prev => [newNotification, ...prev])

    // Автоматическое удаление через 10 секунд для success/info
    if (notification.type === 'success' || notification.type === 'info') {
      setTimeout(() => {
        setNotifications(prev => prev.filter(n => n.id !== newNotification.id))
      }, 10000)
    }

    return newNotification.id
  }, [])

  const removeNotification = useCallback((id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }, [])

  const markAsRead = useCallback((id: string) => {
    setNotifications(prev =>
      prev.map(n => n.id === id ? { ...n, read: true } : n)
    )
  }, [])

  const markAllAsRead = useCallback(() => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })))
  }, [])

  const clearAll = useCallback(() => {
    setNotifications([])
    localStorage.removeItem('notifications')
  }, [])

  const clearRead = useCallback(() => {
    setNotifications(prev => prev.filter(n => !n.read))
  }, [])

  return {
    notifications,
    unreadCount,
    addNotification,
    removeNotification,
    markAsRead,
    markAllAsRead,
    clearAll,
    clearRead
  }
}

/**
 * Хук для toast уведомлений (временных всплывающих сообщений)
 */
export function useToast() {
  const [toasts, setToasts] = useState<Array<{
    id: string
    type: 'info' | 'success' | 'warning' | 'error'
    message: string
  }>>([])

  const showToast = useCallback((
    message: string,
    type: 'info' | 'success' | 'warning' | 'error' = 'info',
    duration = 3000
  ) => {
    const id = Date.now().toString()
    const toast = { id, type, message }

    setToasts(prev => [...prev, toast])

    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id))
    }, duration)

    return id
  }, [])

  const removeToast = useCallback((id: string) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const success = useCallback((message: string) => showToast(message, 'success'), [showToast])
  const error = useCallback((message: string) => showToast(message, 'error', 5000), [showToast])
  const warning = useCallback((message: string) => showToast(message, 'warning', 4000), [showToast])
  const info = useCallback((message: string) => showToast(message, 'info'), [showToast])

  return {
    toasts,
    showToast,
    removeToast,
    success,
    error,
    warning,
    info
  }
}
