export const metadata = {
  title: 'FAQ — Частые вопросы',
  description: 'Ответы на частые вопросы о менторстве, оплате, гарантии и возвратах.',
}

const faqs = [
  {
    q: 'Кому подойдёт менторство?',
    a: 'Новичкам, джунам и специалистам, которые хотят ускорить развитие, сменить стек или подготовиться к собеседованию.',
  },
  {
    q: 'Как выбрать ментора?',
    a: 'Используйте фильтры по стеку, опыту и цене. Читайте отзывы, приходите на демо-сессию и оцените “химию”.',
  },
  {
    q: 'Как проходит оплата?',
    a: 'Оплата через защищённые платёжные провайдеры. Доступны разовые платежи и подписка.',
  },
  {
    q: 'Можно ли вернуть деньги?',
    a: 'Да. Если сессия не состоялась или вы остались недовольны качеством — оформим возврат согласно политике возвратов.',
  },
]

export default function FAQPage() {
  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">FAQ — Частые вопросы</h1>
      <div className="space-y-6">
        {faqs.map((f) => (
          <details key={f.q} className="rounded-lg border bg-white p-5">
            <summary className="cursor-pointer select-none text-lg font-medium">{f.q}</summary>
            <p className="mt-3 text-gray-700">{f.a}</p>
          </details>
        ))}
      </div>
    </main>
  )
}
