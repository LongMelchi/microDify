"use client";

import { useEffect, useState } from "react";
import { getHealth, type HealthInfo } from "@/lib/health";

export default function ProviderPage() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");
  const [info, setInfo] = useState<HealthInfo | null>(null);

  useEffect(() => {
    getHealth()
      .then((data) => {
        setInfo(data);
        setStatus("ok");
      })
      .catch(() => {
        setInfo(null);
        setStatus("error");
      });
  }, []);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">模型提供商管理</h1>

      {/* Health check card */}
      <div className="rounded-lg border p-4 max-w-md">
        {status === "loading" && (
          <p className="text-gray-500">检测后端连接中...</p>
        )}
        {status === "ok" && (
          <p className="text-green-600 font-medium">
            后端已连接：{info?.app} v{info?.version} is running
          </p>
        )}
        {status === "error" && (
          <p className="text-red-500 font-medium">后端未连接</p>
        )}
      </div>
    </div>
  );
}
