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
  const fnRef = useRef(requestFn);
  const onSuccessRef = useRef(onSuccess);
  const onErrorRef = useRef(onError);

  // Always keep refs current without triggering re-execution
  fnRef.current = requestFn;
  onSuccessRef.current = onSuccess;
  onErrorRef.current = onError;

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fnRef.current();
      if (mountedRef.current) {
        setData(result);
        onSuccessRef.current?.(result);
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "请求失败";
      if (mountedRef.current) {
        setError(message);
        onErrorRef.current?.(err instanceof Error ? err : new Error(message));
      }
    } finally {
      if (mountedRef.current) {
        setLoading(false);
      }
    }
  }, []);  // Stable reference — never changes

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) {
      execute();
    }
    return () => {
      mountedRef.current = false;
    };
  }, [execute, immediate]);  // execute is now stable, only immediate matters

  return { data, loading, error, execute };
}
