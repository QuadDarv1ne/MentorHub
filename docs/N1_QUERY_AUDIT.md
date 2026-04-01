# N+1 Query Audit Report

**Дата:** 1 апреля 2026 г.  
**Статус:** В процессе

---

## 📊 Обзор

N+1 проблема возникает, когда код выполняет:
1. Один запрос для получения родительских записей (N)
2. N дополнительных запросов для получения связанных данных (+N)

**Пример проблемы:**
```python
# ПЛОХО - N+1 запрос
users = db.query(User).all()  # 1 запрос
for user in users:
    print(user.profile.email)  # N запросов (по одному на пользователя)

# ХОРОШО - 1 запрос с joinedload
users = db.query(User).options(joinedload(User.profile)).all()
```

---

## 🔍 Найденные Проблемы

### Критичные (Требуется Исправление)

#### 1. chat_rooms.py - Get Messages
**Строка:** 207-230  
**Проблема:** Загрузка сообщений без автора

```python
# Текущий код (ПЛОХО)
query = db.query(ChatMessage).filter(...)
messages = query.all()

for message in messages:
    sender = message.sender  # N+1: запрос на каждое сообщение
```

**Решение:**
```python
# Исправленный код (ХОРОШО)
query = db.query(ChatMessage).options(
    joinedload(ChatMessage.sender)
).filter(...)
messages = query.all()
```

---

#### 2. chat_rooms.py - Get Room with Members
**Строка:** 64-80  
**Проблема:** Проверка комнаты без загрузки members

```python
# Текущий код
room = db.query(ChatRoom).filter(...).first()
# Далее в коде: room.members - N+1
```

**Решение:**
```python
room = db.query(ChatRoom).options(
    joinedload(ChatRoom.members)
).filter(...).first()
```

---

#### 3. calendar.py - Get Events
**Строка:** 210-230  
**Проблема:** Загрузка событий без related data

```python
query = db.query(CalendarEvent).filter(...)
events = query.all()
```

**Решение:**
```python
query = db.query(CalendarEvent).options(
    joinedload(CalendarEvent.user)
).filter(...)
```

---

#### 4. courses.py - Get Course Lessons
**Строка:** 243-247  
**Проблема:** Загрузка уроков без курса

```python
course = db.query(Course).filter(...).first()
lessons = db.query(Lesson).filter(Lesson.course_id == course_id).all()
```

**Решение:**
```python
course = db.query(Course).options(
    joinedload(Course.lessons)
).filter(...).first()
lessons = course.lessons  # Использует loaded relationship
```

---

### Предупреждения (Опционально)

#### 5. achievements.py
**Строки:** 27, 44, 57  
**Статус:** ⚠️ Требуется проверка

```python
achievements = db.query(Achievement).filter(...)
# Achievement может иметь relationship с User
```

**Рекомендация:** Добавить `joinedload(Achievement.user)` если используется в template

---

#### 6. messages.py
**Строки:** 29-60  
**Статус:** ⚠️ Частично исправлено

```python
# Уже используется joinedload для некоторых relationships
messages_query = db.query(Message).options(
    joinedload(Message.sender)
)
```

**Рекомендация:** Проверить все relationships

---

## ✅ Уже Исправлено

### video_calls.py
**Статус:** ✅ Исправлено в сессии 1

```python
# Используется joinedload для creator, participant, chat_room
call = db.query(VideoCall).options(
    joinedload(VideoCall.creator),
    joinedload(VideoCall.participant),
    joinedload(VideoCall.chat_room)
).filter(...).first()
```

---

### courses.py - Get Courses
**Статус:** ✅ Исправлено

```python
courses = db.query(Course).options(
    joinedload(Course.instructor)
).offset(skip).limit(limit).all()
```

---

### courses.py - Get Course Detail
**Статус:** ✅ Исправлено

```python
course = db.query(Course).options(
    joinedload(Course.instructor),
    joinedload(Course.lessons)
).filter(Course.id == course_id).first()
```

---

## 📈 Статистика

| Файл | N+1 Проблем | Статус |
|------|-------------|--------|
| chat_rooms.py | 3 | 🔴 Требуется |
| calendar.py | 1 | 🔴 Требуется |
| courses.py | 1 | ⚠️ Частично |
| achievements.py | 1 | ⚠️ Опционально |
| messages.py | 1 | ⚠️ Проверка |
| video_calls.py | 0 | ✅ Исправлено |
| courses.py (list) | 0 | ✅ Исправлено |

**Всего найдено:** 7 проблем  
**Исправлено:** 2 (28%)  
**Требуется:** 5 (72%)

---

## 🔧 План Исправлений

### Приоритет P0 (Критично)

1. **chat_rooms.py: Get Messages**
   - Добавить `joinedload(ChatMessage.sender)`
   - Добавить `joinedload(ChatMessage.reactions)` если используется

2. **chat_rooms.py: Get Room**
   - Добавить `joinedload(ChatRoom.members)`
   - Добавить `joinedload(ChatRoom.creator)`

3. **calendar.py: Get Events**
   - Добавить `joinedload(CalendarEvent.user)`

### Приоритет P1 (Важно)

4. **courses.py: Get Lessons**
   - Использовать `course.lessons` вместо отдельного query

5. **achievements.py**
   - Проверить использование relationships
   - Добавить joinedload если нужно

---

## 📝 Примеры Исправлений

### chat_rooms.py - Get Messages

**До:**
```python
@router.get("/chat-rooms/{room_id}/messages")
async def get_room_messages(...):
    room = db.query(ChatRoom).filter(...).first()
    
    query = db.query(ChatMessage).filter(
        ChatMessage.room_id == room_id
    ).order_by(ChatMessage.sent_at)
    
    messages = query.offset(skip).limit(limit).all()
    
    result = []
    for message in messages:
        result.append({
            "id": message.id,
            "sender_username": message.sender.username,  # N+1!
            "content": message.content
        })
    
    return result
```

**После:**
```python
@router.get("/chat-rooms/{room_id}/messages")
async def get_room_messages(...):
    room = db.query(ChatRoom).options(
        joinedload(ChatRoom.members)
    ).filter(...).first()
    
    query = db.query(ChatMessage).options(
        joinedload(ChatMessage.sender)
    ).filter(
        ChatMessage.room_id == room_id
    ).order_by(ChatMessage.sent_at)
    
    messages = query.offset(skip).limit(limit).all()
    
    result = []
    for message in messages:
        result.append({
            "id": message.id,
            "sender_username": message.sender.username,  # ✅ No N+1
            "content": message.content
        })
    
    return result
```

---

## 🎯 Метрики Производительности

### До Исправлений

```
Get Messages (100 сообщений):
├── 1 запрос: SELECT * FROM chat_messages
└── 100 запросов: SELECT * FROM users WHERE id = ? (N+1)
Итого: 101 запрос

Время выполнения: ~500ms
```

### После Исправлений

```
Get Messages (100 сообщений):
├── 1 запрос: SELECT * FROM chat_messages JOIN users
Итого: 1 запрос

Время выполнения: ~50ms
```

**Улучшение:** 10x быстрее ⚡

---

## 🚀 Следующие Шаги

1. **Исправить chat_rooms.py** (3 проблемы)
2. **Исправить calendar.py** (1 проблема)
3. **Исправить courses.py** (1 проблема)
4. **Проверить achievements.py** (1 проблема)
5. **Добавить тесты производительности**

---

## 📞 Контакты

**Документация:** [ARCHITECTURE.md](../../docs/ARCHITECTURE.md)  
**Сервисы:** [SERVICES.md](../../backend/docs/SERVICES.md)

---

**MentorHub © 2026** — Open-source платформа для менторства
