import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import Footer from '@/components/Footer'
import { NotificationProvider } from '@/components/NotificationProvider'
import { GlobalLoadingProvider } from '@/components/GlobalLoadingProvider'
import { ThemeProvider } from '@/components/ThemeProvider'
import ServiceWorkerProvider from '@/components/ServiceWorkerProvider'
import { SkipLinks, RouteAnnouncer } from '@/lib/utils/accessibility'

const inter = Inter({ subsets: ['latin', 'cyrillic'], variable: '--font-inter' })

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
  themeColor: '#4f46e5',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" className={inter.variable} suppressHydrationWarning>
      <head>
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#4f46e5" />
        <link rel="apple-touch-icon" href="/icon-192x192.png" />
      </head>
      <body className="antialiased">
        <ThemeProvider defaultTheme="system">
          <SkipLinks />
          <RouteAnnouncer />
          <GlobalLoadingProvider>
            <NotificationProvider>
              <Header />
              <main id="main-content" tabIndex={-1} className="focus:outline-none">
                {children}
              </main>
              <Footer />
              <ServiceWorkerProvider />
            </NotificationProvider>
          </GlobalLoadingProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}