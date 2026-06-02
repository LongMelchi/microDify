export default async function WorkflowEditorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">工作流编辑器</h1>
      <p className="text-[var(--color-text-secondary)]">Workflow #{id} — 可视化编排工作流节点和连线</p>
    </div>
  );
}
