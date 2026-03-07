export type Locale = 'ru' | 'en' | 'zh' | 'he';

export const locales: Locale[] = ['ru', 'en', 'zh', 'he'];

export const defaultLocale: Locale = 'ru';

export const localeNames: Record<Locale, string> = {
  ru: 'Русский',
  en: 'English',
  zh: '简体中文',
  he: 'עברית',
};

export const localeDirections: Record<Locale, 'ltr' | 'rtl'> = {
  ru: 'ltr',
  en: 'ltr',
  zh: 'ltr',
  he: 'rtl',
};

export const localeFlags: Record<Locale, string> = {
  ru: '🇷🇺',
  en: '🇬🇧',
  zh: '🇨🇳',
  he: '🇮🇱',
};
