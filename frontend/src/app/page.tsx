"use client";

import { useRouter } from "next/navigation";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import Skeleton from "@/components/ui/Skeleton";
import { useRequest } from "@/hooks/useRequest";
import { getPage, type Page } from "@/lib/api";
import { getHealth, formatUptime, type HealthInfo } from "@/lib/health";

/* ── Static activity ────────────────────────────────── */

const activities = [
  { text: "客服助手 对话创建", time: "2 分钟前", color: "bg-[var(--color-primary)]" },
  { text: "admin 登录了系统", time: "15 分钟前", color: "bg-[var(--color-success)]" },
  { text: "用户 iamster 注册", time: "1 天前", color: "bg-[var(--color-accent)]" },
];

/* ── Stat card component ────────────────────────────── */

function StatCard({
  label,
  value,
  sub,
  mono = true,
}: {
  label: string;
  value: string;
  sub?: string;
  mono?: boolean;
}) {
  return (
    <Card>
      <div className="px-6 py-5 text-center">
        <p className="text-sm text-[var(--color-text-secondary)]">{label}</p>
        <p className={`text-xl font-semibold mt-2 ${mono ? "font-[var(--font-mono)]" : ""}`}>
          {value}
        </p>
        {sub && (
          <p className="text-xs text-[var(--color-text-tertiary)] mt-1">{sub}</p>
        )}
      </div>
    </Card>
  );
}

/* ── Component ──────────────────────────────────────── */

export default function DashboardPage() {
  const router = useRouter();

  const {
    data: health,
    loading: healthLoading,
    error: healthError,
  } = useRequest<HealthInfo>(() => getHealth());

  const {
    data: userData,
    loading: userLoading,
  } = useRequest<Page<unknown>>(() =>
    getPage("/auth/users", { page: "1", pageSize: "1" })
  );

  const m = health?.metrics;
  const backendOnline = !healthError && health;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">仪表盘</h1>
      <p className="text-[var(--color-text-secondary)] mb-6">
        查看平台概览、快捷操作和最近活动
      </p>

      {/* Stat cards — row 1 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        <StatCard
          label="后端状态"
          mono={false}
          value={
            healthLoading
              ? "..."
              : backendOnline
                ? `${health!.app} v${health!.version}`
                : "--"
          }
          sub={backendOnline ? "" : "未连接"}
        />
        <StatCard
          label="运行时长"
          value={m ? formatUptime(m.uptime_seconds) : healthLoading ? "..." : "--"}
        />
        <StatCard
          label="总请求数"
          value={m ? String(m.total_requests) : healthLoading ? "..." : "--"}
        />
        <StatCard
          label="错误数"
          value={
            m
              ? `${m.error_count} (${m.total_requests > 0 ? ((m.error_count / m.total_requests) * 100).toFixed(1) : 0}%)`
              : healthLoading
                ? "..."
                : "--"
          }
        />
      </div>

      {/* Stat cards — row 2 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
        <StatCard
          label="活跃 SSE"
          value={m ? String(m.active_sse_connections) : healthLoading ? "..." : "--"}
        />
        <StatCard
          label="用户总数"
          value={
            userLoading ? "..." : userData ? String(userData.total) : "--"
          }
        />
        <StatCard label="活跃对话应用" value="--" />
        <StatCard label="Agent 运行中" value="--" />
      </div>

      {/* Quick actions + Recent activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <Card>
          <Card.Header>快捷操作</Card.Header>
          <Card.Body>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary" size="sm" onClick={() => router.push("/chat")}>
                新建对话应用
              </Button>
              <Button variant="secondary" size="sm" onClick={() => router.push("/agent")}>
                创建 Agent
              </Button>
              <Button variant="secondary" size="sm" onClick={() => router.push("/knowledge")}>
                上传知识库
              </Button>
              <Button variant="secondary" size="sm" onClick={() => router.push("/workflow")}>
                新建工作流
              </Button>
              <Button variant="secondary" size="sm" onClick={() => router.push("/prompt")}>
                写 Prompt 模板
              </Button>
            </div>
          </Card.Body>
        </Card>

        <Card>
          <Card.Header>最近活动</Card.Header>
          <Card.Body className="!pt-0">
            <ul>
              {activities.map((a, i) => (
                <li
                  key={i}
                  className="flex items-center gap-3 py-2.5 border-b border-[var(--color-divider)] last:border-b-0"
                >
                  <span
                    className={`w-2.5 h-2.5 rounded-full border-2 border-[var(--color-text)] flex-shrink-0 ${a.color}`}
                  />
                  <span className="flex-1 text-[14px]">{a.text}</span>
                  <span className="text-xs text-[var(--color-text-tertiary)] flex-shrink-0">
                    {a.time}
                  </span>
                </li>
              ))}
            </ul>
          </Card.Body>
        </Card>
      </div>

      {/* TODO: replace static activities with real activity feed API */}
    </div>
  );
}
