import TestimonialCard from './ui/TestimonialCard'

export default function Testimonials() {
  const testimonials = [
    {
      name: 'Алексей Соколов',
      role: 'Junior Developer → Middle Developer',
      text: 'Благодаря менторству на MentorHub я за полгода вырос с Junior до Middle разработчика. Мой ментор помог структурировать знания и подготовиться к собеседованиям.',
      rating: 5
    },
    {
      name: 'Мария Петрова',
      role: 'Сменила карьеру на IT',
      text: 'Я пришла в IT с нуля. Курсы и персональный ментор помогли мне освоить React и найти первую работу уже через 8 месяцев. Огромное спасибо платформе!',
      rating: 5
    },
    {
      name: 'Дмитрий Васильев',
      role: 'DevOps Engineer',
      text: 'Отличная платформа для тех, кто хочет расти профессионально. Здесь можно найти ментора по любому направлению и получить действительно полезные знания.',
      rating: 5
    },
    {
      name: 'Екатерина Иванова',
      role: 'Frontend Developer',
      text: 'Подготовка к собеседованиям с ментором дала невероятный результат. Прошла собеседование в крупную компанию с первого раза. Рекомендую всем!',
      rating: 5
    },
    {
      name: 'Сергей Николаев',
      role: 'Mobile Developer',
      text: 'Курсы на платформе структурированы идеально. Теория + практика + обратная связь от менторов. Именно то, что нужно для эффективного обучения.',
      rating: 5
    },
    {
      name: 'Анна Смирнова',
      role: 'Data Analyst',
      text: 'Нашла здесь своего ментора по Data Science. Занятия проходят продуктивно, всегда получаю ответы на все вопросы. Уже вижу прогресс в своих навыках!',
      rating: 5
    }
  ]

  return (
    <section className="py-16 bg-white">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Что говорят наши студенты
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Реальные отзывы людей, которые достигли своих целей с MentorHub
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {testimonials.map((testimonial, index) => (
            <TestimonialCard
              key={index}
              name={testimonial.name}
              role={testimonial.role}
              text={testimonial.text}
              rating={testimonial.rating}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
