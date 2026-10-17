# Architecture

## Initial decisions

- The repository is split into `frontend`, `backend`, and `docs`; infrastructure
  configuration currently lives at the root in Docker Compose and service
  Dockerfiles.
- The frontend uses Next.js App Router, React, TypeScript, and Tailwind CSS.
- Redux Toolkit owns client authentication state and RTK Query calls the
  versioned API. Framer Motion is used for the authentication panel.
- The API uses FastAPI, SQLAlchemy's asynchronous PostgreSQL driver, and Alembic.
- PostgreSQL is the system of record. Redis and RabbitMQ are provisioned for
  Celery task results and asynchronous AI document indexing/question jobs.
- School knowledge documents are stored in S3 (LocalStack in local Compose) and
  indexed in per-school Chroma collections. LlamaIndex extracts text; FastEmbed
  creates lazy-loaded local embeddings; a LangGraph agent invokes a LangChain
  retrieval tool and a configured OpenAI, Gemini, Ollama, or HuggingFace model.
- The MCP server uses stdio and validates the caller's bearer JWT before
  resolving the school from the database. Nginx is the local HTTP reverse proxy.
- Services read configuration from environment variables. `.env.example`
  documents local values; real secrets must be generated and supplied outside
  source control.
- API documentation is generated from FastAPI OpenAPI at `/api/v1/docs`.
- HTTP request logs are structured JSON and include a server-generated request
  identifier. Liveness does not depend on infrastructure; readiness checks
  PostgreSQL and returns 503 if the database cannot be reached.

## Tenant and identity

Schools are tenant roots. Public onboarding creates a school and its first
`school_admin` in one database transaction. Users currently belong to exactly
one school and carry one of the initial school-admin, teacher, student, or
parent roles. Fine-grained role authorization, multi-school membership, and
tenant-scoped business entities still need to be implemented before ERP data is
introduced. Client-supplied school IDs must never serve as authorization.

## Security baseline and gaps

Passwords are hashed with Argon2. Login uses the OAuth2 password form and
returns a short-lived HS256 JWT; `/auth/me` validates the bearer token and
resolves its user from the database. The browser holds that access token only in
Redux memory, so a page reload requires signing in again. Refresh-token
rotation, password recovery, login throttling, fine-grained authorization, and
tenant-scoped business APIs are not implemented.

Production mode rejects the sample JWT secret. Production deployment must also
provide a generated secret, TLS, restricted network access, a migration
execution policy, and a reviewed tenant-isolation design before handling
school data.
