'use client';

import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Activity, 
  AlertTriangle, 
  Clock, 
  HardDrive,
  Cpu,
  MemoryStick
} from 'lucide-react';
import Card from '@/components/ui/Card';
import MetricCard from '@/components/ui/MetricCard';
import Chart from '@/components/ui/Chart';
import AlertDisplay from '@/components/ui/AlertDisplay';
import { 
  getMetrics, 
  getAlerts
} from '@/lib/api/monitoring';
import { MetricsData, Alert } from '@/lib/api/monitoring';

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [refreshInterval] = useState(30000); // 30 seconds

  // Fetch metrics
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const metricsData = await getMetrics();
      setMetrics(metricsData);
      
      // Fetch alerts
      try {
        const alertData = await getAlerts();
        setAlerts(alertData.alerts || []);
      } catch (alertError) {
        console.warn('Failed to fetch alerts:', alertError);
      }
      
      setError(null);
    } catch (err) {
      setError('Failed to fetch monitoring data');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  // Initial load and setup interval
  useEffect(() => {
    fetchMetrics();
    
    const interval = setInterval(fetchMetrics, refreshInterval);
    return () => clearInterval(interval);
  }, [refreshInterval]);

  if (loading && !metrics) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-red-500" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">Ошибка загрузки</h3>
          <p className="mt-1 text-gray-500">{error}</p>
          <div className="mt-6">
            <button
              onClick={fetchMetrics}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              Повторить попытку
            </button>
          </div>
        </div>
      </Card>
    );
  }

  if (!metrics) {
    return (
      <Card>
        <div className="text-center py-12">
          <Server className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-lg font-medium text-gray-900">Нет данных</h3>
          <p className="mt-1 text-gray-500">Метрики еще не загружены</p>
        </div>
      </Card>
    );
  }

  // Prepare chart data
  const requestRateData = metrics.popular_endpoints.slice(0, 5).map(ep => ({
    label: ep.endpoint.substring(0, 10) + (ep.endpoint.length > 10 ? '...' : ''),
    value: ep.calls
  }));

  const errorRateData = metrics.popular_endpoints.slice(0, 5).map(ep => ({
    label: ep.endpoint.substring(0, 10) + (ep.endpoint.length > 10 ? '...' : ''),
    value: ep.error_count
  }));

  const slowEndpointsData = metrics.slow_endpoints.slice(0, 5).map(se => ({
    label: se.endpoint.substring(0, 10) + (se.endpoint.length > 10 ? '...' : ''),
    value: Math.round(se.avg_ms)
  }));

  return (
    <div className="space-y-6">
      {/* Control Panel */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900">Мониторинг системы</h2>
        <div className="flex items-center space-x-4">
          <div className="text-sm text-gray-500">
            Обновлено: {new Date(metrics.timestamp).toLocaleTimeString()}
          </div>
          <button
            onClick={fetchMetrics}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить
          </button>
        </div>
      </div>

      {/* System Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Состояние системы"
          value={alerts.length > 0 ? "Предупреждения" : "Нормально"}
          icon={Server}
          color={alerts.length > 0 ? "red" : "green"}
        />
        
        <MetricCard
          title="Запросов в секунду"
          value={metrics.application.requests_per_second.toFixed(2)}
          icon={Activity}
          color="blue"
        />
        
        <MetricCard
          title="Процент ошибок"
          value={`${metrics.application.error_rate_percent.toFixed(2)}%`}
          icon={AlertTriangle}
          color={metrics.application.error_rate_percent > 5 ? "red" : "green"}
        />
        
        <MetricCard
          title="Uptime"
          value={`${Math.floor(metrics.uptime_seconds / 3600)}ч ${Math.floor((metrics.uptime_seconds % 3600) / 60)}м`}
          icon={Clock}
          color="purple"
        />
      </div>

      {/* System Resources */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="CPU Usage"
          value={`${metrics.system.cpu_percent.toFixed(1)}%`}
          icon={Cpu}
          color={metrics.system.cpu_percent > 80 ? "red" : metrics.system.cpu_percent > 60 ? "orange" : "green"}
        />
        
        <MetricCard
          title="Memory Usage"
          value={`${metrics.system.memory_percent.toFixed(1)}%`}
          icon={MemoryStick}
          color={metrics.system.memory_percent > 90 ? "red" : metrics.system.memory_percent > 75 ? "orange" : "green"}
        />
        
        <MetricCard
          title="Disk Usage"
          value={`${metrics.system.disk_percent.toFixed(1)}%`}
          icon={HardDrive}
          color={metrics.system.disk_percent > 90 ? "red" : metrics.system.disk_percent > 75 ? "orange" : "green"}
        />
      </div>

      {/* Alerts Section */}
      <Card>
        <AlertDisplay alerts={alerts} />
      </Card>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <Chart 
            data={requestRateData} 
            title="Топ популярных endpoints" 
            color="blue"
            height={250}
          />
        </Card>
        
        <Card>
          <Chart 
            data={errorRateData} 
            title="Ошибки по endpoints" 
            color="red"
            height={250}
          />
        </Card>
        
        <Card>
          <Chart 
            data={slowEndpointsData} 
            title="Медленные endpoints (мс)" 
            color="orange"
            height={250}
          />
        </Card>
        
        <Card>
          <div className="w-full">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Детали системы</h3>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Всего запросов</span>
                <span className="font-medium">{metrics.application.total_requests.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Всего ошибок</span>
                <span className="font-medium">{metrics.application.total_errors.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Память</span>
                <span className="font-medium">
                  {Math.round(metrics.system.memory_used_mb)} MB / {Math.round(metrics.system.memory_total_mb)} MB
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Диск</span>
                <span className="font-medium">
                  {Math.round(metrics.system.disk_used_gb)} GB / {Math.round(metrics.system.disk_total_gb)} GB
                </span>
              </div>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

// We need to import RefreshCw icon
const RefreshCw = ({ className }: { className?: string }) => (
  <svg className={className} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8" />
    <path d="M21 3v5h-5" />
    <path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16" />
    <path d="M8 16H3v5" />
  </svg>
);

export default MonitoringDashboard;