import React from 'react';
import { AlertTriangle, XCircle, X, RefreshCw } from 'lucide-react';

export default function ErrorMessage({ message, onDismiss, onRetry }) {
  if (!message) return null;

  return (
    <div className="error-banner" id="error-message-banner">
      <div className="error-banner-content">
        <div className="error-icon-wrapper">
          <AlertTriangle size={20} className="error-icon" />
        </div>
        <div className="error-text-content">
          <span className="error-title">Request Error</span>
          <p className="error-desc">{message}</p>
        </div>
      </div>

      <div className="error-actions">
        {onRetry && (
          <button type="button" className="btn-error-retry" onClick={onRetry}>
            <RefreshCw size={13} />
            <span>Retry</span>
          </button>
        )}
        {onDismiss && (
          <button
            type="button"
            className="btn-error-dismiss"
            onClick={onDismiss}
            title="Dismiss error"
          >
            <X size={16} />
          </button>
        )}
      </div>
    </div>
  );
}
