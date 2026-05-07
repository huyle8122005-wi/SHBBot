"use client";

import { useEffect, useRef, useCallback, useState } from "react";
import { useChat } from "@/hooks";
import { MessageList } from "./message-list";
import { ChatInput } from "./chat-input";
import { SuggestedQuestions } from "./suggested-questions";
import { ToolApprovalDialog } from "./tool-approval-dialog";
import { Bot, ChevronDown, Check, Sparkles, TrendingUp, ShieldAlert, BarChart3, Globe2 } from "lucide-react";
import { DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem } from "@/components/ui";
import type { PendingApproval, Decision } from "@/types";
import { useConversationStore, useChatStore } from "@/stores";
import { useConversations } from "@/hooks";

import { useAuthStore } from "@/stores";

export function ChatContainer() {
  return <AuthenticatedChatContainer />;
}

function AuthenticatedChatContainer() {
  const { currentConversationId, currentMessages } = useConversationStore();
  const { addMessage: addChatMessage } = useChatStore();
  const { fetchConversations } = useConversations();
  const { isAuthenticated } = useAuthStore();
  const prevConversationIdRef = useRef<string | null | undefined>(undefined);

  const handleConversationCreated = useCallback((conversationId: string) => {
    if (isAuthenticated) {
      fetchConversations();
    }
  }, [fetchConversations, isAuthenticated]);

  const {
    messages,
    isConnected,
    isProcessing,
    connect,
    disconnect,
    sendMessage,
    clearMessages,
    setModel,
    pendingApproval,
    sendResumeDecisions,
  } = useChat({
    conversationId: currentConversationId,
    onConversationCreated: handleConversationCreated,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Clear messages when conversation changes, but NOT when going from null to a new ID
  // (that happens when a new chat is saved - we want to keep the messages)
  useEffect(() => {
    const prevId = prevConversationIdRef.current;
    const currId = currentConversationId;

    // Skip initial mount
    if (prevId === undefined) {
      prevConversationIdRef.current = currId;
      return;
    }

    // Clear messages when:
    // 1. Going from a conversation to null (new chat)
    // 2. Switching between two different conversations
    // Do NOT clear when going from null to a conversation (new chat being saved)
    const shouldClear =
      currId === null || // Going to new chat
      (prevId !== null && prevId !== currId); // Switching between conversations

    if (shouldClear) {
      clearMessages();
    }

    prevConversationIdRef.current = currId;
  }, [currentConversationId, clearMessages]);

  // Load messages from conversation store when switching to a saved conversation
  useEffect(() => {
    if (currentMessages.length > 0) {
      clearMessages();
      currentMessages.forEach((msg) => {
        addChatMessage({
          id: msg.id,
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.created_at),
          conversationId: msg.conversation_id,
          toolCalls: msg.tool_calls?.map((tc) => ({
            id: tc.tool_call_id,
            name: tc.tool_name,
            args: tc.args,
            result: tc.result,
            status: tc.status === "failed" ? "error" : tc.status,
          })),
          user_rating: msg.user_rating ?? undefined,
          rating_count: msg.rating_count ?? undefined,
          fileIds: "files" in msg && Array.isArray((msg as unknown as { files?: unknown[] }).files)
            ? ((msg as unknown as { files: { id: string }[] }).files).map((f) => f.id)
            : undefined,
        });
      });
    }
  }, [currentMessages, addChatMessage, clearMessages]);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) return;
    // Only auto-scroll if user is already near the bottom
    const isNearBottom = container.scrollHeight - container.scrollTop - container.clientHeight < 150;
    if (isNearBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <ChatUI
      messages={messages}
      isConnected={isConnected}
      isProcessing={isProcessing}
      sendMessage={sendMessage}
      onModelChange={setModel}
      messagesEndRef={messagesEndRef}
      scrollContainerRef={scrollContainerRef}
      pendingApproval={pendingApproval}
      onResumeDecisions={sendResumeDecisions}
    />
  );
}

function ModelSelector({ onChange }: { onChange: (model: string | null) => void }) {
  const [availableModels, setAvailableModels] = useState<{value: string; label: string}[]>([
    { value: "", label: "Default" },
  ]);
  const [selected, setSelected] = useState(availableModels[0]);

  useEffect(() => {
    fetch("/api/v1/agent/models", { credentials: "include" })
      .then(r => r.ok ? r.json() : null)
      .then(data => {
        if (data?.models) {
          const models = [
            { value: "", label: `Default (${data.default})` },
            ...data.models.map((m: string) => ({ value: m, label: m })),
          ];
          setAvailableModels(models);
          setSelected(models[0]);
        }
      })
      .catch(() => {});
  }, []);

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-colors">
          {selected.label}
          <ChevronDown className="h-3 w-3" />
        </button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-48">
        {availableModels.map((m) => (
          <DropdownMenuItem key={m.value} onClick={() => { setSelected(m); onChange(m.value || null); }} className="flex items-center justify-between text-xs">
            {m.label}
            {selected.value === m.value && <Check className="h-3.5 w-3.5" />}
          </DropdownMenuItem>
        ))}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

interface ChatUIProps {
  messages: import("@/types").ChatMessage[];
  isConnected: boolean;
  isProcessing: boolean;
  sendMessage: (content: string, fileIds?: string[]) => void;
  onModelChange?: (model: string | null) => void;
  messagesEndRef: React.RefObject<HTMLDivElement | null>;
  scrollContainerRef: React.RefObject<HTMLDivElement | null>;
  pendingApproval?: PendingApproval | null;
  onResumeDecisions?: (decisions: Decision[]) => void;
}

const SHB_SUGGESTIONS = [
  "Tại sao nên đầu tư vào cổ phiếu SHB lúc này?",
  "Dự báo giá cổ phiếu SHB trong 6 tháng tới",
  "Phân tích tác động kinh tế vĩ mô đến ngành ngân hàng",
  "Đánh giá các rủi ro và chiến lược phòng vệ khi đầu tư SHB",
  "Tình hình nợ xấu và khả năng trích lập dự phòng của SHB",
  "Tiềm năng từ mảng tài chính tiêu dùng SHB Finance",
  "Chiến lược chuyển đổi số 2024-2028 của SHB có gì đặc biệt?",
  "So sánh SHB với các ngân hàng Big4 và TMCP cùng phân khúc",
];

function ChatUI({
  messages,
  isConnected,
  isProcessing,
  sendMessage,
  onModelChange,
  messagesEndRef,
  scrollContainerRef,
  pendingApproval,
  onResumeDecisions,
}: ChatUIProps) {
  return (
    <div className="flex flex-col h-full max-w-4xl mx-auto w-full border-x border-border/40 bg-background/50 backdrop-blur-sm shadow-2xl">
      {/* Header Banner */}
      <div className="px-6 py-4 bg-gradient-to-r from-brand/10 via-brand/5 to-transparent border-b border-brand/10 flex items-center justify-between sticky top-0 z-20 backdrop-blur-xl">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-xl bg-brand/10 shadow-inner">
            <Sparkles className="h-5 w-5 text-brand" />
          </div>
          <div>
            <h2 className="text-base font-black text-foreground tracking-tight">SHB Financial AI Pro</h2>
            <div className="flex items-center gap-2">
               <span className="text-[9px] px-1.5 py-0.5 rounded bg-brand/10 text-brand font-bold uppercase tracking-wider">Expert Mode</span>
               <p className="text-[10px] text-muted-foreground font-medium uppercase tracking-tight">Stock & Macro Analysis</p>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-4 mr-4 text-muted-foreground">
             <TrendingUp className="h-4 w-4 opacity-50" />
             <BarChart3 className="h-4 w-4 opacity-50" />
             <Globe2 className="h-4 w-4 opacity-50" />
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-background/80 border border-border/40 shadow-sm">
            <span
              className={`inline-block h-2 w-2 rounded-full ${isConnected ? "bg-green-500 animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" : "bg-red-500"}`}
            />
            <span className="text-[10px] font-black text-muted-foreground uppercase">{isConnected ? "Online" : "Offline"}</span>
          </div>
        </div>
      </div>

      <div ref={scrollContainerRef} className="flex-1 overflow-y-auto px-6 py-8 scrollbar-thin scroll-smooth">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-10 py-10">
            <div className="relative group">
              <div className="absolute inset-0 bg-brand/30 blur-[80px] rounded-full group-hover:bg-brand/40 transition-colors duration-1000" />
              <div className="relative w-28 h-24 rounded-[2.5rem] bg-card border-2 border-brand/20 shadow-[0_20px_50px_rgba(0,0,0,0.1)] flex items-center justify-center transform hover:scale-105 hover:rotate-2 transition-all duration-500 cursor-pointer overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-brand/5 to-transparent" />
                <Bot className="h-14 w-14 text-brand relative z-10" />
              </div>
            </div>
            
            <div className="text-center max-w-lg space-y-4 px-6">
              <h1 className="text-3xl font-black tracking-tighter text-foreground sm:text-4xl">
                Xin chào Nhà đầu tư!
              </h1>
              <p className="text-sm sm:text-base text-muted-foreground leading-relaxed font-medium">
                Tôi là Trợ lý AI thế hệ mới, được tối ưu riêng cho ngân hàng SHB. Tôi sẵn sàng hỗ trợ bạn phân tích mã, dự báo giá và quản trị rủi ro chuyên sâu.
              </p>
            </div>

            <div className="w-full max-w-xl space-y-6">
              <SuggestedQuestions
                questions={SHB_SUGGESTIONS}
                onSelect={(q) => sendMessage(q)}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-8 pb-10">
            <MessageList messages={messages} />
            <div className="pt-6 opacity-0 animate-in fade-in slide-in-from-bottom-4 duration-700 fill-mode-forwards" style={{ animationDelay: '500ms' }}>
               <div className="flex items-center gap-2 mb-4">
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
                  <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-widest px-2">Gợi ý phân tích tiếp theo</span>
                  <div className="h-px flex-1 bg-gradient-to-r from-transparent via-border to-transparent" />
               </div>
               <SuggestedQuestions
                  questions={SHB_SUGGESTIONS.slice(0, 4)}
                  onSelect={(q) => sendMessage(q)}
                />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} className="h-4" />
      </div>

      {/* Human-in-the-Loop: Tool Approval Dialog */}
      {pendingApproval && onResumeDecisions && (
        <div className="px-6 pb-2">
          <ToolApprovalDialog
            actionRequests={pendingApproval.actionRequests}
            reviewConfigs={pendingApproval.reviewConfigs}
            onDecisions={onResumeDecisions}
            disabled={!isConnected}
          />
        </div>
      )}

      <div className="px-6 pb-8">
        <div className="rounded-[2rem] border-2 border-brand/10 bg-card/90 shadow-[0_10px_40px_rgba(0,0,0,0.1)] backdrop-blur-xl overflow-hidden transition-all duration-300 focus-within:border-brand/40 focus-within:shadow-[0_15px_50px_rgba(0,0,0,0.15)] group">
          <div className="px-6 py-4">
            <ChatInput
              onSend={sendMessage}
              disabled={!isConnected || !!pendingApproval}
              isProcessing={isProcessing}
            />
          </div>
          <div className="flex items-center justify-between px-6 py-3 border-t border-border/10 bg-muted/30">
            <div className="flex items-center gap-2">
               <ShieldAlert className="h-3 w-3 text-brand opacity-60" />
               <p className="text-[10px] text-muted-foreground italic font-bold tracking-tight">AI model đang sẵn sàng phân tích chuyên sâu cho bạn</p>
            </div>
            <div className="flex items-center gap-4">
              {onModelChange && (
                <ModelSelector onChange={onModelChange} />
              )}
            </div>
          </div>
        </div>
        <p className="text-[9px] text-center mt-3 text-muted-foreground/60 font-medium tracking-wide">
          Dữ liệu phân tích chỉ mang tính chất tham khảo và hỗ trợ ra quyết định đầu tư.
        </p>
      </div>
    </div>
  );
}
