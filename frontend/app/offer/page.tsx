export const metadata = {
  title: 'Публичная оферта — MentorHub',
}

export default function OfferPage() {
  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-6">Публичная оферта</h1>
      <div className="prose max-w-none rounded-xl border bg-white p-6">
        <p>
          Настоящий документ является предложением заключить договор возмездного оказания услуг (публичная оферта)
          в соответствии с действующим законодательством. При оплате услуг вы подтверждаете принятие условий оферты.
        </p>
        <h3>Предмет</h3>
        <p>Предоставление доступа к сервису менторства, проведение консультаций и сопутствующие сервисы.</p>
        <h3>Стоимость и порядок расчётов</h3>
        <p>Стоимость указывается на сайте. Оплата через указанных платёжных провайдеров.</p>
        <h3>Права и обязанности</h3>
        <p>Пользователь обязуется соблюдать Правила сообщества и AUP. Исполнитель обязуется оказывать услуги добросовестно.</p>
        <p className="text-sm text-gray-500">Вопросы по оферте: <a className="text-indigo-600 hover:underline" href="mailto:maksimqwe42@mail.ru">maksimqwe42@mail.ru</a></p>
      </div>
    </main>
  )
}
