"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import { post, BizError } from "@/lib/api";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!email.trim()) {
      showToast("warning", "请输入邮箱地址");
      return;
    }

    setLoading(true);
    try {
      await post("/auth/forgot-password", { email: email.trim() });
      setSent(true);
    } catch (err) {
      const message =
        err instanceof BizError ? err.message : "发送失败，请稍后重试";
      showToast("error", message);
    } finally {
      setLoading(false);
    }
  }

  /* ── Success state ──────────────────────────────── */

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)]">
        <Card className="w-full max-w-[420px] !shadow-[6px_6px_0_rgba(26,26,46,0.08)]">
          <Card.Body className="!p-10">
            <div className="text-center mb-8">
              <div className="w-12 h-12 mx-auto mb-4 rounded-full bg-[var(--color-secondary)] border-[3px] border-[var(--color-text)] flex items-center justify-center text-white text-xl font-bold">
                ✓
              </div>
              <h1 className="text-2xl font-bold mb-2">邮件已发送</h1>
              <p className="text-[14px] text-[var(--color-text-secondary)]">
                我们已向{" "}
                <span className="font-semibold text-[var(--color-text)]">{email}</span>{" "}
                发送了密码重置链接，请检查收件箱
              </p>
            </div>

            <Button
              variant="secondary"
              className="w-full"
              onClick={() => router.push("/login")}
            >
              返回登录
            </Button>
          </Card.Body>
        </Card>
      </div>
    );
  }

  /* ── Form state ─────────────────────────────────── */

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)]">
      <Card className="w-full max-w-[420px] !shadow-[6px_6px_0_rgba(26,26,46,0.08)]">
        <Card.Body className="!p-10">
          {/* Brand */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 mx-auto mb-4 rounded-[var(--radius-sm)] bg-[var(--color-primary)] border-[3px] border-[var(--color-text)] flex items-center justify-center text-white text-xl font-bold">
              m
            </div>
            <h1 className="text-2xl font-bold mb-2">重置密码</h1>
            <p className="text-[14px] text-[var(--color-text-secondary)]">
              输入注册邮箱，我们将发送密码重置链接
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <Input
              label="邮箱地址"
              required
              type="text"
              placeholder="admin@microdify.local"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />

            <Button variant="primary" loading={loading} className="w-full" type="submit">
              发送重置链接
            </Button>
          </form>

          <div className="flex items-center gap-3 my-5">
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
          </div>

          <p className="text-center text-[13px] text-[var(--color-text-secondary)]">
            <Link href="/login" className="font-semibold text-[var(--color-primary)] no-underline">
              返回登录
            </Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
