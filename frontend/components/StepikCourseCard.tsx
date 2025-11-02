import Link from 'next/link';

interface StepikCourseCardProps {
  id: string;
  title: string;
  description: string;
  imageUrl?: string;
  price: number;
  studentsCount: number;
  rating: number;
  stepikUrl: string;
  category: string;
}

export default function StepikCourseCard({
  id,
  title,
  description,
  imageUrl,
  price,
  studentsCount,
  rating,
  stepikUrl,
  category,
}: StepikCourseCardProps) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg flex flex-col">
      {/* Изображение курса */}
      <div className="aspect-w-16 aspect-h-9 relative">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt={title}
            className="w-full h-48 object-cover"
          />
        ) : (
          <div className="w-full h-48 bg-indigo-100 flex items-center justify-center">
            <span className="text-indigo-600 font-semibold text-lg">{title.charAt(0)}</span>
          </div>
        )}
        <div className="absolute top-4 right-4">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800">
            {category}
          </span>
        </div>
      </div>

      {/* Контент */}
      <div className="p-6 flex-grow">
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          {title}
        </h3>
        <p className="text-sm text-gray-500 mb-4 line-clamp-2">
          {description}
        </p>
        
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <div className="flex items-center">
              <svg className="h-4 w-4 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span className="ml-1 text-sm text-gray-500">{rating.toFixed(1)}</span>
            </div>
            <span className="text-sm text-gray-500">•</span>
            <span className="text-sm text-gray-500">{studentsCount} учеников</span>
          </div>
          <span className="text-lg font-medium text-gray-900">
            {price === 0 ? 'Бесплатно' : `${price} ₽`}
          </span>
        </div>

        <div className="flex space-x-3">
          <a
            href={stepikUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-1 bg-indigo-600 py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 text-center"
          >
            Перейти на Stepik
          </a>
          <Link
            href={`/courses/stepik/${id}`}
            className="flex-1 bg-white py-2 px-4 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 text-center"
          >
            Подробнее
          </Link>
        </div>
      </div>
    </div>
  )
}