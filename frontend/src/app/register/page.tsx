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

/* ── Types ──────────────────────────────────────────── */

interface FieldErrors {
  username?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
}

/* ── Validators ─────────────────────────────────────── */

function validateUsername(v: string): string | undefined {
  if (!v.trim() || v.trim().length < 2) return "用户名至少 2 个字符";
  return undefined;
}

function validateEmail(v: string): string | undefined {
  if (!v.trim()) return "请输入邮箱地址";
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v.trim())) return "请输入有效的邮箱地址";
  return undefined;
}

function validatePassword(v: string): string | undefined {
  if (v.length < 8) return "密码至少 8 个字符";
  return undefined;
}

function validateConfirmPassword(pw: string, cpw: string): string | undefined {
  if (pw !== cpw) return "两次密码输入不一致";
  return undefined;
}

/* ── Component ──────────────────────────────────────── */

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [fieldErrors, setFieldErrors] = useState<FieldErrors>({});
  const [errorModal, setErrorModal] = useState<{ open: boolean; message: string }>({
    open: false,
    message: "",
  });
  const router = useRouter();

  /* ── Blur handler: validate single field on leave ── */

  function handleBlur(field: keyof FieldErrors) {
    let err: string | undefined;
    switch (field) {
      case "username":
        err = validateUsername(username);
        break;
      case "email":
        err = validateEmail(email);
        break;
      case "password":
        err = validatePassword(password);
        break;
      case "confirmPassword":
        err = validateConfirmPassword(password, confirmPassword);
        break;
    }
    setFieldErrors((prev) => {
      if (prev[field] === err) return prev;
      return { ...prev, [field]: err };
    });
  }

  /* ── Clear error on edit ────────────────────────── */

  function clearError(field: keyof FieldErrors) {
    if (fieldErrors[field]) {
      setFieldErrors((prev) => ({ ...prev, [field]: undefined }));
    }
  }

  /* ── Full validation on submit ──────────────────── */

  function validateAll(): boolean {
    const errors: FieldErrors = {
      username: validateUsername(username),
      email: validateEmail(email),
      password: validatePassword(password),
      confirmPassword: validateConfirmPassword(password, confirmPassword),
    };
    setFieldErrors(errors);

    // Auto-focus first error
    const order: (keyof FieldErrors)[] = ["username", "email", "password", "confirmPassword"];
    for (const k of order) {
      if (errors[k]) {
        document.getElementById(k === "username" ? "用户名" : k === "email" ? "邮箱地址" : k === "password" ? "密码" : "确认密码")?.focus();
        break;
      }
    }
    return !Object.values(errors).some(Boolean);
  }

  /* ── Submit ─────────────────────────────────────── */

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!validateAll()) return;

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
      if (err instanceof BizError) {
        setErrorModal({ open: true, message: err.message });
      } else {
        showToast("error", "注册失败，请稍后重试");
      }
    } finally {
      setLoading(false);
    }
  }

  /* ── Render ─────────────────────────────────────── */

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
          <form onSubmit={handleSubmit} noValidate>
            <Input
              label="用户名"
              required
              placeholder="2-50 个字符"
              error={fieldErrors.username}
              value={username}
              onChange={(e) => { setUsername(e.target.value); clearError("username"); }}
              onBlur={() => handleBlur("username")}
              autoComplete="username"
            />

            <Input
              label="邮箱地址"
              required
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
              required
              type="password"
              placeholder="至少 8 个字符"
              hint="至少 8 个字符"
              error={fieldErrors.password}
              value={password}
              onChange={(e) => {
                setPassword(e.target.value);
                clearError("password");
                if (e.target.value === confirmPassword) clearError("confirmPassword");
              }}
              onBlur={() => handleBlur("password")}
              autoComplete="new-password"
            />

            <Input
              label="确认密码"
              required
              type="password"
              placeholder="再次输入密码"
              error={fieldErrors.confirmPassword}
              value={confirmPassword}
              onChange={(e) => {
                setConfirmPassword(e.target.value);
                if (e.target.value === password) clearError("confirmPassword");
              }}
              onBlur={() => handleBlur("confirmPassword")}
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

      {/* Error Modal */}
      <Modal
        open={errorModal.open}
        onClose={() => setErrorModal({ open: false, message: "" })}
        title="注册失败"
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
