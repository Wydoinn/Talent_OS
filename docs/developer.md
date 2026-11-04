# Developer Guide

## 1. Repository layout

- `frontend/` — Angular client application.
- `backend/authentication/` — authentication, candidate registration, and OTP workflows.
- `backend/orchestration/` — job, candidate, scheduling, assessment, and notification workflows.
- `backend/ats_parser_checker/` — resume parsing, analysis, and candidate matching.
- `backend/anti_spoofing/` — session verification, liveness, and integrity checks.
- `backend/requirements.txt` — shared Python dependencies.
- `docs/` — development, operations, architecture, and deployment guidance.

## 2. Prerequisites

- Python 3.10 or newer (use the version validated by your deployment environment).
- Node.js 20 or newer and npm.
- PostgreSQL.
- Redis when the session store is configured to use Redis.
- FFmpeg and platform libraries required by the computer-vision/audio dependencies.
- Runtime asset files required by resume retrieval and session verification. These assets are provisioned separately and are not included in this source package.

## 3. Configure the environment

From the repository root:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Update `backend/.env` with database URLs, authentication secrets, service tokens, mail settings, storage paths, and any optional integrations used by your environment. Do not commit populated environment files. See [Configuration](configuration.md).

## 4. Install dependencies

```bash
python3 -m venv backend/.venv
source backend/.venv/bin/activate
python -m pip install --upgrade pip
pip install -r backend/requirements.txt

cd frontend
npm ci
cd ..
```

On Windows PowerShell, activate the virtual environment with `backend\.venv\Scripts\Activate.ps1`.

## 5. Database preparation

Create separate PostgreSQL databases for authentication, orchestration, and resume analysis. Set the corresponding URLs in `backend/.env`. Apply the migration or schema bootstrap process used by your deployment before starting the services. Do not use production data in local development.

## 6. Start the application

The repository includes convenience launch scripts: `./run-all.sh` on Linux/macOS and `./run-all.ps1` on Windows. Both scripts check for required source packages before starting the complete stack. This source package is missing two such packages; restore them as described in [Source Inventory](source_inventory.md) before using the launch scripts. The local service ports are:

| Component | Port |
|---|---:|
| Frontend | 3000 |
| Authentication API | 8000 |
| Orchestration API | 8001 |
| Anti-spoofing API | 8080 |
| Resume analysis API | 8090 |

For controlled startup, run each service separately from `backend/`:

```bash
cd backend
python -m uvicorn authentication.app.main:app --host 127.0.0.1 --port 8000
python -m uvicorn orchestration.app.main:app --host 127.0.0.1 --port 8001
python -m uvicorn anti_spoofing.app.main:app --host 127.0.0.1 --port 8080
python -m uvicorn ats_parser_checker.app.main:app --host 127.0.0.1 --port 8090
```

Run one command per terminal. Start the frontend with `cd frontend && npm run dev`.

## 7. Quality checks

```bash
# Python syntax validation
python -m compileall -q backend

# Backend tests (run from each service directory)
cd backend/authentication && pytest
cd ../orchestration && pytest
cd ../ats_parser_checker && pytest
cd ../anti_spoofing && pytest

# Frontend checks
cd frontend
npm run lint
npm test
npm run build
```

A successful syntax check does not guarantee that external databases, runtime assets, or downstream services are available. Review [Testing](testing.md) and [Source Inventory](source_inventory.md) before treating this package as a complete deployment artifact.
