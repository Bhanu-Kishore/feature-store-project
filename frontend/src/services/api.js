
import axios from 'axios';

export const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

const client = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

const proxyClient = axios.create({
  baseURL: '/api-proxy',
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

export async function checkHealth() {
  try {
    const response = await client.get('/health');
    return { ok: true, data: response.data };
  } catch {
    try {
      const response = await proxyClient.get('/health');
      return { ok: true, data: response.data };
    } catch {
      return {
        ok: false,
        error: 'Unable to connect to the FastAPI backend.',
      };
    }
  }
}

function handleApiError(err, customerId) {
  if (!err?.response) {
    throw new Error('Unable to connect to the FastAPI backend.');
  }

  const status = err.response.status;
  const detail = err.response.data?.detail;

  if (status === 404) {
    throw new Error(detail || `Customer features not found for "${customerId}".`);
  }

  if (status === 422) {
    throw new Error('Invalid customer ID format.');
  }

  if (status >= 500) {
    throw new Error(detail || 'Prediction request failed.');
  }

  throw new Error(detail || 'Prediction request failed.');
}

export async function getPrediction(customerId) {
  if (!customerId || typeof customerId !== 'string' || !customerId.trim()) {
    throw new Error('Please enter a customer ID.');
  }

  const payload = { customer_id: customerId.trim() };
  let primaryError;

  try {
    const response = await client.post('/predict', payload);
    return response.data;
  } catch (err) {
    primaryError = err;

    if (err.response && err.response.status >= 400 &&
        err.response.status < 500) {
      handleApiError(err, customerId);
    }
  }

  try {
    const response = await proxyClient.post('/predict', payload);
    return response.data;
  } catch (err) {
    handleApiError(
      err.response ? err : (primaryError || err),
      customerId
    );
  }
}
