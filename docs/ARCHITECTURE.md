# Architecture

## Initial decisions

- The repository is split into `frontend`, `backend`, and `docs`; infrastructure
  configuration currently lives at the root in Docker Compose and service
  Dockerfiles.
- The frontend uses Next.js App Router, React, TypeScript, and Tailwind CSS.
- The API uses FastAPI, SQLAlchemy's asynchronous PostgreSQL driver, and Alembic.
- PostgreSQL is the system of record. Redis and RabbitMQ are provisioned for
  future cache, coordination, and asynchronous-work use; no feature currently
  depends on them.
- Services read configuration from environment variables. `.env.example`
  documents local values; real secrets must be generated and supplied outside
  source control.
- API documentation is generated from FastAPI OpenAPI at `/api/v1/docs`.
- HTTP request logs are structured JSON and include a server-generated request
  identifier. Liveness does not depend on infrastructure; readiness checks
  PostgreSQL and returns 503 if the database cannot be reached.

## Tenant isolation

Tenant models and request authorization have not been implemented. Before
business data is introduced, tenant ownership and authorization must be enforced
at the API and persistence boundaries; client-supplied tenant IDs must never
serve as authorization.

## Security baseline and gaps

The foundation exposes no business data and has no authentication endpoints.
JWT configuration is reserved but is not yet used. Production deployment must
provide strong secrets, TLS, restricted network access, a migration execution
policy, and a reviewed tenant-isolation design before handling school data.
