/**
 * MetricDisplay Component
 * Display individual metrics with icons and optional trends
 */
import React from 'react';

const MetricDisplay = ({ 
  label, 
  value, 
  icon, 
  trend = null,
  trendDirection = null, // 'up' | 'down' | 'neutral'
  subtitle = null,
  valueColor = 'text-gray-900',
  size = 'medium' // 'small' | 'medium' | 'large'
}) => {
  const sizeClasses = {
    small: {
      value: 'text-xl',
      label: 'text-xs',
      icon: 'text-lg',
    },
    medium: {
      value: 'text-2xl',
      label: 'text-sm',
      icon: 'text-2xl',
    },
    large: {
      value: 'text-3xl',
      label: 'text-base',
      icon: 'text-3xl',
    },
  };

  const getTrendColor = () => {
    if (!trendDirection) return 'text-gray-500';
    switch (trendDirection) {
      case 'up':
        return 'text-green-600';
      case 'down':
        return 'text-red-600';
      default:
        return 'text-gray-500';
    }
  };

  const getTrendIcon = () => {
    if (!trendDirection) return null;
    switch (trendDirection) {
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '→';
    }
  };

  return (
    <div className="flex items-start gap-3">
      {icon && (
        <div className={`${sizeClasses[size].icon} flex-shrink-0`}>
          {icon}
        </div>
      )}
      <div className="flex-1 min-w-0">
        <div className={`font-bold ${valueColor} ${sizeClasses[size].value}`}>
          {value}
        </div>
        <div className={`${sizeClasses[size].label} text-gray-600 mt-1`}>
          {label}
        </div>
        {subtitle && (
          <div className="text-xs text-gray-500 mt-1">
            {subtitle}
          </div>
        )}
        {trend && (
          <div className={`text-xs font-medium mt-2 flex items-center gap-1 ${getTrendColor()}`}>
            <span>{getTrendIcon()}</span>
            <span>{trend}</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default MetricDisplay;
