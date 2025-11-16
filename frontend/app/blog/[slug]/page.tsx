import { notFound } from 'next/navigation'

export const dynamicParams = true

const posts: Record<string, { title: string; date: string; content: string }> = {
  'kak-podgotsya-k-sobesedovaniyu': {
    title: 'Как подготовиться к собеседованию в IT',
    date: '2025-11-01',
    content:
      'Готовьтесь по вакансиям, прокачивайте алгоритмы, системный дизайн и рассказывайте о своих проектах через STAR. Практикуйтесь с ментором и делайте заметки по каждому интервью.',
  },
  'kak-vybrat-mentora': {
    title: 'Как выбрать ментора: 7 критериев',
    date: '2025-10-20',
    content:
      'Опыт в нужном стеке, кейсы, отзывы, способность объяснять, регулярность, эмпатия и совпадение ожиданий. Возьмите демо-сессию перед подпиской.',
  },
}

interface Props { params: { slug: string } }

export async function generateMetadata({ params }: Props) {
  const post = posts[params.slug]
  if (!post) return { title: 'Пост не найден — Блог' }
  return {
    title: `${post.title} — Блог MentorHub`,
    description: post.content.slice(0, 140),
  }
}

export default function BlogPostPage({ params }: Props) {
  const post = posts[params.slug]
  if (!post) return notFound()
  return (
    <main className="container mx-auto max-w-3xl px-4 py-10">
      <article className="prose prose-indigo max-w-none">
        <h1>{post.title}</h1>
        <p className="text-sm text-gray-500">{new Date(post.date).toLocaleDateString('ru-RU')}</p>
        <p>{post.content}</p>
      </article>
    </main>
  )
}
