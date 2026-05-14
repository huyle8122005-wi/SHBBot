"use client";

import { useCallback, useEffect } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { useAuthStore } from "@/stores";
import { apiClient } from "@/lib/api-client";
import type { User, LoginRequest, RegisterRequest } from "@/types";
import { ROUTES } from "@/lib/constants";
import { supabase } from "@/lib/supabase";

export function useAuth() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading, setUser, setLoading, logout } =
    useAuthStore();

  // Check auth status on mount — always fetch fresh user data.
  useEffect(() => {
    const checkAuth = async () => {
      if (!supabase) {
        setLoading(false);
        return;
      }
      try {
        const { data: { session } } = await supabase.auth.getSession();
        if (session) {
          // Sync session with Next.js cookies if needed
          await apiClient.post("/auth/session", { 
            access_token: session.access_token,
            refresh_token: session.refresh_token 
          });
          
          const data = await apiClient.get<User & { access_token?: string }>("/auth/me");
          const { access_token, ...userData } = data;
          setUser(userData as User);
          useAuthStore.getState().setAccessToken(access_token ?? session.access_token);
        } else {
          setUser(null);
          useAuthStore.getState().setAccessToken(null);
        }
      } catch (error) {
        console.error("Auth check failed:", error);
        setUser(null);
        useAuthStore.getState().setAccessToken(null);
      } finally {
        setLoading(false);
      }
    };

    checkAuth();

    // Listen for auth changes
    if (!supabase) return;
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        await apiClient.post("/auth/session", { 
          access_token: session.access_token,
          refresh_token: session.refresh_token 
        });
        const data = await apiClient.get<User>("/auth/me");
        setUser(data);
      } else if (event === 'SIGNED_OUT') {
        await apiClient.post("/auth/logout");
        setUser(null);
        useAuthStore.getState().setAccessToken(null);
      }
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [setUser, setLoading]);

  const login = useCallback(
    async (credentials: LoginRequest) => {
      if (!supabase) throw new Error("Supabase is not configured");
      setLoading(true);
      try {
        const { data, error } = await supabase.auth.signInWithPassword({
          email: credentials.email,
          password: credentials.password,
        });

        if (error) throw error;
        if (!data.session) throw new Error("No session created");

        // Sync session with Next.js cookies
        await apiClient.post("/auth/session", { 
          access_token: data.session.access_token,
          refresh_token: data.session.refresh_token 
        });

        const userData = await apiClient.get<User>("/auth/me");
        setUser(userData);
        useAuthStore.getState().setAccessToken(data.session.access_token);
        
        router.push(userData.role === "admin" ? ROUTES.DASHBOARD : ROUTES.CHAT);
        return { user: userData, access_token: data.session.access_token };
      } catch (error) {
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [router, setUser, setLoading]
  );

  const register = useCallback(
    async (data: RegisterRequest) => {
      if (!supabase) throw new Error("Supabase is not configured");
      setLoading(true);
      try {
        const { data: signUpData, error } = await supabase.auth.signUp({
          email: data.email,
          password: data.password,
          options: {
            data: {
              full_name: data.full_name,
            }
          }
        });

        if (error) throw error;
        return signUpData.user;
      } catch (error) {
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [setLoading]
  );

  const handleLogout = useCallback(async () => {
    try {
      if (supabase) {
        await supabase.auth.signOut();
      }
      await apiClient.post("/auth/logout");
    } catch {
      // Ignore logout errors
    } finally {
      logout();
      toast.success("Logged out");
      router.push(ROUTES.LOGIN);
    }
  }, [logout, router]);

  const refreshToken = useCallback(async () => {
    try {
      if (!supabase) return false;
      const { data: { session }, error } = await supabase.auth.refreshSession();
      if (error || !session) return false;

      await apiClient.post("/auth/session", { 
        access_token: session.access_token,
        refresh_token: session.refresh_token 
      });

      useAuthStore.getState().setAccessToken(session.access_token);
      const userData = await apiClient.get<User>("/auth/me");
      setUser(userData);
      return true;
    } catch (error) {
      logout();
      router.push(ROUTES.LOGIN);
      return false;
    }
  }, [logout, router, setUser]);

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout: handleLogout,
    refreshToken,
  };
}
