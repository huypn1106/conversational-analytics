/**
 * Stats Center — ChatPanel Component
 * Message input + scrollable message history with streaming support.
 */
import React, { useState, useRef, useEffect } from "react";
import ChartRenderer from "../ChartRenderer/ChartRenderer";
import DataTable from "../DataTable/DataTable";
import SqlViewer from "../SqlViewer/SqlViewer";
import DebugViewer from "../DebugViewer/DebugViewer";
import "./ChatPanel.css";

const EXAMPLE_QUESTIONS = [
  "Show me total revenue by region for the last quarter",
  "What are the top 10 products by sales volume?",
  "Compare monthly active users year over year",
  "Break down customer acquisition cost by channel",
];

export default function ChatPanel({
  messages,
  isStreaming,
  onSendMessage,
  onCancelStream,
  onClearChat,
}) {
  const [input, setInput] = useState("");
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isStreaming) {
      onSendMessage(input.trim());
      setInput("");
    }
  };

  const handleExampleClick = (q) => {
    if (!isStreaming) {
      onSendMessage(q);
    }
  };

  return (
    <div className="chat-panel">
      {/* ── Messages Area ──────────────── */}
      <div className="chat-messages">
        {messages.length === 0 ? (
          <EmptyState onExampleClick={handleExampleClick} />
        ) : (
          messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* ── Input Area ─────────────────── */}
      <div className="chat-input-area">
        <form onSubmit={handleSubmit} className="chat-input-form">
          <input
            ref={inputRef}
            type="text"
            className="chat-input"
            placeholder="Ask a question about your data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={isStreaming}
            id="chat-input"
          />
          {isStreaming ? (
            <button
              type="button"
              className="btn btn-ghost chat-cancel-btn"
              onClick={onCancelStream}
            >
              ■ Stop
            </button>
          ) : (
            <button
              type="submit"
              className="btn btn-primary chat-send-btn"
              disabled={!input.trim()}
            >
              Send →
            </button>
          )}
        </form>
        {messages.length > 0 && (
          <button
            className="btn btn-ghost chat-clear-btn"
            onClick={onClearChat}
            disabled={isStreaming}
          >
            Clear chat
          </button>
        )}
      </div>
    </div>
  );
}

/* ── Sub-components ──────────────────────────── */

function EmptyState({ onExampleClick }) {
  return (
    <div className="empty-state animate-slideUp">
      <div className="empty-state-icon">📊</div>
      <h2>Stats Center</h2>
      <p className="empty-state-subtitle">
        Ask questions about your data in natural language.
        <br />
        I'll generate SQL, run queries, and create interactive charts.
      </p>
      <div className="example-questions">
        <p className="example-label">Try asking:</p>
        {EXAMPLE_QUESTIONS.map((q, i) => (
          <button
            key={i}
            className="example-question glass-card"
            onClick={() => onExampleClick(q)}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  );
}

function MessageBubble({ message }) {
  if (message.type === "user") {
    return (
      <div className="message message-user animate-fadeIn">
        <div className="message-content">{message.content}</div>
      </div>
    );
  }

  if (message.type === "response") {
    return (
      <div className="message message-assistant animate-fadeIn">
        {message.parts.map((part, i) => (
          <ResponsePart key={i} part={part} />
        ))}
        {message.streaming && (
          <div className="streaming-indicator">
            <span className="dot animate-pulse">●</span>
            <span className="dot animate-pulse" style={{ animationDelay: "0.2s" }}>●</span>
            <span className="dot animate-pulse" style={{ animationDelay: "0.4s" }}>●</span>
          </div>
        )}
      </div>
    );
  }

  return null;
}

function ResponsePart({ part }) {
  switch (part.type) {
    case "status":
      return <div className="response-status">{part.content}</div>;
    case "sql":
      return <SqlViewer sql={part.content} />;
    case "table":
      return <DataTable data={part.content} />;
    case "chart":
      return <ChartRenderer figure={part.content} />;
    case "summary":
      return <div className="response-summary">{part.content}</div>;
    case "debug":
      return <DebugViewer debugData={part.content} />;
    case "error":
      return (
        <div className="response-error glass-card">
          ⚠️ {part.content?.message || part.content || "An error occurred"}
        </div>
      );
    default:
      return null;
  }
}
