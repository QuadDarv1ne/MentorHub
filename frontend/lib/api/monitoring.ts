const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// Types for monitoring data
export interface SystemMetrics {
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_total_mb: number;
  disk_percent: number;
  disk_used_gb: number;
  disk_total_gb: number;
}

export interface ApplicationMetrics {
  total_requests: number;
  total_errors: number;
  error_rate_percent: number;
  requests_per_second: number;
}

export interface SlowEndpoint {
  endpoint: string;
  avg_ms: number;
  max_ms: number;
  count: number;
  error_count: number;
  status_codes: Record<string, number>;
}

export interface PopularEndpoint {
  endpoint: string;
  calls: number;
  error_count: number;
}

export interface Alert {
  type: string;
  severity: 'warning' | 'critical';
  message: string;
  threshold?: number;
  endpoint?: string;
}

export interface MetricsData {
  timestamp: string;
  uptime_seconds: number;
  system: SystemMetrics;
  application: ApplicationMetrics;
  slow_endpoints: SlowEndpoint[];
  popular_endpoints: PopularEndpoint[];
  slow_requests_details: Record<string, unknown>;
  alerts: Alert[];
}

export interface CacheStats {
  cache_stats: Record<string, unknown>;
}

/**
 * Get application performance metrics
 */
export async function getMetrics(): Promise<MetricsData> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/metrics`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch metrics: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Reset performance metrics
 */
export async function resetMetrics(): Promise<{ message: string }> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/metrics/reset`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to reset metrics: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get current alerts
 */
export async function getAlerts(): Promise<{ alerts: Alert[] }> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/alerts`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch alerts: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Update alert thresholds
 */
export async function updateAlertThresholds(thresholds: Record<string, number>): Promise<{ message: string }> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/alerts/thresholds`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(thresholds),
  });

  if (!response.ok) {
    throw new Error(`Failed to update alert thresholds: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get cache statistics
 */
export async function getCacheStats(): Promise<CacheStats> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/cache/stats`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch cache stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Reset cache statistics
 */
export async function resetCacheStats(): Promise<{ message: string }> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/cache/reset-stats`;
  
  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to reset cache stats: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get detailed health check
 */
export async function getDetailedHealth(): Promise<Record<string, unknown>> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
  if (!token) {
    throw new Error('Authentication required');
  }

  const url = `${API_BASE_URL}/monitoring/health/detailed`;
  
  const response = await fetch(url, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch detailed health: ${response.statusText}`);
  }

  return response.json();
}