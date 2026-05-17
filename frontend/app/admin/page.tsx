'use client'

import { useState, useEffect, Suspense, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import {
  BarChart, Users, BookOpen, TrendingUp, AlertCircle,
  Filter, Download, Search, ChevronLeft, ChevronRight,
  Shield, UserCheck, UserX, RefreshCw, Loader2, Eye
} from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import MonitoringDashboard from '@/components/MonitoringDashboard'
import {
  getAdminUsers,
  getPlatformStats,
  updateUserRole,
  updateUserStatus,
  type AdminUser,
  type AdminUserListResponse,
  type PlatformStats,
} from '@/lib/api/admin'

function DynamicProgressBar({ percentage, className }: { percentage: number; className: string }) {
  return (
    <div className="w-full bg-gray-200 rounded-full h-2">
      <div
        className={`h-2 rounded-full transition-all duration-500 ${className}`}
        style={{ width: `${Math.min(percentage, 100)}%` }}
      />
    </div>
  )
}

interface StatCardProps {
  label: string
  value: string
  change: string
  icon: React.ComponentType<{ className?: string }>
  bgColor: string
  iconColor: string
  borderColor: string
  loading?: boolean
}

function StatCard({ label, value, change, icon: Icon, bgColor, iconColor, borderColor, loading }: StatCardProps) {
  return (
    <Card className={`${bgColor} border-l-4 ${borderColor}`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-600 text-sm font-medium">{label}</p>
          {loading ? (
            <div className="h-8 w-24 bg-gray-200 animate-pulse rounded mt-2" />
          ) : (
            <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          )}
          <p className="text-green-600 text-xs font-semibold mt-1">{change}</p>
        </div>
        <Icon className={`${iconColor} w-12 h-12 opacity-20`} />
      </div>
    </Card>
  )
}

function formatNumber(n: number): string {
  if (n >= 1_000_000) return `₽${(n / 1_000_000).toFixed(1)}M`
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`
  return String(n)
}

export default function AdminDashboard() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState('overview')
  const [showFilters, setShowFilters] = useState(false)
  const [statsLoading, setStatsLoading] = useState(true)
  const [usersLoading, setUsersLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState<number | null>(null)

  const [stats, setStats] = useState<PlatformStats | null>(null)
  const [userData, setUserData] = useState<AdminUserListResponse | null>(null)
  const [page, setPage] = useState(1)
  const [roleFilter, setRoleFilter] = useState('')
  const [statusFilter, setStatusFilter] = useState('')
  const [searchQuery, setSearchQuery] = useState('')
  const [error, setError] = useState<string | null>(null)

  const pageSize = 10

  const fetchStats = useCallback(async () => {
    setStatsLoading(true)
    try {
      const data = await getPlatformStats()
      setStats(data)
    } catch {
      setStats(null)
    } finally {
      setStatsLoading(false)
    }
  }, [])

  const fetchUsers = useCallback(async () => {
    setUsersLoading(true)
    setError(null)
    try {
      const data = await getAdminUsers({
        page,
        page_size: pageSize,
        role: roleFilter || undefined,
        status: statusFilter || undefined,
        search: searchQuery || undefined,
      })
      setUserData(data)
    } catch {
      setError('Failed to load users')
      setUserData(null)
    } finally {
      setUsersLoading(false)
    }
  }, [page, roleFilter, statusFilter, searchQuery])

  useEffect(() => { fetchStats() }, [fetchStats])
  useEffect(() => { fetchUsers() }, [fetchUsers])

  const handleRoleChange = async (userId: number, newRole: string) => {
    setActionLoading(userId)
    try {
      await updateUserRole(userId, newRole)
      await fetchUsers()
    } catch {
      setError('Failed to update role')
    } finally {
      setActionLoading(null)
    }
  }

  const handleStatusToggle = async (userId: number, currentActive: boolean) => {
    setActionLoading(userId)
    try {
      await updateUserStatus(userId, !currentActive)
      await fetchUsers()
    } catch {
      setError('Failed to update status')
    } finally {
      setActionLoading(null)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    fetchUsers()
  }

  const dashboardStats = [
    {
      label: 'Всего пользователей',
      value: stats ? formatNumber(stats.total_users) : '—',
      change: stats ? `+${stats.new_users_today} сегодня` : '',
      icon: Users,
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-200',
      loading: statsLoading,
    },
    {
      label: 'Активных сессий',
      value: stats ? String(stats.active_sessions_now) : '—',
      change: stats ? `${stats.completed_sessions} завершено` : '',
      icon: BookOpen,
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-200',
      loading: statsLoading,
    },
    {
      label: 'Доход (всего)',
      value: stats ? `₽${formatNumber(stats.total_revenue)}` : '—',
      change: stats ? `${stats.total_enrollments} enrollments` : '',
      icon: TrendingUp,
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-200',
      loading: statsLoading,
    },
    {
      label: 'Рейтинг платформы',
      value: stats ? `${stats.avg_rating.toFixed(2)} ⭐` : '—',
      change: stats ? `${stats.total_reviews} отзывов` : '',
      icon: AlertCircle,
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      borderColor: 'border-orange-200',
      loading: statsLoading,
    },
  ]

  const roleLabel: Record<string, string> = {
    student: 'Студент',
    mentor: 'Ментор',
    admin: 'Администратор',
  }

  const roleColor: Record<string, 'success' | 'warning' | 'info'> = {
    student: 'info',
    mentor: 'success',
    admin: 'warning',
  }

  const statusLabel: Record<string, string> = {
    active: 'Активен',
    inactive: 'Неактивен',
  }

  const statusColor: Record<string, 'success' | 'warning' | 'danger'> = {
    active: 'success',
    inactive: 'danger',
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-gradient-to-br from-indigo-600 to-indigo-700 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-4">Админ панель</h1>
            <p className="text-indigo-100 text-lg">
              Управление платформой и аналитика
            </p>
          </div>
          <button
            onClick={() => { fetchStats(); fetchUsers() }}
            className="flex items-center space-x-2 px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition-colors text-white"
          >
            <RefreshCw size={18} />
            <span>Обновить</span>
          </button>
        </div>
      </div>

      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-3">
            <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
            <p className="text-sm text-red-800">{error}</p>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {dashboardStats.map((stat, index) => (
            <StatCard key={index} {...stat} />
          ))}
        </div>

        <div className="mb-8 border-b border-gray-200">
          <div className="flex flex-wrap gap-4">
            {[
              { id: 'overview', label: 'Обзор' },
              { id: 'users', label: 'Пользователи' },
              { id: 'monitoring', label: 'Мониторинг' },
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

        {activeTab === 'overview' && stats && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <Users size={20} className="text-indigo-600" />
                <span>Пользователи</span>
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium text-gray-700">Всего</span>
                  <span className="text-sm font-bold text-gray-900">{stats.total_users.toLocaleString()}</span>
                </div>
                <DynamicProgressBar percentage={(stats.active_users / Math.max(stats.total_users, 1)) * 100} className="bg-green-600" />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>{stats.active_users.toLocaleString()} активных</span>
                  <span>{(stats.active_users / Math.max(stats.total_users, 1) * 100).toFixed(0)}%</span>
                </div>
                <div className="grid grid-cols-3 gap-4 pt-4 border-t border-gray-200">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-blue-600">{stats.total_students.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">Студентов</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-green-600">{stats.total_mentors.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">Менторов</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-purple-600">{stats.total_admins}</p>
                    <p className="text-xs text-gray-500">Админов</p>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <BookOpen size={20} className="text-indigo-600" />
                <span>Курсы и сессии</span>
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Всего курсов</span>
                  <span className="font-semibold">{stats.total_courses}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Активных курсов</span>
                  <span className="font-semibold">{stats.active_courses}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Записей</span>
                  <span className="font-semibold">{stats.total_enrollments.toLocaleString()}</span>
                </div>
                <div className="border-t border-gray-200 pt-4">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-600">Всего сессий</span>
                    <span className="font-semibold">{stats.total_sessions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between mt-2">
                    <span className="text-sm text-gray-600">Завершено</span>
                    <span className="font-semibold text-green-600">{stats.completed_sessions.toLocaleString()}</span>
                  </div>
                  <div className="flex justify-between mt-2">
                    <span className="text-sm text-gray-600">Запланировано</span>
                    <span className="font-semibold text-blue-600">{stats.scheduled_sessions.toLocaleString()}</span>
                  </div>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <BarChart size={20} className="text-indigo-600" />
                <span>Отзывы и рейтинг</span>
              </h3>
              <div className="space-y-4">
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Всего отзывов</span>
                  <span className="font-semibold">{stats.total_reviews.toLocaleString()}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Средний рейтинг</span>
                  <span className="font-semibold text-yellow-600">{stats.avg_rating.toFixed(2)} ⭐</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-sm text-gray-600">Новые сегодня</span>
                  <span className="font-semibold text-blue-600">{stats.new_users_today}</span>
                </div>
              </div>
            </Card>

            <Card>
              <h3 className="font-semibold text-gray-900 mb-6 flex items-center space-x-2">
                <TrendingUp size={20} className="text-indigo-600" />
                <span>Доход</span>
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg border border-purple-200">
                  <p className="text-sm text-gray-600">Общий доход</p>
                  <p className="text-3xl font-bold text-purple-600 mt-2">
                    ₽{stats.total_revenue.toLocaleString()}
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-3 bg-blue-50 rounded-lg border border-blue-200 text-center">
                    <p className="text-lg font-bold text-blue-600">{stats.verified_users.toLocaleString()}</p>
                    <p className="text-xs text-gray-500">Верифицировано</p>
                  </div>
                  <div className="p-3 bg-green-50 rounded-lg border border-green-200 text-center">
                    <p className="text-lg font-bold text-green-600">{stats.active_sessions_now}</p>
                    <p className="text-xs text-gray-500">Активно сейчас</p>
                  </div>
                </div>
              </div>
            </Card>
          </div>
        )}

        {activeTab === 'overview' && !stats && !statsLoading && (
          <Card>
            <p className="text-gray-500 text-center py-8">
              Не удалось загрузить статистику. Проверьте подключение к API.
            </p>
          </Card>
        )}

        {activeTab === 'monitoring' && (
          <div className="mt-6">
            <Suspense fallback={<div className="text-center py-8">Загрузка мониторинга...</div>}>
              <MonitoringDashboard />
            </Suspense>
          </div>
        )}

        {activeTab === 'users' && (
          <Card>
            <div className="flex items-center justify-between mb-6">
              <h3 className="font-semibold text-gray-900 text-lg">Управление пользователями</h3>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowFilters(!showFilters)}
                  className="flex items-center space-x-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
                >
                  <Filter size={18} />
                  <span>Фильтры</span>
                </button>
              </div>
            </div>

            <form onSubmit={handleSearch} className="mb-6">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Поиск по имени или email..."
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />
              </div>
            </form>

            {showFilters && (
              <div className="mb-6 pb-6 border-b border-gray-200 flex flex-wrap gap-4">
                <select
                  value={roleFilter}
                  onChange={(e) => { setRoleFilter(e.target.value); setPage(1) }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Все роли</option>
                  <option value="student">Студент</option>
                  <option value="mentor">Ментор</option>
                  <option value="admin">Администратор</option>
                </select>
                <select
                  value={statusFilter}
                  onChange={(e) => { setStatusFilter(e.target.value); setPage(1) }}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">Все статусы</option>
                  <option value="active">Активные</option>
                  <option value="inactive">Неактивные</option>
                </select>
              </div>
            )}

            {usersLoading ? (
              <div className="flex items-center justify-center py-12">
                <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
              </div>
            ) : userData ? (
              <>
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Имя</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Email</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Роль</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Статус</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Регистрация</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-600 uppercase">Действия</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-200">
                      {userData.items.length === 0 ? (
                        <tr>
                          <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                            Пользователи не найдены
                          </td>
                        </tr>
                      ) : (
                        userData.items.map(user => (
                          <tr key={user.id} className="hover:bg-gray-50">
                            <td className="px-6 py-4">
                              <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 rounded-full bg-indigo-100 flex items-center justify-center">
                                  <span className="text-sm font-medium text-indigo-600">
                                    {(user.full_name || user.username || user.email)[0].toUpperCase()}
                                  </span>
                                </div>
                                <span className="text-sm font-medium text-gray-900">
                                  {user.full_name || user.username || user.email}
                                </span>
                              </div>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">{user.email}</td>
                            <td className="px-6 py-4 text-sm">
                              <select
                                value={user.role}
                                onChange={(e) => handleRoleChange(user.id, e.target.value)}
                                disabled={actionLoading === user.id}
                                className="text-sm border border-gray-300 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50"
                              >
                                <option value="student">Студент</option>
                                <option value="mentor">Ментор</option>
                                <option value="admin">Админ</option>
                              </select>
                            </td>
                            <td className="px-6 py-4 text-sm">
                              <Badge variant={statusColor[user.is_active ? 'active' : 'inactive']}>
                                {statusLabel[user.is_active ? 'active' : 'inactive']}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 text-sm text-gray-600">
                              {new Date(user.created_at).toLocaleDateString()}
                            </td>
                            <td className="px-6 py-4 text-sm">
                              <div className="flex items-center space-x-2">
                                <button
                                  onClick={() => router.push(`/admin/users/${user.id}`)}
                                  className="flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors"
                                  title="Посмотреть статистику"
                                >
                                  <Eye size={14} />
                                  <span>Статистика</span>
                                </button>
                                <button
                                  onClick={() => handleStatusToggle(user.id, user.is_active)}
                                  disabled={actionLoading === user.id}
                                  className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-colors disabled:opacity-50 ${
                                    user.is_active
                                      ? 'bg-red-50 text-red-600 hover:bg-red-100'
                                      : 'bg-green-50 text-green-600 hover:bg-green-100'
                                  }`}
                                  title={user.is_active ? 'Деактивировать' : 'Активировать'}
                                >
                                  {actionLoading === user.id ? (
                                    <Loader2 className="w-3 h-3 animate-spin" />
                                  ) : user.is_active ? (
                                    <UserX size={14} />
                                  ) : (
                                    <UserCheck size={14} />
                                  )}
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>

                {userData.total_pages > 1 && (
                  <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
                    <p className="text-sm text-gray-600">
                      Показано {((page - 1) * pageSize) + 1}–{Math.min(page * pageSize, userData.total)} из {userData.total}
                    </p>
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => setPage(p => Math.max(1, p - 1))}
                        disabled={page <= 1}
                        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronLeft size={18} />
                      </button>
                      {Array.from({ length: Math.min(userData.total_pages, 5) }, (_, i) => {
                        const start = Math.max(1, page - 2)
                        const pageNum = start + i
                        if (pageNum > userData.total_pages) return null
                        return (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum)}
                            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                              page === pageNum
                                ? 'bg-indigo-600 text-white'
                                : 'border border-gray-300 hover:bg-gray-50'
                            }`}
                          >
                            {pageNum}
                          </button>
                        )
                      })}
                      <button
                        onClick={() => setPage(p => Math.min(userData.total_pages, p + 1))}
                        disabled={page >= userData.total_pages}
                        className="p-2 rounded-lg border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        <ChevronRight size={18} />
                      </button>
                    </div>
                  </div>
                )}
              </>
            ) : (
              <p className="text-gray-500 text-center py-8">
                Не удалось загрузить пользователей. Проверьте подключение к API.
              </p>
            )}
          </Card>
        )}
      </div>
    </div>
  )
}
