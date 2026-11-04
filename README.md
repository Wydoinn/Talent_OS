# TalentOS

TalentOS is a recruitment workflow platform that brings together candidate onboarding, resume analysis, hiring pipeline management, interview scheduling, candidate assessments, and integrity review.

## Capabilities

- Manager and candidate workflows through an Angular web application.
- OTP-based authentication and candidate identity registration.
- Resume parsing, profile enrichment, and job-to-candidate matching.
- Job pipeline, shortlist, invitation, and interview scheduling workflows.
- Structured assessments with written and optional spoken responses.
- Session integrity and liveness checks.
- Candidate and assessment reporting.
- Optional configurable text-generation integration for supported assistant and assessment workflows.

## Repository structure

```text
TalentOS-main/
├── backend/
│   ├── authentication/
│   ├── orchestration/
│   ├── ats_parser_checker/
│   ├── anti_spoofing/
│   ├── requirements.txt
│   └── .env.example
├── frontend/
├── docs/
├── run-all.sh
├── run-all.ps1
└── README.md
```

## Quick start

1. Review [Developer Guide](docs/developer.md) and [Configuration](docs/configuration.md).
2. Copy the environment templates and configure local services.
3. Provision PostgreSQL, optional Redis/vector/graph services, and required runtime assets.
4. Install backend and frontend dependencies.
5. Start the APIs and frontend using the commands in the Developer Guide.

## Documentation

| Document | Description |
|---|---|
| [Developer Guide](docs/developer.md) | Local setup, dependencies, service startup, and developer workflow. |
| [User Operations Manual](docs/user_mop.md) | Manager and candidate operating procedures. |
| [Architecture](docs/architecture.md) | Services, responsibilities, and data flows. |
| [Configuration](docs/configuration.md) | Environment variables and integration settings. |
| [Deployment](docs/deployment.md) | Production deployment and release checklist. |
| [Security](docs/security.md) | Secrets, personal data, and operational controls. |
| [Testing](docs/testing.md) | Unit, frontend, and integration validation. |
| [Troubleshooting](docs/troubleshooting.md) | Common setup and runtime issues. |
| [Source Inventory](docs/source_inventory.md) | Included files, excluded assets, and known limitations. |

## Service endpoints for local development

| Component | URL |
|---|---|
| Frontend | `http://localhost:3000` |
| Authentication API | `http://localhost:8000` |
| Orchestration API | `http://localhost:8001` |
| Anti-spoofing API | `http://localhost:8080` |
| Resume analysis API | `http://localhost:8090` |

API documentation is available at `/docs` for services that expose the FastAPI documentation route.

## License

See [LICENSE](LICENSE).
