# Troubleshooting

## Database connection failures

Confirm the database is reachable from the service container, the database exists, the URL has the correct driver, and the configured credentials have the required permissions. Check migration status before restarting the service.

## OTP or email delivery failures

Check SMTP host, port, sender address, credentials, TLS settings, and outbound network rules. Review service logs for delivery errors without recording OTP values or passwords.

## Service-to-service errors

Confirm the configured service base URLs, private DNS, ports, TLS certificates, and internal service tokens. Test health endpoints from the calling service's network namespace.

## Resume ingestion problems

Confirm the resume source directory exists and is readable, file extensions are supported, parsing dependencies are installed, and storage/vector/graph services are reachable when enabled. Use synthetic PDF or DOCX documents for repeatable tests.

## Camera, microphone, or verification failures

Confirm the browser is served over HTTPS or localhost, the candidate has granted permissions, and the verification service has its required runtime assets. Review readiness output and service logs for missing assets.

## Speech transcription unavailable

Confirm the speech backend is enabled, its configured asset directory exists, required audio dependencies are installed, and the host has adequate CPU/GPU and memory resources. The assessment can only use spoken-answer capture when the configured transcription service is ready.

## Generation endpoint errors

Confirm the endpoint URL, credential, deployment identifier, network route, and expected request/response schema. The integration requires a chat-completions-compatible JSON contract; a generic text-generation endpoint with a different contract will need an adapter.

## Frontend API errors

Check `AUTH_API_BASE_URL` and `ORCHESTRATION_API_BASE_URL`, ensure browser origins are allowed by the APIs, and confirm the frontend is not using stale local storage values for service URLs.
