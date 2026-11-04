# Security and Data Handling

## 1. Sensitive information

The application may process candidate names, contact details, resumes, assessment answers, voice recordings or transcripts, face-related data, and hiring decisions. Treat these records as confidential personal information.

## 2. Secrets and access

- Store credentials in a deployment secret manager.
- Use separate secrets for JWT signing, OTP protection, internal service authentication, databases, mail, and external integrations.
- Rotate secrets using a planned rollout so dependent services remain synchronized.
- Never commit populated environment files or paste credentials into issue trackers and logs.
- Restrict administrative and support access to the minimum required roles.

## 3. Network security

- Enforce HTTPS for all browser-facing endpoints.
- Use explicit CORS allowlists.
- Keep databases, caches, and internal APIs on private networks.
- Authenticate internal service calls and reject unauthenticated cross-service traffic.
- Apply request size limits, timeouts, and rate limits at the ingress and service layers.

## 4. Candidate data

- Use synthetic or approved test records in development and validation.
- Do not bundle candidate resumes, recordings, or screenshots in source-control packages.
- Define retention and deletion periods for resumes, recordings, transcripts, and assessment artifacts.
- Restrict access to raw documents and verification data; use derived signals only where appropriate.
- Avoid exposing unnecessary personal data in logs, exports, notifications, and error messages.

## 5. Hiring decisions

Automated matching, assessment scores, and integrity signals are decision-support information. Review the supporting evidence and apply the organization's hiring policy and applicable law before making decisions. Provide a review path for incorrect or incomplete automated results.

## 6. Operational controls

Patch dependencies, scan source and container images, monitor authentication anomalies, protect backups, and test recovery procedures. Report suspected exposure of candidate records or credentials through the organization's incident-response process.
