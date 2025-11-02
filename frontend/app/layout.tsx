import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin', 'cyrillic'], variable: '--font-inter' })

export const metadata: Metadata = {
  title: 'MentorHub - Платформа для профессионального менторства в IT',
  description: 'Соединяем опытных IT-специалистов с теми, кто стремится развивать свои навыки и построить карьеру в технологиях',
  keywords: ['менторство', 'IT', 'обучение', 'карьера', 'разработка', 'программирование'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ru" className={inter.variable}>
      <body className="antialiased">{children}</body>
    </html>
  )
}

