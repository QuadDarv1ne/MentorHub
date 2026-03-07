import {getRequestConfig} from 'next-intl/server';

export default getRequestConfig(async ({locale}) => ({
  messages: (await import(`./messages/${locale}.json`)).default
}));

// Временное решение: используем русский по умолчанию
// Для полной i18n поддержки нужно добавить [locale] роутинг
