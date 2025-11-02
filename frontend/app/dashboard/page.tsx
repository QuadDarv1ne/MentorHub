import { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Личный кабинет | MentorHub',
  description: 'Управление аккаунтом и настройками на платформе MentorHub'
}

export default function DashboardPage() {
  return (
    <div className="min-h-screen bg-gray-100">
      <div className="py-10">
        <header>
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h1 className="text-3xl font-bold leading-tight text-gray-900">Личный кабинет</h1>
          </div>
        </header>
        <main>
          <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div className="px-4 py-8 sm:px-0">
              <div className="border-4 border-dashed border-gray-200 rounded-lg h-96">
                {/* Заглушка контента */}
                <div className="flex items-center justify-center h-full">
                  <p className="text-gray-500">Здесь будет контент личного кабинета</p>
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  )
}