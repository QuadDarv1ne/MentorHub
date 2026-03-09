'use client';

import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

interface Alert {
  type: string;
  severity: 'warning' | 'critical' | 'info';
  message: string;
  threshold?: number;
  endpoint?: string;
}

interface AlertDisplayProps {
  alerts: Alert[];
}

const AlertDisplay: React.FC<AlertDisplayProps> = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="rounded-lg border border-green-200 bg-green-50 p-4">
        <div className="flex items-center">
          <CheckCircle className="h-5 w-5 text-green-600" />
          <p className="ml-3 text-sm text-green-800">
            Все системы работают нормально. Нет активных предупреждений.
          </p>
        </div>
      </div>
    );
  }

  const getAlertIcon = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return <AlertTriangle className="h-5 w-5 text-red-600" />;
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      default:
        return <Info className="h-5 w-5 text-blue-600" />;
    }
  };

  const getAlertColor = (severity: Alert['severity']) => {
    switch (severity) {
      case 'critical':
        return 'border-red-200 bg-red-50 text-red-800';
      case 'warning':
        return 'border-yellow-200 bg-yellow-50 text-yellow-800';
      default:
        return 'border-blue-200 bg-blue-50 text-blue-800';
    }
  };

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-medium text-gray-900">Системные предупреждения</h3>
      <div className="space-y-2">
        {alerts.map((alert, index) => (
          <div 
            key={index} 
            className={`rounded-lg border p-4 ${getAlertColor(alert.severity)}`}
          >
            <div className="flex items-start">
              {getAlertIcon(alert.severity)}
              <div className="ml-3">
                <p className="text-sm font-medium">
                  {alert.message}
                </p>
                {alert.endpoint && (
                  <p className="mt-1 text-xs">
                    Endpoint: {alert.endpoint}
                  </p>
                )}
                {alert.threshold && (
                  <p className="mt-1 text-xs">
                    Порог: {alert.threshold}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AlertDisplay;