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

---

## 2026-09-08 — Product build Phase A: repository-wide audit + implementation gap report

**Change:**
Produced a full repository audit against the complete-product brief and wrote it
to `docs/architecture/implementation-gap-report.md` (14 sections + video
appendix). No application code written; the audit is the mandated Phase A
deliverable and the input to phases A–R.

**Reasoning:**
The brief explicitly forbids product implementation before the audit is
reported, and AGENTS.md/CLAUDE.md require inspect-before-coding. Confirming what
exists (vs the docs' claims) prevents rebuilding the ML pipeline and prevents
violating the frustrated ADR boundaries (0003 inference separation, 0005 area
rule, 0008 loss, 0009 part segmentation).

**Current logic / state after the change:**

- **Runtime for the product is decided:** the backend will run in the `ai`
  conda env — it already has fastapi/uvicorn/pydantic/python-multipart/
  langgraph/groq/langchain/torch/opencv/pillow, so net-new Python runtime deps
  ≈ none. Frontend uses Node v22 + npm 10.9 available at repo env.
- **Inference engine confirmed:** `ml/experiments/cardd_baseline_ce/
  best_checkpoint.pt` (CarddUNet base 64, 7 channels; dict keys `model_state`,
  `base`, `epoch`); used via a new `ml/inference/` module (ADR 0003) with
  `MODEL_PATH`/`MODEL_VERSION` env resolution. Underfit (val mIoU 0.0475) →
  demo-grade with confidence + low-confidence mode, never production-claim.
- **Videos mapped as a single 30.4 s timeline:** 1.mp4 0–10 s (1080p),
  2.mp4 10–18 s, 3.mp4 18–22.4 s (720p), 4.mp4 22.4–30.4 s; scroll progress →
  `currentTime` seek. Narrative copy is an **open item** — this agent has no
  image input support, so semantic content was verified only programmatically.
- **Storage decision:** local fs behind `ImageStore`/`SessionStore`/
  `TrainingSampleStore`/`ConsentStore` interfaces + stdlib SQLite; Supabase
  untouched (Physios Plus CRM V3 remains off-limits); swap to S3/Postgres later
  without touching domain logic.
- **Cost/repair honesty contract confirmed:** `cost_status=DATA_UNAVAILABLE`
  default; P10/P50/P90 reserved; synthetic demo only behind an explicit flag and
  always labelled "DEMO / SYNTHETIC ESTIMATE — NOT A REAL QUOTE"; repair action
  via a labelled "preliminary demonstration rule".
- **`ci.yml` discrepancy confirmed still open:** `.github/` does not exist.
- **View-of-registry gap recorded:** `registry.json` has no STATUS/superseded
  field (ADR 0008 provenance lives in ADR prose only).

**Open questions:**

1. Video narrative copy — needs a vision-capable review or user direction before
   Phase O.
2. Confirm the demo repair-rule acceptance ("preliminary demonstration rule") is
   acceptable for the teacher showcase (vs no rule at all).
3. Whether to extend the baseline model later (more epochs) to improve demo
   believability before/after the product build — research track, decoupled from
   product phases A–R.

---

## 2026-09-08 — Product build Phase D: ml/inference (ADR 0003)

**Change:**
Created `ml/inference/` (classes, errors, preprocess, engine) wrapping the
CarDD baseline checkpoint behind a typed, honest inference API. 12 new tests +
a real-artefact smoke test; suite now 66 passing; ruff/mypy clean. `ml/training`
stays frozen (ADR 0003: API depends on the inference layer only).

**Reasoning:**
The training contract was verified first: CarddUNet base 64 / 7 channels,
argmax decode, and preprocessing = RGB → cv2 resize 512×512 INTER_LINEAR →
float32 CHW × (1/255) (exactly `ml/training/cardd_dataset.py`). Inference
reproduces that transform and pins equivalence with a recompute test — no
cross-import of training code. Loading follows the artefact contract
(`model_state`/`base`/`epoch`): missing/garbage/mismatched artefacts raise
typed `ModelLoadError`/`ModelVersionError` — there is no silent fallback (ADR
0003). Quality is honest by construction: every result carries the
demo-baseline limitation notes (underfit, mIoU ~0.0475, severity unreliable)
and a `low_confidence` flag from `min_mean_confidence=0.5` and
`min_damage_fraction=0.001`, so nothing downstream can present the mask as
verified ground truth. `git_revision` is only set when explicitly passed
(verified from registry evidence, e.g. `cd2c9c1`), never fabricated.

**Current logic / state after the change:**

- `SegmentationEngine.from_checkpoint(path, model_version=..., device=...)` is
  the seam the API will wire with `MODEL_PATH` in Phase G.
- `predict(rgb)` → `SegmentationResult` (argmax mask 512², softmax 7×512²,
  pixel confidence, mean confidence, class/damage fractions,
  `QualityAssessment`, `ModelMetadata`); `to_dict()` is the compact JSON
  payload (mask base64 PNG + per-class prob summaries).
- Class map is verbatim CarDD COCO: 0=background, 1..6 =
  dent/scratch/crack/glass shatter/lamp broken/tire flat (7 channels, ADR 0008).
- Real baseline smoke passes: `best_checkpoint.pt` loads and predicts a
  1080×1920 input on CPU (~12 s incl. torch load).
- The device default is `cuda` when available, else CPU; model is ~3M params so
  CPU demo is fine.

**Open questions:**

1. Whether `min_mean_confidence`/`min_damage_fraction` defaults (0.5/0.001)
   become product config or remain code defaults — they bias toward
   `low_confidence=True`, the honest baseline posture. Decide in Phase G
   settings wiring.
2. Feature extraction (damage area ratio per class per ADR 0005, presence,
   demo severity framing) is Phase E — not yet built, so nothing should consume
   `SegmentationResult` beyond this phase's tests.

**Change:**
Added the storage subsystem under `apps/api/storage/`: typed records + StrEnum
constants, four Protocol contracts (ImageStore, SessionStore, ConsentStore,
TrainingSampleStore), a stdlib-sqlite3 `Database` with idempotent schema, SQLite
session store, fs+SQLite image store (validation + EXIF strip + path-traversal
guard), SQLite consent + training-sample stores, and a `SessionCleanup`
service. `Settings` gained `database_url`. 26 new tests; gate suite now 54
passing; ruff/mypy clean.

**Reasoning:**
Interfaces precede implementations (mandate §20) so Postgres/S3/Supabase can
replace the sqlite/fs backend without touching domain logic. Training data is
kept structurally unreachable from cleanup: `training_samples` has no FK
cascade from `sessions`, and `SessionCleanup` only deletes image files + asset
rows + soft-closes the session (mandate §17). Privacy default: upload bytes are
re-encoded so EXIF/location metadata is stripped unless `strip_exif=False` is
explicitly requested. `is_valid_id` whitelist + resolve-time escape guard block
path traversal. SQLite is the only DB backend until a Postgres ADR exists
(`DATABASE_URL` already parsed by `resolve_database_path`).

**Current logic / state after the change:**

- Storage layout: session images under `<storage_root>/<session_id>/`, asset
  ledger in SQLite, consented samples under a `dataset_version` in separate
  tables; default DB at `storage/app.db` (all git-ignored).
- `SessionCleanup.cleanup(sid)` → deletes session images+rows and marks the
  session CLOSED; `sweep_expired(now)` does the same for expired active
  sessions. Consent + training samples survive both.
- Session default TTL = 6h (expires_at stored as UTC ISO).
- EXIF: `normalize_image` re-encodes with `exif=b""` by default; PNG has no
  EXIF transport so is re-saved clean; `strip_exif=False` re-embeds the camera
  EXIF for JPEG/WebP.
- Imports: `apps.api.storage` re-exports records, stores, Database,
  SessionCleanup, resolve_database_path, ImageValidationError.

**Open questions:**

1. Cleanup hook mechanism: FastAPI lifespan periodic task vs on-session-close
   endpoint (decide when those endpoints exist — Phases G/P).
2. `database_url` default ("" → storage/app.db) — confirm in .env.example
   wording when the app wires config (Phase G).

---

## 2026-09-08 — Product build Phase B: backend foundation

**Change:**
Created the FastAPI backend foundation under `apps/api/`: `Settings`
(pydantic-settings, env names aligned to `.env.example`), `create_app()` factory
with `apps.api.main:app` as the uvicorn target, `GET /health`, shared contract
`HealthResponse`, an app-level `conftest.py` sys.path seam, and 6 dataset-
independent tests. `.gitignore` now excludes `/storage/` and `/data/training/`.
Gates green: ruff, format, mypy (32 files), pytest 28.

**Reasoning:**
Phase B exists to make the backend runnable and type-tested in the `ai` env
before any business logic lands. The `Annotated[..., Depends(...)]` pattern is
used instead of default-arg `Depends()` (ruff B008). `groq_api_key` reads the
authoritative `GROQ_AUTO_INSPECT_API_KEY` alias — a real bug found by testing:
an unaliased field would have bound to the ambient `GROQ_API_KEY` and silently
never used the real key. Storage interfaces/tables are deliberately NOT built in
this phase (deferred to C, when session/training record types exist) to honour
"no speculative abstraction". No runtime deps were installed — the `ai` env
already provides fastapi/uvicorn/pydantic/langgraph/groq.

**Current logic / state after the change:**

- API entry: `uvicorn apps.api.main:app` in the `ai` env; `/health` returns
  `{status, service, environment, version}`; version = "0.1.0" in
  `apps/api/__init__.py`.
- Settings are env-driven and lru-cached; `allow_synthetic_estimate` defaults
  False (cost demo stays behind an explicit flag); storage roots default to
  `storage/` and `data/training/` (both git-ignored now).
- Tests: `python -m pytest tests/` in `ai` = 28 passed (6 new API tests; the
  ambient-shell `API_URL`/`GROQ_API_KEY` env values taught us defaults tests
  must not depend on the host environment).
- Repo paths: `apps/api/{settings,main}.py`, `apps/api/routers/health.py`,
  `apps/api/shared/schemas.py`, root `conftest.py`.

**Open questions:**

1. New `apps/api` pyproject/lockfile decision deferred to Phase R (CI/deploy);
   for now app deps are physically present in `ai` and documented in the gap
   report §6.
2. Open items from Task 7 unchanged: video narrative copy (Phase O), demo
   repair-rule confirmation (Phase I).

---

## 2026-09-08 — Product build Phases E–K: inversion pipeline wired end-to-end (features/quality/context → LangGraph agent → Groq → repair/cost → consent/state → API)

**Change:**
The backend product path is now complete and green: `ml/inference` exposed
features + overlay; `apps/api/vision/quality.py` validates uploaded photos;
`apps/api/inspection/context.py` builds the inbound inspection context and the
user-vs-model comparison; `apps/api/agent/` implements the LangGraph agent
(extraction via Groq), `repair/` + `cost/` implement the honest repair/cost
rules, `consent_service.py` + `state_store.py` gate training and persist
session state, and `container.py` + routers + `main.py` wire everything into a
bootable FastAPI app. Verification: ruff clean, format clean (82 files), mypy
clean (81 source files), **138 pytest passed** (was 66), `/health` 200 with 7
OpenAPI routes.

**Reasoning:**
Each phase reuses the prior seams: vehicle/incident metadata flows into
`InspectionContext`; the agent's `run_turn` model means every POST /chat is one
graph execution and session state persists as JSON in `session_states`;
`check_context_ready` now *harvests* the incident/damage from the first real
message and only asks for the genuinely-missing optional fields (a turn-counter
fix measured against the flow tests). Honesty defaults are enforced structurally:
the cost estimator *cannot* produce a number (DATA_UNAVAILABLE unless
ALLOW_SYNTHETIC_ESTIMATE, and then only with the demo label), the repair rule
carries `Preliminary demonstration rule` as `RULE_LABEL`, and consented training
samples are written only after `record_decision(GRANTED)` while session cleanup
can never reach training rows (existing storage invariant).

**Current logic / state after the change:**

- **API surface (7 routes):** health, inspections (POST/GET/DELETE), upload
  photo, analyze photo, consent; chat (POST /chat turns the state machine).
- **Agent flow:** greeting/incident harvest → optional fields loop
  (DAMAGE_LOCATION → REPAIR_LOCATION → INSURANCE, cursor-based, "skip"-aware) →
  PHOTO → photo validation (quality validator) → damage analysis (engine) →
  feature extraction → compare_user_vs_model → downstream prediction →
  cost_availability → repair_decision_validation → result_validation →
  final_explanation → consent_prompt (writes GRANTED sample via ConsentService)
  → finalize on next turn (waiting_for=FINISH).
- **Quality validator ordering pinned:** luminance (TOO_DARK) → glare
  (EXCESSIVE_GLARE) → blur (TOO_BLURRY) → contrast (INSUFFICIENT_CONTEXT);
  WRONG_ANGLE/DAMAGE_NOT_VISIBLE remain contract-only (applied later by
  analysis, never fabricated).
- **Extraction (Groq):** `GroqService` protocol with `RuleBasedGroqService`
  (offline, deterministic, used in tests) and `GroqLLMService` (JSON
  response_format with rule fallback); `build_groq_service` only uses the
  server-side `GROQ_AUTO_INSPECT_API_KEY` when present.
- **Feature set:** mask → class presence (verdict map), `damage_area_ratio_image`
  per class (ADR 0005), bounding boxes, min component pixels; confidence +
  `low_confidence` from the engine's honest `QualityAssessment`.
- **Registry metadata flows into the engine** (`git_revision`, best val mIoU as
  `baseline_notes`) — read data-driven at container build, never hard-coded.
- `.env`/settings: `training_dataset_version = "user-consented-v1"`; storage
  files/DB still git-ignored; Supabase untouched.

**Open questions:**

1. Frontend phases L–O are the next workstream (apps/web: Next.js + Tailwind +
   TS strict), including Phase O video narrative copy that a vision-capable
   reviewer (or the user) must confirm — the agent has no image input.
2. Whether `min_mean_confidence`/`min_damage_fraction` (0.5/0.001) should
   become product config vs code defaults.
3. Whether to extend the baseline (more epochs/batch accumulation) to improve
   demo believability before the product showcase.
4. `ci.yml` discrepancy (Phase R) and the PyPI lockfile for app deps remain
   open.

---

## 2026-09-08 — Product build Phases L–O: Next.js frontend (cinematic intro + chat/inspection UI + results + consent)

**Change:**
Built the frontend at `apps/web` (Next 16.3.4, React 19, TS strict, Tailwind v4,
ESLint flat) plus two small, justified backend changes. `/` = scroll-driven
cinematic over the four clips (`public/1..4.mp4`, served via
`apps/web/public/videos` symlink → repo `public`), seeking each clip's
`currentTime` from scroll progress on a single 0–30.42 s timeline, with
segment-ruled narrative overlay + end CTA. `/demo` = the single inspection
journey: typed API client (`lib/api.ts` + `lib/types.ts` mirroring the pydantic
schemas) → agent chat (ChatPanel) → context card (WHAT YOU TOLD US / USER
provenance) → photo bay (guidance/upload/analyze/retake) → four labelled result
blocks (model prediction + overlay, cost DATA_UNAVAILABLE, demo repair rule)
→ optional consent banner → finish. Backend: added CORS (settings
`cors_origins`, default `["http://localhost:3000"]`, CORSMiddleware) and a
bare-yes/no consent rule (`yes`/`no` were previously never resolved by the rule
extractor because they lacked photo/image/train/data context).

**Reasoning:**
The product is one journey, not unrelated pages (gap report §8), so the app is
two routes: the pinned cinematic lands, then `/demo` drives the state machine
via the existing API (no new endpoints). Honesty is enforced at the UI boundary
too: every result block carries an explicit provenance tag, cost shows
"no real quote is available", the overlay is only the predicted mask, and
consent is optional and labelled. CORS is a strict allowlist from settings —
never a wildcard — because the API is meant for the demo frontend only. The
bare-consent fix was forced by an E2E test of the actual UI flow: the consent
prompt asks "yes / no", and the rule extractor could never answer a bare yes/no.

**Current logic / state after the change:**

- Backend unchanged in shape; two additive fixes: CORS middleware
  (origin allowlist) and consent extraction for bare yes/no.
- Frontend gates are the new definition of done for `apps/web`:
  `npm run lint` (0 warnings), `npm run typecheck`, `npm run build`.
- Browser → API contract is one typed client; `NEXT_PUBLIC_API_URL` defaults to
  `http://localhost:8000`; backend CORS defaults to `http://localhost:3000`.
- Cinematic timeline is data-driven from `lib/video.ts` (clip boundaries,
  segment copy). Narrative copy is neutral and marked PENDING_USER_CONFIRMATION
  — the coding agent cannot see the clips.
- Videos are git-tracked at the repo root `public/`; the frontend references
  them via a symlink (`apps/web/public/videos`). This is a fresh-clone
  dependency: the symlink must resolve to the repo-root `public/`.
- Full API journey verified live (TestClient): chat → REPAIR_LOCATION →
  INSURANCE → PHOTO → upload+analyze → pipeline → CONSENT → "yes" → FINISH →
  finished; results surface repair=MANUAL_REVIEW, cost=DATA_UNAVAILABLE,
  comparison=PARTIAL_AGREEMENT, consent=GRANTED.

**Open questions:**

1. Phase P (committed backend E2E test) and Phase Q (Playwright) are the next
   workstreams; Playwright browser availability on this machine is unverified.
2. Narrative copy for the four clips needs a vision-capable reviewer or the
   author's confirmation before Phase R finalises it.
3. Deploy (Vercel/etc.) and a shared frontend/backend lockfile story remain
   Phase R items.
4. The baseline model stays demonstration-grade (low_confidence usually true) —
   improving believability is a research-track decision, decoupled from the
   product build.

---

## 2026-09-08 — Phase P: full end-to-end integration tests + capture-quality wiring

**Change:**
Added `tests/test_e2e_integration.py` (8 durable HTTP tests) that drive the
browser contract through one app per test: happy path against the committed
checkpoint (skip-if-absent, never fail), poor-image rejects then a successful
retake, low-confidence proceeds with an honest flag, DISAGREEMENT /
PARTIAL_AGREEMENT via deterministic stub SegmentationResults, engine-failure 500
with a surviving session, consent-endpoint GRANTED persists a training sample,
and edge validation. Two integration gaps surfaced and closed: `/analyze` now
runs the Phase E `validate_image` gate (422 `{status, reasons}` for
blurry/dark/glare/low-contrast before any model inference) and persists honest
top-level `analysis.low_confidence`/`quality_reasons`; and chat soft-closes a
session on `finished` (410 Gone after). The graph's `damage_analysis` retake now
keys only on hard `quality_reasons`, never on soft low confidence (avoids a
phantom retake-loop on the demo baseline). A real retake bug — `/upload` used
`setdefault`, so a photo taken after a 422 could never replace the rejected one —
was fixed (assignment instead). Frontend: `ApiError` now carries the parsed body
and `DemoJourney` renders quality-reject reasons as a friendly PhotoBay retake
prompt.

**Reasoning:**
Phase P's job is proving the wiring, which only writes durable tests + the
minimal missing pieces the tests expose. Quality rejection belongs in the API
(rejection loop per the gap report), while low model confidence is a soft banner
signal — otherwise the always-low-confidence demo baseline would loop forever on
its own honest flag. Session close-on-finish matches the storage contract
(CLOSED audit row, images gone, `cleanup`/`sweep_expired` untouched). The
`ApiError.body` change keeps the abort message readable while giving the UI the
typed 422 it needs.

**Current logic / state after the change:**

- `/analyze` → 422 quality reject (before engine) or 200 with overlay +
  `low_confidence` (soft); the workflow retake branch is defensive-only.
- A finished chat turn closes the session (410 for GET/chat; DELETE idempotent).
- Uploaded photo always supersedes the previous one in session state.
- Frontend gates unchanged: lint 0 warnings, typecheck, build.
- Test inventory now accurate: **122 tests**. (Earlier "142"/"138" figures in
  this file and TASKS were not measured and are superseded.)

**Open questions:**

1. Phase Q (Playwright) next; browser toolchain on this machine unverified.
2. ci.yml (Phase R) could now run backend gates + frontend gates + E2E.
3. Narrative copy for the four clips still needs a vision-capable reviewer or
   author confirmation.

## 2026-09-08 — Phases Q + R: Playwright browser E2E, CI workflow, cleanup/docs

**Change:**
- **Phase Q (browser E2E).** `apps/web` gained `@playwright/test` (1.63.0),
  `playwright.config.ts` (desktop/tablet/mobile projects on the system Google
  Chrome via `channel: "chrome"` — no browser download; `webServer` boots
  backend on :8000 and `next start` on :3000, `reuseExistingServer`), and
  `e2e/` specs. `e2e/png.ts` synthesises PNG fixtures in pure Node (zlib) —
  validated against `ImageQualityValidator` (VALID sharpness 2093 vs TOO_BLURRY
  1.9). `helpers.ts` retries a chat turn whose send races session creation (the
  demo silently drops a send before its session exists — detected by user-bubble
  count). Journeys: happy path (honest "No real quote available." + provenance
  chips + consent + finish) and blurry→retake→success on desktop; responsive
  shell on all three viewports. Real-engine journeys skip when the git-ignored
  checkpoint is absent — same contract as the pytest skip.
- **Real bug the suite exposed and fixed:** `FsSqliteImageStore.read` reused the
  already root-prefixed record path as the relative path, so a relative storage
  root (`Path("storage")`, the production default) produced
  `storage/storage/<session>/…` and every `/analyze` 500'd. Fix: always
  `asset.path.relative_to(self._root)`; regression test
  `test_read_roundtrip_with_relative_root` (tests only used absolute tmp roots
  before, which masked it).
- **Phase R (cleanup/docs/CI).** `.github/workflows/ci.yml` (backend gates on a
  CPU venv built from pinned `requirements-ci.txt` + `uv sync --group dev`; frontend
  gates; Playwright job using `BACKEND_CMD` so the config's conda default is
  overridden on CI). `requirements-ci.txt` is the CPU-runtime subset of the `ai`
  env (torch/torchvision from the PyTorch CPU index; `onnxruntime`/`aiosqlite`
  omitted — installed in the work env but referenced nowhere). `overview.md`
  rewritten to the implemented system; `implementation-gap-report.md` marked
  superseded (retained as the historical Phase A audit); `registry.json` gained
  `status`/`status_reason` on all 6 runs (`cardd_baseline_ce` = ACTIVE, the rest
  SUPERSEDED).

**Reasoning:**
The browser suite must prove the real wiring (real engine + real UI), while API
determinism (disagreement, engine-failure 500, edge validation) already lives in
the TestClient suite — so Playwright stays small and flake-resistant. CI must
not hard-depend on the GPU workstation or the git-ignored weights: CPU pins +
skip-if-absent keep it green without weakening the local suite. The storage
`read()` fix was a genuinely missing path predicate, not covered by the
absolute-root tests.

**Current logic / state after the change:**

- Relative storage roots resolve exactly once (both `read` and `write` agree).
- Browser suite: `npx playwright test` → 5 passed / 4 skipped-by-design.
- Backend gates: ruff clean, format clean, mypy strict clean (82 files),
  pytest **123 passed**.
- Frontend gates: lint 0 warnings, typecheck clean, build OK.
- CI runs backend + frontend + Playwright; GPU training still never in CI.
- Tasks 13 (P), 14 (Q), 15 (R) recorded in TASKS.md (accurate 123-test count).

**Open questions (now):**

1. Only the four-clip narrative copy remains — needs a vision-capable reviewer or
   the author's confirmation before finalising (was already pending in Phase O).
2. Deployment (Vercel etc.) is intentionally out of scope for the capstone build.
3. The baseline stays demonstration-grade (low_confidence usually true) — any
   believability improvement is a research-track decision, decoupled from the
   product build.
