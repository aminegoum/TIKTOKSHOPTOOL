import { useState, useEffect } from 'react';
import { 
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from 'recharts';
import { format, subDays } from 'date-fns';

const API_BASE_URL = 'http://localhost:8000';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

export default function Analytics() {
  const [dateRange, setDateRange] = useState({
    startDate: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
    endDate: format(new Date(), 'yyyy-MM-dd')
  });
  
  const [loading, setLoading] = useState(true);
  const [shopMetrics, setShopMetrics] = useState(null);
  const [videoPerformance, setVideoPerformance] = useState(null);
  const [livePerformance, setLivePerformance] = useState(null);
  const [productPerformance, setProductPerformance] = useState(null);
  const [brandPerformance, setBrandPerformance] = useState(null);
  const [localSummary, setLocalSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, [dateRange]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Fetch KPI summary (same as Dashboard - ensures consistency)
      const kpiRes = await fetch(
        `${API_BASE_URL}/api/kpis/summary?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}`
      );
      if (kpiRes.ok) {
        const kpiData = await kpiRes.json();
        setLocalSummary(kpiData);
      }

      // Fetch brand performance (from database - always works)
      const brandRes = await fetch(
        `${API_BASE_URL}/api/analytics/brands/performance?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}`
      );
      if (brandRes.ok) {
        const brandData = await brandRes.json();
        setBrandPerformance(brandData);
      }

      // Try to fetch TikTok API data (may fail due to permissions)
      try {
        const shopRes = await fetch(
          `${API_BASE_URL}/api/analytics/shop/performance?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&currency=LOCAL`
        );
        if (shopRes.ok) {
          const shopData = await shopRes.json();
          setShopMetrics(shopData);
        }
      } catch (err) {
        console.log('Shop metrics not available:', err.message);
      }

      try {
        const videoRes = await fetch(
          `${API_BASE_URL}/api/analytics/videos/overview?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&currency=LOCAL`
        );
        if (videoRes.ok) {
          const videoData = await videoRes.json();
          setVideoPerformance(videoData);
        }
      } catch (err) {
        console.log('Video metrics not available:', err.message);
      }

      try {
        const liveRes = await fetch(
          `${API_BASE_URL}/api/analytics/lives/overview?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&currency=LOCAL`
        );
        if (liveRes.ok) {
          const liveData = await liveRes.json();
          setLivePerformance(liveData);
        }
      } catch (err) {
        console.log('LIVE metrics not available:', err.message);
      }

      try {
        const productRes = await fetch(
          `${API_BASE_URL}/api/analytics/products/performance?start_date=${dateRange.startDate}&end_date=${dateRange.endDate}&page_size=10&currency=LOCAL`
        );
        if (productRes.ok) {
          const productData = await productRes.json();
          setProductPerformance(productData);
        }
      } catch (err) {
        console.log('Product metrics not available:', err.message);
      }

    } catch (err) {
      console.error('Error fetching analytics:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const formatCurrency = (value) => {
    if (!value) return '£0.00';
    return new Intl.NumberFormat('en-GB', {
      style: 'currency',
      currency: 'GBP'
    }).format(value);
  };

  const formatNumber = (value) => {
    if (!value) return '0';
    return new Intl.NumberFormat('en-GB').format(value);
  };

  const MetricCard = ({ title, value, subtitle, icon, trend }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {subtitle && <p className="text-sm text-gray-500 mt-1">{subtitle}</p>}
        </div>
        {icon && <div className="text-4xl">{icon}</div>}
      </div>
      {trend && (
        <div className={`mt-4 text-sm ${trend > 0 ? 'text-green-600' : 'text-red-600'}`}>
          {trend > 0 ? '↑' : '↓'} {Math.abs(trend)}% vs previous period
        </div>
      )}
    </div>
  );

  if (loading && !shopMetrics) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">📊 Analytics Dashboard</h1>
        <p className="text-gray-600 mt-2">Comprehensive performance insights for your TikTok Shop</p>
      </div>

      {/* Date Range Selector */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex items-center gap-4">
          <label className="text-sm font-medium text-gray-700">Date Range:</label>
          <input
            type="date"
            value={dateRange.startDate}
            onChange={(e) => setDateRange({ ...dateRange, startDate: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2 text-sm"
          />
          <span className="text-gray-500">to</span>
          <input
            type="date"
            value={dateRange.endDate}
            onChange={(e) => setDateRange({ ...dateRange, endDate: e.target.value })}
            className="border border-gray-300 rounded px-3 py-2 text-sm"
          />
          <button
            onClick={fetchAnalytics}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 text-sm"
          >
            Apply
          </button>
          <button
            onClick={() => setDateRange({
              startDate: format(subDays(new Date(), 7), 'yyyy-MM-dd'),
              endDate: format(new Date(), 'yyyy-MM-dd')
            })}
            className="text-blue-500 hover:text-blue-700 text-sm"
          >
            Last 7 days
          </button>
          <button
            onClick={() => setDateRange({
              startDate: format(subDays(new Date(), 30), 'yyyy-MM-dd'),
              endDate: format(new Date(), 'yyyy-MM-dd')
            })}
            className="text-blue-500 hover:text-blue-700 text-sm"
          >
            Last 30 days
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-6">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Shop Performance Overview - Consistent with Dashboard */}
      {localSummary && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">🏪 Shop Performance</h2>
            <div className="text-sm text-gray-600">
              {localSummary.date_range && (
                <span>
                  {new Date(localSummary.date_range.start).toLocaleDateString()} - {new Date(localSummary.date_range.end).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <MetricCard
              title="Total GMV"
              value={formatCurrency(localSummary?.total_gmv || 0)}
              icon="💰"
              subtitle="Gross Merchandise Value"
            />
            <MetricCard
              title="Total Orders"
              value={formatNumber(localSummary?.total_orders || 0)}
              icon="📦"
              subtitle={`${localSummary?.completed_orders || 0} completed`}
            />
            <MetricCard
              title="Items Sold"
              value={formatNumber(localSummary?.total_items_sold || 0)}
              icon="🛍️"
              subtitle="Total units"
            />
            <MetricCard
              title="Avg Order Value"
              value={formatCurrency(localSummary?.average_order_value || 0)}
              icon="📊"
              subtitle="Per order"
            />
          </div>
          
          {/* Additional KPIs Row */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mt-6">
            <MetricCard
              title="Est. Net Revenue"
              value={formatCurrency(localSummary?.estimated_net_revenue || 0)}
              icon="💵"
              subtitle="After estimated fees"
            />
            <MetricCard
              title="Pending Orders"
              value={formatNumber(localSummary?.pending_orders || 0)}
              icon="⏳"
              subtitle="Awaiting shipment"
            />
            <MetricCard
              title="Cancelled Orders"
              value={formatNumber(localSummary?.cancelled_orders || 0)}
              icon="❌"
              subtitle="Cancelled"
            />
            <MetricCard
              title="Unique Customers"
              value={formatNumber(localSummary?.unique_customers || 0)}
              icon="👥"
              subtitle="Total customers"
            />
          </div>
        </div>
      )}

      {/* Brand Performance Analytics */}
      {brandPerformance && brandPerformance.brands && brandPerformance.brands.length > 0 && (
        <div className="mb-8">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold text-gray-900">🏷️ Brand Performance</h2>
            <button
              onClick={() => {
                const data = brandPerformance.brands.map(brand => ({
                  Brand: brand.brand,
                  GMV: brand.gmv,
                  Orders: brand.orders,
                  'Items Sold': brand.items_sold,
                  'Avg Order Value': brand.avg_order_value
                }));
                const csv = [
                  Object.keys(data[0]).join(','),
                  ...data.map(row => Object.values(row).join(','))
                ].join('\n');
                const blob = new Blob([csv], { type: 'text/csv' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `brand-performance-${dateRange.startDate}-to-${dateRange.endDate}.csv`;
                a.click();
              }}
              className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 text-sm flex items-center gap-2"
            >
              📥 Export Brands CSV
            </button>
          </div>
          
          {/* Brand Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <MetricCard
              title="Total Brands"
              value={formatNumber(brandPerformance?.summary?.total_brands || 0)}
              icon="🏷️"
              subtitle="Unique brands"
            />
            <MetricCard
              title="Brand GMV"
              value={formatCurrency(brandPerformance?.summary?.total_gmv || 0)}
              icon="💰"
              subtitle="Total revenue"
            />
            <MetricCard
              title="Brand Orders"
              value={formatNumber(brandPerformance?.summary?.total_orders || 0)}
              icon="📦"
              subtitle="All orders"
            />
            <MetricCard
              title="Items Sold"
              value={formatNumber(brandPerformance?.summary?.total_items_sold || 0)}
              icon="🛍️"
              subtitle="Total units"
            />
          </div>

          {/* Top 10 Brands Bar Chart */}
          <div className="bg-white rounded-lg shadow p-6 mb-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Top 10 Brands by GMV</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={brandPerformance.brands.slice(0, 10)}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="brand" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Bar dataKey="gmv" fill="#8884d8" name="GMV" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Brand Performance Table */}
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Brand
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    GMV
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Orders
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Items Sold
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Order Value
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {brandPerformance.brands.slice(0, 20).map((brand, index) => (
                  <tr key={brand.brand} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                      {brand.brand}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                      {formatCurrency(brand.gmv)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(brand.orders)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(brand.items_sold)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatCurrency(brand.avg_order_value)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Video Performance */}
      {videoPerformance && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🎥 Video Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="Video GMV"
              value={formatCurrency(videoPerformance?.data?.metrics?.[0]?.gmv || 0)}
              icon="🎬"
            />
            <MetricCard
              title="Video Views"
              value={formatNumber(videoPerformance?.data?.metrics?.[0]?.video_views || 0)}
              icon="👁️"
            />
            <MetricCard
              title="Video CTR"
              value={`${(videoPerformance?.data?.metrics?.[0]?.click_through_rate || 0).toFixed(2)}%`}
              icon="🖱️"
            />
          </div>
        </div>
      )}

      {/* LIVE Performance */}
      {livePerformance && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📺 LIVE Performance</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <MetricCard
              title="LIVE GMV"
              value={formatCurrency(livePerformance?.data?.metrics?.[0]?.gmv || 0)}
              icon="🔴"
            />
            <MetricCard
              title="Peak Viewers"
              value={formatNumber(livePerformance?.data?.metrics?.[0]?.peak_viewers || 0)}
              icon="👥"
            />
            <MetricCard
              title="LIVE Sessions"
              value={formatNumber(livePerformance?.data?.metrics?.[0]?.live_count || 0)}
              icon="📹"
            />
          </div>
        </div>
      )}

      {/* Top Products */}
      {productPerformance?.data?.products && productPerformance.data.products.length > 0 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">🏆 Top Performing Products</h2>
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Rank
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Product ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    GMV
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Units Sold
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Orders
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {productPerformance.data.products.slice(0, 10).map((product, index) => (
                  <tr key={product.product_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      #{index + 1}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.product_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">
                      {formatCurrency(product.gmv)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(product.units_sold)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatNumber(product.orders)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Performance Charts */}
      {shopMetrics?.data?.metrics && shopMetrics.data.metrics.length > 1 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">📈 Performance Trends</h2>
          <div className="bg-white rounded-lg shadow p-6">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={shopMetrics.data.metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip formatter={(value) => formatCurrency(value)} />
                <Legend />
                <Line type="monotone" dataKey="gmv" stroke="#8884d8" name="GMV" />
                <Line type="monotone" dataKey="orders" stroke="#82ca9d" name="Orders" />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* No Data Message */}
      {!loading && !shopMetrics && !error && (
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded">
          <p>No analytics data available for the selected date range. Try selecting a different date range or check if your shop has any activity.</p>
        </div>
      )}
    </div>
  );
}
