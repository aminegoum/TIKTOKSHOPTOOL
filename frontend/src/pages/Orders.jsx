/**
 * Orders Page Component
 * Displays orders table with KPIs and filtering
 */
import React, { useState, useEffect } from 'react';

function Orders() {
  const [orders, setOrders] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState(null);
  
  // Filter input values (what user types)
  const [statusFilterInput, setStatusFilterInput] = useState('');
  const [searchQueryInput, setSearchQueryInput] = useState('');
  const [brandFilterInput, setBrandFilterInput] = useState('');
  
  // Applied filters (what's actually sent to API)
  const [statusFilter, setStatusFilter] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [brandFilter, setBrandFilter] = useState('');
  
  const [expandedOrder, setExpandedOrder] = useState(null);
  const [orderDetails, setOrderDetails] = useState({});
  const [loadingDetails, setLoadingDetails] = useState({});

  useEffect(() => {
    loadOrders();
  }, [page, statusFilter, searchQuery, brandFilter]);

  const loadOrders = async () => {
    try {
      setLoading(true);
      setError(null);

      // Build query params
      const params = new URLSearchParams({
        page: page.toString(),
        page_size: '50'
      });
      
      if (statusFilter) params.append('status', statusFilter);
      if (searchQuery) params.append('search', searchQuery);
      if (brandFilter) params.append('brand', brandFilter);

      console.log('🔍 Loading orders with params:', params.toString());
      console.log('Brand filter:', brandFilter);

      // Load orders and stats
      const [ordersRes, statsRes] = await Promise.all([
        fetch(`http://localhost:8000/api/orders/list?${params}`),
        fetch('http://localhost:8000/api/orders/stats')
      ]);

      if (!ordersRes.ok || !statsRes.ok) {
        throw new Error('Failed to load orders');
      }

      const ordersData = await ordersRes.json();
      const statsData = await statsRes.json();

      console.log('📦 Received orders:', ordersData.orders.length);
      console.log('📊 Pagination:', ordersData.pagination);

      setOrders(ordersData.orders);
      setPagination(ordersData.pagination);
      setStats(statsData);
    } catch (err) {
      console.error('Error loading orders:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadOrderDetails = async (orderId) => {
    if (orderDetails[orderId]) {
      // Already loaded, just toggle
      setExpandedOrder(expandedOrder === orderId ? null : orderId);
      return;
    }

    try {
      setLoadingDetails({ ...loadingDetails, [orderId]: true });
      
      const response = await fetch(`http://localhost:8000/api/orders/${orderId}`);
      if (!response.ok) {
        throw new Error('Failed to load order details');
      }

      const data = await response.json();
      setOrderDetails({ ...orderDetails, [orderId]: data });
      setExpandedOrder(orderId);
    } catch (err) {
      console.error('Error loading order details:', err);
    } finally {
      setLoadingDetails({ ...loadingDetails, [orderId]: false });
    }
  };

  const handleApplyFilters = (e) => {
    e.preventDefault();
    // Apply the filter inputs to the actual filters
    setStatusFilter(statusFilterInput);
    setSearchQuery(searchQueryInput);
    setBrandFilter(brandFilterInput);
    setPage(1); // Reset to first page when filters change
  };

  const handleClearFilters = () => {
    // Clear both inputs and applied filters
    setStatusFilterInput('');
    setSearchQueryInput('');
    setBrandFilterInput('');
    setStatusFilter('');
    setSearchQuery('');
    setBrandFilter('');
    setPage(1);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatCurrency = (amount) => {
    return `£${parseFloat(amount).toFixed(2)}`;
  };

  const getStatusColor = (status) => {
    const colors = {
      'COMPLETED': 'bg-green-100 text-green-800',
      'AWAITING_SHIPMENT': 'bg-yellow-100 text-yellow-800',
      'AWAITING_COLLECTION': 'bg-blue-100 text-blue-800',
      'IN_TRANSIT': 'bg-purple-100 text-purple-800',
      'DELIVERED': 'bg-green-100 text-green-800',
      'CANCELLED': 'bg-red-100 text-red-800',
      'UNPAID': 'bg-gray-100 text-gray-800'
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading && !orders.length) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading orders...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-800 rounded-lg">
          ❌ {error}
        </div>
      )}

      {/* KPI Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Orders</div>
            <div className="text-3xl font-bold text-gray-900">
              {stats.total_orders.toLocaleString()}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total GMV</div>
            <div className="text-3xl font-bold text-green-600">
              {formatCurrency(stats.total_gmv)}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Avg Order Value</div>
            <div className="text-3xl font-bold text-blue-600">
              {formatCurrency(stats.avg_order_value)}
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <div className="text-sm text-gray-600 mb-1">Total Items</div>
            <div className="text-3xl font-bold text-purple-600">
              {stats.total_items.toLocaleString()}
            </div>
          </div>
        </div>
      )}

      {/* Status Breakdown */}
      {stats && stats.status_breakdown && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status Breakdown</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {Object.entries(stats.status_breakdown).map(([status, data]) => (
              <div key={status} className="text-center p-4 bg-gray-50 rounded-lg">
                <div className="text-2xl font-bold text-gray-900">{data.count}</div>
                <div className="text-xs text-gray-600 mt-1">{status.replace(/_/g, ' ')}</div>
                <div className="text-sm text-gray-500 mt-1">{formatCurrency(data.total_amount)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <form onSubmit={handleApplyFilters}>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
            <input
              type="text"
              placeholder="Search by Order ID..."
              value={searchQueryInput}
              onChange={(e) => setSearchQueryInput(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <select
              value={statusFilterInput}
              onChange={(e) => setStatusFilterInput(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="">All Statuses</option>
              <option value="COMPLETED">Completed</option>
              <option value="AWAITING_SHIPMENT">Awaiting Shipment</option>
              <option value="AWAITING_COLLECTION">Awaiting Collection</option>
              <option value="IN_TRANSIT">In Transit</option>
              <option value="DELIVERED">Delivered</option>
              <option value="CANCELLED">Cancelled</option>
              <option value="UNPAID">Unpaid</option>
            </select>
            <input
              type="text"
              placeholder="Filter by brand..."
              value={brandFilterInput}
              onChange={(e) => setBrandFilterInput(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
            <input
              type="text"
              placeholder="Filter by creator..."
              disabled
              title="Creator filtering coming soon"
              className="px-4 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-400 cursor-not-allowed"
            />
          </div>
          <div className="flex gap-2">
            <button
              type="submit"
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Apply Filters
            </button>
            <button
              type="button"
              onClick={handleClearFilters}
              className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
            >
              Clear Filters
            </button>
            {(statusFilter || searchQuery || brandFilter) && (
              <div className="flex items-center gap-2 ml-4 text-sm text-gray-600">
                <span className="font-medium">Active filters:</span>
                {searchQuery && <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded">Order ID: {searchQuery}</span>}
                {statusFilter && <span className="px-2 py-1 bg-green-100 text-green-800 rounded">Status: {statusFilter}</span>}
                {brandFilter && <span className="px-2 py-1 bg-purple-100 text-purple-800 rounded">Brand: {brandFilter}</span>}
              </div>
            )}
          </div>
        </form>
      </div>

      {/* Orders Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Order ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Items
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Brand(s)
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Creator
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tracking
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {orders.map((order) => (
                <React.Fragment key={order.id}>
                  <tr
                    onClick={() => loadOrderDetails(order.id)}
                    className="hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                      {expandedOrder === order.id ? '▼' : '▶'} {order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(order.status)}`}>
                        {order.status.replace(/_/g, ' ')}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(order.created_time)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {formatCurrency(order.total_amount)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.item_count} items
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                      {order.brands || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400 italic">
                      {order.creator || 'Coming soon'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {order.tracking_number || 'N/A'}
                    </td>
                  </tr>
                  {expandedOrder === order.id && orderDetails[order.id] && (
                    <tr>
                      <td colSpan="8" className="px-6 py-4 bg-gray-50">
                        <div className="space-y-4">
                          {/* Products */}
                          <div>
                            <h4 className="font-semibold text-gray-900 mb-2">Products ({orderDetails[order.id].products?.length || 0})</h4>
                            <div className="space-y-2">
                              {orderDetails[order.id].products?.map((product, idx) => (
                                <div key={idx} className="flex items-start gap-4 p-3 bg-white rounded border">
                                  {product.sku_image && (
                                    <img src={product.sku_image} alt={product.product_name} className="w-16 h-16 object-cover rounded" />
                                  )}
                                  <div className="flex-1">
                                    <div className="font-medium text-gray-900">{product.product_name}</div>
                                    <div className="text-sm text-gray-500">SKU: {product.seller_sku}</div>
                                    <div className="text-sm text-gray-500">{product.sku_name}</div>
                                  </div>
                                  <div className="text-right">
                                    <div className="font-semibold text-gray-900">{formatCurrency(product.sale_price)}</div>
                                    {product.platform_discount > 0 && (
                                      <div className="text-xs text-green-600">-{formatCurrency(product.platform_discount)} discount</div>
                                    )}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Payment Details */}
                          {orderDetails[order.id].payment_details && (
                            <div>
                              <h4 className="font-semibold text-gray-900 mb-2">Payment Details</h4>
                              <div className="bg-white p-3 rounded border space-y-1">
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">Subtotal:</span>
                                  <span className="font-medium">{formatCurrency(orderDetails[order.id].payment_details.subtotal)}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                  <span className="text-gray-600">Shipping:</span>
                                  <span className="font-medium">{formatCurrency(orderDetails[order.id].payment_details.shipping_fee)}</span>
                                </div>
                                {orderDetails[order.id].payment_details.platform_discount > 0 && (
                                  <div className="flex justify-between text-sm text-green-600">
                                    <span>Platform Discount:</span>
                                    <span>-{formatCurrency(orderDetails[order.id].payment_details.platform_discount)}</span>
                                  </div>
                                )}
                                <div className="flex justify-between text-sm pt-2 border-t">
                                  <span className="font-semibold">Total:</span>
                                  <span className="font-bold">{formatCurrency(orderDetails[order.id].payment_details.total)}</span>
                                </div>
                                <div className="text-sm text-gray-500 pt-1">
                                  Payment Method: {orderDetails[order.id].payment_method || 'N/A'}
                                </div>
                              </div>
                            </div>
                          )}
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination && (
          <div className="bg-gray-50 px-6 py-4 flex items-center justify-between border-t border-gray-200">
            <div className="text-sm text-gray-700">
              Showing page <span className="font-medium">{pagination.page}</span> of{' '}
              <span className="font-medium">{pagination.total_pages}</span>
              {' '}({pagination.total_count.toLocaleString()} total orders)
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(page - 1)}
                disabled={!pagination.has_prev}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={!pagination.has_next}
                className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default Orders;
