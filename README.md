# Stats Center — Conversational Analytics Platform

**Natural Language → SQL → Interactive Charts**

Stats Center is a conversational analytics platform that lets users ask questions about their data in natural language. It generates SQL queries, executes them against a StarRocks database, and returns interactive Plotly charts — all streamed in real-time via SSE.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python, FastAPI, Vanna AI, Redis |
| **Frontend** | Vite, React, react-plotly.js |
| **Database** | StarRocks (OBT schema) |
| **Inference** | Qwen2.5-Coder via vLLM |

## Architecture

```
User Question  →  React Frontend (SSE Client)
                      ↓
                  FastAPI Backend
                      ↓
              Semantic Router (Redis)
                      ↓
              Vanna Agent Pipeline
              ├── NL → SQL (Qwen/vLLM)
              ├── Execute SQL (StarRocks)
              ├── Generate Chart (Plotly JSON)
              └── Summarize (NL)
                      ↓
              SSE Stream → React → <Plot data={...} layout={...} />
```

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 18+
- Redis
- StarRocks instance
- vLLM server running Qwen2.5-Coder

### Backend
```bash
cd backend
cp .env.example .env   # Edit with your settings
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Docker Compose (Redis + Backend + Frontend)
```bash
docker-compose up
```

## Project Structure

```
prompt-to-chart/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI entrypoint
│   │   ├── config.py         # Pydantic Settings
│   │   ├── dependencies.py   # DI (Redis, settings)
│   │   └── routers/
│   │       ├── chat.py       # SSE chat endpoint
│   │       └── health.py     # Health checks
│   ├── core/
│   │   ├── vanna_agent.py    # Agent pipeline
│   │   ├── llm_service.py    # vLLM adapter
│   │   ├── starrocks_runner.py  # SQL runner
│   │   └── redis_session.py  # Session + routing
│   └── tools/                # Custom Vanna tools
├── frontend/
│   └── src/
│       ├── api/chatStream.js  # SSE client
│       ├── hooks/useChat.js   # Chat state hook
│       └── components/
│           ├── ChatPanel/     # Message UI
│           ├── ChartRenderer/ # Plotly charts
│           ├── DataTable/     # Result tables
│           └── SqlViewer/     # SQL display
└── docker-compose.yml
```

## SSE Event Schema

The `/api/chat` endpoint streams typed events:

| Event Type | Data |
|-----------|------|
| `status` | Progress message string |
| `sql` | Generated SQL string |
| `table` | `{ columns: [], rows: [[]] }` |
| `plotly_chart` | `{ data: [], layout: {} }` — Plotly figure JSON |
| `summary` | Natural language summary string |
| `error` | `{ message, code }` |
| `done` | `null` |

## License

Private — Internal use only.
