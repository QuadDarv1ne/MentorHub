'use client';

import {useLocale} from 'next-intl';
import {localeDirections} from '@/lib/i18n/types';
import {ReactNode} from 'react';

interface LocaleProviderProps {
  children: ReactNode;
  locale: string;
}

/**
 * Провайдер для установки направления текста (LTR/RTL)
 * Используется в root layout
 */
export function LocaleProvider({children, locale}: LocaleProviderProps) {
  const direction = localeDirections[locale as keyof typeof localeDirections];

  return (
    <html lang={locale} dir={direction} suppressHydrationWarning>
      <body className={direction === 'rtl' ? 'rtl' : 'ltr'}>
        {children}
      </body>
    </html>
  );
}

/**
 * Хук для получения текущего направления текста
 */
export function useDirection() {
  const locale = useLocale();
  return localeDirections[locale as keyof typeof localeDirections];
}

/**
 * Хук для проверки, является ли текущий язык RTL
 */
export function useIsRTL() {
  const locale = useLocale();
  return locale === 'he';
}
