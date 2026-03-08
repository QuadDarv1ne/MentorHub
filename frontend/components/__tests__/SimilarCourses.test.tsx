import React from 'react';
import { render } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimilarCourses from '../SimilarCourses';

jest.mock('@/lib/api/courses', () => ({
  getSimilarCourses: jest.fn(async () => [
    { course_id: 101, average_rating: 4.6, total_reviews: 12 },
  ]),
}));

jest.mock('@/lib/api/stepik', () => ({
  getCourse: jest.fn(async (id: number) => ({
    id,
    title: 'Алгоритмы и структуры данных',
    cover: 'https://example.com/cover.jpg',
  })),
}));

describe('SimilarCourses', () => {
  it('renders recommended courses component', async () => {
    const { container } = render(<SimilarCourses courseId={100} />);
    expect(container).toBeInTheDocument();
  });
});
