/**
 * Оптимизированные переиспользуемые UI компоненты
 * React.memo для предотвращения лишних рендеров
 */

import React from 'react'
import { Loader2 } from 'lucide-react'

// Кнопка с состоянием загрузки
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  fullWidth?: boolean
  children: React.ReactNode
}

export const Button = React.memo<ButtonProps>(({
  loading = false,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed'
  
  const variants = {
    primary: 'bg-indigo-600 text-white hover:bg-indigo-700 focus:ring-indigo-500',
    secondary: 'bg-gray-600 text-white hover:bg-gray-700 focus:ring-gray-500',
    outline: 'border-2 border-indigo-600 text-indigo-600 hover:bg-indigo-50 focus:ring-indigo-500',
    ghost: 'text-gray-700 hover:bg-gray-100 focus:ring-gray-500',
    danger: 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500',
  }
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }
  
  const widthClass = fullWidth ? 'w-full' : ''
  
  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${widthClass} ${className}`}
      disabled={disabled || loading}
      {...props}
    >
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </button>
  )
})

Button.displayName = 'Button'

// Input с иконкой и состоянием ошибки
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  icon?: React.ReactNode
  fullWidth?: boolean
}

export const Input = React.memo<InputProps>(({
  label,
  error,
  helperText,
  icon,
  fullWidth = false,
  className = '',
  id,
  ...props
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`
  const hasError = Boolean(error)
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label
          htmlFor={inputId}
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          {label}
        </label>
      )}
      <div className="relative">
        {icon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {icon}
          </div>
        )}
        <input
          id={inputId}
          className={`
            appearance-none block w-full rounded-lg shadow-sm
            ${icon ? 'pl-10' : 'pl-3'} pr-3 py-3
            border ${hasError ? 'border-red-300 focus:border-red-500 focus:ring-red-500' : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'}
            placeholder-gray-400
            focus:outline-none focus:ring-2
            transition-colors
            ${className}
          `}
          aria-invalid={hasError ? 'true' : 'false'}
          aria-describedby={error ? `${inputId}-error` : helperText ? `${inputId}-helper` : undefined}
          {...props}
        />
      </div>
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}
      {helperText && !error && (
        <p id={`${inputId}-helper`} className="mt-1 text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  )
})

Input.displayName = 'Input'

// Alert/Notification компонент
interface AlertProps {
  type: 'success' | 'error' | 'warning' | 'info'
  title?: string
  message: string
  onClose?: () => void
  icon?: React.ReactNode
}

export const Alert = React.memo<AlertProps>(({ type, title, message, onClose, icon }) => {
  const styles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
  }
  
  const iconColors = {
    success: 'text-green-600',
    error: 'text-red-600',
    warning: 'text-yellow-600',
    info: 'text-blue-600',
  }
  
  return (
    <div className={`p-4 rounded-lg border ${styles[type]} flex items-start space-x-3`} role="alert">
      {icon && <span className={`flex-shrink-0 ${iconColors[type]}`}>{icon}</span>}
      <div className="flex-1">
        {title && <h4 className="font-medium mb-1">{title}</h4>}
        <p className="text-sm">{message}</p>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className={`flex-shrink-0 ${iconColors[type]} hover:opacity-70`}
          aria-label="Закрыть уведомление"
        >
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        </button>
      )}
    </div>
  )
})

Alert.displayName = 'Alert'

// Card компонент
interface CardProps {
  children: React.ReactNode
  className?: string
  padding?: boolean
  hoverable?: boolean
  onClick?: () => void
}

export const Card = React.memo<CardProps>(({
  children,
  className = '',
  padding = true,
  hoverable = false,
  onClick,
}) => {
  const interactiveClass = onClick ? 'cursor-pointer' : ''
  const hoverClass = hoverable ? 'hover:shadow-lg transition-shadow' : ''
  const paddingClass = padding ? 'p-6' : ''
  
  if (onClick) {
    return (
      <div
        className={`bg-white rounded-lg border border-gray-200 shadow-sm ${paddingClass} ${hoverClass} ${interactiveClass} ${className}`}
        onClick={onClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && onClick()}
      >
        {children}
      </div>
    )
  }
  
  return (
    <div
      className={`bg-white rounded-lg border border-gray-200 shadow-sm ${paddingClass} ${hoverClass} ${className}`}
    >
      {children}
    </div>
  )
})

Card.displayName = 'Card'

// Badge компонент
interface BadgeProps {
  children: React.ReactNode
  variant?: 'default' | 'success' | 'warning' | 'error' | 'info'
  size?: 'sm' | 'md' | 'lg'
}

export const Badge = React.memo<BadgeProps>(({
  children,
  variant = 'default',
  size = 'md',
}) => {
  const variants = {
    default: 'bg-gray-100 text-gray-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800',
    info: 'bg-blue-100 text-blue-800',
  }
  
  const sizes = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-sm',
    lg: 'px-3 py-1.5 text-base',
  }
  
  return (
    <span className={`inline-flex items-center font-medium rounded-full ${variants[variant]} ${sizes[size]}`}>
      {children}
    </span>
  )
})

Badge.displayName = 'Badge'

// Skeleton loader
interface SkeletonProps {
  className?: string
  variant?: 'text' | 'circular' | 'rectangular'
  width?: string | number
  height?: string | number
}

export const Skeleton = React.memo<SkeletonProps>(({
  className = '',
  variant = 'text',
  width,
  height,
}) => {
  const variantClass = {
    text: 'rounded',
    circular: 'rounded-full',
    rectangular: 'rounded-md',
  }[variant]
  
  const widthClass = width ? (typeof width === 'number' ? `w-[${width}px]` : width) : 'w-full'
  const heightClass = height ? (typeof height === 'number' ? `h-[${height}px]` : height) : 'h-4'
  
  return (
    <div
      className={`animate-pulse bg-gray-200 ${variantClass} ${widthClass} ${heightClass} ${className}`}
      aria-hidden="true"
    />
  )
})

Skeleton.displayName = 'Skeleton'

// Divider
interface DividerProps {
  orientation?: 'horizontal' | 'vertical'
  className?: string
  label?: string
}

export const Divider = React.memo<DividerProps>(({
  orientation = 'horizontal',
  className = '',
  label,
}) => {
  if (orientation === 'vertical') {
    return <div className={`w-px bg-gray-200 ${className}`} role="separator" aria-orientation="vertical" />
  }
  
  if (label) {
    return (
      <div className={`relative flex items-center ${className}`}>
        <div className="flex-grow border-t border-gray-200" role="separator" />
        <span className="px-3 text-sm text-gray-500 bg-white">{label}</span>
        <div className="flex-grow border-t border-gray-200" />
      </div>
    )
  }
  
  return <hr className={`border-gray-200 ${className}`} />
})

Divider.displayName = 'Divider'
