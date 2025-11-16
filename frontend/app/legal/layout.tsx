export const metadata = {
  title: 'Правовая информация — MentorHub',
}

export default function LegalLayout({ children }: { children: React.ReactNode }) {
  return (
    <section className="container mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Правовая информация</h1>
      <div className="rounded-xl border bg-white p-6">
        {children}
      </div>
      <nav className="mt-6 text-sm text-gray-600">
        <ul className="flex flex-wrap gap-4">
          <li><a className="hover:underline" href="/legal/terms">Пользовательское соглашение</a></li>
          <li><a className="hover:underline" href="/legal/privacy">Политика конфиденциальности</a></li>
          <li><a className="hover:underline" href="/legal/cookies">Файлы cookie</a></li>
          <li><a className="hover:underline" href="/legal/dpa">Обработка данных (DPA)</a></li>
          <li><a className="hover:underline" href="/legal/refund">Политика возвратов</a></li>
          <li><a className="hover:underline" href="/legal/aup">Политика допустимого использования</a></li>
          <li><a className="hover:underline" href="/legal/community">Правила сообщества</a></li>
          <li><a className="hover:underline" href="/legal/license">Лицензия</a></li>
          <li><a className="hover:underline" href="/legal/consent">Настройки cookie</a></li>
        </ul>
      </nav>
    </section>
  )
}
