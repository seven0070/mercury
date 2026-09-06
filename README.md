# Mercury – AI Office Platform

Mercury integrates SurfSense, ghost‑pepper, Hermes3D, CrewAI, and Pi into a single AI‑powered research and visualization platform.

## Quick Start

### Local Development

1. Copy `.env.example` to `.env` and fill in your API keys.
2. Install dependencies for each service (see individual `requirements.txt`).
3. Start services:
   - Backend: `cd backend && uvicorn main:app --reload --port 8000`
   - Pi Middleware: `cd pi_middleware && uvicorn middleware:app --reload --port 8001`
   - Real-time Monitor: `cd realtime && uvicorn monitor:app --reload --port 8002`
   - Frontend: `cd chat_ui && python -m http.server 3000`
4. Open `http://localhost:3000` and chat with Mercury.

### Production Deployment (Docker Compose)

1. Copy `.env.example` to `.env` and configure all required variables.
2. Build and start all services:
   ```bash
   docker compose up --build
   ```
3. Access the Chat UI at `http://localhost:3000`.

This will start:
- PostgreSQL database (persistent storage)
- Backend API on port 8000 (with Prometheus metrics at `/metrics`)
- Pi Middleware on port 8001
- Real-time Monitor on port 8002
- Chat UI on port 3000

## Configuration

All configuration is done via environment variables. See `.env.example`.

### Key Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API key for CrewAI LLM | - | Yes |
| `DATABASE_URL` | Database connection string | `sqlite:///./mercury.db` | No (SQLite default) |
| `MERCURY_API_KEY` | API key for backend/middleware security | - | No (recommended for production) |
| `CORS_ALLOWED_ORIGINS` | Comma-separated allowed origins | `http://localhost:3000` | No |
| `SURFSENSE_API_URL` | SurfSense API base URL | `https://api.surfsense.com` | For real API |
| `SURFSENSE_WORKSPACE_ID` | SurfSense workspace ID | - | For real API |
| `SURFSENSE_API_KEY` | SurfSense API key | - | For real API |
| `HERMES3D_LIVE_ENABLED` | Enable live agent status updates | `false` | No |
| `HERMES3D_GATEWAY_URL` | Hermes3D WebSocket gateway | `ws://localhost:18789` | For live updates |
| `PI_MODEL` | OpenAI model for Pi layer | `gpt-4o-mini` | No |

For a complete list, see `.env.example`.

## Components

- **SurfSense**: Web data connector with support for multiple sources (Google Search, Reddit, YouTube, Amazon, etc.)
- **GhostPepper**: Local transcript processor (reads `.md` files from configured directory)
- **Hermes3D**: 3D office visualization with live agent status updates
- **CrewAI**: Multi-agent orchestration (Data Collector → Data Processor → 3D Visualizer)
- **Pi**: Conversational layer with OpenAI-powered intent extraction and response generation

## File Structure

```
mercury/
├── components/          # Core integration wrappers
│   ├── surfsense.py    # SurfSense API client
│   ├── ghost_pepper.py # Transcript processor
│   ├── hermes3d.py     # 3D office visualizer
│   └── hermes3d_live.py # Live agent status sender
├── tools/              # CrewAI tool wrappers
│   ├── surfsense_tool.py
│   ├── ghostpepper_tool.py
│   └── hermes3d_tool.py
├── agents.py           # CrewAI agent definitions
├── tasks.py            # CrewAI task definitions
├── crew.py             # Crew orchestration with step callbacks
├── backend/            # FastAPI backend service
│   ├── main.py         # API endpoints, structured logging, Prometheus
│   ├── database.py     # SQLAlchemy ORM with PostgreSQL support
│   └── requirements.txt
├── pi_middleware/      # Pi conversational layer
│   ├── middleware.py
│   ├── pi_client.py    # OpenAI-based intent/response handler
│   └── requirements.txt
├── realtime/           # WebSocket real-time monitor
├── chat_ui/            # Static frontend with history view
├── .github/workflows/  # CI/CD pipeline
├── docker-compose.yml
├── .env.example
└── README.md
```

## API Endpoints

### Backend (port 8000)
- `POST /execute` - Execute the CrewAI pipeline (requires `X-API-Key` header if configured)
- `GET /history` - Retrieve last 20 queries with previews
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics endpoint

### Pi Middleware (port 8001)
- `POST /chat` - Chat interface with intent extraction and response generation
- `GET /history` - Proxy to backend history endpoint

### Real-time Monitor (port 8002)
- `WebSocket /ws` - Live updates stream (auto-reconnects on disconnect)

## Features

### Connector Selection
Users can choose from multiple SurfSense connectors via dropdown:
- Google Search, Reddit, YouTube, Web Crawl, Amazon, Walmart, Google Maps, Indeed, TikTok, Instagram

### Persistent Storage
All queries are automatically saved to the database (SQLite by default, PostgreSQL in production) with:
- Query goal
- Selected connector
- Full pipeline result
- Timestamp

Click any history item to reload the query and connector.

### Live Agent Status
When `HERMES3D_LIVE_ENABLED=true`, agent statuses are sent to the Hermes3D gateway after each step:
- Working/Completed states
- Task descriptions
- Agent room/desk assignments (configurable via `HERMES3D_AGENT_DESKS`)

### Security
- Optional API key protection (`MERCURY_API_KEY`, `PI_API_KEY`)
- CORS restriction to configured origins
- Non-root Docker containers
- Health checks on all services

### Observability
- Structured logging with `structlog`
- Prometheus metrics for monitoring
- CI/CD pipeline with automated smoke tests

## Docker Services

The `docker-compose.yml` defines:
- **postgres**: PostgreSQL 15 database with persistent volume
- **backend**: Python/FastAPI with health check, non-root user
- **pi_middleware**: Python/FastAPI with OpenAI integration
- **realtime**: Python/FastAPI with WebSocket support
- **chat_ui**: Nginx serving static files

## Mock Fallbacks

The system includes mock fallbacks for development:
- **SurfSense**: Returns sample search results if API not configured
- **GhostPepper**: Returns sample transcript if no files found
- **Hermes3D**: Returns text summary if 3D office not enabled
- **Pi**: Uses rule-based intent extraction if no API key provided

## Troubleshooting

1. **CrewAI errors**: Ensure `OPENAI_API_KEY` is set correctly
2. **Database errors**: Check `DATABASE_URL`; for PostgreSQL ensure the database service is running
3. **Connection errors**: Verify all services are running on correct ports
4. **WebSocket issues**: Check that port 8002 is accessible; frontend auto-reconnects
5. **Docker issues**: Run `docker compose down` then `docker compose up --build`
6. **CORS errors**: Update `CORS_ALLOWED_ORIGINS` to include your frontend URL
7. **API Key errors**: If keys are configured, ensure `X-API-Key` header is sent with requests

## Production Checklist

- [ ] Set strong `MERCURY_API_KEY` and `PI_API_KEY`
- [ ] Configure `DATABASE_URL` for PostgreSQL (included in docker-compose)
- [ ] Set `CORS_ALLOWED_ORIGINS` to your production domain
- [ ] Provide valid `OPENAI_API_KEY` and SurfSense credentials
- [ ] Enable `HERMES3D_LIVE_ENABLED` if using 3D office
- [ ] Review and secure all environment variables
- [ ] Run CI/CD pipeline to verify deployment
- [ ] Monitor `/metrics` endpoint for performance insights
