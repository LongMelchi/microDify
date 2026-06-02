"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const MENU_ITEMS = [
  { href: "/", label: "仪表盘" },
  { href: "/chat", label: "对话" },
  { href: "/agent", label: "Agent" },
  { href: "/knowledge", label: "知识库" },
  { href: "/workflow", label: "工作流" },
  { href: "/prompt", label: "Prompt" },
  { href: "/provider", label: "模型管理" },
  { href: "/users", label: "用户管理" },
  { href: "/settings", label: "设置" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-[220px] min-w-[220px] bg-[var(--color-sidebar)] text-white sticky top-0 h-screen overflow-y-auto flex flex-col">
      {/* Brand */}
      <div className="px-5 py-5 border-b border-[rgba(255,255,255,0.1)]">
        <Link href="/" className="text-lg font-bold tracking-tight text-white no-underline">
          microDify
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3">
        {MENU_ITEMS.map((item) => {
          const isActive =
            item.href === "/"
              ? pathname === "/"
              : pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-5 py-2 text-[13px] font-medium transition-all duration-150 ease-out border-l-[3px] border-transparent
                ${
                  isActive
                    ? "bg-[rgba(91,95,227,0.2)] text-white border-l-[var(--color-primary)]"
                    : "text-[rgba(255,255,255,0.65)] hover:text-white hover:bg-[var(--color-sidebar-hover)]"
                }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>

      {/* Footer user area — elevated from sidebar via lighter bg + stronger divider */}
      <div className="mt-auto bg-[var(--color-sidebar-hover)] border-t-2 border-[rgba(255,255,255,0.12)]">
        <div className="px-5 py-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-[var(--radius-sm)] bg-[var(--color-primary)] border-2 border-[var(--color-text)] flex items-center justify-center text-white font-bold text-[13px] flex-shrink-0">
            A
          </div>
          <div className="min-w-0">
            <p className="text-[13px] font-semibold leading-tight truncate">admin</p>
            <p className="text-[11px] text-[rgba(255,255,255,0.5)] leading-tight mt-0.5">管理员</p>
          </div>
        </div>
      </div>
    </aside>
  );
}
