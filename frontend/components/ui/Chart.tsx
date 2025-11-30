'use client';

import React from 'react';

interface ChartProps {
  data: Array<{ label: string; value: number }>;
  title: string;
  color?: string;
  height?: number;
}

const Chart: React.FC<ChartProps> = ({ 
  data, 
  title, 
  color = 'indigo', 
  height = 200 
}) => {
  // Find min and max values for scaling
  const values = data.map(item => item.value);
  const maxValue = Math.max(...values, 1);
  const minValue = Math.min(...values, 0);
  const range = maxValue - minValue || 1;

  // Color classes
  const colorClasses = {
    indigo: {
      bar: 'fill-indigo-500',
      gradientStart: 'stop-indigo-400',
      gradientEnd: 'stop-indigo-600',
    },
    blue: {
      bar: 'fill-blue-500',
      gradientStart: 'stop-blue-400',
      gradientEnd: 'stop-blue-600',
    },
    green: {
      bar: 'fill-green-500',
      gradientStart: 'stop-green-400',
      gradientEnd: 'stop-green-600',
    },
    red: {
      bar: 'fill-red-500',
      gradientStart: 'stop-red-400',
      gradientEnd: 'stop-red-600',
    },
    orange: {
      bar: 'fill-orange-500',
      gradientStart: 'stop-orange-400',
      gradientEnd: 'stop-orange-600',
    },
  };

  const colors = colorClasses[color as keyof typeof colorClasses] || colorClasses.indigo;

  return (
    <div className="w-full">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="relative">
        <svg 
          width="100%" 
          height={height} 
          viewBox={`0 0 ${data.length * 60 + 40} ${height}`}
          className="overflow-visible"
        >
          {/* Gradient definition */}
          <defs>
            <linearGradient id={`gradient-${color}`} x1="0%" y1="0%" x2="0%" y2="100%">
              <stop offset="0%" className={colors.gradientStart} />
              <stop offset="100%" className={colors.gradientEnd} />
            </linearGradient>
          </defs>
          
          {/* Bars */}
          {data.map((item, index) => {
            const barHeight = ((item.value - minValue) / range) * (height - 40) + 10;
            const x = index * 60 + 20;
            const y = height - barHeight - 20;
            
            return (
              <g key={index}>
                {/* Bar */}
                <rect
                  x={x}
                  y={y}
                  width="30"
                  height={barHeight}
                  className={colors.bar}
                  rx="4"
                />
                
                {/* Label */}
                <text
                  x={x + 15}
                  y={height - 5}
                  textAnchor="middle"
                  className="text-xs fill-gray-600"
                >
                  {item.label}
                </text>
                
                {/* Value */}
                <text
                  x={x + 15}
                  y={y - 5}
                  textAnchor="middle"
                  className="text-xs fill-gray-700 font-medium"
                >
                  {item.value}
                </text>
              </g>
            );
          })}
          
          {/* Baseline */}
          <line
            x1="20"
            y1={height - 20}
            x2={data.length * 60 + 20}
            y2={height - 20}
            stroke="#e5e7eb"
            strokeWidth="1"
          />
        </svg>
      </div>
    </div>
  );
};

export default Chart;