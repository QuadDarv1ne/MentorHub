'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/hooks/useToast'
import { logger } from '@/lib/utils/logger'
import { getProfile, updateProfile, type UserProfile } from '@/lib/api/profile'

export default function ProfilePage() {
  const { user, token } = useAuth()
  const toast = useToast()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    fullName: '',
    bio: '',
    skills: ''
  })

  const fetchProfile = useCallback(async () => {
    try {
      const data = await getProfile()
      setProfile(data)
      setError(null)
      setFormData({
        fullName: data.fullName || '',
        bio: data.bio || '',
        skills: data.skills?.join(', ') || ''
      })
      return
    } catch (error) {
      logger.error('Fetch profile error', error)
    }

    // Fallback: use data from auth hook if API is unavailable
    if (user) {
      const u = user as unknown as Record<string, unknown>
      setProfile({
        id: user.id || 0,
        username: user.email?.split('@')[0] || '',
        email: user.email || '',
        fullName: (u.fullName as string) || user.email || '',
        avatar: u.avatar as string | undefined,
        role: user.role || 'student',
        bio: u.bio as string | undefined,
        skills: (u.skills as string[]) || [],
        rating: (u.rating as number) || 0,
        totalSessions: (u.totalSessions as number) || 0,
        completedSessions: (u.completedSessions as number) || 0,
        joinDate: (u.joinDate as string) || '',
        isOnline: (u.isOnline as boolean) ?? true,
        lastSeen: u.lastSeen as string | undefined,
      })
      setFormData({
        fullName: (u.fullName as string) || '',
        bio: (u.bio as string) || '',
        skills: ((u.skills as string[])?.join(', ')) || ''
      })
      setError('Не удалось загрузить профиль с сервера. Показаны локальные данные.')
    } else {
      setError('Не удалось загрузить профиль')
    }
  }, [user])

  useEffect(() => {
    fetchProfile()
  }, [fetchProfile])

  const handleSave = async () => {
    try {
      await updateProfile({
        full_name: formData.fullName,
        bio: formData.bio,
        skills: formData.skills.split(',').map(s => s.trim()).filter(Boolean),
      })
      toast.success('Профиль сохранён')
      setIsEditing(false)
      fetchProfile()
    } catch (error) {
      logger.error('Save profile error', error)
      toast.error('Ошибка сохранения профиля')
    }
  }

  const completionPercent = profile && profile.totalSessions > 0
    ? Math.round((profile.completedSessions / profile.totalSessions) * 100)
    : 0

  if (error && !profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={fetchProfile}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
          >
            Повторить
          </button>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка профиля...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Header Card */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg overflow-hidden mb-6">
          {/* Cover */}
          <div className="h-32 bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500"></div>

          {/* Profile Info */}
          <div className="px-6 pb-6">
            <div className="flex flex-col sm:flex-row items-center sm:items-end -mt-12 gap-4">
              {/* Avatar */}
              <div className="relative">
                <div className="w-24 h-24 rounded-full bg-gradient-to-br from-indigo-400 to-purple-500 flex items-center justify-center text-4xl border-4 border-white dark:border-gray-800 shadow-lg overflow-hidden">
                  {profile.avatar ? (
                    <img
                      src={profile.avatar}
                      alt={profile.fullName}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span>{profile.fullName?.charAt(0).toUpperCase() || '👤'}</span>
                  )}
                </div>
                {profile.isOnline && (
                  <span className="absolute bottom-1 right-1 w-5 h-5 bg-green-500 border-2 border-white rounded-full"></span>
                )}
              </div>

              {/* Name & Role */}
              <div className="flex-1 text-center sm:text-left">
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {profile.fullName || profile.username}
                </h1>
                <p className="text-gray-600 dark:text-gray-400 capitalize">{profile.role}</p>
                <div className="flex items-center justify-center sm:justify-start gap-4 mt-2">
                  <span className="text-yellow-600 dark:text-yellow-400 font-semibold">
                    ⭐ {profile.rating > 0 ? profile.rating.toFixed(1) : 'N/A'}
                  </span>
                  <span className="text-gray-600 dark:text-gray-400">
                    {profile.totalSessions} сессий
                  </span>
                  <span className="text-green-600 dark:text-green-400">
                    ✓ {profile.completedSessions} завершено
                  </span>
                </div>
              </div>

              {/* Edit Button */}
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
              >
                {isEditing ? 'Отмена' : 'Редактировать'}
              </button>
            </div>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl p-4 mb-6">
            <p className="text-yellow-800 dark:text-yellow-300 text-sm">{error}</p>
          </div>
        )}

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 text-center">
            <p className="text-3xl font-bold text-indigo-600">{profile.totalSessions}</p>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Всего сессий</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 text-center">
            <p className="text-3xl font-bold text-green-600">{profile.completedSessions}</p>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Завершено</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 text-center">
            <p className="text-3xl font-bold text-yellow-600">{profile.rating > 0 ? profile.rating.toFixed(1) : 'N/A'}</p>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Рейтинг</p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-4 text-center">
            <p className="text-3xl font-bold text-purple-600">
              {completionPercent}%
            </p>
            <p className="text-gray-600 dark:text-gray-400 text-sm">Успех</p>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid md:grid-cols-3 gap-6">
          {/* Left Column - Info */}
          <div className="md:col-span-2 space-y-6">
            {/* About */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                📝 О себе
              </h2>
              {isEditing ? (
                <textarea
                  value={formData.bio}
                  onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white resize-none"
                  rows={4}
                  placeholder="Расскажите о себе..."
                />
              ) : (
                <p className="text-gray-600 dark:text-gray-400">
                  {profile.bio || 'Нет информации'}
                </p>
              )}
            </div>

            {/* Skills */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">
                🛠 Навыки
              </h2>
              {isEditing ? (
                <input
                  type="text"
                  value={formData.skills}
                  onChange={(e) => setFormData({ ...formData, skills: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  placeholder="Навыки через запятую (JavaScript, Python, React...)"
                />
              ) : (
                <div className="flex flex-wrap gap-2">
                  {profile.skills && profile.skills.length > 0 ? (
                    profile.skills.map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 rounded-full text-sm font-medium"
                      >
                        {skill}
                      </span>
                    ))
                  ) : (
                    <p className="text-gray-600 dark:text-gray-400">Навыки не указаны</p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right Column - Activity */}
          <div className="space-y-6">
            {/* Status */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                🟢 Статус
              </h2>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className={`w-3 h-3 rounded-full ${profile.isOnline ? 'bg-green-500' : 'bg-gray-400'}`}></span>
                  <span className="text-gray-700 dark:text-gray-300">
                    {profile.isOnline ? 'Онлайн' : 'Офлайн'}
                  </span>
                </div>
                {profile.lastSeen && (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Был(а) {profile.lastSeen}
                  </p>
                )}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6">
              <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                ⚡ Действия
              </h2>
              <div className="space-y-2">
                <a href="/sessions" className="block px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-center font-medium transition-colors">
                  📅 Мои сессии
                </a>
                <a href="/messages" className="block px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-center font-medium transition-colors">
                  💬 Сообщения
                </a>
                <a href="/settings" className="block px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg text-center font-medium transition-colors">
                  ⚙️ Настройки
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Save/Cancel Buttons - Inline */}
        {isEditing && (
          <div className="flex justify-end gap-4 mt-6">
            <button
              onClick={() => {
                setIsEditing(false)
                setFormData({
                  fullName: profile.fullName || '',
                  bio: profile.bio || '',
                  skills: profile.skills?.join(', ') || ''
                })
              }}
              className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white rounded-xl font-medium transition-colors"
            >
              Отмена
            </button>
            <button
              onClick={handleSave}
              className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-colors"
            >
              Сохранить
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
