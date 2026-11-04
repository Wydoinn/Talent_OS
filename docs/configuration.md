# Configuration Reference

## 1. Environment files

Copy the supplied templates before running the application:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

The backend settings use service-specific prefixes. The templates contain placeholders only. Populate only the values required by your deployment.

## 2. Frontend

| Variable | Description |
|---|---|
| `APP_URL` | Public URL used by the server-rendered frontend runtime. |
| `AUTH_API_BASE_URL` | Browser-facing base URL for authentication requests. |
| `ORCHESTRATION_API_BASE_URL` | Browser-facing base URL for orchestration requests. |
| `DEV_HOST` | Development server host binding. |

## 3. Authentication service (`AUTH_`)

| Variable | Description |
|---|---|
| `AUTH_DATABASE_URL` | PostgreSQL connection URL for authentication data. |
| `AUTH_JWT_SECRET_KEY` | Secret used to sign authentication tokens. |
| `AUTH_OTP_SECRET` | Secret used by OTP-related security functions. |
| `AUTH_CORS_ALLOW_ORIGINS` | Comma-separated browser origins allowed by the API. |
| `AUTH_SMTP_*` | Mail host, port, account, sender, and transport settings. |
| `AUTH_PINECONE_API_KEY` | Optional vector-index credential used by identity workflows. |
| `AUTH_PINECONE_INDEX_NAME` | Configured identity index name. |
| `AUTH_ORCHESTRATION_SERVICE_URL` | Internal orchestration endpoint. |
| `AUTH_ORCHESTRATION_SERVICE_TOKEN` | Credential for authenticated internal requests. |
| `AUTH_FACE_MODEL_ROOT` | Root directory for local face assets. |

## 4. Resume analysis service (`ATS_`)

| Variable | Description |
|---|---|
| `ATS_DATABASE_URL` | PostgreSQL connection URL for resume analysis data. |
| `ATS_CORS_ALLOWED_ORIGINS` | Allowed browser origins. |
| `ATS_MODELS_DIR` | Root directory for local analysis assets. |
| `ATS_EMBEDDING_MODEL_DIR` | Directory containing the configured embedding assets. |
| `ATS_RERANKER_MODEL_DIR` | Directory containing the configured reranking assets. |
| `ATS_RESUME_SOURCE_DIR` | Directory scanned for candidate resume files. |
| `ATS_PINECONE_*` | Optional vector-index settings. |
| `ATS_NEO4J_*` | Optional graph database connection settings. |

## 5. Orchestration service (`ORCH_`)

| Variable | Description |
|---|---|
| `ORCH_DATABASE_URL` | PostgreSQL connection URL for orchestration data. |
| `ORCH_AUTH_JWT_SECRET_KEY` | Must match the authentication service signing secret. |
| `ORCH_INTERNAL_SERVICE_TOKEN` | Shared credential for internal service calls. |
| `ORCH_AUTHENTICATION_SERVICE_URL` | Authentication API base URL. |
| `ORCH_ATS_SERVICE_URL` | Resume analysis API base URL. |
| `ORCH_ANTI_SPOOFING_SERVICE_URL` | Session verification API base URL. |
| `ORCH_CANDIDATE_PORTAL_BASE_URL` | Candidate-facing application URL used in notifications. |
| `ORCH_CORS_ALLOWED_ORIGINS` | Allowed browser origins. |
| `ORCH_STT_*` | Local speech transcription backend, asset directory, device, and runtime settings. |
| `ORCH_AI_API_URL` | Optional chat-completions-compatible generation endpoint. |
| `ORCH_AI_API_KEY` | Credential for the configured generation endpoint. |
| `ORCH_AI_DEPLOYMENT_ID` | Deployment identifier accepted by the configured endpoint. |
| `ORCH_SMTP_*` | Mail configuration used by orchestration notifications. |

The optional generation endpoint must accept a JSON request with `model`, `messages`, `temperature`, and `max_tokens`, and return generated text in a compatible response structure. The service supports response text in `choices[0].message.content`, `choices[0].text`, `output_text`, or `text`. Configure an endpoint that satisfies this contract.

## 6. Anti-spoofing service (`ANTI_SPOOFING_`)

| Variable | Description |
|---|---|
| `ANTI_SPOOFING_JWT_SECRET_KEY` | Shared signing secret for validated internal requests. |
| `ANTI_SPOOFING_ALLOWED_ORIGINS` | Allowed browser origins. |
| `ANTI_SPOOFING_MODELS_DIR` | Root directory for local verification assets. |
| `ANTI_SPOOFING_SESSION_STORE_BACKEND` | `memory` for local use or `redis` for shared session state. |
| `ANTI_SPOOFING_REDIS_URL` | Redis connection URL when Redis storage is enabled. |
| `ANTI_SPOOFING_STT_BACKEND` | Speech verification backend or `disabled`. |
| `ANTI_SPOOFING_DEVICE` | Runtime device setting for local inference assets. |

## 7. Security requirements

Use long, unique secrets per environment. Keep `.env` files out of version control. Set explicit HTTPS origins in production and avoid wildcard CORS. Use TLS for database, cache, and service-to-service traffic whenever supported.
