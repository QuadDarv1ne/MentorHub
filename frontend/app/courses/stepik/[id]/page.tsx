'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { useState, useEffect } from 'react';
import Image from 'next/image';
import { getCourseDetails, StepikCourse, StepikInstructor, StepikSection, StepikLesson } from '@/lib/api/stepik';

interface CourseDetails extends StepikCourse {
  instructors: StepikInstructor[];
  syllabus: (StepikSection & {
    lessons: StepikLesson[];
  })[];
}

export default function CourseDetail() {
  const params = useParams();
  const [courseData, setCourseData] = useState<Awaited<ReturnType<typeof getCourseDetails>> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const data = await getCourseDetails(Number(params.id));
        setCourseData(data);
      } catch (err) {
        console.error("Ошибка при загрузке курса:", err);
        setError(err instanceof Error ? err.message : "Произошла ошибка при загрузке курса");
      } finally {
        setIsLoading(false);
      }
    };

    if (params.id) {
      fetchCourse();
    }
  }, [params.id]);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-full mb-2"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!courseData) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Курс не найден
          </h1>
          <Link href="/courses/stepik" className="text-primary-600 hover:text-primary-700">
            Вернуться к списку курсов
          </Link>
        </div>
      </div>
    );
  }

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
          <span className="text-gray-900">{courseData.title}</span>
        </div>

        {/* Заголовок курса */}
        <h1 className="text-3xl font-bold text-gray-900 mb-6">{courseData.title}</h1>

        {/* Основная информация */}
        <div className="bg-white rounded-lg shadow-sm p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              {courseData.cover && (
                <div className="relative h-48 md:h-64 rounded-lg overflow-hidden mb-4">
                  <Image
                    src={courseData.cover}
                    alt={courseData.title}
                    layout="fill"
                    objectFit="cover"
                  />
                </div>
              )}
              <div className="space-y-2">
                <p className="text-gray-600">
                  <span className="font-semibold">Преподаватели:</span>{" "}
                  {courseData.instructors.map((instructor) => instructor.name).join(", ")}
                </p>
                <p className="text-gray-600">
                  <span className="font-semibold">Рейтинг:</span>{" "}
                  {courseData.rating} / 5.0
                </p>
                <p className="text-gray-600">
                  <span className="font-semibold">Студентов:</span>{" "}
                  {courseData.learners_count}
                </p>
              </div>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-lg font-semibold mb-2">О курсе</h3>
                <p className="text-gray-600">{courseData.description}</p>
              </div>
              <div>
                <h3 className="text-lg font-semibold mb-2">Детали</h3>
                <ul className="space-y-2 text-gray-600">
                  <li>
                    <span className="font-medium">Длительность:</span> {courseData.duration}
                  </li>
                  <li>
                    <span className="font-medium">Язык:</span> {courseData.language}
                  </li>
                  <li>
                    <span className="font-medium">Уровень:</span> {courseData.course_format}
                  </li>
                  <li>
                    <span className="font-medium">Стоимость:</span>{" "}
                    {courseData.price ? `${courseData.price} ₽` : "Бесплатно"}
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>



        {/* Программа курса */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          <h2 className="text-2xl font-bold mb-4">Программа курса</h2>
          <div className="space-y-6">
            {courseData.syllabus?.map((section: any, index: number) => (
              <div key={index} className="border-b border-gray-200 pb-4 last:border-0">
                <h3 className="text-lg font-semibold mb-2">{section.title}</h3>
                <ul className="space-y-2">
                  {section.lessons?.map((lesson: any, lessonIndex: number) => (
                    <li key={lessonIndex} className="text-gray-600 ml-4">
                      • {lesson.title}
                    </li>
                  )) || []}
                </ul>
              </div>
            )) || []}
          </div>
        </div>

        {/* Кнопка записи на курс */}
        <div className="mt-8 text-center">
          <a
            href={`https://stepik.org/course/${params.id}`}
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