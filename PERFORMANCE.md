# Улучшения производительности и UX

## Обзор

Документ описывает оптимизации производительности, улучшения пользовательского опыта и доступности, внедренные в проект MentorHub.

## 1. SEO и Метаданные

### Утилита `lib/utils/seo.ts`

**Функционал:**
- Генерация метаданных с Open Graph и Twitter Cards
- Поддержка структурированных данных (JSON-LD)
- Предустановки для типовых страниц
- Управление индексацией (robots, canonical)

**Использование:**

```typescript
import { seoPresets, generateSEOMetadata } from '@/lib/utils/seo'

// Для типовых страниц
export const metadata = seoPresets.home()

// Кастомная конфигурация
export const metadata = generateSEOMetadata({
  title: 'Мой заголовок',
  description: 'Описание страницы',
  path: '/my-page',
  image: '/my-image.png',
})
```

**Структурированные данные:**

```typescript
import { generateOrganizationSchema, generateCourseSchema } from '@/lib/utils/seo'

// Для главной страницы
<script type="application/ld+json">
  {JSON.stringify(generateOrganizationSchema())}
</script>

// Для страницы курса
<script type="application/ld+json">
  {JSON.stringify(generateCourseSchema({
    name: 'React Advanced',
    description: 'Продвинутый курс React',
    provider: 'MentorHub',
    url: 'https://mentorhub.com/courses/react-advanced',
    price: 5000,
  }))}
</script>
```

## 2. Оптимизированные UI компоненты

### `components/ui/OptimizedUI.tsx`

Переиспользуемые компоненты с React.memo для предотвращения лишних рендеров:

**Button** - кнопка с состояниями loading
```typescript
<Button variant="primary" size="md" loading={isSubmitting}>
  Отправить
</Button>
```

**Input** - поле ввода с иконками и ошибками
```typescript
<Input
  label="Email"
  icon={<Mail />}
  error={errors.email}
  helperText="Введите корректный email"
/>
```

**Alert** - уведомления
```typescript
<Alert
  type="success"
  title="Успешно"
  message="Данные сохранены"
  onClose={() => {}}
/>
```

**Card** - карточка контента
```typescript
<Card hoverable onClick={() => {}}>
  Контент
</Card>
```

**Badge** - значок/метка
```typescript
<Badge variant="success" size="md">
  Активен
</Badge>
```

## 3. Loading Skeletons

### `components/ui/Skeletons.tsx`

Улучшенный UX во время загрузки данных:

```typescript
import {
  Skeleton,
  CardSkeleton,
  ListSkeleton,
  TableSkeleton,
  DashboardSkeleton,
} from '@/components/ui/Skeletons'

// Базовый скелетон
<Skeleton variant="text" width={200} lines={3} />

// Скелетон карточки
<CardSkeleton />

// Скелетон списка
<ListSkeleton count={5} />

// Полный дашборд
{loading ? <DashboardSkeleton /> : <Dashboard data={data} />}
```

## 4. Управление формами

### `lib/hooks/useForm.ts`

Универсальный хук с валидацией в реальном времени:

```typescript
import { useForm, validators } from '@/lib/hooks/useForm'

const { values, errors, handleChange, handleSubmit } = useForm(
  {
    email: {
      initialValue: '',
      rules: [
        validators.required(),
        validators.email(),
      ],
      validateOn: 'blur',
    },
    password: {
      initialValue: '',
      rules: [
        validators.required(),
        validators.minLength(6),
      ],
    },
  },
  async (data) => {
    await login(data)
  }
)

<form onSubmit={handleSubmit}>
  <Input {...getFieldProps('email')} />
  <Input {...getFieldProps('password')} type="password" />
  <Button type="submit" loading={isSubmitting}>Войти</Button>
</form>
```

**Встроенные валидаторы:**
- `required()` - обязательное поле
- `email()` - email формат
- `minLength(n)` / `maxLength(n)` - длина
- `pattern(regex)` - регулярное выражение
- `min(n)` / `max(n)` - числовой диапазон
- `match(fieldName)` - совпадение с другим полем
- `url()` - URL формат
- `phone()` - телефон
- `async()` - асинхронная проверка

## 5. Error Boundaries

### `components/ErrorBoundary.tsx`

Перехват и обработка ошибок React:

```typescript
import { ErrorBoundary, AuthErrorBoundary, DashboardErrorBoundary } from '@/components/ErrorBoundary'

// Базовый
<ErrorBoundary>
  <MyComponent />
</ErrorBoundary>

// С кастомным fallback
<ErrorBoundary fallback={<CustomError />}>
  <MyComponent />
</ErrorBoundary>

// Специализированные
<AuthErrorBoundary>
  <LoginForm />
</AuthErrorBoundary>

<DashboardErrorBoundary>
  <Dashboard />
</DashboardErrorBoundary>
```

## 6. Accessibility

### `lib/utils/accessibility.tsx`

Улучшения доступности:

**Skip Links** - переход к основному контенту
```typescript
import { SkipLinks } from '@/lib/utils/accessibility'

<SkipLinks /> // В layout
```

**Route Announcer** - объявление смены роута для скринридеров
```typescript
import { RouteAnnouncer } from '@/lib/utils/accessibility'

<RouteAnnouncer /> // В layout
```

**Focus Trap** - ловушка фокуса для модалок
```typescript
import { FocusTrap } from '@/lib/utils/accessibility'

<FocusTrap active={isOpen}>
  <Modal>...</Modal>
</FocusTrap>
```

**Хуки:**

```typescript
import { useFocusManagement, useAnnouncer, useKeyboardNav } from '@/lib/utils/accessibility'

// Управление фокусом
const { saveFocus, restoreFocus, focusElement } = useFocusManagement()

// Объявления скринридеру
const announce = useAnnouncer()
announce('Данные успешно сохранены', 'polite')

// Клавиатурная навигация
const { focusedIndex, handleKeyDown } = useKeyboardNav(items, (index) => {
  selectItem(index)
})
```

**VisuallyHidden** - скрытие для зрячих, доступно скринридерам
```typescript
import { VisuallyHidden } from '@/lib/utils/accessibility'

<VisuallyHidden>
  Дополнительная информация для скринридеров
</VisuallyHidden>
```

## 7. Общие рекомендации

### Производительность

1. **React.memo** - используйте для компонентов без частых изменений props
2. **useCallback/useMemo** - для тяжелых вычислений и функций в deps
3. **Динамические импорты** - для тяжелых компонентов
   ```typescript
   const HeavyComponent = dynamic(() => import('@/components/Heavy'), {
     loading: () => <Skeleton />,
   })
   ```

### SEO

1. Всегда добавляйте `metadata` в pages
2. Используйте структурированные данные (JSON-LD)
3. Настройте правильные canonical URLs
4. Добавьте Open Graph и Twitter Cards

### Accessibility

1. Используйте семантичный HTML
2. Добавляйте ARIA атрибуты где необходимо
3. Обеспечьте клавиатурную навигацию
4. Тестируйте со скринридерами
5. Соблюдайте контрастность цветов (WCAG AAA)

### UX

1. Показывайте loading states (скелетоны)
2. Обрабатывайте ошибки gracefully (ErrorBoundary)
3. Давайте feedback на действия (уведомления, анимации)
4. Валидируйте формы в реальном времени
5. Используйте debounce для поиска

## Структура файлов

```
frontend/
├── lib/
│   ├── utils/
│   │   ├── seo.ts                    # SEO утилиты
│   │   ├── accessibility.tsx         # A11y компоненты и хуки
│   │   └── ...
│   └── hooks/
│       ├── useForm.ts                # Хук для форм
│       └── ...
├── components/
│   ├── ui/
│   │   ├── OptimizedUI.tsx          # Оптимизированные UI компоненты
│   │   └── Skeletons.tsx            # Loading скелетоны
│   └── ErrorBoundary.tsx            # Error boundaries
└── app/
    ├── layout.tsx                    # SkipLinks, RouteAnnouncer
    └── ...
```

## Тестирование

### Производительность
```bash
npm run build
npm run analyze  # Анализ бандла
```

### Accessibility
```bash
npm run lighthouse  # Lighthouse audit
# Или используйте browser DevTools > Lighthouse
```

### Валидация SEO
- Google Search Console
- Rich Results Test
- Open Graph Debugger

## Дальнейшие улучшения

- [ ] Виртуализация больших списков (react-window)
- [ ] Service Worker для offline режима
- [ ] Code splitting по роутам
- [ ] Image optimization (next/image)
- [ ] Prefetching критичных ресурсов
- [ ] Web Vitals мониторинг
- [ ] Интеграция с Sentry для ошибок
- [ ] A/B тестирование компонентов
