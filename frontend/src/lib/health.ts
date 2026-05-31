/**
 * Health-check API client.
 *
 * Usage::
 *
 *     import { getHealth } from "@/lib/health";
 *     const info = await getHealth();
 */

import { get } from "./api";

/** Shape of the backend ``GET /health`` response (``data`` field after unwrap). */
export interface HealthInfo {
  app: string;
  version: string;
}

/** Fetch the application health status. */
export function getHealth(): Promise<HealthInfo> {
  return get<HealthInfo>("/health");
}
