# Заметки о зависимостях

## pydantic-core конфликт

**Проблема:**
- pydantic 2.5.0 требует pydantic-core==2.14.1
- Нельзя явно указывать pydantic-core==2.41.5

**Решение:**
- Удалить pydantic-core из requirements.txt
- pip автоматически установит совместимую версию

## antlr4-python3-runtime

**Версия:** 4.9.3
**Причина:** Совместимость с omegaconf/hydra

## Установка для локальной разработки

```bash
cd backend
pip install -r requirements.txt
```

pip автоматически разрешит зависимости:
- pydantic-core==2.14.1 (для pydantic 2.5.0)
- antlr4-python3-runtime==4.9.3

## Render deployment

Сборка работает корректно без явного указания pydantic-core.
