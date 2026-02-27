/**
 * Dashboard Page Component
 */
import React, { useState, useEffect } from 'react';
import KPICard from '../components/KPICard';
import SyncButton from '../components/SyncButton';
import TrendsChart from '../components/TrendsChart';
import { getKPISummary, getKPITrends, getSyncStatus } from '../services/api';

function Dashboard() {
  const [kpis, setKpis] = useState(null);
  const [trends, setTrends] = useState([]);
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load KPIs and trends
      const [kpiData, trendsData, syncData] = await Promise.all([
        getKPISummary(),
        getKPITrends(30),
        getSyncStatus()
      ]);

      setKpis(kpiData);
      setTrends(trendsData.trends || []);
      setSyncStatus(syncData);
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Loading view
  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
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
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <KPICard
          title="Total GMV"
          value={kpis ? `£${kpis.total_gmv.toLocaleString()}` : '£0'}
          subtitle={kpis?.date_range ? `Last 30 days` : ''}
          icon="💰"
        />
        <KPICard
          title="Total Orders"
          value={kpis ? kpis.total_orders.toLocaleString() : '0'}
          subtitle={`${kpis?.completed_orders || 0} completed`}
          icon="📦"
        />
        <KPICard
          title="Avg Order Value"
          value={kpis ? `£${kpis.average_order_value.toFixed(2)}` : '£0'}
          subtitle="Per transaction"
          icon="💳"
        />
        <KPICard
          title="Items Sold"
          value={kpis ? kpis.total_items_sold.toLocaleString() : '0'}
          subtitle="Total units"
          icon="🛒"
        />
      </div>

      {/* Sync Button */}
      <div className="mb-8">
        <SyncButton onSyncComplete={loadData} />
      </div>

      {/* Trends Chart */}
      <div className="mb-8">
        <TrendsChart data={trends} />
      </div>

      {/* Order Status Breakdown */}
      {kpis && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status</h3>
          <div className="grid grid-cols-3 gap-4">
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">
                {kpis.completed_orders}
              </div>
              <div className="text-sm text-gray-600 mt-1">Completed</div>
            </div>
            <div className="text-center p-4 bg-yellow-50 rounded-lg">
              <div className="text-2xl font-bold text-yellow-600">
                {kpis.pending_orders}
              </div>
              <div className="text-sm text-gray-600 mt-1">Pending</div>
            </div>
            <div className="text-center p-4 bg-red-50 rounded-lg">
              <div className="text-2xl font-bold text-red-600">
                {kpis.cancelled_orders}
              </div>
              <div className="text-sm text-gray-600 mt-1">Cancelled</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Dashboard;
