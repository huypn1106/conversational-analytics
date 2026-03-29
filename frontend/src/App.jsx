/**
 * Stats Center — Main App Component
 */
import React from "react";
import { useChat } from "./hooks/useChat";
import ChatPanel from "./components/ChatPanel/ChatPanel";
import "./App.css";

// Top-level error boundary to prevent blank screen crashes
class AppErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("App crash caught:", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: "flex", flexDirection: "column", alignItems: "center",
          justifyContent: "center", height: "100vh", color: "#f0f0f5",
          fontFamily: "Inter, sans-serif", gap: "16px", padding: "32px",
          textAlign: "center",
        }}>
          <h2>⚠️ Something went wrong</h2>
          <p style={{ color: "#9999ab" }}>{this.state.error?.message}</p>
          <button
            onClick={() => { this.setState({ hasError: false, error: null }); window.location.reload(); }}
            style={{
              padding: "8px 24px", background: "#6366f1", color: "white",
              border: "none", borderRadius: "8px", cursor: "pointer", fontSize: "14px",
            }}
          >
            Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppContent() {
  const { messages, isStreaming, sessionId, sendMessage, cancelStream, clearChat } = useChat();

  return (
    <div className="app">
      {/* ── Header ──────────────────── */}
      <header className="app-header">
        <div className="app-header-inner">
          <div className="app-logo">
            <span className="app-logo-icon">📊</span>
            <h1 className="app-title">Stats Center</h1>
            <span className="app-version">v0.1</span>
          </div>
          <div className="app-header-meta">
            {sessionId && (
              <span className="session-badge" title={sessionId}>
                Session: {sessionId.slice(0, 8)}…
              </span>
            )}
          </div>
        </div>
      </header>

      {/* ── Main Content ───────────── */}
      <main className="app-main">
        <ChatPanel
          messages={messages}
          isStreaming={isStreaming}
          onSendMessage={sendMessage}
          onCancelStream={cancelStream}
          onClearChat={clearChat}
        />
      </main>
    </div>
  );
}

export default function App() {
  return (
    <AppErrorBoundary>
      <AppContent />
    </AppErrorBoundary>
  );
}
