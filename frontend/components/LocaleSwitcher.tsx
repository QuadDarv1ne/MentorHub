'use client';

import {useLocale} from 'next-intl';
import {useTransition} from 'react';
import {usePathname, useRouter} from '@/lib/i18n/navigation';
import {locales, localeNames, localeFlags, type Locale} from '@/lib/i18n/types';
import {Globe} from 'lucide-react';

/**
 * Компонент переключателя языков
 */
export function LocaleSwitcher() {
  const locale = useLocale();
  const [isPending, startTransition] = useTransition();
  const pathname = usePathname();
  const router = useRouter();

  function onSelectChange(event: React.ChangeEvent<HTMLSelectElement>) {
    const nextLocale = event.target.value as Locale;
    startTransition(() => {
      router.replace(pathname, {locale: nextLocale});
    });
  }

  return (
    <div className="relative inline-flex items-center gap-2">
      <Globe className="h-4 w-4 text-gray-500" />
      <select
        value={locale}
        onChange={onSelectChange}
        disabled={isPending}
        className="appearance-none bg-transparent border border-gray-300 dark:border-gray-600 
                   rounded-md px-3 py-1.5 text-sm font-medium
                   text-gray-700 dark:text-gray-200
                   hover:border-gray-400 dark:hover:border-gray-500
                   focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors duration-200
                   cursor-pointer
                   min-w-[140px]"
        aria-label="Select language"
        dir="ltr"
      >
        {locales.map((loc) => (
          <option key={loc} value={loc} dir={loc === 'he' ? 'rtl' : 'ltr'}>
            {localeFlags[loc]} {localeNames[loc]}
          </option>
        ))}
      </select>
    </div>
  );
}
