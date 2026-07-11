import type { Metadata, Viewport } from 'next'
import { Inter } from 'next/font/google'
import { NextIntlClientProvider } from 'next-intl'
import { getLocale, getMessages } from 'next-intl/server'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import { NotificationProvider } from '@/components/NotificationProvider'
import { GlobalLoadingProvider } from '@/components/GlobalLoadingProvider'
import { ThemeProvider } from '@/components/ThemeProvider'
import { ToastProvider } from '@/components/ui/ToastContext'
import ServiceWorkerProvider from '@/components/ServiceWorkerProvider'
import { SkipLinks, RouteAnnouncer } from '@/lib/utils/accessibility'
import AuthClientInitializer from '@/components/AuthClientInitializer'
import { localeDirections } from '@/lib/i18n/types'

const inter = Inter({ subsets: ['latin', 'cyrillic'], variable: '--font-inter' })

export const dynamic = 'force-dynamic'

export const viewport: Viewport = {
  themeColor: '#4f46e5',
}

export const metadata: Metadata = {
  title: 'MentorHub - Платформа для профессионального менторства в IT',
  description: 'Соединяем опытных IT-специалистов с теми, кто стремится развивать свои навыки и построить карьеру в технологиях',
  keywords: ['менторство', 'IT', 'обучение', 'карьера', 'разработка', 'программирование'],
  manifest: '/manifest.json',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'MentorHub',
  },
  formatDetection: {
    telephone: false,
  },
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const locale = await getLocale()
  const messages = await getMessages()
  const direction = localeDirections[locale as keyof typeof localeDirections]

  return (
    <html lang={locale} dir={direction} className={inter.variable} suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#4f46e5" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body className={`antialiased ${direction === 'rtl' ? 'rtl' : 'ltr'}`}>
        <NextIntlClientProvider locale={locale} messages={messages}>
          <ThemeProvider defaultTheme="system">
            <AuthClientInitializer />
            <SkipLinks />
            <RouteAnnouncer />
            <GlobalLoadingProvider>
              <ToastProvider>
                <NotificationProvider>
                  <Header />
                  <main id="main-content" tabIndex={-1} className="focus:outline-none">
                    {children}
                  </main>
                  <Footer />
                  <ServiceWorkerProvider />
                </NotificationProvider>
              </ToastProvider>
            </GlobalLoadingProvider>
          </ThemeProvider>
        </NextIntlClientProvider>
      </body>
    </html>
  )
}