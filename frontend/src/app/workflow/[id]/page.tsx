/**
 * Workflow editor page.
 * TODO: render a visual workflow editor (node graph, connections, property panel).
 */
export default async function WorkflowEditorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="flex h-screen flex-col">
      <header className="flex items-center justify-between border-b px-4 py-3">
        <h1 className="text-lg font-bold">Workflow #{id}</h1>
      </header>
      <div className="flex flex-1 items-center justify-center bg-gray-100 text-gray-400">
        Visual workflow editor will be rendered here.
      </div>
    </div>
  );
}
