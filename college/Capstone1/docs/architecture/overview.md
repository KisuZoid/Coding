# Architecture Overview

> Status: **implemented.** Phases A–R of the product build completed in
> 2026-09-08; the photo-first scope change (ADR 0011) and `CarddHybrid` model
> (ADR 0010) superseded the Phase R product contract on 2026-09-21. This
> document describes the running system as of that date.

## 1. Shape

AutoInspect-X is a **modular monorepo**, not a set of microservices. A capstone
project with one team and one deployment target gains nothing from network
boundaries between components, and loses reproducibility. See
`docs/decisions/0001-modular-monorepo.md`.

```
AutoInspect-X/
├── apps/
│   ├── web/            Next.js (App Router) frontend — cinematic intro + chat demo
│   └── api/            FastAPI backend — routers, agent (assistant), inspection, vision, storage
├── ml/
│   ├── datasets/       Dataset adapters and audit (CarDD COCO)
│   ├── training/       Training workflows (never imported by the API — ADR 0003)
│   ├── inference/      Production inference path used by the API (ADR 0003)
│   ├── evaluation/     Metrics / benchmark evaluation (research side)
│   ├── analysis/       Error analysis / visualisation helpers (research side)
│   └── experiments/    Registry + per-run records (checkpoints git-ignored)
├── docs/
│   ├── decisions/      ADRs 0001–0011
│   └── architecture/   This overview (+ archived gap report under archive/)
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
`/inspection/{id}/consent`, `/inspection/{id}`, DELETE). The backend loads a
model artefact only through `ml/inference` (`SegmentationEngine`, resolved from
`MODEL_PATH` / `MODEL_VERSION`, dispatching on the checkpoint's `model_arch`;
demo default `ml/experiments/pilot15_hybrid/best_checkpoint.pt`).

## 3. Backend layering (`apps/api`)

```
Router / API layer      apps/api/routers — validation, status codes, serialisation
        ↓
Application services    apps/api/{agent,vision,inspection} — use cases,
                        orchestration (assistant service, quality validator,
                        consent service)
        ↓
Infrastructure          apps/api/storage — SQLite ledger + fs image store,
                        session/state/consent/training-sample stores, cleanup;
                        apps/api/container.py wires everything once at startup
```

- `agent/assistant.py` — `AssistantService` protocol with
  `damages_explanation` / `retake_guidance` / `chat_reply`. Production impl
  `LangChainGroqAssistant` wraps LangChain `ChatGroq` (model
  `llama-3.3-70b-versatile`, `settings.groq_model`); offline/CI uses the
  deterministic `StubAssistant`. `build_assistant` picks one from
  `GROQ_AUTO_INSPECT_API_KEY` (server-side only). No more `groq_service.py`
  rule-based service (ADR 0011).
- `agent/graph.py` — minimal LangGraph: `START → llm_turn → END`; each
  `POST /chat` appends the user message and asks the assistant for a reply
  grounded in the stored prompt-safe evidence. The graph never waits on
  questionnaire fields.
- `vision/quality.py` — heuristic capture-quality gates
  (blur/dark/glare/contrast → TOO_BLURRY / TOO_DARK / EXCESSIVE_GLARE /
  WRONG_ANGLE / DAMAGE_NOT_VISIBLE / INSUFFICIENT_CONTEXT), never inspects
  model output.
- `inspection/` — typed `InspectionContext` + provenance (USER / MODEL /
  DERIVED / INFERRED / SYSTEM) and the consent service. No repair/cost
  comparison fields exist (removed by ADR 0011).
- `storage/` — `FsSqliteImageStore` with EXIF stripping, image assets
  ledgered in SQLite; sessions close via soft-close (GET after close → 410)
  while the audit row is retained.

## 4. ML boundary

Training and inference are separate code paths (ADR 0008: CE over argmax). The
API depends on a versioned model artefact resolved from configuration and load
notes (foreground mIoU, git revision) read from `ml/experiments/registry.json`;
it never imports `ml/training`. Checkpoints are arch-tagged (`model_arch` key)
and the engine dispatches `resnet34_unet`/`baseline` → `ResNet34UNet`,
`hybrid`/`hybrid_segmentation` → `HybridSegmentation` (research models, spec v3
§4/§9.1), while legacy `cardd_*` checkpoints keep loading (ADR 0010); a
base/arch mismatch surfaces as a loud `ModelVersionError`. The
demo default is `ml/experiments/pilot15_hybrid/best_checkpoint.pt`
— a 15-epoch, seed-0 pilot (foreground mIoU 0.5963 at epoch 14, still
improving). That pilot is **preliminary, not a final research conclusion**;
the baseline pilot (`pilot15_baseline`, foreground mIoU 0.6127) is kept for the
planned 60-epoch / 3-seed comparison. Until the checkpoint exists the
real-engine tests skip (not fail). The product always surfaces confidence, a
low-confidence banner, and the "not verified damage extent" caveat rather than
overclaiming; any quality claim about a run is contingent on its training and
verified inference.

## 5. Frontend structure (`apps/web`)

Next.js 16 (App Router), React 19, TypeScript strict, Tailwind CSS. Two routes:

- `/` — cinematic landing: scroll-driven sequence over the four clips
  (`public/1.mp4`…`4.mp4`; total ≈ 30.4 s, declared in `lib/video.ts`), "Skip to
  demo" hand-off. Phase O narrative copy remains neutral and marked
  `PENDING_USER_CONFIRMATION` until a vision-capable reviewer confirms it.
- `/demo` — the photo-first chat (ADR 0011): the composer accepts a photo
  attachment (preview, remove, send); analysis runs the capture-quality gate
  and renders the predicted-mask overlay, class chips, area ratio, and
  confidence inline in the assistant bubble — with retake guidance on quality
  failure and inline consent beneath the chat.

Result honesty contract (UI + API): the overlay is the model's predicted mask
only (MODEL PREDICTION); class labels carry confidence, and an explicit
low-confidence flag/banner marks preliminary results — never verified damage
extent. Area ratios are image-denominator, never cm² (ADR 0005). No cost,
repair-action, or quote block exists anywhere in the UI (ADR 0011), and the
assistant (LangChain or stub) may only restate facts present in the structured
evidence.

## 6. Runtime data flow

```
Browser (apps/web)
  │  POST /inspection/session → send photo in the composer → analyze
  ▼
API routers
  │  session store, image store (validate + EXIF strip + ledger)
  ▼
/analyze (apps/api/routers/inspection.py)
  │  quality gate → reject: 200 QUALITY_FAILED + assistant retake guidance
  │  accept: SegmentationEngine (ml/inference; dispatch by model_arch) →
  │    features / confidence / area ratio / overlay → assistant explanation
  ▼
Browser
  │  overlay + class chips + honesty annotations inline; optional consent
  ▼
POST /chat → LangGraph turn → assistant reply grounded in stored evidence
  ▼
Browser
  │  follow-up conversation; session soft-closes on expiry/delete (410 on reuse)
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

- Cost/repair prediction is out of scope (ADR 0011); no synthetic cost labels
  exist anywhere. The general ground-truth policy (ADR 0004) still governs any
  label family that exists.
- Synthetic hidden-damage labels are labels, never validated evidence.
- No true physical damage area in cm² from an uncontrolled photograph
  (ADR 0005); a normalized image-denominator ratio is used and described as such.
- The model is the only vision evidence source; no LLM "becomes" the vision model.
- Research vs product stays two-track: research is segmentation → features →
  confidence-honesty comparison (RQ1/RQ2); product is cinematic UI → photo-first
  chat → inference → results → consent. Neither distorts the other's
  methodology.