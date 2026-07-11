/** @jest-environment jsdom */
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8001';
process.env.NEXT_PUBLIC_API_URL = 'http://localhost:8001';
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import ProgressTracker from '../ProgressTracker';

jest.mock('@/lib/api/progress', () => ({
  getMyProgress: jest.fn(),
  upsertProgress: jest.fn(),
}));

import { getMyProgress, upsertProgress } from '@/lib/api/progress';

describe('ProgressTracker', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('renders progress component with initial 0%', () => {
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    const { container } = render(<ProgressTracker courseId={200} />);
    expect(screen.getByText('Прогресс по курсу')).toBeInTheDocument();
    const progress = container.querySelector('progress');
    expect(progress).toHaveAttribute('value', '0');
  });

  it('loads existing progress from API', async () => {
    (getMyProgress as jest.Mock).mockResolvedValue([{ progress_percent: 40 }]);
    const { container } = render(<ProgressTracker courseId={200} />);
    await waitFor(() => {
      const progress = container.querySelector('progress');
      expect(progress).toHaveAttribute('value', '40');
    });
  });

  it('shows login prompt when unauthenticated', () => {
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    render(<ProgressTracker courseId={200} />);
    expect(screen.getByText(/войдите в аккаунт/i)).toBeInTheDocument();
    expect(screen.getByRole('slider')).toBeDisabled();
  });

  it('enables controls when token present', () => {
    localStorage.setItem('access_token', 'fake-token');
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    render(<ProgressTracker courseId={200} />);
    expect(screen.getByRole('slider')).not.toBeDisabled();
    expect(screen.getByText('Сохранить')).not.toBeDisabled();
  });

  it('saves progress on save button click', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    (upsertProgress as jest.Mock).mockResolvedValue({ id: 1, course_id: 200, progress_percent: 50 });
    render(<ProgressTracker courseId={200} />);
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '50' } });
    fireEvent.click(screen.getByText('Сохранить'));
    await waitFor(() => {
      expect(upsertProgress).toHaveBeenCalledWith({ course_id: 200, progress_percent: 50 });
    });
    expect(await screen.findByText('Сохранено')).toBeInTheDocument();
  });

  it('shows error on save failure', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    (upsertProgress as jest.Mock).mockRejectedValue(new Error('Network error'));
    render(<ProgressTracker courseId={200} />);
    fireEvent.click(screen.getByText('Сохранить'));
    expect(await screen.findByText('Network error')).toBeInTheDocument();
  });

  it('shows auth error when saving without token', () => {
    (getMyProgress as jest.Mock).mockResolvedValue(null);
    render(<ProgressTracker courseId={200} />);
    fireEvent.click(screen.getByText('Сохранить'));
    expect(screen.getByText('Требуется авторизация для сохранения прогресса')).toBeInTheDocument();
  });

  it('cancels changes and reverts to last saved value', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (getMyProgress as jest.Mock).mockResolvedValue([{ progress_percent: 30 }]);
    const { container } = render(<ProgressTracker courseId={200} />);
    await waitFor(() => {
      const progress = container.querySelector('progress');
      expect(progress).toHaveAttribute('value', '30');
    });
    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '60' } });
    expect(slider).toHaveAttribute('value', '60');
    fireEvent.click(screen.getByText('Отменить'));
    expect(slider).toHaveAttribute('value', '30');
    expect(await screen.findByText('Изменения отменены')).toBeInTheDocument();
  });

  it('marks course as completed', async () => {
    localStorage.setItem('access_token', 'fake-token');
    (getMyProgress as jest.Mock).mockResolvedValue([{ progress_percent: 0 }]);
    (upsertProgress as jest.Mock).mockResolvedValue({ id: 1, course_id: 200, progress_percent: 100 });
    const { container } = render(<ProgressTracker courseId={200} />);
    await waitFor(() => {
      const progress = container.querySelector('progress');
      expect(progress).toHaveAttribute('value', '0');
    });
    fireEvent.click(screen.getByText('Пометить завершённым'));
    await waitFor(() => {
      expect(upsertProgress).toHaveBeenCalledWith({ course_id: 200, progress_percent: 100 });
    });
    const progress = container.querySelector('progress');
    expect(progress).toHaveAttribute('value', '100');
  });
});
