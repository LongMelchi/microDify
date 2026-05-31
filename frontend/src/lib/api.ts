/**
 * Fetch wrapper for API calls.
 * TODO: add base URL, auth header injection, error handling, and token refresh.
 */

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const url = `${BASE_URL}${path}`;

  const res = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      // TODO: inject Authorization header from auth token
      ...options?.headers,
    },
    ...options,
  });

  if (!res.ok) {
    // TODO: structured error handling
    throw new Error(`API error: ${res.status} ${res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export async function apiFetchStream(
  path: string,
  options?: RequestInit
): Promise<Response> {
  const url = `${BASE_URL}${path}`;

  return fetch(url, {
    headers: {
      "Content-Type": "application/json",
      // TODO: inject Authorization header from auth token
      ...options?.headers,
    },
    ...options,
  });
}
