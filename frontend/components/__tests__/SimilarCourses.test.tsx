import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SimilarCourses from '../SimilarCourses';

jest.mock('@/lib/api/courses', () => ({
  getSimilarCourses: jest.fn(),
}));

jest.mock('@/lib/api/stepik', () => ({
  getCourse: jest.fn(),
}));

import { getSimilarCourses } from '@/lib/api/courses';
import { getCourse } from '@/lib/api/stepik';

describe('SimilarCourses', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading skeleton initially', () => {
    (getSimilarCourses as jest.Mock).mockReturnValue(new Promise(() => {}));
    render(<SimilarCourses courseId={100} />);
    expect(screen.getByText('Похожие курсы')).toBeInTheDocument();
    const skeletons = screen.getAllByRole('status');
    expect(skeletons.length).toBeGreaterThanOrEqual(1);
  });

  it('renders similar courses with details', async () => {
    (getSimilarCourses as jest.Mock).mockResolvedValue([
      { course_id: 101, average_rating: 4.6, total_reviews: 12 },
    ]);
    (getCourse as jest.Mock).mockResolvedValue({
      id: 101,
      title: 'Алгоритмы и структуры данных',
      cover: 'https://example.com/cover.jpg',
    });
    render(<SimilarCourses courseId={100} />);
    await waitFor(() => {
      expect(screen.getByText('Алгоритмы и структуры данных')).toBeInTheDocument();
    });
    expect(screen.getByText('Отзывов: 12')).toBeInTheDocument();
    expect(screen.getByText('⭐ 4.6')).toBeInTheDocument();
  });

  it('renders fallback title when Stepik API fails', async () => {
    (getSimilarCourses as jest.Mock).mockResolvedValue([
      { course_id: 101, average_rating: 4.0, total_reviews: 5 },
    ]);
    (getCourse as jest.Mock).mockRejectedValue(new Error('Network error'));
    render(<SimilarCourses courseId={100} />);
    await waitFor(() => {
      expect(screen.getByText('Курс #101')).toBeInTheDocument();
    });
    expect(screen.getByText('⭐ 4.0')).toBeInTheDocument();
  });

  it('shows empty state when no recommendations', async () => {
    (getSimilarCourses as jest.Mock).mockResolvedValue([]);
    render(<SimilarCourses courseId={100} />);
    await waitFor(() => {
      expect(screen.getByText('Пока нет рекомендаций')).toBeInTheDocument();
    });
  });

  it('shows error state on fetch failure', async () => {
    (getSimilarCourses as jest.Mock).mockRejectedValue(new Error('Failed to load'));
    render(<SimilarCourses courseId={100} />);
    await waitFor(() => {
      expect(screen.getByText('Failed to load')).toBeInTheDocument();
    });
  });

  it('renders multiple similar courses', async () => {
    (getSimilarCourses as jest.Mock).mockResolvedValue([
      { course_id: 101, average_rating: 4.5, total_reviews: 10 },
      { course_id: 102, average_rating: 4.0, total_reviews: 5 },
    ]);
    (getCourse as jest.Mock).mockImplementation((id: number) =>
      Promise.resolve({ id, title: `Course ${id}`, cover: `https://example.com/${id}.jpg` })
    );
    render(<SimilarCourses courseId={100} />);
    await waitFor(() => {
      expect(screen.getByText('Course 101')).toBeInTheDocument();
      expect(screen.getByText('Course 102')).toBeInTheDocument();
    });
  });
});
