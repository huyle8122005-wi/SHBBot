"use client";

import { useCallback, useEffect, useRef, useState } from "react";

interface UseWebSocketOptions {
  url: string;
  /** WebSocket subprotocols (e.g. ["access_token.<jwt>", "chat"]) */
  protocols?: string[];
  onMessage?: (event: MessageEvent) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  /** Initial delay for exponential backoff (ms) */
  initialReconnectDelay?: number;
  /** Maximum delay for exponential backoff (ms) */
  maxReconnectDelay?: number;
}

export function useWebSocket({
  url,
  protocols,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnect = true,
  reconnectInterval = 3000,
  maxReconnectAttempts = 20, // Increased default attempts
  initialReconnectDelay = 1000,
  maxReconnectDelay = 30000, // Max 30s between retries
}: UseWebSocketOptions) {
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttemptsRef = useRef(0);
  const isManuallyClosedRef = useRef(false);

  // Use refs for callbacks to avoid recreating connect function
  const onMessageRef = useRef(onMessage);
  const onOpenRef = useRef(onOpen);
  const onCloseRef = useRef(onClose);
  const onErrorRef = useRef(onError);

  // Keep refs updated
  useEffect(() => {
    onMessageRef.current = onMessage;
    onOpenRef.current = onOpen;
    onCloseRef.current = onClose;
    onErrorRef.current = onError;
  }, [onMessage, onOpen, onClose, onError]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN || wsRef.current?.readyState === WebSocket.CONNECTING) return;
    
    // Don't try to connect if we are offline
    if (typeof window !== 'undefined' && !window.navigator.onLine) return;

    isManuallyClosedRef.current = false;
    const ws = protocols && protocols.length > 0 ? new WebSocket(url, protocols) : new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
      reconnectAttemptsRef.current = 0;
      onOpenRef.current?.();
    };

    ws.onmessage = (event) => {
      onMessageRef.current?.(event);
    };

    ws.onclose = () => {
      setIsConnected(false);
      onCloseRef.current?.();

      if (reconnect && !isManuallyClosedRef.current && reconnectAttemptsRef.current < maxReconnectAttempts) {
        // Exponential backoff: initial * (1.5 ^ attempts)
        const delay = Math.min(
          initialReconnectDelay * Math.pow(1.5, reconnectAttemptsRef.current),
          maxReconnectDelay
        );
        
        console.log(`WebSocket disconnected. Retrying in ${Math.round(delay/1000)}s... (Attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`);
        
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttemptsRef.current += 1;
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      onErrorRef.current?.(error);
    };
  }, [url, protocols, reconnect, maxReconnectAttempts, initialReconnectDelay, maxReconnectDelay]);

  const disconnect = useCallback(() => {
    isManuallyClosedRef.current = true;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((data: string | object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message = typeof data === "string" ? data : JSON.stringify(data);
      wsRef.current.send(message);
    } else {
      console.warn("WebSocket not connected. Message not sent.");
    }
  }, []);

  // Reconnect on tab focus or network online
  useEffect(() => {
    if (typeof window === 'undefined') return;

    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isConnected && reconnect) {
        console.log("Tab focused, attempting to reconnect WebSocket...");
        reconnectAttemptsRef.current = 0; // Reset attempts on manual focus
        connect();
      }
    };

    const handleOnline = () => {
      if (!isConnected && reconnect) {
        console.log("Network online, attempting to reconnect WebSocket...");
        reconnectAttemptsRef.current = 0;
        connect();
      }
    };

    window.addEventListener('visibilitychange', handleVisibilityChange);
    window.addEventListener('online', handleOnline);

    return () => {
      window.removeEventListener('visibilitychange', handleVisibilityChange);
      window.removeEventListener('online', handleOnline);
    };
  }, [connect, isConnected, reconnect]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return {
    isConnected,
    connect,
    disconnect,
    sendMessage,
  };
}
