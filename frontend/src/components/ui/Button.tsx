"use client";

import { type ButtonHTMLAttributes, type ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
type ButtonSize = "sm" | "md" | "lg";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  loading?: boolean;
  children: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    "bg-[var(--color-primary)] text-white border-[3px] border-[var(--color-text)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] hover:bg-[var(--color-primary-hover)] hover:shadow-[2px_2px_0_rgba(26,26,46,0.10)]",
  secondary:
    "bg-[var(--color-surface)] text-[var(--color-text)] border-[3px] border-[var(--color-text)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] hover:bg-[var(--color-bg)] hover:shadow-[2px_2px_0_rgba(26,26,46,0.10)]",
  danger:
    "bg-[var(--color-surface)] text-[var(--color-error)] border-[3px] border-[var(--color-error)] shadow-[4px_4px_0_rgba(239,68,68,0.15)] hover:bg-red-50 hover:shadow-[2px_2px_0_rgba(239,68,68,0.15)]",
  ghost:
    "bg-transparent text-[var(--color-text-secondary)] border-[3px] border-transparent shadow-none hover:bg-[var(--color-bg)] hover:text-[var(--color-text)]",
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: "px-3.5 py-1.5 text-[13px] min-h-[36px] border-2",
  md: "px-5 py-2.5 text-[14px] min-h-[44px]",
  lg: "px-7 py-3.5 text-[16px] min-h-[52px]",
};

export default function Button({
  variant = "primary",
  size = "md",
  loading = false,
  disabled,
  children,
  className = "",
  ...props
}: ButtonProps) {
  const isDisabled = disabled || loading;

  return (
    <button
      className={`inline-flex items-center justify-center gap-2 font-semibold rounded-[var(--radius-md)] transition-all duration-150 ease-out cursor-pointer whitespace-nowrap
        hover:translate-x-[2px] hover:translate-y-[2px]
        active:scale-[0.98] active:translate-x-[1px] active:translate-y-[1px]
        focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[var(--color-primary)]
        ${isDisabled ? "opacity-40 pointer-events-none" : ""}
        ${loading ? "relative text-transparent" : ""}
        ${variantClasses[variant]} ${sizeClasses[size]} ${className}`}
      disabled={isDisabled}
      {...props}
    >
      {children}
      {loading && (
        <span
          className="absolute w-[18px] h-[18px] border-2 border-current border-t-transparent rounded-full animate-spin"
          aria-hidden="true"
        />
      )}
    </button>
  );
}
