export const metadata = {
  title: 'Контакты — MentorHub',
  description: 'Связаться с командой MentorHub: поддержка, партнёрства, обратная связь.',
}

export default function ContactPage() {
  return (
    <main className="container mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Контакты</h1>
      <div className="rounded-xl border bg-white p-6">
        <h2 className="text-xl font-semibold mb-3">Поддержка</h2>
        <p className="text-gray-700 mb-6">support@mentorhub.dev — вопросы по оплате, сессиям и аккаунту.</p>

        <h2 className="text-xl font-semibold mb-3">Партнёрства и PR</h2>
        <p className="text-gray-700 mb-6">partnerships@mentorhub.dev — интеграции, спецпроекты, мероприятия.</p>

        <h2 className="text-xl font-semibold mb-3">Обратная связь</h2>
        <p className="text-gray-700">Мы открыты к предложениям — напишите на feedback@mentorhub.dev</p>
      </div>
    </main>
  )
}
