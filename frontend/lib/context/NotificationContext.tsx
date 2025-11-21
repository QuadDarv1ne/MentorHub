/**
 * Провайдер уведомлений и Toast-сообщений
 * Предоставляет глобальный доступ к системе уведомлений
 */

'use client'

import { createContext, useContext, ReactNode } from 'react'
import { useNotifications as useNotificationsHook, useToast as useToastHook } from '@/lib/hooks/useNotifications'

interface NotificationContextValue {
  notifications: ReturnType<typeof useNotificationsHook>
  toast: ReturnType<typeof useToastHook>
}

const NotificationContext = createContext<NotificationContextValue | undefined>(undefined)

interface NotificationProviderProps {
  children: ReactNode
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const notifications = useNotificationsHook()
  const toast = useToastHook()

  return (
    <NotificationContext.Provider value={{ notifications, toast }}>
      {children}
    </NotificationContext.Provider>
  )
}

/**
 * Хук для доступа к уведомлениям
 */
export function useNotificationContext() {
  const context = useContext(NotificationContext)
  
  if (context === undefined) {
    throw new Error('useNotificationContext must be used within NotificationProvider')
  }
  
  return context
}

/**
 * Хук для быстрого доступа только к toast-сообщениям
 */
export function useToastContext() {
  const { toast } = useNotificationContext()
  return toast
}
