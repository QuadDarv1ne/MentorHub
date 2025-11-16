"use client";
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

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

  const logout = () => {
    localStorage.removeItem('access_token');
    router.push('/auth/login');
  };

  return {
    isAuthenticated,
    getToken,
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
