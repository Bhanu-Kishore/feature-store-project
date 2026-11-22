
import React from 'react';
import {
  Hash,
  DollarSign,
  CalendarDays,
  UserRound,
  Layers,
} from 'lucide-react';

export function formatFeatureValue(value, key) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return '—';
  }

  const num = Number(value);

  switch (key) {
    case 'tenure':
      return `${num} months`;

    case 'monthly_charges':
    case 'total_charges':
      return `$${num.toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      })}`;

    case 'senior_citizen':
      return num === 1 ? 'Yes' : 'No';

    default:
      return Number.isInteger(num) ? String(num) : num.toFixed(2);
  }
}

export function FeatureCard({
  title,
  timeframe,
  value,
  rawKey,
  icon: Icon,
  accentColor = 'cyan',
}) {
  const formattedValue = formatFeatureValue(value, rawKey);

  return (
    <div className={`feature-card accent-${accentColor}`} id={`feature-card-${rawKey}`}>
      <div className="feature-card-top">
        <div className="feature-card-icon-wrapper">
          <Icon size={18} className="feature-card-icon" />
        </div>
        <span className="feature-key-tag">{rawKey}</span>
      </div>

      <div className="feature-card-content">
        <h3 className="feature-title">{title}</h3>
        {timeframe && <span className="feature-timeframe">{timeframe}</span>}
      </div>

      <div className="feature-card-bottom">
        <div className="feature-value-wrapper">
          <span className="feature-value">{formattedValue}</span>
          {value !== null && value !== undefined && Number.isFinite(Number(value)) && (
            <span className="feature-raw-sub">Raw: {value}</span>
          )}
        </div>
      </div>
    </div>
  );
}

export default function FeaturesSection({ features, isLoading }) {
  const featureCards = [
    {
      rawKey: 'tenure',
      title: 'Customer Tenure',
      timeframe: 'Months with service',
      icon: CalendarDays,
      accentColor: 'blue',
    },
    {
      rawKey: 'monthly_charges',
      title: 'Monthly Charges',
      timeframe: 'Monthly billing',
      icon: DollarSign,
      accentColor: 'cyan',
    },
    {
      rawKey: 'total_charges',
      title: 'Total Charges',
      timeframe: 'Accumulated billing',
      icon: Hash,
      accentColor: 'emerald',
    },
    {
      rawKey: 'senior_citizen',
      title: 'Senior Citizen',
      timeframe: 'Customer attribute',
      icon: UserRound,
      accentColor: 'purple',
    },
  ];

  return (
    <section className="features-section" id="features-section">
      <div className="section-header">
        <div className="section-title-group">
          <div className="section-title-row">
            <Layers size={20} className="section-icon" />
            <h2 className="section-title">Feast Customer Features</h2>
          </div>
          <p className="section-subtitle">
            Customer attributes retrieved from the Feast online store
          </p>
        </div>
        <span className="features-badge">4 Features</span>
      </div>

      {isLoading ? (
        <div className="features-grid">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="feature-card skeleton-card">
              <div className="skeleton-header" />
              <div className="skeleton-title" />
              <div className="skeleton-value" />
            </div>
          ))}
        </div>
      ) : features ? (
        <div className="features-grid">
          {featureCards.map((item) => (
            <FeatureCard
              key={item.rawKey}
              {...item}
              value={features[item.rawKey]}
            />
          ))}
        </div>
      ) : null}
    </section>
  );
}
