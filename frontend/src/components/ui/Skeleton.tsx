interface SkeletonProps {
  className?: string;
}

const shimmer =
  "bg-[length:400%_100%] bg-gradient-to-r from-[var(--color-divider)] via-[#f0f1f4] to-[var(--color-divider)] animate-[shimmer_1.4s_ease_infinite] rounded-[var(--radius-sm)]";

export default function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`${shimmer} ${className}`} />;
}

/* ── Table Skeleton ─────────────────────────────────── */

function TableSkeleton({ rows = 5 }: { rows?: number }) {
  return (
    <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-6">
      <Skeleton className="w-full h-8 mb-3" />
      {Array.from({ length: rows }).map((_, i) => (
        <div key={i} className="flex gap-3 py-3">
          <Skeleton className="w-10 h-10" />
          <Skeleton className="flex-1 h-4" />
        </div>
      ))}
    </div>
  );
}

/* ── Card Skeleton ──────────────────────────────────── */

function CardSkeleton({ count = 3 }: { count?: number }) {
  return (
    <div className="grid grid-cols-[repeat(auto-fill,minmax(240px,1fr))] gap-4">
      {Array.from({ length: count }).map((_, i) => (
        <div
          key={i}
          className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] p-6"
        >
          <Skeleton className="w-12 h-12 mb-3" />
          <Skeleton className="w-[70%] h-5 mb-2" />
          <Skeleton className="w-full h-3.5 mb-2" />
          <Skeleton className="w-[50%] h-3.5" />
        </div>
      ))}
    </div>
  );
}

Skeleton.Table = TableSkeleton;
Skeleton.Card = CardSkeleton;
