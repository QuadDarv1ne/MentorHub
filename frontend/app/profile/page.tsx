'use client'

import { useState, useEffect } from 'react'
import { User, Briefcase, Save, X, Camera, Eye, EyeOff, LogOut } from 'lucide-react'
import { useAuth } from '@/lib/hooks/useAuth'

interface ProfileData {
  firstName: string
  lastName: string
  email: string
  phone: string
  location: string
  specialization: string
  bio: string
  avatar: string
}

export default function ProfilePage() {
  // Защита маршрута
  const { getUserData } = useAuth()
  
  const [activeTab, setActiveTab] = useState<'profile' | 'settings' | 'security'>('profile')
  const [isEditing, setIsEditing] = useState(false)
  const [showPassword] = useState(false)
  const [loading, setLoading] = useState(true)
  const [formErrors, setFormErrors] = useState<Partial<ProfileData>>({})
  
  // Получаем данные пользователя из localStorage
  const userData = getUserData()
  
  const [formData, setFormData] = useState<ProfileData>({
    firstName: (userData?.name as string) || 'Пользователь',
    lastName: '',
    email: (userData?.email as string) || '',
    phone: '',
    location: 'Москва, Россия',
    specialization: 'React & Node.js разработчик',
    bio: 'Опытный разработчик с 5+ годами опыта в веб-разработке. Специализируюсь на создании высоконагруженных приложений.',
    avatar: '👨‍💼'
  })

  useEffect(() => {
    // Имитация загрузки данных
    const timer = setTimeout(() => {
      setLoading(false)
    }, 500)
    
    return () => clearTimeout(timer)
  }, [])

  const validateForm = () => {
    const errors: Partial<ProfileData> = {}
    if (!formData.firstName.trim()) errors.firstName = 'Имя не заполнено'
    if (!formData.lastName.trim()) errors.lastName = 'Фамилия не заполнена'
    if (!formData.email.includes('@')) errors.email = 'Некорректный email'
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const handleSave = () => {
    if (validateForm()) {
      setIsEditing(false)
    }
  }

  const handleInputChange = (field: keyof ProfileData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    if (formErrors[field]) {
      setFormErrors(prev => ({
        ...prev,
        [field]: undefined
      }))
    }
  }

  const stats = [
    { label: 'Завершено сессий', value: '152' },
    { label: 'Часов обучено', value: '456' },
    { label: 'Средний рейтинг', value: '4.9' },
    { label: 'Благодарственных писем', value: '42' }
  ]

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Мой профиль</h1>
          <p className="text-gray-600 mt-2">Управляйте информацией о своём профиле и настройками аккаунта</p>
        </div>

        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('profile')}
                className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'profile'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <User className="inline-block mr-2 h-4 w-4" />
                Профиль
              </button>
              <button
                onClick={() => setActiveTab('settings')}
                className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'settings'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Briefcase className="inline-block mr-2 h-4 w-4" />
                Настройки
              </button>
              <button
                onClick={() => setActiveTab('security')}
                className={`flex-1 px-6 py-3 font-medium text-sm transition-colors ${
                  activeTab === 'security'
                    ? 'border-b-2 border-indigo-600 text-indigo-600'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                🔒 Безопасность
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div className="flex items-center space-x-6">
                  <div className="relative">
                    <div className="w-24 h-24 bg-gradient-to-br from-indigo-400 to-indigo-600 rounded-full flex items-center justify-center text-5xl shadow-lg">
                      {formData.avatar}
                    </div>
                    {isEditing && (
                      <button className="absolute bottom-0 right-0 bg-white rounded-full p-2 shadow-lg hover:bg-gray-50" title="Загрузить фото">
                        <Camera size={20} className="text-indigo-600" />
                      </button>
                    )}
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900">{formData.firstName} {formData.lastName}</h2>
                    <p className="text-gray-600">{formData.specialization}</p>
                    {!isEditing && (
                      <button
                        onClick={() => setIsEditing(true)}
                        className="mt-2 text-indigo-600 hover:text-indigo-700 font-medium"
                      >
                        Редактировать профиль
                      </button>
                    )}
                  </div>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {stats.map((stat, idx) => (
                    <div key={idx} className="bg-gray-50 rounded-lg p-4 text-center">
                      <p className="text-2xl font-bold text-indigo-600">{stat.value}</p>
                      <p className="text-sm text-gray-600 mt-1">{stat.label}</p>
                    </div>
                  ))}
                </div>

                {isEditing && (
                  <div className="space-y-4 border-t border-gray-200 pt-6">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Имя</label>
                        <input
                          type="text"
                          title="Введите ваше имя"
                          value={formData.firstName}
                          onChange={(e) => handleInputChange('firstName', e.target.value)}
                          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                            formErrors.firstName ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                        {formErrors.firstName && (
                          <p className="text-sm text-red-600 mt-1">{formErrors.firstName}</p>
                        )}
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Фамилия</label>
                        <input
                          type="text"
                          title="Введите вашу фамилию"
                          value={formData.lastName}
                          onChange={(e) => handleInputChange('lastName', e.target.value)}
                          className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                            formErrors.lastName ? 'border-red-500' : 'border-gray-300'
                          }`}
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input
                        type="email"
                        title="Введите ваш email"
                        value={formData.email}
                        onChange={(e) => handleInputChange('email', e.target.value)}
                        className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 ${
                          formErrors.email ? 'border-red-500' : 'border-gray-300'
                        }`}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Телефон</label>
                        <input
                          type="tel"
                          title="Введите ваш номер телефона"
                          value={formData.phone}
                          onChange={(e) => handleInputChange('phone', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Местоположение</label>
                        <input
                          type="text"
                          title="Введите ваше местоположение"
                          value={formData.location}
                          onChange={(e) => handleInputChange('location', e.target.value)}
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Специализация</label>
                      <input
                        type="text"
                        title="Введите вашу специализацию"
                        value={formData.specialization}
                        onChange={(e) => handleInputChange('specialization', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">О себе</label>
                      <textarea
                        title="Расскажите о себе"
                        value={formData.bio}
                        onChange={(e) => handleInputChange('bio', e.target.value)}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
                        rows={4}
                      />
                    </div>

                    <div className="flex space-x-3 pt-4">
                      <button
                        onClick={handleSave}
                        className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                      >
                        <Save size={18} className="mr-2" />
                        Сохранить
                      </button>
                      <button
                        onClick={() => setIsEditing(false)}
                        className="flex-1 bg-gray-200 hover:bg-gray-300 text-gray-900 font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center"
                      >
                        <X size={18} className="mr-2" />
                        Отмена
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'settings' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Предпочтения</h3>
                  <div className="space-y-3">
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
                      <span className="text-gray-700">Получать уведомления по email</span>
                    </label>
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" defaultChecked className="w-4 h-4 rounded" />
                      <span className="text-gray-700">Получать уведомления о новых сообщениях</span>
                    </label>
                    <label className="flex items-center space-x-3">
                      <input type="checkbox" className="w-4 h-4 rounded" />
                      <span className="text-gray-700">Публичный профиль</span>
                    </label>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Язык и регион</h3>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">Язык</label>
                      <select title="Выберите язык" className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500">
                        <option>Русский</option>
                        <option>English</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Пароль</h3>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Текущий пароль</label>
                      <div className="relative">
                        <input
                          type={showPassword ? 'text' : 'password'}
                          placeholder="••••••••"
                          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                        />
                        <button className="absolute right-3 top-2.5 text-gray-500">
                          {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Новый пароль</label>
                      <input
                        type="password"
                        placeholder="••••••••"
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
                      />
                    </div>
                    <button className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded-lg transition-colors">
                      Изменить пароль
                    </button>
                  </div>
                </div>

                <div className="border-t border-gray-200 pt-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 text-red-600">Опасная зона</h3>
                  <button className="w-full bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg transition-colors flex items-center justify-center">
                    <LogOut size={18} className="mr-2" />
                    Выйти из аккаунта
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
