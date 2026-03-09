/**
 * Typed fetch wrappers for Pulse backend.
 * Base URL from VITE_API_URL (default: http://localhost:8000).
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

export interface Service {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface Metric {
  id: string;
  service_id: string;
  name: string;
  value: number;
  timestamp: string;
}

export interface Alert {
  id: string;
  rule_id: string;
  service_id: string;
  metric_value: number;
  triggered_at: string;
  resolved_at: string | null;
  state: string;
}

async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`);
  if (!res.ok) {
    throw new Error(`API ${res.status}: ${res.statusText}`);
  }
  return res.json();
}

export async function getServices(): Promise<Service[]> {
  return fetchJson<Service[]>('/services');
}

export async function getService(id: string): Promise<Service> {
  return fetchJson<Service>(`/services/${id}`);
}

export async function getMetrics(
  serviceId: string,
  params?: { metric_name?: string; start?: string; end?: string; limit?: number }
): Promise<Metric[]> {
  const search = new URLSearchParams();
  if (params?.metric_name) search.set('metric_name', params.metric_name);
  if (params?.start) search.set('start', params.start);
  if (params?.end) search.set('end', params.end);
  if (params?.limit != null) search.set('limit', String(params.limit));
  const q = search.toString();
  return fetchJson<Metric[]>(`/services/${serviceId}/metrics${q ? `?${q}` : ''}`);
}

export async function getAlerts(
  serviceId: string,
  params?: { state?: string }
): Promise<Alert[]> {
  const search = new URLSearchParams();
  if (params?.state) search.set('state', params.state);
  const q = search.toString();
  return fetchJson<Alert[]>(`/services/${serviceId}/alerts${q ? `?${q}` : ''}`);
}
