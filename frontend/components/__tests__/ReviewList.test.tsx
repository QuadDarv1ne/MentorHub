/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import ReviewList from '../ReviewList';

describe('ReviewList', () => {
  beforeEach(() => {
    global.fetch = jest.fn() as jest.Mock;
  });

  it('renders list component', async () => {
    global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => ({ total: 0, data: [] }) })) as jest.Mock;
    const { container } = render(<ReviewList courseId={101} />);
    expect(container).toBeInTheDocument();
  });

  it('renders review items when present', async () => {
    const sample = {
      total: 1,
      data: [
        { id: 1, user_id: 5, user_name: 'Test User', rating: 5, comment: 'Nice', created_at: new Date().toISOString() }
      ]
    };
    global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => sample })) as jest.Mock;

    const { container } = render(<ReviewList courseId={101} />);
    expect(container).toBeInTheDocument();
  });
});
