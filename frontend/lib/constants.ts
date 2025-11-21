/**
 * Константы приложения
 */

// API endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    LOGOUT: '/api/v1/auth/logout',
    REFRESH: '/api/v1/auth/refresh',
    FORGOT_PASSWORD: '/api/v1/auth/forgot-password',
    RESET_PASSWORD: '/api/v1/auth/reset-password',
  },
  USERS: {
    ME: '/api/v1/users/me',
    BY_ID: (id: number) => `/api/v1/users/${id}`,
  },
  MENTORS: {
    LIST: '/api/v1/mentors',
    BY_ID: (id: number) => `/api/v1/mentors/${id}`,
    APPLY: '/api/v1/mentors/apply',
    REVIEWS: (id: number) => `/api/v1/mentors/${id}/reviews`,
  },
  SESSIONS: {
    LIST: '/api/v1/sessions',
    BY_ID: (id: number) => `/api/v1/sessions/${id}`,
    COMPLETE: (id: number) => `/api/v1/sessions/${id}/complete`,
  },
  COURSES: {
    LIST: '/api/v1/courses',
    BY_ID: (id: number) => `/api/v1/courses/${id}`,
    ENROLL: (id: number) => `/api/v1/courses/${id}/enroll`,
    PROGRESS: (id: number) => `/api/v1/courses/${id}/progress`,
  },
  MESSAGES: {
    CHATS: '/api/v1/messages/chats',
    CHAT_HISTORY: (id: number) => `/api/v1/messages/chats/${id}`,
    SEND: '/api/v1/messages',
  },
  PAYMENTS: {
    CREATE: '/api/v1/payments/create',
    HISTORY: '/api/v1/payments/history',
  },
} as const

// Роуты приложения
export const ROUTES = {
  HOME: '/',
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
  },
  DASHBOARD: '/dashboard',
  PROFILE: '/profile',
  SETTINGS: '/settings',
  MENTORS: '/mentors',
  COURSES: '/courses',
  LEARNING: '/learning',
  SESSIONS: '/sessions',
  BOOKING: '/booking',
  MESSAGES: '/messages',
  NOTIFICATIONS: '/notifications',
  STATS: '/stats',
  ACHIEVEMENTS: '/achievements',
  BILLING: '/billing',
  PAYMENT: '/payment',
  SEARCH: '/search',
  RESOURCES: '/resources',
  HELP: '/help',
  ADMIN: '/admin',
  ABOUT: '/about',
  PRICING: '/pricing',
  CONTACT: '/contact',
  TERMS: '/terms',
  PRIVACY: '/privacy',
} as const

// LocalStorage ключи
export const STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_DATA: 'user_data',
  USER_NAME: 'user_name',
  THEME: 'theme',
  LANGUAGE: 'language',
  NOTIFICATIONS: 'notifications',
  RECENT_SEARCHES: 'recent_searches',
} as const

// Роли пользователей
export const USER_ROLES = {
  STUDENT: 'student',
  MENTOR: 'mentor',
  ADMIN: 'admin',
} as const

// Статусы сессий
export const SESSION_STATUS = {
  SCHEDULED: 'scheduled',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  CANCELLED: 'cancelled',
} as const

// Типы уведомлений
export const NOTIFICATION_TYPES = {
  INFO: 'info',
  SUCCESS: 'success',
  WARNING: 'warning',
  ERROR: 'error',
} as const

// Уровни курсов
export const COURSE_LEVELS = {
  BEGINNER: 'beginner',
  INTERMEDIATE: 'intermediate',
  ADVANCED: 'advanced',
  EXPERT: 'expert',
} as const

// Категории курсов
export const COURSE_CATEGORIES = {
  PROGRAMMING: 'programming',
  DATA_SCIENCE: 'data_science',
  DESIGN: 'design',
  BUSINESS: 'business',
  LANGUAGES: 'languages',
  MARKETING: 'marketing',
} as const

// Статусы платежей
export const PAYMENT_STATUS = {
  PENDING: 'pending',
  COMPLETED: 'completed',
  FAILED: 'failed',
  REFUNDED: 'refunded',
} as const

// Типы платежей
export const PAYMENT_TYPES = {
  SESSION: 'session',
  COURSE: 'course',
  SUBSCRIPTION: 'subscription',
} as const

// Планы подписок
export const SUBSCRIPTION_PLANS = {
  FREE: {
    id: 'free',
    name: 'Free',
    price: 0,
    features: [
      'Доступ к базовым курсам',
      'Просмотр профилей менторов',
      'Ограниченное количество сессий',
    ],
  },
  BASIC: {
    id: 'basic',
    name: 'Basic',
    price: 999,
    features: [
      'Доступ ко всем курсам',
      'До 5 сессий в месяц',
      'Чат с менторами',
      'Сертификаты по курсам',
    ],
  },
  PRO: {
    id: 'pro',
    name: 'Pro',
    price: 1999,
    features: [
      'Все возможности Basic',
      'До 15 сессий в месяц',
      'Приоритетная поддержка',
      'Персональный трекер прогресса',
      'Скидка 10% на дополнительные сессии',
    ],
  },
  ENTERPRISE: {
    id: 'enterprise',
    name: 'Enterprise',
    price: 4999,
    features: [
      'Все возможности Pro',
      'Безлимитные сессии',
      'Выделенный ментор',
      'Индивидуальная программа обучения',
      'Приоритетное бронирование',
      'Корпоративные отчеты',
    ],
  },
} as const

// Языки программирования
export const PROGRAMMING_LANGUAGES = [
  'JavaScript',
  'TypeScript',
  'Python',
  'Java',
  'C#',
  'C++',
  'Go',
  'Rust',
  'PHP',
  'Ruby',
  'Swift',
  'Kotlin',
] as const

// Технологии
export const TECHNOLOGIES = [
  'React',
  'Next.js',
  'Vue.js',
  'Angular',
  'Node.js',
  'Express',
  'FastAPI',
  'Django',
  'Flask',
  'Spring',
  'ASP.NET',
  'PostgreSQL',
  'MongoDB',
  'Redis',
  'Docker',
  'Kubernetes',
  'AWS',
  'Azure',
  'GCP',
] as const

// Регулярные выражения
export const REGEX = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^(\+7|8)?[\s-]?\(?[0-9]{3}\)?[\s-]?[0-9]{3}[\s-]?[0-9]{2}[\s-]?[0-9]{2}$/,
  URL: /^(https?:\/\/)?([\da-z.-]+)\.([a-z.]{2,6})([/\w .-]*)*\/?$/,
  USERNAME: /^[a-zA-Z0-9_-]{3,20}$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d@$!%*?&]{8,}$/,
} as const

// Лимиты
export const LIMITS = {
  MAX_FILE_SIZE: 10 * 1024 * 1024, // 10 MB
  MAX_IMAGE_SIZE: 5 * 1024 * 1024, // 5 MB
  MAX_MESSAGE_LENGTH: 1000,
  MAX_BIO_LENGTH: 500,
  MAX_TITLE_LENGTH: 100,
  MIN_PASSWORD_LENGTH: 6,
  MAX_PASSWORD_LENGTH: 50,
} as const

// Таймауты
export const TIMEOUTS = {
  DEBOUNCE: 300,
  THROTTLE: 1000,
  API_TIMEOUT: 30000,
  TOAST_DURATION: 3000,
  ERROR_TOAST_DURATION: 5000,
} as const

// Социальные сети
export const SOCIAL_LINKS = {
  GITHUB: 'https://github.com/QuadDarv1ne/MentorHub',
  LINKEDIN: 'https://linkedin.com/company/mentorhub',
  TWITTER: 'https://twitter.com/MentorHubApp',
  TELEGRAM: 'https://t.me/mentorhub_community',
} as const

// Контакты
export const CONTACTS = {
  EMAIL: 'maksimqwe42@mail.ru',
  PHONE: '+79150480249',
  TELEGRAM: '@quadd4rv1n7',
} as const

// Допустимые типы файлов
export const ALLOWED_FILE_TYPES = {
  IMAGES: ['image/jpeg', 'image/png', 'image/gif', 'image/webp'],
  DOCUMENTS: ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'],
  ARCHIVES: ['application/zip', 'application/x-rar-compressed'],
} as const

// Цветовая схема для типов
export const TYPE_COLORS = {
  info: {
    bg: 'bg-blue-50',
    border: 'border-blue-500',
    text: 'text-blue-900',
    icon: 'text-blue-600',
  },
  success: {
    bg: 'bg-green-50',
    border: 'border-green-500',
    text: 'text-green-900',
    icon: 'text-green-600',
  },
  warning: {
    bg: 'bg-yellow-50',
    border: 'border-yellow-500',
    text: 'text-yellow-900',
    icon: 'text-yellow-600',
  },
  error: {
    bg: 'bg-red-50',
    border: 'border-red-500',
    text: 'text-red-900',
    icon: 'text-red-600',
  },
} as const
