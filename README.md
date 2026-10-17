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

Redis and RabbitMQ are provisioned for future feature work; no current app
feature depends on them. The current Alembic baseline creates no business
tables.

## Backend development

Requires Python 3.12+. From `backend/`, install the project and development
dependencies with `python -m pip install -e ".[dev]"`, then run the API with
`uvicorn app.main:app --reload`. Run `alembic upgrade head` to apply migrations,
`pytest` for backend tests, and `ruff check app tests alembic` for linting.
Provide `DATABASE_URL` in the environment when connecting to PostgreSQL.

## Frontend development

Requires Node.js 22+. From `frontend/`, run `npm ci`, then `npm run dev`.
Use `npm run typecheck`, `npm run lint`, and `npm run build` to validate changes.
Run `npm test` for the React Testing Library unit tests.
