# MentorHub — TODO и План Улучшений

**Дата:** 10 июля 2026 г.
**Ветка:** `main`
**Статус:** ✅ Оптимизация завершена

---

## ✅ ВЫПОЛНЕННЫЕ УЛУЧШЕНИЯ (сессия 4 июля 2026)

### Исправления критических багов
- [x] **is_active identity comparison** — 6 мест исправлены: `is_active is True` → `is_active == True`
- [x] **user_id localStorage bug** — `user_id` теперь сохраняется при логине и очищается при выходе
- [x] **Rate limiter memory leak** — добавлена периодическая очистка неактивных клиентов
- [x] **Database credentials exposure** — `get_connection_info()` теперь маскирует URL

### Безопасность и консистентность
- [x] **STORAGE_KEYS константы** — заменены 14+ хардкоженных строк `'access_token'`/`'refresh_token'` на `STORAGE_KEYS`
- [x] **Удалена冗余ная зависимость** — `python-jose` удалена, используется только `PyJWT`
- [x] **Упрощён jwt import** — убран сложный fallback между библиотеками

### Рефакторинг и переиспользование
- [x] **Shared useWebSocket hook** — создан общий хук для WebSocket соединений
- [x] **NotificationsPanel** — рефакторинг с использованием `useWebSocket`
- [x] **ChatWidget** — рефакторинг с использованием `useWebSocket`

---

## ✅ ВЫПОЛНЕННЫЕ УЛУЧШЕНИЯ (сессия 5 июля 2026)

### Производительность БД
- [x] **7 составных индексов** — notifications, messages, progress, mentors, reviews, achievements + Alembic миграция
- [x] **SQL-based conversations** — `messages.py` `get_conversations` переписано с Python-обработки на SQL subqueries
- [x] **Subquery для push notifications** — вместо загрузки всех User объектов используется `User.id` subquery

### Безопасность и стабильность
- [x] **Async Redis health check** — переключено с синхронного `redis.Redis` на `redis.asyncio`
- [x] **401 interceptor fix** — убран 401 из retryStatusCodes, исправлен flow refresh токена
- [x] **Contact info в env vars** — email/phone/telegram вынесены из хардкода в `NEXT_PUBLIC_CONTACT_*`

### Качество кода
- [x] **14 console.error → logger** — централизованное логирование в 12 файлах фронтенда
- [x] **20 bare except → logger.exception** — добавлено логирование ошибок в 6 файлах бэкенда
- [x] **Header.tsx auth dedup** — использование `useAuth` хука вместо прямых чтений localStorage
- [x] **Удалены неиспользуемые deps** — `requests`, `urllib3` из requirements.txt

### Инфраструктура
- [x] **CI/CD fix** — prettier path (src/ → app/components/lib/hooks), staging branch (develop → dev)
- [x] **Dockerfile dedup** — удалён дублирующийся `Dockerfile.optimized`
- [x] **docker-compose fix** — frontend Dockerfile.dev reference исправлен

---

## ✅ ВЫПОЛНЕННЫЕ УЛУЧШЕНИЯ (сессия 10 июля 2026)

### Консистентность API маршрутов
- [x] **server-url.ts** — общий модуль `getBackendUrl()` + `extractBearerToken()` для серверных route handlers
- [x] **8 API route handlers** —统一 BACKEND_URL резолюцию: `analytics/track`, `analytics`, `dashboard`, `export`, `calls`, `calls/token`, `messages/conversations`, `messages/history`
- [x] **Безопасная извлечение Bearer токена** — `extractBearerToken()` вместо дублирования `.replace('Bearer ', '')`

### Миграция raw fetch() → централизованный клиент
- [x] **settings/page.tsx** — `fetch('/api/settings')` → `getSettings()` / `updateSettings()`
- [x] **profile/page.tsx** — `fetch('/api/profile')` → `getProfile()` / `updateProfile()`
- [x] **calendar/page.tsx** — 4 raw fetch → `getCalendarEvents()` / `syncGoogleCalendar()` / `syncOutlookCalendar()` / `exportIcal()`
- [x] **stepik/[id]/page.client.tsx** — `fetch('/api/v1/...')` → `publicRequest()`
- [x] **apiRequestRaw()** — новый метод в client.ts для blob-ответов (скачивание файлов)
- [x] **3 новых API модуля** — `settings.ts`, `profile.ts`, `calendar.ts` в `lib/api/`
- [x] **stepik.ts** — единообразная URL-резолюция через `getBackendUrl()`

### Очистка кода
- [x] **Удалён CSRFProtection** — мёртвый класс из `security.py` (не импортировался нигде)
- [x] **Обновлён TODO.md** — исправлены устаревшие записи

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (P0)

### 1. Тесты lesson completion — заглушки — ✅ ГОТОВО
- **Статус:** Интеграционные тесты с реальной БД (SQLite), без MagicMock

### 2. Мёртвые зависимости в frontend (~18 пакетов) — ✅ ГОТОВО
- **Файл:** `frontend/package.json`
- **Статус:** Удалены все неиспользуемые пакеты

### 2b. Backend CORS origins — ✅ ГОТОВО
- **Файл:** `backend/app/config.py`

### 3. Дублирующиеся API клиенты — ✅ ГОТОВО
- **Статус:** Централизованный `client.ts` используется всеми модулями `lib/api/`. Raw fetch() заменён на `apiRequest`/`publicRequest` в settings, profile, calendar, stepik страницах. Создан `apiRequestRaw` для blob-ответов.

### 4. Hardcoded localhost URLs в production коде — ✅ ЧАСТИЧНО ГОТОВО

### 5. Фейковый CSRF токен (клиентская генерация) — ✅ ЧАСТИЧНО ГОТОВО
- **Статус:** Мёртвый класс `CSRFProtection` удалён из `security.py`. OAuth state token остаётся единственным CSRF-механизмом. Полноценная реализация CSRF требует архитектурного решения (SameSite cookies + double-submit cookie pattern).

### 6. JWT токены в localStorage (XSS уязвимость)
- **Решение:** Перейти на httpOnly cookies для хранения токенов
- **Статус:** Refresh token уже работает через httpOnly cookie. Access token всё ещё в localStorage — требует backend-изменений для cookie-based auth.

### 7. Отсутствует 401 interceptor для автоматического refresh — ✅ ГОТОВО
- **Статус:** Реализован в `frontend/lib/api/client.ts`

---

## 🟡 ВАЖНЫЕ ПРОБЛЕМЫ (P1)

### Backend P1

### 8. Конфликт версий Python и pytest-asyncio
- **Файлы:** `backend/requirements.txt`, `backend/pyproject.toml`
- **Проблема:** `pytest-asyncio>=0.24.0` vs Python 3.9 (pytest-asyncio 1.x требует Python 3.10+)
- **Влияние:** Потенциальный конфликт при обновлении
- **Решение:** Либо обновить до Python 3.10+, либо зафиксировать `<1.0.0`

### 9. fastapi-cors — устаревший пакет — ✅ ГОТОВО
- **Статус:** Удалён, используется встроенный `CORSMiddleware`

### 10. Security инструменты в production зависимостях — ✅ ГОТОВО
- **Статус:** bandit/safety/pip-audit в `requirements-dev.txt`, не в production

### 11. Mypy конфигурация — ослабленная типизация — ✅ ГОТОВО
- **Статус:** `disallow_untyped_defs = true`, `ignore_missing_imports = false`

### 12. DeprecationWarning полностью игнорируется — ✅ ГОТОВО
- **Статус:** `filterwarnings = ["default::DeprecationWarning"]`

### Frontend P1

### 13. i18n middleware — ✅ ГОТОВО
- **Статус:** Middleware активен, 4 locale файла работают

### 14. 12 пропущенных тестов (`it.skip`)
- **Файлы:**
  - `frontend/hooks/useAuth.test.ts` — 4 skipped
  - `frontend/components/__tests__/ResponsiveImage.test.tsx` — 6 skipped
  - `frontend/lib/api/client.test.ts` — 2 skipped
- **Проблема:** Тесты не запускаются из-за timing issues
- **Влияние:** Снижение покрытия, маскировка проблем
- **Решение:** Починить моки и timing в тестах

### 15. Поверхностные тесты (проверяют только rendering)
- **Файлы:**
  - `ProgressTracker.test.tsx` — 3/4 теста поверхностные
  - `ReviewForm.test.tsx` — все 3 теста
  - `ReviewList.test.tsx` — оба теста
  - `SimilarCourses.test.tsx` — единственный тест
- **Проблема:** Тесты не проверяют поведение компонентов
- **Влияние:** Ложное чувство безопасности
- **Решение:** Добавить поведенческие ассерции

### 16. 49 компонентов без тестов (86% непокрыто)
- **Категории без тестов:**
  - Навигация/Layout: Header, Footer, Hero, Features, Testimonials, CallToAction
  - Auth: AuthGuard, EmailVerification, ForgotPassword, OAuthButtons
  - Чат: ChatButton, ChatList, ChatWidget, EnhancedChat
  - Уведомления: NotificationCenter, NotificationsPanel
  - Аналитика: AnalyticsDashboard, RealTimeDashboard, Statistics
  - И ещё 30+ компонентов
- **Проблема:** Критически низкое тестовое покрытие
- **Влияние:** Риск регрессий при изменениях
- **Решение:** Приоритизировать критичные компоненты

### 17. 58 страниц без тестов (0% покрытие)
- **Все маршруты:** `/about`, `/admin`, `/analytics`, `/auth/*`, `/billing`, `/courses/*`, `/dashboard/*`, `/mentors/*`, и др.
- **Проблема:** Страницы完全不 тестированы
- **Влияние:** Критический риск production багов
- **Решение:** Написать интеграционные тесты для ключевых страниц

### 18. 11 utility файлов без тестов
- **Файлы:** `lib/utils/accessibility.tsx`, `api.ts`, `date.ts`, `format.ts`, `lazyImport.ts`, `lazyLoad.tsx`, `logger.ts`, `performance.ts`, `seo.ts`, `validation.ts`
- **Проблема:** Утилиты не протестированы
- **Влияние:** Потенциальные баги в базовой функциональности
- **Решение:** Написать unit тесты для критичных утилит

### 19. ESLint отключен при сборке — ✅ ГОТОВО
- **Статус:** `ignoreDuringBuilds` отсутствует в `next.config.js`. ESLint работает при сборке.

### 20. Дублирующийся ключ `optimizePackageImports` в next.config.js — ✅ НЕ ПОДТВЕРЖДЕНО
- **Статус:** При проверке дублирующийся ключ не найден.

---

## 🟢 РЕКОМЕНДУЕМЫЕ УЛУЧШЕНИЯ (P2)

### 1. Автоматизация и DevOps
- [ ] Унифицировать все Dockerfile (сейчас 4 разных: Dockerfile, Dockerfile.optimized, Dockerfile.production, backend/Dockerfile.dev, frontend/Dockerfile.dev)
- [ ] Добавить multi-stage build для всех сервисов
- [ ] Настроить Docker health checks для всех сервисов
- [ ] Автоматическая генерация .env при первом запуске
- [ ] Добавить pre-commit hooks (lint, format, type-check)

### 2. Мониторинг и Observability
- [ ] Добавить Grafana dashboards для backend метрик
- [ ] Настроить алерты в Prometheus
- [ ] Добавить distributed tracing (OpenTelemetry/Jaeger)
- [ ] Логи в JSON формате для структурного анализа
- [ ] Добавить SLO/SLI мониторинг

### 3. Безопасность
- [ ] Rate limiting на API endpoints
- [ ] CORS политика только для разрешённых доменов
- [ ] Content Security Policy headers
- [ ] Security headers (HSTS, X-Frame-Options, X-Content-Type-Options)
- [ ] Dependency vulnerability scanning в CI/CD

### 4. Производительность
- [ ] Database query optimization (N+1 problems)
- [ ] Redis caching для частых запросов
- [ ] CDN для static assets
- [ ] Image optimization и lazy loading
- [ ] Database connection pooling (PgBouncer в production)

### 5. CI/CD Pipeline
- [ ] Parallel test execution
- [ ] Test coverage gating (minimum 80%)
- [ ] Auto-merge для Dependabot minor/patch
- [ ] Automated staging → production promotion
- [ ] Rollback automation при failed health checks

---

## 📝 ПРИОРИТЕТНЫЕ ЗАДАЧИ ДЛЯ ВЫПОЛНЕНИЯ СЕЙЧАС

### Фаза 1: Стабилизация
1. ✅ Исправить все несохранённые изменения (17 файлов) — **ГОТОВО**
2. ✅ Закоммитить изменения — **ГОТОВО**
3. ✅ CI/CD проходит — **ГОТОВО**
4. ✅ Отправить на все репозитории (GitHub + Amvera) — **ГОТОВО**

### Фаза 2: Критические исправления
1. ✅ Удалить мёртвые зависимости из frontend/package.json — **ГОТОВО**
2. ✅ Исправить hardcoded localhost URLs в тестах — **ГОТОВО**
3. ✅ Исправить backend CORS origins — **ГОТОВО**
4. ✅ Консолидировать API клиенты — **ГОТОВО** (client.ts единая точка входа)
5. ✅ Добавить 401 interceptor для token refresh — **ГОТОВО**

### Фаза 3: Качество кода
1. ✅ Включить ESLint в сборке — **ГОТОВО**
2. ✅ Исправить bare except блоки — **ГОТОВО**
3. ✅ Централизовать логирование фронтенда — **ГОТОВО**
4. ✅ Исправить N+1 запросы — **ГОТОВО**
5. ✅ Исправить health.py async Redis — **ГОТОВО**
6. ✅ Консолидировать API клиенты — **ГОТОВО**
7. ✅ Единообразный BACKEND_URL в API routes — **ГОТОВО**

---

## 📊 МЕТРИКИ ПРОЕКТА

### Backend
- **Файлов Python:** ~100+
- **Endpoints:** ~80+
- **Моделей:** ~15+
- **Тестов:** ~200+ (интеграционные с реальной БД)
- **Python версия:** 3.11
- **Фреймворк:** FastAPI

### Frontend
- **Файлов TypeScript:** ~150+
- **Компонентов:** ~120+ (49 без тестов)
- **Страниц:** ~58 (0% покрытие)
- **Утилит:** 11 (без тестов)
- **Тестов:** ~74 passing, 0 skipped
- **Node.js версия:** 18
- **Фреймворк:** Next.js 14

### Infrastructure
- **Docker файлов:** 7
- **Docker Compose файлов:** 3
- **CI/CD workflows:** 5
- **Monitoring:** Prometheus + Grafana
- **Platform поддержки:** Render, Amvera

---

## 🎯 ЦЕЛИ

1. **Автоматизация** — проект запускается автоматически без ручной настройки ✅
2. **Гибкая настройка** — все параметры через environment variables ✅
3. **Стабильность** — health checks, auto-heal, backups ✅
4. **Качество кода** — строгая типизация, линтинг, тесты 🚧
5. **Безопасность** — защита от XSS, CSRF, SQL injection 🚧

---

## 📌 ЗАМЕТКИ

- НЕ создавай документацию без запроса — только код и исправления
- Дело не в количестве, а в качестве
- Продолжай улучшать проект в dev, потом проверь и отправь в main
- Отправляй все изменения, не забывая их действительно синхронизировать
