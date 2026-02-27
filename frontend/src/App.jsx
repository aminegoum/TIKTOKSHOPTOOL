/**
 * Main App Component
 */
import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Analytics from './pages/Analytics';
import Orders from './pages/Orders';
import Products from './pages/Products';
import GlobalRefreshButton from './components/GlobalRefreshButton';
import { getAuthStatus, getSyncStatus, getAuthUrl, handleAuthCallback } from './services/api';

function MainLayout({ authStatus, syncStatus, children, onRefresh }) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                TikTok Shop Dashboard
              </h1>
              <p className="text-sm text-gray-600 mt-1">
                {authStatus.shop_name || 'LookFantastic'} • Shop ID: {authStatus.shop_id}
              </p>
            </div>
            <div className="flex items-center gap-6">
              <div className="text-sm text-gray-600">
                {syncStatus && (
                  <div>
                    <div>Orders: {syncStatus.orders.count}</div>
                    <div>Products: {syncStatus.products.count}</div>
                  </div>
                )}
              </div>
              <GlobalRefreshButton onRefreshComplete={onRefresh} />
            </div>
          </div>
          
          {/* Navigation */}
          <nav className="mt-4 flex gap-4 border-t pt-4">
            <Link
              to="/"
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === '/'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📊 Dashboard
            </Link>
            <Link
              to="/orders"
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === '/orders'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📦 Orders
            </Link>
            <Link
              to="/products"
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === '/products'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              🏷️ Products & Brands
            </Link>
            <Link
              to="/analytics"
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                location.pathname === '/analytics'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              📈 Analytics
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            TikTok Shop Dashboard v0.1.0 • LookFantastic
          </p>
        </div>
      </footer>
    </div>
  );
}

function App() {
  const [authStatus, setAuthStatus] = useState({ authenticated: false });
  const [syncStatus, setSyncStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Handle OAuth callback on mount
  useEffect(() => {
    handleOAuthCallback();
  }, []);

  const handleOAuthCallback = async () => {
    // Check if we're on the callback URL
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');
    const state = urlParams.get('state');

    if (code) {
      try {
        setLoading(true);
        // Exchange code for token
        await handleAuthCallback(code, state);
        // Clear URL parameters
        window.history.replaceState({}, document.title, window.location.pathname);
        // Load auth data
        await loadData();
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError('Authorization failed. Please try again.');
        setLoading(false);
      }
    } else {
      // No callback, just load data normally
      loadData();
    }
  };

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check auth status
      const auth = await getAuthStatus();
      setAuthStatus(auth);

      if (auth.authenticated) {
        // Load sync status
        const syncData = await getSyncStatus();
        setSyncStatus(syncData);
      }
    } catch (err) {
      console.error('Error loading data:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectTikTok = async () => {
    try {
      const { authorization_url } = await getAuthUrl();
      window.location.href = authorization_url;
    } catch (err) {
      setError('Failed to get authorization URL');
    }
  };

  // Not authenticated view
  if (!authStatus.authenticated) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md w-full text-center">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              TikTok Shop Dashboard
            </h1>
            <p className="text-gray-600">LookFantastic Performance Tracking</p>
          </div>
          
          <div className="mb-6">
            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <span className="text-4xl">🛍️</span>
            </div>
            <p className="text-gray-700 mb-4">
              Connect your TikTok Shop account to start tracking performance metrics
            </p>
          </div>

          <button
            onClick={handleConnectTikTok}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Connect TikTok Shop
          </button>

          {error && (
            <div className="mt-4 p-3 bg-red-50 text-red-800 rounded-lg text-sm">
              {error}
            </div>
          )}
        </div>
      </div>
    );
  }

  // Loading view
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  // Main app view with routing
  return (
    <Router>
      <MainLayout authStatus={authStatus} syncStatus={syncStatus} onRefresh={loadData}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/orders" element={<Orders />} />
          <Route path="/products" element={<Products />} />
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;
