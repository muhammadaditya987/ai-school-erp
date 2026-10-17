# School ERP

The starting point for a multi-tenant School ERP built with Next.js and
FastAPI. The project is being delivered incrementally; consult
[delivery progress](./docs/PROGRESS.md) for implemented and outstanding work.

## Local development with Docker Compose

1. Copy `.env.example` to `.env` and replace every sample secret with a
   development-only value. Keep the PostgreSQL and RabbitMQ credentials in
   their respective URLs in sync if you change them.
2. Start the services:

   ```powershell
   docker compose up --build
   ```

3. Open the web app at `http://localhost:3000`. API documentation is at
   `http://localhost:8000/api/v1/docs`; the PostgreSQL readiness probe is at
   `http://localhost:8000/api/v1/health/ready`.
4. Apply migrations from the backend container:

   ```powershell
   docker compose exec backend alembic upgrade head
   ```

Redis and RabbitMQ back the Celery worker and job results. LocalStack provides
a local S3-compatible bucket for school knowledge documents. The school and AI
tables are created by Alembic migrations; apply them after the stack is healthy.
Open `http://localhost:8080` (or the frontend at `http://localhost:3000`),
register at `/register`, and sign in at `/login`. The protected dashboard is at
`/dashboard`; the AI assistant is at `/assistant`.

The AI assistant accepts UTF-8 text and Markdown documents up to 5 MiB. Set
`AI_PROVIDER` to `openai`, `gemini`, `ollama`, or `huggingface`, then provide the
matching API key or local endpoint/model in `.env`. The default provider is
OpenAI; AI requests fail explicitly until its API key is configured. The local
Ollama service is optional: start it with `docker compose --profile ai-local up`
and pull a model with `docker compose exec ollama ollama pull llama3.2`.

The MCP server uses stdio transport and validates the short-lived bearer token
configured in `MCP_ACCESS_TOKEN` before searching the same school-isolated
Chroma index. Set the token in the MCP client's process environment (do not add
it to tool arguments), then start the local server with
`docker compose --profile mcp run --rm mcp`.

See [Railway service setup](./deploy/railway/README.md) and the Render Blueprint
in [`render.yaml`](./render.yaml) for hosted deployment configuration. Production
requires externally provisioned PostgreSQL, Redis, RabbitMQ, S3, provider
credentials, TLS, and synchronized API/worker environment settings.

## Backend development

Requires Python 3.12+. From `backend/`, install the project, development, AI,
and MCP dependencies with `python -m pip install -e ".[dev,ai,mcp]"`, then run
the API with `uvicorn app.main:app --reload`. Run `alembic upgrade head` to
apply migrations, `pytest` for backend tests, and `ruff check app tests alembic`
for linting. Provide `DATABASE_URL` in the environment when connecting to
PostgreSQL. The
OAuth2 token endpoint is `/api/v1/auth/token`; send its short-lived JWT as a
Bearer token to protected API endpoints. See [API documentation](./docs/API.md)
for registration and login payloads.

## Frontend development

Requires Node.js 22+. From `frontend/`, run `npm ci`, then `npm run dev`.
Use `npm run typecheck`, `npm run lint`, and `npm run build` to validate changes.
Run `npm test` for the React Testing Library unit tests.
