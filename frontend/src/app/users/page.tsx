"use client";

import { useState, useRef } from "react";
import Table from "@/components/ui/Table";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Input";
import Button from "@/components/ui/Button";
import Tag from "@/components/ui/Tag";
import Modal from "@/components/ui/Modal";
import Skeleton from "@/components/ui/Skeleton";
import { showToast } from "@/components/ui/Toast";
import { useRequest } from "@/hooks/useRequest";
import { useConfirm } from "@/hooks/useConfirm";
import { get, post, put, del, BizError } from "@/lib/api";

/* ── Types ──────────────────────────────────────────── */

interface UserItem {
  id: string;
  username: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

interface UserListData {
  items: UserItem[];
  total: number;
}

/* ── Helpers ────────────────────────────────────────── */

const avatarColors = [
  "bg-[var(--color-primary)]",
  "bg-[var(--color-secondary)]",
  "bg-[var(--color-accent)]",
];

function formatDate(iso: string): string {
  try {
    const d = new Date(iso);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  } catch {
    return iso;
  }
}

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
  /* ── Filter state ───────────────────────────────── */

  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [page, setPage] = useState(1);
  const pageRef = useRef(page);
  pageRef.current = page;

  /* ── Data fetching ──────────────────────────────── */

  const fetchUsers = () => {
    const params: Record<string, string> = { page: String(pageRef.current), pageSize: "20" };
    const s = search.trim();
    if (s) { params.email = s; params.username = s; }
    if (statusFilter !== "all") params.status = statusFilter;
    return get<UserListData>("/auth/users", params);
  };

  const { data, loading, error, execute } = useRequest<UserListData>(fetchUsers);

  /* ── Search ─────────────────────────────────────── */

  function handleSearch() {
    setPage(1);
    pageRef.current = 1;
    execute();
  }

  function handleSearchKeyDown(e: React.KeyboardEvent) {
    if (e.key === "Enter") handleSearch();
  }

  /* ── Status filter ──────────────────────────────── */

  function handleStatusChange(val: string) {
    setStatusFilter(val);
    setPage(1);
    pageRef.current = 1;
    execute();
  }

  /* ── Pagination ─────────────────────────────────── */

  function handlePageChange(p: number) {
    setPage(p);
    pageRef.current = p;
    execute();
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

  const { confirm, ConfirmationDialog } = useConfirm();

  /* ── Create handlers ────────────────────────────── */

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
      execute();
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

  /* ── Edit handlers ──────────────────────────────── */

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
      execute();
    } catch (err) {
      const msg = err instanceof BizError ? err.message : "更新失败";
      showToast("error", msg);
    } finally {
      setEditLoading(false);
    }
  }

  /* ── Delete handler ─────────────────────────────── */

  async function handleDelete(user: UserItem) {
    const ok = await confirm(() => del(`/auth/users/${user.id}`));
    if (ok) {
      showToast("success", `已删除用户 ${user.username}`);
      execute();
    }
  }

  /* ── Render: loading ────────────────────────────── */

  if (loading) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-6">用户管理</h1>
        <Skeleton.Table rows={5} />
      </div>
    );
  }

  /* ── Render: error ──────────────────────────────── */

  if (error) {
    return (
      <div>
        <h1 className="text-2xl font-bold mb-6">用户管理</h1>
        <div className="bg-[var(--color-surface)] border-[3px] border-[var(--color-text)] rounded-[var(--radius-lg)] shadow-[4px_4px_0_rgba(26,26,46,0.10)] p-12 text-center">
          <p className="text-[var(--color-error)] font-medium mb-4">{error}</p>
          <Button variant="secondary" size="sm" onClick={execute}>
            重试
          </Button>
        </div>
      </div>
    );
  }

  /* ── Render: list ───────────────────────────────── */

  const users = data?.items || [];
  const total = data?.total || 0;

  const roleMap: Record<string, { label: string; variant: "primary" | "info" | "default" }> = {
    admin: { label: "管理员", variant: "primary" },
    developer: { label: "开发者", variant: "info" },
    viewer: { label: "查看者", variant: "default" },
  };

  const statusMap: Record<string, { label: string; variant: "success" | "warning" }> = {
    active: { label: "活跃", variant: "success" },
    inactive: { label: "未激活", variant: "warning" },
  };

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
              onChange={handleStatusChange}
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

      {/* User table */}
      {users.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-[var(--color-bg)] border-[3px] border-[var(--color-border)] flex items-center justify-center text-2xl text-[var(--color-text-tertiary)]">
            👤
          </div>
          <h3 className="text-base font-semibold mb-2">暂无用户</h3>
          <p className="text-[var(--color-text-secondary)] mb-5">
            还没有任何用户账号，点击上方按钮创建第一个用户
          </p>
          <Button variant="primary" size="sm" onClick={openCreate}>
            新建用户
          </Button>
        </div>
      ) : (
        <Table>
          <Table.Head>
            <Table.Row>
              <Table.HeaderCell>用户</Table.HeaderCell>
              <Table.HeaderCell>邮箱</Table.HeaderCell>
              <Table.HeaderCell>角色</Table.HeaderCell>
              <Table.HeaderCell>状态</Table.HeaderCell>
              <Table.HeaderCell>创建时间</Table.HeaderCell>
              <Table.HeaderCell>操作</Table.HeaderCell>
            </Table.Row>
          </Table.Head>
          <Table.Body>
            {users.map((user, i) => {
              const role = roleMap[user.role] || roleMap.developer;
              const status = statusMap[user.status] || statusMap.inactive;
              return (
                <Table.Row key={user.id}>
                  <Table.Cell>
                    <div className="flex items-center gap-2.5">
                      <div
                        className={`w-8 h-8 rounded-[var(--radius-sm)] ${avatarColors[i % 3]} border-2 border-[var(--color-text)] flex items-center justify-center text-white font-bold text-[13px] flex-shrink-0`}
                      >
                        {user.username.charAt(0).toUpperCase()}
                      </div>
                      <span className="font-semibold">{user.username}</span>
                    </div>
                  </Table.Cell>
                  <Table.Cell className="font-[var(--font-mono)] text-[13px]">
                    {user.email}
                  </Table.Cell>
                  <Table.Cell>
                    <Tag variant={role.variant}>{role.label}</Tag>
                  </Table.Cell>
                  <Table.Cell>
                    <Tag variant={status.variant}>{status.label}</Tag>
                  </Table.Cell>
                  <Table.Cell className="text-[12px] text-[var(--color-text-secondary)]">
                    {formatDate(user.created_at)}
                  </Table.Cell>
                  <Table.Cell>
                    <div className="flex items-center gap-1">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => openEdit(user)}
                      >
                        编辑
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="!text-[var(--color-error)]"
                        onClick={() => handleDelete(user)}
                      >
                        删除
                      </Button>
                    </div>
                  </Table.Cell>
                </Table.Row>
              );
            })}
          </Table.Body>
          <Table.Footer total={total} page={page} onPageChange={handlePageChange} />
        </Table>
      )}

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
