/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import Header from '../Header';

jest.mock('@/hooks/useAuth', () => ({
  useAuth: jest.fn(),
}));

jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: jest.fn(), prefetch: jest.fn() }),
}));

jest.mock('next/link', () => {
  // eslint-disable-next-line react/display-name
  return ({ children, href, ...props }: { children: React.ReactNode; href: string; [key: string]: unknown }) =>
    <a href={href} {...props}>{children}</a>;
});

jest.mock('../NotificationCenter', () => ({
  NotificationCenter: () => <div data-testid="notification-center">Notifications</div>,
}));

jest.mock('../navigation/NavMenu', () => ({
  NavMenu: () => <nav data-testid="nav-menu">Nav</nav>,
  MobileNavMenu: () => <div data-testid="mobile-nav-menu">Mobile Nav</div>,
}));

jest.mock('../ThemeToggle', () => ({
  __esModule: true,
  default: () => <button data-testid="theme-toggle">Theme</button>,
}));

import { useAuth } from '@/hooks/useAuth';

describe('Header', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders logo and brand name', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByText('MentorHub')).toBeInTheDocument();
    expect(screen.getByText('Менторы')).toBeInTheDocument();
    expect(screen.getByText('Курсы')).toBeInTheDocument();
    expect(screen.getByText('Сессии')).toBeInTheDocument();
  });

  it('shows login button when not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByText('Войти')).toBeInTheDocument();
    expect(screen.getByText('Начать')).toBeInTheDocument();
    expect(screen.queryByText('Выйти')).not.toBeInTheDocument();
  });

  it('shows user profile and logout when authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { full_name: 'John Doe', username: 'johndoe', role: 'student' },
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('Выйти')).toBeInTheDocument();
    expect(screen.getByTestId('notification-center')).toBeInTheDocument();
    expect(screen.queryByText('Войти')).not.toBeInTheDocument();
  });

  it('shows username when full_name is not available', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { username: 'johndoe', role: 'student' },
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByText('johndoe')).toBeInTheDocument();
  });

  it('calls logout when logout button is clicked', () => {
    const logoutMock = jest.fn();
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { username: 'test', role: 'student' },
      logout: logoutMock,
    });
    render(<Header />);
    fireEvent.click(screen.getByLabelText('Выйти'));
    expect(logoutMock).toHaveBeenCalled();
  });

  it('toggles mobile menu', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    const { container } = render(<Header />);
    const menuButton = container.querySelector('.md\\:hidden');
    expect(menuButton).toBeInTheDocument();
    fireEvent.click(menuButton!);
    expect(screen.getByTestId('mobile-nav-menu')).toBeInTheDocument();
    fireEvent.click(menuButton!);
    expect(screen.queryByTestId('mobile-nav-menu')).not.toBeInTheDocument();
  });

  it('shows mobile auth links when not authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    const { container } = render(<Header />);
    fireEvent.click(container.querySelector('.md\\:hidden')!);
    expect(screen.getAllByText('Войти').length).toBe(2);
    expect(screen.getAllByText('Начать').length).toBe(2);
  });

  it('shows mobile profile and logout when authenticated', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: true,
      user: { full_name: 'Jane', username: 'jane', role: 'mentor' },
      logout: jest.fn(),
    });
    const { container } = render(<Header />);
    fireEvent.click(container.querySelector('.md\\:hidden')!);
    expect(screen.getAllByText('Jane').length).toBe(2);
    expect(screen.getByText('Уведомления')).toBeInTheDocument();
    expect(screen.getAllByLabelText('Выйти').length).toBe(2);
  });

  it('renders navigation links with correct hrefs', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByText('Менторы').closest('a')).toHaveAttribute('href', '/mentors');
    expect(screen.getByText('Курсы').closest('a')).toHaveAttribute('href', '/courses');
    expect(screen.getByText('Сессии').closest('a')).toHaveAttribute('href', '/sessions');
  });

  it('renders theme toggle', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByTestId('theme-toggle')).toBeInTheDocument();
  });

  it('renders NavMenu component', () => {
    (useAuth as jest.Mock).mockReturnValue({
      isAuthenticated: false,
      user: null,
      logout: jest.fn(),
    });
    render(<Header />);
    expect(screen.getByTestId('nav-menu')).toBeInTheDocument();
  });
});
