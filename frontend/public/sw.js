// Service Worker для MentorHub
const CACHE_NAME = 'mentorhub-v1'
const OFFLINE_URL = '/offline.html'

// Ресурсы для кэширования при установке
const STATIC_CACHE_URLS = [
  '/',
  '/offline.html',
  '/manifest.json',
  '/icon-192x192.png',
  '/icon-512x512.png',
]

// Установка Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(STATIC_CACHE_URLS).then((cache) => {
      console.log('[Service Worker] Кэширование статических ресурсов')
      return cache.addAll(STATIC_CACHE_URLS)
    })
  )
  // Активируем новый SW сразу
  self.skipWaiting()
})

// Активация Service Worker
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    })
  )
  // Берём контроль над страницами сразу
  self.clients.claim()
})

// Обработка запросов
self.addEventListener('fetch', (event) => {
  // Игнорируем не-GET запросы
  if (event.request.method !== 'GET') return

  // Игнорируем внешние запросы (не к нашему домену)
  if (!event.request.url.startsWith(self.location.origin)) return

  event.respondWith(
    caches.match(event.request).then((cachedResponse) => {
      if (cachedResponse) {
        // Возвращаем из кэша, но обновляем в фоне
        event.waitUntil(updateCache(event.request))
        return cachedResponse
      }

      // Если нет в кэше, делаем запрос к сети
      return fetchAndCache(event.request)
    }).catch(() => {
      // Если офлайн и нет в кэше, показываем offline страницу
      if (event.request.destination === 'document') {
        return caches.match(OFFLINE_URL)
      }
    })
  )
})

// Функция обновления кэша в фоне
async function updateCache(request) {
  try {
    const response = await fetch(request)
    const cache = await caches.open(CACHE_NAME)
    await cache.put(request, response)
  } catch (error) {
    // Игнорируем ошибки сети
  }
}

// Функция запроса к сети с кэшированием
async function fetchAndCache(request) {
  try {
    const response = await fetch(request)
    const cache = await caches.open(CACHE_NAME)
    await cache.put(request, response.clone())
    return response
  } catch (error) {
    throw error
  }
}

// Push уведомления
self.addEventListener('push', (event) => {
  const data = event.data?.json() ?? {}
  const title = data.title ?? 'MentorHub'
  const options = {
    body: data.body ?? 'Новое уведомление',
    icon: '/icon-192x192.png',
    badge: '/icon-192x192.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: data.primaryKey ?? 1,
      url: data.url ?? '/',
    },
    actions: [
      {
        action: 'open',
        title: 'Открыть',
      },
      {
        action: 'close',
        title: 'Закрыть',
      },
    ],
  }

  event.waitUntil(self.registration.showNotification(title, options))
})

// Обработка клика по уведомлению
self.addEventListener('notificationclick', (event) => {
  event.notification.close()

  if (event.action === 'open' || !event.action) {
    const urlToOpen = event.notification.data?.url ?? '/'
    event.waitUntil(
      clients.matchAll({ type: 'window' }).then((windowClients) => {
        // Проверяем есть ли уже открытая вкладка
        for (let client of windowClients) {
          if (client.url === urlToOpen && 'focus' in client) {
            return client.focus()
          }
        }
        // Открываем новую вкладку
        if (clients.openWindow) {
          return clients.openWindow(urlToOpen)
        }
      })
    )
  }
})

// Background sync
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-messages') {
    event.waitUntil(syncMessages())
  }
})

async function syncMessages() {
  // Синхронизация сообщений в фоне
  console.log('[Service Worker] Синхронизация сообщений')
}
