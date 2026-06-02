import { type ReactNode } from "react";
import Button from "./Button";

interface EmptyStateProps {
  icon?: string;
  title: string;
  description: string;
  actionLabel?: string;
  onAction?: () => void;
}

export default function EmptyState({
  icon = "📄",
  title,
  description,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="text-center py-12 px-6">
      <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-bg)] border-[3px] border-[var(--color-border)] flex items-center justify-center text-[24px] text-[var(--color-text-tertiary)]">
        {icon}
      </div>
      <h3 className="text-[16px] font-semibold mb-2">{title}</h3>
      <p className="text-[var(--color-text-secondary)] mb-5 max-w-[320px] mx-auto">
        {description}
      </p>
      {actionLabel && onAction && (
        <Button variant="primary" onClick={onAction}>
          {actionLabel}
        </Button>
      )}
    </div>
  );
}
