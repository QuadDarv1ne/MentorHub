"use client";

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User } from '@/lib/api/auth';

interface UseAuthReturn {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (token: string, user: User) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  error: string | null;
  getUserData: () => User | null;
}

interface UseAuthOptions {
  redirectTo?: string;
  redirectOnAuth?: boolean;
}

/**
 * Улучшенный hook для аутентификации
 * - Кэширование данных пользователя
 * - Автоматический refresh токена
 * - Обработка ошибок
 * - Оптимистичные обновления
 */
export function useAuth(options: UseAuthOptions = {}): UseAuthReturn {
  const { redirectTo = '/auth/login', redirectOnAuth = true } = options;
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Проверка токена и загрузка пользователя
  const checkAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        setUser(null);
        setLoading(false);
        if (redirectOnAuth) {
          router.push(redirectTo);
        }
        return;
      }

      // Проверка срока действия токена (упрощённо)
      const tokenData = JSON.parse(atob(token.split('.')[1]));
      const isExpired = tokenData.exp * 1000 < Date.now();

      if (isExpired) {
        // Попытка refresh токена
        const refreshToken = localStorage.getItem('refresh_token');
        if (refreshToken) {
          try {
            const response = await fetch('/api/v1/auth/refresh', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (response.ok) {
              const data = await response.json();
              localStorage.setItem('access_token', data.access_token);
              // Продолжаем с новым токеном
            } else {
              // Refresh не удался - logout
              logout();
              return;
            }
          } catch (refreshError) {
            console.error('Token refresh failed:', refreshError);
            logout();
            return;
          }
        } else {
          logout();
          return;
        }
      }

      // Загрузка данных пользователя
      try {
        const response = await fetch('/api/v1/users/me', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
          setError(null);
        } else if (response.status === 401) {
          logout();
          return;
        }
      } catch (apiError) {
        console.error('Failed to fetch user:', apiError);
        setError('Не удалось загрузить данные пользователя');
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      setError('Ошибка проверки аутентификации');
    } finally {
      setLoading(false);
    }
  }, [router, redirectTo, redirectOnAuth]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (token: string, userData: User) => {
    try {
      localStorage.setItem('access_token', token);
      localStorage.setItem('user_name', userData.full_name || userData.email);
      localStorage.setItem('user_role', userData.role);
      setUser(userData);
      setError(null);
      
      // Перенаправление после успешного входа
      router.push('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
      setError('Ошибка при входе');
      throw err;
    }
  };

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    setUser(null);
    router.push('/auth/login');
  }, [router]);

  const refreshUser = async () => {
    await checkAuth();
  };

  const getUserData = useCallback(() => {
    return user;
  }, [user]);

  return {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    logout,
    refreshUser,
    error,
    getUserData,
  };
}

/**
 * Hook для опциональной аутентификации
 * Не перенаправляет, возвращает статус
 */
export function useOptionalAuth(): {
  user: User | null;
  loading: boolean;
  isAuthenticated: boolean;
  getToken: () => string | null;
} {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem('access_token');
      
      if (token) {
        try {
          const response = await fetch('/api/v1/users/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          });

          if (response.ok) {
            const userData = await response.json();
            setUser(userData);
          }
        } catch (err) {
          console.error('Optional auth check failed:', err);
        }
      }
      
      setLoading(false);
    };

    initAuth();
  }, []);

  const isAuthenticated = () => !!localStorage.getItem('access_token');
  const getToken = () => localStorage.getItem('access_token');

  return {
    user,
    loading,
    isAuthenticated,
    getToken,
  };
}

/**
 * Hook для проверки роли пользователя
 */
export function useRole(requiredRoles: string[]): {
  hasRole: boolean;
  isLoading: boolean;
} {
  const { user, loading, isAuthenticated } = useOptionalAuth();

  const hasRole = isAuthenticated && user ? 
    requiredRoles.includes(user.role) : false;

  return {
    hasRole,
    isLoading: loading,
  };
}

/**
 * Hook для проверки владения ресурсом
 */
export function useOwnership(resourceOwnerId: number | undefined): {
  isOwner: boolean;
  isAdmin: boolean;
  canEdit: boolean;
  isLoading: boolean;
} {
  const { user, loading } = useOptionalAuth();

  const isOwner = user ? user.id === resourceOwnerId : false;
  const isAdmin = user ? user.role === 'admin' : false;
  const canEdit = isOwner || isAdmin;

  return {
    isOwner,
    isAdmin,
    canEdit,
    isLoading: loading,
  };
}
