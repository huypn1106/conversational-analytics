/**
 * Stats Center — ChartRenderer Component
 * Renders Plotly charts from backend JSON using react-plotly.js.
 */
import React, { useState } from "react";
import "./ChartRenderer.css";

// Handle CJS/ESM interop — unwrap .default if present
import _factory from "react-plotly.js/factory";
import _Plotly from "plotly.js/dist/plotly";
const createPlotlyComponent = _factory.default || _factory;
const Plotly = _Plotly.default || _Plotly;
const Plot = createPlotlyComponent(Plotly);

const DARK_LAYOUT_DEFAULTS = {
  template: "plotly_dark",
  paper_bgcolor: "rgba(0,0,0,0)",
  plot_bgcolor: "rgba(0,0,0,0)",
  font: {
    family: "Inter, -apple-system, system-ui, sans-serif",
    color: "#f0f0f5",
  },
  margin: { l: 50, r: 30, t: 50, b: 50 },
  autosize: true,
};

const CHART_CONFIG = {
  displayModeBar: true,
  displaylogo: false,
  modeBarButtonsToRemove: ["lasso2d", "select2d"],
  toImageButtonOptions: {
    format: "png",
    filename: "stats_center_chart",
    scale: 2,
  },
  responsive: true,
};

// Error boundary to catch Plotly rendering errors
class ChartErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div className="chart-error glass-card">
          <span>⚠️ Chart rendering failed</span>
          <small>{this.state.error?.message}</small>
        </div>
      );
    }
    return this.props.children;
  }
}

export default function ChartRenderer({ figure }) {
  const [isFullscreen, setIsFullscreen] = useState(false);

  if (!figure || !figure.data) {
    return null;
  }

  // Merge dark theme defaults into layout
  const layout = {
    ...DARK_LAYOUT_DEFAULTS,
    ...(figure.layout || {}),
    font: { ...DARK_LAYOUT_DEFAULTS.font, ...(figure.layout?.font || {}) },
  };

  const chart = (
    <ChartErrorBoundary>
      <Plot
        data={figure.data}
        layout={layout}
        config={CHART_CONFIG}
        useResizeHandler={true}
        style={{ width: "100%", height: "100%" }}
        className="chart-plot"
      />
    </ChartErrorBoundary>
  );

  return (
    <>
      <div className="chart-renderer glass-card animate-fadeIn">
        <div className="chart-header">
          <span className="chart-badge">📊 Chart</span>
          <button
            className="btn btn-ghost chart-fullscreen-btn"
            onClick={() => setIsFullscreen(true)}
            title="Fullscreen"
          >
            ⛶
          </button>
        </div>
        <div className="chart-container">{chart}</div>
      </div>

      {isFullscreen && (
        <div className="chart-modal-overlay" onClick={() => setIsFullscreen(false)}>
          <div className="chart-modal" onClick={(e) => e.stopPropagation()}>
            <button
              className="btn btn-ghost chart-close-btn"
              onClick={() => setIsFullscreen(false)}
            >
              ✕
            </button>
            <div className="chart-modal-content">{chart}</div>
          </div>
        </div>
      )}
    </>
  );
}
