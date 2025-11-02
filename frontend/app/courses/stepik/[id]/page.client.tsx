'use client';

import Link from 'next/link';
import Image from 'next/image';
import type { StepikCourse, StepikInstructor, StepikSection, StepikLesson } from '@/lib/api/stepik';

interface CourseDetailProps {
  course: StepikCourse & {
    instructors: StepikInstructor[];
    syllabus: (StepikSection & {
      lessons: StepikLesson[];
    })[];
  };
}

export default function CourseDetailClient({ course }: CourseDetailProps) {
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
                  {course.review_summary?.average.toFixed(1) || "Нет оценок"} / 5.0
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