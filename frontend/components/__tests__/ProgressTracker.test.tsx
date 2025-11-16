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
  // first call is fetch of existing progress (GET), second is upsert (POST)
  const postCall = (global as any).fetch.mock.calls.find((c: any[]) => c[1] && c[1].method === 'POST');
  expect(postCall).toBeDefined();
  const [url, opts] = postCall;
  expect(url).toContain('/api/v1/progress');
  expect(opts.headers.Authorization).toBe('Bearer fake-token');
  expect(JSON.parse(opts.body)).toEqual({ course_id: 200, progress_percent: 50 });
  });

  it('shows success message and allows cancel to revert changes', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (global as any).fetch = jest.fn((url: string, opts?: any) => {
      if (opts && opts.method === 'POST') {
        return Promise.resolve({ ok: true, json: async () => ({ id: 1, course_id: 200, progress_percent: 30 }) });
      }
      return Promise.resolve({ ok: true, json: async () => ([])});
    });

    render(<ProgressTracker courseId={200} />);
    const slider = screen.getByRole('slider') as HTMLInputElement;
    // change to 30 and save
    fireEvent.change(slider, { target: { value: '30' } });
    fireEvent.click(screen.getByRole('button', { name: /Сохранить/i }));
    await waitFor(() => expect(screen.getByText(/Сохранено/i)).toBeInTheDocument());

    // change to 80 and then cancel
    fireEvent.change(slider, { target: { value: '80' } });
    fireEvent.click(screen.getByRole('button', { name: /Отменить/i }));
    expect(slider.value).toBe('30');
    expect(screen.getByText(/Изменения отменены/i)).toBeInTheDocument();
  });

  it('shows login prompt when unauthenticated and disables controls', () => {
    // no token in localStorage
    render(<ProgressTracker courseId={200} />);
    expect(screen.getByText(/Для сохранения прогресса/i)).toBeInTheDocument();
    const slider = screen.getByRole('slider') as HTMLInputElement;
    expect(slider).toBeDisabled();
  });
});
