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

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    if (!username.trim() || username.trim().length < 2) {
      showToast("warning", "用户名至少 2 个字符");
      return;
    }
    if (!email.trim()) {
      showToast("warning", "请输入邮箱地址");
      return;
    }
    if (password.length < 8) {
      showToast("warning", "密码至少 8 个字符");
      return;
    }
    if (password !== confirmPassword) {
      showToast("warning", "两次密码输入不一致");
      return;
    }

    setLoading(true);
    try {
      const result = await post<{ access_token: string; token_type: string }>(
        "/auth/register",
        { email: email.trim(), username: username.trim(), password }
      );
      setToken(result.access_token);
      showToast("success", "注册成功");
      router.push("/");
    } catch (err) {
      const message =
        err instanceof BizError ? err.message : "注册失败，请稍后重试";
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
            <h1 className="text-2xl font-bold mb-2">创建 microDify 账号</h1>
            <p className="text-[14px] text-[var(--color-text-secondary)]">
              填写以下信息注册新账号
            </p>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit}>
            <Input
              label="用户名"
              required
              placeholder="2-50 个字符"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
            />

            <Input
              label="邮箱地址"
              required
              type="text"
              placeholder="admin@microdify.local"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              autoComplete="email"
            />

            <Input
              label="密码"
              required
              type="password"
              placeholder="至少 8 个字符"
              hint="至少 8 个字符"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />

            <Input
              label="确认密码"
              required
              type="password"
              placeholder="再次输入密码"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              autoComplete="new-password"
            />

            <Button variant="primary" loading={loading} className="w-full" type="submit">
              注册
            </Button>
          </form>

          {/* Divider */}
          <div className="flex items-center gap-3 my-5">
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
            <span className="text-[12px] text-[var(--color-text-tertiary)]">或</span>
            <span className="flex-1 h-px bg-[var(--color-divider)]" />
          </div>

          <p className="text-center text-[13px] text-[var(--color-text-secondary)]">
            已有账号？
            <Link href="/login" className="font-semibold text-[var(--color-primary)] no-underline ml-1">
              立即登录
            </Link>
          </p>
        </Card.Body>
      </Card>
    </div>
  );
}
