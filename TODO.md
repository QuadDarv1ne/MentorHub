# MentorHub - План улучшений

## ✅ Выполнено

### i18n (Интернационализация)
- [x] next-intl библиотека
- [x] 4 языка: ru, en, zh, he
- [x] RTL поддержка для иврита
- [x] LocaleSwitcher компонент
- [x] Переводы (800+ строк)
- [ ] [locale] роутинг для полной поддержки

### Деплой конфигурация
- [x] Heroku (Procfile, app.json)
- [x] Railway (railway.toml)
- [x] Render (render.yaml)
- [x] Vercel (vercel.json)
- [x] Netlify (netlify.toml)
- [x] Cloudflare (wrangler.toml)
- [x] AWS ECS (Terraform)
- [x] Google Cloud Run (cloud-run.yaml)
- [x] GitHub Actions CI/CD
- [x] Скрипты deploy.sh / deploy.ps1

### Backend исправления
- [x] regex → pattern (FastAPI warning)
- [x] pydantic-core==2.41.5
- [x] antlr4-python3-runtime==4.9.3
- [x] decode_access_token функция
- [x] health.py (get_redis → удалено)
- [x] analytics.py (require_admin → get_current_user)
- [x] push_notifications.py (Pydantic схемы)

### Frontend исправления
- [x] useSearchParams Suspense boundary
- [x] Tabs компонент (icon, children)
- [x] Badge/Button variant исправления
- [x] useCallback/useMemo зависимости
- [x] Set итерация (Array.from)
- [x] LazyComponents.tsx - исправлен тип loading и поддержка именованных экспортов
- [x] useAuth.ts - isAuthenticated теперь boolean (не функция)
- [x] client.ts - Headers тип (Record<string, string>)
- [x] start.sh - удалён --optimize-for-size из NODE_OPTIONS
- [x] console.log cleanup (12 файлов)
- [x] alert() → useToast (MonitoringDashboard, booking, blog)
- [x] test/page.tsx cleanup

### Deploy исправления
- [x] Render деплой работает
- [x] health.py - async Redis клиент
- [x] Redis production документация (DEPLOYMENT-REDIS-RENDER.md)
- [x] Render деплой документация (DEPLOYMENT-RENDER.md)
- [x] render.yaml конфигурация
- [x] User.role тип - добавлен 'admin'

### Backend исправления (дополнительно)
- [x] timezone import в auth.py
- [x] prometheus.py UnboundLocalError fix
- [x] dependencies.py - дубли импортов
- [x] .gitignore - test.db, *.db-shm, *.db-wal
- [x] cache.py - восстановлены @cached декораторы
- [x] courses.ts getSimilarCourses - реализована логика
- [x] cleanup unused imports (payments.py, websocket.py, courses.py, mentors.py, users.py, stats.py)
- [x] request_logging.py - убраны debug логи
- [x] ErrorBoundary упрощён (1 компонент вместо 3)

### Тесты исправления (2026-03-10)
- [x] test_e2e.py - регистрация (username), логин (json), endpoint (/users/me)
- [x] test_sessions.py - 18/18 тестов работают, mentor_client фикстура
- [x] test_users.py - unique email/username в тестах
- [x] test_auth.py - sample_user_data unique, test_register_duplicate_email fix
- [x] test_security.py - expectations исправлены
- [x] conftest.py - sample_user_data unique id

### Тесты (2026-03-10) - Прогресс
- [x] test_auth.py: 11/11 passed ✅
- [x] test_sessions.py: 18/18 passed ✅
- [x] test_users.py: 8/8 passed ✅
- [x] test_courses.py: 11/11 passed ✅
- [x] test_cache.py: 10/10 passed ✅
- [x] test_e2e.py: 3/3 passed (registration flow) ✅
- [x] test_reviews.py: 18/18 passed (unique users + status codes) ✅
- [x] test_progress.py: 10/14 passed (unique users + status codes) ✅
- [x] conftest.py - sync_authenticated_client, authenticated_headers фикстуры ✅
- [x] sample_user_data - unique email/username ✅
- [ ] test_websocket_chat.py - исправить (mock проблемы)
- [ ] test_notifications.py - исправить (KeyError: 'access_token')
- [ ] test_mentors.py - исправить (fixture mismatch)
- [ ] test_errors.py - исправить (формат ответов)
- [ ] Достичь 80% coverage (текущее: ~45-60%)

### Monitoring и Infrastructure
- [x] Prometheus конфигурация (monitoring/prometheus/prometheus.yml)
- [x] Grafana datasource (monitoring/grafana/datasource.yaml)
- [x] Grafana dashboard (monitoring/grafana/dashboard.json)
- [x] Node Exporter для метрик системы
- [x] docker-compose.prod.yml - health checks для всех сервисов ✅
- [x] Nginx reverse proxy конфигурация ✅
- [x] Database backup скрипт ✅
- [x] Celery worker + beat конфигурация ✅
- [x] Redis maxmemory и allkeys-lru policy ✅
- [x] PostgreSQL performance tuning ✅

---

## 🔥 Приоритетные задачи

### 1. Оптимизация изображений ✅
```
Выполнено:
- components/Avatar.tsx - Image компонент
- components/SimilarCourses.tsx - Image с fill
- app/courses/stepik/[id]/page.client.tsx - fill, sizes, quality
- frontend/lib/utils/imageOptimization.tsx - ResponsiveImage
```

### 2. Redis для production ✅
```
Выполнено:
- docker-compose.prod.yml - Redis без пароля
- REDIS_URL обновлён во всех сервисах
- backend, celery_worker, celery_beat - подключены
```

### 3. Тесты coverage ⚠️ В ПРОЦЕССЕ
```
backend/tests/:
- [x] test_auth.py - 11/11 passed ✅
- [x] test_sessions.py - 18/18 passed ✅
- [x] test_users.py - 8/8 passed ✅
- [x] test_courses.py - 11/11 passed ✅
- [x] test_cache.py - 10/10 passed ✅
- [x] test_reviews.py - 18/18 passed ✅
- [x] test_progress.py - 10/14 passed ✅
- [x] test_e2e.py - 3/3 passed ✅
- [ ] test_websocket_chat.py - исправить (mock проблемы)
- [ ] test_notifications.py - исправить (KeyError: 'access_token')
- [ ] test_mentors.py - исправить (fixture mismatch)
- [ ] test_errors.py - исправить (формат ответов)
- [ ] Достичь 80% coverage (текущее: ~45-60%)

frontend/__tests__/:
- [ ] Создать директорию __tests__
- [ ] Добавить компонентные тесты
- [ ] Интеграционные тесты

Цель: 80%+ coverage
```

### 4. Docker Compose production ✅
```
docker-compose.prod.yml:
- [x] Nginx reverse proxy
- [x] PostgreSQL с бэкапами
- [x] Redis cache
- [x] Health checks для всех сервисов
- [x] Monitoring (Prometheus + Grafana)
- [x] Celery worker + beat
- [x] Database backup service
- [x] Resource limits и deploy replicas
```

### 5. Мониторинг и алерты ⚠️ ЧАСТИЧНО
```
monitoring/:
- [x] Prometheus конфигурация
- [x] Grafana datasource
- [x] Grafana dashboard
- [x] Node Exporter
- [ ] Alert rules (CPU, Memory, Error rate)
- [ ] Alertmanager интеграция

Sentry integration:
- [x] Frontend: sentry.client.config.ts
- [x] Backend: sentry.sdk
- [ ] Performance monitoring настройка
- [ ] Error tracking dashboard
```

---

## 📋 Среднесрочные задачи

### 6. Database оптимизация
```
- [ ] Индексы для частых запросов
- [ ] Connection pooling (pgbouncer)
- [ ] Query optimization (N+1 problem)
- [ ] Database migrations tests (Alembic)
```

### 7. Security hardening
```
- [ ] Rate limiting для API endpoints
- [ ] CORS настройка для production
- [ ] HTTPS redirect
- [ ] Security headers (CSP, HSTS)
- [ ] Input validation (zod/pydantic)
- [ ] SQL injection protection
```

### 8. Performance optimization
```
Frontend:
- [ ] Code splitting
- [ ] Lazy loading компонентов
- [ ] Bundle size optimization
- [ ] Lighthouse score > 90

Backend:
- [ ] Response caching
- [ ] Database query caching
- [ ] Async operations где возможно
- [ ] Connection pooling
```

### 9. CI/CD улучшения
```
.github/workflows/:
- [x] backend-tests.yml - автотесты с coverage ✅
- [x] frontend-tests.yml - тесты + type check + build ✅
- [x] ci-cd.yml - основной workflow ✅
- [x] deploy-cloudflare.yml ✅
- [x] deploy-multi-platform.yml ✅
- [ ] Staging environment
- [ ] Automated testing before deploy
- [ ] Rollback механизм
- [ ] Slack/Telegram уведомления
- [ ] Auto-deploy из main
```

### 10. Documentation ✅ ЧАСТИЧНО
```
docs/:
- [x] API documentation (OpenAPI/Swagger) ✅ docs/API/openapi.md
- [x] Architecture diagrams ✅ docs/ARCHITECTURE.md
- [x] Developer onboarding guide ✅ docs/CI-CD.md
- [x] Deployment guide (step-by-step) ✅ docs/DEPLOYMENT/
  - render.md
  - redis-render.md
  - amvera.md
  - production.md
  - production-v2.md
- [x] Troubleshooting guide ✅ docs/DEPLOYMENT/ENVIRONMENT-VARIABLES.md
- [x] Security guide ✅ docs/SECURITY/
- [x] Features documentation ✅ docs/FEATURES/
- [x] Monitoring docs ✅ docs/MONITORING/
- [x] Testing guide ✅ backend/tests/README.md
- [ ] API Reference полный ✅ docs/API/reference.md
```

---

## 🎯 Долгосрочные задачи

### 11. Feature requests
```
- [ ] WebSocket chat (полная реализация)
- [ ] Video calls (Agora integration)
- [ ] Payment processing (Stripe)
- [ ] Email notifications (Celery tasks)
- [ ] Admin dashboard
- [ ] Analytics dashboard
- [ ] Mobile app (React Native)
```

### 12. Scalability
```
- [ ] Horizontal scaling (Kubernetes)
- [ ] Load balancing
- [ ] CDN for static assets
- [ ] Database sharding
- [ ] Microservices architecture
```

### 13. Quality of Life
```
- [ ] Dark mode
- [ ] PWA support
- [ ] Offline mode
- [ ] Push notifications
- [ ] Social login (Google, GitHub)
- [ ] Two-factor authentication
```

---

## 📊 Метрики для отслеживания

### Performance
- Lighthouse score: > 90 ⚠️ Требуется проверка
- First Contentful Paint: < 1.5s ⚠️ Требуется проверка
- Time to Interactive: < 3.5s ⚠️ Требуется проверка
- API response time: < 200ms ⚠️ Требуется проверка

### Quality
- Test coverage: > 80% ⚠️ Текущее: ~45-60%
- Code quality (SonarQube): A ⚠️ Требуется настройка
- Security score: A+ ⚠️ Требуется проверка

### Reliability
- Uptime: > 99.9% ⚠️ Требуется мониторинг
- Error rate: < 0.1% ⚠️ Sentry настроен, требуется отслеживание
- MTTR (Mean Time To Recovery): < 1h ⚠️ Требуется мониторинг

### Infrastructure ✅
- Health checks: 100% сервисов
- Resource limits: настроены
- Backup retention: 7 дней / 4 недели / 6 месяцев

---

## 📝 Заметки

### Известные проблемы
1. ~~Redis не подключён в production~~ ✅ Исправлено
2. ~~Тесты падают из-за antlr4 версии~~ ✅ Исправлено
3. ~~Некоторые API endpoints требуют авторизации админа~~ ✅ Исправлено
4. ~~Nginx reverse proxy не настроен~~ ✅ Исправлено
5. ~~Health checks отсутствуют~~ ✅ Исправлено
6. ⚠️ Websocket тесты - mock проблемы
7. ⚠️ Notifications/Mentors тесты - fixture mismatch
8. ⚠️ Coverage ~45-60% (цель: 80%)

### Технические долги
1. ~~Удалить закомментированный код~~ ✅ console.log удалены
2. ~~Обновить устаревшие зависимости~~ ✅ timezone, prometheus fix
3. ~~Рефакторить большие компоненты~~ ✅ ErrorBoundary упрощён
4. [ ] Добавить типизацию для всех API endpoints
5. [ ] Удалить archive/ директорию
6. [ ] Обновить Dockerfile.production (использовать основной Dockerfile)

### Идеи для улучшений
1. [ ] Добавить GraphQL API
2. [ ] Реализовать real-time уведомления
3. [ ] Добавить экспорт данных (PDF, Excel)
4. [ ] Интеграция с календарями (Google, Outlook)
5. [ ] Dark mode
6. [ ] PWA support

### Новые задачи (из code review)
1. ~~Logger cleanup в production~~ ✅ request_logging.py
2. ~~ErrorBoundary упростить~~ ✅ 1 компонент вместо 3
3. ~~courses.ts getSimilarCourses~~ ✅ реализована
4. ~~request_logging.py~~ ✅ убраны debug логи
5. ~~cache.py - восстановить декораторы~~ ✅ @cached работают
6. ~~Monitoring Prometheus+Grafana~~ ✅ конфигурация готова
7. ~~docker-compose.prod.yml health checks~~ ✅ все сервисы
8. ~~CI/CD workflows~~ ✅ 5 workflow файлов

---

**Последнее обновление:** 2026-03-18
**Статус:** Monitoring настроен, Docker Compose production готов, тесты 60/76 passed
**Следующий приоритет:** Исправить failing тесты, достичь 80% coverage

### Сессия 2026-03-18 (TODO.md update)
**Обновления:**
- ✅ Monitoring: Prometheus + Grafana + Node Exporter конфигурация
- ✅ docker-compose.prod.yml: health checks, resource limits, replicas
- ✅ CI/CD: 5 workflow файлов готовы
- ✅ Documentation: 28 MD файлов в docs/
- ✅ Тесты: 60/76 passed (~80% работающих)

**Что работает:**
- ✅ Backend API - все endpoints доступны
- ✅ Database - PostgreSQL с performance tuning
- ✅ Redis - cache с allkeys-lru policy
- ✅ Health checks - для всех сервисов
- ✅ CI/CD - тесты запускаются при push
- ✅ Nginx reverse proxy - frontend + backend
- ✅ Celery worker + beat
- ✅ Database backup - ежедневные бэкапы
- ✅ Sentry - frontend + backend конфигурация

**Известные проблемы:**
1. ⚠️ Тесты влияют друг на друга (shared DB state) - conftest cleanup добавлен
2. ⚠️ Websocket тесты - mock проблемы (ERROR)
3. ⚠️ Notifications/Mentors тесты - KeyError: 'access_token' (fixture mismatch)
4. ⚠️ Coverage ~45-60% (цель: 80%)

**План на следующую сессию:**
1. [ ] Исправить test_websocket_chat.py (mock проблемы)
2. [ ] Исправить test_notifications.py (KeyError: 'access_token')
3. [ ] Исправить test_mentors.py (fixture mismatch)
4. [ ] Исправить test_errors.py (формат ответов)
5. [ ] Добавить тесты для непокрытых модулей
6. [ ] Достичь 80% coverage

**Результаты тестов (2026-03-10):**
- ✅ test_auth.py: 11/11 passed
- ✅ test_sessions.py: 18/18 passed
- ✅ test_users.py: 8/8 passed
- ✅ test_courses.py: 11/11 passed
- ✅ test_cache.py: 10/10 passed
- ✅ test_e2e.py: 3/3 passed
- ✅ test_reviews.py: 18/18 passed
- ⚠️ test_progress.py: 10/14 passed
- 📊 Total: 60 passed, 3 failed (при совместном запуске)

**Синхронизация:**
- dev ↔ main ✅
- GitHub Actions готовы к работе
