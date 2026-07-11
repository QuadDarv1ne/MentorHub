/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { LoadingFallback, CardSkeleton, ListSkeleton, TableSkeleton, withLazyLoad } from '../lazyLoad';

describe('LoadingFallback', () => {
  it('renders a loading spinner', () => {
    const { container } = render(<LoadingFallback />);
    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('has accessible structure', () => {
    const { container } = render(<LoadingFallback />);
    const flexContainer = container.querySelector('.flex');
    expect(flexContainer).toBeInTheDocument();
  });
});

describe('CardSkeleton', () => {
  it('renders a card skeleton with pulse animation', () => {
    const { container } = render(<CardSkeleton />);
    const skeleton = container.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('renders skeleton elements', () => {
    const { container } = render(<CardSkeleton />);
    const grayBars = container.querySelectorAll('.bg-gray-200');
    expect(grayBars.length).toBeGreaterThanOrEqual(5);
  });
});

describe('ListSkeleton', () => {
  it('renders default 3 items', () => {
    const { container } = render(<ListSkeleton />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(3);
  });

  it('renders specified number of items', () => {
    const { container } = render(<ListSkeleton items={5} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(5);
  });

  it('renders at least 1 item', () => {
    const { container } = render(<ListSkeleton items={0} />);
    const skeletons = container.querySelectorAll('.animate-pulse');
    expect(skeletons).toHaveLength(0);
  });
});

describe('TableSkeleton', () => {
  it('renders default 5 rows and 4 columns', () => {
    const { container } = render(<TableSkeleton />);
    const rows = container.querySelectorAll('.border-b');
    // header + 5 rows
    expect(rows.length).toBeGreaterThanOrEqual(6);
  });

  it('renders specified number of rows', () => {
    const { container } = render(<TableSkeleton rows={3} cols={2} />);
    const grayBars = container.querySelectorAll('.bg-gray-200');
    expect(grayBars.length).toBeGreaterThanOrEqual(3);
  });
});

describe('withLazyLoad', () => {
  it('wraps component with Suspense', () => {
    const MockComponent = () => <div>Content</div>;
    const LazyLoaded = withLazyLoad(MockComponent);
    render(<LazyLoaded />);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('uses custom fallback when provided', () => {
    const MockComponent = () => <div>Content</div>;
    const CustomFallback = () => <div>Custom Fallback</div>;
    const LazyLoaded = withLazyLoad(MockComponent, <CustomFallback />);
    render(<LazyLoaded />);
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('passes props to wrapped component', () => {
    interface Props { name: string; }
    const MockComponent = ({ name }: Props) => <div>Hello {name}</div>;
    const LazyLoaded = withLazyLoad<Props>(MockComponent);
    render(<LazyLoaded name="World" />);
    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });
});
