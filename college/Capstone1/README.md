# AutoInspect-X

**Photo-first vehicle exterior damage segmentation** — turn one photograph
into a pixel-level predicted mask, normalized image-relative damage features,
confidence flags, and an honest conversational explanation.

Repair-cost and repair-action prediction are out of scope (ADR 0011). The
overlay is always a **MODEL PREDICTION**; it is not verified physical damage
extent. No cost, quote, repair-action, hidden-damage, or cm² field is part of
the product or research claim.

> **Status:** implemented photo-first prototype with an explicit five-model
> runtime catalogue. Four controlled 60-epoch-target runs and one explicitly
> exploratory continuation are available locally. See `TASKS.md` for the
> current validation and documentation work.

## Research question

On CarDD, how does a CNN–Transformer hybrid compare with a ResNet34 U-Net
baseline for damage-segmentation quality and confidence honesty under a shared
training and evaluation contract?

The current catalogue provides two controlled seeds (`42` and `1337`) for each
architecture. It is a controlled two-seed comparison, not a completed
three-seed experiment. The exploratory `final100_hybrid_seed42` continuation
is not a matched comparison.

## Runtime model catalogue

The API and frontend use an explicit allowlist. The default is
`final60_hybrid_seed42` because it is a controlled, measured hybrid checkpoint;
the incomplete final-100 continuation is never the default.

| Model ID | Architecture | Seed | Status | Best validation foreground mIoU | Best epoch | Record |
|---|---|---:|---|---:|---:|---|
| `final60_baseline_seed42` | `ResNet34UNet` | 42 | CONTROLLED | 0.6676585078 | 44 | recorded |
| `final60_baseline_seed1337` | `ResNet34UNet` | 1337 | CONTROLLED | 0.6681153178 | 50 | recorded |
| `final60_hybrid_seed42` | `HybridSegmentation` | 42 | CONTROLLED | 0.6701672077 | 49 | recorded; stopped at 59 |
| `final60_hybrid_seed1337` | `HybridSegmentation` | 1337 | CONTROLLED | 0.6731674075 | 47 | recorded; stopped at 57 |
| `final100_hybrid_seed42` | `HybridSegmentation` | 42 | EXPLORATORY | 0.6715497971 | 58 | `PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS` |

The final-100 record contains a best checkpoint and periodic evidence observed
at epochs 54–84, but not the complete continuation history or termination
reason. It must not be described as a completed 100-epoch run. Exact metrics,
configuration, and provenance live in each ignored
`ml/experiments/<model_id>/run_record.json` and in `ml/experiments/registry.json`.

## Product flow

1. The browser creates a session and chooses an available catalogue model.
2. The user attaches one photo; the upload is validated and EXIF-stripped.
3. The capture-quality gate rejects poor images with `QUALITY_FAILED` and
   retake guidance.
4. The selected engine dispatches from checkpoint `model_arch` metadata and
   returns a 7-channel argmax mask (background plus six CarDD damage classes).
5. The API returns/stores predicted classes, image-denominator area ratios,
   mean confidence, `low_confidence`, quality, model metadata, and an overlay.
6. The assistant explains only the persisted evidence; follow-up chat remains
   grounded in that evidence. Consent is optional and never turns a predicted
   mask into validated ground truth.

## HTTP model selection

```text
GET  /models
POST /inspection/session
     {"model_id": "final60_hybrid_seed42"}
PATCH /inspection/{session_id}/model
     {"model_id": "final60_baseline_seed1337"}
POST /inspection/{session_id}/upload
POST /inspection/{session_id}/analyze
```

The selected ID is persisted in session state and returned with analysis. Model
selection is locked after inspection evidence exists. Unknown IDs return
`MODEL_NOT_FOUND`; changes after analysis return `MODEL_SELECTION_LOCKED`.

`MODEL_ID` is the normal configuration. `MODEL_PATH` and `MODEL_VERSION` remain
supported only for deliberate legacy/custom-checkpoint compatibility.

## Architecture

- Baseline: `ml/models/resnet34_unet.py`.
- Proposed research model: `ml/models/hybrid_segmentation.py` (CNN encoder,
  bottleneck attention, decoder with skips).
- Legacy `CarddUNet`/`CarddHybrid` files remain for archive provenance and
  legacy dispatch; they are not current catalogue defaults.
- Inference: `ml/inference/engine.py`; architecture-tagged checkpoints dispatch
  without filename guessing.
- Training and inference remain separate (ADR 0003); the API does not import
  training code.
- Model resolution: `apps/api/model_catalog.py` and `apps/api/container.py`.

## Dataset and evidence labels

CarDD-COCO is the training/evaluation dataset. The locally measured official
split counts are train `2,816`, validation `810`, and test `374` images. CarDD
annotations are treated as REAL GROUND TRUTH for segmentation evaluation.
Areas exposed by the product are DERIVED FEATURES
(`damaged_pixels / total_image_pixels`); an uncontrolled photograph does not
support physical area in cm².

Run records and registry entries retain dataset, split, seed, architecture,
configuration, metrics, and provenance. No training/test mixing or duplicate
claim is introduced by the runtime catalogue.

## Repository map

```text
apps/api/          FastAPI routes, catalogue, container, state, assistant
apps/web/          Next.js photo-first demo and model selector
ml/models/         ResNet34UNet, HybridSegmentation, legacy Cardd models
ml/training/       Reproducible training entrypoint and shared pipeline
ml/inference/      Architecture-aware production inference
ml/experiments/    Git-ignored checkpoints, run records, registry
archive/           Superseded docs, code, and experiment provenance
docs/decisions/    ADRs 0001–0013
docs/research/     Literature review and research alignment documents
tests/             API, engine, model-catalogue, and integration tests
public/            Cinematic frame sequences; scene 4 OCR-audited to 84 live frames
```

## Running locally

Use the `ai` conda environment for Python/ML commands:

```bash
conda activate ai
cp .env.example .env
uvicorn apps.api.main:app --reload --port 8000
```

In a second terminal:

```bash
cd apps/web
npm install
npm run dev
```

Set `MODEL_ID=final60_hybrid_seed42` in `.env` (or choose another available
catalogue model in the UI). Leave the Groq key empty to use the deterministic
offline assistant. Never commit `.env`.

## Quality gates

```bash
conda run -n ai python -m pytest tests/
conda run -n ai ruff check apps/ ml/ tests/ conftest.py
conda run -n ai ruff format --check apps/ ml/ tests/ conftest.py
conda run -n ai python -m mypy apps/ ml/ tests/
cd apps/web && npm run lint -- --max-warnings=0 && npm run typecheck && npm run build
```

The current change has passed the focused model/API tests, Ruff, mypy, and all
three frontend static/build gates. The full pytest suite and browser suite are
still to be rerun after the documentation and deliverable reconciliation.

## Artifact policy

- Active experiment directories keep `best_checkpoint.pt` and
  `run_record.json` only.
- `ml/experiments/` and `archive/experiments/` are git-ignored local storage;
  their registry/run-record IDs are documented rather than weights being
  committed.
- Superseded pilot material is archived with provenance.
- Never commit `*.pt`, `*.pth`, `storage/`, datasets, or `.env`.
- Removing or restoring any cost-like output requires a new ADR.

## Limitations and next work

- The current controlled catalogue has two seeds, not a completed three-seed
  comparison.
- `final100_hybrid_seed42` has a reconstructed partial record; its missing
  history cannot be recovered from the current artifacts.
- RQ2 confidence-honesty operational definition and research summary remain
  pending.
- The live cinematic scene uses 84 OCR-audited frames; 156 legacy frames containing obsolete repair/cost copy are archived, not served. Direct visual interpretation of the images was unavailable in the current tool environment.
- Single-photo inference does not establish hidden damage, physical scale,
  repair action, or cost.

See `TASKS.md`, `MEMORY.md`, `RUNBOOK.md`, ADR 0012, and ADR 0013 for the current
plan and decision record.
