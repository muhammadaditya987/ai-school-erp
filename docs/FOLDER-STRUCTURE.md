# Folder structure

```text
.
├── backend/
│   ├── alembic/             # Migration environment and revisions
│   ├── app/
│   │   ├── api/             # Versioned API routes
│   │   ├── core/            # Settings and logging
│   │   └── db/              # SQLAlchemy base and session
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── docs/                    # Architecture, API, database, and delivery docs
├── frontend/
│   ├── public/
│   ├── src/app/             # Next.js App Router
│   ├── vitest.config.mts    # Frontend unit-test configuration
│   ├── Dockerfile
│   └── package.json
└── docker-compose.yml       # Local service topology
```

The requested `infrastructure`, `docker`, and `tests` top-level directories
will be introduced when their contents warrant separate ownership. Backend
tests currently live next to the backend service. Redis, RabbitMQ, reverse
proxy, object storage, AI integrations, and CI deployment workflows are not yet
implemented as application capabilities.
