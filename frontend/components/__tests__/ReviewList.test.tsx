/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, waitFor } from '@testing-library/react';
import ReviewList from '../ReviewList';

describe('ReviewList', () => {
  beforeEach(() => {
    (global as any).fetch = jest.fn();
  });

  it('renders no reviews message when empty', async () => {
    (global as any).fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => ({ total: 0, data: [] }) }));
    render(<ReviewList courseId={101} />);
    await waitFor(() => expect(screen.getByText(/Пока нет отзывов/i)).toBeInTheDocument());
  });

  it('renders review items when present', async () => {
    const sample = {
      total: 1,
      data: [
        { id: 1, user_id: 5, user_name: 'Test User', rating: 5, comment: 'Nice', created_at: new Date().toISOString() }
      ]
    };
    (global as any).fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => sample }));

    render(<ReviewList courseId={101} />);
    await waitFor(() => expect(screen.getByText(/Test User/)).toBeInTheDocument());
    expect(screen.getByText(/Nice/)).toBeInTheDocument();
  });
});
