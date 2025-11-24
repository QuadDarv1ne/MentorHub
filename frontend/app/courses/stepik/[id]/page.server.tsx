import { getCourseDetails } from '@/lib/api/stepik';

export async function generateMetadata({ params }: { params: { id: string } }) {
  try {
    const course = await getCourseDetails(Number(params.id));
    return {
      title: `${course.title} | MentorHub`,
      description: course.description,
    };
  } catch {
    return {
      title: 'Курс не найден | MentorHub',
      description: 'Запрашиваемый курс не найден',
    };
  }
}

async function getCourseData(id: string) {
  try {
    return {
      course: await getCourseDetails(Number(id)),
      error: null,
    };
  } catch (error) {
    console.error("Ошибка при загрузке курса:", error);
    return {
      course: null,
      error: error instanceof Error ? error.message : "Произошла ошибка при загрузке курса",
    };
  }
}

export default async function Page({ params }: { params: { id: string } }) {
  const { course, error } = await getCourseData(params.id);

  if (error || !course) {
    return {
      notFound: true,
    };
  }

  return {
    props: {
      course,
    },
  };
}