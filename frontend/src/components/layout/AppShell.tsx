"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import Sidebar from "@/components/layout/Sidebar";
import { getToken, isTokenExpired, clearToken } from "@/lib/auth";
import { onHttpError } from "@/lib/api";

/** Routes that render standalone (no sidebar, no auth required). */
const PUBLIC_ROUTES = ["/login", "/register", "/forgot-password"];

function isPublic(pathname: string): boolean {
  return PUBLIC_ROUTES.some(
    (r) => pathname === r || pathname.startsWith(r + "/")
  );
}

/**
 * Top-level shell that decides the chrome around a page:
 *
 *   - Public auth routes (login/register/...) render the page alone.
 *   - Every other route requires a valid token; otherwise the user is
 *     redirected to ``/login``. Authenticated routes get the sidebar.
 */
export default function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const pub = isPublic(pathname);

  // Gate rendering of protected pages until the token check has run, so a
  // logged-out user never sees a flash of protected content.
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    if (pub) return;
    const token = getToken();
    if (!token || isTokenExpired(token)) {
      router.replace("/login");
      setAuthorized(false);
    } else {
      setAuthorized(true);
    }
  }, [pathname, pub, router]);

  // Session-wide 401 handling: if the token expires mid-session, clear it and
  // bounce to login. Skipped on public routes (the login error is shown there).
  useEffect(() => {
    return onHttpError((code) => {
      if (code === 401 && !isPublic(pathname)) {
        clearToken();
        router.replace("/login");
      }
    });
  }, [pathname, router]);

  if (pub) {
    // ``body`` is a flex row; give public pages a full-width slot so their
    // own ``flex items-center justify-center`` actually centres on screen.
    return <div className="flex-1">{children}</div>;
  }

  if (!authorized) {
    // Token check pending or failed — render nothing while redirecting.
    return null;
  }

  return (
    <>
      <Sidebar />
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </>
  );
}
