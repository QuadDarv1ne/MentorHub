/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import ProgressList, { type ProgressItem } from '../ProgressList';

describe('ProgressList', () => {
  it('renders empty state', () => {
    render(<ProgressList items={[]} />);
    expect(screen.getByRole('status')).toHaveTextContent(/Пока нет данных/i);
  });

  it('renders items with percent and status', () => {
    const items: ProgressItem[] = [
      { id: 1, course_id: 101, progress_percent: 20, completed: false, lesson_id: null },
      { id: 2, course_id: 102, progress_percent: 100, completed: true, lesson_id: 5 },
    ];
    render(<ProgressList items={items} />);

    expect(screen.getByText(/Курс #101/)).toBeInTheDocument();
    expect(screen.getByText(/Курс #102/)).toBeInTheDocument();
    expect(screen.getAllByText(/В процессе|Завершено/).length).toBeGreaterThanOrEqual(2);
    expect(screen.getAllByText(/%/).length).toBeGreaterThanOrEqual(2);
  });
});
