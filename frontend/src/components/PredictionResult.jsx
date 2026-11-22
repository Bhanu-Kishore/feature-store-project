
import React from 'react';
import { Cpu, CheckCircle2, Clock, Zap, Target } from 'lucide-react';

export default function PredictionResult({
  result,
  isLoading,
  timestamp,
  responseTime,
}) {
  if (isLoading) {
    return (
      <div className="card prediction-result-card loading-card" id="prediction-result-section">
        <div className="card-header">
          <div className="card-header-icon pulse-icon">
            <Cpu size={20} />
          </div>
          <div>
            <h2 className="card-title">Churn Prediction</h2>
            <p className="card-description">Running inference...</p>
          </div>
        </div>
        <div className="prediction-placeholder loading-placeholder">
          <div className="shimmer-box" />
          <p className="loading-text">
            Retrieving customer features from Feast and scoring with MLflow...
          </p>
        </div>
      </div>
    );
  }

  if (!result) {
    return (
      <div className="card prediction-result-card empty-card" id="prediction-result-section">
        <div className="card-header">
          <div className="card-header-icon">
            <Cpu size={20} />
          </div>
          <div>
            <h2 className="card-title">Churn Prediction</h2>
            <p className="card-description">Awaiting customer selection</p>
          </div>
        </div>
        <div className="prediction-placeholder">
          <Target size={40} className="placeholder-icon" />
          <p className="placeholder-title">No Prediction Generated Yet</p>
          <p className="placeholder-sub">
            Enter a customer ID or select a sample customer to predict churn.
          </p>
        </div>
      </div>
    );
  }

  const { customer_id, prediction, prediction_label } = result;
  const isChurn = prediction === 1;

  return (
    <div className="card prediction-result-card" id="prediction-result-section">
      <div className="card-header">
        <div className="card-header-icon active">
          <Cpu size={20} />
        </div>
        <div className="card-header-main">
          <div className="card-title-row">
            <h2 className="card-title">Churn Prediction</h2>
            <span className="user-badge" id="result-customer-badge">
              Customer: {customer_id}
            </span>
          </div>
          <p className="card-description">
            Prediction based on customer features retrieved from Feast
          </p>
        </div>
      </div>

      <div className="prediction-body">
        <div className="prediction-output-container">
          <div className="output-label-row">
            <span className="output-label">Predicted Outcome</span>
            <span className="confidence-pill">
              <Zap size={12} />
              <span>Model output</span>
            </span>
          </div>

          <div className="prediction-value-box" id="model-output-value">
            <span className="prediction-number">{prediction}</span>
          </div>

          <h3>{prediction_label}</h3>

          <p className="card-description">
            {isChurn
              ? 'The model predicts this customer may leave the service.'
              : 'The model predicts this customer may stay with the service.'}
          </p>

          <div className="prediction-meta-grid">
            <div className="meta-item">
              <span className="meta-label">Target</span>
              <span className="meta-value">Churn (0 or 1)</span>
            </div>

            {responseTime != null && (
              <div className="meta-item">
                <span className="meta-label">Latency</span>
                <span className="meta-value">{responseTime} ms</span>
              </div>
            )}

            {timestamp && (
              <div className="meta-item">
                <span className="meta-label">Evaluated At</span>
                <span className="meta-value">{timestamp}</span>
              </div>
            )}
          </div>
        </div>

        <div className="prediction-footer">
          <div className="mlflow-badge">
            <CheckCircle2 size={16} className="mlflow-check-icon" />
            <span>Powered by MLflow Model</span>
          </div>
        </div>
      </div>
    </div>
  );
}
