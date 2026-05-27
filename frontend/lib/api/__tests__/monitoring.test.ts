/**
 * Monitoring API Service Tests
 */

// Set env var before any imports that depend on it
// Note: do NOT include /api/v1 - the client adds it automatically
process.env.NEXT_PUBLIC_API_BASE_URL = 'http://localhost:8000';

import {
  getMetrics,
  resetMetrics,
  getAlerts,
  updateAlertThresholds
} from '../monitoring';

const API_BASE = `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1`;

// Mock the fetch function
global.fetch = jest.fn();

describe('Monitoring API Service', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();

    // Mock localStorage
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => 'test-token'),
      },
      writable: true,
    });
  });

  describe('getMetrics', () => {
    it('should fetch metrics successfully', async () => {
      const mockResponse = {
        timestamp: '2023-01-01T00:00:00Z',
        uptime_seconds: 3600,
        system: {
          cpu_percent: 45.2,
          memory_percent: 65.8,
          memory_used_mb: 512,
          memory_total_mb: 1024,
          disk_percent: 42.1,
          disk_used_gb: 50.5,
          disk_total_gb: 120
        },
        application: {
          total_requests: 15234,
          total_errors: 23,
          error_rate_percent: 0.15,
          requests_per_second: 4.23
        },
        slow_endpoints: [],
        popular_endpoints: [],
        slow_requests_details: {},
        alerts: []
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getMetrics();

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalled();
      const [url, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(url).toBe(`${API_BASE}/monitoring/metrics`);
      expect(options.method ?? 'GET').toBe('GET');
      expect(options.headers['Authorization']).toBe('Bearer test-token');
    });
  });

  describe('getAlerts', () => {
    it('should fetch alerts successfully', async () => {
      const mockResponse = {
        alerts: [
          {
            type: 'high_cpu_usage',
            severity: 'warning',
            message: 'High CPU usage: 85.2%',
            threshold: 80.0
          }
        ]
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await getAlerts();

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalled();
      const [url, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(url).toBe(`${API_BASE}/monitoring/alerts`);
      expect(options.method ?? 'GET').toBe('GET');
      expect(options.headers['Authorization']).toBe('Bearer test-token');
    });
  });

  describe('updateAlertThresholds', () => {
    it('should update alert thresholds successfully', async () => {
      const mockThresholds = {
        error_rate: 5.0,
        response_time: 2.0
      };

      const mockResponse = {
        message: 'Пороговые значения успешно обновлены'
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await updateAlertThresholds(mockThresholds);

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalled();
      const [url, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(url).toBe(`${API_BASE}/monitoring/alerts/thresholds`);
      expect(options.method).toBe('POST');
      expect(options.headers['Authorization']).toBe('Bearer test-token');
      expect(JSON.parse(options.body)).toEqual(mockThresholds);
    });
  });

  describe('resetMetrics', () => {
    it('should reset metrics successfully', async () => {
      const mockResponse = {
        message: 'Метрики успешно сброшены'
      };

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockResponse),
      });

      const result = await resetMetrics();

      expect(result).toEqual(mockResponse);
      expect(global.fetch).toHaveBeenCalled();
      const [url, options] = (global.fetch as jest.Mock).mock.calls[0];
      expect(url).toBe(`${API_BASE}/monitoring/metrics/reset`);
      expect(options.method).toBe('POST');
      expect(options.headers['Authorization']).toBe('Bearer test-token');
    });
  });
});
