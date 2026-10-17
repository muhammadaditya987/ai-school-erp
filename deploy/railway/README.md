# Railway services

Create separate Railway services from the repository. In each service's
Settings, set its Railway Config File path to the corresponding configuration:

| Service | Railway config |
| --- | --- |
| API | `deploy/railway/api.toml` |
| Celery worker | `deploy/railway/worker.toml` |
| Frontend | `deploy/railway/frontend.toml` |

These Railway Dockerfiles use the repository root as the build context; leave
each service's root directory at the repository root.

Add Railway PostgreSQL and Redis plugins, and provision a RabbitMQ broker and
an AWS S3 bucket. Set `DATABASE_URL`, `REDIS_URL`, `RABBITMQ_URL`, `JWT_SECRET_KEY`,
`S3_BUCKET`, `S3_REGION`, `S3_ACCESS_KEY_ID`, and `S3_SECRET_ACCESS_KEY` on both
the API and worker. Set the same `AI_PROVIDER` and its provider-specific API
key/model on the API and worker. Set `API_INTERNAL_URL` on the frontend to the
private API URL with the `/api/v1` prefix.

Use a shared Chroma server (`CHROMA_HOST` and `CHROMA_PORT`) for API/worker
instances; do not use per-container ephemeral Chroma directories in a scaled
deployment. Run `alembic upgrade head` as a one-off release command before
starting API replicas. Keep API and worker secrets synchronized with Railway
shared variables and restrict network access to private service addresses.
