
"use client";

import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { useAuthStore } from "@/stores";
import { apiClient } from "@/lib/api-client";
import { ROUTES } from "@/lib/constants";
import type { User } from "@/types";
import { Spinner } from "@/components/ui";

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, setUser } = useAuthStore();
  const [checking, setChecking] = useState(!isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) return;

    // Allow guest access to chat route
    const isChatRoute = pathname?.includes(ROUTES.CHAT);

    const verify = async () => {
      try {
        const user = await apiClient.get<User>("/auth/me");
        setUser(user);
      } catch {
        // Only redirect to login if NOT on a route that allows guests
        if (!isChatRoute) {
          router.replace(ROUTES.LOGIN);
        }
      } finally {
        setChecking(false);
      }
    };

    verify();
  }, [isAuthenticated, router, setUser, pathname]);

  // If we are checking auth and not authenticated, 
  // only show spinner for protected routes.
  // For chat route, we can show the UI even while checking (it will just be guest mode initially).
  const isChatRoute = pathname?.includes(ROUTES.CHAT);
  if (checking && !isAuthenticated && !isChatRoute) {
    return (
      <div className="flex h-screen items-center justify-center" role="status" aria-live="polite">
        <Spinner className="text-muted-foreground h-6 w-6" />
        <span className="sr-only">Checking authentication...</span>
      </div>
    );
  }

  return <>{children}</>;
}
