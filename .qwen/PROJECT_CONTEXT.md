# MentorHub — Проект Контекст

## Статус на 2026-03-08

### Развёртывание (Render)
- ✅ Web Service развёрнут: https://mentorhub-7eat.onrender.com/
- ✅ PostgreSQL создана (Free, Oregon)
  - Internal URL: `postgresql://mentorhub_927e_user:cPiIR0gZkJPPYfonjh1CKYC9THBqLeeH@dpg-d6mssmma2pns73ddpmcg-a/mentorhub_927e`
  - Добавлена в Environment Variables
- ⚠️ Redis НЕ создан (используется memory cache)
- ⚠️ DATABASE_URL добавлен в Environment, ждём подтверждения работы

### Последние изменения
1. **Dockerfile**: ARG для переменных окружения (DATABASE_URL, REDIS_URL, SECRET_KEY)
2. **start.sh**: Проверка DATABASE_URL (warning, не ошибка)
3. **config.py**: Валидация переменных (warnings вместо errors)
4. **render.yaml**: Инструкция по настройке

### Синхронизация веток
- ✅ `dev` = `main` (синхронизированы)
- Последний коммит: `056a723 fix: allow start without database (warnings only)`

### Что проверить после деплоя
В логах Render искать:
```
DATABASE_URL: postgresql://...
✅ Database connection successful
Environment: production
```

### Проблемы и решения
| Проблема | Решение |
|----------|---------|
| sbp-qr не в PyPI | Закомментирован в requirements.txt |
| DATABASE_URL не читался | Добавлен в Environment Variables вручную |
| ALLOWED_HOSTS=["*"] | Исправлено на [] с валидацией |
| JWT без aud/iss | Добавлены claims в auth.py и security.py |
| WebSocket токен в URL | Изменено на auth через первое сообщение |
| Порт 10000 занят | Render сам назначает PORT |

### Переменные окружения (настроено в Render)
- ✅ DATABASE_URL — из PostgreSQL
- ✅ SECRET_KEY — сгенерирована
- ✅ ENVIRONMENT=production
- ✅ RENDER=true
- ⚠️ REDIS_URL — не настроен (memory cache fallback)

### Следующие шаги
1. Проверить логи после деплоя
2. Создать Redis (опционально, для production)
3. Настроить REDIS_URL
4. Протестировать API

### Файлы проекта
- Backend: `backend/app/`
- Frontend: `frontend/`
- Docker: `Dockerfile`, `start.sh`
- Deploy: `deploy/render/render.yaml`
