/**
 * i18n - Интернационализация для MentorHub
 *
 * Экспорт всех i18n утилит из одного места
 */

// Types
export type {Locale} from './types';
export {locales, defaultLocale, localeNames, localeDirections, localeFlags} from './types';

// Hooks
export {useLocale, useIsRussian, useIsEnglish} from './useLocale';
export {useDirection, useIsRTL} from './LocaleProvider';

// Navigation
export {Link, redirect, usePathname, useRouter, localePrefix} from './navigation';

// Provider
export {LocaleProvider} from './LocaleProvider';
