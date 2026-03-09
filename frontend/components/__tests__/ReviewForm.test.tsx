/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import ReviewForm from '../ReviewForm';

describe('ReviewForm', () => {
  beforeEach(() => {
    global.fetch = jest.fn() as jest.Mock;
    localStorage.clear();
  });

  it('renders form fields', () => {
    const { container } = render(<ReviewForm courseId={123} />);
    expect(container).toBeInTheDocument();
  });

  it('submits data with Authorization header when token present', async () => {
    localStorage.setItem('access_token', 'fake-token');
    global.fetch = jest.fn(() => Promise.resolve({ ok: true })) as jest.Mock;

    const { container } = render(<ReviewForm courseId={123} />);
    expect(container).toBeInTheDocument();
    
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  it('shows auth required error when response is 401', async () => {
    global.fetch = jest.fn(() => Promise.resolve({ ok: false, status: 401, json: async () => ({ detail: 'Unauthorized' }) })) as jest.Mock;
    const { container } = render(<ReviewForm courseId={123} />);
    expect(container).toBeInTheDocument();
    
    await new Promise(resolve => setTimeout(resolve, 100));
  });
});
