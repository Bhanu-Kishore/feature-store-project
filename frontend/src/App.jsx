
import React, { useState, useEffect, useCallback } from 'react';
import Header from './components/Header';
import SystemStatus from './components/SystemStatus';
import PredictionForm from './components/PredictionForm';
import PredictionResult from './components/PredictionResult';
import FeaturesSection from './components/FeatureCard';
import ErrorMessage from './components/ErrorMessage';
import ArchitectureBar from './components/ArchitectureBar';
import { checkHealth, getPrediction, API_BASE_URL } from './services/api';

export default function App() {
  const [fastApiStatus, setFastApiStatus] = useState('checking');
  const [isRefreshingHealth, setIsRefreshingHealth] = useState(false);
  const [isLoadingPrediction, setIsLoadingPrediction] = useState(false);
  const [activeUserId, setActiveUserId] = useState('7590-VHVEG');
  const [predictionData, setPredictionData] = useState(null);
  const [predictionTimestamp, setPredictionTimestamp] = useState(null);
  const [responseTime, setResponseTime] = useState(null);
  const [error, setError] = useState(null);

  const verifyBackendHealth = useCallback(async () => {
    setIsRefreshingHealth(true);
    try {
      const res = await checkHealth();
      setFastApiStatus(res.ok ? 'connected' : 'offline');
    } catch {
      setFastApiStatus('offline');
    } finally {
      setIsRefreshingHealth(false);
    }
  }, []);

  useEffect(() => {
    verifyBackendHealth();
  }, [verifyBackendHealth]);

  const handleGetPrediction = async (customerIdToQuery) => {
    const targetId =
      typeof customerIdToQuery === 'string'
        ? customerIdToQuery.trim()
        : activeUserId.trim();

    if (!targetId) {
      setError('Please enter a customer ID.');
      return;
    }

    setError(null);
    setIsLoadingPrediction(true);
    setActiveUserId(targetId);

    const startTime = performance.now();

    try {
      const data = await getPrediction(targetId);
      const endTime = performance.now();

      setPredictionData(data);
      setResponseTime(Math.round(endTime - startTime));
      setPredictionTimestamp(new Date().toLocaleTimeString());
      setFastApiStatus('connected');
    } catch (err) {
      setError(err.message || 'Prediction request failed.');
      if (err.message?.includes('Unable to connect')) {
        setFastApiStatus('offline');
      }
    } finally {
      setIsLoadingPrediction(false);
    }
  };

  return (
    <div className="app-layout">
      <div className="ambient-background" />

      <div className="app-container">
        <Header isOnline={fastApiStatus === 'connected'} />

        <SystemStatus
          fastApiStatus={fastApiStatus}
          onRefresh={verifyBackendHealth}
          isRefreshing={isRefreshingHealth}
        />

        {error && (
          <ErrorMessage
            message={error}
            onDismiss={() => setError(null)}
            onRetry={() => handleGetPrediction(activeUserId)}
          />
        )}

        <main className="dashboard-grid">
          <div className="grid-column">
            <PredictionForm
              onSubmit={handleGetPrediction}
              isLoading={isLoadingPrediction}
              activeUserId={activeUserId}
            />
          </div>

          <div className="grid-column">
            <PredictionResult
              result={predictionData}
              isLoading={isLoadingPrediction}
              timestamp={predictionTimestamp}
              responseTime={responseTime}
            />
          </div>
        </main>

        <FeaturesSection
          features={predictionData?.features}
          isLoading={isLoadingPrediction}
        />

        <ArchitectureBar />

        <footer className="dashboard-footer">
          <div className="footer-left">
            <span>Customer Churn Feature Store Dashboard</span>
            <span className="footer-dot">•</span>
            <span>Target API: <code>{API_BASE_URL}</code></span>
          </div>
          <div className="footer-right">
            <span>FastAPI + Feast Online Store + MLflow</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
