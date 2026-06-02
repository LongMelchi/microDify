"use client";

import { type ReactNode, useEffect, useCallback } from "react";

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title: string;
  children: ReactNode;
  footer?: ReactNode;
}

export default function Modal({ open, onClose, title, children, footer }: ModalProps) {
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    },
    [onClose]
  );

  useEffect(() => {
    if (open) {
      document.addEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "hidden";
    }
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      document.body.style.overflow = "";
    };
  }, [open, handleKeyDown]);

  if (!open) return null;

  return (
    <div
      className="fixed inset-0 z-100 flex items-center justify-center bg-[rgba(26,26,46,0.35)] backdrop-blur-[4px]"
      onClick={onClose}
    >
      <div
        className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[6px_6px_0_rgba(26,26,46,0.08)] w-[90%] max-w-[480px] animate-[modalIn_250ms_cubic-bezier(0.16,1,0.3,1)]"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-5 border-b-2 border-[var(--color-divider)]">
          <h3 className="text-[16px] font-semibold">{title}</h3>
          <button
            onClick={onClose}
            className="text-[18px] text-[var(--color-text-tertiary)] cursor-pointer bg-none border-none leading-none"
            aria-label="关闭"
          >
            &times;
          </button>
        </div>
        <div className="px-6 py-6">{children}</div>
        {footer && (
          <div className="flex justify-end gap-3 px-6 py-4 border-t-2 border-[var(--color-divider)]">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
