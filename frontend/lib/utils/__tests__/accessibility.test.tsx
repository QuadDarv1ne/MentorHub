/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import {
  SkipLinks,
  RouteAnnouncer,
  VisuallyHidden,
  AriaDescription,
  useKeyboardNav,
} from '../accessibility';

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(() => '/test'),
}));

describe('SkipLinks', () => {
  it('renders skip navigation links', () => {
    render(<SkipLinks />);
    expect(screen.getByText('Перейти к основному содержимому')).toBeInTheDocument();
    expect(screen.getByText('Перейти к навигации')).toBeInTheDocument();
  });

  it('links point to correct targets', () => {
    render(<SkipLinks />);
    const mainLink = screen.getByText('Перейти к основному содержимому');
    expect(mainLink).toHaveAttribute('href', '#main-content');
    const navLink = screen.getByText('Перейти к навигации');
    expect(navLink).toHaveAttribute('href', '#navigation');
  });

  it('has sr-only class initially', () => {
    const { container } = render(<SkipLinks />);
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('sr-only');
  });
});

describe('RouteAnnouncer', () => {
  it('renders screen reader announcer element', () => {
    render(<RouteAnnouncer />);
    const announcer = screen.getByRole('status');
    expect(announcer).toBeInTheDocument();
    expect(announcer).toHaveAttribute('aria-live', 'polite');
    expect(announcer).toHaveAttribute('aria-atomic', 'true');
    expect(announcer.className).toContain('sr-only');
  });
});

describe('VisuallyHidden', () => {
  it('renders children with sr-only class', () => {
    render(<VisuallyHidden>Hidden Text</VisuallyHidden>);
    const element = screen.getByText('Hidden Text');
    expect(element.className).toContain('sr-only');
  });

  it('renders as span by default', () => {
    render(<VisuallyHidden>Text</VisuallyHidden>);
    const element = screen.getByText('Text');
    expect(element.tagName).toBe('SPAN');
  });

  it('renders as specified element type', () => {
    render(<VisuallyHidden as="div">Text</VisuallyHidden>);
    const element = screen.getByText('Text');
    expect(element.tagName).toBe('DIV');
  });
});

describe('AriaDescription', () => {
  it('renders with correct id', () => {
    render(<AriaDescription id="desc-1">Description text</AriaDescription>);
    const el = screen.getByText('Description text');
    expect(el).toHaveAttribute('id', 'desc-1');
    expect(el.className).toContain('sr-only');
  });
});

describe('useKeyboardNav', () => {
  function KeyboardNavTest({ items, onSelect }: { items: unknown[]; onSelect?: (index: number) => void }) {
    const { focusedIndex, handleKeyDown } = useKeyboardNav(items, onSelect);
    return (
      <div onKeyDown={handleKeyDown} tabIndex={0} role="listbox">
        {items.map((item, i) => (
          <div key={i} role="option" aria-selected={focusedIndex === i} data-focused={focusedIndex === i}>
            {String(item)}
          </div>
        ))}
        <div data-testid="focused-index">{focusedIndex}</div>
      </div>
    );
  }

  it('starts with no item focused', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    expect(screen.getByTestId('focused-index').textContent).toBe('-1');
  });

  it('navigates down on ArrowDown', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    expect(screen.getByTestId('focused-index').textContent).toBe('0');
  });

  it('navigates up on ArrowUp', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    expect(screen.getByTestId('focused-index').textContent).toBe('1');
    fireEvent.keyDown(listbox, { key: 'ArrowUp' });
    expect(screen.getByTestId('focused-index').textContent).toBe('0');
  });

  it('wraps around at end of list', () => {
    render(<KeyboardNavTest items={['A', 'B']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    expect(screen.getByTestId('focused-index').textContent).toBe('1');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    expect(screen.getByTestId('focused-index').textContent).toBe('0');
  });

  it('wraps around at start of list', () => {
    render(<KeyboardNavTest items={['A', 'B']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowUp' });
    expect(screen.getByTestId('focused-index').textContent).toBe('1');
  });

  it('navigates to first item on Home', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'Home' });
    expect(screen.getByTestId('focused-index').textContent).toBe('0');
  });

  it('navigates to last item on End', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'End' });
    expect(screen.getByTestId('focused-index').textContent).toBe('2');
  });

  it('calls onSelect on Enter', () => {
    const onSelect = jest.fn();
    render(<KeyboardNavTest items={['A', 'B']} onSelect={onSelect} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'Enter' });
    expect(onSelect).toHaveBeenCalledWith(0);
  });

  it('calls onSelect on Space', () => {
    const onSelect = jest.fn();
    render(<KeyboardNavTest items={['A', 'B']} onSelect={onSelect} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: ' ' });
    expect(onSelect).toHaveBeenCalledWith(0);
  });

  it('resets focus on Escape', () => {
    render(<KeyboardNavTest items={['A', 'B', 'C']} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'ArrowDown' });
    fireEvent.keyDown(listbox, { key: 'Escape' });
    expect(screen.getByTestId('focused-index').textContent).toBe('-1');
  });

  it('does not call onSelect when no item is focused', () => {
    const onSelect = jest.fn();
    render(<KeyboardNavTest items={['A', 'B']} onSelect={onSelect} />);
    const listbox = screen.getByRole('listbox');
    fireEvent.keyDown(listbox, { key: 'Enter' });
    expect(onSelect).not.toHaveBeenCalled();
  });
});
