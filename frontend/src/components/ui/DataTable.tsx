"use client";

import {
  type ReactNode,
  useState,
  useCallback,
  useRef,
  useEffect,
  forwardRef,
  useImperativeHandle,
} from "react";
import Table from "./Table";
import Skeleton from "./Skeleton";
import EmptyState from "./EmptyState";
import Button from "./Button";

/* ── Types ──────────────────────────────────────────── */

interface Column<T> {
  key: string;
  label: string;
  width?: string;
  render?: (row: T) => ReactNode;
}

interface FetchResult<T> {
  items: T[];
  total: number;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  fetchData: (params: { page: number; pageSize: number }) => Promise<FetchResult<T>>;
  pageSize?: number;
  emptyTitle?: string;
  emptyDesc?: string;
  emptyAction?: ReactNode;
  onRowClick?: (row: T) => void;
}

export interface DataTableHandle {
  refresh: () => Promise<void>;
}

/* ── Component ──────────────────────────────────────── */

function DataTableInner<T>(
  {
    columns,
    fetchData,
    pageSize = 20,
    emptyTitle = "暂无数据",
    emptyDesc,
    emptyAction,
    onRowClick,
  }: DataTableProps<T>,
  ref: React.Ref<DataTableHandle>
) {
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);

  const mountedRef = useRef(true);

  const load = useCallback(
    async (p: number) => {
      setLoading(true);
      setError(null);
      try {
        const result = await fetchData({ page: p, pageSize });
        if (mountedRef.current) {
          setData(result.items);
          setTotal(result.total);
          setPage(p);
        }
      } catch (err) {
        if (mountedRef.current) {
          setError(err instanceof Error ? err.message : "请求失败");
        }
      } finally {
        if (mountedRef.current) {
          setLoading(false);
        }
      }
    },
    [fetchData, pageSize]
  );

  useEffect(() => {
    mountedRef.current = true;
    load(1);
    return () => {
      mountedRef.current = false;
    };
  }, [load]);

  useImperativeHandle(ref, () => ({
    refresh: () => load(page),
  }));

  /* ── Render states ──────────────────────────────── */

  if (loading) {
    return <Skeleton.Table rows={pageSize} />;
  }

  if (error) {
    return (
      <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-12 text-center">
        <p className="text-[var(--color-error)] font-medium mb-4">{error}</p>
        <Button variant="secondary" size="sm" onClick={() => load(page)}>
          重试
        </Button>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <EmptyState
        title={emptyTitle}
        description={emptyDesc || "当前没有可显示的数据"}
        actionLabel={undefined}
      />
    );
  }

  return (
    <Table>
      <Table.Head>
        <Table.Row>
          {columns.map((col) => (
            <Table.HeaderCell key={col.key} className={col.width ? `w-[${col.width}]` : ""}>
              {col.label}
            </Table.HeaderCell>
          ))}
        </Table.Row>
      </Table.Head>
      <Table.Body>
        {data.map((row, i) => (
          <Table.Row key={i}>
            {columns.map((col) => (
              <Table.Cell
                key={col.key}
                className={onRowClick ? "cursor-pointer" : ""}
              >
                {col.render
                  ? col.render(row)
                  : (row as Record<string, unknown>)[col.key] as ReactNode}
              </Table.Cell>
            ))}
          </Table.Row>
        ))}
      </Table.Body>
      <Table.Footer total={total} page={page} onPageChange={(p) => load(p)} />
    </Table>
  );
}

const DataTable = forwardRef(DataTableInner) as <T>(
  props: DataTableProps<T> & { ref?: React.Ref<DataTableHandle> }
) => ReactNode;

export default DataTable;
