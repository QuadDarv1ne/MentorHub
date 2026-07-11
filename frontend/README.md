# MentorHub Frontend

Frontend приложение для платформы MentorHub, созданное на Next.js 14 с TypeScript и Tailwind CSS.

## 🚀 Быстрый старт

### Установка зависимостей

```bash
npm install
```

### Запуск в режиме разработки

```bash
npm run dev
```

Приложение будет доступно по адресу: http://localhost:3000

### Сборка для продакшена

```bash
npm run build
npm start
```

## 📁 Структура проекта

```
frontend/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Корневой layout
│   ├── page.tsx          # Главная страница
│   └── globals.css        # Глобальные стили
├── components/            # React компоненты
│   ├── Header.tsx        # Навигация
│   ├── Footer.tsx        # Подвал
│   ├── Hero.tsx          # Hero секция
│   ├── Features.tsx      # Возможности
│   ├── CodingTasks.tsx   # Задачи на код
│   ├── InterviewTrainer.tsx # Тренажер собеседований
│   ├── QuestionDatabase.tsx # База вопросов
│   ├── PopularQuestions.tsx # Популярные вопросы
│   └── MentorsPreview.tsx  # Предпросмотр менторов
├── lib/                   # Утилиты
├── store/                 # State management
└── public/                # Статические файлы
```

## 🎨 Технологии

- **Next.js 14** - React фреймворк с App Router
- **TypeScript** - Типизация
- **Tailwind CSS** - Стилизация
- **Lucide React** - Иконки
- **React Hook Form** - Работа с формами
- **Zod** - Валидация

## 🎯 Особенности главной страницы

Главная страница создана в стиле [Solvit.space](https://solvit.space/) и включает:

1. **Hero секция** - Призыв к действию и основное сообщение
2. **Возможности** - Карточки с основным функционалом
3. **Задачи на код** - Примеры задач с прогрессом
4. **Тренажер собеседований** - Активные сессии подготовки
5. **База вопросов** - Технологии и количество вопросов
6. **Популярные вопросы** - Топ подборки по темам
7. **Менторы** - Предпросмотр менторов с рейтингами

## 🌐 Переменные окружения

Создайте файл `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8001
NEXT_PUBLIC_AGORA_APP_ID=your-agora-app-id
NODE_ENV=development
```

## 📝 Скрипты

- `npm run dev` - Запуск в режиме разработки
- `npm run build` - Сборка для продакшена
- `npm run start` - Запуск продакшен версии
- `npm run lint` - Проверка кода линтером
- `npm run format` - Форматирование кода
- `npm run type-check` - Проверка типов TypeScript

## 🎨 Стилизация

Проект использует Tailwind CSS с кастомной конфигурацией:
- Primary цвета (синий)
- Secondary цвета (фиолетовый)
- Адаптивный дизайн (mobile-first)
- Компонентные классы в `globals.css`

## 📱 Адаптивность

Все компоненты адаптивны и работают на:
- Мобильных устройствах (< 640px)
- Планшетах (640px - 1024px)
- Десктопах (> 1024px)

## 🔗 API интеграция

Frontend подключается к backend API через переменную окружения `NEXT_PUBLIC_API_URL`.

---

**Создано для проекта MentorHub**

