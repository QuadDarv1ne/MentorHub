/**
 * @jest-environment jsdom
 */
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import AuthGuard from '../AuthGuard';

const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter: () => ({ push: mockPush }),
}));

describe('AuthGuard', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('renders children when authorized with valid token', () => {
    const validToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjo5OTk5OTk5OTk5fQ.dozjgO2hcLh4K442R99999';
    localStorage.setItem('access_token', validToken);
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('redirects to login when no token and requireAuth is true', () => {
    delete window.location;
    window.location = { pathname: '/dashboard' } as unknown as Location;
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    expect(mockPush).toHaveBeenCalledWith('/auth/login?redirect=%2Fdashboard');
  });

  it('shows unauthorized message when no token and requireAuth is true', () => {
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    expect(screen.getByText('Требуется авторизация')).toBeInTheDocument();
    expect(screen.getByText('Войти в систему')).toBeInTheDocument();
  });

  it('renders children when no token but requireAuth is false', () => {
    render(<AuthGuard requireAuth={false}><div>Public Content</div></AuthGuard>);
    expect(screen.getByText('Public Content')).toBeInTheDocument();
  });

  it('redirects to login on expired token', () => {
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.dozjgO2hcLh4K442R99999';
    localStorage.setItem('access_token', expiredToken);
    localStorage.setItem('refresh_token', 'some-refresh');
    delete window.location;
    window.location = { pathname: '/profile' } as unknown as Location;
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    expect(mockPush).toHaveBeenCalledWith('/auth/login?redirect=%2Fprofile');
    expect(localStorage.getItem('access_token')).toBeNull();
    expect(localStorage.getItem('refresh_token')).toBeNull();
  });

  it('uses custom redirect path', () => {
    delete window.location;
    window.location = { pathname: '/admin' } as unknown as Location;
    render(<AuthGuard redirectTo="/custom-login"><div>Protected</div></AuthGuard>);
    expect(mockPush).toHaveBeenCalledWith('/custom-login?redirect=%2Fadmin');
  });

  it('renders login button that navigates to login page', () => {
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    const loginButton = screen.getByText('Войти в систему');
    fireEvent.click(loginButton);
    expect(mockPush).toHaveBeenCalledWith('/auth/login');
  });

  it('handles malformed token gracefully', () => {
    localStorage.setItem('access_token', 'invalid-token');
    delete window.location;
    window.location = { pathname: '/dashboard' } as unknown as Location;
    render(<AuthGuard><div>Protected Content</div></AuthGuard>);
    expect(mockPush).toHaveBeenCalledWith('/auth/login?redirect=%2Fdashboard');
  });
});
