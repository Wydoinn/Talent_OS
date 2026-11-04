# Deployment Guide

## 1. Deployment model

Deploy the frontend and each backend API as independently managed services. Keep internal APIs on private networking where possible; expose only the routes required by the browser client.

## 2. Production checklist

- Build the frontend with `npm ci` and `npm run build`.
- Install backend dependencies from the pinned requirements file in a clean virtual environment or immutable image.
- Provision PostgreSQL databases, apply schema migrations, and configure automated backups.
- Provision Redis when shared anti-spoofing session storage is required.
- Configure vector and graph services where enabled.
- Provision all local runtime assets to the paths configured for each service.
- Set unique secrets, database URLs, internal service tokens, SMTP credentials, and public URLs through the deployment secret manager.
- Configure HTTPS, trusted proxy headers, request size limits, and explicit CORS origins.
- Configure health checks, restart policies, resource requests/limits, and log collection.
- Validate service-to-service connectivity before enabling candidate access.

## 3. Network and ports

The local development ports are listed in [Architecture](architecture.md). In production, assign private service addresses and expose the frontend plus only approved API endpoints through the ingress or reverse proxy. Do not publish internal service tokens or database endpoints to the browser.

## 4. Runtime process

Run each API under a process manager or container orchestrator with one clearly defined command, a non-root user, read-only application files where practical, and explicit writable directories for temporary uploads and logs. Configure graceful shutdown and appropriate worker counts for each workload.

## 5. Health and observability

Use each service's health endpoint to confirm process availability. Add readiness checks for dependencies and local assets before directing traffic. Collect structured logs, request identifiers, error rates, latency, queue depth where applicable, and database/cache health. Avoid logging OTP values, tokens, resume contents, or raw assessment recordings.

## 6. Backups and recovery

Back up service databases and required configuration metadata. Keep runtime assets in a controlled artifact store with versioning and integrity checks. Test database restore and service recovery procedures periodically.

## 7. Release validation

Run the checks in [Testing](testing.md), validate the exact deployed environment variables, and exercise one end-to-end candidate workflow using synthetic data before opening the release to users. Review [Known Limitations](source_inventory.md) before using this source package as a complete production release.
