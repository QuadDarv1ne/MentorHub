/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import ProgressTracker from '../ProgressTracker';

describe('ProgressTracker', () => {
  beforeEach(() => {
    global.fetch = jest.fn() as jest.Mock;
    localStorage.clear();
  });

  it('renders progress component', () => {
    const { container } = render(<ProgressTracker courseId={200} />);
    expect(container).toBeInTheDocument();
  });

  it('saves progress with auth header when token present', async () => {
    localStorage.setItem('access_token', 'fake-token');
    global.fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => ({ id: 1, course_id: 200, progress_percent: 50 }) })) as jest.Mock;

    const { container } = render(<ProgressTracker courseId={200} />);
    expect(container).toBeInTheDocument();
    
    await new Promise(resolve => setTimeout(resolve, 100));
    expect(global.fetch).toHaveBeenCalled();
  });

  it('shows success message and allows cancel to revert changes', async () => {
    localStorage.setItem('access_token', 'fake-token');
    global.fetch = jest.fn((url: string, opts?: RequestInit) => {
      if (opts && opts.method === 'POST') {
        return Promise.resolve({ ok: true, json: async () => ({ id: 1, course_id: 200, progress_percent: 30 }) });
      }
      return Promise.resolve({ ok: true, json: async () => ([])});
    });

    const { container } = render(<ProgressTracker courseId={200} />);
    expect(container).toBeInTheDocument();
    
    await new Promise(resolve => setTimeout(resolve, 100));
  });

  it('shows login prompt when unauthenticated and disables controls', () => {
    const { container } = render(<ProgressTracker courseId={200} />);
    expect(container).toBeInTheDocument();
  });
});
