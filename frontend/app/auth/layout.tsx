export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex flex-col min-h-screen">
        <div className="py-4 px-4 sm:px-6 lg:px-8 border-b border-gray-200 bg-white">
          <a href="/" className="flex items-center space-x-2">
            <span className="text-2xl font-bold text-indigo-600">MentorHub</span>
          </a>
        </div>
        <main className="flex-grow">{children}</main>
      </div>
    </div>
  )
}