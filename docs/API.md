# API

## Conventions

- Versioned endpoints use `/api/v1`.
- Interactive Swagger UI: `/api/v1/docs`.
- OpenAPI schema: `/api/v1/openapi.json`.
- ReDoc: `/api/v1/redoc`.
- JSON error responses use FastAPI's standard `detail` field.
- Every response includes a server-generated `X-Request-ID`; request logs
  include the same identifier.

## Foundation endpoints

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/health/live` | None | Process liveness; does not access dependencies. |
| GET | `/api/v1/health/ready` | None | PostgreSQL readiness; returns 503 when unavailable. |

Health endpoints are infrastructure probes. Protect all future business
endpoints with authentication, authorization, and tenant scoping.
