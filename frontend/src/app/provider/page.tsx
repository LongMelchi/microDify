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
      <h1 className="text-2xl font-bold mb-2">模型管理</h1>
      <p className="text-[var(--color-text-secondary)] mb-6">查看 LLM 提供商连接状态和运行指标</p>

      {/* Metric cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-4">
          <p className="text-sm text-[var(--color-text-secondary)]">后端状态</p>
          {status === "loading" && <p className="text-[var(--color-text-tertiary)]">检测中...</p>}
          {status === "ok" && (
            <p className="text-[var(--color-success)] font-semibold text-lg">
              {info?.app} v{info?.version}
            </p>
          )}
          {status === "error" && (
            <p className="text-[var(--color-error)] font-semibold text-lg">未连接</p>
          )}
        </div>

        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-4">
          <p className="text-sm text-[var(--color-text-secondary)]">运行时长</p>
          <p className="text-xl font-semibold font-[var(--font-mono)]">
            {m ? formatUptime(m.uptime_seconds) : "—"}
          </p>
        </div>

        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-4">
          <p className="text-sm text-[var(--color-text-secondary)]">总请求数</p>
          <p className="text-xl font-semibold font-[var(--font-mono)]">{m?.total_requests ?? "—"}</p>
        </div>

        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-4">
          <p className="text-sm text-[var(--color-text-secondary)]">错误数</p>
          <p className="text-xl font-semibold font-[var(--font-mono)]">
            {m != null
              ? `${m.error_count} (${m.total_requests > 0 ? ((m.error_count / m.total_requests) * 100).toFixed(1) : 0}%)`
              : "—"}
          </p>
        </div>
      </div>

      {/* Active SSE */}
      {m != null && (
        <p className="text-sm text-[var(--color-text-secondary)]">
          {m.active_sse_connections > 0
            ? `活跃 SSE 连接: ${m.active_sse_connections}`
            : "无活跃 SSE 连接"}
        </p>
      )}
    </div>
  );
}
