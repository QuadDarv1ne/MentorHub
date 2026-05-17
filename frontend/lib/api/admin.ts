import { apiRequest, publicRequest } from './client'

export interface AdminUser {
  id: number
  email: string
  username: string
  full_name: string | null
  role: 'student' | 'mentor' | 'admin'
  is_active: boolean
  is_verified: boolean
  avatar_url: string | null
  created_at: string
  updated_at: string
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PlatformStats {
  total_users: number
  total_students: number
  total_mentors: number
  total_admins: number
  verified_users: number
  active_users: number
  total_sessions: number
  completed_sessions: number
  scheduled_sessions: number
  total_courses: number
  active_courses: number
  total_enrollments: number
  total_reviews: number
  avg_rating: number
  total_revenue: number
  new_users_today: number
  active_sessions_now: number
}

export async function getAdminUsers(params?: {
  page?: number
  page_size?: number
  role?: string
  status?: string
  search?: string
  sort_by?: string
  sort_order?: string
}): Promise<AdminUserListResponse> {
  const searchParams = new URLSearchParams()
  if (params?.page) searchParams.set('page', String(params.page))
  if (params?.page_size) searchParams.set('page_size', String(params.page_size))
  if (params?.role) searchParams.set('role', params.role)
  if (params?.status) searchParams.set('status', params.status)
  if (params?.search) searchParams.set('search', params.search)
  if (params?.sort_by) searchParams.set('sort_by', params.sort_by)
  if (params?.sort_order) searchParams.set('sort_order', params.sort_order)

  const qs = searchParams.toString()
  return apiRequest<AdminUserListResponse>(`/admin/users${qs ? `?${qs}` : ''}`)
}

export async function getAdminUser(userId: number): Promise<AdminUser> {
  return apiRequest<AdminUser>(`/admin/users/${userId}`)
}

export async function updateUserRole(userId: number, role: string): Promise<AdminUser> {
  return apiRequest<AdminUser>(`/admin/users/${userId}/role`, {
    method: 'PUT',
    body: JSON.stringify({ role }),
  })
}

export async function updateUserStatus(userId: number, isActive: boolean): Promise<AdminUser> {
  return apiRequest<AdminUser>(`/admin/users/${userId}/status`, {
    method: 'PUT',
    body: JSON.stringify({ is_active: isActive }),
  })
}

export async function getPlatformStats(): Promise<PlatformStats> {
  return apiRequest<PlatformStats>('/admin/stats/platform')
}

export interface MonitoringMetrics {
  requests_total?: number
  requests_per_second?: number
  error_rate?: number
  avg_response_time?: number
  p95_response_time?: number
  p99_response_time?: number
  slow_requests?: number
  memory_usage_percent?: number
  cpu_usage_percent?: number
  disk_usage_percent?: number
  uptime_seconds?: number
  active_connections?: number
}

export interface Alert {
  id: string
  severity: 'info' | 'warning' | 'critical'
  message: string
  timestamp: string
  metric: string
  value: number
  threshold: number
}

export async function getMonitoringMetrics(): Promise<MonitoringMetrics> {
  return apiRequest<MonitoringMetrics>('/admin/metrics')
}

export async function getAlerts(): Promise<Alert[]> {
  return apiRequest<Alert[]>('/admin/alerts')
}
