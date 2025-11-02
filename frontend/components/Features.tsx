import { Code, MessageSquare, BookOpen, Users, Video, Target, ArrowRight } from 'lucide-react'

const features = [
  {
    icon: Code,
    title: 'Задачи на код',
    description: 'Решайте задачи на код в нашей песочнице и проверяйте свои навыки в программировании',
    link: '/coding',
    linkText: 'Перейти',
  },
  {
    icon: MessageSquare,
    title: 'Тренажер собеседований',
    description: 'Отвечайте на вопросы и получайте аналитику по собеседованию. Найдите свои слабые и сильные места',
    link: '/interview',
    linkText: 'Пройти собеседование',
  },
  {
    icon: BookOpen,
    title: 'База вопросов',
    description: 'Изучайте нужные вам технологии. Отвечайте на вопросы и отслеживайте свой прогресс',
    link: '/questions',
    linkText: 'Перейти',
  },
  {
    icon: Users,
    title: 'Менторы',
    description: 'Опытные специалисты помогут вам подготовиться к собеседованию в топовых компаниях',
    link: '/mentors',
    linkText: 'Все менторы',
  },
  {
    icon: Target,
    title: 'Роадмапы',
    description: 'Прокачивайте свои знания в роадмапах постепенно, отслеживайте свой прогресс',
    link: '/roadmaps',
    linkText: 'Перейти',
  },
  {
    icon: Video,
    title: 'Видео сессии',
    description: 'Проводите индивидуальные сессии с менторами через видеоконференции',
    link: '/sessions',
    linkText: 'Забронировать',
  },
]

export default function Features() {
  return (
    <section className="section-padding bg-white">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Возможности
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Всё, что нужно для быстрой подготовки к собеседованию
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <div
                key={index}
                className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-lg transition-shadow duration-200"
              >
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mb-4">
                  <Icon className="w-6 h-6 text-primary-600" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {feature.title}
                </h3>
                <p className="text-gray-600 mb-4">
                  {feature.description}
                </p>
                <a
                  href={feature.link}
                  className="text-primary-600 hover:text-primary-700 font-medium inline-flex items-center group"
                >
                  {feature.linkText}
                  <ArrowRight className="ml-1 w-4 h-4 group-hover:translate-x-1 transition-transform" />
                </a>
              </div>
            )
          })}
        </div>
      </div>
    </section>
  )
}

