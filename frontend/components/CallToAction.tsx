import Link from 'next/link'
import { ArrowRight } from 'lucide-react'
import Button from './ui/Button'

export default function CallToAction() {
  return (
    <section className="py-20 bg-gradient-to-r from-indigo-600 to-purple-600">
      <div className="container-custom">
        <div className="max-w-4xl mx-auto text-center text-white">
          <h2 className="text-4xl font-bold mb-6">
            Готовы начать свой путь в IT?
          </h2>
          <p className="text-xl mb-8 opacity-90">
            Присоединяйтесь к тысячам студентов, которые уже развивают свою карьеру с MentorHub.
            Найдите ментора, пройдите курсы и достигните своих целей!
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/mentors">
              <Button variant="secondary" size="lg" className="bg-white text-indigo-600 hover:bg-gray-100">
                Найти ментора
                <ArrowRight className="ml-2 h-5 w-5" />
              </Button>
            </Link>
            <Link href="/courses">
              <Button variant="outline" size="lg" className="border-white text-white hover:bg-white/10">
                Посмотреть курсы
              </Button>
            </Link>
          </div>
          <p className="mt-8 text-sm opacity-75">
            Первая сессия с ментором — бесплатно!
          </p>
        </div>
      </div>
    </section>
  )
}
