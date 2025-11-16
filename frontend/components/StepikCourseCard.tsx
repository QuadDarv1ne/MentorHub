import Link from 'next/link';
import Image from 'next/image';
import { Star, Users, ExternalLink, BookOpen, Clock } from 'lucide-react';
import { useState } from 'react';

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
  duration?: string; // Новое: длительность курса
  level?: 'beginner' | 'intermediate' | 'advanced'; // Новое: уровень сложности
  isFavorite?: boolean; // Новое: избранное
  onFavoriteToggle?: (id: string) => void; // Новое: callback для избранного
  tags?: string[]; // Новое: теги курса
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
  duration,
  level = 'beginner',
  isFavorite = false,
  onFavoriteToggle,
  tags = [],
}: StepikCourseCardProps) {
  const [isImageError, setIsImageError] = useState(false);
  const [isFavorited, setIsFavorited] = useState(isFavorite);

  // Форматирование чисел
  const formatStudentsCount = (count: number): string => {
    if (count >= 1000) {
      return `${(count / 1000).toFixed(1)}k`;
    }
    return count.toString();
  };

  // Цвета для уровня сложности
  const levelColors = {
    beginner: 'bg-green-100 text-green-800',
    intermediate: 'bg-yellow-100 text-yellow-800',
    advanced: 'bg-red-100 text-red-800',
  };

  const levelLabels = {
    beginner: 'Начальный',
    intermediate: 'Средний',
    advanced: 'Продвинутый',
  };

  // Обработчик избранного
  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsFavorited(!isFavorited);
    onFavoriteToggle?.(id);
  };

  return (
    <article className="bg-white overflow-hidden shadow-md rounded-xl flex flex-col hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 group">
      {/* Изображение курса */}
      <div className="relative h-48 overflow-hidden bg-gradient-to-br from-indigo-100 to-purple-100">
        {imageUrl && !isImageError ? (
          <Image
            src={imageUrl}
            alt={title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            onError={() => setIsImageError(true)}
            sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <BookOpen className="w-16 h-16 text-indigo-400" />
          </div>
        )}
        
        {/* Бейджи сверху */}
        <div className="absolute top-3 left-3 right-3 flex justify-between items-start">
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-white/90 backdrop-blur-sm text-indigo-700 shadow-sm">
            {category}
          </span>
          
          {/* Кнопка избранного */}
          {onFavoriteToggle && (
            <button
              onClick={handleFavoriteClick}
              className="p-2 rounded-full bg-white/90 backdrop-blur-sm hover:bg-white transition-colors shadow-sm"
              aria-label={isFavorited ? 'Удалить из избранного' : 'Добавить в избранное'}
            >
              <svg 
                className={`w-5 h-5 ${isFavorited ? 'fill-red-500 text-red-500' : 'text-gray-400'}`}
                fill={isFavorited ? 'currentColor' : 'none'}
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" 
                />
              </svg>
            </button>
          )}
        </div>

        {/* Бейдж уровня */}
        <div className="absolute bottom-3 left-3">
          <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium ${levelColors[level]}`}>
            {levelLabels[level]}
          </span>
        </div>
      </div>

      {/* Контент */}
      <div className="p-5 flex-grow flex flex-col">
        {/* Заголовок */}
        <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-indigo-600 transition-colors">
          {title}
        </h3>
        
        {/* Описание */}
        <p className="text-sm text-gray-600 mb-4 line-clamp-2 flex-grow">
          {description}
        </p>

        {/* Теги */}
        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {tags.slice(0, 3).map((tag, index) => (
              <span 
                key={index}
                className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
              >
                {tag}
              </span>
            ))}
            {tags.length > 3 && (
              <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-500">
                +{tags.length - 3}
              </span>
            )}
          </div>
        )}
        
        {/* Метрики курса */}
        <div className="flex items-center gap-4 mb-4 text-sm text-gray-600">
          {/* Рейтинг */}
          <div className="flex items-center gap-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            <span className="font-medium text-gray-900">{rating.toFixed(1)}</span>
          </div>
          
          {/* Количество студентов */}
          <div className="flex items-center gap-1">
            <Users className="w-4 h-4 text-gray-400" />
            <span>{formatStudentsCount(studentsCount)}</span>
          </div>

          {/* Длительность */}
          {duration && (
            <div className="flex items-center gap-1">
              <Clock className="w-4 h-4 text-gray-400" />
              <span>{duration}</span>
            </div>
          )}
        </div>

        {/* Цена и кнопки */}
        <div className="mt-auto pt-4 border-t border-gray-100">
          <div className="flex items-center justify-between mb-3">
            <div>
              {price === 0 ? (
                <span className="text-lg font-bold text-green-600">Бесплатно</span>
              ) : (
                <div className="flex items-baseline gap-1">
                  <span className="text-2xl font-bold text-gray-900">{price.toLocaleString('ru-RU')}</span>
                  <span className="text-sm text-gray-500">₽</span>
                </div>
              )}
            </div>
          </div>

          {/* Кнопки действий */}
          <div className="flex gap-2">
            <a
              href={stepikUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 inline-flex items-center justify-center gap-2 bg-indigo-600 py-2.5 px-4 rounded-lg text-sm font-semibold text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
            >
              Stepik
              <ExternalLink className="w-4 h-4" />
            </a>
            <Link
              href={`/courses/stepik/${id}`}
              className="flex-1 inline-flex items-center justify-center bg-white py-2.5 px-4 border-2 border-gray-200 rounded-lg text-sm font-semibold text-gray-700 hover:border-indigo-300 hover:text-indigo-600 hover:bg-indigo-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all"
            >
              Подробнее
            </Link>
          </div>
        </div>
      </div>

      {/* Индикатор новизны (опционально) */}
      {/* Можно добавить, если есть поле isNew */}
      {/* {isNew && (
        <div className="absolute top-0 right-0 bg-gradient-to-br from-pink-500 to-rose-500 text-white px-3 py-1 text-xs font-bold rounded-bl-lg rounded-tr-lg">
          НОВИНКА
        </div>
      )} */}
    </article>
  );
}