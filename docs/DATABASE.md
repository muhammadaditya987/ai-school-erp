# Database

## Current foundation

- PostgreSQL 16 is the only configured database.
- SQLAlchemy 2 async sessions use `asyncpg` and `pool_pre_ping`.
- Alembic is configured under `backend/alembic`; tenant and user models are
  registered in `backend/app/db/models.py`.
- Migration `0002_school_users` adds schools and users with unique school slugs,
  globally unique normalized emails, roles, and a school foreign key. Apply it
  with `alembic upgrade head`; schema changes must not run during app startup.

## Planned core entities

Schools are tenant roots, and every user is associated with one school. The
initial school administrator is created atomically with the school. Fine-grained
permissions, memberships for users belonging to multiple schools, audit events,
and tenant-owned academic records remain future work. Every future tenant-owned
row must have an explicit school relationship and be scoped server-side.

## Local database

Docker Compose provisions a named PostgreSQL volume. Database credentials and
the API connection string are configured via `.env`; do not use production
credentials for local development.
