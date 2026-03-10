'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import { ChevronLeft, Calendar, User, Share2, MessageCircle, Heart } from 'lucide-react'
import Link from 'next/link'
import Button from '@/components/ui/Button'
import Card from '@/components/ui/Card'

interface BlogPost {
  slug: string
  title: string
  author: string
  date: string
  readTime: string
  category: string
  image: string
  excerpt: string
  likes: number
  comments: number
  content: string
}

const posts: Record<string, BlogPost> = {
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

const relatedPosts = [
  { slug: 'react-performance', title: 'Оптимизация React', image: '⚙️' },
  { slug: 'typescript-tips', title: 'Tips TypeScript', image: '📘' },
  { slug: 'web-optimization', title: 'Оптимизация сайта', image: '🚀' }
]

// Функция для парсинга markdown-контента
function parseContent(content: string) {
  return content.split('\n\n').map((block, idx) => {
    // Заголовки
    if (block.startsWith('#')) {
      const level = (block.match(/^#+/) || [''])[0].length
      const text = block.replace(/^#+\s/, '')
      const classNames: Record<number, string> = {
        1: 'text-4xl font-bold text-gray-900 mt-8 mb-4',
        2: 'text-2xl font-bold text-gray-900 mt-6 mb-3',
        3: 'text-xl font-bold text-gray-900 mt-4 mb-2'
      }
      const Tag = `h${Math.min(level, 6)}` as keyof JSX.IntrinsicElements
      return (
        <Tag key={idx} className={classNames[level] || 'text-lg font-semibold text-gray-900'}>
          {text}
        </Tag>
      )
    }
    
    // Списки
    if (block.includes('\n-') || block.includes('\n1.')) {
      const lines = block.split('\n')
      const listItems = lines.filter(line => line.trim().startsWith('-') || /^\d+\./.test(line.trim()))
      const isOrdered = /^\d+\./.test(listItems[0]?.trim() || '')
      const ListTag = isOrdered ? 'ol' : 'ul'
      
      return (
        <ListTag key={idx} className={`space-y-2 ${isOrdered ? 'list-decimal' : 'list-disc'} list-inside ml-4`}>
          {listItems.map((item, i) => {
            const text = item.replace(/^[-\d.]\s*/, '').trim()
            // Обработка жирного текста **text**
            const formattedText = text.split(/(\*\*.*?\*\*)/).map((part, j) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return <strong key={j}>{part.slice(2, -2)}</strong>
              }
              return part
            })
            return <li key={i} className="text-gray-700 text-lg">{formattedText}</li>
          })}
        </ListTag>
      )
    }
    
    // Обычные параграфы
    return (
      <p key={idx} className="text-gray-700 text-lg leading-relaxed">
        {block}
      </p>
    )
  })
}

export default function BlogPostPage({ params }: Props) {
  const [liked, setLiked] = useState(false)
  const [comment, setComment] = useState('')
  const router = useRouter()
  const post = posts[params.slug]

  if (!post) {
    router.push('/blog')
    return null
  }

  const handleShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: post.title,
          text: post.excerpt,
          url: window.location.href,
        })
      } catch {
        // Sharing failed silently
      }
    } else {
      navigator.clipboard.writeText(window.location.href)
      alert('Ссылка скопирована в буфер обмена!')
    }
  }

  const handleCommentSubmit = () => {
    if (comment.trim()) {
      setComment('')
      alert('Комментарий отправлен!')
    }
  }

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      {/* Back Button */}
      <Link href="/blog" className="inline-flex items-center text-indigo-600 hover:text-indigo-700 mb-6 transition-colors">
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

          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">{post.title}</h1>

          <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-6 text-gray-600 border-t border-b border-gray-200 py-4">
            <div className="flex items-center gap-2">
              <User className="h-4 w-4" />
              <span>{post.author}</span>
            </div>
            <div className="flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              <time dateTime={post.date}>
                {new Date(post.date).toLocaleDateString('ru-RU', { 
                  year: 'numeric', 
                  month: 'long', 
                  day: 'numeric' 
                })}
              </time>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setLiked(!liked)}
                aria-label={liked ? 'Убрать лайк' : 'Поставить лайк'}
                className={`inline-flex items-center gap-2 px-3 py-1 rounded-lg transition-all ${
                  liked ? 'bg-red-100 text-red-600' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                <Heart className={`h-4 w-4 ${liked ? 'fill-current' : ''}`} />
                <span>{post.likes + (liked ? 1 : 0)}</span>
              </button>
              <button 
                aria-label="Комментарии" 
                className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              >
                <MessageCircle className="h-4 w-4" />
                <span>{post.comments}</span>
              </button>
              <button 
                onClick={handleShare}
                aria-label="Поделиться" 
                className="inline-flex items-center gap-2 px-3 py-1 rounded-lg bg-gray-100 text-gray-600 hover:bg-gray-200 transition-colors"
              >
                <Share2 className="h-4 w-4" />
              </button>
            </div>
          </div>
        </header>

        {/* Content */}
        <div className="mb-12">
          <div className="text-6xl mb-8" role="img" aria-label="Иконка поста">{post.image}</div>
          <div className="prose prose-lg max-w-none">
            {parseContent(post.content)}
          </div>
        </div>

        {/* Tags */}
        <div className="border-t border-gray-200 py-6 mb-12">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Теги</h3>
          <div className="flex flex-wrap gap-2">
            {['Обучение', 'Карьера', 'IT', 'Развитие'].map((tag) => (
              <Link
                key={tag}
                href={`/blog?tag=${tag.toLowerCase()}`}
                className="px-3 py-1 rounded-full bg-gray-100 text-gray-700 text-sm hover:bg-gray-200 transition-colors"
              >
                #{tag}
              </Link>
            ))}
          </div>
        </div>

        {/* Author Info */}
        <Card padding="lg" className="bg-indigo-50 border border-indigo-200 mb-12">
          <div className="flex items-start gap-4">
            <div className="text-5xl flex-shrink-0" role="img" aria-label="Аватар автора">👨‍💼</div>
            <div className="flex-1">
              <h4 className="font-bold text-gray-900 mb-1">{post.author}</h4>
              <p className="text-gray-700 mb-3">
                Опытный разработчик и наставник. Помогает новичкам и профессионалам достичь своих целей в IT.
              </p>
              <Link href="/mentors/1">
                <Button variant="secondary" size="sm">
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
                  <div className="text-5xl mb-3" role="img" aria-label="Иконка статьи">{relPost.image}</div>
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
        <h3 className="text-2xl font-bold text-gray-900 mb-6">Комментарии ({post.comments})</h3>
        <Card padding="md" className="mt-6">
          <h4 className="font-semibold text-gray-900 mb-4">Оставить комментарий</h4>
          <textarea
            id="comment"
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Ваш комментарий..."
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 mb-4 resize-none"
            rows={4}
            aria-label="Поле для комментария"
          />
          <Button variant="secondary" onClick={handleCommentSubmit}>
            Отправить комментарий
          </Button>
        </Card>
      </div>
    </main>
  )
}
