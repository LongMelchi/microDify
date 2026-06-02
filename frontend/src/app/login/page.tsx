"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Card from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Modal from "@/components/ui/Modal";
import { showToast } from "@/components/ui/Toast";
import { post, BizError } from "@/lib/api";
import { setToken } from "@/lib/auth";

/* ── Validators ─────────────────────────────────────── */

function validateEmail(v: string): string | undefined {
  if (!v.trim()) return "请输入邮箱地址";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())) return "请输入有效的邮箱地址";
  return undefined;
}

function validatePassword(v: string): string | undefined {
  if (!v) return "请输入密码";
  return undefined;
}

/* ── Component ──────────────────────────────────────── */

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
  const [errorModal, setErrorModal] = useState<{ open: boolean; message: string }>({
    open: false,
    message: "",
  });
  const router = useRouter();

  /* ── Blur validation ─────────────────────────────── */

  function handleBlur(field: "email" | "password") {
    const err = field === "email" ? validateEmail(email) : validatePassword(password);
    setFieldErrors((prev) => (prev[field] === err ? prev : { ...prev, [field]: err }));
  }

  function clearError(field: "email" | "password") {
    if (fieldErrors[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  /* ── Full validation on submit ───────────────────── */

  function validateAll(): boolean {
    const errors = {
      email: validateEmail(email),
      password: validatePassword(password),
    };
    setFieldErrors(errors);
    if (errors.email) {
      document.getElementById("邮箱地址")?.focus();
    } else if (errors.password) {
      document.getElementById("密码")?.focus();
    }
    return !errors.email && !errors.password;
  }

  /* ── Submit ──────────────────────────────────────── */

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validateAll()) return;

    setLoading(true);
    try {
      const result = await post<{ access_token: string; token_type: string }>(
        "/auth/login",
        { email: email.trim(), password }
      );
      setToken(result.access_token);
      router.push("/");
    } catch (err) {
      if (err instanceof BizError) {
        setErrorModal({ open: true, message: err.message });
      } else {
        showToast("error", "登录失败，请稍后重试");
      }
    } finally {
      setLoading(false);
    }
  }

  /* ── Render ──────────────────────────────────────── */

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
          <form onSubmit={handleSubmit} noValidate>
            <Input
              label="邮箱地址"
              type="text"
              placeholder="admin@microdify.local"
              error={fieldErrors.email}
              value={email}
              onChange={(e) => { setEmail(e.target.value); clearError("email"); }}
              onBlur={() => handleBlur("email")}
              autoComplete="email"
            />

            <Input
              label="密码"
              type="password"
              placeholder="输入密码"
              error={fieldErrors.password}
              value={password}
              onChange={(e) => { setPassword(e.target.value); clearError("password"); }}
              onBlur={() => handleBlur("password")}
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

      {/* Error Modal */}
      <Modal
        open={errorModal.open}
        onClose={() => setErrorModal({ open: false, message: "" })}
        title="登录失败"
        footer={
          <Button
            variant="primary"
            size="sm"
            onClick={() => setErrorModal({ open: false, message: "" })}
          >
            我知道了
          </Button>
        }
      >
        <p className="text-[14px] text-[var(--color-text-secondary)]">{errorModal.message}</p>
      </Modal>
    </div>
  );
}
