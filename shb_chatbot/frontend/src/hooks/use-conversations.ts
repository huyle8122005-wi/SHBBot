
"use client";

import { useCallback, useRef, useEffect } from "react";
import { apiClient } from "@/lib/api-client";
import { useConversationStore, useChatStore, useAuthStore, useGuestConversationStore } from "@/stores";
import type {
  Conversation,
  ConversationMessage,
  ConversationListResponse,
} from "@/types";

interface CreateConversationResponse {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
  is_archived: boolean;
}

interface MessagesResponse {
  items: ConversationMessage[];
  total: number;
}

export function useConversations() {
  const { isAuthenticated } = useAuthStore();
  const guestStore = useGuestConversationStore();
  const {
    conversations: authConversations,
    currentConversationId,
    currentMessages,
    isLoading,
    error,
    setConversations,
    addConversation,
    updateConversation,
    removeConversation,
    setCurrentConversationId,
    setCurrentMessages,
    setLoading,
    setError,
  } = useConversationStore();
  const { clearMessages } = useChatStore();
  const hasMoreRef = useRef(true);
  const PAGE_SIZE = 30;

  // Sync guest conversations to the standard Conversation array format
  const conversations = isAuthenticated 
    ? authConversations 
    : guestStore.conversations.map(c => ({
        id: c.id,
        title: c.title,
        created_at: c.updatedAt,
        updated_at: c.updatedAt,
        is_archived: false,
      }));

  const fetchConversations = useCallback(async () => {
    if (!isAuthenticated) return;
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<ConversationListResponse>(
        `/conversations?limit=${PAGE_SIZE}`
      );
      setConversations(response.items);
      hasMoreRef.current = response.items.length >= PAGE_SIZE;
      // URL ?id= param always takes priority
      const urlId = new URLSearchParams(window.location.search).get("id");
      if (urlId && response.items.some(c => c.id === urlId)) {
        if (useConversationStore.getState().currentConversationId !== urlId) {
          setCurrentConversationId(urlId);
          clearMessages();
          setCurrentMessages([]);
          try {
            const msgs = await apiClient.get<MessagesResponse>(`/conversations/${urlId}/messages`);
            setCurrentMessages(msgs.items);
          } catch {}
        }
      }
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Failed to fetch conversations";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [setConversations, setLoading, setError, setCurrentConversationId, setCurrentMessages, clearMessages, isAuthenticated]);

  const loadingMoreRef = useRef(false);

  const fetchMoreConversations = useCallback(async () => {
    if (!isAuthenticated || !hasMoreRef.current || loadingMoreRef.current) return;
    loadingMoreRef.current = true;
    const current = useConversationStore.getState().conversations;
    try {
      const response = await apiClient.get<ConversationListResponse>(
        `/conversations?limit=${PAGE_SIZE}&skip=${current.length}`
      );
      if (response.items.length > 0) {
        setConversations([...current, ...response.items]);
      }
      hasMoreRef.current = response.items.length >= PAGE_SIZE;
    } catch {} finally {
      loadingMoreRef.current = false;
    }
  }, [setConversations, isAuthenticated]);

  const createConversation = useCallback(
    async (title?: string): Promise<Conversation | null> => {
      if (!isAuthenticated) {
        return null;
      }
      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.post<CreateConversationResponse>(
          "/conversations",
          { title }
        );
        const newConversation: Conversation = {
          id: response.id,
          title: response.title,
          created_at: response.created_at,
          updated_at: response.updated_at,
          is_archived: response.is_archived,
        };
        addConversation(newConversation);
        return newConversation;
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to create conversation";
        setError(message);
        return null;
      } finally {
        setLoading(false);
      }
    },
    [addConversation, setLoading, setError, isAuthenticated]
  );

  const selectConversation = useCallback(
    async (id: string) => {
      setCurrentConversationId(id);
      clearMessages();
      const url = new URL(window.location.href);
      url.searchParams.set("id", id);
      window.history.replaceState({}, "", url.toString());
      
      if (!isAuthenticated) {
        const guestConv = guestStore.getConversation(id);
        if (guestConv) {
          // Convert ChatMessage to ConversationMessage format if needed, 
          // but our chat-container can just read from the store directly if we set currentMessages.
          // Since ChatMessage is not exactly ConversationMessage, we'll map the basic fields
          setCurrentMessages(guestConv.messages.map(m => ({
            id: m.id,
            conversation_id: id,
            role: m.role,
            content: m.content,
            created_at: m.timestamp.toISOString(),
            tool_calls: m.toolCalls?.map(tc => ({
              id: tc.id,
              tool_call_id: tc.id,
              tool_name: tc.name,
              args: tc.args,
              result: tc.result,
              status: tc.status === "error" ? "failed" : tc.status
            })),
            user_rating: m.user_rating,
            rating_count: m.rating_count,
            files: m.fileIds?.map(fid => ({ id: fid }))
          } as any)));
        } else {
          setCurrentMessages([]);
        }
        return;
      }

      setLoading(true);
      setError(null);
      try {
        const response = await apiClient.get<MessagesResponse>(
          `/conversations/${id}/messages`
        );
        setCurrentMessages(response.items);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to fetch messages";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [setCurrentConversationId, clearMessages, setCurrentMessages, setLoading, setError, isAuthenticated, guestStore]
  );

  const archiveConversation = useCallback(
    async (id: string) => {
      if (!isAuthenticated) return;
      try {
        await apiClient.patch(`/conversations/${id}`, { is_archived: true });
        updateConversation(id, { is_archived: true });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to archive conversation";
        setError(message);
      }
    },
    [updateConversation, setError, isAuthenticated]
  );

  const deleteConversation = useCallback(
    async (id: string) => {
      if (!isAuthenticated) {
        guestStore.deleteConversation(id);
        if (useConversationStore.getState().currentConversationId === id) {
          setCurrentConversationId(null);
          clearMessages();
          setCurrentMessages([]);
        }
        return;
      }
      try {
        await apiClient.delete(`/conversations/${id}`);
        removeConversation(id);
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to delete conversation";
        setError(message);
      }
    },
    [removeConversation, setError, isAuthenticated, guestStore, setCurrentConversationId, clearMessages, setCurrentMessages]
  );

  const renameConversation = useCallback(
    async (id: string, title: string) => {
      if (!isAuthenticated) {
        guestStore.renameConversation(id, title);
        return;
      }
      try {
        await apiClient.patch(`/conversations/${id}`, { title });
        updateConversation(id, { title });
      } catch (err) {
        const message =
          err instanceof Error ? err.message : "Failed to rename conversation";
        setError(message);
      }
    },
    [updateConversation, setError, isAuthenticated, guestStore]
  );

  const startNewChat = useCallback(async () => {
    // If current conversation is empty (no messages), just reuse it
    const currentId = useConversationStore.getState().currentConversationId;
    if (currentId) {
      const msgs = useConversationStore.getState().currentMessages;
      if (msgs.length === 0 && isAuthenticated) {
        clearMessages();
        return;
      }
    }
    clearMessages();
    setCurrentMessages([]);
    setCurrentConversationId(null);
    const url = new URL(window.location.href);
    url.searchParams.delete("id");
    window.history.replaceState({}, "", url.toString());

    if (isAuthenticated) {
      const newConversation = await createConversation();
      if (newConversation) {
        setCurrentConversationId(newConversation.id);
        url.searchParams.set("id", newConversation.id);
        window.history.replaceState({}, "", url.toString());
      }
    }
  }, [clearMessages, setCurrentMessages, createConversation, setCurrentConversationId, isAuthenticated]);

  return {
    conversations,
    currentConversationId,
    currentMessages,
    isLoading,
    error,
    fetchConversations,
    fetchMoreConversations,
    hasMore: isAuthenticated ? hasMoreRef.current : false,
    createConversation,
    selectConversation,
    archiveConversation,
    deleteConversation,
    renameConversation,
    startNewChat,
  };
}
