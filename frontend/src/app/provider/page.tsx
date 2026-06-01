"use client";

import { useEffect, useState } from "react";
import { getHealth, formatUptime, type HealthInfo } from "@/lib/health";

const REFRESH_MS = 30_000;

export default function ProviderPage() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [info, setInfo] = useState<HealthInfo | null>(null);

  useEffect(() => {
    const fetch = () =>
      getHealth()
        .then((data) => {
          setInfo(data);
          setStatus("ok");
        })
        .catch(() => {
          setStatus("error");
        });
    fetch();
    const timer = setInterval(fetch, REFRESH_MS);
    return () => clearInterval(timer);
  }, []);

  const m = info?.metrics;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">模型提供商管理</h1>

      {/* Health + Metrics cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Status */}
        <div className="rounded-lg border p-4">
          <p className="text-sm text-gray-500">后端状态</p>
          {status === "loading" && <p className="text-gray-400">检测中...</p>}
          {status === "ok" && (
            <p className="text-green-600 font-medium text-lg">
              {info?.app} v{info?.version}
            </p>
          )}
          {status === "error" && (
            <p className="text-red-500 font-medium text-lg">未连接</p>
          )}
        </div>

        {/* Uptime */}
        <div className="rounded-lg border p-4">
          <p className="text-sm text-gray-500">运行时长</p>
          <p className="text-xl font-medium">
            {m ? formatUptime(m.uptime_seconds) : "—"}
          </p>
        </div>

        {/* Total requests */}
        <div className="rounded-lg border p-4">
          <p className="text-sm text-gray-500">总请求数</p>
          <p className="text-xl font-medium">{m?.total_requests ?? "—"}</p>
        </div>

        {/* Error rate */}
        <div className="rounded-lg border p-4">
          <p className="text-sm text-gray-500">错误数</p>
          <p className="text-xl font-medium">
            {m != null
              ? `${m.error_count} (${m.total_requests > 0 ? ((m.error_count / m.total_requests) * 100).toFixed(1) : 0}%)`
              : "—"}
          </p>
        </div>
      </div>

      {/* Active SSE */}
      {m != null && (
        <div className="text-sm text-gray-400">
          {m.active_sse_connections > 0
            ? `活跃 SSE 连接: ${m.active_sse_connections}`
            : "无活跃 SSE 连接"}
        </div>
      )}
    </div>
  );
}
