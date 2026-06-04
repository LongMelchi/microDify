import { type ReactNode } from "react";

type TagVariant = "default" | "primary" | "success" | "warning" | "error" | "info";

interface TagProps {
  variant?: TagVariant;
  children: ReactNode;
  className?: string;
}

const variantClasses: Record<TagVariant, string> = {
  default: "bg-[var(--color-bg)] text-[var(--color-text)]",
  primary: "bg-[var(--color-primary-light)] text-[var(--color-primary)]",
  success: "bg-[var(--color-secondary-light)] text-[#059669]",
  warning: "bg-[var(--color-accent-light)] text-[#b45309]",
  error: "bg-red-50 text-[#dc2626]",
  info: "bg-blue-50 text-[#2563eb]",
};

export default function Tag({ variant = "default", children, className = "" }: TagProps) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-3 py-[3px] text-[12px] font-semibold rounded-[var(--radius-full)] border-2 border-[var(--color-text)] leading-relaxed whitespace-nowrap ${variantClasses[variant]} ${className}`}
    >
      {children}
    </span>
  );
}

/* ── Badge ──────────────────────────────────────────── */

interface BadgeProps {
  count: number | string;
  className?: string;
}

export function Badge({ count, className = "" }: BadgeProps) {
  return (
    <span
      className={`inline-flex items-center justify-center min-w-[20px] h-5 px-1.5 text-[11px] font-bold text-white bg-[var(--color-error)] rounded-[var(--radius-full)] font-[var(--font-mono)] ${className}`}
    >
      {count}
    </span>
  );
}
