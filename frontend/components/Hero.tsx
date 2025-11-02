'use client'

import Link from 'next/link'
import { ArrowRight } from 'lucide-react'

export default function Hero() {
  return (
    <section className="bg-gradient-to-b from-primary-50 to-white section-padding">
      <div className="container-custom">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
            Тренажёр для подготовки<br />
            <span className="text-primary-600">к техническим собеседованиям</span>
          </h1>
          
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            Подготовиться к собеседованию
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/register" className="btn-primary text-lg px-8 py-4 inline-flex items-center justify-center group">
              Начать подготовку
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/mentors" className="btn-secondary text-lg px-8 py-4">
              Найти ментора
            </Link>
          </div>
        </div>
      </div>
    </section>
  )
}

