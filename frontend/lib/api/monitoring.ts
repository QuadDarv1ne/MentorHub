/**
 * Monitoring API — metrics, alerts, cache stats, health checks.
 */

import { apiRequest } from './client'

export interface SystemMetrics {
  cpu_percent: number
  memory_percent: number
  memory_used_mb: number
  memory_total_mb: number
  disk_percent: number
  disk_used_gb: number
  disk_total_gb: number
}

export interface ApplicationMetrics {
  total_requests: number
  total_errors: number
  error_rate_percent: number
  requests_per_second: number
}

export interface SlowEndpoint {
  endpoint: string
  avg_ms: number
  max_ms: number
  count: number
  error_count: number
  status_codes: Record<string, number>
}

export interface PopularEndpoint {
  endpoint: string
  calls: number
  error_count: number
}

export interface Alert {
  type: string
  severity: 'warning' | 'critical'
  message: string
  threshold?: number
  endpoint?: string
}

export interface MetricsData {
  timestamp: string
  uptime_seconds: number
  system: SystemMetrics
  application: ApplicationMetrics
  slow_endpoints: SlowEndpoint[]
  popular_endpoints: PopularEndpoint[]
  slow_requests_details: Record<string, unknown>
  alerts: Alert[]
}

export interface CacheStats {
  cache_stats: Record<string, unknown>
}

/** Get application performance metrics */
export async function getMetrics(): Promise<MetricsData> {
  return apiRequest<MetricsData>('/monitoring/metrics')
}

/** Reset performance metrics */
export async function resetMetrics(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/monitoring/metrics/reset', {
    method: 'POST',
  })
}

/** Get current alerts */
export async function getAlerts(): Promise<{ alerts: Alert[] }> {
  return apiRequest<{ alerts: Alert[] }>('/monitoring/alerts')
}

/** Update alert thresholds */
export async function updateAlertThresholds(thresholds: Record<string, number>): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/monitoring/alerts/thresholds', {
    method: 'POST',
    body: JSON.stringify(thresholds),
  })
}

/** Get cache statistics */
export async function getCacheStats(): Promise<CacheStats> {
  return apiRequest<CacheStats>('/monitoring/cache/stats')
}

/** Reset cache statistics */
export async function resetCacheStats(): Promise<{ message: string }> {
  return apiRequest<{ message: string }>('/monitoring/cache/reset-stats', {
    method: 'POST',
  })
}

/** Get detailed health check */
export async function getDetailedHealth(): Promise<Record<string, unknown>> {
  return apiRequest<Record<string, unknown>>('/monitoring/health/detailed')
}
