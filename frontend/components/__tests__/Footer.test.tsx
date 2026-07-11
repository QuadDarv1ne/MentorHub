/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import Footer from '../Footer';

jest.mock('next/link', () => {
  // eslint-disable-next-line react/display-name
  return ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: any }) =>
    <a href={href} {...props}>{children}</a>;
});

describe('Footer', () => {
  it('renders company name', () => {
    render(<Footer />);
    expect(screen.getByRole('heading', { level: 3 })).toHaveTextContent('MentorHub');
  });

  it('renders navigation sections', () => {
    render(<Footer />);
    expect(screen.getByText(/Платформа/)).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: /Поддержка/ })).toBeInTheDocument();
    expect(screen.getByText(/Правовая информация/)).toBeInTheDocument();
  });

  it('renders copyright notice with current year', () => {
    render(<Footer />);
    const currentYear = new Date().getFullYear().toString();
    expect(screen.getByText(new RegExp(currentYear))).toBeInTheDocument();
  });

  it('renders social media or contact links', () => {
    render(<Footer />);
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
  });
});
