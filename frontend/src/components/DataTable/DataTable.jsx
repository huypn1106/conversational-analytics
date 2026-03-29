/**
 * Stats Center — DataTable Component
 * Renders query result data in a styled, scrollable table.
 */
import React from "react";
import "./DataTable.css";

export default function DataTable({ data }) {
  if (!data || !data.columns || !data.rows || data.rows.length === 0) {
    return null;
  }

  return (
    <div className="data-table-wrapper glass-card animate-fadeIn">
      <div className="data-table-header">
        <span className="data-table-badge">📋 Results</span>
        <span className="data-table-count">{data.row_count ?? data.rows.length} rows</span>
      </div>
      <div className="data-table-scroll">
        <table className="data-table">
          <thead>
            <tr>
              {data.columns.map((col, i) => (
                <th key={i}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.rows.map((row, ri) => (
              <tr key={ri}>
                {row.map((cell, ci) => (
                  <td key={ci}>{formatCell(cell)}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

function formatCell(value) {
  if (value === null || value === undefined) return "—";
  if (typeof value === "number") {
    return Number.isInteger(value) ? value.toLocaleString() : value.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  return String(value);
}
