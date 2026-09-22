# AutoInspect-X

**Photo-first vehicle exterior damage segmentation** — turn a single photograph
into a pixel-level damage mask and an honest, conversational inspection, while
keeping every output strictly labelled (MODEL PREDICTION) and never over-claiming
what an uncontrolled photo can support.

> **Status: implemented prototype + research pilots.** FastAPI backend,
> PyTorch segmentation engine, LangChain-based chat assistant, and Next.js
> frontend run locally. Two 15-epoch research pilots
> (`pilot15_baseline`, `pilot15_hybrid`) are trained and wired into the stack.
> See `RUNBOOK.md` for run instructions.

---

## Problem

- An insurer, a used-car inspector, or a driver needs: **where is the damage,
  and how sure can an automated system honestly be?**
- Public, licence-clear, pixel-annotated data exists (CarDD, VehiDE), but no
  public dataset carries observed *repair costs* — so cost prediction is not
  reproducible ground truth and is **out of scope** (ADR 0011).
- Commercial damage tools are closed-source and do not publish calibration
  curves; a reproducible, *honesty-contract* baseline is the defensible opening.

## Research objective & scope

Answer (photo-first scope, ADR 0011):

- **RQ1 — segmentation quality:** does the CNN+Transformer hybrid
  (`HybridSegmentation`) achieve higher damage-segmentation quality (foreground
  mIoU, mDice, pixel accuracy, small-damage slice) than the plain U-Net baseline
  (`ResNet34UNet`) on CarDD under *identical splits, seed, and schedule*?
- **RQ2 — confidence honesty:** how well does the `low_confidence` /
  mean-confidence signal separate images where the predicted mask agrees with
  ground truth from images where it does not? *(Operational definition to be
  locked.)*
- **RQ3 — representation honesty:** describe evidence (per-class image-relative
  area ratios, mask overlays) without claiming physical area, hidden damage,
  repair action, or cost.

**Explicitly out of scope:** repair-cost / repair-action prediction (ADR 0011),
hidden-damage risk, physical area in cm², multi-view reconstruction.

## Product workflow

Single photo in → honest answer out:

1. **Capture / upload** one photo (type/quality gate).
2. **Segmentation** runs the engine (512×512 RGB → 7-class logits).
3. **Evidentiary payload** is produced: predicted mask, per-class
   image-relative area ratios (DERIVED FEATURE), mean confidence, `low_confidence`
   flag — every item labelled MODEL PREDICTION.
4. **Conversational assistant** (LangChain + ChatGroq, with offline stub) grounds
   a chat narrative in that payload; nothing is asserted beyond it.
5. **UI** (Next.js) shows the photo, overlay, ratios, flags, and chat; a damage
   estimate and honesty flags are always visible.

## ML architecture

- **Research models** (spec `docs/architecture/cnn-transformer-segmentation.md`,
  v3):
  - Baseline `ResNet34UNet` — `ml/models/resnet34_unet.py`.
  - Proposed `HybridSegmentation` — CNN encoder → transformer bottleneck
    (d_model = base×8, 4 heads, 2 layers, sinusoidal position encoding) → CNN
    decoder with skips — `ml/models/hybrid_segmentation.py`.
- **Legacy (KEEP, archival):** `ml/models/cardd_hybrid.py` (ADR 0010),
  `ml/models/cardd_unet.py` (ADR 0006) — still loadable by the engine/train
  legacy dispatch; see `archive/README.md`.
- **Harness:** `ml/training/train.py` (`--model baseline|hybrid|cardd_*`),
  shared loss `ml/training/loss.py`, metrics `ml/evaluation/metrics.py`.
- **Inference:** `ml/inference/engine.py` — `model_arch` dispatch for
  `resnet34_unet`/`baseline`, `hybrid`/`hybrid_segmentation`, and legacy
  `cardd_*`; produces mask + ratios + confidence + flags.

## Current model

- **Demo default:** `ml/experiments/pilot15_hybrid/best_checkpoint.pt`
  (experiment `pilot15_hybrid`, EXPERT ID `pilot15_hybrid-20260922-115320`,
  git `fb2fb59`).
- **Loading:** container reads `MODEL_PATH` / `MODEL_VERSION` (see `.env.example`),
  resolves the checkpoint from `ml/experiments/`, and pulls provenance
  (git revision, metric, notes) from `ml/experiments/registry.json`.
- **Input/output:** 512×512 RGB in → per-pixel logits over 7 classes; mask via
  argmax; confidence from softmax mean; `low_confidence` below thresholds.

## Baseline

- `pilot15_baseline` (`ResNet34UNet`), same splits/seed/schedule as the hybrid.
- Legacy records:
  - `cardd_baseline_ce` (CarddUNet, 5 epochs) — val mIoU 0.0475, SUPERSEDED
    (underfit).
  - `pilot15_baseline` — **foreground mIoU 0.6127** / mDice 0.7440 / pixel acc
    0.8979 @ epoch 14 (MEASURED).

## Dataset

- **CarDD** (Wang, Li, Wu, IEEE TITS 2023, DOI 10.1109/TITS.2023.3258480) —
  4,000 images / 9,000+ instance masks. Annotation = REAL GROUND TRUTH.
- Official splits preserved: train 2,816 / val 810 / test 374 (measured locally).
- Only damage masks exist in CarDD: **no** part masks, vehicle metadata, or cost
  annotations — a key reason cost prediction is out of scope.
- Protocol: image-denominator area ratio `damaged_pixels / total_pixels` per
  class (DERIVED FEATURE); physical cm² is never claimed.
- Other verified datasets (VehiDE, CrashCar101, CDA-Net, three-quarter-view) are
  reviewed in `docs/research/literature_review.tex` and cited in the research
  report, but are **not** used for training.

## Classes

1. Background (0)
2. Dent (1)
3. Scratch (2)
4. Crack (3)
5. Glass shatter (4)
6. Lamp broken (5)
7. Tire flat (6)

Metrics exclude background and are reported per class and as foreground means.

## Current pilot experiments

- **`pilot15_hybrid` — ACTIVE** (`HybridSegmentation`, 15 epochs, seed 0, full
  official splits): **foreground mIoU 0.5963**, mDice 0.7320, pixel acc 0.8873
  @ epoch 14; ~27.9M params.
- **`pilot15_baseline` — SUPERSEDED / retained arm** (`ResNet34UNet`, identical
  schedule): **foreground mIoU 0.6127**, mDice 0.7440, pixel acc 0.8979 @ epoch
  14; ~24.6M params.
- Both use EMA weights, warm-up + cosine decay, class-sampled batches, and the
  shared softmax-CE loss. **Both were still improving at epoch 14.**

> **Important — do not over-read.** The 15-epoch pilots are *preliminary
> validation observations* (intermediate check, single seed, no statistical
> test). They do **not** establish that either architecture is superior. The
> final comparison is the planned **60-epoch, 3-seed** run (see TASKS.md),
> which must complete before any architecture-level claim.

## Research status

- Segmentation core, engine, API, UI, and honesty contract: **implemented**.
- Research comparison RQ1/RQ2: **PARTIAL** — pilots trained and measured; final
  multi-seed comparison and the RQ2 operational definition are **PLANNED**.
- Literature review: **done** (`docs/research/literature_review.tex` →
  `literature_review.pdf`, 10 pp., IEEEtran, 30 verified references).
- Evidence integrity is governed by `AGENTS.md` (ground-truth categories:
  REAL GROUND TRUTH / WEAK LABEL / SYNTHETIC LABEL / DERIVED FEATURE /
  MODEL PREDICTION / ASSUMPTION).

## Repository structure (this project)

```
apps/
  api/                  FastAPI service: settings, container (checkpoint
                        resolution + registry metadata), routes, mocks/stubs,
                        request/response schemas
  web/                  Next.js frontend (photo upload, overlay, chat, honesty
                        flags); e2e Playwright+Codecept journeys
ml/
  models/               resnet34_unet.py, hybrid_segmentation.py (+ legacy
                        cardd_hybrid.py, cardd_unet.py)
  training/             train.py (baseline|hybrid|cardd_*), loss.py, data.py,
                        augmentation, checkpointing/EMA/registry writers
  inference/            engine.py (model_arch dispatch, prediction payload,
                        honesty flags, experiment resolution)
  evaluation/           evaluate_run.py, metrics.py, error_analysis.py
  analysis/             error analysis tooling
  experiments/          (git-ignored) pilot15_baseline/, pilot15_hybrid/,
                        registry.json
docs/
  decisions/            ADRs 0001–0011 (locked, append-only)
  architecture/         cnn-transformer-segmentation.md (spec v3), overview.md
  research/             literature_review.tex/.bib/.pdf, problem-definition.md,
                        implementation-alignment.md
  ml/                   ml-engineering-guidelines.md
tests/                  pytest suite (engine, smoke, e2e integration, legacy)
archive/
  docs/                 pinned historical documents (research-scope,
                        experiment-principles, segmentation-experiment-config,
                        cost-multimodal-data-readiness, implementation-gap,
                        CLAUDE_CODE bootstrap)
  experiments/          (git-ignored) historical experiment dirs + logs
                        (cardd_baseline_*, cardd_hybrid_ce, phase*, smoke_*)
  legacy-code/          archived sources (e.g. ml/training/train_smoke.py)
  README.md             provenance + move register
storage/models/         (git-ignored) relocated periodic checkpoints
AUTOinspectX_PROJECT_STATE.md   current-state brief (kept)
AutoInspect-X_Research_Report_Corrected.md  research report (source of truth
                        for research claims)
README.md RUNBOOK.md TASKS.md MEMORY.md LOGIC.md CLAUDE.md AGENTS.md init.md
IEEE-conference-template-062824/  vendor IEEE LaTeX template (reference)
```

## Running

Full instructions: **`RUNBOOK.md`** (backend `uvicorn`, frontend
`npm run dev`, model defaults, troubleshooting).

Quickstart:

```bash
# backend (ml-ai env)
cd apps/api && uvicorn main:app --reload

# frontend
cd apps/web && npm install && npm run dev
```

- Set `MODEL_PATH` and optional `MODEL_VERSION` in `.env` (see `.env.example`)
  to override the default checkpoint (`pilot15_hybrid`).
- Use `MODEL_VERSION=production` to load a pinned registry id explicitly.

## Tests

```bash
# backend: ruff + mypy + pytest (135 tests as of the last full run)
ruff check . && mypy .            # ml/, apps/api, tests
python -m pytest                  # engine, smoke, e2e integration

# frontend
cd apps/web && npm run lint -- --max-warnings=0 && npm run typecheck && npm run build

# compiled literature review (10 pp., IEEEtran)
cd docs/research && tectonic literature_review.tex
```

## Checkpoint storage policy

- Current model artifacts live under `ml/experiments/` (git-ignored; registry is
  the pointer). `git status` must never show `*.pt`.
- Large periodic checkpoints live under `storage/models/pilot15_*/` (git-ignored,
  external storage). `archive/experiments/` holds historical runs/logs.
- **Never commit `*.pt`, `*.pth`, `storage/`, or `ml/experiments/`.** See
  `.gitignore`. Git repo root is the parent folder — always scope commits to
  `college/Capstone1/...`.

## Archive policy

Superseded material goes to `archive/...` **with provenance** (see
`archive/README.md`), never deleted. Policy map: current research architecture
and models KEEP live; demo-era / superseded experiments ARCHIVE; generated
caches and node/test artifacts IGNORE; non-project files EXTERNAL (never `git
add .`). Removing/restoring cost-like output requires a new ADR (ADR 0011).

## Limitations

- 15-epoch pilots: single seed, no statistical significance — preliminary only.
- Small-damage slice remains the binding constraint for both architectures.
- Single uncontrolled photo → no physical scale, no hidden-damage detection, no
  cost estimates (by design).
- Synthetic data (CrashCar101-class) is training-only, never validation evidence.
- Quality gate rejects poor captures (`QUALITY_FAILED`) instead of emitting a
  fake mask.

## Next steps

See **`TASKS.md`** for the full tracker. Immediate: (1) rewrite trackers
(done), (2) final scoped git commits, (3) **60-epoch / 3-seed comparison** of
`ResNet34UNet` vs `HybridSegmentation` and RQ2 confidence-honesty operational
definition — the blocker for any architecture claim.