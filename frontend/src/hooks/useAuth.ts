"use client";

/**
 * Authentication hook.
 * TODO: implement token retrieval, refresh, and user state management.
 */
export function useAuth() {
  return {
    isAuthenticated: false,
    user: null as { id: string; email: string } | null,
    login: async (_email: string, _password: string) => {
      // TODO: POST /api/auth/login
    },
    logout: () => {
      // TODO: clear token and redirect
    },
  };
}
