"use client";

import { useEffect, useState, useCallback, type ReactNode } from "react";

type ToastType = "success" | "error" | "warning" | "info";

interface ToastItem {
  id: number;
  type: ToastType;
  message: string;
  duration: number;
}

let toastId = 0;
let addToastFn: ((type: ToastType, message: string, options?: { duration?: number }) => void) | null = null;

export function showToast(
  type: ToastType,
  message: string,
  options?: { duration?: number }
) {
  addToastFn?.(type, message, options);
}

const icons: Record<ToastType, string> = {
  success: "✓",
  error: "✗",
  warning: "⚠",
  info: "ℹ",
};

const borderColors: Record<ToastType, string> = {
  success: "border-[var(--color-success)]",
  error: "border-[var(--color-error)]",
  warning: "border-[var(--color-warning)]",
  info: "border-[var(--color-info)]",
};

export default function ToastContainer() {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = useCallback(
    (type: ToastType, message: string, options?: { duration?: number }) => {
      const duration = options?.duration ?? 4000;
      const id = ++toastId;
      setToasts((prev) => [...prev, { id, type, message, duration }]);
      if (duration > 0) {
        setTimeout(() => {
          setToasts((prev) => prev.filter((t) => t.id !== id));
        }, duration);
      }
    },
    []
  );

  useEffect(() => {
    addToastFn = addToast;
    return () => {
      addToastFn = null;
    };
  }, [addToast]);

  const remove = (id: number) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  return (
    <div className="fixed top-5 right-5 z-200 flex flex-col gap-3" aria-live="polite">
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`flex items-center gap-3 px-4 py-3.5 rounded-[var(--radius-md)] border-[3px] border-[var(--color-text)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] bg-[var(--color-surface)] text-[14px] font-medium min-w-[320px] animate-[toastIn_300ms_cubic-bezier(0.16,1,0.3,1)] ${borderColors[t.type]}`}
        >
          <span className="text-[18px] flex-shrink-0">{icons[t.type]}</span>
          <span>{t.message}</span>
          <button
            className="ml-auto text-[18px] text-[var(--color-text-tertiary)] cursor-pointer bg-none border-none"
            onClick={() => remove(t.id)}
            aria-label="关闭"
          >
            &times;
          </button>
        </div>
      ))}
    </div>
  );
}
