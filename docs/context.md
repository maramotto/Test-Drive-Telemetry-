# context.md — Test Drive Telemetry

Context for anyone (human or AI assistant) working on this repository. Read this before writing code.

## What this project is

A backend platform that ingests vehicle test-drive telemetry, processes it asynchronously and exposes results through a REST API and a simple web dashboard. It simulates the kind of R&D data platform an automotive company runs on the cloud: engineers upload raw test-drive files, the platform validates them, computes KPIs and data-quality reports, and makes results queryable per run, per vehicle and across the fleet.

It is a portfolio project built over a weekend (~30 hours) to exercise a specific stack and to learn Azure coming from AWS. It is deployed and publicly accessible.

**Priorities, in order:** correctness and robustness of the pipeline → clean, defensible design decisions → working Azure deployment → documentation → UI. The UI is deliberately plain.

## Data

- **Source:** "Battery and Heating Data in Real Driving Cycles", TUM (Technical University of Munich), IEEE DataPort / Kaggle. 72 real trips of a 2014 BMW i3 (60 Ah) in Munich, sampled at 10 Hz, summer and winter. Signals: environment (ambient temperature, elevation), vehicle (speed, throttle), battery (voltage, current, temperature, SoC), heating circuit (cabin temperature, heating power). Cite it in the README.
- **Synthetic fleet:** `scripts/generate_fleet.py` turns the real trips into a test fleet of 8–10 vehicles (`TST-001`...) using NumPy with a fixed seed: battery ageing, sensor noise, data gaps, out-of-order timestamps and injected anomalies (temperature spikes, frozen sensors). Always document what is real and what is synthetic.
- **OEM-agnostic by design:** ingestion goes through source adapters. The TUM/BMW adapter is just the first one; another OEM or internal format means a new adapter, not changes to the pipeline.
- Raw data lives in `data/` and is git-ignored, except small samples in `data/samples/` used by tests.

## Stack

- Python 3.12, Django, Django REST Framework, drf-spectacular (OpenAPI)
- PostgreSQL — relational metadata (psycopg)
- MongoDB — processed telemetry and analytics (PyMongo, no ODM)
- pandas / NumPy — processing and KPIs
- Celery with Redis as broker
- django-storages — local filesystem locally, Azure Blob Storage in the cloud
- Django templates + Pico.css/Bootstrap (CDN) + Chart.js + HTMX — no JS framework
- pytest, pytest-django, ruff, pre-commit
- Docker / docker-compose locally; Azure in the cloud

## Architecture

```
Client / Web ──► Django + DRF (web) ──► PostgreSQL  (vehicles, campaigns, test runs + status)
                        │
                        ├──► Blob Storage / local FS  (raw CSV files)
                        │
                        └──► Redis (broker) ──► Celery worker
                                                   │ adapter → quality → KPIs
                                                   └──► MongoDB (results, time series)
```

Flow: `POST /api/test-runs/` stores the file, creates a `TestRun` in `PENDING`, enqueues `process_test_run(run_id)` and returns `202 Accepted`. The worker moves the run to `PROCESSING`, writes results to MongoDB and ends in `DONE` or `FAILED`. Clients poll the run's status.

### Data model

**PostgreSQL (Django ORM)**
- `Vehicle`: code, model, year, nominal battery capacity
- `TestCampaign`: name, season, goal
- `TestRun`: vehicle, campaign, file, SHA-256 hash (unique), status `PENDING | PROCESSING | DONE | FAILED`, error, timestamps

**MongoDB (PyMongo)**
- `run_results`: one document per run, keyed by `run_id` — KPIs + embedded data-quality report
- `run_timeseries`: downsampled 1 Hz series per run, kept separate because it grows unbounded
- Indexes on `run_id`, `vehicle_code`, `campaign`

Run status is the source of truth in PostgreSQL. There are no cross-database transactions; the worker writes to MongoDB first (idempotent upsert) and then updates the status.

### KPIs and quality checks

- KPIs: distance, energy consumed and recovered (V·I integrated, split by sign), kWh/100 km, ΔSoC, max battery temperature and time above threshold, harsh acceleration/braking events, heating share of consumption.
- Quality: null % per column, time gaps, non-monotonic timestamps, frozen sensors (rolling std ≈ 0), out-of-range values.

## Repository layout

```
app/                 Django project and apps
  telemetry/         models, serializers, views, tasks
  telemetry/adapters/  source adapters (SourceAdapter, TumBmwI3Adapter)
  telemetry/processing/  quality checks and KPIs (pure functions)
  mongo.py           shared PyMongo client
  web/               templates and views for the dashboard
scripts/             fleet generator, bulk upload
data/samples/        small sample files for tests
docs/adr/            architecture decision records
docs/engineering-log.md  problems found and how they were solved
infra/               Azure scripts (az cli / Bicep)
.github/workflows/   CI and deployment
```

## Conventions

- **Git:** one branch and one PR per step. PR description: what, why, how to test. Conventional Commits (`feat:`, `fix:`, `chore:`, `docs:`, `test:`). `main` is protected; everything goes through PRs and CI must be green.
- **Configuration:** everything through environment variables (12-factor). `.env.example` lists them all. The same image runs locally and in Azure; only variables change. No secrets in code, images or CI variables.
- **Processing code:** pure, vectorised functions (no `DataFrame.apply` on rows unless justified), fully unit-tested with sample files. Canonical column names and SI-friendly units after the adapter.
- **Celery tasks:** receive ids, never objects. Idempotent (upsert by `run_id`, status checks). `acks_late=True`. Retry with backoff only for transient errors (network, storage), never for invalid data. Structured logs including `run_id`.
- **API:** DRF ViewSets, pagination, filtering with django-filter, `select_related`/`prefetch_related` to avoid N+1. Public read, token-protected writes. `202` for accepted uploads, `409` for duplicate files.
- **Tests:** pytest. Every PR adds or updates tests. Query-count assertions on list endpoints.
- **Language:** code, comments, docs, UI and commit messages in English.
- **Style:** ruff for linting and formatting. Prefer simple and explicit over clever.

## Azure deployment

| Component | Azure service | AWS equivalent |
|---|---|---|
| Web + worker + Redis | Container Apps (one environment, three apps) | ECS / Fargate |
| Images | Azure Container Registry | ECR |
| Relational DB | Azure Database for PostgreSQL Flexible Server | RDS |
| Document DB | Cosmos DB for MongoDB | DocumentDB |
| Raw files | Blob Storage (private container `raw-runs`) | S3 |
| Secrets | Key Vault, referenced from Container Apps | Secrets Manager |
| Identity | User-assigned Managed Identity + RBAC | IAM roles |
| Logs | Log Analytics | CloudWatch |
| CI/CD auth | GitHub Actions with OIDC federated credentials | OIDC to IAM role |

- Everything lives in one resource group, `rg-telemetry-demo`, with a budget alert.
- The managed identity has `Storage Blob Data Contributor`, `Key Vault Secrets User` and `AcrPull`. Code uses `DefaultAzureCredential`; no storage keys.
- Worker has no ingress and scales on Redis queue length (KEDA), minimum 0 replicas.
- Redis runs as a container with internal TCP ingress to keep demo costs low (see ADR).
- Check aggregation pipelines against Cosmos DB: MongoDB compatibility is not complete.

## Decisions (ADRs)

- ADR-001 — PostgreSQL for relational metadata, MongoDB for processed telemetry
- ADR-002 — PyMongo over an ODM/ORM for the analytics layer
- ADR-003 — Cosmos DB for MongoDB vs MongoDB Atlas on Azure
- ADR-004 — Redis as a container instead of a managed Redis for the demo

Write new ADRs in `docs/adr/` as short files: context, decision, consequences.

## Scope and non-goals

- In scope: ingestion, validation, KPIs, async processing, analytics API, Azure deployment, simple dashboard, documentation.
- Out of scope: real authentication/SSO, multi-tenancy, ML models, polished UI, production-grade observability, high availability. Mention them as "what I would do for production" instead of building them.

## Plan and status

Progress is tracked as percentage of completion. Update this section as steps are merged.

| Phase | Range | Status |
|---|---|---|
| 0 · Data and foundations | 0–8 % | not started |
| 1 · Local skeleton (compose, Django, Celery, CI) | 8–18 % | not started |
| 2 · Relational domain and API | 18–32 % | not started |
| 3 · Data pipeline (fleet, adapters, KPIs, Celery, aggregations) | 32–55 % | not started |
| 4 · Azure | 55–78 % | not started |
| 5 · Web | 78–88 % | not started |
| 6 · Documentation and demo | 88–100 % | not started |

Cut order if short on time: CI/CD to Azure → KEDA scaling → live upload from the web → fleet-wide comparisons.
Never cut: task idempotency, Managed Identity + Key Vault, engineering log.

## Notes for AI assistants

- Stay within the current step's scope; don't add dependencies or features not listed here without saying so.
- When a change involves a design decision, propose an ADR entry.
- When something surprising happens (library quirk, Azure difference, data issue), suggest an entry for `docs/engineering-log.md`.
- Prefer small, reviewable diffs with tests.
