# Architecture Overview

> Status: target architecture. Nothing below is implemented yet. This document
> describes where code will go and how the boundaries are drawn, so that future
> work lands in the right place.

## 1. Shape

AutoInspect-X is a **modular monorepo**, not a set of microservices. A capstone
project with one team and one deployment target gains nothing from network
boundaries between components, and loses reproducibility. See
`docs/decisions/0001-modular-monorepo.md`.

```
AutoInspect-X/
├── apps/
│   ├── web/            React + TypeScript frontend
│   └── api/            FastAPI backend
├── ml/
│   ├── datasets/       Dataset documentation — no large data in Git
│   ├── models/         Model definitions and registry
│   ├── training/       Training workflows
│   ├── inference/      Production inference code
│   ├── evaluation/     Metrics and benchmark evaluation
│   └── experiments/    Reproducible experiment configs and results
├── packages/
│   └── shared/         Genuinely shared types and contracts only
├── docs/
├── scripts/
├── tests/
└── automation/         Exported workflow definitions, if automation is added
```

Only `docs/` and `.github/` exist today. Every other directory is created when a
task needs it.

## 2. Dependency direction

```
web       → api contracts
api       → application → domain → infrastructure
ml        → datasets / models / evaluation
web      ↛ ml internals
api      ↛ training internals
training ↛ frontend
```

Cross-boundary imports are prohibited. The frontend talks to the backend over
HTTP contracts. The backend loads a model artefact through the inference layer;
it never imports training code.

## 3. Backend layering

```
Router / API layer      HTTP concerns: validation, status codes, serialisation
        ↓
Application service     Use cases, orchestration, transactions
        ↓
Domain                  Entities and rules — no framework imports
        ↓
Infrastructure          Database, storage, model runtime, external services
```

Business logic never lives in a route handler. A route parses the request,
delegates to an application service, and maps the result to a response.

Planned logical modules: `inspections`, `vehicles`, `damages`, `estimates`,
`reports`, `models`. None exists yet; each is created when its responsibilities
are known.

## 4. ML boundary

```
Dataset → Preprocessing → Training → Evaluation → Model artefact → Inference API
```

Training and inference are separate concerns with separate code paths. Training
code never ships inside the API application. The API depends on a versioned
model artefact resolved from configuration (`MODEL_PATH`, `MODEL_VERSION`), never
from a hard-coded path. See `docs/decisions/0003-separate-training-and-inference.md`.

## 5. Frontend structure

React with TypeScript in strict mode. Planned screens:

```
Dashboard · Inspection Upload · Inspection Result · Damage Visualization
Repair Estimate · Inspection History · Report · Settings
```

Every view handles loading, error, and empty states explicitly. The interface
must visibly separate an AI estimate from a final professional workshop
quotation — this is a correctness requirement, not a styling preference.

## 6. Runtime data flow

```
Browser
  │  upload image + vehicle metadata
  ▼
API router
  │  validate, persist the inspection record
  ▼
Application service
  │  call the inference layer
  ▼
Inference
  │  segmentation → damage features → fusion → action + cost quantiles
  ▼
Application service
  │  assemble the explainable report
  ▼
Browser
     overlay, features, estimate range, confidence, export
```

## 7. Storage

No database exists yet. When one is chosen, the decision is recorded as an ADR
covering the engine, the migration tool, and how model artefacts and uploaded
images are stored. Uploaded images are user data — see `SECURITY.md`.

## 8. Quality gates

```
format → lint → type check → unit tests → integration / E2E when applicable
```

GPU training never runs in CI. ML evaluation runs as an explicit experiment, not
as part of the application test suite.
