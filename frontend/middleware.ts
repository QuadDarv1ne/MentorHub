// Временно отключено до миграции на [locale] роутинг
// import createMiddleware from 'next-intl/middleware';

// export default createMiddleware({
//   locales: ['ru', 'en', 'zh', 'he'],
//   defaultLocale: 'ru',
//   localePrefix: 'always',
//   localeDetection: true,
// });

export function middleware() {
  // Пустой middleware пока i18n не настроен на уровне роутинга
}

export const config = {
  matcher: [],
};
