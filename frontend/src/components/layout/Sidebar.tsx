"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const MENU_ITEMS = [
  { href: "/chat", label: "对话" },
  { href: "/agent", label: "Agent" },
  { href: "/knowledge", label: "知识库" },
  { href: "/workflow", label: "工作流" },
  { href: "/prompt", label: "Prompt" },
  { href: "/provider", label: "模型管理" },
  { href: "/settings", label: "设置" },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="w-56 bg-gray-900 text-white min-h-screen flex flex-col">
      {/* Brand */}
      <div className="px-5 py-5 text-lg font-bold tracking-wide border-b border-gray-700">
        microDify
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3">
        {MENU_ITEMS.map((item) => {
          const isActive =
            pathname === item.href || pathname.startsWith(item.href + "/");
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`block px-5 py-2.5 text-sm transition-colors ${
                isActive
                  ? "bg-gray-700 text-white font-medium border-l-3 border-blue-400"
                  : "text-gray-300 hover:bg-gray-800 hover:text-white"
              }`}
            >
              {item.label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
