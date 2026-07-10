'use client'

import { useState, useEffect } from 'react'
import { useToast } from '@/hooks/useToast'
import { logger } from '@/lib/utils/logger'
import {
  getCalendarEvents,
  syncGoogleCalendar,
  syncOutlookCalendar,
  exportIcal,
  type CalendarEvent,
} from '@/lib/api/calendar'

interface CalendarSettings {
  googleSync: boolean
  outlookSync: boolean
  icalExport: boolean
  reminders: boolean
  reminderMinutes: number
}

export default function CalendarPage() {
  const toast = useToast()
  const [events, setEvents] = useState<CalendarEvent[]>([])
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [view, setView] = useState<'month' | 'week' | 'day'>('month')
  const [settings, setSettings] = useState<CalendarSettings>({
    googleSync: false,
    outlookSync: false,
    icalExport: true,
    reminders: true,
    reminderMinutes: 15
  })

  useEffect(() => {
    fetchEvents()
  }, [selectedDate])

  const fetchEvents = async () => {
    try {
      const data = await getCalendarEvents()
      setEvents(data)
    } catch (error) {
      logger.error('Fetch events error', error)
    }
  }

  const syncWithGoogle = async () => {
    try {
      await syncGoogleCalendar()
      setSettings({ ...settings, googleSync: true })
      toast.success('Google Calendar синхронизирован')
      fetchEvents()
    } catch (error) {
      logger.error('Google sync error', error)
      toast.error('Ошибка синхронизации с Google Calendar')
    }
  }

  const syncWithOutlook = async () => {
    try {
      await syncOutlookCalendar()
      setSettings({ ...settings, outlookSync: true })
      toast.success('Outlook Calendar синхронизирован')
      fetchEvents()
    } catch (error) {
      logger.error('Outlook sync error', error)
      toast.error('Ошибка синхронизации с Outlook Calendar')
    }
  }

  const handleExportIcal = async () => {
    try {
      const response = await exportIcal()
      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = 'mentorhub-calendar.ics'
        link.click()
        window.URL.revokeObjectURL(url)
        toast.success('iCal файл экспортирован')
      } else {
        toast.error('Ошибка экспорта iCal')
      }
    } catch (error) {
      logger.error('iCal export error', error)
      toast.error('Ошибка экспорта iCal')
    }
  }

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear()
    const month = date.getMonth()
    const firstDay = new Date(year, month, 1)
    const lastDay = new Date(year, month + 1, 0)
    const daysInMonth = lastDay.getDate()
    const startingDay = firstDay.getDay()
    
    return { daysInMonth, startingDay, year, month }
  }

  const getEventsForDay = (day: number) => {
    const date = new Date(selectedDate.getFullYear(), selectedDate.getMonth(), day)
    const dateStr = date.toISOString().split('T')[0]
    return events.filter(event => event.start_time.startsWith(dateStr))
  }

  const { daysInMonth, startingDay } = getDaysInMonth(selectedDate)
  const monthNames = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь', 'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              📅 Календарь
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              {monthNames[selectedDate.getMonth()]} {selectedDate.getFullYear()}
            </p>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSelectedDate(new Date())}
              className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition-colors"
            >
              Сегодня
            </button>
            <div className="flex bg-white dark:bg-gray-800 rounded-lg overflow-hidden">
              <button
                onClick={() => setView('month')}
                className={`px-4 py-2 ${view === 'month' ? 'bg-indigo-600 text-white' : 'text-gray-700 dark:text-gray-300'}`}
              >
                Месяц
              </button>
              <button
                onClick={() => setView('week')}
                className={`px-4 py-2 ${view === 'week' ? 'bg-indigo-600 text-white' : 'text-gray-700 dark:text-gray-300'}`}
              >
                Неделя
              </button>
              <button
                onClick={() => setView('day')}
                className={`px-4 py-2 ${view === 'day' ? 'bg-indigo-600 text-white' : 'text-gray-700 dark:text-gray-300'}`}
              >
                День
              </button>
            </div>
          </div>
        </div>

        <div className="grid lg:grid-cols-4 gap-6">
          {/* Calendar */}
          <div className="lg:col-span-3 bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
            {/* Weekday Headers */}
            <div className="grid grid-cols-7 border-b border-gray-200 dark:border-gray-700">
              {['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'].map(day => (
                <div key={day} className="p-3 text-center font-semibold text-gray-700 dark:text-gray-300">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7">
              {/* Empty cells for days before month starts */}
              {Array.from({ length: startingDay }).map((_, i) => (
                <div key={`empty-${i}`} className="p-2 min-h-[100px] bg-gray-50 dark:bg-gray-900/50" />
              ))}

              {/* Days */}
              {Array.from({ length: daysInMonth }).map((_, i) => {
                const day = i + 1
                const dayEvents = getEventsForDay(day)
                const isToday = day === new Date().getDate()
                
                return (
                  <div
                    key={day}
                    className={`p-2 min-h-[100px] border-b border-r border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700/50 cursor-pointer ${
                      isToday ? 'bg-indigo-50 dark:bg-indigo-900/20' : ''
                    }`}
                    onClick={() => {/* Show day view */}}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className={`text-sm font-medium ${
                        isToday ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-900 dark:text-white'
                      }`}>
                        {day}
                      </span>
                      {dayEvents.length > 0 && (
                        <span className="text-xs text-gray-500 dark:text-gray-400">
                          {dayEvents.length}
                        </span>
                      )}
                    </div>
                    
                    {/* Events */}
                    <div className="space-y-1">
                      {dayEvents.slice(0, 3).map(event => (
                        <div
                          key={event.id}
                          className={`text-xs px-2 py-1 rounded truncate ${
                            event.type === 'session' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' :
                            event.type === 'meeting' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' :
                            'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                          }`}
                        >
                          {event.title}
                        </div>
                      ))}
                      {dayEvents.length > 3 && (
                        <div className="text-xs text-gray-500 dark:text-gray-400 pl-2">
                          +{dayEvents.length - 3} ещё
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Integrations */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                🔄 Интеграции
              </h3>
              <div className="space-y-4">
                <button
                  onClick={syncWithGoogle}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between ${
                    settings.googleSync
                      ? 'bg-green-600 hover:bg-green-700 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                  }`}
                >
                  <span>Google Calendar</span>
                  {settings.googleSync && <span>✓</span>}
                </button>
                
                <button
                  onClick={syncWithOutlook}
                  className={`w-full px-4 py-3 rounded-lg font-medium transition-colors flex items-center justify-between ${
                    settings.outlookSync
                      ? 'bg-blue-600 hover:bg-blue-700 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-900 dark:text-white'
                  }`}
                >
                  <span>Outlook Calendar</span>
                  {settings.outlookSync && <span>✓</span>}
                </button>
                
                <button
                  onClick={handleExportIcal}
                  className="w-full px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors"
                >
                  📥 Экспорт iCal
                </button>
              </div>
            </div>

            {/* Upcoming Events */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                📌 Предстоящие
              </h3>
              <div className="space-y-3">
                {events.slice(0, 5).map(event => (
                  <div key={event.id} className="p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
                      {event.title}
                    </h4>
                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      {new Date(event.start_time).toLocaleDateString('ru-RU', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            {/* Settings */}
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
              <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-4">
                ⚙️ Настройки
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-700 dark:text-gray-300">Напоминания</span>
                  <input
                    type="checkbox"
                    checked={settings.reminders}
                    onChange={(e) => setSettings({ ...settings, reminders: e.target.checked })}
                    className="w-4 h-4"
                  />
                </div>
                <div>
                  <label className="text-sm text-gray-700 dark:text-gray-300 block mb-2">
                    Напоминать за (минут)
                  </label>
                  <select
                    value={settings.reminderMinutes}
                    onChange={(e) => setSettings({ ...settings, reminderMinutes: Number(e.target.value) })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    <option value={5}>5 минут</option>
                    <option value={15}>15 минут</option>
                    <option value={30}>30 минут</option>
                    <option value={60}>1 час</option>
                  </select>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
