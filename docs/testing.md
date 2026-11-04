# Testing and Validation

## 1. Python syntax check

From the repository root:

```bash
python -m compileall -q backend
```

This checks Python syntax without importing runtime dependencies or connecting to external services.

## 2. Backend tests

Run each test suite from its service directory:

```bash
cd backend/authentication && pytest
cd backend/orchestration && pytest
cd backend/ats_parser_checker && pytest
cd backend/anti_spoofing && pytest
```

Provide test database configuration and required fixtures as described by each test module. Do not point test runs at production databases or candidate directories.

## 3. Frontend tests

```bash
cd frontend
npm ci
npm run lint
npm test
npm run build
```

## 4. Integration validation

Validate health endpoints and service connectivity, then execute a synthetic end-to-end scenario: manager sign-in, job creation, resume ingestion, candidate review, invitation, schedule booking, candidate sign-in, assessment completion, and manager report review.

## 5. Scope and validation status

The delivered source package omits two application model packages that are imported by the orchestration and resume analysis services. Full runtime and integration tests cannot be considered complete until those source packages are restored from the authoritative project repository. See [Source Inventory](source_inventory.md).
