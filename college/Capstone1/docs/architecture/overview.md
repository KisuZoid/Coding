# Architecture Overview

> Status: **implemented.** Phases A–R of the product build are complete
> (2026-09-08). This document describes the running system. The original
> target-architecture document was superseded by this one.

## 1. Shape

AutoInspect-X is a **modular monorepo**, not a set of microservices. A capstone
project with one team and one deployment target gains nothing from network
boundaries between components, and loses reproducibility. See
`docs/decisions/0001-modular-monorepo.md`.

```
AutoInspect-X/
├── apps/
│   ├── web/            Next.js (App Router) frontend — cinematic intro + demo journey
│   └── api/            FastAPI backend — routers, agent, storage, vision, cost, repair
├── ml/
│   ├── datasets/       Dataset adapters and audit (CarDD COCO)
│   ├── training/       Training workflows (never imported by the API — ADR 0003)
│   ├── inference/      Production inference path used by the API (ADR 0003)
│   ├── evaluation/     Metrics / benchmark evaluation (research side)
│   ├── analysis/       Error analysis / visualisation helpers (research side)
│   └── experiments/    Registry + per-run records (checkpoints git-ignored)
├── docs/
│   ├── decisions/      ADRs 0001–0009
│   └── architecture/   This overview, gap report (superseded), cost readiness
├── public/             4 demo clips served to the frontend (video.mapped timeline)
├── tests/              Pytest suite (API-level + backend E2E, 123 tests)
├── storage/            SQLite ledger + session-scoped image files (ephemeral)
├── data/training/      Consented training samples (user-consented-v1)
├── .github/workflows/  ci.yml (backend, frontend, Playwright jobs)
├── pyproject.toml      ruff/mypy/pytest config; dev tool group (uv); package=false
├── uv.lock
└── requirements-ci.txt CPU-runtime subset of the `ai` env for CI runners
```

## 2. Dependency direction

```
web       → api contracts (typed client in apps/web/lib)
api       → application → domain → infrastructure
ml/inference ≠ ml/training (ADR 0003: the API never imports training code)
web      ↛ ml internals
```

Cross-boundary imports are prohibited. The frontend talks to the backend over
HTTP contracts (`/health`, `/inspection/session`, `/chat`,
`/inspection/{id}/upload`, `/inspection/{id}/analyze`,
`/inspection/{id}`, DELETE). The backend loads a model artefact only through
`ml/inference` (`SegmentationEngine`, resolved from `MODEL_PATH` /
`MODEL_VERSION`; default `ml/experiments/cardd_baseline_ce/best_checkpoint.pt`).

## 3. Backend layering (`apps/api`)

```
Router / API layer      apps/api/routers — validation, status codes, serialisation
        ↓
Application services    apps/api/{agent,vision,repair,cost,inspection} — use cases,
                        rules, orchestration (LangGraph workflow, quality validator,
                        repair rule, cost estimator, consent service)
        ↓
Infrastructure          apps/api/storage — SQLite ledger + fs image store,
                        session/state/consent/training-sample stores, cleanup;
                        apps/api/container.py wires everything once at startup
```

- `agent/graph.py` — LangGraph state graph: START → collect incident / damage
  location / repair location / insurance → PHOTO → (quality loop) → damage
  analysis → repair + cost → comparison → consent → finish. `agent/groq_service.py`
  is the conversational/explanation service; the Groq key is server-side only
  (`.env`, `GROQ_AUTO_INSPECT_API_KEY`).
- `vision/quality.py` — heuristic capture-quality gates
  (blur/dark/glare/contrast → TOO_BLURRY / TOO_DARK / EXCESSIVE_GLARE /
  INSUFFICIENT_CONTEXT), never inspects model output.
- `inspection/` — typed `InspectionContext` + provenance; user-vs-model
  comparison (AGREEMENT / PARTIAL_AGREEMENT / DISAGREEMENT / NOT_APPLICABLE).
- `repair/`, `cost/` — `DemoRepairEstimator` (labelled demonstration rule) and
  `UnavailableCostEstimator` (honest `DATA_UNAVAILABLE`; synthetic demo quote
  only behind `ALLOW_SYNTHETIC_ESTIMATE` and always labelled
  "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE").
- `storage/` — `FsSqliteImageStore` with EXIF stripping, image assets
  ledgered in SQLite; sessions close via soft-close (GET after finish → 410)
  while the audit row is retained.

## 4. ML boundary

Training and inference are separate code paths (ADR 0008: CE over argmax). The
API depends on a versioned model artefact resolved from configuration and load
notes (val mIoU, git revision) read from `ml/experiments/registry.json`; it
never imports `ml/training`. The committed demo checkpoint
(`cardd_baseline_ce`, val mIoU ≈ 0.048) is explicitly **demonstration-grade
and underfit**: the product surfaces confidence, a low-confidence banner, and
the "not verified damage extent" caveat rather than overclaiming.

## 5. Frontend structure (`apps/web`)

Next.js 16 (App Router), React 19, TypeScript strict, Tailwind CSS. Two routes:

- `/` — cinematic landing: scroll-driven sequence over the four clips
  (`public/1.mp4`…`4.mp4`; total ≈ 30.4 s, declared in `lib/video.ts`), "Skip to
  demo" hand-off. Phase O narrative copy remains neutral and marked
  `PENDING_USER_CONFIRMATION` until a vision-capable reviewer confirms it.
- `/demo` — the inspection journey: chat → context summary → photo guidance →
  upload (camera on mobile) → capture-quality validation UX with retake
  guidance → analysis stages → labelled result blocks → consent → completion.

Result honesty contract (UI + API): four labelled blocks — WHAT YOU TOLD US
(provenance: user), WHAT THE MODEL FOUND (provenance: model prediction; image
denominator only, never cm², ADR 0005), WHAT WE ESTIMATE (shows
"You have no real quote" unless a labelled synthetic estimate is enabled), WHAT
WE RECOMMEND (provenance: demo rule). The overlay image is the predicted mask
only; the low-confidence banner explains the demo model limits.

## 6. Runtime data flow

```
Browser (apps/web)
  │  session → chat turns (context) → photo upload
  ▼
API routers
  │  session store, image store (validate + EXIF strip + ledger)
  ▼
LangGraph workflow (orchestration only)
  │  damage_analysis: quality gate → SegmentationEngine (ml/inference) →
  │    features/confidence/area ratio/overlay → compare user vs model
  ▼
Application services
  │  repair rule + cost estimator (honest states) → explanation
  ▼
Browser
  │  result blocks + overlay + consent (optional) → finish (session soft-close)
```

## 7. Storage

- Session metadata + state in SQLite (`Storage/app.db`); uploaded images on the
  filesystem under `storage/<session_id>/`, deleted with the session.
- Consented training samples (image + labels + provenance + consent + dataset
  version) land in `data/training/user-consented-v1/` and are never touched by
  session cleanup. Consent is always optional and clearly labelled.
- No Supabase project exists (the connected account belongs to another product —
  never written to). Supabase/S3/Postgres can replace these behind the same
  interfaces with a new ADR.

## 8. Quality gates

Every phase ends with the full suite green:

Backend (`ai` conda env, or CI `.venv` via `uv sync` + `requirements-ci.txt`):

```
uv run ruff check apps/ ml/ tests/ conftest.py
uv run ruff format --check apps/ ml/ tests/ conftest.py
uv run python -m mypy apps/ ml/ tests/     # strict
uv run python -m pytest tests/             # 123 tests
```

Frontend (in `apps/web`):

```
npm run lint -- --max-warnings=0
npm run typecheck
npm run build
npx playwright test                        # desktop/tablet/mobile
```

CI (`.github/workflows/ci.yml`) runs backend, frontend, and Playwright jobs on
CPU runners. GPU training never runs in CI (ADR/tooling rule); the commits
demo checkpoint is git-ignored, so the real-engine browser journeys and the
`test_full_journey_happy_path_with_real_engine` pytest skip cleanly when absent
— exactly the same check in both suites.

## 9. Honesty rules (relevant even at architecture level)

- Rule-generated cost table ≠ real repair-cost ground truth (ADR 0004).
- Synthetic hidden-damage labels are labels, never validated evidence.
- No true physical damage area in cm² from an uncontrolled photograph
  (ADR 0005); a normalized image-denominator ratio is used and described as such.
- The model is the only vision evidence source; no LLM "becomes" the vision model.
- Research vs product stays two-track: research is segmentation → features →
  downstream; product is cinematic UI → conversation → photo → inference →
  results → consent. Neither distorts the other's methodology.