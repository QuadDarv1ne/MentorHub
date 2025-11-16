import { Users, BookOpen, Award, TrendingUp } from 'lucide-react'
import StatCard from './ui/StatCard'

export default function Statistics() {
  const stats = [
    {
      title: 'Активных пользователей',
      value: '15,000+',
      icon: <Users className="h-6 w-6" />,
      trend: { value: 12, isPositive: true },
      description: 'Студенты и менторы'
    },
    {
      title: 'Проведено сессий',
      value: '50,000+',
      icon: <TrendingUp className="h-6 w-6" />,
      trend: { value: 18, isPositive: true },
      description: 'За всё время'
    },
    {
      title: 'Доступных курсов',
      value: '200+',
      icon: <BookOpen className="h-6 w-6" />,
      trend: { value: 8, isPositive: true },
      description: 'По всем направлениям'
    },
    {
      title: 'Средний рейтинг',
      value: '4.8',
      icon: <Award className="h-6 w-6" />,
      description: 'Из 5 звёзд'
    }
  ]

  return (
    <section className="py-16 bg-gray-50">
      <div className="container-custom">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Наши достижения
          </h2>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Тысячи студентов уже достигли своих целей с помощью MentorHub
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {stats.map((stat, index) => (
            <StatCard
              key={index}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              trend={stat.trend}
              description={stat.description}
            />
          ))}
        </div>
      </div>
    </section>
  )
}
