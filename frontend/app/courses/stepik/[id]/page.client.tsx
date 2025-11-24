'use client';

import Link from 'next/link';
import Image from 'next/image';
import type { StepikCourse, StepikInstructor, StepikSection, StepikLesson } from '@/lib/api/stepik';
import ReviewList from '@/components/ReviewList';
import ReviewForm from '@/components/ReviewForm';
import { useState, useEffect } from 'react';

interface CourseDetailProps {
  course: StepikCourse & {
    instructors: StepikInstructor[];
    syllabus: (StepikSection & {
      lessons: StepikLesson[];
    })[];
  };
}

export default function CourseDetailClient({ course }: CourseDetailProps) {
  const [reloadReviewsKey, setReloadReviewsKey] = useState(0);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [aggregate, setAggregate] = useState<{ average_rating: number; total_reviews: number } | null>(null);

  useEffect(() => {
    // Check localStorage token for simple auth check
    try {
      const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
      setIsAuthenticated(Boolean(token));
    } catch {
      setIsAuthenticated(false);
    }

    // Fetch aggregated rating from backend
    const fetchAgg = async () => {
      try {
        const res = await fetch(`/api/v1/courses/${course.id}/reviews/aggregate`);
        if (!res.ok) return;
        const data = await res.json();
        setAggregate({ average_rating: data.average_rating, total_reviews: data.total_reviews });
      } catch {
        // ignore
      }
    };

    fetchAgg();
  }, [course.id, reloadReviewsKey]);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-8">
        {/* Хлебные крошки */}
        <div className="text-sm text-gray-600 mb-6">
          <Link href="/courses" className="hover:text-primary-600">
            Курсы
          </Link>
          <span className="mx-2">/</span>
          <Link href="/courses/stepik" className="hover:text-primary-600">
            Stepik
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{course.title}</span>
        </div>

        {/* Заголовок курса */}
        <h1 className="text-3xl font-bold text-gray-900 mb-6">{course.title}</h1>

        {/* Основная информация */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              {course.cover && (
                <div className="relative h-48 md:h-64 rounded-lg overflow-hidden mb-4">
                  <Image
                    src={course.cover}
                    alt={course.title}
                    layout="fill"
                    objectFit="cover"
                  />
                </div>
              )}
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-semibold">Преподаватели:</span>{" "}
                  {course.instructors.map(instructor => instructor.name).join(", ")}
                </p>
                <p className="text-gray-600">
                  <span className="font-semibold">Рейтинг:</span>{" "}
                  {aggregate && aggregate.total_reviews > 0 ? (
                    <>{aggregate.average_rating.toFixed(1)} / 5.0 ({aggregate.total_reviews} отзывов)</>
                  ) : course.review_summary?.average ? (
                    <>{course.review_summary.average.toFixed(1)} / 5.0 (stepik)</>
                  ) : (
                    <>Нет оценок</>
                  )}
                </p>
                <p className="text-gray-600">
                  <span className="font-semibold">Студентов:</span>{" "}
                  {course.learners_count}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">О курсе</h3>
                <p className="text-gray-600">{course.description}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Детали</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>
                    <span className="font-medium">Формат:</span> {course.course_format}
                  </li>
                  <li>
                    <span className="font-medium">Язык:</span> {course.language}
                  </li>
                  <li>
                    <span className="font-medium">Нагрузка:</span> {course.workload}
                  </li>
                  <li>
                    <span className="font-medium">Стоимость:</span>{" "}
                    {course.price ? `${course.price} ₽` : "Бесплатно"}
                  </li>
                  <li>
                    <span className="font-medium">Сертификат:</span>{" "}
                    {course.is_certificate_issued ? "Выдается" : "Не выдается"}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Требования и пререквизиты */}
        {(course.requirements || course.prerequisites) && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Требования к курсу</h2>
            <div className="space-y-4">
              {course.requirements && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Необходимые знания</h3>
                  <p className="text-gray-600">{course.requirements}</p>
                </div>
              )}
              {course.prerequisites && (
                <div>
                  <h3 className="text-lg font-semibold mb-2">Предварительные требования</h3>
                  <p className="text-gray-600">{course.prerequisites}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Целевая аудитория */}
        {course.target_audience && (
          <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
            <h2 className="text-2xl font-bold mb-4">Для кого этот курс</h2>
            <p className="text-gray-600">{course.target_audience}</p>
          </div>
        )}

        {/* Программа курса */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-4">Программа курса</h2>
          <div className="space-y-6">
            {course.syllabus.map((section, index) => (
              <div key={index} className="border-b border-gray-200 pb-4 last:border-0">
                <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                <ul className="space-y-2">
                  {section.lessons.map((lesson, lessonIndex) => (
                    <li key={lessonIndex} className="text-gray-600 ml-4">
                      • {lesson.title}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        {/* Отзывы */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <ReviewList key={reloadReviewsKey} courseId={course.id} />
          </div>
          <div>
              {isAuthenticated ? (
              <ReviewForm courseId={course.id} onSuccess={() => setReloadReviewsKey(k => k + 1)} />
            ) : (
              <div className="bg-white p-4 rounded shadow text-center">
                <p className="mb-2">Пожалуйста, войдите в систему, чтобы оставить отзыв.</p>
                <button onClick={() => (window.location.href = '/auth/login')} className="px-4 py-2 bg-primary-600 text-white rounded">Войти</button>
              </div>
            )}
          </div>
        </div>

        {/* Кнопка записи на курс */}
        <div className="mt-8 text-center">
          <a
            href={`https://stepik.org/course/${course.id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-block bg-primary-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
          >
            Записаться на курс
          </a>
        </div>
      </div>
    </div>
  );
}