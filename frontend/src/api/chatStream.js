/**
 * Stats Center — SSE Chat API Client
 * Consumes the streaming chat endpoint and dispatches typed events.
 */

/**
 * @typedef {'status' | 'sql' | 'table' | 'plotly_chart' | 'summary' | 'error' | 'done'} EventType
 * @typedef {{ type: EventType, data: any }} ChatEvent
 */

/**
 * Sends a chat message and streams back SSE events.
 *
 * @param {string} message - User's natural language question
 * @param {string | null} sessionId - Existing session ID (or null for new)
 * @param {(event: ChatEvent) => void} onEvent - Callback for each SSE event
 * @param {AbortSignal} [signal] - Optional abort signal
 * @returns {Promise<void>}
 */
export async function streamChat(message, sessionId, onEvent, signal) {
  const body = { message };
  if (sessionId) {
    body.session_id = sessionId;
  }

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    signal,
  });

  if (!response.ok) {
    const error = await response.text();
    onEvent({
      type: "error",
      data: { message: `HTTP ${response.status}: ${error}`, code: "HTTP_ERROR" },
    });
    onEvent({ type: "done", data: null });
    return;
  }

  // Extract session ID from header
  const newSessionId = response.headers.get("X-Session-Id");

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  try {
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });

      // Parse SSE events from buffer
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith("data: ")) {
          try {
            const parsed = JSON.parse(trimmed.slice(6));

            // Inject session ID into first status event
            if (parsed.type === "status" && newSessionId && parsed.data?.session_id) {
              parsed._sessionId = newSessionId;
            }

            onEvent(parsed);
          } catch (e) {
            console.warn("Failed to parse SSE event:", trimmed, e);
          }
        }
      }
    }
  } catch (err) {
    if (err.name !== "AbortError") {
      onEvent({
        type: "error",
        data: { message: err.message, code: "STREAM_ERROR" },
      });
      onEvent({ type: "done", data: null });
    }
  }
}

/**
 * Fetch session history.
 * @param {string} sessionId
 * @returns {Promise<{ session_id: string, history: Array, found: boolean }>}
 */
export async function getSessionHistory(sessionId) {
  const response = await fetch(`/api/sessions/${sessionId}/history`);
  if (!response.ok) {
    throw new Error(`Failed to fetch history: ${response.status}`);
  }
  return response.json();
}

/**
 * Create a new session.
 * @returns {Promise<{ session_id: string, created: boolean }>}
 */
export async function createSession() {
  const response = await fetch("/api/sessions", { method: "POST" });
  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.status}`);
  }
  return response.json();
}
