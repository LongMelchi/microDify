"use client";

import { useState, useRef } from "react";
import DataTable, { type DataTableHandle } from "@/components/ui/DataTable";
import { Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import Modal from "@/components/ui/Modal";
import { showToast } from "@/components/ui/Toast";
import { useRequest } from "@/hooks/useRequest";
import { useConfirm } from "@/hooks/useConfirm";
import { getPage, post, put, del, BizError } from "@/lib/api";
import { getHealth, type HealthInfo } from "@/lib/health";
import { formatDateTime } from "@/lib/utils";

/* ── Types ──────────────────────────────────────────── */

interface ProviderItem {
  id: string;
  name: string;
  provider_type: string;
  base_url: string;
  api_key: string;
  note: string | null;
  is_active: boolean;
  last_called_at: string | null;
  created_at: string;
}

interface TestResultState {
  open: boolean;
  ok: boolean;
  provider: string;
  model?: string;
  sent?: string;
  response?: string;
  error?: string;
}

/* ── Helpers ────────────────────────────────────────── */

const typeColors: Record<string, string> = {
  openai: "bg-[var(--color-primary)]",
  anthropic: "bg-[var(--color-secondary)]",
};
const defaultColor = "bg-[var(--color-primary)]";

const typeLabels: Record<string, string> = {
  openai: "OpenAI",
  anthropic: "Anthropic",
};

const typeTagVariants: Record<string, "primary" | "info" | "default"> = {
  openai: "primary",
  anthropic: "info",
};

const typeOptions = [
  { value: "openai", label: "OpenAI" },
  { value: "anthropic", label: "Anthropic" },
];

/* ── Component ──────────────────────────────────────── */

export default function ProviderPage() {
  const tableRef = useRef<DataTableHandle>(null);
  const { confirm, ConfirmationDialog } = useConfirm();
  const { data: health } = useRequest<HealthInfo>(() => getHealth());

  const fetchProviders = (args: { page: number; pageSize: number }) =>
    getPage<ProviderItem>("/provider/configs", {
      page: String(args.page),
      pageSize: String(args.pageSize),
    });

  /* ── Modal / form state ─────────────────────────── */

  const [modalOpen, setModalOpen] = useState(false);
  const [editData, setEditData] = useState<ProviderItem | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<TestResultState>({
    open: false,
    ok: false,
    provider: "",
  });

  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState("openai");
  const [formBaseUrl, setFormBaseUrl] = useState("");
  const [formApiKey, setFormApiKey] = useState("");
  const [formNote, setFormNote] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [formSaving, setFormSaving] = useState(false);

  function openCreate() {
    setEditData(null);
    setFormName("");
    setFormType("openai");
    setFormBaseUrl("");
    setFormApiKey("");
    setFormNote("");
    setFormErrors({});
    setModalOpen(true);
  }

  function openEdit(p: ProviderItem) {
    setEditData(p);
    setFormName(p.name);
    setFormType(p.provider_type);
    setFormBaseUrl(p.base_url);
    setFormApiKey(""); // 后端只回脱敏 key，编辑时留空表示不修改
    setFormNote(p.note || "");
    setFormErrors({});
    setModalOpen(true);
  }

  function clearError(field: string) {
    setFormErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!formName.trim()) errors.name = "请输入名称";
    if (!formBaseUrl.trim()) errors.baseUrl = "请输入 Base URL";
    if (!editData && !formApiKey.trim()) errors.apiKey = "请输入 API Key";
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;
    setFormSaving(true);
    try {
      if (editData) {
        const body: Record<string, string> = {
          name: formName.trim(),
          provider_type: formType,
          base_url: formBaseUrl.trim(),
        };
        if (formApiKey.trim()) body.api_key = formApiKey.trim();
        if (formNote.trim()) body.note = formNote.trim();
        await put(`/provider/configs/${editData.id}`, body);
        showToast("success", "提供商已更新");
      } else {
        await post("/provider/configs", {
          name: formName.trim(),
          provider_type: formType,
          base_url: formBaseUrl.trim(),
          api_key: formApiKey.trim(),
          note: formNote.trim() || undefined,
        });
        showToast("success", "提供商已添加");
      }
      setModalOpen(false);
      tableRef.current?.refresh();
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "保存失败";
      showToast("error", msg);
    } finally {
      setFormSaving(false);
    }
  }

  async function handleDelete(provider: ProviderItem) {
    const ok = await confirm(() => del(`/provider/configs/${provider.id}`));
    if (ok) {
      showToast("success", `已删除 ${provider.name}`);
      tableRef.current?.refresh();
    }
  }

  async function handleTest(provider: ProviderItem) {
    setTestingId(provider.id);
    try {
      const result = await post<{
        ok: boolean;
        provider: string;
        model?: string;
        sent?: string;
        response?: string;
        error?: string;
      }>(`/provider/configs/${provider.id}/test`);
      setTestResult({
        open: true,
        ok: result.ok,
        provider: result.provider || provider.name,
        model: result.model,
        sent: result.sent,
        response: result.response,
        error: result.error,
      });
      if (result.ok) {
        tableRef.current?.refresh(); // 状态已变为活跃
      }
    } catch {
      setTestResult({
        open: true,
        ok: false,
        provider: provider.name,
        error: "网络请求失败，请检查后端服务",
      });
    } finally {
      setTestingId(null);
    }
  }

  /* ── Columns ────────────────────────────────────── */

  const columns = [
    {
      key: "name",
      label: "名称",
      render: (p: ProviderItem) => (
        <div className="flex items-center gap-2.5">
          <div
            className={`w-8 h-8 rounded-[var(--radius-sm)] ${typeColors[p.provider_type] || defaultColor} border-2 border-[var(--color-text)] flex items-center justify-center text-white font-bold text-[13px] flex-shrink-0`}
          >
            {p.name.charAt(0)}
          </div>
          <span className="font-semibold">{p.name}</span>
        </div>
      ),
    },
    {
      key: "provider_type",
      label: "类型",
      render: (p: ProviderItem) => (
        <Tag variant={typeTagVariants[p.provider_type] || "default"}>
          {typeLabels[p.provider_type] || p.provider_type}
        </Tag>
      ),
    },
    {
      key: "base_url",
      label: "Base URL",
      className: "font-[var(--font-mono)] text-[13px] max-w-[220px] truncate",
      render: (p: ProviderItem) => p.base_url,
    },
    {
      key: "api_key",
      label: "API Key",
      className: "font-[var(--font-mono)] text-[13px]",
      render: (p: ProviderItem) => p.api_key,
    },
    {
      key: "note",
      label: "备注",
      className: "text-[13px] text-[var(--color-text-secondary)] max-w-[180px] truncate",
      render: (p: ProviderItem) => p.note || "--",
    },
    {
      key: "is_active",
      label: "状态",
      render: (p: ProviderItem) => (
        <Tag variant={p.is_active ? "success" : "warning"}>
          {p.is_active ? "活跃" : "未激活"}
        </Tag>
      ),
    },
    {
      key: "last_called_at",
      label: "最近调用",
      className: "text-[12px] text-[var(--color-text-secondary)]",
      render: (p: ProviderItem) => (p.last_called_at ? formatDateTime(p.last_called_at) : "--"),
    },
    {
      key: "actions",
      label: "操作",
      render: (p: ProviderItem) => (
        <div className="flex items-center gap-1">
          <button
            type="button"
            disabled={testingId === p.id}
            onClick={() => handleTest(p)}
            className="inline-flex items-center gap-2 px-3.5 py-1.5 text-[13px] font-semibold rounded-[var(--radius-md)] border-2 border-[var(--color-text)] bg-[var(--color-surface)] text-[var(--color-text)] shadow-[2px_2px_0_rgba(26,26,46,0.10)] transition-all duration-150 ease-out cursor-pointer hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none active:scale-[0.98] disabled:opacity-60 disabled:pointer-events-none min-h-[36px]"
          >
            {testingId === p.id && (
              <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            {testingId === p.id ? "测试中..." : "测试连接"}
          </button>
          <Button variant="ghost" size="sm" onClick={() => openEdit(p)}>
            编辑
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="!text-[var(--color-error)]"
            onClick={() => handleDelete(p)}
          >
            删除
          </Button>
        </div>
      ),
    },
  ];

  /* ── Render ─────────────────────────────────────── */

  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">模型管理</h1>
      <p className="text-[var(--color-text-secondary)] mb-6">
        管理 LLM 提供商连接和模型配置
        {health && (
          <span className="text-[var(--color-text-tertiary)] ml-2">
            microDify v{health.version}
          </span>
        )}
      </p>

      {/* Toolbar */}
      <div className="flex items-center justify-end mb-5">
        <Button variant="primary" size="sm" onClick={openCreate}>
          + 新增提供商
        </Button>
      </div>

      <DataTable<ProviderItem>
        ref={tableRef}
        columns={columns}
        fetchData={fetchProviders}
        emptyIcon="⚡"
        emptyTitle="暂无提供商"
        emptyDesc="还没有配置任何 LLM 提供商，点击下方按钮添加"
        emptyActionLabel="新增提供商"
        onEmptyAction={openCreate}
      />

      {/* Create / Edit modal */}
      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editData ? "编辑提供商" : "新增提供商"}
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setModalOpen(false)}>
              取消
            </Button>
            <Button variant="primary" size="sm" loading={formSaving} onClick={handleSave}>
              保存
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-1">
          <Input
            label="名称"
            required
            placeholder="DeepSeek"
            value={formName}
            error={formErrors.name}
            onChange={(e) => { setFormName(e.target.value); clearError("name"); }}
          />
          <Select label="类型" value={formType} onChange={setFormType} options={typeOptions} />
          <Input
            label="Base URL"
            required
            placeholder="https://api.deepseek.com"
            value={formBaseUrl}
            error={formErrors.baseUrl}
            onChange={(e) => { setFormBaseUrl(e.target.value); clearError("baseUrl"); }}
          />
          <Input
            label="API Key"
            required={!editData}
            type="password"
            placeholder={editData ? "留空表示不修改" : "sk-..."}
            value={formApiKey}
            error={formErrors.apiKey}
            onChange={(e) => { setFormApiKey(e.target.value); clearError("apiKey"); }}
          />
          <Input
            label="备注"
            placeholder="可选：用途说明"
            value={formNote}
            onChange={(e) => setFormNote(e.target.value)}
          />
        </div>
      </Modal>

      {ConfirmationDialog}

      {/* Test result modal */}
      <Modal
        open={testResult.open}
        onClose={() => setTestResult((prev) => ({ ...prev, open: false }))}
        title={testResult.ok ? "测试通过" : "测试失败"}
        footer={
          <Button
            variant={testResult.ok ? "primary" : "secondary"}
            size="sm"
            onClick={() => setTestResult((prev) => ({ ...prev, open: false }))}
          >
            关闭
          </Button>
        }
      >
        <div className="text-[14px] space-y-3">
          <div>
            <span className="text-[var(--color-text-secondary)]">提供商：</span>
            <span className="font-semibold ml-1">{testResult.provider}</span>
          </div>
          {testResult.model && (
            <div>
              <span className="text-[var(--color-text-secondary)]">模型：</span>
              <span className="font-mono text-[13px] ml-1">{testResult.model}</span>
            </div>
          )}
          {testResult.sent && (
            <div>
              <span className="text-[var(--color-text-secondary)]">发送内容：</span>
              <div className="mt-1 p-3 rounded-[var(--radius-sm)] bg-[var(--color-bg)] border-2 border-[var(--color-border)] font-mono text-[13px] whitespace-pre-wrap">
                {testResult.sent}
              </div>
            </div>
          )}
          {testResult.response && (
            <div>
              <span className="text-[var(--color-text-secondary)]">返回内容：</span>
              <div className="mt-1 p-3 rounded-[var(--radius-sm)] bg-[var(--color-secondary-light)] border-2 border-[var(--color-secondary)] font-mono text-[13px] whitespace-pre-wrap max-h-[200px] overflow-y-auto">
                {testResult.response}
              </div>
            </div>
          )}
          {testResult.error && (
            <div>
              <span className="text-[var(--color-text-secondary)]">错误信息：</span>
              <div className="mt-1 p-3 rounded-[var(--radius-sm)] bg-red-50 border-2 border-[var(--color-error)] text-[var(--color-error)] font-mono text-[13px] whitespace-pre-wrap">
                {testResult.error}
              </div>
            </div>
          )}
        </div>
      </Modal>
    </div>
  );
}
