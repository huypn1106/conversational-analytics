/**
 * Stats Center — useChat Hook
 * Manages conversational state, SSE streaming, and session persistence.
 */
import { useState, useCallback, useRef, useEffect } from "react";
import { streamChat } from "../api/chatStream";

const SESSION_KEY = "stats-center-session-id";
const MSG_KEY_PREFIX = "stats-center-messages-";

export function useChat() {
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem(SESSION_KEY) || null
  );
  
  const [messages, setMessages] = useState(() => {
    const savedId = localStorage.getItem(SESSION_KEY);
    if (savedId) {
      const savedMsgs = localStorage.getItem(MSG_KEY_PREFIX + savedId);
      return savedMsgs ? JSON.parse(savedMsgs) : [];
    }
    return [];
  });
  
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef(null);

  // Persist session ID and messages
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(SESSION_KEY, sessionId);
      localStorage.setItem(MSG_KEY_PREFIX + sessionId, JSON.stringify(messages));
    }
  }, [sessionId, messages]);

  const sendMessage = useCallback(
    async (text) => {
      if (!text.trim() || isStreaming) return;

      // Add user message
      const userMessage = { id: Date.now(), type: "user", content: text };
      setMessages((prev) => [...prev, userMessage]);
      setIsStreaming(true);

      // Create an abort controller for cancellation
      const controller = new AbortController();
      abortRef.current = controller;

      // Accumulate assistant response parts into a single response group
      const responseId = Date.now() + 1;
      let responseParts = [];

      const addPart = (type, content) => {
        responseParts.push({ type, content });
        setMessages((prev) => {
          const existing = prev.findIndex((m) => m.id === responseId);
          const responseMsg = {
            id: responseId,
            type: "response",
            parts: [...responseParts],
            streaming: true,
          };
          if (existing >= 0) {
            return [...prev.slice(0, existing), responseMsg, ...prev.slice(existing + 1)];
          }
          return [...prev, responseMsg];
        });
      };

      try {
        await streamChat(
          text,
          sessionId,
          (event) => {
            // Capture session ID
            if (event._sessionId) {
              setSessionId(event._sessionId);
            }
            if (event.type === "status" && event.data?.session_id) {
              setSessionId(event.data.session_id);
            }

            switch (event.type) {
              case "status":
                addPart("status", typeof event.data === "string" ? event.data : event.data?.message || "Processing...");
                break;
              case "sql":
                addPart("sql", event.data);
                break;
              case "table":
                addPart("table", event.data);
                break;
              case "plotly_chart":
                addPart("chart", event.data);
                break;
              case "summary":
                addPart("summary", event.data);
                break;
              case "debug":
                addPart("debug", event.data);
                break;
              case "error":
                addPart("error", event.data);
                break;
              case "done":
                // Mark response as complete
                setMessages((prev) =>
                  prev.map((m) =>
                    m.id === responseId ? { ...m, streaming: false } : m
                  )
                );
                break;
              default:
                break;
            }
          },
          controller.signal
        );
      } catch (err) {
        if (err.name !== "AbortError") {
          addPart("error", { message: err.message, code: "CLIENT_ERROR" });
        }
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }
    },
    [sessionId, isStreaming]
  );

  const cancelStream = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      setIsStreaming(false);
    }
  }, []);

  const clearChat = useCallback(() => {
    setMessages([]);
    setSessionId(null);
    localStorage.removeItem(SESSION_KEY);
  }, []);

  const loadSession = useCallback((id) => {
    if (isStreaming) return;
    setSessionId(id);
    const savedMsgs = localStorage.getItem(MSG_KEY_PREFIX + id);
    setMessages(savedMsgs ? JSON.parse(savedMsgs) : []);
  }, [isStreaming]);

  const createSession = useCallback(() => {
    if (isStreaming) return;
    setSessionId(null);
    setMessages([]);
    localStorage.removeItem(SESSION_KEY);
  }, [isStreaming]);

  return {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    cancelStream,
    clearChat,
    loadSession,
    createSession,
  };
}
