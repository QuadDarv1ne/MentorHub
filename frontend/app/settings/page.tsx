'use client'

import { useState, useEffect, useCallback } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { useToast } from '@/hooks/useToast'
import { logger } from '@/lib/utils/logger'

// --- Sub-components defined outside render ---

interface TabButtonProps {
  id: string
  label: string
  icon: string
  active: boolean
  onClick: () => void
}

const TabButton = ({ id, label, icon, active, onClick }: TabButtonProps) => (
  <button
    onClick={onClick}
    role="tab"
    aria-selected={active}
    aria-controls={`panel-${id}`}
    id={`tab-${id}`}
    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
      active
        ? 'bg-indigo-600 text-white'
        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
    }`}
  >
    <span aria-hidden="true">{icon}</span> {label}
  </button>
)

interface ToggleProps {
  enabled: boolean
  onChange: (val: boolean) => void
  label: string
}

const Toggle = ({ enabled, onChange, label }: ToggleProps) => (
  <button
    onClick={() => onChange(!enabled)}
    role="switch"
    aria-checked={enabled}
    aria-label={label}
    className={`relative w-12 h-6 rounded-full transition-colors ${
      enabled ? 'bg-indigo-600' : 'bg-gray-300 dark:bg-gray-600'
    }`}
  >
    <span
      className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
        enabled ? 'left-7' : 'left-1'
      }`}
    />
  </button>
)

interface SettingsData {
  language: string
  timezone: string
  emailNotifications: boolean
  pushNotifications: boolean
  profileVisibility: string
  showOnlineStatus: boolean
  showLastSeen: boolean
  twoFactorEnabled: boolean
  sessionsLimit: number
}

const DEFAULT_SETTINGS: SettingsData = {
  language: 'ru',
  timezone: 'Europe/Moscow',
  emailNotifications: true,
  pushNotifications: true,
  profileVisibility: 'public',
  showOnlineStatus: true,
  showLastSeen: true,
  twoFactorEnabled: false,
  sessionsLimit: 5,
}

export default function SettingsPage() {
  const { token } = useAuth()
  const toast = useToast()
  const [activeTab, setActiveTab] = useState('general')
  const [settings, setSettings] = useState<SettingsData>(DEFAULT_SETTINGS)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [hasChanges, setHasChanges] = useState(false)

  useEffect(() => {
    fetchSettings()
  }, [])

  const fetchSettings = async () => {
    try {
      const response = await fetch('/api/settings', {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
      if (response.ok) {
        const data = await response.json()
        setSettings(data)
        return
      }
    } catch (error) {
      logger.error('Fetch settings error', error)
    }
    // Fallback: keep defaults, show error
    toast.error('Не удалось загрузить настройки с сервера')
  }

  const handleSave = useCallback(async () => {
    setIsSaving(true)
    try {
      const response = await fetch('/api/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify(settings)
      })

      if (response.ok) {
        toast.success('Настройки сохранены')
        setHasChanges(false)
      } else {
        toast.error('Ошибка сохранения')
      }
    } catch (error) {
      logger.error('Save settings error', error)
      toast.error('Ошибка сохранения настроек')
    } finally {
      setIsSaving(false)
    }
  }, [settings, token, toast])

  const updateSetting = <K extends keyof SettingsData>(key: K, value: SettingsData[K]) => {
    setSettings(prev => ({ ...prev, [key]: value }))
    setHasChanges(true)
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка настроек...</p>
        </div>
      </div>
    )
  }

  const tabs = [
    { id: 'general', label: 'Основные', icon: '🔧' },
    { id: 'privacy', label: 'Приватность', icon: '🔒' },
    { id: 'security', label: 'Безопасность', icon: '🛡' },
    { id: 'notifications', label: 'Уведомления', icon: '🔔' },
  ]

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          ⚙️ Настройки
        </h1>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-6" role="tablist" aria-label="Настройки">
          {tabs.map(tab => (
            <TabButton
              key={tab.id}
              id={tab.id}
              label={tab.label}
              icon={tab.icon}
              active={activeTab === tab.id}
              onClick={() => setActiveTab(tab.id)}
            />
          ))}
        </div>

        {/* Content */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-md p-6 mb-6" role="tabpanel" id={`panel-${activeTab}`}>
          {/* General Settings */}
          {activeTab === 'general' && (
            <>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-6">
                🔧 Основные настройки
              </h2>

              <div className="space-y-6">
                <div>
                  <label htmlFor="settings-language" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Язык
                  </label>
                  <select
                    id="settings-language"
                    value={settings.language}
                    onChange={(e) => updateSetting('language', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value="ru">Русский</option>
                    <option value="en">English</option>
                    <option value="zh">中文</option>
                    <option value="he">עברית</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="settings-timezone" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Часовой пояс
                  </label>
                  <select
                    id="settings-timezone"
                    value={settings.timezone}
                    onChange={(e) => updateSetting('timezone', e.target.value)}
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
                <div>
                  <label htmlFor="settings-visibility" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Видимость профиля
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Кто может видеть ваш профиль</p>
                  <select
                    id="settings-visibility"
                    value={settings.profileVisibility}
                    onChange={(e) => updateSetting('profileVisibility', e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
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
                    onChange={(v) => updateSetting('showOnlineStatus', v)}
                    label="Показывать статус онлайн"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Показывать «Был(а)»</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Другие видят, когда вы последний раз были онлайн</p>
                  </div>
                  <Toggle
                    enabled={settings.showLastSeen}
                    onChange={(v) => updateSetting('showLastSeen', v)}
                    label="Показывать время последнего посещения"
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
                    onChange={(v) => updateSetting('twoFactorEnabled', v)}
                    label="Двухфакторная аутентификация"
                  />
                </div>

                <div>
                  <label htmlFor="settings-sessions-limit" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Лимит активных сессий
                  </label>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">Максимальное количество одновременных сессий</p>
                  <select
                    id="settings-sessions-limit"
                    value={settings.sessionsLimit}
                    onChange={(e) => updateSetting('sessionsLimit', Number(e.target.value))}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
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
                    onChange={(v) => updateSetting('emailNotifications', v)}
                    label="Email уведомления"
                  />
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium text-gray-900 dark:text-white">Push уведомления</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">Получать push уведомления в браузере</p>
                  </div>
                  <Toggle
                    enabled={settings.pushNotifications}
                    onChange={(v) => updateSetting('pushNotifications', v)}
                    label="Push уведомления"
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
            disabled={isSaving || !hasChanges}
            className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed text-white rounded-xl font-medium transition-colors"
          >
            {isSaving ? (
              <span className="flex items-center gap-2">
                <span className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></span>
                Сохранение...
              </span>
            ) : (
              'Сохранить настройки'
            )}
          </button>
        </div>
      </div>
    </div>
  )
}
