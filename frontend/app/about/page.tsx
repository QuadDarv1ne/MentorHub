export const metadata = {
  title: 'О проекте — MentorHub',
  description: 'MentorHub — открытая платформа для менторства в IT: миссия, ценности, команда и путь развития.',
}

export default function AboutPage() {
  return (
    <main className="container mx-auto max-w-5xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">О проекте</h1>
      <p className="text-gray-700 leading-relaxed mb-6">
        MentorHub — это открытая платформа для менторов и студентов в IT. Мы помогаем учиться быстрее,
        системнее и результативнее: от первых шагов до трудоустройства.
      </p>

      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-3">Миссия</h2>
        <p className="text-gray-700">Делать качественное наставничество доступным каждому, независимо от опыта и локации.</p>
      </section>

      <section className="mb-10">
        <h2 className="text-2xl font-semibold mb-3">Ценности</h2>
        <ul className="list-disc pl-6 text-gray-700 space-y-2">
          <li>Прозрачность и доверие</li>
          <li>Практика и результат</li>
          <li>Уважение и инклюзивность</li>
          <li>Открытость к обратной связи</li>
        </ul>
      </section>

      <section className="mb-10 grid gap-6 md:grid-cols-2">
        <div className="p-5 rounded-lg border bg-white">
          <h3 className="text-lg font-semibold mb-2">Для студентов</h3>
          <p className="text-gray-700">Персональные планы, разбор задач, подготовка к собеседованиям, карьерная стратегия.</p>
        </div>
        <div className="p-5 rounded-lg border bg-white">
          <h3 className="text-lg font-semibold mb-2">Для менторов</h3>
          <p className="text-gray-700">Профиль ментора, расписание, отзывы, аналитика, монетизация экспертизы.</p>
        </div>
      </section>

      <section>
        <h2 className="text-2xl font-semibold mb-3">Контакты</h2>
        <div className="rounded-lg border bg-white p-5">
          <p className="text-gray-800 font-medium">Ответственный: Дуплей Максим Игоревич</p>
          <ul className="mt-2 text-gray-700 space-y-1">
            <li><span className="text-gray-500">Email:</span> <a className="text-indigo-600 hover:underline" href="mailto:maksimqwe42@mail.ru">maksimqwe42@mail.ru</a></li>
            <li><span className="text-gray-500">Телефон:</span> <a className="text-indigo-600 hover:underline" href="tel:+79150480249">+7 915 048‑02‑49</a></li>
            <li><span className="text-gray-500">Telegram:</span> <a className="text-indigo-600 hover:underline" href="https://t.me/quadd4rv1n7" target="_blank" rel="noopener noreferrer">@quadd4rv1n7</a></li>
          </ul>
        </div>
      </section>
    </main>
  )
}
