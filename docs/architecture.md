# Architecture Overview

## 1. System context

TalentOS is a web-based recruitment workflow platform. The browser client communicates with a set of independently hosted APIs. Each backend service owns a focused business capability and communicates with peer services through configured HTTP endpoints and shared data contracts.

## 2. Components

| Component | Responsibility | Local port |
|---|---|---:|
| Angular frontend | Manager workspace, candidate portal, assessments, and reporting views | 3000 |
| Authentication API | OTP flows, candidate identity registration, and authentication tokens | 8000 |
| Orchestration API | Jobs, candidate pipeline, assessment sessions, scheduling, and notifications | 8001 |
| Anti-spoofing API | Session integrity, liveness, identity consistency, and challenge verification | 8080 |
| Resume analysis API | Document parsing, resume analysis, and candidate matching | 8090 |

## 3. Primary workflows

### Candidate onboarding

The frontend sends sign-up and verification requests to the Authentication API. The service validates OTP workflows, persists account data, and coordinates configured identity checks.

### Resume ingestion and matching

The Resume Analysis API reads configured resume sources, extracts document content, derives matching signals, and returns candidate analysis to the orchestration layer. The Orchestration API associates results with jobs and candidate records.

### Assessment lifecycle

The Orchestration API creates assessment sessions, issues prompts, records answers, and aggregates assessment results. The frontend presents the candidate experience and reports. The Anti-spoofing API performs session verification and returns integrity signals to orchestration.

### Notifications and scheduling

The Orchestration API manages interview slots, candidate invitations, reminders, and email delivery through the configured mail service.

## 4. Data and infrastructure

- PostgreSQL stores service-owned application records. Use separate databases or schemas according to the deployment's ownership boundaries.
- Redis may be used for session state when the anti-spoofing session store is configured for Redis.
- A vector index and optional graph database support configured candidate retrieval and relationship analysis.
- Runtime computer-vision, speech, embedding, and ranking assets are provisioned outside this source package.
- Secrets and service URLs are supplied through environment variables.

## 5. Design boundaries

The browser should call the public frontend-facing APIs only. Internal service credentials must remain server-side. Service URLs, secrets, storage paths, and allowed browser origins must be environment-specific.

For service dependencies, setup requirements, and known source omissions, see [Source Inventory](source_inventory.md) and [Configuration](configuration.md).
