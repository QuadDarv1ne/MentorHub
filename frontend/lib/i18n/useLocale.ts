'use client';

import {useLocale as useNextLocale} from 'next-intl';
import {Locale} from './types';

/**
 * Хук для получения текущей локали
 * @returns Текущая локаль
 */
export function useLocale() {
  return useNextLocale() as Locale;
}

/**
 * Проверка, является ли текущая локаль русской
 */
export function useIsRussian() {
  const locale = useLocale();
  return locale === 'ru';
}

/**
 * Проверка, является ли текущая локаль английской
 */
export function useIsEnglish() {
  const locale = useLocale();
  return locale === 'en';
}
