/**
 * Knowledge base detail page.
 * TODO: show knowledge base info, document list with upload/delete, chunk preview.
 */
export default async function KnowledgeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <h1 className="mb-6 text-2xl font-bold">Knowledge Base #{id}</h1>
      <p className="text-gray-500">
        Document list and upload interface will be rendered here.
      </p>
    </div>
  );
}
