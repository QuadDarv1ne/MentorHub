export const metadata = {
  title: 'Контакты — MentorHub',
  description: 'Связаться с командой MentorHub: поддержка, партнёрства, обратная связь.',
}

export default function ContactPage() {
  return (
    <main className="container mx-auto max-w-3xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Контакты</h1>
      <div className="rounded-xl border bg-white p-6 space-y-6">
        <div>
          <h2 className="text-xl font-semibold mb-2">Ответственный по вопросам</h2>
          <p className="text-gray-800">Дуплей Максим Игоревич</p>
          <ul className="mt-2 text-gray-700 space-y-1">
            <li><span className="text-gray-500">Email:</span> <a className="text-indigo-600 hover:underline" href="mailto:maksimqwe42@mail.ru">maksimqwe42@mail.ru</a></li>
            <li><span className="text-gray-500">Телефон:</span> <a className="text-indigo-600 hover:underline" href="tel:+79150480249">+7 915 048‑02‑49</a></li>
            <li><span className="text-gray-500">Telegram:</span> <a className="text-indigo-600 hover:underline" href="https://t.me/quadd4rv1n7" target="_blank" rel="noopener noreferrer">@quadd4rv1n7</a></li>
          </ul>
        </div>
        <div>
          <h2 className="text-xl font-semibold mb-2">Общие вопросы</h2>
          <p className="text-gray-700">Пишите по любым вопросам поддержки, партнёрств и PR на указанные выше контакты.</p>
        </div>
      </div>
    </main>
  )
}
