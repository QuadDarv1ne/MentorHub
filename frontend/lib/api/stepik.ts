import { cache } from '../cache';

// Use internal API routes with absolute URL for server-side rendering
const API_BASE = 'http://localhost:3000/api/stepik';

const CACHE_KEYS = {
  course: (id: number) => `stepik:course:${id}`,
  courseList: (page: number) => `stepik:courses:page:${page}`,
  instructor: (id: number) => `stepik:instructor:${id}`,
  sections: (courseId: number) => `stepik:sections:${courseId}`,
  lessons: (ids: number[]) => `stepik:lessons:${ids.join(',')}`,
};

export interface StepikCourse {
  id: number;
  title: string;
  description: string;
  cover: string;
  summary: string;
  course_format: string;
  target_audience: string;
  is_public: boolean;
  language: string;
  is_certificate_issued: boolean;
  instructors: number[] | StepikInstructor[];
  sections: number[] | StepikSection[];
  lessons: number[] | StepikLesson[];
  learners_count: number;
  rating: number;
  review_summary: {
    average: number;
    total: number;
    distribution: number[];
  };
  price: number | null;
  duration: number;
  requirements: string;
  prerequisites: string;
  workload: string;
}

export interface StepikInstructor {
  id: number;
  name: string;
  avatar: string;
  bio: string;
}

export interface StepikSection {
  id: number;
  title: string;
  position: number;
  lessons: number[] | StepikLesson[];
}

export interface StepikLesson {
  id: number;
  title: string;
  position: number;
}

interface ApiResponse<T> {
  meta: {
    page: number;
    has_next: boolean;
    has_previous: boolean;
  };
  courses?: T[];
  users?: T[];
  sections?: T[];
  units?: T[];
  lessons?: T[];
}

/**
 * Получает информацию о курсе по его ID
 */
export async function getCourse(courseId: number): Promise<StepikCourse> {
  const cacheKey = CACHE_KEYS.course(courseId);
  const cachedData = cache.get<StepikCourse>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  const response = await fetch(`${API_BASE}/courses/${courseId}`);
  if (!response.ok) {
    throw new Error(`Ошибка при получении курса: ${response.statusText}`);
  }
  const data = await response.json();
  const course = data.courses[0];
  
  cache.set(cacheKey, course);
  return course;
}

/**
 * Получает список курсов с пагинацией
 */
export async function getCourses(page: number = 1): Promise<ApiResponse<StepikCourse>> {
  const cacheKey = CACHE_KEYS.courseList(page);
  const cachedData = cache.get<ApiResponse<StepikCourse>>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  const response = await fetch(
    `${API_BASE}/courses/${page}?language=ru`
  );
  if (!response.ok) {
    throw new Error(`Ошибка при получении списка курсов: ${response.statusText}`);
  }
  const data = await response.json();
  
  cache.set(cacheKey, data);
  return data;
}

/**
 * Получает информацию об инструкторах курса
 */
export async function getInstructors(instructorIds: number[]): Promise<StepikInstructor[]> {
  const cacheKey = CACHE_KEYS.instructor(instructorIds[0]); // Используем первый ID как ключ
  const cachedData = cache.get<StepikInstructor[]>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  const response = await fetch(
    `${API_BASE}/users?ids=${instructorIds.join(',')}`
  );
  if (!response.ok) {
    throw new Error(`Ошибка при получении информации об инструкторах: ${response.statusText}`);
  }
  const data = await response.json();
  
  cache.set(cacheKey, data.users);
  return data.users;
}

/**
 * Получает разделы курса
 */
export async function getCourseSections(courseId: number): Promise<StepikSection[]> {
  const cacheKey = CACHE_KEYS.sections(courseId);
  const cachedData = cache.get<StepikSection[]>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  const response = await fetch(
    `${API_BASE}/sections?course=${courseId}`
  );
  if (!response.ok) {
    throw new Error(`Ошибка при получении разделов курса: ${response.statusText}`);
  }
  const data = await response.json();
  
  cache.set(cacheKey, data.sections);
  return data.sections;
}

/**
 * Получает уроки для разделов
 */
export async function getLessons(lessonIds: number[]): Promise<StepikLesson[]> {
  // If no lesson IDs, return empty array
  if (lessonIds.length === 0) {
    return [];
  }
  
  const cacheKey = CACHE_KEYS.lessons(lessonIds);
  const cachedData = cache.get<StepikLesson[]>(cacheKey);
  if (cachedData) {
    return cachedData;
  }

  const response = await fetch(
    `${API_BASE}/lessons?ids=${lessonIds.join(',')}`
  );
  if (!response.ok) {
    throw new Error(`Ошибка при получении уроков: ${response.statusText}`);
  }
  const data = await response.json();
  
  cache.set(cacheKey, data.lessons);
  return data.lessons;
}

/**
 * Получает полную информацию о курсе, включая инструкторов и программу
 */
export async function getCourseDetails(courseId: number) {
  try {
    // Получаем основную информацию о курсе
    const course = await getCourse(courseId);

    // Получаем информацию об инструкторах
    let instructors: StepikInstructor[] = [];
    if (Array.isArray(course.instructors) && course.instructors.length > 0) {
      if (typeof course.instructors[0] === 'number') {
        instructors = await getInstructors(course.instructors as number[]);
      } else {
        instructors = course.instructors as StepikInstructor[];
      }
    }

    // Получаем разделы курса
    const sections = await getCourseSections(courseId);

    // Получаем все уроки для всех разделов (нормализуем ids)
    const lessonIds: number[] = sections.flatMap((section) => {
      if (!Array.isArray(section.lessons) || section.lessons.length === 0) return [];
      const first = section.lessons[0];
      if (typeof first === 'number') {
        return section.lessons as number[];
      }
      // уроки уже объекты
      return (section.lessons as StepikLesson[]).map((l) => l.id);
    }).filter(id => id !== undefined && id !== null); // Filter out any undefined or null IDs

    const lessons = await getLessons(lessonIds);

    // Формируем структурированную программу курса
    const syllabus = sections.map((section) => {
      const sectionLessons: StepikLesson[] = (Array.isArray(section.lessons) && section.lessons.length && typeof section.lessons[0] === 'number')
        ? (section.lessons as number[]).map((id) => lessons.find((l) => l.id === id)).filter((l): l is StepikLesson => !!l)
        : (section.lessons as StepikLesson[]).map((l) => {
            // if it's already an object, try to find the canonical lesson object returned by getLessons, fallback to itself
            const foundLesson = lessons.find((x) => x.id === (l as StepikLesson).id);
            return foundLesson || (l as StepikLesson);
          });

      return {
        ...section,
        lessons: sectionLessons.sort((a, b) => a.position - b.position),
      };
    }).sort((a, b) => a.position - b.position);

    return {
      ...course,
      instructors,
      syllabus
    };
  } catch (error) {
    console.error('Ошибка при получении детальной информации о курсе:', error);
    throw error;
  }
}