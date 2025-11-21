/**
 * Утилиты для работы с датами
 */

/**
 * Форматирование даты в читаемый вид
 */
export function formatDate(date: Date | string, format: 'short' | 'long' | 'full' = 'short'): string {
  const d = typeof date === 'string' ? new Date(date) : date

  switch (format) {
    case 'short':
      return d.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      })
    
    case 'long':
      return d.toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    
    case 'full':
      return d.toLocaleDateString('ru-RU', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    
    default:
      return d.toLocaleDateString('ru-RU')
  }
}

/**
 * Форматирование времени
 */
export function formatTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  
  return d.toLocaleTimeString('ru-RU', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * Форматирование даты и времени
 */
export function formatDateTime(date: Date | string): string {
  return `${formatDate(date)} ${formatTime(date)}`
}

/**
 * Относительное время ("5 минут назад", "вчера" и т.д.)
 */
export function getRelativeTime(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const now = new Date()
  const diffMs = now.getTime() - d.getTime()
  const diffSec = Math.floor(diffMs / 1000)
  const diffMin = Math.floor(diffSec / 60)
  const diffHour = Math.floor(diffMin / 60)
  const diffDay = Math.floor(diffHour / 24)

  if (diffSec < 60) {
    return 'только что'
  } else if (diffMin < 60) {
    return `${diffMin} ${pluralize(diffMin, 'минуту', 'минуты', 'минут')} назад`
  } else if (diffHour < 24) {
    return `${diffHour} ${pluralize(diffHour, 'час', 'часа', 'часов')} назад`
  } else if (diffDay === 1) {
    return 'вчера'
  } else if (diffDay < 7) {
    return `${diffDay} ${pluralize(diffDay, 'день', 'дня', 'дней')} назад`
  } else {
    return formatDate(d)
  }
}

/**
 * Плюрализация русских слов
 */
function pluralize(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10
  const mod100 = n % 100

  if (mod10 === 1 && mod100 !== 11) {
    return one
  } else if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) {
    return few
  } else {
    return many
  }
}

/**
 * Добавление дней к дате
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date)
  result.setDate(result.getDate() + days)
  return result
}

/**
 * Вычитание дней из даты
 */
export function subtractDays(date: Date, days: number): Date {
  return addDays(date, -days)
}

/**
 * Начало дня
 */
export function startOfDay(date: Date): Date {
  const result = new Date(date)
  result.setHours(0, 0, 0, 0)
  return result
}

/**
 * Конец дня
 */
export function endOfDay(date: Date): Date {
  const result = new Date(date)
  result.setHours(23, 59, 59, 999)
  return result
}

/**
 * Проверка, является ли дата сегодняшним днем
 */
export function isToday(date: Date): boolean {
  const today = new Date()
  return (
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear()
  )
}

/**
 * Проверка, является ли дата вчерашним днем
 */
export function isYesterday(date: Date): boolean {
  const yesterday = subtractDays(new Date(), 1)
  return (
    date.getDate() === yesterday.getDate() &&
    date.getMonth() === yesterday.getMonth() &&
    date.getFullYear() === yesterday.getFullYear()
  )
}

/**
 * Проверка, является ли дата завтрашним днем
 */
export function isTomorrow(date: Date): boolean {
  const tomorrow = addDays(new Date(), 1)
  return (
    date.getDate() === tomorrow.getDate() &&
    date.getMonth() === tomorrow.getMonth() &&
    date.getFullYear() === tomorrow.getFullYear()
  )
}

/**
 * Получение диапазона дат (начало и конец недели/месяца)
 */
export function getWeekRange(date: Date = new Date()): { start: Date; end: Date } {
  const start = new Date(date)
  const day = start.getDay()
  const diff = start.getDate() - day + (day === 0 ? -6 : 1) // Понедельник как начало недели
  
  start.setDate(diff)
  start.setHours(0, 0, 0, 0)
  
  const end = new Date(start)
  end.setDate(start.getDate() + 6)
  end.setHours(23, 59, 59, 999)
  
  return { start, end }
}

export function getMonthRange(date: Date = new Date()): { start: Date; end: Date } {
  const start = new Date(date.getFullYear(), date.getMonth(), 1)
  const end = new Date(date.getFullYear(), date.getMonth() + 1, 0, 23, 59, 59, 999)
  
  return { start, end }
}

/**
 * Разница между датами в днях
 */
export function daysDifference(date1: Date, date2: Date): number {
  const d1 = startOfDay(date1)
  const d2 = startOfDay(date2)
  const diffMs = d2.getTime() - d1.getTime()
  return Math.floor(diffMs / (1000 * 60 * 60 * 24))
}

/**
 * Форматирование длительности (в минутах) в читаемый вид
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes} мин`
  }
  
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  
  if (mins === 0) {
    return `${hours} ${pluralize(hours, 'час', 'часа', 'часов')}`
  }
  
  return `${hours} ч ${mins} мин`
}

/**
 * Проверка, является ли дата выходным днем
 */
export function isWeekend(date: Date): boolean {
  const day = date.getDay()
  return day === 0 || day === 6
}

/**
 * Получение названия месяца
 */
export function getMonthName(date: Date, format: 'short' | 'long' = 'long'): string {
  return date.toLocaleDateString('ru-RU', {
    month: format === 'short' ? 'short' : 'long'
  })
}

/**
 * Получение названия дня недели
 */
export function getDayName(date: Date, format: 'short' | 'long' = 'long'): string {
  return date.toLocaleDateString('ru-RU', {
    weekday: format === 'short' ? 'short' : 'long'
  })
}
