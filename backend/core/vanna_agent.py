"""
Stats Center — Vanna Agent Factory
Assembles the Vanna agent with StarRocks runner, Ollama service, and Redis session.
"""
from __future__ import annotations

import json
import logging
import asyncio
from typing import Any

from core.starrocks_runner import StarRocksRunner
from core.llm_service import OllamaLlmService, STARROCKS_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class VannaAgent:
    """
    Orchestrates the NL → SQL → Data → Chart pipeline.

    For Phase 1, this is a simplified direct implementation.
    Phase 2 will integrate with the full Vanna Agent framework
    (ToolRegistry, RunSqlTool, VisualizeDataTool).
    """

    def __init__(
        self,
        llm: OllamaLlmService | None = None,
        sql_runner: StarRocksRunner | None = None,
        schema_ddl: str | None = None,
    ):
        self.llm = llm or OllamaLlmService()
        self.sql_runner = sql_runner or StarRocksRunner()
        self.schema_ddl = schema_ddl or ""

    async def load_schema(self) -> str:
        """Load DDL from StarRocks and cache it asynchronously."""
        try:
            self.schema_ddl = await asyncio.to_thread(self.sql_runner.get_schema)
            logger.info("Loaded schema DDL (%d chars)", len(self.schema_ddl))
        except Exception as exc:
            logger.warning("Could not load schema: %s", exc)
        return self.schema_ddl

    async def generate_sql(self, question: str, context: list[dict] | None = None, debug_list: list | None = None) -> str:
        """
        Generate SQL from a natural language question.
        Uses the LLM with schema context and conversation history.
        """
        messages = []

        # Add schema context
        if self.schema_ddl:
            messages.append({
                "role": "user",
                "content": f"Here is the database schema:\n\n```sql\n{self.schema_ddl}\n```",
            })
            messages.append({
                "role": "assistant",
                "content": "I understand the schema. I'll generate SQL queries based on these tables.",
            })

        # Add conversation history for follow-ups
        if context:
            messages.extend(context[-6:])  # Last 3 turns max

        # Add the current question
        messages.append({
            "role": "user",
            "content": f"Generate a StarRocks SQL query for: {question}",
        })

        if debug_list is not None:
            debug_list.append({
                "step": "SQL Generation",
                "system_prompt": STARROCKS_SYSTEM_PROMPT,
                "messages": messages.copy()
            })

        sql = await self.llm.achat(
            messages=messages,
            system_prompt=STARROCKS_SYSTEM_PROMPT,
        )

        # Clean up: strip markdown code fences if present
        sql = sql.strip()
        if sql.startswith("```"):
            lines = sql.split("\n")
            sql = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        return sql.strip()

    async def execute_sql(self, sql: str) -> dict:
        """
        Execute SQL asynchronously and return results as a serializable dict.
        Returns: { columns: [...], rows: [[...], ...], row_count: int }
        """
        import pandas as pd

        df = await asyncio.to_thread(self.sql_runner.run_sql, sql)

        import json
        
        # Use pandas to_json to safely handle Decimals, Dates, and NaN
        parsed = json.loads(df.to_json(orient="split", date_format="iso"))

        return {
            "columns": parsed.get("columns", []),
            "rows": parsed.get("data", []),
            "row_count": len(df),
        }

    async def generate_chart(
        self, question: str, columns: list[str], rows: list[list], context: list[dict] | None = None, debug_list: list | None = None, **kwargs
    ) -> dict:
        """
        Generate a Plotly figure JSON from query results.
        Uses the LLM to determine the best chart type and configuration.

        Returns: { data: [...], layout: {...} }  (Plotly figure spec)
        """
        # Build a data preview for the LLM
        import pandas as pd

        df = pd.DataFrame(rows, columns=columns)
        preview = df.head(5).to_string(index=False)
        col_types = {col: str(df[col].dtype) for col in columns}

        prompt = f"""Given this data from the query "{question}":

Columns and types: {col_types}

Data preview:
{preview}

Total rows: {len(rows)}

Generate a Plotly figure specification as a JSON object with "data" and "layout" keys.
Choose the most appropriate chart type (bar, line, scatter, pie, heatmap).
Use a dark theme (template: "plotly_dark").
Make the chart clear, well-labeled, and visually appealing.

Return ONLY valid JSON, no explanation."""

        messages = []
        if context:
            messages.extend(context[-3:]) # Only take recent context

        messages.append({"role": "user", "content": prompt})

        if debug_list is not None:
            debug_list.append({
                "step": "Chart Generation",
                "messages": messages.copy()
            })

        response = await self.llm.achat(
            messages=messages,
        )

        # Parse the JSON response
        response = response.strip()
        if response.startswith("```"):
            lines = response.split("\n")
            response = "\n".join(
                lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
            )

        try:
            chart = json.loads(response.strip())
        except json.JSONDecodeError:
            logger.warning("LLM returned invalid chart JSON, using fallback")
            chart = self._fallback_chart(question, columns, rows)

        # Ensure dark theme
        chart.setdefault("layout", {})
        chart["layout"].setdefault("template", "plotly_dark")
        chart["layout"].setdefault("paper_bgcolor", "rgba(0,0,0,0)")
        chart["layout"].setdefault("plot_bgcolor", "rgba(0,0,0,0)")

        return chart

    def _fallback_chart(
        self, question: str, columns: list[str], rows: list[list]
    ) -> dict:
        """Simple fallback chart when LLM chart generation fails."""
        if len(columns) < 2:
            return {
                "data": [{"x": list(range(len(rows))), "y": [r[0] for r in rows], "type": "bar"}],
                "layout": {"title": question},
            }

        # Use first column as x, second as y
        return {
            "data": [{
                "x": [r[0] for r in rows],
                "y": [r[1] for r in rows],
                "type": "bar",
                "marker": {"color": "#6366f1"},
            }],
            "layout": {
                "title": question,
                "xaxis": {"title": columns[0]},
                "yaxis": {"title": columns[1] if len(columns) > 1 else "Count"},
            },
        }

    async def generate_summary(self, question: str, columns: list[str], rows: list[list], debug_list: list | None = None) -> str:
        """Generate a natural language summary of the query results."""
        import pandas as pd

        df = pd.DataFrame(rows, columns=columns)
        preview = df.head(10).to_string(index=False)

        prompt = f"""Summarize the following query results in 2-3 sentences.
Question: "{question}"

Data ({len(rows)} rows):
{preview}

Be concise, highlight key trends or outliers. Use specific numbers."""

        messages = [{"role": "user", "content": prompt}]
        if debug_list is not None:
            debug_list.append({
                "step": "Summary Generation",
                "messages": messages.copy()
            })

        return await self.llm.achat(
            messages=messages,
        )
