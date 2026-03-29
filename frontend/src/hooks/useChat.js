/**
 * Stats Center — useChat Hook
 * Manages conversational state, SSE streaming, and session persistence.
 */
import { useState, useCallback, useRef, useEffect } from "react";
import { streamChat } from "../api/chatStream";

const SESSION_KEY = "stats-center-session-id";

/**
 * Message types in the conversation:
 * - user:    User's question
 * - status:  Progress update (generating SQL, executing, etc.)
 * - sql:     Generated SQL code
 * - table:   Query result table { columns, rows }
 * - chart:   Plotly figure { data, layout }
 * - summary: NL summary of results
 * - error:   Error message
 */

export function useChat() {
  const [messages, setMessages] = useState([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState(
    () => localStorage.getItem(SESSION_KEY) || null
  );
  const abortRef = useRef(null);

  // Persist session ID
  useEffect(() => {
    if (sessionId) {
      localStorage.setItem(SESSION_KEY, sessionId);
    }
  }, [sessionId]);

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

  return {
    messages,
    isStreaming,
    sessionId,
    sendMessage,
    cancelStream,
    clearChat,
  };
}
