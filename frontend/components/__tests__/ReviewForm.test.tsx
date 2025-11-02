/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ReviewForm from '../ReviewForm';

describe('ReviewForm', () => {
  beforeEach(() => {
    // clear fetch mock and localStorage
    (global as any).fetch = jest.fn();
    localStorage.clear();
  });

  it('renders form fields', () => {
    render(<ReviewForm courseId={123} />);
    expect(screen.getByLabelText(/Оценка/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Ваш отзыв/i)).toBeInTheDocument();
  });

  it('submits data with Authorization header when token present', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (global as any).fetch = jest.fn(() => Promise.resolve({ ok: true }));

    render(<ReviewForm courseId={123} />);

    fireEvent.change(screen.getByLabelText(/Оценка/i), { target: { value: '4' } });
    fireEvent.change(screen.getByPlaceholderText(/Ваш отзыв/i), { target: { value: 'Great course' } });

    fireEvent.click(screen.getByRole('button', { name: /Отправить/i }));

    await waitFor(() => expect((global as any).fetch).toHaveBeenCalled());

    const [url, opts] = (global as any).fetch.mock.calls[0];
    expect(url).toContain('/api/v1/courses/123/reviews');
    expect(opts.headers.Authorization).toBe('Bearer fake-token');
    expect(JSON.parse(opts.body)).toEqual({ rating: 4, comment: 'Great course' });
  });

  it('shows auth required error when response is 401', async () => {
    (global as any).fetch = jest.fn(() => Promise.resolve({ ok: false, status: 401, json: async () => ({ detail: 'Unauthorized' }) }));
    render(<ReviewForm courseId={123} />);

    fireEvent.click(screen.getByRole('button', { name: /Отправить/i }));

    await waitFor(() => expect(screen.getByText(/Требуется авторизация/i)).toBeInTheDocument());
  });
});
