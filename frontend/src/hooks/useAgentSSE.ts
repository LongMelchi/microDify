"use client";

/**
 * Agent-specific SSE hook — streams ReAct reasoning steps alongside final answer.
 * TODO: extend useSSE to parse structured agent events (thinking, tool_call, observation, answer).
 */
export function useAgentSSE() {
  // TODO: implement agent SSE logic with ReAct step parsing
  return {
    isConnected: false,
    steps: [] as {
      type: "thinking" | "tool_call" | "observation" | "answer";
      content: string;
    }[],
    connect: async (_url: string) => {
      // TODO
    },
    disconnect: () => {
      // TODO
    },
  };
}
