/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProgressTracker from '../ProgressTracker';

describe('ProgressTracker', () => {
  beforeEach(() => {
    (global as any).fetch = jest.fn();
    localStorage.clear();
  });

  it('renders progress bar and controls', () => {
    render(<ProgressTracker courseId={200} />);
    expect(screen.getByText(/Прогресс по курсу/i)).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('saves progress with auth header when token present', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (global as any).fetch = jest.fn(() => Promise.resolve({ ok: true, json: async () => ({ id: 1, course_id: 200, progress_percent: 50 }) }));

    render(<ProgressTracker courseId={200} />);

    const slider = screen.getByRole('slider') as HTMLInputElement;
    fireEvent.change(slider, { target: { value: '50' } });

    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));

    await waitFor(() => expect((global as any).fetch).toHaveBeenCalled());
    const [url, opts] = (global as any).fetch.mock.calls[0];
    expect(url).toContain('/api/v1/progress');
    expect(opts.headers.Authorization).toBe('Bearer fake-token');
    expect(JSON.parse(opts.body)).toEqual({ course_id: 200, progress_percent: 50 });
  });
});
