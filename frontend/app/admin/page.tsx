'use client'

import { useState } from 'react'
import { BarChart, Users, BookOpen, TrendingUp, AlertCircle, Filter, Download } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'

interface User {
  id: number
  name: string
  email: string
  role: 'student' | 'mentor' | 'admin'
  joinDate: string
  status: 'active' | 'inactive' | 'suspended'
  courses: number
  revenue?: number
}

interface Course {
  id: number
  title: string
  instructor: string
  students: number
  revenue: number
  rating: number
  status: 'published' | 'draft' | 'archived'
}

interface Report {
  month: string
  revenue: number
  students: number
  sessions: number
  growth: number
}

interface StatCardProps {
  label: string
  value: string
  change: string
  icon: React.ComponentType<{ className?: string }>
  bgColor: string
  iconColor: string
  borderColor: string
}

// Helper component for dynamic progress bars
function DynamicProgressBar({ percentage, className }: { percentage: number; className: string }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2" data-progress={percentage}>
      <div
        className={`h-2 rounded-full transition-all ${className}`}
        data-width={percentage}
      />
    </div>
  )
}

export default function AdminDashboard() {
  const [activeTab, setActiveTab] = useState('overview')
  const [selectedRole, setSelectedRole] = useState('all')
  const [showFilters, setShowFilters] = useState(false)

  const dashboardStats = [
    {
      label: 'Всего пользователей',
      value: '12,847',
      change: '+12.5%',
      icon: Users,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200'
    },
    {
      label: 'Активных сессий',
      value: '1,284',
      change: '+8.2%',
      icon: BookOpen,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200'
    },
    {
      label: 'Доход (месяц)',
      value: '₽2,847,500',
      change: '+24.3%',
      icon: TrendingUp,
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200'
    },
    {
      label: 'Жалобы',
      value: '23',
      change: '+5',
      icon: AlertCircle,
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      borderColor: 'border-orange-200'
    }
  ]

  const mockUsers: User[] = [
    { id: 1, name: 'Максим Иванов', email: 'maksim@example.com', role: 'student', joinDate: '2025-01-15', status: 'active', courses: 3 },
    { id: 2, name: 'Иван Петров', email: 'ivan@example.com', role: 'mentor', joinDate: '2024-12-01', status: 'active', revenue: 45000, courses: 5 },
    { id: 3, name: 'Елена Смирнова', email: 'elena@example.com', role: 'student', joinDate: '2025-02-20', status: 'active', courses: 1 },
    { id: 4, name: 'Петр Козлов', email: 'petr@example.com', role: 'mentor', joinDate: '2025-01-05', status: 'inactive', revenue: 12000, courses: 2 },
    { id: 5, name: 'Анна Волкова', email: 'anna@example.com', role: 'student', joinDate: '2025-02-10', status: 'suspended', courses: 0 }
  ]

  const mockCourses: Course[] = [
    { id: 1, title: 'React Advanced Patterns', instructor: 'Иван Петров', students: 234, revenue: 125000, rating: 4.8, status: 'published' },
    { id: 2, title: 'Node.js Deep Dive', instructor: 'Петр Аксенов', students: 156, revenue: 89000, rating: 4.7, status: 'published' },
    { id: 3, title: 'System Design Mastery', instructor: 'Дмитрий Волков', students: 89, revenue: 52000, rating: 4.9, status: 'published' },
    { id: 4, title: 'Frontend Testing Best Practices', instructor: 'Мария Сидорова', students: 0, revenue: 0, rating: 0, status: 'draft' },
    { id: 5, title: 'JavaScript ES6+ Complete Guide', instructor: 'Иван Петров', students: 412, revenue: 187000, rating: 4.6, status: 'published' }
  ]

  const monthlyReports: Report[] = [
    { month: 'Январь', revenue: 1250000, students: 8900, sessions: 2340, growth: 15 },
    { month: 'Февраль', revenue: 1580000, students: 10200, sessions: 2890, growth: 18 },
    { month: 'Март', revenue: 2120000, students: 12850, sessions: 3450, growth: 26 },
    { month: 'Апрель', revenue: 2420000, students: 14200, sessions: 3890, growth: 14 }
  ]

  const StatCard = ({ label, value, change, icon: Icon, bgColor, iconColor, borderColor }: StatCardProps) => (
    <Card className={`${bgColor} border-l-4 ${borderColor}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{label}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          <p className="text-green-600 text-xs font-semibold mt-1">{change}</p>
        </div>
        <Icon className={`${iconColor} w-12 h-12 opacity-20`} />
      </div>
    </Card>
  )

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Заголовок */}
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold mb-4">Админ панель</h1>
          <p className="text-indigo-100 text-lg">
            Управление платформой и аналитика
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {/* Основные показатели */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardStats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        {/* Вкладки */}
        <div className="mb-8 border-b border-gray-200">
          <div className="flex flex-wrap gap-4">
            {[
              { id: 'overview', label: 'Обзор' },
              { id: 'users', label: 'Пользователи' },
              { id: 'courses', label: 'Курсы' },
              { id: 'reports', label: 'Отчеты' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-2 border-b-2 font-medium transition-colors ${
                  activeTab === tab.id
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        {/* Содержимое вкладок */}

        {/* Обзор */}
        {activeTab === 'overview' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* График доходов */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <TrendingUp size={20} className="text-indigo-600" />
                <span>Ежемесячный доход</span>
              </h3>
              <div className="space-y-4">
                {monthlyReports.map(report => (
                  <div key={report.month}>
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-gray-700">{report.month}</span>
                      <span className="text-sm font-bold text-gray-900">₽{(report.revenue / 1000000).toFixed(2)}M</span>
                    </div>
                    <DynamicProgressBar percentage={(report.revenue / 2500000) * 100} className="bg-indigo-600" />
                  </div>
                ))}
              </div>
            </Card>

            {/* Статистика активности */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <BarChart size={20} className="text-indigo-600" />
                <span>Активность пользователей</span>
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Новые пользователи</span>
                    <span className="text-sm font-bold text-gray-900">1,240</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-green-600 h-2 rounded-full progress-78" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Активные сессии</span>
                    <span className="text-sm font-bold text-gray-900">1,284</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-600 h-2 rounded-full progress-85" />
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Завершенные курсы</span>
                    <span className="text-sm font-bold text-gray-900">348</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-purple-600 h-2 rounded-full progress-65" />
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {/* Пользователи */}
        {activeTab === 'users' && (
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold text-gray-900 text-lg">Управление пользователями</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                  title="Фильтры"
                >
                  <Filter size={18} />
                  <span>Фильтры</span>
                </button>
                <button
                  className="flex items-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
                  title="Экспортировать"
                >
                  <Download size={18} />
                  <span>Экспорт</span>
                </button>
              </div>
            </div>

            {/* Фильтры */}
            {showFilters && (
              <div className="mb-6 pb-6 border-b border-gray-200 flex flex-wrap gap-4">
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  title="Выберите роль"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="all">Все роли</option>
                  <option value="student">Студент</option>
                  <option value="mentor">Ментор</option>
                  <option value="admin">Администратор</option>
                </select>
                <select
                  title="Выберите статус"
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option>Все статусы</option>
                  <option>Активные</option>
                  <option>Неактивные</option>
                  <option>Заблокированные</option>
                </select>
              </div>
            )}

            {/* Таблица пользователей */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50 border-b border-gray-200">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Имя</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Email</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Роль</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Статус</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Присоединился</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Действия</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {mockUsers.map(user => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 text-sm font-medium text-gray-900">{user.name}</td>
                      <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                      <td className="px-6 py-4 text-sm">
                        <Badge variant={user.role === 'mentor' ? 'success' : user.role === 'admin' ? 'warning' : 'info'}>
                          {user.role === 'student' ? 'Студент' : user.role === 'mentor' ? 'Ментор' : 'Администратор'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm">
                        <Badge
                          variant={
                            user.status === 'active'
                              ? 'success'
                              : user.status === 'inactive'
                              ? 'warning'
                              : 'danger'
                          }
                        >
                          {user.status === 'active' ? 'Активен' : user.status === 'inactive' ? 'Неактивен' : 'Заблокирован'}
                        </Badge>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-600">{user.joinDate}</td>
                      <td className="px-6 py-4 text-sm">
                        <button className="text-indigo-600 hover:text-indigo-700 font-medium">Редактировать</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        )}

        {/* Курсы */}
        {activeTab === 'courses' && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {mockCourses.map(course => (
              <Card key={course.id}>
                <div className="flex items-start justify-between mb-3">
                  <h3 className="font-semibold text-gray-900 text-lg flex-1">{course.title}</h3>
                  <Badge
                    variant={course.status === 'published' ? 'success' : course.status === 'draft' ? 'warning' : 'info'}
                  >
                    {course.status === 'published' ? 'Опубликован' : course.status === 'draft' ? 'Черновик' : 'Архивирован'}
                  </Badge>
                </div>
                <p className="text-sm text-gray-600 mb-4">Инструктор: {course.instructor}</p>

                <div className="space-y-3 py-4 border-t border-b border-gray-200">
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Студентов:</span>
                    <span className="font-semibold text-gray-900">{course.students}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Доход:</span>
                    <span className="font-semibold text-gray-900">₽{course.revenue.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span className="text-gray-600">Рейтинг:</span>
                    <span className="font-semibold text-gray-900">
                      {course.rating > 0 ? `${course.rating} ⭐` : 'Нет рейтинга'}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4">
                  <button className="text-indigo-600 hover:text-indigo-700 font-medium text-sm">Редактировать</button>
                  <button className="text-red-600 hover:text-red-700 font-medium text-sm">Удалить</button>
                </div>
              </Card>
            ))}
          </div>
        )}

        {/* Отчеты */}
        {activeTab === 'reports' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Детальная таблица */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6">Ежемесячные показатели</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-gray-50 border-b border-gray-200">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">Месяц</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">Доход</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-600">Студенты</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {monthlyReports.map(report => (
                      <tr key={report.month}>
                        <td className="px-4 py-3 text-sm font-medium text-gray-900">{report.month}</td>
                        <td className="px-4 py-3 text-sm text-gray-600">₽{(report.revenue / 1000000).toFixed(2)}M</td>
                        <td className="px-4 py-3 text-sm text-gray-600">{report.students.toLocaleString()}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>

            {/* Статистика */}
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6">Итоговая статистика</h3>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg border border-blue-200">
                  <p className="text-sm text-gray-600">Общий доход</p>
                  <p className="text-3xl font-bold text-blue-600 mt-2">₽7,370,500</p>
                  <p className="text-xs text-blue-600 mt-1">+18% за последний период</p>
                </div>
                <div className="p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg border border-green-200">
                  <p className="text-sm text-gray-600">Всего студентов</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">46,250</p>
                  <p className="text-xs text-green-600 mt-1">+22% за последний период</p>
                </div>
                <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                  <p className="text-sm text-gray-600">Средняя оценка курса</p>
                  <p className="text-3xl font-bold text-purple-600 mt-2">4.75 ⭐</p>
                  <p className="text-xs text-purple-600 mt-1">На основе 12,847 рецензий</p>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
}
