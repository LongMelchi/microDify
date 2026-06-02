"use client";

import { useState, useRef } from "react";
import Modal from "@/components/ui/Modal";
import Button from "@/components/ui/Button";
import { showToast } from "@/components/ui/Toast";

export function useConfirm(options?: {
  title?: string;
  message?: string;
  confirmLabel?: string;
}) {
  const title = options?.title ?? "确认删除";
  const message = options?.message ?? "确定要执行此操作吗？此操作不可恢复。";
  const confirmLabel = options?.confirmLabel ?? "确认删除";

  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const callRef = useRef<(() => Promise<unknown>) | null>(null);
  const resolveRef = useRef<((ok: boolean) => void) | null>(null);

  function confirm(apiCall: () => Promise<unknown>): Promise<boolean> {
    return new Promise((resolve) => {
      callRef.current = apiCall;
      resolveRef.current = resolve;
      setOpen(true);
    });
  }

  async function handleConfirm() {
    if (!callRef.current) return;
    setLoading(true);
    try {
      await callRef.current();
      showToast("success", "操作成功");
      setOpen(false);
      resolveRef.current?.(true);
    } catch (err) {
      const msg = err instanceof Error ? err.message : "操作失败";
      showToast("error", msg);
    } finally {
      setLoading(false);
    }
  }

  function handleCancel() {
    setOpen(false);
    resolveRef.current?.(false);
  }

  const dialog = (
    <Modal
      open={open}
      onClose={handleCancel}
      title={title}
      footer={
        <>
          <Button variant="secondary" size="sm" onClick={handleCancel}>
            取消
          </Button>
          <Button variant="danger" size="sm" loading={loading} onClick={handleConfirm}>
            {confirmLabel}
          </Button>
        </>
      }
    >
      <p className="text-[14px] text-[var(--color-text-secondary)]">{message}</p>
    </Modal>
  );

  return { confirm, ConfirmationDialog: dialog } as const;
}
