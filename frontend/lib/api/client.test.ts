/**
 * Тесты для API client с retry logic
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { fetchWithRetry, ApiError, NetworkError, TimeoutError } from './client'

// Mock fetch globally
const mockFetch = vi.fn()
global.fetch = mockFetch as any

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('fetchWithRetry', () => {
    it('должен успешно вернуть ответ при первом запросе', async () => {
      const mockResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
        json: async () => ({ data: 'test' }),
      }
      mockFetch.mockResolvedValueOnce(mockResponse)

      const response = await fetchWithRetry('/api/test')

      expect(mockFetch).toHaveBeenCalledTimes(1)
      expect(response.ok).toBe(true)
    })

    it('должен повторить запрос при 500 ошибке', async () => {
      const errorResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      }
      const successResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
      }

      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(errorResponse)
        .mockResolvedValueOnce(successResponse)

      const response = await fetchWithRetry('/api/test', {}, {
        maxRetries: 3,
        retryDelay: 10,
        retryStatusCodes: [500, 502, 503],
      })

      expect(mockFetch).toHaveBeenCalledTimes(3)
      expect(response.ok).toBe(true)
    })

    it('должен выбросить ошибку после максимального количества попыток', async () => {
      const errorResponse = {
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
      }

      mockFetch.mockResolvedValue(errorResponse)

      await expect(
        fetchWithRetry('/api/test', {}, {
          maxRetries: 2,
          retryDelay: 10,
          retryStatusCodes: [500],
        })
      ).rejects.toThrow(ApiError)

      expect(mockFetch).toHaveBeenCalledTimes(3) // 1 + 2 retries
    })

    it('должен выбросить TimeoutError при превышении времени ожидания', async () => {
      mockFetch.mockImplementation(() => {
        return new Promise((_, reject) => {
          setTimeout(() => reject(new Error('Timeout')), 50000)
        })
      })

      await expect(
        fetchWithRetry('/api/test', {}, {
          maxRetries: 0,
          retryDelay: 10,
          retryStatusCodes: [],
        })
      ).rejects.toThrow(TimeoutError)
    })

    it('не должен повторять запрос при 400 ошибке', async () => {
      const errorResponse = {
        ok: false,
        status: 400,
        statusText: 'Bad Request',
      }

      mockFetch.mockResolvedValueOnce(errorResponse)

      await expect(
        fetchWithRetry('/api/test', {}, {
          maxRetries: 3,
          retryDelay: 10,
          retryStatusCodes: [500, 502],
        })
      ).rejects.toThrow(ApiError)

      expect(mockFetch).toHaveBeenCalledTimes(1)
    })

    it('должен повторить при 429 Too Many Requests', async () => {
      const rateLimitResponse = {
        ok: false,
        status: 429,
        statusText: 'Too Many Requests',
      }
      const successResponse = {
        ok: true,
        status: 200,
        statusText: 'OK',
      }

      mockFetch
        .mockResolvedValueOnce(rateLimitResponse)
        .mockResolvedValueOnce(successResponse)

      const response = await fetchWithRetry('/api/test', {}, {
        maxRetries: 2,
        retryDelay: 10,
        retryStatusCodes: [429, 500, 502],
      })

      expect(mockFetch).toHaveBeenCalledTimes(2)
      expect(response.ok).toBe(true)
    })
  })

  describe('ApiError', () => {
    it('должен создать ApiError с правильными свойствами', () => {
      const error = new ApiError('Test error', 404, 'NOT_FOUND')

      expect(error.name).toBe('ApiError')
      expect(error.message).toBe('Test error')
      expect(error.status).toBe(404)
      expect(error.code).toBe('NOT_FOUND')
    })
  })

  describe('NetworkError', () => {
    it('должен создать NetworkError с правильными свойствами', () => {
      const error = new NetworkError('Network is unreachable')

      expect(error.name).toBe('NetworkError')
      expect(error.message).toBe('Network is unreachable')
    })
  })

  describe('TimeoutError', () => {
    it('должен создать TimeoutError с правильными свойствами', () => {
      const error = new TimeoutError('Request timed out after 30s')

      expect(error.name).toBe('TimeoutError')
      expect(error.message).toBe('Request timed out after 30s')
    })
  })
})
