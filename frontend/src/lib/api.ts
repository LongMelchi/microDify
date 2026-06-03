/**
 * HTTP client wrapper — mirrors microDify's unified ``Result<T>`` response format.
 *
 * Usage::
 *
 *     import { get, post } from "@/lib/api";
 *     const user = await get<User>("/auth/me");
 *     const kb   = await post<KnowledgeBase>("/knowledge/", { name: "..." });
 */

import { getToken } from "./auth";

// ── Types ──────────────────────────────────────────────────────────────────────

/** Mirrors ``app/core/schemas.Result[T]`` from the backend. */
export interface ApiResponse<T = unknown> {
  code: number;
  message: string;
  data: T | null;
  // Present only for ``PageResult`` responses.
  total?: number;
  page?: number;
  size?: number;
}

/** Normalised paginated payload returned by {@link getPage}. */
export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
}

/** Error thrown when the backend returns ``code !== 200`` or the network is down. */
export class BizError extends Error {
  code: number;

  constructor(code: number, message: string) {
    super(message);
    this.code = code;
    this.name = "BizError";
  }
}

// ── Error event bus ────────────────────────────────────────────────────────────

type ErrorHandler = (code: number, message: string) => void;

const listeners: ErrorHandler[] = [];

/**
 * Subscribe to HTTP errors.
 *
 * Page-level components can call ``onHttpError((code, msg) => { ... })`` to
 * show toast messages or redirect to login on 401.
 */
export function onHttpError(handler: ErrorHandler): () => void {
  listeners.push(handler);
  return () => {
    const idx = listeners.indexOf(handler);
    if (idx !== -1) listeners.splice(idx, 1);
  };
}

function emitError(code: number, message: string): void {
  for (const fn of listeners) {
    try {
      fn(code, message);
    } catch {
      // Swallow — don't let a broken error handler break the app.
    }
  }
}

// ── Core request ───────────────────────────────────────────────────────────────

const BASE_URL = "/api";
const DEFAULT_TIMEOUT_MS = 30_000;

async function request<T>(
  method: string,
  url: string,
  data?: unknown,
  params?: Record<string, string>,
): Promise<ApiResponse<T>> {
  // Build full URL with query params
  const fullUrl = new URL(`${BASE_URL}${url}`, window.location.origin);
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      fullUrl.searchParams.set(k, v);
    }
  }

  // Headers
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
  };
  const token = getToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  // Timeout via AbortController
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), DEFAULT_TIMEOUT_MS);

  try {
    const res = await fetch(fullUrl.toString(), {
      method,
      headers,
      body: data !== undefined ? JSON.stringify(data) : undefined,
      signal: controller.signal,
    });

    const json: ApiResponse<T> = await res.json();

    if (json.code === 200) {
      return json;
    }

    emitError(json.code, json.message);
    throw new BizError(json.code, json.message);
  } catch (err) {
    // Rethrow our own BizError — it's already been emitted.
    if (err instanceof BizError) throw err;

    // Abort (timeout)
    if (err instanceof DOMException && err.name === "AbortError") {
      emitError(0, "请求超时，请稍后重试");
      throw new BizError(0, "请求超时，请稍后重试");
    }

    // Network down
    if (err instanceof TypeError && err.message === "Failed to fetch") {
      emitError(0, "网络不可用，请检查网络连接");
      throw new BizError(0, "网络不可用，请检查网络连接");
    }

    emitError(0, "未知错误");
    throw new BizError(0, err instanceof Error ? err.message : "未知错误");
  } finally {
    clearTimeout(timer);
  }
}

// ── Convenience methods ────────────────────────────────────────────────────────

export async function get<T>(url: string, params?: Record<string, string>): Promise<T> {
  return (await request<T>("GET", url, undefined, params)).data as T;
}

export async function post<T>(url: string, data?: unknown): Promise<T> {
  return (await request<T>("POST", url, data)).data as T;
}

export async function put<T>(url: string, data?: unknown): Promise<T> {
  return (await request<T>("PUT", url, data)).data as T;
}

export async function del<T>(url: string): Promise<T> {
  return (await request<T>("DELETE", url)).data as T;
}

/**
 * Fetch a paginated (``PageResult``) endpoint, normalising the envelope's
 * ``data`` / ``total`` / ``page`` / ``size`` into a {@link Page}.
 */
export async function getPage<T>(
  url: string,
  params?: Record<string, string>,
): Promise<Page<T>> {
  const res = await request<T[]>("GET", url, undefined, params);
  return {
    items: (res.data as T[]) ?? [],
    total: res.total ?? 0,
    page: res.page ?? 1,
    size: res.size ?? 20,
  };
}
