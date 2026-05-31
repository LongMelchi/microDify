/**
 * Chat conversation page.
 * TODO: render the conversation interface with message list and SSE streaming input.
 */
export default async function ChatConversationPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  return (
    <div className="mx-auto flex h-screen max-w-4xl flex-col px-4 py-6">
      <h1 className="mb-4 text-xl font-bold">Chat #{id}</h1>
      <div className="flex-1 rounded-lg border bg-white p-4">
        <p className="text-gray-400 text-center mt-20">
          Conversation messages will appear here.
        </p>
      </div>
      {/* TODO: message input bar */}
    </div>
  );
}
