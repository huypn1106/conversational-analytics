/**
 * Stats Center — DebugViewer Component
 * Collapsible debug panel showing LLM prompts for different generation steps.
 */
import React, { useState } from "react";
import "./DebugViewer.css";

export default function DebugViewer({ debugData }) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!debugData || !debugData.messages) return null;

  return (
    <div className="debug-viewer animate-fadeIn">
      <button
        className="debug-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
        title="View LLM Prompt Debug Data"
      >
        <span className="debug-toggle-icon">{isExpanded ? "▾" : "▸"}</span>
        <span className="debug-toggle-label">Debug Data: {debugData.step}</span>
      </button>

      {isExpanded && (
        <div className="debug-content-wrapper glass-card">
          {debugData.system_prompt && (
             <div className="debug-section">
                <div className="debug-role">System Prompt</div>
                <pre><code>{debugData.system_prompt}</code></pre>
             </div>
          )}
          {debugData.messages.map((msg, idx) => (
             <div key={idx} className="debug-section">
                <div className="debug-role">Role: {msg.role}</div>
                <pre><code>{msg.content}</code></pre>
             </div>
          ))}
        </div>
      )}
    </div>
  );
}
