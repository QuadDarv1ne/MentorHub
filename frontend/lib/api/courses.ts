export interface SimilarCourse {
  course_id: number;
  average_rating: number;
  total_reviews: number;
}

/**
 * Заглушка для getSimilarCourses
 * TODO: реализовать логику подбора похожих курсов
 */
export async function getSimilarCourses(_courseId: number): Promise<SimilarCourse[]> {
  return [];
}

export interface Course {
  id: number;
  title: string;
  description: string;
  progress: number;
  certificate?: boolean;
}

export async function getMyCourses(): Promise<Course[]> {
  return [];
}

export async function getCourse(id: number): Promise<Course> {
  return { id, title: '', description: '', progress: 0 };
}
