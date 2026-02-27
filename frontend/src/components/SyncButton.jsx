/**
 * Manual Sync Button Component
 */
import React, { useState } from 'react';
import { triggerSync } from '../services/api';

const SyncButton = ({ onSyncComplete }) => {
  const [syncing, setSyncing] = useState(false);
  const [message, setMessage] = useState('');

  const handleSync = async (syncType) => {
    setSyncing(true);
    setMessage('');
    
    try {
      const result = await triggerSync(syncType, 30);
      setMessage(`✅ ${result.message}`);
      
      // Call callback if provided
      if (onSyncComplete) {
        onSyncComplete();
      }
      
      // Clear message after 5 seconds
      setTimeout(() => setMessage(''), 5000);
    } catch (error) {
      setMessage(`❌ Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setSyncing(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Manual Data Sync
      </h3>
      
      <div className="flex gap-3">
        <button
          onClick={() => handleSync('orders')}
          disabled={syncing}
          className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {syncing ? '⏳ Syncing...' : '🔄 Sync Orders'}
        </button>
        
        <button
          onClick={() => handleSync('products')}
          disabled={syncing}
          className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          {syncing ? '⏳ Syncing...' : '🔄 Sync Products'}
        </button>
      </div>
      
      {message && (
        <div className={`mt-4 p-3 rounded-lg ${
          message.startsWith('✅') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
        }`}>
          {message}
        </div>
      )}
      
      <p className="mt-3 text-sm text-gray-500">
        Syncs last 30 days of data from TikTok Shop
      </p>
    </div>
  );
};

export default SyncButton;
