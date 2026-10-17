# Delivery progress

Updated: 2026-10-17

## Current milestone: AI-enabled school workspace

- [x] Repository skeleton and environment-variable template.
- [x] FastAPI application, structured request logs, and liveness/readiness routes.
- [x] Async PostgreSQL connection and Alembic migration environment.
- [x] Next.js App Router, TypeScript, Tailwind, and responsive landing page.
- [x] React Testing Library and Vitest unit-test foundation.
- [x] Docker Compose services for PostgreSQL, Redis, RabbitMQ, API, and frontend.
- [x] School registration, administrator login, JWT bearer authentication, and current-user endpoint.
- [x] School/user SQLAlchemy models and initial tenant/auth migration.
- [x] Redux Toolkit, RTK Query, Framer Motion, and frontend registration/login/dashboard flow.
- [x] Celery workers with RabbitMQ broker and Redis result backend.
- [x] S3 document storage, ChromaDB vector search, LlamaIndex parsing, and a LangGraph/LangChain RAG agent.
- [x] OpenAI, Gemini, Ollama, and HuggingFace provider adapters.
- [x] Token-validated MCP stdio knowledge search and an AI assistant frontend.
- [x] Nginx reverse proxy, LocalStack S3 service, and Render/Railway deployment configurations.
- [x] GitHub Actions checks for frontend, backend, and container builds.
- [x] Backend pytest, Ruff, and Alembic upgrade/schema parity checks.
- [x] Frontend type-check, lint, unit tests, and production build.
- [x] Docker Compose configuration validation.
- [ ] Run the full Compose stack against PostgreSQL and verify end-to-end startup.
- [ ] Add Playwright end-to-end browser tests.

## ERP feature status

School onboarding and bearer authentication are implemented. Tenant membership
and role records exist, but fine-grained authorization and tenant-scoped academic
APIs are not implemented yet. Teacher/student/class/subject/schedule management,
attendance, grading, finance, library, notifications, realtime messaging,
general-purpose storage, and analytics remain future modules.

## Stack status

- Frontend: Next.js, React, TypeScript, Tailwind CSS, Redux Toolkit, RTK Query,
  and Framer Motion are installed and used.
- Backend: FastAPI, PostgreSQL/SQLAlchemy, Alembic, and JWT/OAuth2 are used.
  Redis is the Celery result backend and RabbitMQ is the Celery broker.
- AI: OpenAI, Gemini, LangChain, LangGraph, LlamaIndex, ChromaDB, RAG,
  LangGraph agent, Ollama, HuggingFace, and MCP are integrated.
- Infrastructure: Docker, Compose, Nginx, S3 integration, Render/Railway
  deployment configuration, and GitHub Actions are included.

## Next implementation sequence

1. Run the full Compose stack against PostgreSQL and verify end-to-end startup.
2. Add refresh-token lifecycle, recovery, throttling, and authentication security hardening.
3. Deliver tenant-scoped people, classes, schedules, attendance, and grading APIs.
4. Add document deletion/re-indexing, PDF support, and AI response/source citations.
5. Set production credentials and exercise both hosting blueprints in their provider dashboards.
