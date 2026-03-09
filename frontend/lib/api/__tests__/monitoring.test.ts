/**
 * Monitoring API Service Tests
 */

import { 
  getMetrics, 
  resetMetrics, 
  getAlerts, 
  updateAlertThresholds
} from '../monitoring';

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
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/monitoring/metrics',
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
      );
    });

    it('should throw error when fetch fails', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        statusText: 'Not Found',
      });

      await expect(getMetrics()).rejects.toThrow('Failed to fetch metrics: Not Found');
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
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/monitoring/alerts',
        expect.objectContaining({
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
      );
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
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/monitoring/alerts/thresholds',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
          body: JSON.stringify(mockThresholds),
        })
      );
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
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/monitoring/metrics/reset',
        expect.objectContaining({
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer test-token',
          },
        })
      );
    });
  });
});