/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ReviewList from '../ReviewList';

const mockReviews = {
  total: 2,
  page: 1,
  page_size: 10,
  total_pages: 1,
  data: [
    { id: 1, user_id: 5, user_name: 'Test User', rating: 5, comment: 'Nice', created_at: '2024-01-15T10:00:00Z' },
    { id: 2, user_id: 6, user_name: null, rating: 4, comment: 'Good', created_at: '2024-01-14T10:00:00Z' },
  ],
};

jest.mock('@/lib/api/client', () => ({
  publicRequest: jest.fn(),
}));

import { publicRequest } from '@/lib/api/client';

describe('ReviewList', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('shows loading state initially', () => {
    (publicRequest as jest.Mock).mockReturnValue(new Promise(() => {}));
    render(<ReviewList courseId={101} />);
    expect(screen.getByText('Загрузка отзывов...')).toBeInTheDocument();
  });

  it('renders review items when present', async () => {
    (publicRequest as jest.Mock).mockResolvedValue(mockReviews);
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });
    expect(screen.getByText('Nice')).toBeInTheDocument();
    expect(screen.getByText('Пользователь #6')).toBeInTheDocument();
    expect(screen.getByText('Good')).toBeInTheDocument();
  });

  it('shows empty state when no reviews', async () => {
    (publicRequest as jest.Mock).mockResolvedValue({ total: 0, page: 1, page_size: 10, total_pages: 0, data: [] });
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Пока нет отзывов. Будьте первым!')).toBeInTheDocument();
    });
  });

  it('renders star ratings correctly', async () => {
    (publicRequest as jest.Mock).mockResolvedValue(mockReviews);
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('5 ★')).toBeInTheDocument();
      expect(screen.getByText('4 ★')).toBeInTheDocument();
    });
  });

  it('disables previous button on first page', async () => {
    (publicRequest as jest.Mock).mockResolvedValue({
      total: 20, page: 1, page_size: 10, total_pages: 2, data: mockReviews.data,
    });
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });
    expect(screen.getByText('Предыдущая')).toBeDisabled();
    expect(screen.getByText('Следующая')).not.toBeDisabled();
  });

  it('navigates to next page', async () => {
    (publicRequest as jest.Mock).mockResolvedValue({
      total: 20, page: 1, page_size: 10, total_pages: 2, data: mockReviews.data,
    });
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Test User')).toBeInTheDocument();
    });
    fireEvent.click(screen.getByText('Следующая'));
    await waitFor(() => {
      expect(publicRequest).toHaveBeenCalledWith('/courses/101/reviews?page=2&page_size=10');
    });
  });

  it('handles API errors gracefully', async () => {
    (publicRequest as jest.Mock).mockRejectedValue(new Error('API Error'));
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Пока нет отзывов. Будьте первым!')).toBeInTheDocument();
    });
  });

  it('renders page number indicator', async () => {
    (publicRequest as jest.Mock).mockResolvedValue({
      total: 20, page: 1, page_size: 10, total_pages: 2, data: mockReviews.data,
    });
    render(<ReviewList courseId={101} />);
    await waitFor(() => {
      expect(screen.getByText('Страница 1')).toBeInTheDocument();
    });
  });
});
