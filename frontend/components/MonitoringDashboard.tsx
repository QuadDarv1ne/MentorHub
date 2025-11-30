'use client';

import React, { useState, useEffect } from 'react';
import { 
  Server, 
  Activity, 
  AlertTriangle, 
  Clock, 
  HardDrive,
  Cpu,
  MemoryStick,
  Settings,
  Bell,
  Trash2
} from 'lucide-react';
import Card from '@/components/ui/Card';
import MetricCard from '@/components/ui/MetricCard';
import Chart from '@/components/ui/Chart';
import AlertDisplay from '@/components/ui/AlertDisplay';
import { 
  getMetrics, 
  getAlerts,
  updateAlertThresholds,
  resetMetrics
} from '@/lib/api/monitoring';
import { MetricsData, Alert } from '@/lib/api/monitoring';

const MonitoringDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<MetricsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [refreshInterval] = useState(30000); // 30 seconds
  const [showThresholdModal, setShowThresholdModal] = useState(false);
  const [newThresholds, setNewThresholds] = useState<Record<string, number>>({
    error_rate: 5.0,
    response_time: 2.0,
    cpu_usage: 80.0,
    memory_usage: 90.0
  });

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

  // Reset metrics
  const handleResetMetrics = async () => {
    if (window.confirm('Вы уверены, что хотите сбросить все метрики? Это действие нельзя отменить.')) {
      try {
        await resetMetrics();
        fetchMetrics(); // Refresh after reset
        alert('Метрики успешно сброшены');
      } catch (err) {
        alert('Ошибка при сбросе метрик');
        console.error('Error resetting metrics:', err);
      }
    }
  };

  // Handle threshold update
  const handleThresholdChange = (key: string, value: string) => {
    setNewThresholds(prev => ({
      ...prev,
      [key]: parseFloat(value) || 0
    }));
  };

  // Save threshold updates
  const saveThresholds = async () => {
    try {
      await updateAlertThresholds(newThresholds);
      setShowThresholdModal(false);
      fetchMetrics(); // Refresh after update
      alert('Пороговые значения успешно обновлены');
    } catch (err) {
      alert('Ошибка при обновлении пороговых значений');
      console.error('Error updating thresholds:', err);
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
        <div className="flex items-center space-x-2">
          <div className="text-sm text-gray-500">
            Обновлено: {new Date(metrics.timestamp).toLocaleTimeString()}
          </div>
          <button
            onClick={() => setShowThresholdModal(true)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            title="Настройки алертов"
          >
            <Settings className="h-4 w-4" />
          </button>
          <button
            onClick={handleResetMetrics}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            title="Сбросить метрики"
          >
            <Trash2 className="h-4 w-4" />
          </button>
          <button
            onClick={fetchMetrics}
            className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            title="Обновить данные"
          >
            <RefreshCw className="h-4 w-4" />
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

      {/* Threshold Settings Modal */}
      {showThresholdModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Настройки алертов</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Порог ошибок (%)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={newThresholds.error_rate}
                  onChange={(e) => handleThresholdChange('error_rate', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Порог времени ответа (сек)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={newThresholds.response_time}
                  onChange={(e) => handleThresholdChange('response_time', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Порог CPU (%)
                </label>
                <input
                  type="number"
                  step="1"
                  value={newThresholds.cpu_usage}
                  onChange={(e) => handleThresholdChange('cpu_usage', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Порог памяти (%)
                </label>
                <input
                  type="number"
                  step="1"
                  value={newThresholds.memory_usage}
                  onChange={(e) => handleThresholdChange('memory_usage', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>
            
            <div className="mt-6 flex justify-end space-x-3">
              <button
                onClick={() => setShowThresholdModal(false)}
                className="px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Отмена
              </button>
              <button
                onClick={saveThresholds}
                className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Alerts Section */}
      <Card>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-gray-900">Системные предупреждения</h3>
          <Bell className="h-5 w-5 text-gray-500" />
        </div>
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