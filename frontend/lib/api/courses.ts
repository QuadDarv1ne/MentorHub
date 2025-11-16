export type SimilarCourse = {
  course_id: number;
  average_rating: number;
  total_reviews: number;
};

export async function getSimilarCourses(courseId: number, limit = 5): Promise<SimilarCourse[]> {
  const res = await fetch(`/api/v1/courses/${courseId}/similar?limit=${limit}`, {
    headers: {
      'Content-Type': 'application/json',
    },
  });
  if (!res.ok) throw new Error('Failed to fetch similar courses');
  return res.json();
}
