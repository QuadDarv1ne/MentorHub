'use client'

import { useState } from 'react'
import { User, Bell, Eye, Mail, Shield } from 'lucide-react'
import Card from '@/components/ui/Card'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import Input from '@/components/ui/Input'
import Tabs from '@/components/ui/Tabs'

export default function SettingsPage() {
  const [emailNotifications, setEmailNotifications] = useState(true)
  const [pushNotifications, setPushNotifications] = useState(true)
  const [sessionReminders, setSessionReminders] = useState(true)
  const [newsletter, setNewsletter] = useState(false)

  const tabs = [
    {
      id: 'account',
      label: 'Аккаунт',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Основная информация</h3>
            <div className="space-y-4">
              <Input
                label="Email"
                type="email"
                defaultValue="user@example.com"
                disabled
                fullWidth
                helperText="Email нельзя изменить"
              />
              <Input
                label="Имя и фамилия"
                type="text"
                defaultValue="Иван Петров"
                fullWidth
              />
              <Input
                label="Телефон"
                type="tel"
                defaultValue="+7 (999) 123-45-67"
                fullWidth
              />
            </div>
          </div>

          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Профиль</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Аватар
                </label>
                <div className="flex items-center gap-4">
                  <div className="h-20 w-20 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold">
                    ИП
                  </div>
                  <Button variant="outline" size="sm">
                    Загрузить фото
                  </Button>
                </div>
              </div>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-6 border-t">
            <Button variant="outline">Отмена</Button>
            <Button variant="primary">Сохранить изменения</Button>
          </div>
        </div>
      )
    },
    {
      id: 'notifications',
      label: 'Уведомления',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Настройки уведомлений
            </h3>
            <div className="space-y-4">
              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Email уведомления</div>
                    <div className="text-sm text-gray-500">Получать уведомления на email</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={emailNotifications}
                  onChange={(e) => setEmailNotifications(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>

              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <Bell className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Push уведомления</div>
                    <div className="text-sm text-gray-500">Уведомления в браузере</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={pushNotifications}
                  onChange={(e) => setPushNotifications(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>

              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Напоминания о сессиях</div>
                    <div className="text-sm text-gray-500">За 1 час до начала</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={sessionReminders}
                  onChange={(e) => setSessionReminders(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>

              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <Mail className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Новостная рассылка</div>
                    <div className="text-sm text-gray-500">Новости и обновления платформы</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  checked={newsletter}
                  onChange={(e) => setNewsletter(e.target.checked)}
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-6 border-t">
            <Button variant="outline">Отмена</Button>
            <Button variant="primary">Сохранить изменения</Button>
          </div>
        </div>
      )
    },
    {
      id: 'security',
      label: 'Безопасность',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Пароль</h3>
            <div className="space-y-4">
              <Input
                label="Текущий пароль"
                type="password"
                fullWidth
              />
              <Input
                label="Новый пароль"
                type="password"
                fullWidth
                helperText="Минимум 8 символов"
              />
              <Input
                label="Подтвердите новый пароль"
                type="password"
                fullWidth
              />
            </div>
            <div className="mt-4">
              <Button variant="primary">Изменить пароль</Button>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Двухфакторная аутентификация</h3>
            <p className="text-gray-600 mb-4">
              Защитите свой аккаунт дополнительным уровнем безопасности
            </p>
            <Button variant="outline">
              <Shield className="h-4 w-4 mr-2" />
              Настроить 2FA
            </Button>
          </div>

          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Активные сессии</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Chrome на Windows</div>
                  <div className="text-sm text-gray-500">Москва, Россия • Сейчас</div>
                </div>
                <Badge variant="success" size="sm">Текущая</Badge>
              </div>
              <div className="flex items-center justify-between p-4 border rounded-lg">
                <div>
                  <div className="font-medium text-gray-900">Safari на iPhone</div>
                  <div className="text-sm text-gray-500">Москва, Россия • 2 дня назад</div>
                </div>
                <Button variant="outline" size="sm">Завершить</Button>
              </div>
            </div>
          </div>
        </div>
      )
    },
    {
      id: 'privacy',
      label: 'Приватность',
      content: (
        <div className="space-y-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Видимость профиля</h3>
            <div className="space-y-4">
              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <Eye className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Публичный профиль</div>
                    <div className="text-sm text-gray-500">Ваш профиль виден всем пользователям</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>

              <label className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                <div className="flex items-center gap-3">
                  <User className="h-5 w-5 text-gray-600" />
                  <div>
                    <div className="font-medium text-gray-900">Показывать активность</div>
                    <div className="text-sm text-gray-500">Время последнего входа</div>
                  </div>
                </div>
                <input
                  type="checkbox"
                  defaultChecked
                  className="rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
                />
              </label>
            </div>
          </div>

          <div className="pt-6 border-t">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Данные</h3>
            <div className="space-y-3">
              <Button variant="outline" fullWidth>
                Скачать мои данные
              </Button>
              <Button variant="danger" fullWidth>
                Удалить аккаунт
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Удаление аккаунта необратимо. Все ваши данные будут удалены.
            </p>
          </div>
        </div>
      )
    }
  ]

  return (
    <main className="container mx-auto max-w-4xl px-4 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Настройки</h1>
        <p className="text-gray-600">
          Управляйте настройками вашего аккаунта и профиля
        </p>
      </div>

      <Card padding="none">
        <div className="p-6">
          <Tabs tabs={tabs} defaultTab="account" />
        </div>
      </Card>
    </main>
  )
}
