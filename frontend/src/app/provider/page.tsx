"use client";

import { useState, useRef } from "react";
import Table from "@/components/ui/Table";
import { Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import Modal from "@/components/ui/Modal";
import Skeleton from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import { useRequest } from "@/hooks/useRequest";
import { useConfirm } from "@/hooks/useConfirm";
import { get, post, put, del, BizError } from "@/lib/api";
import { getHealth, type HealthInfo } from "@/lib/health";

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

interface ProviderListData {
  items: ProviderItem[];
  total: number;
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
const defaultTagVariant: "primary" | "info" | "default" = "default";

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  } catch {
    return iso;
  }
}

function formatDateTime(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
  } catch {
    return iso;
  }
}

/* ── Component ──────────────────────────────────────── */

export default function ProviderPage() {
  /* ── List state ─────────────────────────────────── */

  const [page, setPage] = useState(1);
  const pageRef = useRef(page);
  pageRef.current = page;

  const fetchProviders = () =>
    get<ProviderListData>("/provider/configs", {
      page: String(pageRef.current),
      pageSize: "20",
    });

  const { data, loading, error, execute } = useRequest<ProviderListData>(fetchProviders);

  /* ── UI state ───────────────────────────────────── */

  const [modalOpen, setModalOpen] = useState(false);
  const [editData, setEditData] = useState<ProviderItem | null>(null);
  const [testingId, setTestingId] = useState<string | null>(null);
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [testResult, setTestResult] = useState<{
    open: boolean;
    ok: boolean;
    provider: string;
    model?: string;
    sent?: string;
    response?: string;
    error?: string;
  }>({ open: false, ok: false, provider: "" });

  const { data: health } = useRequest<HealthInfo>(() => getHealth());

  /* ── Form state ─────────────────────────────────── */

  const [formName, setFormName] = useState("");
  const [formType, setFormType] = useState("openai");
  const [formBaseUrl, setFormBaseUrl] = useState("");
  const [formApiKey, setFormApiKey] = useState("");
  const [formNote, setFormNote] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [formSaving, setFormSaving] = useState(false);

  const { confirm, ConfirmationDialog } = useConfirm();

  /* ── Modal ──────────────────────────────────────── */

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
    setFormApiKey(p.api_key);  // 后端返回完整 key，预填供修改
    setFormNote(p.note || "");
    setFormErrors({});
    setModalOpen(true);
  }

  /* ── API key toggle ─────────────────────────────── */

  function maskKey(key: string): string {
    if (key.length <= 8) return "****";
    return key.slice(0, 4) + "****" + key.slice(-4);
  }

  function toggleKey(id: string) {
    setShowKeys((prev) => ({ ...prev, [id]: !prev[id] }));
  }

  /* ── Validation ─────────────────────────────────── */

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

  /* ── Save ───────────────────────────────────────── */

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
      execute();
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "保存失败";
      showToast("error", msg);
    } finally {
      setFormSaving(false);
    }
  }

  /* ── Delete ─────────────────────────────────────── */

  async function handleDelete(provider: ProviderItem) {
    const ok = await confirm(() => del(`/provider/configs/${provider.id}`));
    if (ok) {
      showToast("success", `已删除 ${provider.name}`);
      execute();
    }
  }

  /* ── Test connection ────────────────────────────── */

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
        execute();  // 刷新列表（状态已变为活跃）
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

  /* ── Pagination ─────────────────────────────────── */

  function handlePageChange(p: number) {
    setPage(p);
    pageRef.current = p;
    execute();
  }

  /* ── Render ─────────────────────────────────────── */

  const typeOptions = [
    { value: "openai", label: "OpenAI" },
    { value: "anthropic", label: "Anthropic" },
  ];

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

      {/* Loading */}
      {loading ? (
        <Skeleton.Table rows={5} />
      ) : error ? (
        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-12 text-center">
          <p className="text-[var(--color-error)] font-medium mb-4">{error}</p>
          <Button variant="secondary" size="sm" onClick={execute}>重试</Button>
        </div>
      ) : !data || data.items.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-bg)] border-[3px] border-[var(--color-border)] flex items-center justify-center text-2xl text-[var(--color-text-tertiary)]">
            ⚡
          </div>
          <h3 className="text-base font-semibold mb-2">暂无提供商</h3>
          <p className="text-[var(--color-text-secondary)] mb-5">
            还没有配置任何 LLM 提供商，点击上方按钮添加
          </p>
          <Button variant="primary" size="sm" onClick={openCreate}>
            新增提供商
          </Button>
        </div>
      ) : (
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.HeaderCell>名称</Table.HeaderCell>
              <Table.HeaderCell>类型</Table.HeaderCell>
              <Table.HeaderCell>Base URL</Table.HeaderCell>
              <Table.HeaderCell>API Key</Table.HeaderCell>
              <Table.HeaderCell>备注</Table.HeaderCell>
              <Table.HeaderCell>状态</Table.HeaderCell>
              <Table.HeaderCell>最近调用</Table.HeaderCell>
              <Table.HeaderCell>操作</Table.HeaderCell>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            {data.items.map((p) => (
              <Table.Row key={p.id}>
                <Table.Cell>
                  <div className="flex items-center gap-2.5">
                    <div
                      className={`w-8 h-8 rounded-[var(--radius-sm)] ${typeColors[p.provider_type] || defaultColor} border-2 border-[var(--color-text)] flex items-center justify-center text-white font-bold text-[13px] flex-shrink-0`}
                    >
                      {p.name.charAt(0)}
                    </div>
                    <span className="font-semibold">{p.name}</span>
                  </div>
                </Table.Cell>
                <Table.Cell>
                  <Tag variant={typeTagVariants[p.provider_type] || defaultTagVariant}>
                    {typeLabels[p.provider_type] || p.provider_type}
                  </Tag>
                </Table.Cell>
                <Table.Cell className="font-[var(--font-mono)] text-[13px] max-w-[220px] truncate">
                  {p.base_url}
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-2">
                    <span className="font-[var(--font-mono)] text-[13px]">
                      {showKeys[p.id] ? p.api_key : maskKey(p.api_key)}
                    </span>
                    <button
                      type="button"
                      onClick={() => toggleKey(p.id)}
                      className="text-[11px] font-medium text-[var(--color-primary)] cursor-pointer border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] px-2 py-0.5 bg-[var(--color-surface)] hover:border-[var(--color-primary)] transition-all duration-150"
                    >
                      {showKeys[p.id] ? "隐藏" : "显示"}
                    </button>
                  </div>
                </Table.Cell>
                <Table.Cell className="text-[13px] text-[var(--color-text-secondary)] max-w-[180px] truncate">
                  {p.note || "--"}
                </Table.Cell>
                <Table.Cell>
                  <Tag variant={p.is_active ? "success" : "warning"}>
                    {p.is_active ? "活跃" : "未激活"}
                  </Tag>
                </Table.Cell>
                <Table.Cell className="text-[12px] text-[var(--color-text-secondary)]">
                  {p.last_called_at ? formatDateTime(p.last_called_at) : "--"}
                </Table.Cell>
                <Table.Cell>
                  <div className="flex items-center gap-1">
{/* 测试按钮用原生 button 而非 <Button> 组件，因为需要在 loading 时保留文字可见（Button 的 loading 会隐藏文字） */}                    <button
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
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
          <Table.Footer
            total={data.total}
            page={page}
            pageSize={20}
            onPageChange={handlePageChange}
          />
        </Table>
      )}

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
          <Select
            label="类型"
            value={formType}
            onChange={setFormType}
            options={typeOptions}
          />
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
