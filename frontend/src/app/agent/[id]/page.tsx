/**
 * Agent detail / config page.
 * TODO: render agent config form (system prompt, model selection, tool toggles, knowledge bindings).
 */
export default async function AgentDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="mb-6 text-2xl font-bold">Agent #{id}</h1>
      <p className="text-gray-500">
        Agent configuration form will be rendered here.
      </p>
    </div>
  );
}
