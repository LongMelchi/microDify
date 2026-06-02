"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import { post, BizError } from "@/lib/api";

/* ── Validator ──────────────────────────────────────── */

function validateEmail(v: string): string | undefined {
  if (!v.trim()) return "请输入邮箱地址";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())) return "请输入有效的邮箱地址";
  return undefined;
}

/* ── Component ──────────────────────────────────────── */

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [emailError, setEmailError] = useState<string | undefined>(undefined);
  const router = useRouter();

  /* ── Blur validation ─────────────────────────────── */

  function handleBlur() {
    const err = validateEmail(email);
    if (emailError !== err) setEmailError(err);
  }

  function clearError() {
    if (emailError) setEmailError(undefined);
  }

  /* ── Submit ──────────────────────────────────────── */

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    const err = validateEmail(email);
    if (err) {
      setEmailError(err);
      document.getElementById("邮箱地址")?.focus();
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

  /* ── Success state ────────────────────────────────── */

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

  /* ── Form state ───────────────────────────────────── */

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
          <form onSubmit={handleSubmit} noValidate>
            <Input
              label="邮箱地址"
              required
              type="text"
              placeholder="admin@microdify.local"
              error={emailError}
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError(); }}
              onBlur={handleBlur}
              autoComplete="email"
            />

            <Button variant="primary" loading={loading} className="w-full" type="submit">
              发送重置链接
            </Button>
          </form>

          <p className="text-center mt-5 text-[13px] text-[var(--color-text-secondary)]">
            <Link href="/login" className="font-semibold text-[var(--color-primary)] no-underline">
              返回登录
            </Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
