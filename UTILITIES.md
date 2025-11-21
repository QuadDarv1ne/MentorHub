# 📚 Документация утилит MentorHub

## Обзор

Данная документация описывает все вспомогательные утилиты проекта MentorHub. Утилиты организованы по функциональным категориям и предоставляют готовые решения для типичных задач.

---

## 📁 Структура утилит

```
lib/
├── hooks/                    # React хуки
│   ├── useAuth.ts           # Аутентификация и защита роутов
│   ├── useNotifications.ts  # Система уведомлений
│   └── usePerformance.ts    # Хуки производительности
├── utils/                   # Вспомогательные функции
│   ├── api.ts              # API клиент и WebSocket
│   ├── date.ts             # Работа с датами
│   ├── format.ts           # Форматирование данных
│   ├── performance.ts      # Оптимизация производительности
│   ├── security.ts         # Безопасность
│   ├── validation.ts       # Валидация форм
│   └── lazyLoad.tsx        # Ленивая загрузка компонентов
├── context/                 # React контексты
│   └── NotificationContext.tsx
└── constants.ts            # Константы приложения
```

---

## 🔐 Аутентификация (useAuth)

### Описание
Хук для управления аутентификацией и защиты страниц от неавторизованного доступа.

### Использование

```typescript
import { useAuth } from '@/lib/hooks/useAuth'

export default function ProtectedPage() {
  const { isLoading } = useAuth()

  if (isLoading) {
    return <div>Загрузка...</div>
  }

  return <div>Защищенный контент</div>
}
```

### Защищенные роуты
- `/profile` - Профиль пользователя
- `/settings` - Настройки
- `/dashboard` - Панель управления
- `/sessions` - Сессии с менторами
- `/booking` - Бронирование
- `/messages` - Сообщения
- `/notifications` - Уведомления
- `/stats` - Статистика
- `/achievements` - Достижения
- `/billing` - Счета и оплата
- `/payment` - Платежи
- `/learning` - Мое обучение

---

## 🔔 Система уведомлений (useNotifications)

### Описание
Хук для управления уведомлениями с сохранением в localStorage.

### Интерфейс Notification

```typescript
interface Notification {
  id: string
  type: 'info' | 'success' | 'warning' | 'error'
  title: string
  message: string
  timestamp: Date
  read: boolean
}
```

### API

#### useNotifications()

```typescript
const {
  notifications,        // Массив всех уведомлений
  unreadCount,         // Количество непрочитанных
  addNotification,     // Добавить уведомление
  removeNotification,  // Удалить по ID
  markAsRead,          // Отметить как прочитанное
  markAllAsRead,       // Отметить все как прочитанные
  clearAll,            // Удалить все
  clearRead            // Удалить прочитанные
} = useNotifications()
```

#### Пример использования

```typescript
// Добавление уведомления
addNotification({
  type: 'success',
  title: 'Успешно',
  message: 'Профиль обновлен'
})

// Отметить как прочитанное
markAsRead('notification-id')

// Удалить
removeNotification('notification-id')
```

### useToast()

Хук для временных всплывающих сообщений (toast).

```typescript
const { success, error, warning, info } = useToast()

// Использование
success('Данные сохранены')
error('Ошибка подключения')
warning('Внимание: срок подписки истекает')
info('Новое сообщение от ментора')
```

### NotificationCenter

Компонент для отображения центра уведомлений.

```typescript
import { NotificationCenter } from '@/components/NotificationCenter'

<NotificationCenter />
```

---

## 🌐 API клиент (api.ts)

### Описание
Централизованный клиент для работы с API и WebSocket.

### Конфигурация

Переменная окружения:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### REST API

#### Аутентификация

```typescript
import { api } from '@/lib/utils/api'

// Вход
const { access_token, user } = await api.auth.login({
  email: 'user@example.com',
  password: 'password123'
})

// Регистрация
await api.auth.register({
  email: 'user@example.com',
  password: 'password123',
  name: 'Иван Иванов'
})

// Восстановление пароля
await api.auth.forgotPassword({ email: 'user@example.com' })

// Сброс пароля
await api.auth.resetPassword({
  token: 'reset-token',
  password: 'newPassword123'
})
```

#### Пользователи

```typescript
// Получить текущего пользователя
const user = await api.users.me()

// Обновить профиль
await api.users.update({ name: 'Новое имя', bio: 'О себе' })

// Получить пользователя по ID
const user = await api.users.get(123)
```

#### Менторы

```typescript
// Список менторов
const mentors = await api.mentors.list({
  skills: ['JavaScript', 'React'],
  minRating: 4.5
})

// Получить ментора
const mentor = await api.mentors.get(456)

// Подать заявку на роль ментора
await api.mentors.apply({
  skills: ['Python', 'Django'],
  experience: 5,
  bio: 'Опытный разработчик...'
})

// Отзывы о менторе
const reviews = await api.mentors.reviews(456)
```

#### Сессии

```typescript
// Список сессий
const sessions = await api.sessions.list()

// Создать сессию
const session = await api.sessions.create({
  mentor_id: 456,
  scheduled_at: '2024-12-30T10:00:00Z',
  duration: 60,
  topic: 'Code Review'
})

// Завершить сессию
await api.sessions.complete(789, {
  rating: 5,
  comment: 'Отличная сессия!'
})
```

#### Курсы

```typescript
// Список курсов
const courses = await api.courses.list()

// Записаться на курс
await api.courses.enroll(123)

// Прогресс
const progress = await api.courses.progress(123)
```

#### Сообщения

```typescript
// Список чатов
const chats = await api.messages.chats()

// История чата
const messages = await api.messages.chatHistory(456)

// Отправить сообщение
await api.messages.send({
  chat_id: 456,
  content: 'Здравствуйте!'
})
```

#### Платежи

```typescript
// Создать платеж
const payment = await api.payments.create({
  amount: 1000,
  type: 'session',
  session_id: 789
})

// История платежей
const history = await api.payments.history()
```

### WebSocket

```typescript
import { WebSocketClient } from '@/lib/utils/api'

const ws = new WebSocketClient()

// Подключение
ws.connect(
  (data) => {
    console.log('Получено сообщение:', data)
  },
  (error) => {
    console.error('Ошибка WebSocket:', error)
  }
)

// Отправка данных
ws.send({ type: 'message', content: 'Привет!' })

// Отключение
ws.disconnect()
```

### Обработка ошибок

```typescript
import { ApiError } from '@/lib/utils/api'

try {
  await api.auth.login({ email, password })
} catch (error) {
  if (error instanceof ApiError) {
    console.error('Статус:', error.status)
    console.error('Данные:', error.data)
  }
}
```

---

## 📅 Работа с датами (date.ts)

### Форматирование

```typescript
import { formatDate, formatTime, formatDateTime } from '@/lib/utils/date'

formatDate(new Date(), 'short')  // "30.12.2024"
formatDate(new Date(), 'long')   // "30 декабря 2024"
formatDate(new Date(), 'full')   // "понедельник, 30 декабря 2024"

formatTime(new Date())           // "14:30"
formatDateTime(new Date())       // "30.12.2024 14:30"
```

### Относительное время

```typescript
import { getRelativeTime } from '@/lib/utils/date'

getRelativeTime(new Date())                    // "только что"
getRelativeTime(new Date(Date.now() - 60000))  // "1 минуту назад"
getRelativeTime(new Date(Date.now() - 3600000)) // "1 час назад"
```

### Манипуляции с датами

```typescript
import { addDays, subtractDays, daysDifference } from '@/lib/utils/date'

addDays(new Date(), 7)           // Дата через 7 дней
subtractDays(new Date(), 3)      // Дата 3 дня назад
daysDifference(date1, date2)     // Разница в днях
```

### Проверки

```typescript
import { isToday, isYesterday, isTomorrow, isWeekend } from '@/lib/utils/date'

isToday(new Date())              // true
isYesterday(date)                // false
isWeekend(new Date())            // зависит от дня недели
```

### Диапазоны

```typescript
import { getWeekRange, getMonthRange } from '@/lib/utils/date'

const { start, end } = getWeekRange(new Date())
const { start, end } = getMonthRange(new Date())
```

### Длительность

```typescript
import { formatDuration } from '@/lib/utils/date'

formatDuration(45)   // "45 мин"
formatDuration(90)   // "1 ч 30 мин"
formatDuration(120)  // "2 ч"
```

---

## 📝 Форматирование данных (format.ts)

### Числа

```typescript
import { formatNumber, formatCurrency, abbreviateNumber, formatPercent } from '@/lib/utils/format'

formatNumber(1234567.89, 2)      // "1 234 567,89"
formatCurrency(1000, 'RUB')      // "1 000 ₽"
abbreviateNumber(1500)           // "1.5K"
formatPercent(75.5, 1)           // "75.5%"
```

### Строки

```typescript
import { 
  capitalize, 
  capitalizeWords, 
  truncate, 
  toKebabCase, 
  toCamelCase,
  toPascalCase 
} from '@/lib/utils/format'

capitalize('hello world')         // "Hello world"
capitalizeWords('hello world')    // "Hello World"
truncate('Long text...', 10)      // "Long te..."
toKebabCase('HelloWorld')         // "hello-world"
toCamelCase('hello-world')        // "helloWorld"
toPascalCase('hello-world')       // "HelloWorld"
```

### Цвета

```typescript
import { hexToRgb, rgbToHex, randomColor } from '@/lib/utils/format'

hexToRgb('#FF5733')              // { r: 255, g: 87, b: 51 }
rgbToHex(255, 87, 51)            // "#FF5733"
randomColor()                    // "#A3B2C1"
```

### Маскирование

```typescript
import { maskEmail, maskPhone, maskCard } from '@/lib/utils/format'

maskEmail('test@example.com')           // "t***@example.com"
maskPhone('+79150480249')               // "+7915***-**-49"
maskCard('4111111111111111')            // "4111 **** **** 1111"
```

### Массивы

```typescript
import { chunk, shuffle, unique, groupBy, sortBy } from '@/lib/utils/format'

chunk([1, 2, 3, 4, 5], 2)               // [[1, 2], [3, 4], [5]]
shuffle([1, 2, 3, 4, 5])                // [3, 1, 5, 2, 4]
unique([1, 2, 2, 3, 3, 3])              // [1, 2, 3]
groupBy(users, 'role')                  // { admin: [...], user: [...] }
sortBy(users, 'name', 'asc')            // Отсортированный массив
```

---

## ✅ Валидация (validation.ts)

### Email и телефон

```typescript
import { isValidEmail, isValidPhone, formatPhone } from '@/lib/utils/validation'

isValidEmail('user@example.com')        // true
isValidPhone('+79150480249')            // true
formatPhone('89150480249')              // "+7 915 048-02-49"
```

### Пароли

```typescript
import { validatePassword } from '@/lib/utils/validation'

const result = validatePassword('MyPass123!')
// {
//   isValid: true,
//   strength: 4,
//   errors: []
// }
```

Уровни силы пароля:
- 0: Очень слабый (< 6 символов)
- 1: Слабый (≥ 6 символов)
- 2: Средний (≥ 6 символов + цифры)
- 3: Хороший (≥ 6 символов + цифры + смешанный регистр)
- 4: Сильный (≥ 10 символов + цифры + смешанный регистр)
- 5: Очень сильный (≥ 10 символов + цифры + смешанный регистр + спецсимволы)

### Банковские карты

```typescript
import { isValidCreditCard, formatCardNumber } from '@/lib/utils/validation'

isValidCreditCard('4111111111111111')   // true (алгоритм Луна)
formatCardNumber('4111111111111111')    // "4111 1111 1111 1111"
```

### Файлы

```typescript
import { isValidFileType, isValidFileSize } from '@/lib/utils/validation'

isValidFileType(file, ['image/jpeg', 'image/png'])  // true/false
isValidFileSize(file, 5 * 1024 * 1024)              // true/false
```

### Российские форматы

```typescript
import { isValidINN, isValidZipCode } from '@/lib/utils/validation'

isValidINN('7743013902')        // true (10 или 12 цифр)
isValidZipCode('123456')        // true
```

### XSS защита

```typescript
import { sanitizeHtml } from '@/lib/utils/validation'

sanitizeHtml('<script>alert("XSS")</script>Hello')  // "Hello"
```

---

## ⚡ Производительность (performance.ts)

### Debounce

```typescript
import { debounce } from '@/lib/utils/performance'

const handleSearch = debounce((query: string) => {
  // API запрос выполнится только через 300ms после последнего ввода
  api.search(query)
}, 300)
```

### Throttle

```typescript
import { throttle } from '@/lib/utils/performance'

const handleScroll = throttle(() => {
  // Функция вызовется максимум раз в 1000ms
  console.log('Scrolling...')
}, 1000)
```

### Memoization

```typescript
import { memoize } from '@/lib/utils/performance'

const expensiveCalculation = memoize((n: number) => {
  // Результат кешируется для каждого уникального n
  return Array.from({ length: n }, (_, i) => i).reduce((a, b) => a + b, 0)
})
```

---

## 🎨 Ленивая загрузка (lazyLoad.tsx)

```typescript
import { lazyLoad } from '@/lib/utils/lazyLoad'

const HeavyComponent = lazyLoad(
  () => import('@/components/HeavyComponent'),
  { fallback: <div>Загрузка компонента...</div> }
)

export default function Page() {
  return (
    <div>
      <HeavyComponent />
    </div>
  )
}
```

---

## 📋 Константы (constants.ts)

### API Endpoints

```typescript
import { API_ENDPOINTS } from '@/lib/constants'

API_ENDPOINTS.AUTH.LOGIN            // '/api/v1/auth/login'
API_ENDPOINTS.USERS.BY_ID(123)      // '/api/v1/users/123'
```

### Роуты

```typescript
import { ROUTES } from '@/lib/constants'

ROUTES.HOME                         // '/'
ROUTES.AUTH.LOGIN                   // '/auth/login'
ROUTES.DASHBOARD                    // '/dashboard'
```

### LocalStorage ключи

```typescript
import { STORAGE_KEYS } from '@/lib/constants'

localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, token)
localStorage.getItem(STORAGE_KEYS.USER_DATA)
```

### Лимиты

```typescript
import { LIMITS } from '@/lib/constants'

LIMITS.MAX_FILE_SIZE                // 10 MB
LIMITS.MAX_IMAGE_SIZE               // 5 MB
LIMITS.MIN_PASSWORD_LENGTH          // 6
```

### Таймауты

```typescript
import { TIMEOUTS } from '@/lib/constants'

TIMEOUTS.DEBOUNCE                   // 300ms
TIMEOUTS.API_TIMEOUT                // 30000ms
TIMEOUTS.TOAST_DURATION             // 3000ms
```

---

## 🛡️ Безопасность (security.ts)

### Хеширование паролей

```typescript
import { hashPassword, verifyPassword } from '@/lib/utils/security'

// На клиенте не используется, только для примера
const hashed = await hashPassword('myPassword123')
const isValid = await verifyPassword('myPassword123', hashed)
```

### JWT токены

```typescript
import { generateToken, verifyToken } from '@/lib/utils/security'

const token = generateToken({ userId: 123 })
const payload = verifyToken(token)
```

---

## 📊 Примеры использования

### Форма с валидацией

```typescript
'use client'

import { useState } from 'react'
import { isValidEmail, validatePassword } from '@/lib/utils/validation'
import { useToast } from '@/lib/hooks/useNotifications'

export default function RegisterForm() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const { success, error } = useToast()

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!isValidEmail(email)) {
      error('Неверный формат email')
      return
    }

    const passwordResult = validatePassword(password)
    if (!passwordResult.isValid) {
      error(passwordResult.errors[0])
      return
    }

    // Отправка формы
    success('Регистрация успешна!')
  }

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Пароль"
      />
      <button type="submit">Зарегистрироваться</button>
    </form>
  )
}
```

### Поиск с debounce

```typescript
'use client'

import { useState, useEffect } from 'react'
import { debounce } from '@/lib/utils/performance'
import { api } from '@/lib/utils/api'

export default function SearchComponent() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  useEffect(() => {
    const debouncedSearch = debounce(async (searchQuery: string) => {
      if (searchQuery.length < 2) return
      
      const data = await api.mentors.list({ search: searchQuery })
      setResults(data)
    }, 300)

    debouncedSearch(query)
  }, [query])

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Поиск менторов..."
      />
      <ul>
        {results.map(mentor => (
          <li key={mentor.id}>{mentor.name}</li>
        ))}
      </ul>
    </div>
  )
}
```

---

## 🔗 Связанные документы

- [AUTHENTICATION.md](./AUTHENTICATION.md) - Документация по аутентификации
- [CONTRIBUTING.md](./CONTRIBUTING.md) - Руководство для разработчиков
- [README.md](./README.md) - Основная документация проекта

---

**Версия**: 1.0  
**Дата обновления**: Декабрь 2024  
**Автор**: QuadDarv1ne
