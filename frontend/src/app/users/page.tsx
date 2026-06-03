"use client";

import { useState, useRef, useMemo } from "react";
import DataTable, { type DataTableHandle } from "@/components/ui/DataTable";
import { Input, Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import Modal from "@/components/ui/Modal";
import { showToast } from "@/components/ui/Toast";
import { useConfirm } from "@/hooks/useConfirm";
import { getPage, post, put, del, BizError } from "@/lib/api";
import { formatDate } from "@/lib/utils";

/* ── Types ──────────────────────────────────────────── */

interface UserItem {
  id: string;
  username: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

/* ── Helpers ────────────────────────────────────────── */

const avatarColors = [
  "bg-[var(--color-primary)]",
  "bg-[var(--color-secondary)]",
  "bg-[var(--color-accent)]",
];

function avatarColor(name: string): string {
  const code = name.charCodeAt(0) || 0;
  return avatarColors[code % avatarColors.length];
}

const roleMap: Record<string, { label: string; variant: "primary" | "info" | "default" }> = {
  admin: { label: "管理员", variant: "primary" },
  developer: { label: "开发者", variant: "info" },
  viewer: { label: "查看者", variant: "default" },
};

const statusMap: Record<string, { label: string; variant: "success" | "warning" }> = {
  active: { label: "活跃", variant: "success" },
  inactive: { label: "未激活", variant: "warning" },
};

function validateField(field: string, value: string): string | undefined {
  if (field === "username") {
    if (!value.trim() || value.trim().length < 2) return "用户名至少 2 个字符";
  }
  if (field === "email") {
    if (!value.trim()) return "请输入邮箱地址";
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim())) return "请输入有效的邮箱地址";
  }
  if (field === "password") {
    if (value.length < 8) return "密码至少 8 个字符";
  }
  return undefined;
}

/* ── Component ──────────────────────────────────────── */

export default function UsersPage() {
  const tableRef = useRef<DataTableHandle>(null);
  const { confirm, ConfirmationDialog } = useConfirm();

  /* ── Filters ────────────────────────────────────── */

  const [search, setSearch] = useState("");
  const [appliedSearch, setAppliedSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  const params = useMemo(() => {
    const p: Record<string, string> = {};
    if (appliedSearch) {
      p.email = appliedSearch;
      p.username = appliedSearch;
    }
    if (statusFilter !== "all") p.status = statusFilter;
    return p;
  }, [appliedSearch, statusFilter]);

  const fetchUsers = (args: { page: number; pageSize: number; params: Record<string, string> }) =>
    getPage<UserItem>("/auth/users", {
      page: String(args.page),
      pageSize: String(args.pageSize),
      ...args.params,
    });

  function handleSearch() {
    setAppliedSearch(search.trim());
  }

  function handleSearchKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") handleSearch();
  }

  /* ── Create user modal ──────────────────────────── */

  const [createOpen, setCreateOpen] = useState(false);
  const [formUsername, setFormUsername] = useState("");
  const [formEmail, setFormEmail] = useState("");
  const [formPassword, setFormPassword] = useState("");
  const [formConfirmPassword, setFormConfirmPassword] = useState("");
  const [formLoading, setFormLoading] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  /* ── Edit user modal ────────────────────────────── */

  const [editOpen, setEditOpen] = useState(false);
  const [editUser, setEditUser] = useState<UserItem | null>(null);
  const [editUsername, setEditUsername] = useState("");
  const [editStatus, setEditStatus] = useState("active");
  const [editLoading, setEditLoading] = useState(false);

  function openCreate() {
    setFormUsername("");
    setFormEmail("");
    setFormPassword("");
    setFormConfirmPassword("");
    setFormErrors({});
    setCreateOpen(true);
  }

  function blurCreateField(field: string) {
    let err: string | undefined;
    if (field === "confirmPassword") {
      err = formPassword !== formConfirmPassword ? "两次密码输入不一致" : undefined;
    } else {
      const val = field === "username" ? formUsername : field === "email" ? formEmail : formPassword;
      err = validateField(field, val);
    }
    setFormErrors((prev) => (prev[field] === err ? prev : { ...prev, [field]: err || "" }));
  }

  function clearFormError(field: string) {
    setFormErrors((prev) => {
      if (!prev[field]) return prev;
      const next = { ...prev };
      delete next[field];
      return next;
    });
  }

  function validateCreateForm(): boolean {
    const errors: Record<string, string> = {};
    const ue = validateField("username", formUsername);
    const ee = validateField("email", formEmail);
    const pe = validateField("password", formPassword);
    const ce = formPassword !== formConfirmPassword ? "两次密码输入不一致" : undefined;
    if (ue) errors.username = ue;
    if (ee) errors.email = ee;
    if (pe) errors.password = pe;
    if (ce) errors.confirmPassword = ce;
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  }

  async function handleCreate() {
    if (!validateCreateForm()) return;
    setFormLoading(true);
    try {
      await post("/auth/register", {
        username: formUsername.trim(),
        email: formEmail.trim(),
        password: formPassword,
      });
      showToast("success", `用户 ${formUsername} 创建成功`);
      setCreateOpen(false);
      tableRef.current?.refresh();
    } catch (err) {
      if (err instanceof BizError) {
        setFormErrors((prev) => ({ ...prev, email: err.message }));
      } else {
        showToast("error", "创建失败，请稍后重试");
      }
    } finally {
      setFormLoading(false);
    }
  }

  function openEdit(user: UserItem) {
    setEditUser(user);
    setEditUsername(user.username);
    setEditStatus(user.status);
    setEditOpen(true);
  }

  async function handleEdit() {
    if (!editUser) return;
    if (!editUsername.trim() || editUsername.trim().length < 2) {
      showToast("warning", "用户名至少 2 个字符");
      return;
    }
    setEditLoading(true);
    try {
      await put(`/auth/users/${editUser.id}`, {
        username: editUsername.trim(),
        status: editStatus,
      });
      showToast("success", "用户信息已更新");
      setEditOpen(false);
      tableRef.current?.refresh();
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "更新失败";
      showToast("error", msg);
    } finally {
      setEditLoading(false);
    }
  }

  async function handleDelete(user: UserItem) {
    const ok = await confirm(() => del(`/auth/users/${user.id}`));
    if (ok) {
      showToast("success", `已删除用户 ${user.username}`);
      tableRef.current?.refresh();
    }
  }

  /* ── Columns ────────────────────────────────────── */

  const columns = [
    {
      key: "username",
      label: "用户",
      render: (u: UserItem) => (
        <div className="flex items-center gap-2.5">
          <div
            className={`w-8 h-8 rounded-[var(--radius-sm)] ${avatarColor(u.username)} border-2 border-[var(--color-text)] flex items-center justify-center text-white font-bold text-[13px] flex-shrink-0`}
          >
            {u.username.charAt(0).toUpperCase()}
          </div>
          <span className="font-semibold">{u.username}</span>
        </div>
      ),
    },
    {
      key: "email",
      label: "邮箱",
      className: "font-[var(--font-mono)] text-[13px]",
      render: (u: UserItem) => u.email,
    },
    {
      key: "role",
      label: "角色",
      render: (u: UserItem) => {
        const r = roleMap[u.role] || roleMap.developer;
        return <Tag variant={r.variant}>{r.label}</Tag>;
      },
    },
    {
      key: "status",
      label: "状态",
      render: (u: UserItem) => {
        const s = statusMap[u.status] || statusMap.inactive;
        return <Tag variant={s.variant}>{s.label}</Tag>;
      },
    },
    {
      key: "created_at",
      label: "创建时间",
      className: "text-[12px] text-[var(--color-text-secondary)]",
      render: (u: UserItem) => formatDate(u.created_at),
    },
    {
      key: "actions",
      label: "操作",
      render: (u: UserItem) => (
        <div className="flex items-center gap-1">
          <Button variant="ghost" size="sm" onClick={() => openEdit(u)}>
            编辑
          </Button>
          <Button
            variant="ghost"
            size="sm"
            className="!text-[var(--color-error)]"
            onClick={() => handleDelete(u)}
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
      <h1 className="text-2xl font-bold mb-2">用户管理</h1>
      <p className="text-[var(--color-text-secondary)] mb-6">
        管理系统用户、分配角色和权限
      </p>

      {/* Toolbar */}
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div style={{ width: 140 }}>
            <Select
              value={statusFilter}
              onChange={setStatusFilter}
              options={[
                { value: "all", label: "全部状态" },
                { value: "active", label: "活跃" },
                { value: "inactive", label: "未激活" },
              ]}
              className="!mb-0"
            />
          </div>
          <input
            type="text"
            placeholder="搜索用户名或邮箱..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={handleSearchKeyDown}
            className="w-[220px] px-3.5 py-2.5 text-[14px] font-sans border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-surface)] text-[var(--color-text)] min-h-[44px] placeholder:text-[var(--color-text-tertiary)] outline-none focus:border-[var(--color-primary)] focus:shadow-[0_0_0_3px_var(--color-primary-light)] transition-all duration-150"
          />
          <Button variant="secondary" size="sm" onClick={handleSearch}>
            搜索
          </Button>
        </div>
        <Button variant="primary" size="sm" onClick={openCreate}>
          + 新建用户
        </Button>
      </div>

      <DataTable<UserItem>
        ref={tableRef}
        columns={columns}
        fetchData={fetchUsers}
        params={params}
        emptyIcon="👤"
        emptyTitle="暂无用户"
        emptyDesc="还没有任何用户账号，点击下方按钮创建第一个用户"
        emptyActionLabel="新建用户"
        onEmptyAction={openCreate}
      />

      {/* Create user modal */}
      <Modal
        open={createOpen}
        onClose={() => setCreateOpen(false)}
        title="创建新用户"
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setCreateOpen(false)}>
              取消
            </Button>
            <Button variant="primary" size="sm" loading={formLoading} onClick={handleCreate}>
              创建用户
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-1">
          <Input label="用户名" required placeholder="2-50 个字符" value={formUsername} error={formErrors.username} onChange={(e) => { setFormUsername(e.target.value); clearFormError("username"); }} onBlur={() => blurCreateField("username")} />
          <Input label="邮箱地址" required placeholder="user@microdify.local" value={formEmail} error={formErrors.email} onChange={(e) => { setFormEmail(e.target.value); clearFormError("email"); }} onBlur={() => blurCreateField("email")} />
          <Input label="初始密码" required type="password" placeholder="至少 8 个字符" value={formPassword} error={formErrors.password} onChange={(e) => { setFormPassword(e.target.value); clearFormError("password"); if (e.target.value === formConfirmPassword) clearFormError("confirmPassword"); }} onBlur={() => blurCreateField("password")} />
          <Input label="确认密码" required type="password" placeholder="再次输入密码" value={formConfirmPassword} error={formErrors.confirmPassword} onChange={(e) => { setFormConfirmPassword(e.target.value); if (e.target.value === formPassword) clearFormError("confirmPassword"); }} onBlur={() => blurCreateField("confirmPassword")} />
        </div>
      </Modal>

      {/* Edit user modal */}
      <Modal
        open={editOpen}
        onClose={() => setEditOpen(false)}
        title="编辑用户"
        footer={
          <>
            <Button variant="secondary" size="sm" onClick={() => setEditOpen(false)}>
              取消
            </Button>
            <Button variant="primary" size="sm" loading={editLoading} onClick={handleEdit}>
              保存
            </Button>
          </>
        }
      >
        <div className="flex flex-col gap-1">
          <Input
            label="用户名"
            required
            value={editUsername}
            onChange={(e) => setEditUsername(e.target.value)}
          />
          <div className="mb-5 max-w-[480px]">
            <label className="block text-[14px] font-semibold mb-2">邮箱地址</label>
            <input
              type="text"
              disabled
              value={editUser?.email || ""}
              className="w-full px-3.5 py-2.5 text-[14px] font-sans border-2 border-[var(--color-border)] rounded-[var(--radius-sm)] bg-[var(--color-bg)] text-[var(--color-text-tertiary)] min-h-[44px] cursor-not-allowed"
            />
            <p className="text-[12px] text-[var(--color-text-tertiary)] mt-1">邮箱不可修改</p>
          </div>
          <Select
            label="状态"
            value={editStatus}
            onChange={setEditStatus}
            options={[
              { value: "active", label: "活跃" },
              { value: "inactive", label: "未激活" },
            ]}
          />
        </div>
      </Modal>

      {ConfirmationDialog}
    </div>
  );
}
