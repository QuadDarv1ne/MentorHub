# UI Components

Переиспользуемые UI компоненты для MentorHub.

## Button

Кнопка с различными вариантами стилей.

```tsx
import { Button } from '@/components/ui'

<Button variant="primary" size="md">
  Нажми меня
</Button>
```

**Props:**
- `variant`: 'primary' | 'secondary' | 'outline' | 'danger' | 'ghost'
- `size`: 'sm' | 'md' | 'lg'
- `fullWidth`: boolean
- `loading`: boolean

## Input

Поле ввода с поддержкой label, error и helper text.

```tsx
import { Input } from '@/components/ui'

<Input
  label="Email"
  type="email"
  error="Неверный формат email"
  helperText="Введите ваш email"
  required
  fullWidth
/>
```

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `fullWidth`: boolean
- все стандартные пропсы HTMLInputElement

## Textarea

Многострочное поле ввода.

```tsx
import { Textarea } from '@/components/ui'

<Textarea
  label="Описание"
  rows={4}
  error="Обязательное поле"
  fullWidth
/>
```

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `fullWidth`: boolean
- `rows`: number
- все стандартные пропсы HTMLTextareaElement

## Select

Выпадающий список.

```tsx
import { Select } from '@/components/ui'

const options = [
  { value: '1', label: 'Вариант 1' },
  { value: '2', label: 'Вариант 2' },
]

<Select
  label="Выберите вариант"
  options={options}
  error="Выберите значение"
  fullWidth
/>
```

**Props:**
- `label`: string
- `error`: string
- `helperText`: string
- `fullWidth`: boolean
- `options`: { value: string; label: string }[]
- все стандартные пропсы HTMLSelectElement

## Card

Контейнер для контента с рамкой и тенью.

```tsx
import { Card } from '@/components/ui'

<Card hover padding="md">
  <h3>Заголовок</h3>
  <p>Контент</p>
</Card>
```

**Props:**
- `hover`: boolean - эффект при наведении
- `padding`: 'none' | 'sm' | 'md' | 'lg'

## Badge

Бейджик для отображения статуса или категории.

```tsx
import { Badge } from '@/components/ui'

<Badge variant="success" size="sm">
  Активен
</Badge>
```

**Props:**
- `variant`: 'default' | 'success' | 'warning' | 'danger' | 'info'
- `size`: 'sm' | 'md' | 'lg'

## StatCard

Карточка для отображения статистики.

```tsx
import { StatCard } from '@/components/ui'
import { Users } from 'lucide-react'

<StatCard
  title="Пользователей"
  value="15,000+"
  icon={<Users className="h-6 w-6" />}
  trend={{ value: 12, isPositive: true }}
  description="За последний месяц"
/>
```

**Props:**
- `title`: string
- `value`: string | number
- `icon`: ReactNode
- `trend`: { value: number; isPositive: boolean }
- `description`: string

## TestimonialCard

Карточка для отображения отзыва пользователя.

```tsx
import { TestimonialCard } from '@/components/ui'

<TestimonialCard
  name="Иван Иванов"
  role="Frontend Developer"
  text="Отличная платформа!"
  rating={5}
/>
```

**Props:**
- `name`: string
- `role`: string
- `text`: string
- `rating`: number (0-5)

## Использование

Все компоненты можно импортировать напрямую или через barrel export:

```tsx
// Напрямую
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'

// Через barrel export
import { Button, Input, Card } from '@/components/ui'
```
