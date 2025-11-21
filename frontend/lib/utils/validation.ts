/**
 * Утилиты для валидации данных
 */

/**
 * Валидация email адреса
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Валидация номера телефона (российский формат)
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^(\+7|8)?[\s-]?\(?[0-9]{3}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/
  return phoneRegex.test(phone)
}

/**
 * Валидация пароля
 */
export interface PasswordValidation {
  isValid: boolean
  errors: string[]
  strength: number // 0-5
}

export function validatePassword(password: string): PasswordValidation {
  const errors: string[] = []
  let strength = 0

  if (password.length < 6) {
    errors.push('Пароль должен быть не менее 6 символов')
  } else {
    strength++
  }

  if (password.length >= 10) {
    strength++
  }

  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) {
    strength++
  } else {
    errors.push('Пароль должен содержать строчные и заглавные буквы')
  }

  if (/\d/.test(password)) {
    strength++
  } else {
    errors.push('Пароль должен содержать хотя бы одну цифру')
  }

  if (/[^a-zA-Z0-9]/.test(password)) {
    strength++
  }

  return {
    isValid: errors.length === 0,
    errors,
    strength
  }
}

/**
 * Валидация URL
 */
export function isValidUrl(url: string): boolean {
  try {
    const urlObj = new URL(url)
    return urlObj.protocol === 'http:' || urlObj.protocol === 'https:'
  } catch {
    return false
  }
}

/**
 * Валидация имени пользователя
 */
export function isValidUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/
  return usernameRegex.test(username)
}

/**
 * Валидация кредитной карты (простая проверка)
 */
export function isValidCreditCard(cardNumber: string): boolean {
  // Удаляем пробелы и дефисы
  const cleaned = cardNumber.replace(/[\s-]/g, '')
  
  // Проверка длины (13-19 цифр)
  if (!/^\d{13,19}$/.test(cleaned)) {
    return false
  }

  // Алгоритм Луна
  let sum = 0
  let isEven = false

  for (let i = cleaned.length - 1; i >= 0; i--) {
    let digit = parseInt(cleaned.charAt(i), 10)

    if (isEven) {
      digit *= 2
      if (digit > 9) {
        digit -= 9
      }
    }

    sum += digit
    isEven = !isEven
  }

  return sum % 10 === 0
}

/**
 * Валидация даты рождения (возраст от 13 до 120 лет)
 */
export function isValidBirthDate(date: Date): boolean {
  const today = new Date()
  const birthDate = new Date(date)
  
  let age = today.getFullYear() - birthDate.getFullYear()
  const monthDiff = today.getMonth() - birthDate.getMonth()
  
  if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
    age--
  }

  return age >= 13 && age <= 120
}

/**
 * Валидация ZIP кода (российский формат)
 */
export function isValidZipCode(zip: string): boolean {
  const zipRegex = /^\d{6}$/
  return zipRegex.test(zip)
}

/**
 * Санитизация HTML (базовая защита от XSS)
 */
export function sanitizeHtml(html: string): string {
  const div = document.createElement('div')
  div.textContent = html
  return div.innerHTML
}

/**
 * Валидация диапазона чисел
 */
export function isInRange(value: number, min: number, max: number): boolean {
  return value >= min && value <= max
}

/**
 * Валидация формата файла
 */
export function isValidFileType(file: File, allowedTypes: string[]): boolean {
  return allowedTypes.includes(file.type)
}

/**
 * Валидация размера файла
 */
export function isValidFileSize(file: File, maxSizeMB: number): boolean {
  const maxSizeBytes = maxSizeMB * 1024 * 1024
  return file.size <= maxSizeBytes
}

/**
 * Проверка на пустую строку (с учетом пробелов)
 */
export function isEmpty(value: string): boolean {
  return !value || value.trim().length === 0
}

/**
 * Проверка на наличие только букв
 */
export function isAlpha(value: string): boolean {
  return /^[a-zA-Zа-яА-ЯёЁ]+$/.test(value)
}

/**
 * Проверка на наличие только цифр
 */
export function isNumeric(value: string): boolean {
  return /^\d+$/.test(value)
}

/**
 * Проверка на буквы и цифры
 */
export function isAlphanumeric(value: string): boolean {
  return /^[a-zA-Z0-9а-яА-ЯёЁ]+$/.test(value)
}

/**
 * Валидация ИНН (для физических лиц - 12 цифр)
 */
export function isValidINN(inn: string): boolean {
  if (!/^\d{10}$|^\d{12}$/.test(inn)) {
    return false
  }

  // Упрощенная проверка (полная проверка требует контрольных сумм)
  return true
}

/**
 * Форматирование номера телефона
 */
export function formatPhone(phone: string): string {
  const cleaned = phone.replace(/\D/g, '')
  
  if (cleaned.length === 11 && cleaned.startsWith('8')) {
    return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9)}`
  }
  
  if (cleaned.length === 11 && cleaned.startsWith('7')) {
    return `+7 (${cleaned.slice(1, 4)}) ${cleaned.slice(4, 7)}-${cleaned.slice(7, 9)}-${cleaned.slice(9)}`
  }
  
  return phone
}

/**
 * Форматирование номера карты
 */
export function formatCardNumber(cardNumber: string): string {
  const cleaned = cardNumber.replace(/\D/g, '')
  const groups = cleaned.match(/.{1,4}/g)
  return groups ? groups.join(' ') : cleaned
}
