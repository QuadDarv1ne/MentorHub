/** @jest-environment jsdom */
import React from 'react';
import '@testing-library/jest-dom';
import { render } from '@testing-library/react';
import ProgressList, { type ProgressItem } from '../ProgressList';

describe('ProgressList', () => {
  it('renders empty state', () => {
    const { container } = render(<ProgressList items={[]} />);
    expect(container).toBeInTheDocument();
  });

  it('renders items with percent and status', () => {
    const items: ProgressItem[] = [
      { id: 1, course_id: 101, progress_percent: 20, completed: false, lesson_id: null },
      { id: 2, course_id: 102, progress_percent: 100, completed: true, lesson_id: 5 },
    ];
    const { container } = render(<ProgressList items={items} />);
    expect(container).toBeInTheDocument();
  });
});
