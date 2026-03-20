# Lighthouse Performance Guide

## Обзор

MentorHub использует **Lighthouse CI** для автоматического аудита производительности, доступности, best practices и SEO.

## Целевые метрики

| Категория | Цель | Минимум |
|-----------|------|---------|
| Performance | >90 | >80 |
| Accessibility | >90 | >90 |
| Best Practices | >90 | >80 |
| SEO | >90 | >80 |

### Core Web Vitals

| Метрика | Цель | Допустимо |
|---------|------|-----------|
| First Contentful Paint (FCP) | <1.5s | <2.5s |
| Largest Contentful Paint (LCP) | <2.5s | <4.0s |
| Cumulative Layout Shift (CLS) | <0.1 | <0.25 |
| Total Blocking Time (TBT) | <300ms | <600ms |

## Запуск аудита

### Локально

```bash
cd frontend

# Установка зависимостей
npm install

# Сборка и экспорт
npm run build
npm run export

# Запуск Lighthouse CI
npm run lighthouse
```

### В CI/CD

Lighthouse запускается автоматически при:
- Push в `main` или `dev`
- Pull Request в `main`
- Еженедельно по понедельникам в 6:00 UTC

Результаты загружаются как GitHub artifacts.

## Конфигурация

### .lighthouserc.json

```json
{
  "ci": {
    "collect": {
      "staticDistDir": "./out",
      "url": [
        "http://localhost/ru/index.html",
        "http://localhost/ru/mentors/index.html",
        "http://localhost/ru/courses/index.html",
        "http://localhost/ru/sessions/index.html"
      ],
      "settings": {
        "onlyCategories": ["performance", "accessibility", "best-practices", "seo"],
        "preset": "desktop"
      }
    },
    "assert": {
      "assertions": {
        "categories:performance": ["warn", {"minScore": 0.9}],
        "categories:accessibility": ["error", {"minScore": 0.9}],
        "first-contentful-paint": ["warn", {"maxNumericValue": 1500}],
        "largest-contentful-paint": ["warn", {"maxNumericValue": 2500}],
        "cumulative-layout-shift": ["warn", {"maxNumericValue": 0.1}]
      }
    }
  }
}
```

## Оптимизации производительности

### Изображения

✅ **Использует Next.js Image:**
```tsx
import Image from 'next/image'

<Image
  src="/avatar.jpg"
  alt="User avatar"
  width={100}
  height={100}
  priority  // Для LCP элементов
  sizes="(max-width: 768px) 50vw, 100vw"
  quality={85}
/>
```

✅ **Форматы:** WebP + AVIF (автоматическая конвертация)

✅ **Lazy loading:** Для изображений ниже fold

### Code Splitting

✅ **Автоматическое разделение:**
- `commons.js` - общие модули
- `lib.js` - node_modules
- `react.js` - React + ReactDOM
- `next.js` - Next.js core
- `lucide.js` - иконки

✅ **Dynamic imports:**
```tsx
import dynamic from 'next/dynamic'

const HeavyComponent = dynamic(() => import('./HeavyComponent'), {
  loading: () => <LoadingSpinner />,
  ssr: false  // Если не нужен SSR
})
```

### CSS оптимизации

✅ **CSS минимизация:** `optimizeCss: true`

✅ **Critical CSS:** Автоматическая инлайн-вставка

✅ **Tailwind PurgeCSS:** Удаление неиспользуемых стилей

### Шрифты

✅ **font-display: swap:** Для всех шрифтов

✅ **Preload:** Для критических шрифтов

```tsx
<link
  rel="preload"
  href="/fonts/inter-var.woff2"
  as="font"
  type="font/woff2"
  crossOrigin="anonymous"
/>
```

### Кэширование

✅ **HTTP кэш заголовки:**
```
Cache-Control: public, max-age=31536000, immutable
```

✅ **ETag:** Включено в next.config.js

✅ **Stale-while-revalidate:** Для API запросов

## Security Headers

Для Lighthouse Best Practices добавлены заголовки:

```javascript
headers: async () => [
  {
    source: '/:path*',
    headers: [
      { key: 'Strict-Transport-Security', value: 'max-age=63072000; includeSubDomains; preload' },
      { key: 'X-Frame-Options', value: 'SAMEORIGIN' },
      { key: 'X-Content-Type-Options', value: 'nosniff' },
      { key: 'X-XSS-Protection', value: '1; mode=block' },
      { key: 'Referrer-Policy', value: 'origin-when-cross-origin' },
    ],
  },
]
```

## Доступность (Accessibility)

### Чеклист

- ✅ Alt text для всех изображений
- ✅ ARIA labels для интерактивных элементов
- ✅ Keyboard navigation (Tab, Enter, Escape)
- ✅ Focus indicators
- ✅ Color contrast >4.5:1
- ✅ Form labels для всех input
- ✅ Error messages с aria-describedby

### Тестирование

```bash
# Axe DevTools в браузере
# Lighthouse Accessibility аудит
npm run lighthouse
```

## SEO

### Мета-теги

```tsx
<Head>
  <title>MentorHub - Платформа для менторства</title>
  <meta name="description" content="Найдите ментора для развития в IT" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <link rel="canonical" href="https://mentorhub.app/ru" />
  
  {/* Open Graph */}
  <meta property="og:title" content="MentorHub" />
  <meta property="og:description" content="Платформа для менторства" />
  <meta property="og:image" content="/og-image.png" />
  
  {/* Twitter Card */}
  <meta name="twitter:card" content="summary_large_image" />
</Head>
```

### Sitemap

Автоматическая генерация:
- `/sitemap.xml`
- `/ru/sitemap.xml`
- `/en/sitemap.xml`

### Robots.txt

```
User-agent: *
Allow: /
Sitemap: https://mentorhub.app/sitemap.xml
```

## Мониторинг

### GitHub Actions

Результаты каждого запуска сохраняются в artifacts:
- HTML отчёты
- JSON данные
- Скриншоты

### Тренды

Следите за метриками в `main` ветке:
- Performance score
- FCP, LCP, CLS, TBT
- Bundle size

## Troubleshooting

### Низкий Performance score

**Проблемы:**
1. Большой bundle size
2. Медленный LCP
3. Высокий CLS

**Решения:**
```bash
# Анализ bundle size
npm run analyze

# Проверка изображений
# Используйте Image компонент с proper sizes

# Проверка шрифтов
# Добавьте font-display: swap
```

### Проблемы с доступностью

**Частые ошибки:**
1. Missing alt attributes
2. Missing form labels
3. Low color contrast

**Решение:**
- Запустите Lighthouse аудит
- Исправьте ошибки по очереди
- Протестируйте с keyboard navigation

### SEO проблемы

**Проверьте:**
1. Meta title/description
2. Canonical URLs
3. Structured data (JSON-LD)
4. Mobile-friendly тест

## Ссылки

- [Lighthouse Documentation](https://developer.chrome.com/docs/lighthouse/overview/)
- [Web Vitals](https://web.dev/vitals/)
- [Next.js Performance](https://nextjs.org/docs/advanced-features/measuring-performance)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
