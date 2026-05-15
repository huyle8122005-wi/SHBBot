"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type { ChatMessage, Conversation } from "@/types";

interface GuestConversation {
  id: string;
  title: string;
  updatedAt: string;
  messages: ChatMessage[];
}

interface GuestConversationState {
  conversations: GuestConversation[];
  saveConversation: (id: string, title: string, messages: ChatMessage[]) => void;
  getConversation: (id: string) => GuestConversation | undefined;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, title: string) => void;
  clearAll: () => void;
}

export const useGuestConversationStore = create<GuestConversationState>()(
  persist(
    (set, get) => ({
      conversations: [],
      saveConversation: (id, title, messages) => {
        set((state) => {
          const existing = state.conversations.filter((c) => c.id !== id);
          const current = state.conversations.find((c) => c.id === id);
          const newConv: GuestConversation = { 
            id, 
            title: current?.title !== "New conversation" && current?.title ? current.title : title, 
            updatedAt: new Date().toISOString(), 
            messages 
          };
          const updated = [newConv, ...existing].slice(0, 5); // Keep last 5
          return { conversations: updated };
        });
      },
      getConversation: (id) => get().conversations.find((c) => c.id === id),
      deleteConversation: (id) => {
        set((state) => ({ conversations: state.conversations.filter((c) => c.id !== id) }));
      },
      renameConversation: (id, title) => {
        set((state) => ({
          conversations: state.conversations.map((c) => 
            c.id === id ? { ...c, title, updatedAt: new Date().toISOString() } : c
          )
        }));
      },
      clearAll: () => set({ conversations: [] }),
    }),
    { name: "guest-conversations" }
  )
);
