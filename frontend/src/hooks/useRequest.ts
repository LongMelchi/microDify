"use client";

import { useState, useCallback, useRef, useEffect } from "react";

/* ── Types ──────────────────────────────────────────── */

interface UseRequestOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (err: Error) => void;
}

interface UseRequestReturn<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  execute: () => Promise<void>;
}

/* ── Hook ───────────────────────────────────────────── */

export function useRequest<T>(
  requestFn: () => Promise<T>,
  options: UseRequestOptions<T> = {}
): UseRequestReturn<T> {
  const { immediate = true, onSuccess, onError } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(immediate);
  const [error, setError] = useState<string | null>(null);

  const mountedRef = useRef(true);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await requestFn();
      if (mountedRef.current) {
        setData(result);
        onSuccess?.(result);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "请求失败";
      if (mountedRef.current) {
        setError(message);
        onError?.(err instanceof Error ? err : new Error(message));
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, [requestFn, onSuccess, onError]);

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) {
      execute();
    }
    return () => {
      mountedRef.current = false;
    };
  }, [execute, immediate]);

  return { data, loading, error, execute };
}
