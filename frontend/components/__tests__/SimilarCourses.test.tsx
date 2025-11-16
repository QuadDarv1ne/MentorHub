import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
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
  it('renders recommended courses with Stepik title', async () => {
    render(<SimilarCourses courseId={100} />);
    // initial loading
    expect(screen.getByRole('status')).toBeInTheDocument();

    await waitFor(() => {
      expect(
        screen.getByText('Алгоритмы и структуры данных')
      ).toBeInTheDocument();
    });

    // rating and reviews visible
    expect(screen.getByText(/⭐ 4\.6/)).toBeInTheDocument();
    expect(screen.getByText(/Отзывов: 12/)).toBeInTheDocument();

    // link to course page exists
    const link = screen.getByRole('link');
    expect(link).toHaveAttribute('href', '/courses/stepik/101');
  });
});
