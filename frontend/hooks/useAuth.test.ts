/**
 * Тесты для useAuth hook
 */

import { describe, it, expect, beforeEach, afterEach } from '@jest/globals'
import { renderHook, act, waitFor } from '@testing-library/react'
import { useAuth, useOptionalAuth, useRole, useOwnership } from './useAuth'

// Mock next/navigation
jest.mock('next/navigation', () => ({
  useRouter: () => ({
    push: jest.fn(),
    replace: jest.fn(),
    prefetch: jest.fn(),
    back: jest.fn(),
  }),
}))

// Mock fetch
const mockFetch = jest.fn()
global.fetch = mockFetch as any

describe('useAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('должен вернуть isAuthenticated=false когда нет токена', async () => {
    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('должен вернуть isAuthenticated=true когда есть токен', async () => {
    // Setup mock token
    const mockToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjo5OTk5OTk5OTk5fQ.dozjgO2hcLh4K442R99999'
    localStorage.setItem('access_token', mockToken)

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        role: 'student',
        full_name: 'Test User',
        is_active: true,
        is_verified: true,
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
      }),
    })

    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).toEqual({
      id: 1,
      email: 'test@example.com',
      username: 'testuser',
      role: 'student',
      full_name: 'Test User',
      is_active: true,
      is_verified: true,
    })
  })

  it('должен сделать logout при истёкшем токене без refresh', async () => {
    // Setup expired token
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.expired'
    localStorage.setItem('access_token', expiredToken)

    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(localStorage.getItem('access_token')).toBeNull()
  })

  it('должен попробовать refresh токена при истёкшем access token', async () => {
    // Setup expired token and refresh token
    const expiredToken = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwiZXhwIjoxfQ.expired'
    const refreshToken = 'refresh_token_123'
    localStorage.setItem('access_token', expiredToken)
    localStorage.setItem('refresh_token', refreshToken)

    // Mock successful refresh
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          access_token: 'new_access_token',
          refresh_token: 'new_refresh_token',
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          id: 1,
          email: 'test@example.com',
          username: 'testuser',
          role: 'student',
        }),
      })

    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Check that refresh was called
    expect(mockFetch).toHaveBeenCalledWith(
      '/api/v1/auth/refresh',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
    )
  })

  it('должен выполнить login и сохранить данные', async () => {
    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    const mockUser = {
      id: 1,
      email: 'test@example.com',
      username: 'testuser',
      role: 'student' as const,
      full_name: 'Test User',
      is_active: true,
      is_verified: true,
      created_at: '2024-01-01T00:00:00Z',
    }

    await act(async () => {
      await result.current.login('test_token', mockUser)
    })

    expect(localStorage.getItem('access_token')).toBe('test_token')
    expect(localStorage.getItem('user_name')).toBe('Test User')
    expect(localStorage.getItem('user_role')).toBe('student')
    expect(result.current.user).toEqual(mockUser)
  })

  it('должен выполнить logout и очистить данные', async () => {
    localStorage.setItem('access_token', 'test_token')
    localStorage.setItem('refresh_token', 'refresh_token')
    localStorage.setItem('user_name', 'Test User')
    localStorage.setItem('user_role', 'student')

    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await act(async () => {
      result.current.logout()
    })

    expect(localStorage.getItem('access_token')).toBeNull()
    expect(localStorage.getItem('refresh_token')).toBeNull()
    expect(localStorage.getItem('user_name')).toBeNull()
    expect(localStorage.getItem('user_role')).toBeNull()
    expect(result.current.user).toBeNull()
  })

  it('должен обновить данные пользователя через refreshUser', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'old@example.com',
        username: 'olduser',
        role: 'student',
      }),
    })

    const { result } = renderHook(() => useAuth({ redirectOnAuth: false }))

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    // Change mock for refresh
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'new@example.com',
        username: 'newuser',
        role: 'mentor',
      }),
    })

    await act(async () => {
      await result.current.refreshUser()
    })

    expect(result.current.user?.email).toBe('new@example.com')
    expect(result.current.user?.role).toBe('mentor')
  })
})

describe('useOptionalAuth Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('должен вернуть isAuthenticated=false без токена', async () => {
    const { result } = renderHook(() => useOptionalAuth())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(false)
    expect(result.current.user).toBeNull()
  })

  it('должен вернуть isAuthenticated=true с токеном', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        role: 'student',
      }),
    })

    const { result } = renderHook(() => useOptionalAuth())

    await waitFor(() => {
      expect(result.current.loading).toBe(false)
    })

    expect(result.current.isAuthenticated).toBe(true)
    expect(result.current.user).not.toBeNull()
  })
})

describe('useRole Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('должен вернуть hasRole=false когда пользователь не авторизован', async () => {
    const { result } = renderHook(() => useRole(['admin', 'mentor']))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.hasRole).toBe(false)
  })

  it('должен вернуть hasRole=true когда роль совпадает', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        role: 'admin',
      }),
    })

    const { result } = renderHook(() => useRole(['admin', 'mentor']))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.hasRole).toBe(true)
  })

  it('должен вернуть hasRole=false когда роль не совпадает', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 1,
        email: 'test@example.com',
        username: 'testuser',
        role: 'student',
      }),
    })

    const { result } = renderHook(() => useRole(['admin', 'mentor']))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.hasRole).toBe(false)
  })
})

describe('useOwnership Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    localStorage.clear()
  })

  it('должен вернуть isOwner=true когда user.id === resourceOwnerId', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 5,
        email: 'test@example.com',
        username: 'testuser',
        role: 'student',
      }),
    })

    const { result } = renderHook(() => useOwnership(5))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.isOwner).toBe(true)
    expect(result.current.canEdit).toBe(true)
    expect(result.current.isAdmin).toBe(false)
  })

  it('должен вернуть isAdmin=true когда роль admin', async () => {
    localStorage.setItem('access_token', 'valid_token')

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: 5,
        email: 'test@example.com',
        username: 'testuser',
        role: 'admin',
      }),
    })

    const { result } = renderHook(() => useOwnership(10))

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false)
    })

    expect(result.current.isOwner).toBe(false)
    expect(result.current.isAdmin).toBe(true)
    expect(result.current.canEdit).toBe(true)
  })
})
