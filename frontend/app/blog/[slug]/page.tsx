'use client'

import { useState } from 'react'
import { notFound } from 'next/navigation'
import { ChevronLeft, Calendar, User, Share2, MessageCircle, Heart } from 'lucide-react'
import Link from 'next/link'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

const posts: Record<string, any> = {
  'kak-podgotsya-k-sobesedovaniyu': {
    slug: 'kak-podgotsya-k-sobesedovaniyu',
    title: 'Как подготовиться к собеседованию в IT',
    author: 'Иван Петров',
    date: '2025-11-01',
    readTime: '10 мин',
    category: 'Карьера',
    image: '🎯',
    excerpt: 'Готовьтесь по вакансиям, прокачивайте алгоритмы и рассказывайте о своих проектах через STAR.',
    likes: 342,
    comments: 28,
    content: `
# Как подготовиться к собеседованию в IT

Собеседование - это ответственный момент в карьере разработчика. Давайте разберёмся, как правильно подготовиться.

## 1. Изучите требования вакансии

Прочитайте описание вакансии несколько раз. Выпишите все требования и умения, которые вам нужно знать.

## 2. Повторите основы

- **Алгоритмы**: LeetCode, Codeforces
- **Структуры данных**: массивы, связные списки, деревья
- **Паттерны проектирования**: Factory, Singleton, Observer

## 3. Подготовьте STAR истории

Используйте методику STAR для рассказа о своих проектах:

- **Situation** - контекст
- **Task** - задача
- **Action** - действия
- **Result** - результаты

## 4. Практикуйтесь с ментором

Репетиция собеседования с опытным ментором очень помогает:

- Получите фидбек на свои ответы
- Привыкните к формату
- Избавитесь от волнения

## Советы по день собеседования

1. Хорошо поспите в ночь перед собеседованием
2. Проверьте интернет-соединение
3. Придите за 10 минут до начала
4. Улыбайтесь и говорите уверенно
5. Задавайте вопросы о компании

Удачи на собеседовании! 🚀
    `.trim(),
  },
  'kak-vybrat-mentora': {
    slug: 'kak-vybrat-mentora',
    title: 'Как выбрать ментора: 7 критериев',
    author: 'Мария Сидорова',
    date: '2025-10-20',
    readTime: '8 мин',
    category: 'Обучение',
    image: '👨‍🏫',
    excerpt: 'Опыт, кейсы, отзывы, способность объяснять - главные критерии выбора ментора.',
    likes: 289,
    comments: 15,
    content: `
# Как выбрать ментора: 7 критериев

Выбор ментора - это одно из самых важных решений в вашем пути развития как разработчика.

## Критерий 1: Опыт в нужной области

Ментор должен иметь реальный опыт в том направлении, которое вас интересует.

## Критерий 2: Портфолио и кейсы

Попросите примеры проектов, в которых он участвовал. Это покажет уровень его компетенции.

## Критерий 3: Отзывы студентов

Прочитайте отзывы предыдущих учеников. Они дадут вам объективную оценку.

## Критерий 4: Способность объяснять

Ментор должен уметь доступно объяснить сложные концепции.

## Критерий 5: Регулярность и надёжность

Убедитесь, что ментор может гарантировать регулярные занятия.

## Критерий 6: Эмпатия

Хороший ментор должен понимать сложности обучения и помогать морально.

## Критерий 7: Совпадение ожиданий

Обсудите цели, темп обучения и формат занятий.

## Совет

Попросите демо-сессию перед тем, как подписаться на полный курс. Это поможет понять, подходит ли вам этот ментор.

Удачи в поиске идеального ментора! 📚
    `.trim(),
  },
}

interface Props {
  params: { slug: string }
}

export async function generateMetadata({ params }: Props) {
  const post = posts[params.slug]
  if (!post) return { title: 'Пост не найден — Блог' }
  return {
    title: `${post.title} — Блог MentorHub`,
    description: post.excerpt,
  }
}

const relatedPosts = [
  { slug: 'react-performance', title: 'Оптимизация React', image: '⚙️' },
  { slug: 'typescript-tips', title: 'Tips TypeScript', image: '📘' },
  { slug: 'web-optimization', title: 'Оптимизация сайта', image: '🚀' }
]

export default function BlogPostPage({ params }: Props) {
  const [liked, setLiked] = useState(false)
  const post = posts[params.slug]

  if (!post) return notFound()

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      {/* Back Button */}
      <Link href="/blog" className="inline-flex items-center text-indigo-600 hover:text-indigo-700 mb-6">
        <ChevronLeft className="h-4 w-4 mr-1" />
        Вернуться к блогу
      </Link>

      {/* Header */}
      <article>
        <header className="mb-10">
          <div className="flex items-center gap-2 mb-4">
            <span className="text-sm font-semibold px-3 py-1 bg-indigo-100 text-indigo-700 rounded-full">
              {post.category}
            </span>
            <span className="text-sm text-gray-600">{post.readTime}</span>
          </div>

          <h1 className="text-5xl font-bold text-gray-900 mb-4">{post.title}</h1>

          <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-6 text-gray-600 border-t border-b border-gray-200 py-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span>{post.author}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <span>{new Date(post.date).toLocaleDateString('ru-RU')}</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setLiked(!liked)}
                title="Лайк"
                className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg transition-colors ${
                  liked ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Heart className={`h-4 w-4 ${liked ? 'fill-current' : ''}`} />
                {post.likes + (liked ? 1 : 0)}
              </button>
              <button title="Комментарии" className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200">
                <MessageCircle className="h-4 w-4" />
                {post.comments}
              </button>
              <button title="Поделиться" className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200">
                <Share2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="mb-12">
          <div className="text-6xl mb-8">{post.image}</div>
          <div className="text-gray-700 leading-relaxed space-y-6">
            {post.content.split('\n\n').map((paragraph: string, idx: number) => {
              if (paragraph.startsWith('#')) {
                const level = paragraph.match(/^#+/)?.[0].length || 1
                const text = paragraph.replace(/^#+\s/, '')
                const classNames: Record<number, string> = {
                  1: 'text-4xl font-bold text-gray-900 mt-8 mb-4',
                  2: 'text-2xl font-bold text-gray-900 mt-6 mb-3',
                  3: 'text-xl font-bold text-gray-900 mt-4 mb-2'
                }
                return (
                  <div key={idx} className={classNames[level] || 'text-lg font-semibold text-gray-900'}>
                    {text}
                  </div>
                )
              }
              return (
                <p key={idx} className="text-gray-700 text-lg leading-relaxed">
                  {paragraph}
                </p>
              )
            })}
          </div>
        </div>

        {/* Tags */}
        <div className="border-t border-gray-200 py-6 mb-12">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Теги</h3>
          <div className="flex flex-wrap gap-2">
            {['Обучение', 'Карьера', 'IT', 'Развитие'].map((tag) => (
              <button
                key={tag}
                className="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm hover:bg-gray-200"
              >
                #{tag}
              </button>
            ))}
          </div>
        </div>

        {/* Author Info */}
        <Card padding="lg" className="bg-indigo-50 border border-indigo-200 mb-12">
          <div className="flex items-center gap-4">
            <div className="text-5xl flex-shrink-0">👨‍💼</div>
            <div>
              <h4 className="font-bold text-gray-900 mb-1">{post.author}</h4>
              <p className="text-gray-700 mb-3">
                Опытный разработчик и наставник. Помогает новичкам и профессионалам достичь своих целей в IT.
              </p>
              <Link href="/mentors/1">
                <Button variant="primary" size="sm">
                  Связаться с автором
                </Button>
              </Link>
            </div>
          </div>
        </Card>

        {/* Related Posts */}
        <div>
          <h3 className="text-2xl font-bold text-gray-900 mb-6">Похожие статьи</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {relatedPosts.map((relPost) => (
              <Link key={relPost.slug} href={`/blog/${relPost.slug}`}>
                <Card padding="md" hover className="h-full flex flex-col">
                  <div className="text-5xl mb-3">{relPost.image}</div>
                  <h4 className="font-semibold text-gray-900 mb-2 flex-1">{relPost.title}</h4>
                  <span className="text-indigo-600 text-sm font-medium">Читать →</span>
                </Card>
              </Link>
            ))}
          </div>
        </div>
      </article>

      {/* Comments Section */}
      <div className="mt-16 pt-12 border-t border-gray-200">
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Комментарии</h3>
        <Card padding="md" className="mt-6">
          <h4 className="font-semibold text-gray-900 mb-4">Оставить комментарий</h4>
          <textarea
            id="comment"
            placeholder="Ваш комментарий..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-4"
            rows={4}
          />
          <Button variant="primary">Отправить комментарий</Button>
        </Card>
      </div>
    </main>
  )
}
