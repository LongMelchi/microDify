import { type ReactNode, Children, isValidElement } from "react";

/* ── Table ──────────────────────────────────────────── */

interface TableProps {
  children: ReactNode;
  className?: string;
}

function isFooter(child: unknown): boolean {
  return isValidElement(child) && (child.type as { displayName?: string }).displayName === "TableFooter";
}

export default function Table({ children, className = "" }: TableProps) {
  const kids = Children.toArray(children);
  const footer = kids.find(isFooter);
  const body = kids.filter((c) => !isFooter(c));

  return (
    <div
      className={`bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] overflow-hidden ${className}`}
    >
      <table className="w-full border-collapse text-[14px]">{body}</table>
      {footer}
    </div>
  );
}

/* ── Table Header ───────────────────────────────────── */

function TableHead({ children }: { children: ReactNode }) {
  return <thead className="bg-[var(--color-bg)]">{children}</thead>;
}

/* ── Table Header Cell ──────────────────────────────── */

function TableHeaderCell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <th
      className={`px-4 py-3 text-left font-semibold text-[12px] uppercase tracking-wider text-[var(--color-text-secondary)] border-b-2 border-[var(--color-border)] ${className}`}
    >
      {children}
    </th>
  );
}

/* ── Table Body ─────────────────────────────────────── */

function TableBody({ children }: { children: ReactNode }) {
  return <tbody>{children}</tbody>;
}

/* ── Table Row ──────────────────────────────────────── */

function TableRow({ children }: { children: ReactNode }) {
  return (
    <tr className="even:bg-[rgba(248,249,252,0.5)] hover:bg-[var(--color-primary-light)] transition-colors duration-100">
      {children}
    </tr>
  );
}

/* ── Table Cell ─────────────────────────────────────── */

function TableCell({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <td className={`px-4 py-3 border-b border-[var(--color-divider)] ${className}`}>
      {children}
    </td>
  );
}

/* ── Table Footer / Pagination ──────────────────────── */

interface TableFooterProps {
  total: number;
  page: number;
  pageSize?: number;
  onPageChange?: (page: number) => void;
}

function TableFooter({ total, page, pageSize = 20, onPageChange }: TableFooterProps) {
  const maxPage = Math.max(1, Math.ceil(total / pageSize));
  const hasPrev = page > 1;
  const hasNext = page < maxPage;

  return (
    <div className="flex items-center justify-between px-6 py-4 border-t-2 border-[var(--color-divider)] text-[13px] text-[var(--color-text-secondary)]">
      <span>共 {total} 条</span>
      <div className="flex gap-1">
        <button
          className="w-9 h-9 border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] font-semibold text-[13px] cursor-pointer transition-all duration-150 hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] disabled:opacity-30 disabled:cursor-not-allowed"
          disabled={!hasPrev}
          onClick={() => onPageChange?.(page - 1)}
        >
          &lt;
        </button>
        <button className="w-9 h-9 border-2 border-[var(--color-primary)] rounded-[var(--radius-sm)] bg-[var(--color-primary)] text-white font-semibold text-[13px]">
          {page}
        </button>
        <button
          className="w-9 h-9 border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] font-semibold text-[13px] cursor-pointer transition-all duration-150 hover:border-[var(--color-primary)] hover:text-[var(--color-primary)] disabled:opacity-30 disabled:cursor-not-allowed"
          disabled={!hasNext}
          onClick={() => onPageChange?.(page + 1)}
        >
          &gt;
        </button>
      </div>
    </div>
  );
}

TableFooter.displayName = "TableFooter";

Table.Head = TableHead;
Table.HeaderCell = TableHeaderCell;
Table.Body = TableBody;
Table.Row = TableRow;
Table.Cell = TableCell;
Table.Footer = TableFooter;
