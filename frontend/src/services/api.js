/**
 * API service for TikTok Shop Dashboard
 */
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Authentication
export const getAuthStatus = async () => {
  const response = await api.get('/api/auth/status');
  return response.data;
};

export const getAuthUrl = async () => {
  const response = await api.get('/api/auth/authorize-url');
  return response.data;
};

export const handleAuthCallback = async (code, state) => {
  const response = await api.post('/api/auth/callback', { code, state });
  return response.data;
};

// Data Sync
export const triggerSync = async (syncType, daysBack = 30) => {
  const response = await api.post('/api/sync/trigger', {
    sync_type: syncType,
    days_back: daysBack,
  });
  return response.data;
};

// Global refresh - syncs all data types
export const triggerGlobalRefresh = async (daysBack = 30) => {
  const response = await api.post('/api/sync/trigger', {
    sync_type: 'all',
    days_back: daysBack,
  });
  return response.data;
};

export const getSyncStatus = async () => {
  const response = await api.get('/api/sync/status');
  return response.data;
};

// KPIs
export const getKPISummary = async (startDate = null, endDate = null) => {
  const params = {};
  if (startDate) params.start_date = startDate;
  if (endDate) params.end_date = endDate;
  
  const response = await api.get('/api/kpis/summary', { params });
  return response.data;
};

export const getKPITrends = async (days = 30) => {
  const response = await api.get('/api/kpis/trends', { params: { days } });
  return response.data;
};

export const getTopProducts = async (limit = 10) => {
  const response = await api.get('/api/kpis/top-products', { params: { limit } });
  return response.data;
};

// Analytics - Finance
export const getFinanceTransactions = async (daysBack = 30) => {
  const response = await api.get('/api/analytics/finance/transactions', { params: { days_back: daysBack } });
  return response.data;
};

export const getSettlements = async (daysBack = 30) => {
  const response = await api.get('/api/analytics/finance/settlements', { params: { days_back: daysBack } });
  return response.data;
};

// Analytics - Returns
export const getReturns = async (daysBack = 30, pageSize = 20) => {
  const response = await api.get('/api/analytics/returns', { params: { days_back: daysBack, page_size: pageSize } });
  return response.data;
};

// Analytics - Fulfillment
export const getFulfillmentOrders = async (pageSize = 20) => {
  const response = await api.get('/api/analytics/fulfillment/orders', { params: { page_size: pageSize } });
  return response.data;
};

// Analytics - Reviews
export const getProductReviews = async (productId, pageSize = 20) => {
  const response = await api.get(`/api/analytics/products/${productId}/reviews`, { params: { page_size: pageSize } });
  return response.data;
};

// Analytics - Promotions
export const getPromotions = async (pageSize = 20) => {
  const response = await api.get('/api/analytics/promotions', { params: { page_size: pageSize } });
  return response.data;
};

// Analytics - Shop Performance
export const getShopPerformance = async (startDate, endDate, currency = 'LOCAL') => {
  const response = await api.get('/api/analytics/shop/performance', {
    params: { start_date: startDate, end_date: endDate, currency }
  });
  return response.data;
};

export default api;
