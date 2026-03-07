import createMiddleware from 'next-intl/middleware';

export default createMiddleware({
  // Список поддерживаемых локалей
  locales: ['ru', 'en', 'zh', 'he'],

  // Локаль по умолчанию
  defaultLocale: 'ru',

  // Префикс URL всегда (кроме defaultLocale при localePrefix: 'as-needed')
  localePrefix: 'always',

  // Определение локали из заголовков
  localeDetection: true,
});

export const config = {
  // Матчер для всех маршрутов кроме api, static файлов и файлов с точкой
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'],
};
