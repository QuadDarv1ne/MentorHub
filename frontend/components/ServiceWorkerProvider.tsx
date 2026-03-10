"use client"

import { useEffect, useState } from 'react'

export default function ServiceWorkerProvider() {
  const [isSupported, setIsSupported] = useState(false)
  const [registration, setRegistration] = useState<ServiceWorkerRegistration | null>(null)
  const [updateAvailable, setUpdateAvailable] = useState(false)

  useEffect(() => {
    // Проверяем поддержку Service Worker
    if ('serviceWorker' in navigator) {
      setIsSupported(true)

      // Регистрируем Service Worker
      window.addEventListener('load', async () => {
        try {
          const reg = await navigator.serviceWorker.register('/sw.js', {
            scope: '/',
          })
          setRegistration(reg)
          console.log('[PWA] Service Worker зарегистрирован:', reg)

          // Проверяем обновления
          reg.addEventListener('updatefound', () => {
            const newWorker = reg.installing
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                  // Доступно обновление
                  setUpdateAvailable(true)
                  console.log('[PWA] Доступно обновление')
                }
              })
            }
          })
        } catch (error) {
          console.error('[PWA] Ошибка регистрации Service Worker:', error)
        }
      })
    }
  }, [])

  // Функция обновления
  const updateServiceWorker = async () => {
    if (registration?.waiting) {
      registration.waiting.postMessage({ type: 'SKIP_WAITING' })
      window.location.reload()
    }
  }

  // Запрос разрешения на уведомления
  const requestNotificationPermission = async () => {
    if ('Notification' in window) {
      const permission = await Notification.requestPermission()
      console.log('[PWA] Разрешение на уведомления:', permission)
      return permission === 'granted'
    }
    return false
  }

  if (!isSupported) {
    return null
  }

  return (
    <>
      {updateAvailable && (
        <div className="fixed bottom-4 right-4 bg-primary-600 text-white px-6 py-3 rounded-lg shadow-lg z-50 flex items-center gap-4 animate-slide-up">
          <span>🔄 Доступно обновление приложения</span>
          <button
            onClick={updateServiceWorker}
            className="bg-white text-primary-600 px-4 py-2 rounded-md font-medium hover:bg-gray-100 transition-colors"
          >
            Обновить
          </button>
          <button
            onClick={() => setUpdateAvailable(false)}
            className="text-white hover:text-gray-200 transition-colors"
            aria-label="Закрыть"
          >
            ✕
          </button>
        </div>
      )}

      <button
        onClick={requestNotificationPermission}
        className="fixed bottom-4 left-4 bg-gray-800 dark:bg-gray-700 text-white px-4 py-2 rounded-lg shadow-lg text-sm hover:bg-gray-900 dark:hover:bg-gray-600 transition-colors z-40"
        title="Включить уведомления"
      >
        🔔 Уведомления
      </button>
    </>
  )
}
