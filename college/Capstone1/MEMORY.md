# MEMORY.md — AutoInspect-X

Compact record of what this repository *now believes to be true*. This file is
re-written to reflect current state only; it does not duplicate `README.md`
(what it is) or `TASKS.md` (what is pending). Historical reasoning lives in the
ADRs and git log.

> **Integrity anchor:** the 15-epoch pilot numbers below are **preliminary
> validation observations, not a research conclusion.** No architecture is
> claimed superior until the locked 60-epoch / 3-seed comparison completes.

## Current state (2026-09-24)

- **Phase-I report delivered (Task E/E2).** `Capstone report/DSN4091 Capstone
  Project Phase-I Report - Kislay Anand.docx` + `.pdf` (78 pp. A4) generated
  from the sample-report structure and real repository evidence. Student:
  Kislay Anand (23BAI10359); supervisor Dr. Rudra Kalyan Nayak.
  **2026-09-24 final revision pass applied:** front matter (cover, bonafide,
  acknowledgements, abstract, LOF, TOC) preserved intact; Chapter 3 carries a
  precise 5-column tech stack with versions read only from repo manifests
  (requirements-ci.txt, package.json+lock, pyproject.toml, uv.lock); Chapter 4
  expanded to eight sections (4.4 Data Flow, 4.5 ML/CV Methodology, 4.7
  Novelty inserted; 4.6 UI renamed) with the real repository folder tree;
  Chapter 5 pseudo-code replaced by pointers to Appendix B; Appendix B holds 14
  complete verbatim listings with source path + true line ranges, all
  wrap-free at the emitted mono size. QC-verified: TOC/LOF page numbers
  converge (two-pass LibreOffice render), 22 LOF figures with pages, chapters
  start fresh pages, front-matter roman / body-decimal footers, no secrets,
  no cost/repair claims, no Underbelly content, no stripped-experiment names
  (only verbatim engine.py legacy-dispatch lines remain). Pilot numbers quoted
  verbatim from `run_record.json` (preliminary; see integrity anchor). Report
  builder script at `/tmp/opencode/revise_report.py` (surgical python-docx
  edits from `Capstone report/DSN4091 ... .docx`); report content is not
  maintained in-repo.
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
  `MODEL_PATH`/`MODEL_VERSION` env overrides (`.env.example`); `.env` points at
  `pilot15_hybrid` — **2026-09-22 it had been left pointing at the archived
  `cardd_hybrid_ce` run, which surfaced as "model unavailable" in the demo.**
  `container.py` resolves the checkpoint path CWD-/repo-root-independently and
  logs resolved path + registry metadata; `engine.from_checkpoint` accepts a
  `model` alias for legacy artefacts; the router classifies load vs. inference
  failures; the startup lifespan logs a clear error when the checkpoint is
  missing. New `tests/test_model_integration.py` covers all of this.
- **Gates (last full run):** ruff clean, mypy clean (86 files), pytest
  **144 passed**, eslint/tsc/next build clean.
- **Literature review:** `docs/research/literature_review.tex` + `references.bib`
  (30 verified refs), compiled with tectonic → `literature_review.pdf` (10 pp.,
  IEEEtran; `IEEEtran.cls`/`.bst` copied next to the tex for self-contained
  builds; `*.aux/bbl/blg/synctex` git-ignored). Author block = **Capstone Group
  160, School of Computing Science Engineering and AI, VIT Bhopal University,
  Sehore**; `\label{sec:hybrid}` added so `\ref{sec:hybrid}` resolves (was a
  dangling `??` the previous PDF silently rendered).

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
- Next recommended step and full tracker: `TASKS.md` (Phase-I report done;
  next: viva dry-run or the 60-epoch / 3-seed comparison).