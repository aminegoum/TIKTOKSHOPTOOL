/**
 * Global Refresh Button Component
 * Triggers a full data sync from TikTok Shop API
 */
import React, { useState } from 'react';
import { triggerGlobalRefresh, getSyncStatus } from '../services/api';

function GlobalRefreshButton({ onRefreshComplete }) {
  const [syncing, setSyncing] = useState(false);
  const [progress, setProgress] = useState(null);
  const [error, setError] = useState(null);

  const handleRefresh = async () => {
    try {
      setSyncing(true);
      setError(null);
      setProgress('Starting sync...');

      // Trigger global refresh
      await triggerGlobalRefresh(30);
      
      // Poll for status
      const pollInterval = setInterval(async () => {
        try {
          const status = await getSyncStatus();
          
          if (status.is_syncing) {
            setProgress(`Syncing... ${status.orders_synced || 0} orders processed`);
          } else {
            clearInterval(pollInterval);
            setProgress('Sync complete!');
            setSyncing(false);
            
            // Notify parent to refresh data
            if (onRefreshComplete) {
              setTimeout(() => {
                onRefreshComplete();
                setProgress(null);
              }, 1000);
            }
          }
        } catch (err) {
          console.error('Error checking sync status:', err);
        }
      }, 2000);

      // Stop polling after 5 minutes
      setTimeout(() => {
        clearInterval(pollInterval);
        if (syncing) {
          setSyncing(false);
          setProgress(null);
        }
      }, 300000);

    } catch (err) {
      console.error('Error triggering refresh:', err);
      setError(err.message || 'Failed to start sync');
      setSyncing(false);
      setProgress(null);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={handleRefresh}
        disabled={syncing}
        className={`
          flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all
          ${syncing 
            ? 'bg-gray-300 text-gray-600 cursor-not-allowed' 
            : 'bg-blue-600 text-white hover:bg-blue-700 active:scale-95'
          }
        `}
      >
        <svg 
          className={`w-5 h-5 ${syncing ? 'animate-spin' : ''}`} 
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" 
          />
        </svg>
        {syncing ? 'Syncing...' : 'Refresh All Data'}
      </button>

      {progress && (
        <span className="text-sm text-gray-600 animate-pulse">
          {progress}
        </span>
      )}

      {error && (
        <span className="text-sm text-red-600">
          ❌ {error}
        </span>
      )}
    </div>
  );
}

export default GlobalRefreshButton;
