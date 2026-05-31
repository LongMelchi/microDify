"use client";

import { useCallback, useRef, useState } from "react";

/**
 * Generic SSE hook for streaming chat responses.
 * TODO: implement EventSource or fetch-based SSE reading with reconnect logic.
 */
export function useSSE() {
  const [isConnected, setIsConnected] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const connect = useCallback(
    async (_url: string, _onMessage: (data: string) => void) => {
      // TODO: open SSE connection, parse event stream, call onMessage for each chunk
    },
    []
  );

  const disconnect = useCallback(() => {
    abortRef.current?.abort();
    setIsConnected(false);
  }, []);

  return { isConnected, connect, disconnect };
}
