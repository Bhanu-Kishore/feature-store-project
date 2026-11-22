import React from 'react';
import { Layers, Activity, Sparkles } from 'lucide-react';

export default function Header({ isOnline = true }) {
  return (
    <header className="header-container">
      <div className="header-brand">
        <div className="brand-icon-wrapper">
          <Layers className="brand-icon" size={28} />
          <div className="brand-icon-glow" />
        </div>
        <div className="header-titles">
          <div className="header-title-row">
            <h1 className="header-title">Feature Store Intelligence Dashboard</h1>
            <span className="version-pill">v1.0</span>
          </div>
          <p className="header-subtitle">
            Real-time feature retrieval and ML prediction
          </p>
        </div>
      </div>

      <div className="header-actions">
        <div className={`status-pill ${isOnline ? 'online' : 'offline'}`} id="system-status-indicator">
          <span className="pulse-dot" />
          <span className="status-label">
            {isOnline ? 'System Online' : 'System Offline'}
          </span>
        </div>
      </div>
    </header>
  );
}
