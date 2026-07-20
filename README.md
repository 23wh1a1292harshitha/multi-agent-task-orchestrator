# AgentFlow — Multi-Agent Task Orchestrator

A production-shaped backend that decomposes a natural-language task into a sequence of specialized AI agents, executes them asynchronously, and persists full execution state — built with FastAPI, PostgreSQL, Redis, Celery, LangGraph, and Groq (Llama 3.3).

**Example:**
> Input: `"Research Cloud Computing, summarize it, and write a professional email."`
> Output: a research briefing → a concise summary → a ready-to-send email, with every intermediate step stored and inspectable.

---

## Why this project

Most "AI project" resume entries are a single script calling an LLM API. This one demonstrates the backend engineering that sits *around* the AI call in a real system:

- Async processing so the API never blocks on a multi-second LLM chain
- Persisted, resumable state — every agent's output is stored, not just the final result
- User-scoped authorization (JWT), so tasks are only visible to the user who created them
- A deterministic, declarative agent graph (LangGraph) instead of hand-rolled chained function calls
- Fully containerized — one command runs the entire stack

---

## Architecture

```
Client
  │  POST /tasks (JWT auth)
  ▼
FastAPI  ──creates Task (status=pending)──▶  PostgreSQL
  │
  │  enqueues job
  ▼
Redis (broker)
  │
  ▼
Celery Worker
  │  runs LangGraph:
  │
  │   ┌────────────┐     ┌───────────────┐     ┌─────────────┐
  │   │  Research  │ ──▶ │    Summary     │ ──▶ │    Email     │
  │   │   Agent    │     │     Agent      │     │    Agent     │
  │   └────────────┘     └───────────────┘     └─────────────┘
  │        (each node calls Groq / Llama 3.3, output feeds the next)
  ▼
PostgreSQL  ◀── persists plan, per-step output, final result, or error

Client polls GET /tasks/{id} for status and results
```

**Key design decision:** the API layer never executes the agent workflow directly. `POST /tasks` only writes a row and enqueues a Celery job — this keeps the HTTP request/response cycle fast regardless of how long the underlying LLM chain takes, and lets the worker scale independently of the API.

---

## Tech stack

| Layer | Choice | Why |
|---|---|---|
| API | FastAPI | Async-native, typed, auto-generated OpenAPI docs |
| Database | PostgreSQL + SQLAlchemy + Alembic | Relational integrity, tracked schema migrations (not `create_all()`) |
| Auth | JWT (python-jose) + bcrypt | Stateless auth, industry-standard password hashing |
| Queue / Broker | Celery + Redis | Decouples slow LLM calls from the request cycle; production-standard combination |
| Agent orchestration | LangGraph | Explicit state graph instead of implicit chained function calls — supports conditional/branching workflows without rearchitecting |
| LLM | Groq (Llama 3.3 70B) | Fast inference, generous free tier, OpenAI-compatible client |
| Containerization | Docker + Docker Compose | One-command reproducible environment: API, worker, Postgres, Redis |

---

## Project structure

```
app/
├── main.py                 # FastAPI entrypoint
├── config.py                # Centralized settings (env-driven)
├── api/routes/               # Thin HTTP layer (auth, tasks)
├── core/                     # Security (JWT/hashing), Celery app config
├── db/models/                 # SQLAlchemy models (User, Task)
├── schemas/                   # Pydantic request/response models
├── services/                   # Business logic layer
├── agents/                     # LLM client + individual agents + LangGraph definition
└── workers/                    # Celery task definitions
alembic/                        # Tracked DB migrations
```

---

## Running it

**Requirements:** Docker Desktop, a free [Groq API key](https://console.groq.com/keys)

```bash
git clone <your-repo-url>
cd multi-agent-orchestrator
cp .env.example .env        # then fill in SECRET_KEY and GROQ_API_KEY
docker-compose up --build -d
docker exec -it orchestrator_api alembic upgrade head
```

API docs available at **http://localhost:8000/docs**

---

## Example usage

**1. Register**
```http
POST /auth/register
{
  "email": "you@example.com",
  "password": "yourpassword"
}
```

**2. Log in** (form-encoded, per OAuth2 spec) → returns a JWT

**3. Submit a task**
```http
POST /tasks
Authorization: Bearer <token>
{
  "input_text": "Research Cloud Computing, summarize it, and write a professional email."
}
```
Returns immediately with `status: "pending"`.

**4. Poll for the result**
```http
GET /tasks/{id}
```
```json
{
  "status": "completed",
  "plan": ["research", "summary", "email"],
  "steps_output": {
    "research": "...",
    "summary": "...",
    "email": "..."
  },
  "final_result": "... the generated email ..."
}
```

---

## Notable implementation details

- **Object-level authorization** — every task query is scoped to `user_id`, and a task belonging to another user returns `404` (not `403`), avoiding existence leakage (OWASP API Security Top 10 #1).
- **Full execution trace, not just the final answer** — `steps_output` stores each agent's output independently, making the pipeline debuggable when output quality is off, since LLM output is non-deterministic.
- **Provider-agnostic LLM seam** — all agents call a single `call_gemini()`-style adapter function; swapping the underlying provider (this project moved from Gemini to Groq mid-build) touches one file, not every agent.
- **Non-root container user** — the Docker image runs as an unprivileged user rather than root, following container security best practice.

---

## Possible extensions

- Conditional/branching graph edges (e.g., skip research for purely factual short inputs)
- WebSocket support for live status updates instead of polling
- Refresh tokens alongside short-lived access tokens
- Rate limiting per user on `POST /tasks`