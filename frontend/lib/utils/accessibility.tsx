/**
 * Accessibility компоненты и хуки
 * Skip links, focus management, ARIA utilities
 */

'use client'

import React, { useEffect, useRef } from 'react'
import { usePathname } from 'next/navigation'

// Skip Navigation Links
export function SkipLinks() {
  return (
    <div className="sr-only focus:not-sr-only">
      <a
        href="#main-content"
        className="fixed top-0 left-0 z-50 bg-indigo-600 text-white px-4 py-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Перейти к основному содержимому
      </a>
      <a
        href="#navigation"
        className="fixed top-0 left-0 z-50 bg-indigo-600 text-white px-4 py-2 ml-2 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
      >
        Перейти к навигации
      </a>
    </div>
  )
}

// Focus Trap для модальных окон
interface FocusTrapProps {
  children: React.ReactNode
  active?: boolean
}

export function FocusTrap({ children, active = true }: FocusTrapProps) {
  const containerRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!active) return

    const container = containerRef.current
    if (!container) return

    const focusableElements = container.querySelectorAll<HTMLElement>(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )

    const firstElement = focusableElements[0]
    const lastElement = focusableElements[focusableElements.length - 1]

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return

      if (e.shiftKey) {
        // Shift + Tab
        if (document.activeElement === firstElement) {
          e.preventDefault()
          lastElement.focus()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          e.preventDefault()
          firstElement.focus()
        }
      }
    }

    // Установить фокус на первый элемент при монтировании
    firstElement?.focus()

    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [active])

  return (
    <div ref={containerRef} tabIndex={-1}>
      {children}
    </div>
  )
}

// Автоматический фокус на главном контенте при смене роута
export function RouteAnnouncer() {
  const pathname = usePathname()
  const announceRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (announceRef.current) {
      // Сообщить скринридерам о смене страницы
      announceRef.current.textContent = `Переход на страницу ${document.title}`
      
      // Переместить фокус на main content
      const mainContent = document.getElementById('main-content')
      if (mainContent) {
        mainContent.focus()
      }
    }
  }, [pathname])

  return (
    <div
      ref={announceRef}
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
    />
  )
}

// Визуально скрытый текст (для скринридеров)
interface VisuallyHiddenProps {
  children: React.ReactNode
  as?: keyof JSX.IntrinsicElements
}

export function VisuallyHidden({ children, as: Component = 'span' }: VisuallyHiddenProps) {
  return <Component className="sr-only">{children}</Component>
}

// Хук для управления фокусом
export function useFocusManagement() {
  const previousFocusRef = useRef<HTMLElement | null>(null)

  const saveFocus = () => {
    previousFocusRef.current = document.activeElement as HTMLElement
  }

  const restoreFocus = () => {
    previousFocusRef.current?.focus()
  }

  const focusElement = (selector: string) => {
    const element = document.querySelector<HTMLElement>(selector)
    element?.focus()
  }

  return { saveFocus, restoreFocus, focusElement }
}

// Хук для объявлений скринридеру
export function useAnnouncer() {
  const announceRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    // Создать aria-live регион если его нет
    if (!announceRef.current) {
      const div = document.createElement('div')
      div.setAttribute('role', 'status')
      div.setAttribute('aria-live', 'polite')
      div.setAttribute('aria-atomic', 'true')
      div.className = 'sr-only'
      document.body.appendChild(div)
      announceRef.current = div
    }

    return () => {
      announceRef.current?.remove()
    }
  }, [])

  const announce = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
    if (announceRef.current) {
      announceRef.current.setAttribute('aria-live', priority)
      announceRef.current.textContent = message
    }
  }

  return announce
}

// Компонент для ARIA описаний
interface AriaDescriptionProps {
  id: string
  children: React.ReactNode
}

export function AriaDescription({ id, children }: AriaDescriptionProps) {
  return (
    <div id={id} className="sr-only">
      {children}
    </div>
  )
}

// Хелпер для генерации уникальных ID (для aria-labelledby, aria-describedby)
let idCounter = 0

export function useUniqueId(prefix = 'id'): string {
  const idRef = useRef<string>()

  if (!idRef.current) {
    idRef.current = `${prefix}-${++idCounter}`
  }

  return idRef.current
}

// Keyboard Navigation Helper
export function useKeyboardNav(
  items: unknown[],
  onSelect?: (index: number) => void
) {
  const [focusedIndex, setFocusedIndex] = React.useState(-1)

  const handleKeyDown = (e: React.KeyboardEvent) => {
    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault()
        setFocusedIndex((prev) => (prev + 1) % items.length)
        break
      case 'ArrowUp':
        e.preventDefault()
        setFocusedIndex((prev) => (prev - 1 + items.length) % items.length)
        break
      case 'Home':
        e.preventDefault()
        setFocusedIndex(0)
        break
      case 'End':
        e.preventDefault()
        setFocusedIndex(items.length - 1)
        break
      case 'Enter':
      case ' ':
        e.preventDefault()
        if (focusedIndex >= 0 && onSelect) {
          onSelect(focusedIndex)
        }
        break
      case 'Escape':
        setFocusedIndex(-1)
        break
    }
  }

  return {
    focusedIndex,
    setFocusedIndex,
    handleKeyDown,
  }
}
