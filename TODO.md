# MentorHub — TODO и План Улучшений

**Дата:** 5 апреля 2026 г.
**Ветка:** `dev` → `main`
**Статус:** 🔧 В процессе стабилизации

---

## 📋 Текущие несохранённые изменения (17 файлов)

### CI/CD Workflow (4 файла)
- [x] `.github/workflows/ci-cd.yml` — исправлены ветки `develop` → `dev`
- [x] `.github/workflows/deploy-notifications.yml` — убран дублирующийся `with:` блок
- [x] `.github/workflows/lighthouse.yml` — Node.js 20 → 18 (совместимость)
- [x] `.github/workflows/main.yml` — добавлен PostgreSQL сервис для тестов

### Docker (4 файла)
- [x] `Dockerfile.optimized` — исправлены ENV комментарии
- [x] `Dockerfile.production` — исправлены ENV комментарии
- [x] `docker-compose.prod.yml` — исправлен Dockerfile frontend → `Dockerfile.frontend`
- [x] `docker-compose.yml` — исправлен путь nginx.conf `./nginx.conf` → `./nginx/nginx.conf`

### Frontend API (6 файлов)
- [x] `frontend/hooks/useChat.ts` — WebSocket URL fallback через `NEXT_PUBLIC_API_URL`
- [x] `frontend/lib/api/achievements.ts` — fallback `NEXT_PUBLIC_API_URL`
- [x] `frontend/lib/api/auth.ts` — fallback `NEXT_PUBLIC_API_URL`
- [x] `frontend/lib/api/dashboard.ts` — fallback `NEXT_PUBLIC_API_URL`
- [x] `frontend/lib/api/monitoring.ts` — fallback `NEXT_PUBLIC_API_URL`
- [x] `frontend/lib/api/sessions.ts` — fallback `NEXT_PUBLIC_API_URL`

### Monitoring и Nginx (3 файла)
- [x] `monitoring/prometheus/prometheus.yml` — исправлен postgres exporter target
- [x] `nginx/nginx.conf` — исправлены upstream на Docker сервисы (`frontend:3000`, `backend:8000`)
- [x] `nginx/nginx.conf.template` — обновлён комментарий

---

## 🔴 КРИТИЧЕСКИЕ ПРОБЛЕМЫ (P0)

### 1. Тесты lesson completion — заглушки
- **Файл:** `backend/tests/test_lesson_completion.py`
- **Строки:** 73, 85, 89, 94, 99, 108, 113, 118
- **Проблема:** Все тесты используют `MagicMock`, реальная логика не реализована
- **Влияние:** Нет реальной проверки функционала завершения уроков
- **Решение:** Реализовать полноценные интеграционные тесты с БД

### 2. Мёртвые зависимости в frontend (~18 пакетов) — ✅ ГОТОВО
- **Файл:** `frontend/package.json`
- **Статус:** Удалены все неиспользуемые пакеты: @reduxjs/toolkit, zustand, @tanstack/react-query, swr, react-query, clsx, date-fns, jwt-decode, qrcode.react, react-hook-form, react-hot-toast, tailwind-merge, zod, typescript (перемещён в devDependencies), @sentry/types, @testing-library/dom, critters, ts-node
- **Влияние:** Значительное уменьшение bundle size и времени установки

### 2b. Backend CORS origins — ✅ ГОТОВО
- **Файл:** `backend/app/config.py`
- **Статус:** Удалены `http://localhost:8000` и `http://127.0.0.1:8000` из `_dev_cors_origins` — backend не должен CORS-allow самого себя.

### 3. Три дублирующихся API клиента
- **Файлы:**
  - `frontend/lib/api/client.ts` — `fetchWithRetry`, `apiRequest`
  - `frontend/lib/utils/api.ts` — `fetchAPI`, `api` объект, `WebSocketClient`
  - `frontend/lib/api/auth.ts` — `login`, `register`, `getCurrentUser`
- **Проблема:** Дублирование кода, несогласованность, hardcoded URL
- **Влияние:** Сложность поддержки, потенциальные баги
- **Решение:** Консолидировать в единый configured API client с interceptor'ами

### 4. Hardcoded localhost URLs в production коде — ✅ ЧАСТИЧНО ГОТОВО
- **Статус:** Протестированные файлы исправлены (e2e.py, monitoring.test.ts). TODO.md entries для login/page.tsx:105 и stepik.ts:4 оказались неактуальны — эти файлы уже используют env vars.
- **Оставшиеся:** CI/CD workflow файлы используют hardcoded localhost для CI среды — это приемлемо.

### 5. Фейковый CSRF токен (клиентская генерация)
- **Файл:** `frontend/lib/hooks/useAuth.ts` — `generateCSRFToken()`
- **Проблема:** CSRF токен генерируется на клиенте и хранится в localStorage
- **Влияние:** Не обеспечивает никакой защиты от CSRF атак
- **Решение:** Реализовать server-side CSRF generation + validation

### 6. JWT токены в localStorage (XSS уязвимость)
- **Файл:** `frontend/lib/hooks/useAuth.ts`
- **Проблема:** `access_token` и `refresh_token` хранятся в localStorage
- **Влияние:** Уязвимость к XSS атакам
- **Решение:** Перейти на httpOnly cookies для хранения токенов

### 7. Отсутствует 401 interceptor для автоматического refresh
- **Файлы:** `frontend/lib/api/client.ts`, `frontend/lib/utils/api.ts`
- **Проблема:** При 401 ответе нет автоматического refresh токена
- **Влияние:** Пользователь внезапно разлогинивается
- **Решение:** Добавить interceptor для automatic token refresh on 401

---

## 🟡 ВАЖНЫЕ ПРОБЛЕМЫ (P1)

### Backend P1

### 8. Конфликт версий Python и pytest-asyncio
- **Файлы:** `backend/requirements.txt`, `backend/pyproject.toml`
- **Проблема:** `pytest-asyncio>=0.24.0` vs Python 3.9 (pytest-asyncio 1.x требует Python 3.10+)
- **Влияние:** Потенциальный конфликт при обновлении
- **Решение:** Либо обновить до Python 3.10+, либо зафиксировать `<1.0.0`

### 9. fastapi-cors — устаревший пакет
- **Файл:** `backend/requirements.txt` — `fastapi-cors>=0.0.6`
- **Проблема:** FastAPI имеет встроенный `CORSMiddleware`, пакет устарел
- **Влияние:** Потенциальные конфликты, неподдерживаемый код
- **Решение:** Заменить на `fastapi.middleware.cors.CORSMiddleware`

### 10. Security инструменты в production зависимостях
- **Файл:** `backend/requirements.txt` — `bandit`, `safety`, `pip-audit`
- **Проблема:** CI/CD инструменты в production зависимостях
- **Влияние:** Увеличение Docker образа, поверхность атаки
- **Решение:** Переместить в `requirements-dev.txt`

### 11. Mypy конфигурация — ослабленная типизация
- **Файл:** `backend/pyproject.toml`
- **Проблемы:**
  - `disallow_untyped_defs = false`
  - `ignore_missing_imports = true`
- **Влияние:** Снижение безопасности типов
- **Решение:** Включить `true` + добавить `types-*` stub пакеты

### 12. DeprecationWarning полностью игнорируется
- **Файл:** `backend/pyproject.toml` — `filterwarnings = ["ignore::DeprecationWarning"]`
- **Проблема:** Маскировка устаревших API
- **Влияние:** Пропуск важных предупреждений
- **Решение:** Изменить на `default::DeprecationWarning`

### Frontend P1

### 13. i18n middleware отключен
- **Файлы:** `frontend/middleware.ts` (закомментировано), `frontend/i18n.ts`
- **Проблема:** 4 языковых файла загружены, но роутинг не работает
- **Влияние:** Мёртвый код, путаница
- **Решение:** Либо включить i18n routing, либо удалить языковые файлы

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

### 19. ESLint отключен при сборке
- **Файл:** `frontend/next.config.js` — `eslint: { ignoreDuringBuilds: true }`
- **Проблема:** Ошибки линтинга не блокируют сборку
- **Влияние:** Возможны проблемы качества в production
- **Решение:** Включить ESLint checks, исправить все ошибки

### 20. Дублирующийся ключ `optimizePackageImports` в next.config.js — ✅ НЕ ПОДТВЕРЖДЕНО
- **Файл:** `frontend/next.config.js`
- **Статус:** При проверке дублирующийся ключ не найден — возможно, уже исправлено или entry неактуален.

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

### Фаза 1: Стабилизация (текущая)
1. ✅ Исправить все несохранённые изменения (17 файлов) — **ГОТОВО**
2. ⏳ Закоммитить изменения в `dev`
3. ⏳ Проверить что CI/CD проходит
4. ⏳ Слить `dev` → `main`
5. ⏳ Отправить на удалённый репозиторий

### Фаза 2: Критические исправления (следующая)
1. ✅ Удалить мёртвые зависимости из frontend/package.json — **ГОТОВО**
2. ✅ Исправить hardcoded localhost URLs в тестах — **ГОТОВО**
3. ✅ Исправить backend CORS origins — **ГОТОВО**
4. ⏳ Консолидировать API клиенты
5. ⏳ Добавить 401 interceptor для token refresh

### Фаза 3: Качество кода
1. Включить ESLint в сборке
2. Исправить все lint ошибки
3. Увеличить покрытие тестами критичных компонентов
4. Включить строгую типизацию mypy

---

## 📊 МЕТРИКИ ПРОЕКТА

### Backend
- **Файлов Python:** ~100+
- **Endpoints:** ~80+
- **Моделей:** ~15+
- **Тестов:** ~200+ (с заглушками)
- **Python версия:** 3.11
- **Фреймворк:** FastAPI

### Frontend
- **Файлов TypeScript:** ~150+
- **Компонентов:** ~120+ (49 без тестов)
- **Страниц:** ~58 (0% покрытие)
- **Утилит:** 11 (без тестов)
- **Тестов:** ~74 passing, 12 skipped
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
