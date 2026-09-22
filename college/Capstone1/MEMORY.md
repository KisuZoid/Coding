# MEMORY.md — AutoInspect-X

Compact record of what this repository *now believes to be true*. This file is
re-written to reflect current state only; it does not duplicate `README.md`
(what it is) or `TASKS.md` (what is pending). Historical reasoning lives in the
ADRs and git log.

> **Integrity anchor:** the 15-epoch pilot numbers below are **preliminary
> validation observations, not a research conclusion.** No architecture is
> claimed superior until the locked 60-epoch / 3-seed comparison completes.

## Current state (2026-09-22)

- **Project:** photo-first vehicle damage *segmentation* with an honesty
  contract (MODEL PREDICTION always labelled; no cost/severity/physical-area
  outputs — ADR 0011).
- **Research models (spec v3):** baseline `ResNet34UNet`, proposed
  `HybridSegmentation` (CNN encoder → transformer bottleneck → CNN decoder with
  skips). Legacy `CarddHybrid`/`CarddUNet` exist but are superseded; their model
  files stay live because the engine and train legacy dispatch load `cardd_*`
  checkpoints; run records are archived.
- **Models/checkpoints (git-ignored):**
  - `ml/experiments/pilot15_hybrid/best_checkpoint.pt` — **ACTIVE, demo
    default**, experiment `pilot15_hybrid-20260922-115320`, git `fb2fb59`,
    foreground mIoU 0.5963 / mDice 0.7320 / pixel acc 0.8873 @ epoch 14,
    ~27.9M params.
  - `ml/experiments/pilot15_baseline/best_checkpoint.pt` — **SUPERSEDED /
    retained baseline arm**, `pilot15_baseline-20260922-110722`, foreground
    mIoU 0.6127 / mDice 0.7440 / pixel acc 0.8979 @ epoch 14, ~24.6M params.
  - Both: 15 epochs, seed 0, full official CarDD splits, EMA weights, shared
    softmax-CE loss, class-sampled batches. **Both were still improving at
    epoch 14 → do not over-read.**
  - Large periodic checkpoints → `storage/models/pilot15_{baseline,hybrid}/`.
  - Historical experiment dirs + logs → `archive/experiments/` (git-ignored).
- **Registry:** `ml/experiments/registry.json` (list; git-ignored). Pilot
  entries carry `config` (full hyperparameters), `git_revision`, `best_epoch`,
  `best_val_foreground_miou`, `status`, `status_reason`. Legacy entries keep
  `best_val_mean_iou`; container falls back when foreground key absent.
- **Engine constraints (verified):**
  - `_build_model` normalizes `arch_l = "".join(arch.lower().split("_"))`;
    `resnet34unet`/`baseline` → ResNet34UNet; `hybrid`/`hybrid_segmentation` →
    HybridSegmentation; `carddhybrid` → CarddHybrid; empty/`carddunet` →
    CarddUNet; else `ModelVersionError`.
  - `from_checkpoint` enforces base-consistency **only** for arch names starting
    with `cardd` (research checkpoints store `base=0`); `experiment_id` defaults
    to parent dir name; tuple `(logits, aux)` outputs handled via `_main_logits`.
  - Honesty flags (`min_mean_confidence`, `min_damage_fraction`) are set per
    checkpoint by the container; demo-default thresholds are conservative.
- **API/UI defaults:** container default checkpoint = `pilot15_hybrid`;
  `MODEL_PATH`/`MODEL_VERSION` env overrides (`.env.example`); e2e journeys and
  integration tests trace the pilot15_hybrid path end-to-end.
- **Gates (last full run):** ruff clean, mypy clean (86 files), pytest
  **135 passed**, eslint/tsc/next build clean.
- **Literature review:** `docs/research/literature_review.tex` + `references.bib`
  (30 verified refs), compiled with tectonic → `literature_review.pdf` (10 pp.,
  IEEEtran; `IEEEtran.cls`/`.bst` copied next to the tex for self-contained
  builds; `*.aux/bbl/blg/synctex` git-ignored).

## Conventions (do not break)

- **Git:** repo root is the parent folder, not `Capstone1`. Never `git add .`
  / `git add -A`; always scope to `college/Capstone1/...`. Never commit
  `*.pt`, `storage/`, `ml/experiments/`, caches.
- **Evidence labels:** REAL GROUND TRUTH / WEAK LABEL / SYNTHETIC LABEL /
  DERIVED FEATURE / MODEL PREDICTION / ASSUMPTION stay distinct in code, data,
  docs, and UI (AGENTS.md §3).
- **Cost/severity/area:** reintroducing any cost-like field or physical-area
  claim requires a new ADR (ADR 0011).
- **Archive, don't delete:** superseded material → `archive/...` with
  provenance entries in `archive/README.md`.
- **Docs:** `docs/decisions/` (ADRs) and `docs/architecture/
  cnn-transformer-segmentation.md` (spec v3) are authoritative/append-only.
- **Experiments:** every run records experiment ID, dataset+version, splits,
  seed, code/model version, hyperparameters, metrics, assumptions in
  `ml/experiments/<id>/run_record.json` + registry (AGENTS.md §4).

## Open items

- RQ2 confidence-honesty operational definition not yet locked; RQ1 final
  comparison pending the 60-epoch / 3-seed run → `research_summary.md`.
- `cardd_*` demo-era model files kept live solely for legacy dispatch; safe to
  archive only after a documented decision that legacy load is dropped.
- Registry `data_root` points at the training machine path
  (`/content/data/CarDD_COCO`); harmless for inference but not portable metadata.
- Next recommended step and full tracker: `TASKS.md`.