export const metadata = {
  title: 'Политика возвратов — MentorHub',
}

export default function RefundPage() {
  return (
    <div className="prose max-w-none">
      <h2>Политика возвратов</h2>
      <ul>
        <li>Если сессия не состоялась по вине ментора — полный возврат.</li>
        <li>Если качество услуги неудовлетворительно — рассмотрим частичный/полный возврат после проверки.</li>
        <li>Подписку можно отменить в любой момент — доступ действует до конца оплаченного периода.</li>
      </ul>
      <p>Связаться по вопросам возвратов: <a className="text-indigo-600 hover:underline" href="mailto:maksimqwe42@mail.ru">maksimqwe42@mail.ru</a></p>
    </div>
  )
}
