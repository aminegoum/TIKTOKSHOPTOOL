/**
 * Analytics Service for TikTok Shop Dashboard
 * Provides functions to call all 15 analytics endpoints
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Format date to YYYY-MM-DD format
 */
export const formatDate = (date) => {
  if (!date) return null;
  const d = new Date(date);
  return d.toISOString().split('T')[0];
};

/**
 * Get date range for common periods
 */
export const getDateRange = (period) => {
  const endDate = new Date();
  const startDate = new Date();
  
  switch (period) {
    case '7days':
      startDate.setDate(endDate.getDate() - 7);
      break;
    case '30days':
      startDate.setDate(endDate.getDate() - 30);
      break;
    case '90days':
      startDate.setDate(endDate.getDate() - 90);
      break;
    default:
      startDate.setDate(endDate.getDate() - 30);
  }
  
  return {
    start_date: formatDate(startDate),
    end_date: formatDate(endDate),
  };
};

// ============================================================================
// SHOP PERFORMANCE ANALYTICS
// ============================================================================

/**
 * Get shop performance metrics
 * Endpoint: /api/analytics/shop/performance/metrics
 */
export const getShopPerformanceMetrics = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/shop/performance/metrics', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching shop performance metrics:', error);
    throw error;
  }
};

/**
 * Get shop performance overview
 * Endpoint: /api/analytics/shop/performance/overview
 */
export const getShopPerformanceOverview = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/shop/performance/overview', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching shop performance overview:', error);
    throw error;
  }
};

/**
 * Get hourly performance data
 * Endpoint: /api/analytics/shop/performance/hourly
 */
export const getHourlyPerformance = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/shop/performance/hourly', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching hourly performance:', error);
    throw error;
  }
};

/**
 * Get shop trends
 * Endpoint: /api/analytics/shop/trends
 */
export const getShopTrends = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/shop/trends', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching shop trends:', error);
    throw error;
  }
};

// ============================================================================
// CONTENT PERFORMANCE ANALYTICS
// ============================================================================

/**
 * Get video performances
 * Endpoint: /api/analytics/videos/performances
 */
export const getVideoPerformances = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/videos/performances', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching video performances:', error);
    throw error;
  }
};

/**
 * Get live stream performance
 * Endpoint: /api/analytics/live/{live_id}/performance
 */
export const getLivePerformance = async (liveId, startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get(`/api/analytics/live/${liveId}/performance`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching live performance:', error);
    throw error;
  }
};

// ============================================================================
// PRODUCT ANALYTICS
// ============================================================================

/**
 * Get product performance
 * Endpoint: /api/analytics/products/{product_id}/performance
 */
export const getProductPerformance = async (productId, startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get(`/api/analytics/products/${productId}/performance`, { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching product performance:', error);
    throw error;
  }
};

/**
 * Get SKU performances
 * Endpoint: /api/analytics/skus/performance
 */
export const getSKUPerformances = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/skus/performance', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching SKU performances:', error);
    throw error;
  }
};

/**
 * Get top products
 * Endpoint: /api/analytics/products/top
 */
export const getTopProducts = async (startDate, endDate, limit = 10) => {
  try {
    const params = { limit };
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/products/top', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching top products:', error);
    throw error;
  }
};

// ============================================================================
// SALES ANALYTICS
// ============================================================================

/**
 * Get order statistics
 * Endpoint: /api/analytics/orders/statistics
 */
export const getOrderStatistics = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/orders/statistics', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching order statistics:', error);
    throw error;
  }
};

/**
 * Get order trends
 * Endpoint: /api/analytics/orders/trends
 */
export const getOrderTrends = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/orders/trends', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching order trends:', error);
    throw error;
  }
};

// ============================================================================
// TRAFFIC ANALYTICS
// ============================================================================

/**
 * Get traffic overview
 * Endpoint: /api/analytics/traffic/overview
 */
export const getTrafficOverview = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/traffic/overview', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching traffic overview:', error);
    throw error;
  }
};

/**
 * Get traffic sources
 * Endpoint: /api/analytics/traffic/sources
 */
export const getTrafficSources = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/traffic/sources', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching traffic sources:', error);
    throw error;
  }
};

// ============================================================================
// FINANCIAL ANALYTICS
// ============================================================================

/**
 * Get revenue report
 * Endpoint: /api/analytics/finance/revenue
 */
export const getRevenueReport = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/finance/revenue', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching revenue report:', error);
    throw error;
  }
};

/**
 * Get settlement report
 * Endpoint: /api/analytics/finance/settlements
 */
export const getSettlementReport = async (startDate, endDate) => {
  try {
    const params = {};
    if (startDate) params.start_date = formatDate(startDate);
    if (endDate) params.end_date = formatDate(endDate);
    
    const response = await api.get('/api/analytics/finance/settlements', { params });
    return response.data;
  } catch (error) {
    console.error('Error fetching settlement report:', error);
    throw error;
  }
};

// ============================================================================
// BATCH OPERATIONS
// ============================================================================

/**
 * Fetch all analytics data for a given date range
 * Useful for loading the complete analytics dashboard
 */
export const getAllAnalytics = async (startDate, endDate) => {
  try {
    const [
      shopMetrics,
      shopOverview,
      shopTrends,
      orderStats,
      orderTrends,
      trafficOverview,
      trafficSources,
      revenue,
      topProducts,
    ] = await Promise.allSettled([
      getShopPerformanceMetrics(startDate, endDate),
      getShopPerformanceOverview(startDate, endDate),
      getShopTrends(startDate, endDate),
      getOrderStatistics(startDate, endDate),
      getOrderTrends(startDate, endDate),
      getTrafficOverview(startDate, endDate),
      getTrafficSources(startDate, endDate),
      getRevenueReport(startDate, endDate),
      getTopProducts(startDate, endDate, 10),
    ]);

    return {
      shopMetrics: shopMetrics.status === 'fulfilled' ? shopMetrics.value : null,
      shopOverview: shopOverview.status === 'fulfilled' ? shopOverview.value : null,
      shopTrends: shopTrends.status === 'fulfilled' ? shopTrends.value : null,
      orderStats: orderStats.status === 'fulfilled' ? orderStats.value : null,
      orderTrends: orderTrends.status === 'fulfilled' ? orderTrends.value : null,
      trafficOverview: trafficOverview.status === 'fulfilled' ? trafficOverview.value : null,
      trafficSources: trafficSources.status === 'fulfilled' ? trafficSources.value : null,
      revenue: revenue.status === 'fulfilled' ? revenue.value : null,
      topProducts: topProducts.status === 'fulfilled' ? topProducts.value : null,
    };
  } catch (error) {
    console.error('Error fetching all analytics:', error);
    throw error;
  }
};

export default {
  // Utilities
  formatDate,
  getDateRange,
  
  // Shop Performance
  getShopPerformanceMetrics,
  getShopPerformanceOverview,
  getHourlyPerformance,
  getShopTrends,
  
  // Content Performance
  getVideoPerformances,
  getLivePerformance,
  
  // Product Analytics
  getProductPerformance,
  getSKUPerformances,
  getTopProducts,
  
  // Sales Analytics
  getOrderStatistics,
  getOrderTrends,
  
  // Traffic Analytics
  getTrafficOverview,
  getTrafficSources,
  
  // Financial Analytics
  getRevenueReport,
  getSettlementReport,
  
  // Batch Operations
  getAllAnalytics,
};
