export const metadata = {
  title: 'Тарифы — MentorHub',
  description: 'Выберите удобный формат менторства: разовые сессии, подписка или интенсив.',
}

const plans = [
  {
    name: 'Старт',
    price: 'Бесплатно',
    period: '',
    features: ['Каталог менторов', 'Открытые материалы', 'Демо-сессии (ограниченно)'],
    cta: 'Начать',
  },
  {
    name: 'Сессии',
    price: 'от $30',
    period: 'за 60 мин',
    features: ['1:1 созвоны', 'Домашние задания', 'Обратная связь', 'Подбор менторов'],
    cta: 'Выбрать ментора',
    highlighted: true,
  },
  {
    name: 'Подписка',
    price: '$99',
    period: 'в месяц',
    features: ['2 сессии/мес', 'Чат с ментором', 'План развития', 'Подготовка к интервью'],
    cta: 'Оформить',
  },
]

export default function PricingPage() {
  return (
    <main className="container mx-auto max-w-6xl px-4 py-10">
      <h1 className="text-3xl font-bold tracking-tight text-gray-900 mb-2">Тарифы</h1>
      <p className="text-gray-700 mb-8">Гибкая оплата — разовые сессии или подписка. Отменить можно в любой момент.</p>

      <div className="grid gap-6 md:grid-cols-3">
        {plans.map((p) => (
          <div key={p.name} className={`rounded-xl border p-6 bg-white ${p.highlighted ? 'ring-2 ring-indigo-600' : ''}`}>
            <h3 className="text-xl font-semibold mb-2">{p.name}</h3>
            <div className="flex items-baseline gap-2 mb-4">
              <span className="text-3xl font-bold">{p.price}</span>
              {p.period && <span className="text-gray-500">{p.period}</span>}
            </div>
            <ul className="text-gray-700 space-y-2 mb-6 list-disc pl-5">
              {p.features.map((f) => (
                <li key={f}>{f}</li>
              ))}
            </ul>
            <button className="w-full rounded-md bg-indigo-600 px-4 py-2 text-white hover:bg-indigo-700">{p.cta}</button>
          </div>
        ))}
      </div>

      <p className="text-sm text-gray-500 mt-6">Указанные цены — ориентировочные. Итоговая стоимость зависит от выбранного ментора и предметной области.</p>
    </main>
  )
}
