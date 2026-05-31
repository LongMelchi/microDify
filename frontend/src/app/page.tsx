import Link from "next/link";

/**
 * Dashboard home page.
 * TODO: replace with real metrics and navigation tiles.
 */
export default function DashboardPage() {
  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="mb-8 text-3xl font-bold">microDify</h1>
      <p className="mb-8 text-gray-600">
        Welcome to microDify, your lightweight AI Agent platform.
      </p>

      <nav className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        <NavCard href="/chat" label="Chat Apps" />
        <NavCard href="/agent" label="Agents" />
        <NavCard href="/knowledge" label="Knowledge Bases" />
        <NavCard href="/workflow" label="Workflows" />
        <NavCard href="/prompt" label="Prompt Templates" />
        <NavCard href="/settings" label="Settings" />
      </nav>
    </div>
  );
}

function NavCard({ href, label }: { href: string; label: string }) {
  return (
    <Link
      href={href}
      className="rounded-lg border bg-white p-6 shadow-sm transition hover:shadow-md"
    >
      <h2 className="text-lg font-semibold">{label}</h2>
      <p className="mt-1 text-sm text-gray-500">
        Manage your {label.toLowerCase()}
      </p>
    </Link>
  );
}
