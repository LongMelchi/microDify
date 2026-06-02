export default async function ChatConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return (
    <div>
      <h1 className="text-2xl font-bold mb-2">对话详情</h1>
      <p className="text-[var(--color-text-secondary)]">Chat #{id} — 与 AI 进行流式对话</p>
    </div>
  );
}
