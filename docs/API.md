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

## Authentication and school onboarding

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/register` | None | Create a school and its first `school_admin` account. |
| POST | `/api/v1/auth/token` | OAuth2 password form | Exchange email/password for a short-lived JWT access token. |
| GET | `/api/v1/auth/me` | Bearer JWT | Return the authenticated user and their school ID. |

Registration accepts `school_name`, a unique lowercase kebab-case
`school_slug`, `full_name`, `email`, and a password of at least 12 characters.
The token endpoint uses the OAuth2 form fields `username` (the email) and
`password`. Send its `access_token` as `Authorization: Bearer <token>`.

Access tokens expire after the configured `JWT_ACCESS_TOKEN_EXPIRE_MINUTES`
(15 minutes by default). The frontend currently keeps the token in memory, so
reloading the page ends the session. Refresh-token rotation and account recovery
are not implemented yet.

## AI knowledge assistant

| Method | Path | Authentication | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/ai/documents` | School admin or teacher | Upload UTF-8 `.txt`/`.md` (up to 5 MiB) to S3 and queue school-scoped indexing. |
| GET | `/api/v1/ai/documents` | School admin or teacher | List this school's indexed documents and statuses. |
| POST | `/api/v1/ai/ask` | School admin or teacher | Queue a question for the school's RAG agent; returns a job ID. |
| GET | `/api/v1/ai/jobs/{job_id}` | Job owner | Poll the job and read its result when complete. |

The worker parses uploads with LlamaIndex, creates a separate Chroma collection
per school with local FastEmbed embeddings, and answers questions using a
LangGraph agent with a LangChain retrieval tool. Configure `AI_PROVIDER` as
`openai`, `gemini`, `ollama`, or `huggingface`. A missing provider credential,
unavailable worker, or failed generation is reported as an error; no generated
answer is substituted. Completed answers and task state are stored in
PostgreSQL; Redis holds the Celery task result backend.

The optional MCP stdio server exposes `search_school_knowledge(query)`. Supply
the short-lived JWT via the MCP process's `MCP_ACCESS_TOKEN` environment
variable; the server verifies the JWT and school role before searching, rather
than accepting a client-selected school ID or putting a bearer token in tool
arguments.
