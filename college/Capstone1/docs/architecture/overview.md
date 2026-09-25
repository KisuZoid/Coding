# Architecture Overview

Status: implemented photo-first system with the five-model runtime catalogue
defined by ADR 0012. The current controlled objective is Dice + Focal under ADR
0013; the CE path is historical. The architecture boundary follows ADR 0003:
training code is never imported by the API.

## 1. System shape

```text
apps/web/       Next.js App Router frontend and photo-first demo
apps/api/       FastAPI routers, application services, state, storage, catalogue
ml/inference/   Production segmentation engine and evidence payload
ml/training/    Research-only dataset, training, loss, and checkpoint code
ml/evaluation/  Full-split metrics and qualitative evaluation
ml/experiments/ Git-ignored checkpoints, run records, and registry
archive/        Superseded docs, code, and experiment provenance
```

The frontend communicates only through typed HTTP contracts. The API depends
on `ml/inference`, not `ml/training`.

## 2. Runtime flow

```text
GET /models
  → select one explicit catalogue model
POST /inspection/session (optional model_id)
  → persist model_id in session state
POST /inspection/{id}/upload
  → validate and EXIF-strip the photo
POST /inspection/{id}/analyze
  → capture-quality gate
  → selected SegmentationEngine
  → predicted mask, classes, normalized ratios, confidence, overlay, metadata
  → assistant explanation grounded in stored evidence
POST /inspection/{id}/consent (optional)
POST /chat
  → grounded follow-up turn
```

A quality failure returns `200` with `QUALITY_FAILED`, retake guidance, and no
mask. Model selection is locked once inspection evidence exists.

## 3. Model catalogue and engine

`apps/api/model_catalog.py` is the explicit five-entry allowlist:

- `final60_baseline_seed42` — CONTROLLED ResNet34UNet.
- `final60_baseline_seed1337` — CONTROLLED ResNet34UNet.
- `final60_hybrid_seed42` — CONTROLLED HybridSegmentation; default.
- `final60_hybrid_seed1337` — CONTROLLED HybridSegmentation.
- `final100_hybrid_seed42` — EXPLORATORY HybridSegmentation with a partial
  reconstructed run record.

`apps/api/container.py` resolves the catalogue ID, caches one engine per
model, and reports model metadata. `ml/inference/engine.py` reads
`model_arch` from the checkpoint and dispatches to the matching model class;
it does not guess an architecture from a filename. `MODEL_PATH` remains a
legacy/custom path escape hatch and is not the normal catalogue selection.

The four controlled entries use two available seeds (`42`, `1337`) and a
60-epoch target schedule. The final-100 entry is a continuation with incomplete
history and is not a matched comparison.

## 4. Backend layers

```text
Router / API layer       apps/api/routers
Application services     apps/api/agent, vision, inspection
Infrastructure           apps/api/storage, container, settings
```

- `routers/models.py` exposes the catalogue.
- `routers/inspection.py` owns session/upload/analyze/consent routes and model
  selection locking.
- `agent/assistant.py` defines the assistant protocol and the Groq/offline
  implementations.
- `agent/graph.py` runs a minimal grounded chat turn.
- `vision/quality.py` performs the capture-quality gate.
- `storage/` manages SQLite session state, images, consent, and training
  samples.
- `container.py` wires model, assistant, storage, and services once at startup.

Errors use typed codes, including `MODEL_NOT_FOUND`,
`MODEL_SELECTION_LOCKED`, `MODEL_UNAVAILABLE`, `INFERENCE_FAILED`, and
`LLM_UNAVAILABLE`. Tracebacks and secrets never appear in API responses.

## 5. ML boundary

Training and inference are separate. Training records the dataset, split,
architecture, seed, hyperparameters, metrics, assumptions, and Git revision in
`run_record.json` and the registry. The API consumes only a versioned checkpoint
and the explicit catalogue.

Active experiment directories retain only `best_checkpoint.pt` and
`run_record.json`. Pilot and legacy artifacts remain under
`archive/experiments/` for provenance. The repository never commits weights.

The final-100 record is intentionally marked
`PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`; missing epochs and termination reason
are not reconstructed by inference.

## 6. Frontend

Next.js 16 / React 19 / TypeScript strict provides:

- `/` — scroll-driven cinematic introduction.
- `/demo` — photo composer, quality feedback, predicted overlay, class/area/
  confidence display, model provenance, optional consent, and grounded chat.

The UI labels the overlay as a MODEL PREDICTION. It never presents normalized
ratios as cm², predicted damage as verified extent, or the assistant as a
replacement for the vision model. Repair cost/action and quotation blocks do
not exist.

## 7. Evidence contract

| Output | Category | Contract |
|---|---|---|
| CarDD training/evaluation masks | REAL GROUND TRUTH | Dataset annotations only |
| Predicted segmentation mask | MODEL PREDICTION | Argmax output; not verified extent |
| Mean confidence and low-confidence flag | MODEL PREDICTION | Preliminary signal |
| Image-relative area ratios | DERIVED FEATURE | Pixels divided by image pixels |
| Assistant narrative | MODEL PREDICTION / ASSUMPTION | Grounded in stored evidence |
| Consent sample | MODEL_SUGGESTED provenance | Optional; not validated ground truth |

No synthetic cost labels, hidden-damage probabilities, physical areas, or
repair actions are emitted.

## 8. Quality gates

Backend:

```bash
ruff check apps/ ml/ tests/ conftest.py
ruff format --check apps/ ml/ tests/ conftest.py
python -m mypy apps/ ml/ tests/
python -m pytest tests/
```

Frontend:

```bash
cd apps/web
npm run lint -- --max-warnings=0
npm run typecheck
npm run build
npx playwright test
```

The current change passed focused model/API tests, Ruff, mypy, frontend static
checks, and the Next.js build. Full pytest, Playwright, and documentation builds
remain pending; the `public/4/` textual OCR audit is complete, while direct
visual interpretation was unavailable in the current tool environment.

## 9. Invariants

- Model IDs are allowlisted; arbitrary paths are not catalogue entries.
- Model selection is persisted and immutable after analysis.
- Architecture is checkpoint-declared and checked at load time.
- Training data and test data remain separated.
- The API never imports training code.
- No cost/repair/physical-area fields are introduced without a new ADR.
- Historical artifacts are archived with provenance rather than silently
  deleted.
