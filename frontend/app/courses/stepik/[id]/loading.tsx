export default function Loading() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="animate-pulse">
          {/* Хлебные крошки */}
          <div className="h-4 bg-gray-200 rounded w-1/4 mb-8"></div>

          {/* Заголовок */}
          <div className="h-8 bg-gray-200 rounded w-3/4 mb-8"></div>

          {/* Основная информация */}
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                {/* Изображение */}
                <div className="h-48 md:h-64 bg-gray-200 rounded-lg mb-4"></div>
                {/* Информация об инструкторах */}
                <div className="space-y-2">
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                </div>
              </div>

              <div className="space-y-4">
                {/* О курсе */}
                <div>
                  <div className="h-6 bg-gray-200 rounded w-1/4 mb-2"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-full"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>

                {/* Детали */}
                <div>
                  <div className="h-6 bg-gray-200 rounded w-1/4 mb-2"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Программа курса */}
          <div className="bg-white rounded-lg shadow-sm p-6">
            <div className="h-6 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="space-y-4">
              {[1, 2, 3].map((_, index) => (
                <div key={index}>
                  <div className="h-5 bg-gray-200 rounded w-1/2 mb-2"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                    <div className="h-4 bg-gray-200 rounded w-2/3"></div>
                    <div className="h-4 bg-gray-200 rounded w-1/2"></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}