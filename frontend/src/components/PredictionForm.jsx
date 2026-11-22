
import React, { useState } from 'react';
import { UserCheck, Search, Loader2, ArrowRight } from 'lucide-react';

const EXAMPLE_CUSTOMERS = [
  '7590-VHVEG',
  '5575-GNVDE',
  '3668-QPYBK',
  '7795-CFOCW',
  '9237-HQITU',
];

export default function PredictionForm({
  onSubmit,
  isLoading,
  activeUserId,
}) {
  const [customerId, setCustomerId] = useState(
    activeUserId || '7590-VHVEG'
  );

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(customerId.trim());
  };

  const handleSelectExample = (id) => {
    setCustomerId(id);
    onSubmit(id);
  };

  return (
    <div className="card prediction-form-card" id="customer-prediction-section">
      <div className="card-header">
        <div className="card-header-icon">
          <UserCheck size={20} />
        </div>
        <div>
          <h2 className="card-title">Customer Churn Prediction</h2>
          <p className="card-description">
            Retrieve customer features from Feast and predict churn.
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="prediction-form">
        <div className="form-group">
          <label htmlFor="customer-id-input" className="form-label">
            Enter Customer ID
          </label>

          <div className="input-wrapper">
            <Search className="input-icon" size={18} />
            <input
              id="customer-id-input"
              type="text"
              className="form-input"
              placeholder="e.g. 7590-VHVEG"
              value={customerId}
              onChange={(e) => setCustomerId(e.target.value)}
              disabled={isLoading}
              autoComplete="off"
              spellCheck="false"
            />

            {customerId && !isLoading && (
              <button
                type="button"
                className="input-clear-btn"
                onClick={() => setCustomerId('')}
                title="Clear input"
              >
                ×
              </button>
            )}
          </div>
        </div>

        <div className="quick-select-section">
          <span className="quick-select-label">Sample customers:</span>
          <div className="quick-select-chips">
            {EXAMPLE_CUSTOMERS.map((id) => (
              <button
                key={id}
                type="button"
                className={`chip ${customerId === id ? 'chip-active' : ''}`}
                onClick={() => handleSelectExample(id)}
                disabled={isLoading}
              >
                {id}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          className="btn btn-primary submit-btn"
          disabled={isLoading || !customerId.trim()}
          id="btn-get-prediction"
        >
          {isLoading ? (
            <>
              <Loader2 size={18} className="spin-icon" />
              <span>Retrieving features...</span>
            </>
          ) : (
            <>
              <span>Predict Churn</span>
              <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>
    </div>
  );
}
