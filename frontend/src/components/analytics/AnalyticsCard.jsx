/**
 * AnalyticsCard Component
 * Reusable card wrapper for analytics sections
 */
import React from 'react';

const AnalyticsCard = ({ 
  title, 
  subtitle, 
  children, 
  icon, 
  loading = false,
  error = null,
  className = ''
}) => {
  return (
    <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          {icon && (
            <div className="text-2xl">
              {icon}
            </div>
          )}
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              {title}
            </h3>
            {subtitle && (
              <p className="text-sm text-gray-500 mt-1">
                {subtitle}
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="mt-4">
        {loading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="p-4 bg-red-50 text-red-800 rounded-lg text-sm">
            <p className="font-medium">Error loading data</p>
            <p className="mt-1">{error}</p>
          </div>
        ) : (
          children
        )}
      </div>
    </div>
  );
};

export default AnalyticsCard;
