"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { User } from '@/lib/api/auth';

/**
 * Hook для проверки аутентификации
 * Перенаправляет на страницу логина, если пользователь не авторизован
 */
export function useAuth(redirectTo = '/auth/login') {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      router.push(redirectTo);
    }
  }, [router, redirectTo]);

  const isAuthenticated = () => {
    return !!localStorage.getItem('access_token');
  };

  const getToken = () => {
    return localStorage.getItem('access_token');
  };

  const login = async (token: string, user: User) => {
    localStorage.setItem('access_token', token);
    localStorage.setItem('user_name', user.full_name || user.email);
    localStorage.setItem('user_role', user.role);
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    router.push('/auth/login');
  };

  return {
    isAuthenticated,
    getToken,
    login,
    logout,
  };
}

/**
 * Hook для опциональной аутентификации
 * Не перенаправляет, но возвращает статус
 */
export function useOptionalAuth() {
  const isAuthenticated = () => {
    return !!localStorage.getItem('access_token');
  };

  const getToken = () => {
    return localStorage.getItem('access_token');
  };

  return {
    isAuthenticated,
    getToken,
  };
}