import React from 'react';
import { Server, Database, Cpu, RefreshCw } from 'lucide-react';

export default function SystemStatus({
  fastApiStatus = 'checking', // 'connected' | 'offline' | 'checking'
  onRefresh,
  isRefreshing = false,
}) {
  const isFastApiOk = fastApiStatus === 'connected';
  const isFastApiChecking = fastApiStatus === 'checking';

  return (
    <div className="system-status-container" id="system-status-section">
      <div className="system-status-header">
        <span className="system-status-title">System Infrastructure Status</span>
        {onRefresh && (
          <button
            type="button"
            className="status-refresh-btn"
            onClick={onRefresh}
            disabled={isRefreshing}
            title="Refresh FastAPI health check"
            id="btn-refresh-health"
          >
            <RefreshCw size={13} className={isRefreshing ? 'spin-icon' : ''} />
            <span>Check Health</span>
          </button>
        )}
      </div>

      <div className="status-grid">
        {/* FastAPI Status - Live Health Endpoint */}
        <div className={`status-item ${isFastApiOk ? 'status-ok' : isFastApiChecking ? 'status-checking' : 'status-error'}`}>
          <div className="status-item-left">
            <Server size={18} className="status-item-icon" />
            <div className="status-item-info">
              <span className="status-item-name">FastAPI</span>
              <span className="status-item-desc">API Gateway & Inference Service</span>
            </div>
          </div>
          <div className="status-badge">
            <span className="status-indicator-dot" />
            <span className="status-badge-text">
              {isFastApiChecking
                ? 'Connecting...'
                : isFastApiOk
                ? 'Connected'
                : 'Offline'}
            </span>
          </div>
        </div>

        {/* Feast Online Store Status */}
        <div className="status-item status-ok">
          <div className="status-item-left">
            <Database size={18} className="status-item-icon" />
            <div className="status-item-info">
              <span className="status-item-name">Feast Online Store</span>
              <span className="status-item-desc">Low-latency Entity Feature Registry</span>
            </div>
          </div>
          <div className="status-badge">
            <span className="status-indicator-dot" />
            <span className="status-badge-text">Connected</span>
          </div>
        </div>

        {/* MLflow Model Status */}
        <div className="status-item status-ok">
          <div className="status-item-left">
            <Cpu size={18} className="status-item-icon" />
            <div className="status-item-info">
              <span className="status-item-name">MLflow Model</span>
              <span className="status-item-desc">Scikit-Learn Production Artifact</span>
            </div>
          </div>
          <div className="status-badge">
            <span className="status-indicator-dot" />
            <span className="status-badge-text">Loaded</span>
          </div>
        </div>
      </div>
    </div>
  );
}
