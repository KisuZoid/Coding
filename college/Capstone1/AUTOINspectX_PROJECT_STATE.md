# AutoInspect-X Project State

Current consolidated state of the photo-first vehicle damage segmentation
capstone. This file is documentation-only; implementation and experiment
records remain the sources of truth for code and measured results.

> **Evidence labels:** REAL GROUND TRUTH, WEAK LABEL, SYNTHETIC LABEL,
> DERIVED FEATURE, MODEL PREDICTION, and ASSUMPTION retain the meanings in
> `AGENTS.md`. No cost, repair-action, hidden-damage, or physical cm² claim is
> part of the current product.

## 1. Current definition

AutoInspect-X accepts one vehicle photograph, applies a capture-quality gate,
runs a selected segmentation model, and returns an evidence-labelled predicted
mask with normalized image-relative features, confidence, and an honest
explanation. Optional consent and follow-up chat use the stored evidence.

The conversational assistant is separate from the vision model. LangChain
ChatGroq is used when configured; otherwise a deterministic `StubAssistant` is
used. The assistant cannot turn a predicted mask into verified damage or add
repair/cost claims.

## 2. Current runtime catalogue

ADR 0012 defines an explicit five-entry runtime allowlist. ADR 0013 records the
current controlled objective, 0.50 foreground Dice plus 0.50 multiclass Focal.
The API resolves model IDs through `apps/api/model_catalog.py`; the frontend
displays available entries and persists the selected ID in session state.

| ID | Architecture | Seed | Status | Best val foreground mIoU | Best epoch | Provenance |
|---|---|---:|---|---:|---:|---|
| `final60_baseline_seed42` | `ResNet34UNet` | 42 | CONTROLLED | 0.6676585078 | 44 | `final60_baseline_seed42-20260923-231704` |
| `final60_baseline_seed1337` | `ResNet34UNet` | 1337 | CONTROLLED | 0.6681153178 | 50 | `final60_baseline_seed1337-20260925-095441` |
| `final60_hybrid_seed42` | `HybridSegmentation` | 42 | CONTROLLED | 0.6701672077 | 49 | `final60_hybrid_seed42-20260924-005716`; early stop 59 |
| `final60_hybrid_seed1337` | `HybridSegmentation` | 1337 | CONTROLLED | 0.6731674075 | 47 | `final60_hybrid_seed1337-20260925-110553`; early stop 57; resume metadata retained |
| `final100_hybrid_seed42` | `HybridSegmentation` | 42 | EXPLORATORY | 0.6715497971 | 58 | `final100_hybrid_seed42`; partial reconstructed record |

`final60_hybrid_seed42` is the product default. The four controlled entries
use the 60-epoch target configuration and two available seeds. The records may
end early through the configured patience rule; this is not a claim that every
run consumed all 60 epochs.

`final100_hybrid_seed42` is an exploratory continuation resumed from the
seed-42 hybrid checkpoint. Its run record has `completed: false`,
`record_status: PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`, observed periodic
snapshots at epochs 54, 59, 64, 69, 74, 79, and 84, and a best checkpoint at
epoch 58. Complete continuation metrics and the termination reason are
missing. The available validation foreground mIoU is
`0.6715497970581055`; no completed 100-epoch or superiority claim follows.

Exact configuration, split, seed, class weights, metrics, and provenance are in
the ignored `ml/experiments/<id>/run_record.json` files and
`ml/experiments/registry.json`.

## 3. Measured model results

The table above reports best validation foreground mIoU from run records, with
background excluded from the foreground mean. It is not a test-set table and
does not establish statistical significance.

The final-100 best checkpoint additionally records foreground mDice
`0.7861893773078918` and pixel accuracy `0.9250539049690152`. These values are
checkpoint metadata, not evidence of a completed experimental schedule.

Pilot and legacy values remain in the registry and archive. They are historical
observations and must not be mixed into the current controlled table.

## 4. Data and evidence

- Dataset: CarDD-COCO official splits, locally measured as train `2,816`,
  validation `810`, and test `374` images.
- CarDD masks are REAL GROUND TRUTH for segmentation training/evaluation.
- Uploaded photographs are user inputs, not calibrated physical measurements.
- Masks, class outputs, confidence, and overlay are MODEL PREDICTION.
- `damaged_pixels / total_image_pixels` is a DERIVED FEATURE; physical area in
  cm² is not supported by an uncontrolled photograph.
- Consent samples retain model-suggested provenance and are not validated
  hidden-damage or ground-truth evidence.
- No synthetic cost table or repair-action label is used.

## 5. API and frontend state

Implemented endpoints include:

- `GET /health`
- `GET /models`
- `POST /inspection/session` with optional `model_id`
- `PATCH /inspection/{session_id}/model` before analysis
- photo upload, analyze, optional consent, state retrieval, and delete
- grounded follow-up chat

Analysis returns the selected model ID and model metadata. Quality rejection
returns `200` with `status="QUALITY_FAILED"` and no mask. Selection is locked
once inspection evidence exists. Unknown IDs and locked changes have distinct
error codes.

The Next.js demo has a model selector, analysis provenance, predicted overlay,
class/area/confidence display, honesty messaging, and optional consent. The
live cinematic scene uses 84 OCR-audited frames; 156 obsolete frames containing
repair/cost copy are archived and not served. Direct visual interpretation of
the images was unavailable in the current tool environment.

## 6. Architecture and boundaries

- `apps/api/model_catalog.py` — explicit catalogue and public metadata.
- `apps/api/container.py` — per-model engine cache and session resolution.
- `ml/inference/engine.py` — architecture dispatch from checkpoint metadata.
- `ml/models/resnet34_unet.py` — controlled baseline.
- `ml/models/hybrid_segmentation.py` — controlled proposed architecture.
- `ml/training/train.py` — research-only training; never imported by the API.
- `apps/web/` — frontend contracts and demo.

Legacy `CarddUNet`/`CarddHybrid` model files remain load-bearing for legacy
checkpoint dispatch and archive provenance. They are not current catalogue
defaults. Training and inference remain separated under ADR 0003.

## 7. Artifact state

Active experiment directories contain only:

```text
ml/experiments/<model_id>/best_checkpoint.pt
ml/experiments/<model_id>/run_record.json
```

`ml/experiments/registry.json` is the local index. Pilot experiment directories
and legacy experiment directories are under `archive/experiments/`. Pilot
periodic snapshots were removed from live storage. These paths are git-ignored;
weights, datasets, `.env`, and storage content must never be committed.

ADR 0011 remains the scope boundary. Reintroducing cost-like fields or physical
area claims requires a new ADR and evidence review.

## 8. Research status

- Segmentation core, engine, API, UI, and honesty contract: implemented.
- Controlled comparison: two seeds and two architectures are available for
  current model-specific measurements.
- RQ1 comparative interpretation: not locked; no superiority claim is made.
- RQ2 confidence-honesty operational definition: pending.
- Research summary: pending.
- External validation and three-seed completion: not present in the current
  evidence set.
- Final-100 continuation: partial record only.

## 9. Verification state

Current cleanup verification:

- Focused model/API tests: 18 passed.
- Ruff: passed for the changed Python scope.
- Mypy: passed for `apps/api` and `ml/inference`.
- Frontend ESLint, TypeScript typecheck, and Next.js build: passed.
- Full pytest, Playwright, documentation compilation, and deliverable
  reconciliation: pending. The `public/4/` textual OCR audit is complete;
  direct visual interpretation was unavailable in the current tool environment.

## 10. Open decisions and next task

1. Reconcile the report, presentation, literature-review outputs, and current
   documentation with the five-model table.
2. Run the complete validation matrix and inspect the final Git/artifact state.
3. Decide whether to collect a third controlled seed and lock the RQ2 metric
   before writing a comparative research conclusion.
4. Do not attempt to fill final-100 history unless an original log or a new
   reproducible run is available.

See `TASKS.md`, `MEMORY.md`, `RUNBOOK.md`, ADR 0011, ADR 0012, ADR 0013, and the
research report for the current operational contract.
