"use client";

import { useState, useRef } from "react";
import DataTable, { type DataTableHandle } from "@/components/ui/DataTable";
import Table from "@/components/ui/Table";
import { Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import Modal from "@/components/ui/Modal";
import { showToast } from "@/components/ui/Toast";
import { useRequest } from "@/hooks/useRequest";
import { useConfirm } from "@/hooks/useConfirm";
import { get, getPage, post, put, del, BizError } from "@/lib/api";
import { getHealth, type HealthInfo } from "@/lib/health";
import { formatDateTime } from "@/lib/utils";

/* ── Types ──────────────────────────────────────────── */

interface AuthConfig {
  api_key?: string;
  client_id?: string;
  client_secret?: string;
  token_url?: string;
}

interface ProviderItem {
  id: string;
  name: string;
  provider_type: string;
  base_url: string;
  auth_type: string;
  auth_config: AuthConfig;
  note: string | null;
  is_active: boolean;
  last_called_at: string | null;
  health_status: string;
  last_health_check_at: string | null;
  consecutive_failures: number;
  last_error_message: string | null;
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

interface ProviderModelItem {
  id: string;
  provider_config_id: string;
  model_name: string;
  display_name: string | null;
  supports_chat: boolean;
  supports_embedding: boolean;
  supports_vision: boolean;
  max_tokens: number | null;
  default_temperature: number | null;
  input_cost_per_1k: number | null;
  output_cost_per_1k: number | null;
  is_enabled: boolean;
  sort_order: number;
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

const authTypeLabels: Record<string, string> = {
  bearer: "Bearer Token",
  api_key_header: "API Key Header",
  oauth_cc: "OAuth 2.0",
  none: "无鉴权",
};

const authTypeOptions = [
  { value: "bearer", label: "Bearer Token" },
  { value: "api_key_header", label: "API Key Header" },
  { value: "oauth_cc", label: "OAuth 2.0" },
  { value: "none", label: "无鉴权" },
];

const healthStatusLabels: Record<string, string> = {
  unknown: "未知",
  healthy: "健康",
  degraded: "降级",
  unhealthy: "异常",
};

const healthStatusVariants: Record<string, "success" | "warning" | "error" | "default"> = {
  unknown: "default",
  healthy: "success",
  degraded: "warning",
  unhealthy: "error",
};

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
  const [formAuthType, setFormAuthType] = useState("bearer");
  const [formApiKey, setFormApiKey] = useState("");
  const [formClientId, setFormClientId] = useState("");
  const [formClientSecret, setFormClientSecret] = useState("");
  const [formTokenUrl, setFormTokenUrl] = useState("");
  const [formNote, setFormNote] = useState("");
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [formSaving, setFormSaving] = useState(false);

  /* ── API Key view modal ─────────────────────────── */
  const [keyModal, setKeyModal] = useState<{
    open: boolean;
    providerName: string;
    keyType: string;
    keyValue: string;
  }>({ open: false, providerName: "", keyType: "", keyValue: "" });

  /* ── Model management state ──────────────────────── */

  const [modelModalProviderId, setModelModalProviderId] = useState<string | null>(null);
  const [modelModalProviderName, setModelModalProviderName] = useState("");
  const [models, setModels] = useState<ProviderModelItem[]>([]);
  const [modelsLoading, setModelsLoading] = useState(false);
  const [modelFormOpen, setModelFormOpen] = useState(false);
  const [modelEditData, setModelEditData] = useState<ProviderModelItem | null>(null);
  const [modelFormSaving, setModelFormSaving] = useState(false);
  const [modelDeletingId, setModelDeletingId] = useState<string | null>(null);

  /* Model form fields */
  const [mModelName, setMModelName] = useState("");
  const [mDisplayName, setMDisplayName] = useState("");
  const [mSupportsChat, setMSupportsChat] = useState(true);
  const [mSupportsEmbedding, setMSupportsEmbedding] = useState(false);
  const [mSupportsVision, setMSupportsVision] = useState(false);
  const [mMaxTokens, setMMaxTokens] = useState("");
  const [mTemperature, setMTemperature] = useState("");
  const [mIsEnabled, setMIsEnabled] = useState(true);
  const [mFormErrors, setMFormErrors] = useState<Record<string, string>>({});

  /* ── API Key helpers ───────────────────────────── */

  function maskKeyPreview(key: string): string {
    if (!key || key.length <= 8) return "****";
    return key.slice(0, 6) + "****" + key.slice(-4);
  }

  function viewFullKey(provider: ProviderItem) {
    const keyValue = provider.auth_config?.api_key
      || provider.auth_config?.client_secret
      || "";
    const keyType = provider.auth_config?.api_key
      ? "API Key"
      : provider.auth_config?.client_secret
        ? "Client Secret"
        : "鉴权密钥";
    setKeyModal({
      open: true,
      providerName: provider.name,
      keyType,
      keyValue,
    });
  }

  /* ── Provider form helpers ──────────────────────── */

  function resetAuthFields(type: string) {
    setFormAuthType(type);
    setFormApiKey("");
    setFormClientId("");
    setFormClientSecret("");
    setFormTokenUrl("");
  }

  function openCreate() {
    setEditData(null);
    setFormName("");
    setFormType("openai");
    setFormBaseUrl("");
    resetAuthFields("bearer");
    setFormNote("");
    setFormErrors({});
    setModalOpen(true);
  }

  function openEdit(p: ProviderItem) {
    setEditData(p);
    setFormName(p.name);
    setFormType(p.provider_type);
    setFormBaseUrl(p.base_url);
    const authType = p.auth_type || "bearer";
    setFormAuthType(authType);
    setFormApiKey(p.auth_config?.api_key || "");
    setFormClientId(p.auth_config?.client_id || "");
    setFormClientSecret(p.auth_config?.client_secret || "");
    setFormTokenUrl(p.auth_config?.token_url || "");
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

  function buildAuthConfig(): AuthConfig {
    switch (formAuthType) {
      case "bearer":
      case "api_key_header":
        return { api_key: formApiKey.trim() };
      case "oauth_cc":
        return {
          client_id: formClientId.trim(),
          client_secret: formClientSecret.trim(),
          token_url: formTokenUrl.trim(),
        };
      case "none":
        return {};
      default:
        return { api_key: formApiKey.trim() };
    }
  }

  function validate(): boolean {
    const errors: Record<string, string> = {};
    if (!formName.trim()) errors.name = "请输入名称";
    if (!formBaseUrl.trim()) errors.baseUrl = "请输入 Base URL";
    if (formAuthType === "bearer" || formAuthType === "api_key_header") {
      if (!editData && !formApiKey.trim()) errors.apiKey = "请输入 API Key";
    }
    if (formAuthType === "oauth_cc") {
      if (!editData && !formClientId.trim()) errors.clientId = "请输入 Client ID";
      if (!editData && !formClientSecret.trim()) errors.clientSecret = "请输入 Client Secret";
      if (!formTokenUrl.trim()) errors.tokenUrl = "请输入 Token URL";
    }
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleSave() {
    if (!validate()) return;
    setFormSaving(true);
    try {
      const authConfig = buildAuthConfig();
      if (editData) {
        const body: Record<string, unknown> = {
          name: formName.trim(),
          provider_type: formType,
          base_url: formBaseUrl.trim(),
          auth_type: formAuthType,
          auth_config: authConfig,
        };
        if (formNote.trim()) body.note = formNote.trim();
        await put(`/provider/configs/${editData.id}`, body);
        showToast("success", "提供商已更新");
      } else {
        await post("/provider/configs", {
          name: formName.trim(),
          provider_type: formType,
          base_url: formBaseUrl.trim(),
          auth_type: formAuthType,
          auth_config: authConfig,
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

  /* ── Model management ──────────────────────────── */

  async function openModelManager(p: ProviderItem) {
    setModelModalProviderId(p.id);
    setModelModalProviderName(p.name);
    setModelsLoading(true);
    try {
      const result = await get<ProviderModelItem[]>(`/provider/configs/${p.id}/models`);
      setModels(result || []);
    } catch {
      setModels([]);
    } finally {
      setModelsLoading(false);
    }
  }

  function openModelCreate() {
    setModelEditData(null);
    setMModelName("");
    setMDisplayName("");
    setMSupportsChat(true);
    setMSupportsEmbedding(false);
    setMSupportsVision(false);
    setMMaxTokens("");
    setMTemperature("");
    setMIsEnabled(true);
    setMFormErrors({});
    setModelFormOpen(true);
  }

  function openModelEdit(m: ProviderModelItem) {
    setModelEditData(m);
    setMModelName(m.model_name);
    setMDisplayName(m.display_name || "");
    setMSupportsChat(m.supports_chat);
    setMSupportsEmbedding(m.supports_embedding);
    setMSupportsVision(m.supports_vision);
    setMMaxTokens(m.max_tokens?.toString() || "");
    setMTemperature(m.default_temperature?.toString() || "");
    setMIsEnabled(m.is_enabled);
    setMFormErrors({});
    setModelFormOpen(true);
  }

  function clearModelError(field: string) {
    setMFormErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function validateModel(): boolean {
    const errors: Record<string, string> = {};
    if (!mModelName.trim()) errors.model_name = "请输入模型名称";
    if (mMaxTokens && (isNaN(Number(mMaxTokens)) || Number(mMaxTokens) < 1))
      errors.max_tokens = "请输入有效的整数";
    if (mTemperature && (isNaN(Number(mTemperature)) || Number(mTemperature) < 0 || Number(mTemperature) > 2))
      errors.default_temperature = "请输入 0-2 之间的数值";
    setMFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleModelSave() {
    if (!validateModel() || !modelModalProviderId) return;
    setModelFormSaving(true);
    try {
      const body: Record<string, unknown> = {
        model_name: mModelName.trim(),
        display_name: mDisplayName.trim() || null,
        supports_chat: mSupportsChat,
        supports_embedding: mSupportsEmbedding,
        supports_vision: mSupportsVision,
        max_tokens: mMaxTokens ? Number(mMaxTokens) : null,
        default_temperature: mTemperature ? Number(mTemperature) : null,
        is_enabled: mIsEnabled,
      };
      if (modelEditData) {
        await put(`/provider/configs/${modelModalProviderId}/models/${modelEditData.id}`, body);
        showToast("success", "模型已更新");
      } else {
        await post(`/provider/configs/${modelModalProviderId}/models`, body);
        showToast("success", "模型已添加");
      }
      setModelFormOpen(false);
      // Reload models
      const result = await get<ProviderModelItem[]>(`/provider/configs/${modelModalProviderId}/models`);
      setModels(result || []);
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "保存失败";
      showToast("error", msg);
    } finally {
      setModelFormSaving(false);
    }
  }

  async function handleModelDelete(model: ProviderModelItem) {
    if (!modelModalProviderId) return;
    setModelDeletingId(model.id);
    try {
      await del(`/provider/configs/${modelModalProviderId}/models/${model.id}`);
      showToast("success", `已删除 ${model.model_name}`);
      const result = await get<ProviderModelItem[]>(`/provider/configs/${modelModalProviderId}/models`);
      setModels(result || []);
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "删除失败";
      showToast("error", msg);
    } finally {
      setModelDeletingId(null);
    }
  }

  function formatTokenCount(n: number | null): string {
    if (!n) return "--";
    if (n >= 1000) return `${Math.round(n / 1000)}K`;
    return String(n);
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
      key: "auth_type",
      label: "鉴权方式",
      render: (p: ProviderItem) => (
        <Tag variant="default">{authTypeLabels[p.auth_type] || p.auth_type}</Tag>
      ),
    },
    {
      key: "api_key",
      label: "API Key",
      render: (p: ProviderItem) => {
        const rawKey = p.auth_config?.api_key || p.auth_config?.client_secret || p.auth_config?.client_id || "";
        if (!rawKey) return <span className="text-[var(--color-text-tertiary)] text-[13px]">--</span>;
        return (
          <div className="flex items-center gap-2">
            <span className="font-[var(--font-mono)] text-[13px] text-[var(--color-text-secondary)]">
              {maskKeyPreview(rawKey)}
            </span>
            <button
              type="button"
              onClick={(e) => { e.stopPropagation(); viewFullKey(p); }}
              className="whitespace-nowrap text-[11px] font-semibold text-[var(--color-primary)] cursor-pointer border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] px-2 py-0.5 bg-[var(--color-surface)] hover:border-[var(--color-primary)] transition-all duration-150 flex-shrink-0"
            >
              查看完整KEY
            </button>
          </div>
        );
      },
    },
    {
      key: "note",
      label: "备注",
      className: "text-[13px] text-[var(--color-text-secondary)] max-w-[180px] truncate",
      render: (p: ProviderItem) => p.note || "--",
    },
    {
      key: "is_active",
      label: "启用",
      render: (p: ProviderItem) => (
        <Tag variant={p.is_active ? "success" : "warning"}>
          {p.is_active ? "已启用" : "已停用"}
        </Tag>
      ),
    },
    {
      key: "health_status",
      label: "健康",
      render: (p: ProviderItem) => {
        const status = p.health_status || "unknown";
        const lastCheck = p.last_health_check_at
          ? formatDateTime(p.last_health_check_at)
          : "从未检测";
        const tooltipLines = [`最近检测: ${lastCheck}`];
        if (p.consecutive_failures > 0) tooltipLines.push(`连续失败: ${p.consecutive_failures} 次`);
        if (p.last_error_message) tooltipLines.push(`错误: ${p.last_error_message.slice(0, 100)}`);
        return (
          <span title={tooltipLines.join("\n")}>
            <Tag variant={healthStatusVariants[status] || "default"}>
              {healthStatusLabels[status] || status}
            </Tag>
          </span>
        );
      },
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
        <div className="flex items-center gap-1 whitespace-nowrap">
          <button
            type="button"
            disabled={testingId === p.id}
            onClick={() => handleTest(p)}
            className="whitespace-nowrap inline-flex items-center gap-2 px-3.5 py-1.5 text-[13px] font-semibold rounded-[var(--radius-md)] border-2 border-[var(--color-text)] bg-[var(--color-surface)] text-[var(--color-text)] shadow-[2px_2px_0_rgba(26,26,46,0.10)] transition-all duration-150 ease-out cursor-pointer hover:translate-x-[2px] hover:translate-y-[2px] hover:shadow-none active:scale-[0.98] disabled:opacity-60 disabled:pointer-events-none min-h-[36px]"
          >
            {testingId === p.id && (
              <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
            )}
            {testingId === p.id ? "测试中..." : "测试连接"}
          </button>
          <Button variant="ghost" size="sm" onClick={() => openModelManager(p)}>
            模型
          </Button>
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
          <Select
            label="鉴权方式"
            value={formAuthType}
            onChange={(v) => resetAuthFields(v)}
            options={authTypeOptions}
          />
          {/* Bearer / API Key Header */}
          {(formAuthType === "bearer" || formAuthType === "api_key_header") && (
            <Input
              label="API Key"
              required={!editData}
              type="password"
              placeholder={editData ? "留空表示不修改" : "sk-..."}
              value={formApiKey}
              error={formErrors.apiKey}
              onChange={(e) => { setFormApiKey(e.target.value); clearError("apiKey"); }}
            />
          )}
          {/* OAuth 2.0 Client Credentials */}
          {formAuthType === "oauth_cc" && (
            <>
              <Input
                label="Client ID"
                required={!editData}
                placeholder="your-client-id"
                value={formClientId}
                error={formErrors.clientId}
                onChange={(e) => { setFormClientId(e.target.value); clearError("clientId"); }}
              />
              <Input
                label="Client Secret"
                required={!editData}
                type="password"
                placeholder={editData ? "留空表示不修改" : "your-client-secret"}
                value={formClientSecret}
                error={formErrors.clientSecret}
                onChange={(e) => { setFormClientSecret(e.target.value); clearError("clientSecret"); }}
              />
              <Input
                label="Token URL"
                required
                placeholder="https://auth.example.com/oauth/token"
                value={formTokenUrl}
                error={formErrors.tokenUrl}
                onChange={(e) => { setFormTokenUrl(e.target.value); clearError("tokenUrl"); }}
              />
            </>
          )}
          {/* none — 无需鉴权字段 */}
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

      {/* Model manager modal */}
      <Modal
        open={modelModalProviderId !== null}
        onClose={() => setModelModalProviderId(null)}
        title={`模型管理 — ${modelModalProviderName}`}
        footer={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setModelModalProviderId(null)}
          >
            关闭
          </Button>
        }
      >
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-[13px] text-[var(--color-text-secondary)]">
              管理该供应商下的可用模型配置
            </p>
            <Button variant="primary" size="sm" onClick={openModelCreate}>
              + 新增模型
            </Button>
          </div>
          {modelsLoading ? (
            <div className="text-center py-8 text-[var(--color-text-tertiary)]">加载中...</div>
          ) : models.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-[var(--color-text-secondary)] mb-3">该供应商下暂无模型</p>
              <Button variant="primary" size="sm" onClick={openModelCreate}>
                新增模型
              </Button>
            </div>
          ) : (
            <Table>
              <Table.Head>
                <Table.Row>
                  <Table.HeaderCell>模型名称</Table.HeaderCell>
                  <Table.HeaderCell>展示名</Table.HeaderCell>
                  <Table.HeaderCell>能力</Table.HeaderCell>
                  <Table.HeaderCell>上下文</Table.HeaderCell>
                  <Table.HeaderCell>温度</Table.HeaderCell>
                  <Table.HeaderCell>状态</Table.HeaderCell>
                  <Table.HeaderCell>操作</Table.HeaderCell>
                </Table.Row>
              </Table.Head>
              <Table.Body>
                {models.map((m) => (
                  <Table.Row key={m.id}>
                    <Table.Cell>
                      <span className="font-semibold font-[var(--font-mono)] text-[13px]">{m.model_name}</span>
                    </Table.Cell>
                    <Table.Cell className="text-[13px] text-[var(--color-text-secondary)]">
                      {m.display_name || "--"}
                    </Table.Cell>
                    <Table.Cell>
                      <div className="flex items-center gap-1">
                        {m.supports_chat && <Tag variant="primary">Chat</Tag>}
                        {m.supports_embedding && <Tag variant="info">Embed</Tag>}
                        {m.supports_vision && <Tag variant="default">Vision</Tag>}
                        {!m.supports_chat && !m.supports_embedding && !m.supports_vision && (
                          <span className="text-[12px] text-[var(--color-text-tertiary)]">--</span>
                        )}
                      </div>
                    </Table.Cell>
                    <Table.Cell className="text-[13px] font-[var(--font-mono)]">
                      {formatTokenCount(m.max_tokens)}
                    </Table.Cell>
                    <Table.Cell className="text-[13px] font-[var(--font-mono)]">
                      {m.default_temperature?.toFixed(1) ?? "--"}
                    </Table.Cell>
                    <Table.Cell>
                      <Tag variant={m.is_enabled ? "success" : "warning"}>
                        {m.is_enabled ? "启用" : "禁用"}
                      </Tag>
                    </Table.Cell>
                    <Table.Cell>
                      <div className="flex items-center gap-1 whitespace-nowrap">
                        <Button variant="ghost" size="sm" onClick={() => openModelEdit(m)}>
                          编辑
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="!text-[var(--color-error)]"
                          disabled={modelDeletingId === m.id}
                          onClick={() => handleModelDelete(m)}
                        >
                          {modelDeletingId === m.id ? "删除中..." : "删除"}
                        </Button>
                      </div>
                    </Table.Cell>
                  </Table.Row>
                ))}
              </Table.Body>
            </Table>
          )}
        </div>
      </Modal>

      {/* Model create / edit modal */}
      <Modal
        open={modelFormOpen}
        onClose={() => setModelFormOpen(false)}
        title={modelEditData ? "编辑模型" : "新增模型"}
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setModelFormOpen(false)}>
              取消
            </Button>
            <Button variant="primary" size="sm" loading={modelFormSaving} onClick={handleModelSave}>
              保存
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-1">
          <Input
            label="模型名称"
            required
            placeholder="gpt-4o"
            value={mModelName}
            error={mFormErrors.model_name}
            onChange={(e) => { setMModelName(e.target.value); clearModelError("model_name"); }}
          />
          <Input
            label="展示名称"
            placeholder="可选：用户可见的别名"
            value={mDisplayName}
            onChange={(e) => setMDisplayName(e.target.value)}
          />
          <div className="flex flex-col gap-1.5 mt-1">
            <label className="text-[13px] font-semibold text-[var(--color-text)]">能力</label>
            <div className="flex items-center gap-4">
              <label className="flex items-center gap-1.5 text-[13px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={mSupportsChat}
                  onChange={(e) => setMSupportsChat(e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-[var(--color-border)] accent-[var(--color-primary)]"
                />
                对话 Chat
              </label>
              <label className="flex items-center gap-1.5 text-[13px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={mSupportsEmbedding}
                  onChange={(e) => setMSupportsEmbedding(e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-[var(--color-border)] accent-[var(--color-primary)]"
                />
                嵌入 Embedding
              </label>
              <label className="flex items-center gap-1.5 text-[13px] cursor-pointer">
                <input
                  type="checkbox"
                  checked={mSupportsVision}
                  onChange={(e) => setMSupportsVision(e.target.checked)}
                  className="w-4 h-4 rounded border-2 border-[var(--color-border)] accent-[var(--color-primary)]"
                />
                视觉 Vision
              </label>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3 mt-1">
            <Input
              label="上下文窗口"
              type="number"
              placeholder="如 128000"
              value={mMaxTokens}
              error={mFormErrors.max_tokens}
              onChange={(e) => { setMMaxTokens(e.target.value); clearModelError("max_tokens"); }}
            />
            <Input
              label="默认温度"
              type="number"
              placeholder="0.0 - 2.0"
              value={mTemperature}
              error={mFormErrors.default_temperature}
              onChange={(e) => { setMTemperature(e.target.value); clearModelError("default_temperature"); }}
            />
          </div>
          <div className="flex items-center gap-3 mt-1">
            <label className="text-[13px] font-semibold text-[var(--color-text)]">启用</label>
            <label className="flex items-center gap-1.5 text-[13px] cursor-pointer">
              <input
                type="checkbox"
                checked={mIsEnabled}
                onChange={(e) => setMIsEnabled(e.target.checked)}
                className="w-4 h-4 rounded border-2 border-[var(--color-border)] accent-[var(--color-primary)]"
              />
              启用此模型
            </label>
          </div>
        </div>
      </Modal>

      {/* API Key viewer modal */}
      <Modal
        open={keyModal.open}
        onClose={() => setKeyModal((prev) => ({ ...prev, open: false }))}
        title="查看完整密钥"
        footer={
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setKeyModal((prev) => ({ ...prev, open: false }))}
          >
            关闭
          </Button>
        }
      >
        <div className="space-y-4">
          <div>
            <span className="text-[var(--color-text-secondary)] text-[13px]">提供商</span>
            <p className="font-semibold mt-0.5">{keyModal.providerName}</p>
          </div>
          <div>
            <span className="text-[var(--color-text-secondary)] text-[13px]">密钥类型</span>
            <p className="font-semibold mt-0.5">{keyModal.keyType}</p>
          </div>
          <div>
            <span className="text-[var(--color-text-secondary)] text-[13px]">完整密钥</span>
            <div className="mt-1.5 p-3 rounded-[var(--radius-sm)] bg-[var(--color-bg)] border-2 border-[var(--color-border)] font-[var(--font-mono)] text-[13px] break-all select-all">
              {keyModal.keyValue}
            </div>
            <p className="text-[11px] text-[var(--color-text-tertiary)] mt-1.5">
              密钥仅在创建/编辑时可修改，此处仅供查看
            </p>
          </div>
        </div>
      </Modal>
    </div>
  );
}
