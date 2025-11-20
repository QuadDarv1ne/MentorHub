import React from 'react'
import { AlertCircle, CheckCircle, InfoIcon, AlertTriangle, X } from 'lucide-react'

export interface NotificationProps {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message?: string
  onClose?: () => void
  autoClose?: boolean
  duration?: number
}

interface Props {
  notification: NotificationProps
  onClose?: (id: string) => void
}

const icons = {
  success: <CheckCircle className="h-5 w-5 text-green-600" />,
  error: <AlertCircle className="h-5 w-5 text-red-600" />,
  info: <InfoIcon className="h-5 w-5 text-blue-600" />,
  warning: <AlertTriangle className="h-5 w-5 text-yellow-600" />
}

const bgColors = {
  success: 'bg-green-50 border-green-200',
  error: 'bg-red-50 border-red-200',
  info: 'bg-blue-50 border-blue-200',
  warning: 'bg-yellow-50 border-yellow-200'
}

const textColors = {
  success: 'text-green-900',
  error: 'text-red-900',
  info: 'text-blue-900',
  warning: 'text-yellow-900'
}

export default function Notification({ notification, onClose }: Props) {
  React.useEffect(() => {
    if (notification.autoClose !== false) {
      const timer = setTimeout(
        () => onClose?.(notification.id),
        notification.duration || 5000
      )
      return () => clearTimeout(timer)
    }
  }, [notification, onClose])

  return (
    <div
      className={`flex items-start gap-3 p-4 rounded-lg border ${bgColors[notification.type]} animate-in fade-in slide-in-from-top-2 duration-300`}
      role="alert"
    >
      <div className="flex-shrink-0">{icons[notification.type]}</div>
      <div className="flex-1">
        <h3 className={`font-semibold ${textColors[notification.type]}`}>
          {notification.title}
        </h3>
        {notification.message && (
          <p className={`text-sm mt-1 ${textColors[notification.type]}`}>
            {notification.message}
          </p>
        )}
      </div>
      <button
        onClick={() => onClose?.(notification.id)}
        className={`flex-shrink-0 ${textColors[notification.type]} hover:opacity-70`}
        aria-label="Закрыть уведомление"
      >
        <X className="h-5 w-5" />
      </button>
    </div>
  )
}
