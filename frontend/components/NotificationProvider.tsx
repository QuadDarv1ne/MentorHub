'use client'

import React, { createContext, useContext, useState, useCallback } from 'react'
import Notification, { NotificationProps } from './Notification'

interface NotificationContextType {
  showNotification: (
    title: string,
    options?: Partial<Omit<NotificationProps, 'id' | 'title'>>
  ) => void
  hideNotification: (id: string) => void
  notifications: NotificationProps[]
}

const NotificationContext = createContext<NotificationContextType | undefined>(
  undefined
)

export function NotificationProvider({
  children
}: {
  children: React.ReactNode
}) {
  const [notifications, setNotifications] = useState<NotificationProps[]>([])

  const showNotification = useCallback(
    (
      title: string,
      options?: Partial<Omit<NotificationProps, 'id' | 'title'>>
    ) => {
      const id = Date.now().toString()
      const notification: NotificationProps = {
        id,
        title,
        type: 'info',
        autoClose: true,
        duration: 5000,
        ...options
      }
      setNotifications((prev) => [...prev, notification])
    },
    []
  )

  const hideNotification = useCallback((id: string) => {
    setNotifications((prev) => prev.filter((n) => n.id !== id))
  }, [])

  return (
    <NotificationContext.Provider value={{ showNotification, hideNotification, notifications }}>
      {children}
      <div className="fixed top-4 right-4 space-y-3 z-50 pointer-events-none">
        {notifications.map((notification) => (
          <div key={notification.id} className="pointer-events-auto">
            <Notification
              notification={notification}
              onClose={hideNotification}
            />
          </div>
        ))}
      </div>
    </NotificationContext.Provider>
  )
}

export function useNotification() {
  const context = useContext(NotificationContext)
  if (!context) {
    throw new Error(
      'useNotification must be used within NotificationProvider'
    )
  }
  return context
}

export function useNotify() {
  const { showNotification } = useNotification()
  return {
    success: (title: string, message?: string) =>
      showNotification(title, { type: 'success', message }),
    error: (title: string, message?: string) =>
      showNotification(title, { type: 'error', message }),
    info: (title: string, message?: string) =>
      showNotification(title, { type: 'info', message }),
    warning: (title: string, message?: string) =>
      showNotification(title, { type: 'warning', message })
  }
}
