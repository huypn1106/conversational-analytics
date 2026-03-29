/**
 * Stats Center — SqlViewer Component
 * Collapsible SQL code block with syntax highlighting and copy button.
 */
import React, { useState } from "react";
import "./SqlViewer.css";

export default function SqlViewer({ sql }) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [copied, setCopied] = useState(false);

  if (!sql) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback
      const ta = document.createElement("textarea");
      ta.value = sql;
      document.body.appendChild(ta);
      ta.select();
      document.execCommand("copy");
      document.body.removeChild(ta);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  return (
    <div className="sql-viewer animate-fadeIn">
      <button
        className="sql-toggle"
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <span className="sql-toggle-icon">{isExpanded ? "▾" : "▸"}</span>
        <span className="sql-toggle-label">SQL Query</span>
      </button>

      {isExpanded && (
        <div className="sql-code-wrapper">
          <button
            className="btn btn-ghost sql-copy-btn"
            onClick={handleCopy}
          >
            {copied ? "✓ Copied" : "Copy"}
          </button>
          <pre className="sql-code">
            <code>{sql}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
