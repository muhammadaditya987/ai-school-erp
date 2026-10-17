# Database

## Current foundation

- PostgreSQL 16 is the only configured database.
- SQLAlchemy 2 async sessions use `asyncpg` and `pool_pre_ping`.
- Alembic is configured under `backend/alembic`; models are registered through
  `backend/app/db/base.py`.
- The initial schema contains no application tables. Generate and review a
  migration whenever models are added; do not create or modify the schema with
  application startup code.

## Planned core entities

The tenant and identity model is not implemented. The initial design should
define schools/tenants, users, tenant memberships, roles/permissions, and audit
events before tenant-owned ERP entities. Each tenant-owned row must have an
explicit tenant relationship and access must be scoped server-side.

## Local database

Docker Compose provisions a named PostgreSQL volume. Database credentials and
the API connection string are configured via `.env`; do not use production
credentials for local development.
