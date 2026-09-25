# TASKS.md — AutoInspect-X

Current tracker for the five-model runtime catalogue, evidence cleanup, and
final validation. Historical task history remains in Git and the archived
project documents.

> **Integrity rule:** the four 60-epoch-target entries are a controlled
> two-seed comparison, not a completed three-seed study. The
> `final100_hybrid_seed42` record is exploratory and partially reconstructed.
> Do not claim architecture superiority, statistical significance, or completed
> final-100 training.

## Current state

- Product: photo-first FastAPI + Next.js demo implemented under ADR 0011.
- Runtime catalogue: five explicit model IDs exposed by `GET /models`.
- Default: `final60_hybrid_seed42`.
- Session model selection: persisted before analysis and locked afterward.
- Active artifacts: best checkpoint plus run record per catalogue entry.
- Pilot/legacy experiments: archived with provenance; periodic pilot snapshots
  removed from live storage.
- Cinematic scene 4: OCR-audited all 240 source frames; 001–084 remain live and
  085–240 are archived because they contain obsolete repair/cost copy.
- Documentation and deliverable refresh: **in progress**.
- Full backend/browser/document validation: **in progress**.

## Completed in this cleanup

- Added `apps/api/model_catalog.py` and `GET /models`.
- Added API schemas, model errors, session model selection, and per-model
  engine caching.
- Added `model_id` to inspection responses and engine metadata.
- Added the frontend model selector and model provenance display.
- Created a transparent partial record for `final100_hybrid_seed42` from the
  available best/periodic checkpoint metadata.
- Updated the ignored experiment registry with four controlled and one
  exploratory catalogue entries.
- Moved `pilot15_baseline` and `pilot15_hybrid` to `archive/experiments/`.
- Removed live periodic checkpoints from active experiment and pilot storage
  directories.
- Updated code examples, focused tests, e2e checkpoint paths, `.env.example`,
  local model settings, and the catalogue documentation.
- Added ADR 0012 for the five-model runtime catalogue and partial final-100
  record.
- Added ADR 0013 for the current Dice + Focal objective and marked CE as
  historical for the current catalogue.
- OCR-audited all 240 `public/4` frames, retained frames 001–084 in the live
  scene, archived 085–240 under `archive/cinematic/legacy-public-4/`, and
  updated the live frame count to 757 total frames.
- Focused model/API tests, Ruff, mypy, frontend lint, typecheck, and build
  passed. The focused test run reported 18 passing tests.

## Active

1. Replace remaining live pilot/default references in root docs, research
   alignment docs, archive register, and any overlooked scripts.
2. Reconcile the report, presentation, literature-review artifacts, and any
   generated PDFs with the current five-model catalogue.
3. Run the full backend pytest suite and Playwright suite.
4. Recheck ignored artifacts, local configuration, generated outputs, and
   `git status --short --branch` before handoff.

## Current model evidence

| ID | Architecture | Seed | Status | Best val foreground mIoU | Best epoch | Record state |
|---|---|---:|---|---:|---:|---|
| `final60_baseline_seed42` | ResNet34UNet | 42 | CONTROLLED | 0.6676585078 | 44 | recorded |
| `final60_baseline_seed1337` | ResNet34UNet | 1337 | CONTROLLED | 0.6681153178 | 50 | recorded |
| `final60_hybrid_seed42` | HybridSegmentation | 42 | CONTROLLED | 0.6701672077 | 49 | recorded; early stop 59 |
| `final60_hybrid_seed1337` | HybridSegmentation | 1337 | CONTROLLED | 0.6731674075 | 47 | recorded; early stop 57; resume metadata retained |
| `final100_hybrid_seed42` | HybridSegmentation | 42 | EXPLORATORY | 0.6715497971 | 58 | `PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`; `completed: false` |

The final-100 record observed periodic checkpoints from epochs 54 through 84
but lacks complete history, continuation metrics, and termination reason.

## Documentation deliverables

- `README.md` — current product, catalogue, evidence, and artifact policy.
- `RUNBOOK.md` — local operation, API selection, training, and validation.
- `MEMORY.md` — compact current facts and unresolved decisions.
- `AUTOINspectX_PROJECT_STATE.md` — consolidated state snapshot.
- `docs/architecture/overview.md` — current system architecture.
- `docs/research/implementation-alignment.md` and
  `docs/research/problem-definition.md` — research/code reconciliation.
- `AutoInspect-X_Research_Report_Corrected.md` — research source of truth;
  current catalogue correction must remain clearly dated and qualified.
- `AutoInspect-X_Capstone.pptx` and `Capstone report/` — regenerate or amend
  only from verified current evidence. Both were reconciled against the
  five-entry catalogue on 2026-09-25: the report is 82 A4 pages with a converged
  TOC, LOF and 15 verified code listings, and the deck is 17 slides with the
  pilot-era metrics, three-seed claim and stale repository tree removed.
- `docs/research/literature_review.tex/.pdf` — preserve verified literature;
  do not add model-performance claims without sources. Recompiled with Tectonic
  on 2026-09-25: 10 pages, 30 references, no unresolved citations.

## Known limitations

- Only two controlled seeds are present; a third seed is not present.
- RQ2 confidence-honesty operational definition and research summary are
  pending.
- The final-100 history cannot be reconstructed beyond the artifacts listed in
  its run record.
- OCR completed the textual audit of the cinematic frames; direct visual
  interpretation was unavailable in the current tool environment.
- Single-photo outputs do not establish hidden damage, physical scale, repair
  action, or cost.

## Validation status

Run on 2026-09-25 with the `ai` conda environment and Node 22:

- `ruff check` and `ruff format --check` clean; `mypy` strict clean over
  `apps/ ml/ tests/`.
- Full `pytest tests/`: 147 passed.
- Frontend `lint --max-warnings=0`, `typecheck`, `build`: pass.
- Full Playwright run: 34 passed, 8 skipped (intentional desktop-only engine
  journeys on tablet and mobile).
- Literature review compiles to 10 pages with no unresolved citations.
- Report and deck regenerate with converged pagination and no stale
  pilot-era claim.

Two environment-driven defects were fixed rather than papered over: the
git-ignored `.env` leaked `MODEL_ID` into tests of the legacy checkpoint route,
and the responsive status chip was asserted as visible on viewports where it is
deliberately hidden.

## Next recommended task

Hand the working tree to the user for review, then decide whether the
report/deck generator should be committed so the deliverables are reproducible
from the repository alone. Do not commit unless explicitly requested.
