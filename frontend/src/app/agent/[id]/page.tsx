export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">Agent 配置</h1>
      <p className="text-[var(--color-text-secondary)]">Agent #{id} — 编辑模型、工具和知识库绑定</p>
    </div>
  );
}
