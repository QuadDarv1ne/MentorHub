"use client";
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  text?: string;
  variant?: 'default' | 'dots' | 'bars' | 'pulse';
}

export default function LoadingSpinner({ 
  size = 'md', 
  fullScreen = false,
  text,
  variant = 'default'
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'h-8 w-8 border-2',
    md: 'h-12 w-12 border-2',
    lg: 'h-16 w-16 border-4'
  };

  const renderSpinner = () => {
    switch (variant) {
      case 'dots':
        return (
          <div className="flex space-x-2">
            <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce"></div>
            <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
            <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
          </div>
        );
      
      case 'bars':
        return (
          <div className="flex space-x-1">
            {[...Array(5)].map((_, i) => (
              <div 
                key={i}
                className="w-2 bg-indigo-600 rounded-full animate-pulse"
                style={{ 
                  height: size === 'sm' ? '20px' : size === 'md' ? '30px' : '40px',
                  animationDelay: `${i * 0.1}s`
                }}
              ></div>
            ))}
          </div>
        );
      
      case 'pulse':
        return (
          <div className="relative">
            <div className={`${sizeClasses[size]} border-indigo-600 border-t-transparent rounded-full animate-spin opacity-30`}></div>
            <div className={`absolute top-0 left-0 ${sizeClasses[size]} border-indigo-600 border-t-transparent rounded-full animate-ping`}></div>
          </div>
        );
      
      default:
        return (
          <div className={`${sizeClasses[size]} border-indigo-600 border-t-transparent rounded-full animate-spin`}></div>
        );
    }
  };

  const spinner = (
    <div className="flex flex-col items-center justify-center">
      {renderSpinner()}
      {text && (
        <p className="mt-4 text-sm text-gray-600">{text}</p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center">
        {spinner}
      </div>
    );
  }

  return spinner;
}

// Enhanced loading states for different sections
export function PageLoader({ text = "Загрузка страницы..." }: { text?: string }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-100 flex items-center justify-center">
      <div className="text-center">
        <div className="relative inline-block mb-6">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-24 h-24 bg-indigo-100 rounded-full opacity-20 animate-ping"></div>
          </div>
          <div className="relative w-24 h-24 bg-indigo-100 rounded-full flex items-center justify-center">
            <div className="h-12 w-12 border-4 border-indigo-600 border-t-transparent rounded-full animate-spin"></div>
          </div>
        </div>
        <p className="text-lg font-medium text-gray-700">{text}</p>
        <p className="text-sm text-gray-500 mt-2">Это может занять несколько секунд</p>
      </div>
    </div>
  );
}

export function SectionLoader({ text = "Загрузка данных..." }: { text?: string }) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center">
        <div className="flex space-x-2 justify-center mb-4">
          <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce"></div>
          <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
          <div className="h-3 w-3 bg-indigo-600 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
        </div>
        <p className="text-sm text-gray-600">{text}</p>
      </div>
    </div>
  );
}

export function InlineLoader({ size = 'sm' }: { size?: 'sm' | 'md' }) {
  const sizeClasses = size === 'sm' ? 'h-4 w-4' : 'h-6 w-6';
  
  return (
    <div className="inline-flex items-center">
      <div className={`${sizeClasses} border-2 border-indigo-600 border-t-transparent rounded-full animate-spin mr-2`}></div>
      <span className="text-sm text-gray-600">Загрузка...</span>
    </div>
  );
}