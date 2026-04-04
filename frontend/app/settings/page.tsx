'use client'

import { useState } from 'react'
import { useToast } from '@/hooks/useToast'
import { logger } from '@/lib/utils/logger'

export default function SettingsPage() {
  const toast = useToast()
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState({
    // General
    language: 'ru',
    timezone: 'Europe/Moscow',
    emailNotifications: true,
    pushNotifications: true,

    // Privacy
    profileVisibility: 'public',
    showOnlineStatus: true,
    showLastSeen: true,

    // Security
    twoFactorEnabled: false,
    sessionsLimit: 5,
  })

  const handleSave = async () => {
    try {
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      })

      if (response.ok) {
        toast.success('Настройки сохранены')
      } else {
        toast.error('Ошибка сохранения')
      }
    } catch (error) {
      logger.error('Save settings error', error)
      toast.error('Ошибка сохранения настроек')
    }
  }

  interface TabButtonProps {
    id: string
    label: string
    icon: React.ReactNode
  }

  const TabButton = ({ id, label, icon }: TabButtonProps) => (
    <button
      onClick={() => setActiveTab(id)}
      className={`px-4 py-2 rounded-lg font-medium transition-colors ${
        activeTab === id
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
      }`}
    >
      {icon} {label}
    </button>
  )

  interface ToggleProps {
    enabled: boolean
    onChange: (val: boolean) => void
  }

  const Toggle = ({ enabled, onChange }: ToggleProps) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`relative w-12 h-6 rounded-full transition-colors ${
        enabled ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'
      }`}
    >
      <span
        className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-transform ${
          enabled ? 'left-7' : 'left-1'
        }`}
      />
    </button>
  )

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          ⚙️ Настройки
        </h1>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          <TabButton id="general" label="Основные" icon="🔧" />
          <TabButton id="privacy" label="Приватность" icon="🔒" />
          <TabButton id="security" label="Безопасность" icon="🛡" />
          <TabButton id="notifications" label="Уведомления" icon="🔔" />
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6">
          {/* General Settings */}
          {activeTab === 'general' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                🔧 Основные настройки
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Язык
                  </label>
                  <select
                    value={settings.language}
                    onChange={(e) => setSettings({ ...settings, language: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                    <option value="zh">中文</option>
                    <option value="he">עברית</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Часовой пояс
                  </label>
                  <select
                    value={settings.timezone}
                    onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="Europe/Moscow">Москва (UTC+3)</option>
                    <option value="Europe/Kiev">Киев (UTC+2)</option>
                    <option value="Asia/Almaty">Алматы (UTC+5)</option>
                    <option value="Asia/Yekaterinburg">Екатеринбург (UTC+5)</option>
                    <option value="Asia/Vladivostok">Владивосток (UTC+10)</option>
                  </select>
                </div>
              </div>
            </>
          )}

          {/* Privacy Settings */}
          {activeTab === 'privacy' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                🔒 Настройки приватности
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Видимость профиля</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Кто может видеть ваш профиль</p>
                  </div>
                  <select
                    value={settings.profileVisibility}
                    onChange={(e) => setSettings({ ...settings, profileVisibility: e.target.value })}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="public">Все</option>
                    <option value="students">Только студенты</option>
                    <option value="mentors">Только менторы</option>
                    <option value="private">Приватный</option>
                  </select>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Показывать статус онлайн</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Другие видят, когда вы онлайн</p>
                  </div>
                  <Toggle
                    enabled={settings.showOnlineStatus}
                    onChange={(v: boolean) => setSettings({ ...settings, showOnlineStatus: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Показывать «Был(а)»</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Другие видят, когда вы последний раз были онлайн</p>
                  </div>
                  <Toggle
                    enabled={settings.showLastSeen}
                    onChange={(v: boolean) => setSettings({ ...settings, showLastSeen: v })}
                  />
                </div>
              </div>
            </>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                🛡 Настройки безопасности
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Двухфакторная аутентификация</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Дополнительная защита аккаунта</p>
                  </div>
                  <Toggle
                    enabled={settings.twoFactorEnabled}
                    onChange={(v: boolean) => setSettings({ ...settings, twoFactorEnabled: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Лимит активных сессий</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Максимальное количество одновременных сессий</p>
                  </div>
                  <select
                    value={settings.sessionsLimit}
                    onChange={(e) => setSettings({ ...settings, sessionsLimit: Number(e.target.value) })}
                    className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value={3}>3</option>
                    <option value={5}>5</option>
                    <option value={10}>10</option>
                    <option value={999}>Без лимита</option>
                  </select>
                </div>

                <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
                  <button className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium transition-colors">
                    🚫 Завершить все другие сессии
                  </button>
                </div>
              </div>
            </>
          )}

          {/* Notifications Settings */}
          {activeTab === 'notifications' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                🔔 Настройки уведомлений
              </h2>
              
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Email уведомления</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Получать уведомления на email</p>
                  </div>
                  <Toggle
                    enabled={settings.emailNotifications}
                    onChange={(v: boolean) => setSettings({ ...settings, emailNotifications: v })}
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Push уведомления</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Получать push уведомления в браузере</p>
                  </div>
                  <Toggle
                    enabled={settings.pushNotifications}
                    onChange={(v: boolean) => setSettings({ ...settings, pushNotifications: v })}
                  />
                </div>
              </div>
            </>
          )}
        </div>

        {/* Save Button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl font-medium transition-colors shadow-lg"
          >
            💾 Сохранить настройки
          </button>
        </div>
      </div>
    </div>
  )
}
