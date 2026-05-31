"use client";

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { User, login as apiLogin, logout as apiLogout, getCurrentUser, refreshToken as apiRefreshToken } from '@/lib/api/auth';
import { STORAGE_KEYS } from '@/lib/api/client';
import { logger } from '@/lib/utils/logger';

export interface UseAuthReturn {
  user: User | null;
  token: string | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  error: string | null;
  getUserData: () => User | null;
}

export interface UseAuthOptions {
  redirectTo?: string;
  redirectOnAuth?: boolean;
}

/**
 * Улучшенный hook для аутентификации
 * - Использует единый API клиент
 * - Автоматический refresh токена
 * - Обработка ошибок
 */
export function useAuth(options: UseAuthOptions = {}): UseAuthReturn {
  const { redirectTo = '/auth/login', redirectOnAuth = true } = options;
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const logout = useCallback(() => {
    localStorage.removeItem(STORAGE_KEYS.ACCESS_TOKEN);
    localStorage.removeItem(STORAGE_KEYS.REFRESH_TOKEN);
    localStorage.removeItem('user_name');
    localStorage.removeItem('user_role');
    setUser(null);
    router.push('/auth/login');
  }, [router]);

  // Проверка токена и загрузка пользователя
  const checkAuth = useCallback(async () => {
    try {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);

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
        const storedRefreshToken = localStorage.getItem(STORAGE_KEYS.REFRESH_TOKEN);
        if (storedRefreshToken) {
          try {
            const data = await apiRefreshToken(storedRefreshToken);
            // SECURITY: JWT stored in localStorage is vulnerable to XSS attacks.
            localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
            localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);
          } catch (refreshError) {
            logger.error('Token refresh failed', refreshError);
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
        const userData = await getCurrentUser();
        setUser(userData);
        setError(null);
      } catch (apiError) {
        logger.error('Failed to fetch user', apiError);
        if (apiError instanceof Error && apiError.message.includes('401')) {
          logout();
        } else {
          setError('Не удалось загрузить данные пользователя');
        }
      }
    } catch (err) {
      logger.error('Auth check failed', err);
      setError('Ошибка проверки аутентификации');
    } finally {
      setLoading(false);
    }
  }, [router, redirectTo, redirectOnAuth, logout]);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const login = async (email: string, password: string) => {
    try {
      const data = await apiLogin({ email, password });
      // SECURITY: JWT stored in localStorage is vulnerable to XSS attacks.
      // TODO: migrate to httpOnly cookies when backend supports secure cookie-based auth.
      localStorage.setItem(STORAGE_KEYS.ACCESS_TOKEN, data.access_token);
      localStorage.setItem(STORAGE_KEYS.REFRESH_TOKEN, data.refresh_token);

      const userData = await getCurrentUser();
      localStorage.setItem('user_name', userData.full_name || userData.email);
      localStorage.setItem('user_role', userData.role);
      setUser(userData);
      setError(null);
      router.push('/dashboard');
    } catch (err) {
      logger.error('Login failed', err);
      setError('Ошибка при входе');
      throw err;
    }
  };

  const handleLogout = async () => {
    try {
      await apiLogout();
    } catch {
      // Ignore errors — still clear local state
    }
    logout();
  };

  const refreshUser = async () => {
    await checkAuth();
  };

  const getUserData = useCallback(() => {
    return user;
  }, [user]);

  return {
    user,
    // SECURITY: Reading JWT from localStorage is vulnerable to XSS attacks.
    token: typeof window !== 'undefined' ? localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN) : null,
    loading,
    isAuthenticated: !!user,
    login,
    logout: handleLogout,
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
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);
      setIsAuthenticated(!!token);

      if (token) {
        try {
          const userData = await getCurrentUser();
          setUser(userData);
        } catch (err) {
          logger.error('Optional auth check failed', err);
        }
      }

      setLoading(false);
    };

    initAuth();
  }, []);

  // SECURITY: JWT stored in localStorage is vulnerable to XSS attacks.
  const getToken = () => localStorage.getItem(STORAGE_KEYS.ACCESS_TOKEN);

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
export function useOwnership(resourceOwnerId: number | string | undefined): {
  isOwner: boolean;
  isAdmin: boolean;
  canEdit: boolean;
  isLoading: boolean;
} {
  const { user, loading } = useOptionalAuth();

  const isOwner = user && resourceOwnerId !== undefined
    ? String(user.id) === String(resourceOwnerId)
    : false;
  const isAdmin = user ? user.role === 'admin' : false;
  const canEdit = isOwner || isAdmin;

  return {
    isOwner,
    isAdmin,
    canEdit,
    isLoading: loading,
  };
}
