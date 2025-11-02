import { Metadata } from 'next'
import StepikCourseCard from '@/components/StepikCourseCard'

export const metadata: Metadata = {
  title: 'Курсы на Stepik | MentorHub',
  description: 'Курсы от Дуплей Максима Игоревича на платформе Stepik'
}

const stepikCourses = [
  {
    id: '210134',
    title: 'Java полное руководство',
    description: 'Полный курс по языку программирования Java с нуля до профессионального уровня. Изучите основы, ООП, коллекции, многопоточность и многое другое.',
    stepikUrl: 'https://stepik.org/a/210134',
    price: 0,
    studentsCount: 150,
    rating: 4.8,
    category: 'Java'
  },
  {
    id: '178781',
    title: 'Python разработка с нуля',
    description: 'Практический курс по Python: от основ до создания реальных проектов. Включает работу с базами данных, веб-разработку и автоматизацию.',
    stepikUrl: 'https://stepik.org/a/178781',
    price: 0,
    studentsCount: 200,
    rating: 4.9,
    category: 'Python'
  },
  {
    id: '212445',
    title: 'Android разработка для начинающих',
    description: 'Создавайте мобильные приложения для Android. Курс охватывает основы разработки, работу с UI компонентами, базами данных и API.',
    stepikUrl: 'https://stepik.org/a/212445',
    price: 0,
    studentsCount: 120,
    rating: 4.7,
    category: 'Android'
  },
  {
    id: '252727',
    title: 'DevOps практики и инструменты',
    description: 'Изучите основные практики и инструменты DevOps: Docker, Kubernetes, CI/CD, мониторинг и автоматизацию.',
    stepikUrl: 'https://stepik.org/a/252727',
    price: 0,
    studentsCount: 80,
    rating: 4.6,
    category: 'DevOps'
  },
  {
    id: '252698',
    title: 'Базы данных и SQL',
    description: 'Комплексный курс по работе с базами данных: проектирование, SQL, оптимизация запросов, работа с PostgreSQL.',
    stepikUrl: 'https://stepik.org/a/252698',
    price: 0,
    studentsCount: 170,
    rating: 4.8,
    category: 'Базы данных'
  },
  {
    id: '238534',
    title: 'Frontend разработка',
    description: 'Современная frontend разработка: HTML, CSS, JavaScript, React. Создание адаптивных и интерактивных веб-приложений.',
    stepikUrl: 'https://stepik.org/a/238534',
    price: 0,
    studentsCount: 190,
    rating: 4.9,
    category: 'Frontend'
  }
]

export default function StepikCoursesPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="md:flex md:items-center md:justify-between">
              <div className="flex-1 min-w-0">
                <h1 className="text-3xl font-bold leading-tight text-gray-900">
                  Курсы на Stepik
                </h1>
                <p className="mt-2 text-sm text-gray-600">
                  Курсы от преподавателя Дуплей Максима Игоревича
                </p>
              </div>
              <div className="mt-4 flex md:mt-0 md:ml-4">
                <a
                  href="https://stepik.org/users/150943726/teach"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Профиль на Stepik
                </a>
              </div>
            </div>
          </div>
        </header>

        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              {/* Фильтры */}
              <div className="bg-white shadow rounded-lg p-4 mb-6">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <input
                    type="text"
                    placeholder="Поиск по курсам..."
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  />
                  <select
                    id="category"
                    name="category"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    aria-label="Категория курса"
                  >
                    <option value="">Все категории</option>
                    <option value="java">Java</option>
                    <option value="python">Python</option>
                    <option value="android">Android</option>
                    <option value="devops">DevOps</option>
                    <option value="database">Базы данных</option>
                    <option value="frontend">Frontend</option>
                  </select>
                  <select
                    id="sort"
                    name="sort"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    aria-label="Сортировка"
                  >
                    <option value="popular">По популярности</option>
                    <option value="rating">По рейтингу</option>
                    <option value="newest">Сначала новые</option>
                  </select>
                  <select
                    id="price"
                    name="price"
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    aria-label="Цена"
                  >
                    <option value="">Любая цена</option>
                    <option value="free">Бесплатные</option>
                    <option value="paid">Платные</option>
                  </select>
                </div>
              </div>

              {/* Статистика */}
              <div className="bg-white shadow rounded-lg p-6 mb-6">
                <dl className="grid grid-cols-1 gap-5 sm:grid-cols-4">
                  <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Всего курсов
                    </dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">
                      {stepikCourses.length}
                    </dd>
                  </div>
                  <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Всего учеников
                    </dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">
                      {stepikCourses.reduce((sum, course) => sum + course.studentsCount, 0)}
                    </dd>
                  </div>
                  <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Средний рейтинг
                    </dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">
                      {(stepikCourses.reduce((sum, course) => sum + course.rating, 0) / stepikCourses.length).toFixed(1)}
                    </dd>
                  </div>
                  <div className="px-4 py-5 bg-gray-50 shadow rounded-lg overflow-hidden sm:p-6">
                    <dt className="text-sm font-medium text-gray-500 truncate">
                      Бесплатных курсов
                    </dt>
                    <dd className="mt-1 text-3xl font-semibold text-gray-900">
                      {stepikCourses.filter(course => course.price === 0).length}
                    </dd>
                  </div>
                </dl>
              </div>

              {/* Список курсов */}
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {stepikCourses.map(course => (
                  <StepikCourseCard
                    key={course.id}
                    {...course}
                  />
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}