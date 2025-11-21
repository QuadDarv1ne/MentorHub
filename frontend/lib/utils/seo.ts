/**
 * SEO утилиты для генерации метаданных страниц
 * Поддержка Open Graph, Twitter Cards, структурированных данных
 */

import { Metadata } from 'next'

interface SEOConfig {
  title: string
  description: string
  path?: string
  image?: string
  type?: 'website' | 'article' | 'profile'
  publishedTime?: string
  authors?: string[]
  tags?: string[]
  noIndex?: boolean
}

const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://mentorhub.com'
const SITE_NAME = 'MentorHub'
const DEFAULT_DESCRIPTION = 'Платформа для менторства и развития в IT. Найдите своего ментора, развивайте навыки, достигайте карьерных целей.'
const DEFAULT_IMAGE = '/og-image.png'

/**
 * Генерирует метаданные для страницы с полной поддержкой SEO
 */
export function generateSEOMetadata(config: SEOConfig): Metadata {
  const {
    title,
    description,
    path = '',
    image = DEFAULT_IMAGE,
    type = 'website',
    publishedTime,
    authors,
    tags,
    noIndex = false,
  } = config

  const fullTitle = title.includes(SITE_NAME) ? title : `${title} | ${SITE_NAME}`
  const url = `${BASE_URL}${path}`
  const imageUrl = image.startsWith('http') ? image : `${BASE_URL}${image}`

  const metadata: Metadata = {
    title: fullTitle,
    description,
    applicationName: SITE_NAME,
    
    // Open Graph
    openGraph: {
      type,
      title: fullTitle,
      description,
      url,
      siteName: SITE_NAME,
      images: [
        {
          url: imageUrl,
          width: 1200,
          height: 630,
          alt: title,
        },
      ],
      locale: 'ru_RU',
      ...(publishedTime && type === 'article' && {
        publishedTime,
      }),
      ...(authors && type === 'article' && {
        authors: authors,
      }),
    },

    // Twitter Cards
    twitter: {
      card: 'summary_large_image',
      title: fullTitle,
      description,
      images: [imageUrl],
      creator: '@MentorHubApp',
      site: '@MentorHubApp',
    },

    // Additional metadata
    ...(tags && {
      keywords: tags,
    }),

    // Robots
    robots: noIndex
      ? {
          index: false,
          follow: false,
          nocache: true,
          googleBot: {
            index: false,
            follow: false,
          },
        }
      : {
          index: true,
          follow: true,
          googleBot: {
            index: true,
            follow: true,
            'max-video-preview': -1,
            'max-image-preview': 'large',
            'max-snippet': -1,
          },
        },

    // Canonical
    alternates: {
      canonical: url,
    },

    // Verification
    verification: {
      google: process.env.NEXT_PUBLIC_GOOGLE_SITE_VERIFICATION,
      yandex: process.env.NEXT_PUBLIC_YANDEX_VERIFICATION,
    },
  }

  return metadata
}

/**
 * Предустановленные конфигурации для типовых страниц
 */
export const seoPresets = {
  home: (): Metadata =>
    generateSEOMetadata({
      title: 'Платформа менторства в IT',
      description: DEFAULT_DESCRIPTION,
      path: '/',
    }),

  mentors: (): Metadata =>
    generateSEOMetadata({
      title: 'Каталог менторов',
      description: 'Найдите опытного IT-ментора для достижения карьерных целей. Программирование, DevOps, дизайн, менеджмент и другие направления.',
      path: '/mentors',
    }),

  courses: (): Metadata =>
    generateSEOMetadata({
      title: 'Обучающие курсы и треки',
      description: 'Структурированные программы обучения с поддержкой менторов. От основ программирования до продвинутых технологий.',
      path: '/courses',
    }),

  pricing: (): Metadata =>
    generateSEOMetadata({
      title: 'Тарифы и цены',
      description: 'Гибкие тарифные планы для студентов и профессионалов. Разовые сессии, подписки, корпоративные решения.',
      path: '/pricing',
    }),

  blog: (): Metadata =>
    generateSEOMetadata({
      title: 'Блог',
      description: 'Статьи о менторстве, карьерном развитии, трендах в IT и практических советах от экспертов.',
      path: '/blog',
      type: 'website',
    }),

  auth: {
    login: (): Metadata =>
      generateSEOMetadata({
        title: 'Вход в аккаунт',
        description: 'Войдите в свой аккаунт MentorHub для доступа к менторам, курсам и персональному обучению.',
        path: '/auth/login',
        noIndex: true,
      }),

    register: (): Metadata =>
      generateSEOMetadata({
        title: 'Регистрация',
        description: 'Создайте аккаунт MentorHub и начните своё путешествие в IT-менторстве. Бесплатная регистрация.',
        path: '/auth/register',
        noIndex: true,
      }),

    forgotPassword: (): Metadata =>
      generateSEOMetadata({
        title: 'Восстановление пароля',
        description: 'Восстановите доступ к аккаунту MentorHub.',
        path: '/auth/forgot-password',
        noIndex: true,
      }),
  },

  dashboard: (): Metadata =>
    generateSEOMetadata({
      title: 'Личный кабинет',
      description: 'Управляйте обучением, сессиями с менторами и отслеживайте прогресс.',
      path: '/dashboard',
      noIndex: true,
    }),

  profile: (): Metadata =>
    generateSEOMetadata({
      title: 'Профиль пользователя',
      description: 'Просмотрите и редактируйте свой профиль.',
      path: '/profile',
      noIndex: true,
    }),
}

/**
 * Генерация JSON-LD структурированных данных для Organization
 */
export function generateOrganizationSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'Organization',
    name: SITE_NAME,
    url: BASE_URL,
    logo: `${BASE_URL}/logo.png`,
    description: DEFAULT_DESCRIPTION,
    sameAs: [
      'https://github.com/QuadDarv1ne/MentorHub',
      'https://twitter.com/MentorHubApp',
      'https://linkedin.com/company/mentorhub',
    ],
    contactPoint: {
      '@type': 'ContactPoint',
      contactType: 'Customer Service',
      email: 'support@mentorhub.com',
      availableLanguage: ['Russian', 'English'],
    },
  }
}

/**
 * Генерация JSON-LD для Course
 */
export function generateCourseSchema(course: {
  name: string
  description: string
  provider: string
  url: string
  image?: string
  price?: number
  currency?: string
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Course',
    name: course.name,
    description: course.description,
    provider: {
      '@type': 'Organization',
      name: course.provider,
      sameAs: BASE_URL,
    },
    url: course.url,
    ...(course.image && { image: course.image }),
    ...(course.price !== undefined && {
      offers: {
        '@type': 'Offer',
        price: course.price,
        priceCurrency: course.currency || 'RUB',
      },
    }),
  }
}

/**
 * Генерация JSON-LD для Person (mentor profile)
 */
export function generatePersonSchema(person: {
  name: string
  jobTitle: string
  description: string
  image?: string
  url: string
}) {
  return {
    '@context': 'https://schema.org',
    '@type': 'Person',
    name: person.name,
    jobTitle: person.jobTitle,
    description: person.description,
    ...(person.image && { image: person.image }),
    url: person.url,
    worksFor: {
      '@type': 'Organization',
      name: SITE_NAME,
    },
  }
}
