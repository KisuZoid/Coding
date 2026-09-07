# MEMORY.md — AutoInspect-X

Running memory of what changed in this repository and why. Append a new entry
after every update, newest at the bottom. `TASKS.md` records *what was asked*;
this file records *what the project now believes to be true*.

Entry format:

```
## YYYY-MM-DD — <title>
**Change:** what changed
**Reasoning:** why it was done this way
**Current logic / state after the change:** the state a future session inherits
**Open questions:** anything unresolved
```

---

## 2026-09-07 — Repository bootstrap

**Change:**
Created the foundation of the repository: session protocol (`init.md`), agent
and tooling rules (`CLAUDE.md`, `AGENTS.md`), continuity files (`MEMORY.md`,
`TASKS.md`, `LOGIC.md`), project documentation (`README.md`, `CONTRIBUTING.md`,
`SECURITY.md`), architecture and research documentation under `docs/`, four
ADRs, Python tooling configuration, an environment template, ignore rules, and a
minimal CI workflow. Initialised Git.

**Reasoning:**
The bootstrap brief requires an architecture-first foundation with no product
functionality. Directories with no justified content were deliberately not
created, because empty scaffolding invites speculative code in later sessions.

**Current logic / state after the change:**

- The repository contains documentation and configuration only. There is no
  application code, ML code, database, or frontend.
- The research document `AutoInspect-X_Research_Report_Corrected.md` is **not**
  present. Everything in `docs/research/` is derived from the bootstrap brief
  alone and is marked as provisional until the research document arrives.
- Verified environment: Node v22.22.2, Python 3.13.12, uv 0.11.11, Docker
  present. Vercel CLI and n8n CLI are not installed.
- MCP servers: `playwright` configured; `github` configured but failing to
  connect ("Incompatible auth server: does not support dynamic client
  registration"); claude.ai Supabase connector available; Vercel plugin server
  available. **No n8n MCP server is configured.**
- Supabase: the connected account holds one project only, "Physios Plus CRM V3"
  (`nykalxhmbupsarhicrtd`), which belongs to a different product. AutoInspect-X
  has no Supabase project. Writing to that ref from this repository is
  prohibited.
- Automation: none exists. `LOGIC.md` documents the intended location and the
  contract that any future workflow must satisfy.

**Open questions:**

1. Where is the research document, and does it change the pipeline framing used
   in this bootstrap?
2. Which segmentation dataset will be used, and under which licence?
3. What is the real source of repair-cost labels? Until that is answered, cost
   values must be treated as SYNTHETIC LABEL, never as REAL GROUND TRUTH.
4. Does this project need a database at all, and if so, Supabase or Postgres?
5. Is any n8n automation actually planned, or was the mention exploratory?

---

## 2026-09-08 — Environment, Phase 1 CarDD audit, Phase 2 adapter prep

**Change:**
- Designated the **`ai` conda environment** as the ML workstation. Python 3.12.13,
  torch 2.5.1+cu121, torchvision, opencv-python, sklearn, pandas, numpy,
  mlflow, matplotlib. GPU: RTX 3050 Laptop, ~4 GB VRAM, CUDA 13.0 driver.
  `mypy` 2.3.1 and `pytest` installed into `ai` via uv pip (additive only).
- Phase 0 cleanup: unstaged a LibreOffice lock file, added `.~lock.*#` to
  `.gitignore`, corrected the project path in `init.md`, recorded the `ai` env in
  `CLAUDE.md`.
- Created `ml/` with the CarDD audit tooling (`cardd_audit.py`,
  `cardd_vis.py`) and the training adapter prep (`cardd_dataset.py`,
  `smoke_test.py`), plus `tests/test_cardd_dataset.py`.
- Fixed `.gitignore` so `/datasets/` anchors only the root dataset directory.

**Reasoning:**
The `ai` env is the only CUDA-enabled PyTorch runtime on this machine; ML code
must run there rather than in the repo's torch-free `.venv`. The audit and
adapter follow the phase plan: understand the data before choosing a model, and
validate label/mask mechanics before training.

**Current logic / state after the change:**

- CarDD-COCO is the working dataset: 6 damage classes, standard COCO instance
  format. Splits: train 2816/6211, val 810/1744, test 374/785. No image-level
  leakage, no duplicate images, no missing files. Strong class imbalance
  (scratch heavy, tire flat 9% of scratch) and large per-class area spreads.
- **CarDD provides damage masks but NO vehicle-part masks.** The research
  feature `normalized_damage_area = damaged_pixels / part_pixels` therefore
  needs a part-segmentation source that CarDD does not supply. This is an open
  design decision.
- The training adapter (`CarddInstanceSegDataset`) is lazy, split-scoped,
  seedable, and returns per-instance binary masks + category ids at 512×512 with
  a padding collate for variable instance counts. Augmentation beyond resize is
  not yet implemented.
- Quality gates pass in `ai`: ruff, ruff-format, mypy, pytest (6), and the
  standalone smoke test.
- The research document is still absent; no research-facing code reconciled.

**Open questions:**

1. What segmentation framework/model wins Phase 3 (ultralytics YOLO seg vs.
   raw PyTorch)? Needs an ADR.
2. Is vehicle-part segmentation in scope, and from where (CarDD lacks parts)?
3. Still pending (from bootstrap): real cost-label source; database decision;
   n8n automation; research document location.

---

## 2026-09-08 — Phase 2: typed CarDD adapter, GROQ env template, ADR 0005

**Change:**
- Created `ml/datasets/cardd_adapter.py`: a typed adapter that owns all CarDD
  reading — COCO JSON loading, split validation, categories, annotations, image
  loading, polygon rasterization. `ml/training/cardd_dataset.py` now consumes it
  instead of re-parsing JSON, so audit and training share one read path.
- Added `ml/__init__.py`, `ml/datasets/__init__.py`, `ml/training/__init__.py`
  so `ml.*` imports are unambiguous to mypy (was "source file found twice").
- Added `GROQ_AUTO_INSPECT_API_KEY=` to `.env.example` under a new LLM (Groq)
  section — the live `.env` had the key, the template did not.
- Recorded ADR 0005: CarDD has **no vehicle-part masks**, so
  `normalized_damage_area = damaged_pixels / part_pixels` is not implemented and
  not reported from CarDD-only data. Only `damage_pixels / total_image_pixels`
  is derived, as a DERIVED FEATURE. A part-mask source, if adopted later, needs
  its own ADR with licence and label-mapping rules.
- Added `tests/test_cardd_adapter.py` (5 tests, dataset-gated); fixed import
  paths in `smoke_test.py` (sys.path bootstrap) and `cardd_vis.py`.

**Reasoning:**
Phase 2 exists to make the data layer trustworthy before any model: a single
typed read path means training and evaluation cannot diverge on split names,
polygon layout, or category ids. ADR 0005 makes the research-integrity rule
(ADR 0004) concrete for the area feature so no later code accidentally reports a
part-normalized ratio that the data cannot support.

**Current logic / state after the change:**

- CarDD read path: `CarddAdapter` → `CarddInstanceSegDataset` (lazy, split-scoped,
  512×512, padding collate). Public dataset API unchanged.
- Area feature rule: only image-denominator ratio is derivable today.
  `normalized_damage_area` name reserved for the part-normalized form.
- Package layout: `ml/datasets`, `ml/training` are real packages now.
- `.env.example` covers `GROQ_AUTO_INSPECT_API_KEY`.
- Quality gates: ruff clean, format clean, mypy clean (10 files), pytest 11
  passed, standalone smoke test passed (no leakage, forward/backward OK).
- Both mandated root documents are still absent; nothing research-facing has
  been reconciled.

**Open questions:**

1. Segmentation framework for Phase 3 (needs ADR; candidate: ultralytics YOLO
   seg vs. raw PyTorch residual-unet).
2. Is vehicle-part segmentation in scope; if yes, from which source?
3. Research document + bootstrap update doc still missing — where are they?
4. Cost-label source remains unknown; costs stay SYNTHETIC until a real source.

---

## 2026-09-08 — Phase 3: framework ADR, small U-Net, GPU smoke training run

**Change:**
- ADR 0006: segmentation framework is **raw PyTorch small U-Net** (ultralytics
  YOLO deferred as a potential comparison baseline only).
- `ml/models/cardd_unet.py`: compact U-Net (`_DoubleConv`, pool-down,
  convT-up, skips; base 32 → ~1.93 M params).
- `ml/training/train_smoke.py`: tiny seeded training loop (per-class mask
  aggregation, positive-pixel-weighted BCE, run record + checkpoint under
  `ml/experiments/`, git-ignored).
- Ran it on the RTX 3050 (cuda): mean BCE 0.685 → 0.584 → 0.489 over 3 epochs,
  one-batch val pixel-accuracy 0.40. Loss decreasing → machinery verified.

**Reasoning:**
The phase goal is verifying the training machinery end-to-end within 4 GB VRAM,
not producing a model. Raw PyTorch reuses the typed adapter, requires no new
install, and keeps loss/metrics under our control so baselines (vision-only /
simple-fusion) can be compared on identical splits and seeds later.

**Current logic / state after the change:**

- Full ML path now exercised on GPU: `CarddAdapter` → `CarddInstanceSegDataset`
  → DataLoader → `CarddUNet` → BCE → backward → checkpoint → one inference pass.
- Loss design: per-class binary targets indexed by CarDD category id
  (channel 0 = background); loss weights by positive pixels so imbalance does
  not zero-out the gradient.
- `ml/experiments/` is git-ignored; committed docs reference experiment IDs.
- Smoke loss is a smoke signal, not a research result. No accuracy claims.
- Quality gates: ruff clean, format clean, mypy clean (12 files), pytest 11
  passed, standalone smoke test passed.

**Open questions:**

1. Research document + bootstrap doc still absent — everything research-facing
   (metric set, final architecture, cost labels) stays provisional.
2. Actual experiment harness (augmentation, LR schedule, mIoU/Dice harness,
   checkpoint registry) is Phase 4+ territory, pending the research report.
3. Vehicle-part segmentation scope still open (ADR 0005 constrains area
   features to image-denominator until a part source exists).

---

## 2026-09-08 — Phase 4: segmentation experiment harness

**Change:**
- `ml/training/loss.py`: `aggregate_targets` / `bce_loss` shared by smoke + real
  trainers (single target/loss definition; `train_smoke.py` now imports them).
- `ml/evaluation/metrics.py`: confusion-matrix based `per_class_iou`,
  `per_class_dice`, `mean_iou`, `mean_dice` (background excluded by default;
  absent classes = 0.0; exact for perfect predictions).
- `ml/training/cardd_dataset.py`: optional `augment=True` → random horizontal
  flip applied to image+masks together + mild brightness/contrast jitter
  (global torch RNG → reproducible, varies per epoch). Default off, existing
  behaviour unchanged.
- `ml/training/train.py`: `TrainingConfig` dataclass, seed, CosineAnnealingLR,
  per-epoch val mIoU/mDice/per-class/pixel accuracy, best-checkpoint save,
  `run_record.json`, and appends to `ml/experiments/registry.json`.
- Phase 4 baseline GPU run (tiny subset): train BCE 0.580→0.371 over 3 epochs;
  val mIoU 0.045→0.054, mDice 0.083→0.100. Machinery verified; not a result.
- Fixed output-path bug: experiments now write to repo-root `ml/experiments/`.
- `tests/test_evaluation_metrics.py` (+5, dataset-independent).

**Reasoning:**
The recorded Phase 4 follow-up is to turn the smoke trainer into a real
experiment harness. Metrics must be standard (IoU/Dice) because they are what
research reporting will need, but the set stays explicitly provisional until the
research document arrives. Sharing one loss/target definition prevents the smoke
and real paths drifting apart semantically. Augmentation lives in the dataset so
image/mask correspondence is preserved by construction.

**Current logic / state after the change:**

- Training path: `CarddAdapter` → `CarddInstanceSegDataset` (optionally
  augmented) → DataLoader → `CarddUNet` → `bce_loss` → backward → scheduler →
  per-epoch val metrics → best checkpoint → `run_record.json` +
  `registry.json` (git-ignored; committed docs reference experiment IDs).
- Metric semantics: classes indexed by CarDD category id, channel 0 background;
  overlaps collapse via argmax (rare; documented limitation). Absent classes
  score 0.0, macro means exclude background.
- `ml/evaluation/` now exists; `CLAUDE.md` layout reflects it.
- Quality gates: ruff clean, format clean, mypy clean (17 files), pytest 16
  passed, smoke test passed, Phase 4 train run OK.

**Open questions:**

1. Research document + bootstrap doc still absent — finalized metric set,
   architecture, and cost labels stay provisional.
2. The concrete phase-by-phase plan for phases 4–18 from the original brief is
   not stored verbatim in the repo; the next phase should be confirmed against
   the brief (likely baseline training at meaningful scale).
3. Checkpoint resume and fixed train/val sample splits are pending; no hparam
   claims yet.

---

## 2026-09-08 — Phases 5–12: research-doc reconciliation, locked experiment, metrics extension, full baseline, error analysis, part-seg decision, cost data-readiness

**Change:**
- **Mandated docs in repo root** (copied from `~/Downloads/`):
  `AutoInspect-X_Research_Report_Corrected.md` (research source of truth) and
  `CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md`. Provenance note: the research
  file's Downloads name was truncated (`ROLE_Act as a senior AI_ML research
  advisor, rese....md`); exact-filename match unconfirmed.
- **Phase 5** `docs/research/implementation-alignment.md`: research-vs-code
  reconciliation table (CarDD counts, framework divergence, part-mask/`A_phys`
  gap, hidden-damage not started, quantile-cost blocked, citation-integrity).
- **Phase 6** `docs/research/segmentation-experiment-config.md`: locked config —
  official splits; 7 channels; 512×512; batch 2 (VRAM 2.85 GB peak measured);
  Adam 1e-3 / 1e-5; CosineAnnealingLR; 5 epochs; seed 0; best val mIoU.
- **Phase 7** metric harness: `per_class_precision/recall` + macro means;
  `ml/evaluation/small_damage.py` (small = below train p25 area ≈ 3014 px @ 512,
  measured); `ml/evaluation/evaluate_run.py` (full overall/per-class/small +
  montages); 5 new tests.
- **Loss correction — ADR 0007 then ADR 0008.** BCE was structurally broken: the
  first full run (`cardd_baseline_full`) collapsed (train BCE 1e-4, model never
  predicted background). Root cause: BCE+argmax incompatible with
  `background = never-set channel`. **Adopted softmax CE over the argmax class
  target** (`loss.py::cross_entropy_loss`). `train.py`/`train_smoke.py` updated.
- **Pixel-accuracy bug fixed**: normalize by class-map pixels (not 7× channels).
- **Phase 8** real baseline `cardd_baseline_ce` (base 64, full train, 5 epochs,
  batch 2): train CE 0.92→0.75; best val mIoU 0.0475 (ep 2); val pxAcc 0.760,
  test pxAcc 0.762, small-damage ≈ 0. `research_summary.md` written. Underfit —
  not a research conclusion.
- **Phase 9** `ml/analysis/error_analysis.py` + report: FN dominates; small
  damage invisible; large damage partially recovered; FP on plausible surfaces.
- **Phase 10** `ADR 0009`: **part segmentation NOT adopted** — image-denominator
  `damage_area_ratio_image` stays the only area feature (no part-mask source).
- **Phase 11** `docs/research/cost-multimodal-data-readiness.md`: verified by
  schema inspection that CarDD has no make/model/year/variant, no repair
  action/location, **no observed cost/currency/parts/labour** → **cost-model
  implementation stops** (per plan + AGENTS.md). Only damage classes
  (REAL GROUND TRUTH) and image-denominator area (DERIVED) are available.

**Reasoning:**
The user's Phase 5–12 plan requires research-grounded decisions, not more
machinery. CE-over-argmax was forced by evidence (two failed BCE runs) and makes
the training objective identical to the metric decode. Part segmentation and cost
were both ruled by data honesty (AGENTS.md §3/ADRs 0005/0009; Phase 11 schema
check): a viable cost pipeline needs real labels that do not exist.

**Current logic / state after the change:**

- **Correct training objective (ADR 0008):** softmax CE on the argmax class
  target; decode == metric decode == argmax. Background is a real class.
- **Correct small-damage criterion:** train p25 area ≈ 3014 px @ 512 (measured).
- **Experiments (git-ignored):** `cardd_baseline_ce` = the Phase 8 baseline;
  `cardd_baseline_full`, `phase8_fixcheck`, `phase8_midsize_fixcheck` =
  superseded BCE provenance (not comparable).
- **Reports live with their run:** `research_summary.md`, `evaluation/*` montages,
  `error_analysis/*` per `ml/experiments/<run>/`.
- **Gates:** ruff clean, format clean, mypy clean (18 source files), pytest 22
  passed, smoke test passed, full eval + error-analysis runs executed.
- **Current scope (unchanged by design):** vision-only path through segmentation
  only. No cost, no fusion, no cross-attention, no frontend, no LangGraph/Groq.

**Open questions / known gaps:**

1. Baseline is a 5-epoch underfit (FN-dominated, small-damage ≈ 0) — needs more
   epochs / larger effective batch before any architecture conclusion.
2. `.github/workflows/ci.yml` still missing despite docs claiming it.
3. Cost/multimodal work is blocked on real labels; a SYNTHETIC study is
   possible only behind a new ADR that labels it as SYNTHETIC LABEL.
4. Research report filename provenance vs the exact `..._Corrected.md` name.
