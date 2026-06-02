"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";
import { post, BizError } from "@/lib/api";
import { setToken } from "@/lib/auth";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!email.trim()) {
      showToast("warning", "请输入邮箱地址");
      return;
    }
    if (!password) {
      showToast("warning", "请输入密码");
      return;
    }

    setLoading(true);
    try {
      const result = await post<{ access_token: string; token_type: string }>(
        "/auth/login",
        { email: email.trim(), password }
      );
      setToken(result.access_token);
      router.push("/");
    } catch (err) {
      const message =
        err instanceof BizError ? err.message : "登录失败，请检查邮箱和密码";
      showToast("error", message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--color-bg)]">
      <Card className="w-full max-w-[420px] !shadow-[6px_6px_0_rgba(26,26,46,0.08)]">
        <Card.Body className="!p-10">
          {/* Brand */}
          <div className="text-center mb-8">
            <div className="w-12 h-12 mx-auto mb-4 rounded-[var(--radius-sm)] bg-[var(--color-primary)] border-[3px] border-[var(--color-text)] flex items-center justify-center text-white text-xl font-bold">
              m
            </div>
            <h1 className="text-2xl font-bold mb-2">登录 microDify</h1>
            <p className="text-[14px] text-[var(--color-text-secondary)]">
              使用你的团队账号登录 AI Agent 平台
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <Input
              label="邮箱地址"
              type="text"
              placeholder="admin@microdify.local"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />

            <Input
              label="密码"
              type="password"
              placeholder="输入密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
            />

            {/* Remember me + Forgot password */}
            <div className="flex items-center justify-between mb-5">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => setRemember(e.target.checked)}
                  className="w-[18px] h-[18px] accent-[var(--color-primary)] cursor-pointer"
                />
                <span className="text-[14px]">记住我</span>
              </label>
              <Link href="/forgot-password" className="text-[13px] font-medium text-[var(--color-primary)] no-underline">
                忘记密码？
              </Link>
            </div>

            <Button variant="primary" loading={loading} className="w-full" type="submit">
              登录
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
            <span className="text-[12px] text-[var(--color-text-tertiary)]">或</span>
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
          </div>

          <p className="text-center text-[13px] text-[var(--color-text-secondary)]">
            还没有账号？
            <Link href="/register" className="font-semibold text-[var(--color-primary)] no-underline ml-1">
              注册新账号
            </Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
