/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ReviewForm from '../ReviewForm';

jest.mock('@/lib/api/client', () => ({
  apiRequest: jest.fn(),
}));

import { apiRequest } from '@/lib/api/client';

describe('ReviewForm', () => {
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders form fields with default values', () => {
    render(<ReviewForm courseId={123} />);
    expect(screen.getByText('Оставьте отзыв')).toBeInTheDocument();
    expect(screen.getByLabelText('Оценка:')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Ваш отзыв (необязательно)')).toBeInTheDocument();
    expect(screen.getByText('Отправить')).toBeInTheDocument();
  });

  it('renders all rating options (1-5)', () => {
    render(<ReviewForm courseId={123} />);
    const select = screen.getByLabelText('Оценка:') as HTMLSelectElement;
    expect(select.value).toBe('5');
  });

  it('submits form with rating and comment', async () => {
    (apiRequest as jest.Mock).mockResolvedValue({ id: 1 });
    render(<ReviewForm courseId={123} onSuccess={mockOnSuccess} />);
    fireEvent.change(screen.getByLabelText('Оценка:'), { target: { value: '4' } });
    fireEvent.change(screen.getByPlaceholderText('Ваш отзыв (необязательно)'), { target: { value: 'Great course!' } });
    fireEvent.click(screen.getByText('Отправить'));
    await waitFor(() => {
      expect(apiRequest).toHaveBeenCalledWith('/courses/123/reviews', {
        method: 'POST',
        body: JSON.stringify({ rating: 4, comment: 'Great course!' }),
      });
    });
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('resets form after successful submission', async () => {
    (apiRequest as jest.Mock).mockResolvedValue({ id: 1 });
    render(<ReviewForm courseId={123} />);
    fireEvent.change(screen.getByLabelText('Оценка:'), { target: { value: '3' } });
    fireEvent.change(screen.getByPlaceholderText('Ваш отзыв (необязательно)'), { target: { value: 'OK' } });
    fireEvent.click(screen.getByText('Отправить'));
    await waitFor(() => {
      expect(apiRequest).toHaveBeenCalled();
    });
    const select = screen.getByLabelText('Оценка:') as HTMLSelectElement;
    expect(select.value).toBe('5');
    expect(screen.getByPlaceholderText('Ваш отзыв (необязательно)')).toHaveValue('');
  });

  it('shows auth error on 401 response', async () => {
    (apiRequest as jest.Mock).mockRejectedValue(new Error('401'));
    render(<ReviewForm courseId={123} />);
    fireEvent.click(screen.getByText('Отправить'));
    await waitFor(() => {
      expect(screen.getByText('Требуется авторизация. Пожалуйста, войдите.')).toBeInTheDocument();
    });
  });

  it('shows network error on generic failure', async () => {
    (apiRequest as jest.Mock).mockRejectedValue(new Error('Network error'));
    render(<ReviewForm courseId={123} />);
    fireEvent.click(screen.getByText('Отправить'));
    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('disables submit button during submission', async () => {
    let resolvePromise: (value: unknown) => void;
    const promise = new Promise((resolve) => { resolvePromise = resolve; });
    (apiRequest as jest.Mock).mockReturnValue(promise);
    render(<ReviewForm courseId={123} />);
    fireEvent.click(screen.getByText('Отправить'));
    expect(screen.getByText('Отправка...')).toBeInTheDocument();
    expect(screen.getByText('Отправка...')).toBeDisabled();
    resolvePromise!({ id: 1 });
    await waitFor(() => {
      expect(screen.getByText('Отправить')).toBeInTheDocument();
    });
  });

  it('calls onSuccess callback when provided', async () => {
    (apiRequest as jest.Mock).mockResolvedValue({ id: 1 });
    render(<ReviewForm courseId={123} onSuccess={mockOnSuccess} />);
    fireEvent.click(screen.getByText('Отправить'));
    await waitFor(() => {
      expect(mockOnSuccess).toHaveBeenCalledTimes(1);
    });
  });
});
