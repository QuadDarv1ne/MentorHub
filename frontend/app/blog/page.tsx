import Link from 'next/link'

export const metadata = {
  title: 'Блог — MentorHub',
  description: 'Советы по карьере в IT, менторство, интервью и истории успеха.',
}

const posts = [
  { slug: 'kak-podgotsya-k-sobesedovaniyu', title: 'Как подготовиться к собеседованию в IT', date: '2025-11-01' },
  { slug: 'kak-vybrat-mentora', title: 'Как выбрать ментора: 7 критериев', date: '2025-10-20' },
]

export default function BlogPage() {
  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Блог</h1>
      <ul className="space-y-4">
        {posts.map((p) => (
          <li key={p.slug} className="rounded-lg border bg-white p-5">
            <time className="text-sm text-gray-500">{new Date(p.date).toLocaleDateString('ru-RU')}</time>
            <h2 className="text-xl font-semibold mt-1">
              <Link href={`/blog/${p.slug}`} className="text-indigo-600 hover:underline">{p.title}</Link>
            </h2>
          </li>
        ))}
      </ul>
    </main>
  )
}
