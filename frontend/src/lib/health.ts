/**
 * Health-check API client.
 */

import { get } from "./api";

export interface Metrics {
  uptime_seconds: number;
  total_requests: number;
  active_sse_connections: number;
  status_counts: Record<string, number>;
  error_count: number;
}

export interface HealthInfo {
  app: string;
  version: string;
  metrics: Metrics;
}

/** Fetch the application health status including runtime metrics. */
export function getHealth(): Promise<HealthInfo> {
  return get<HealthInfo>("/health");
}

/** Format seconds to human-readable duration. */
export function formatUptime(seconds: number): string {
  const h = Math.floor(seconds / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  const s = Math.floor(seconds % 60);
  if (h > 0) return `${h}h ${m}m ${s}s`;
  if (m > 0) return `${m}m ${s}s`;
  return `${s}s`;
}
