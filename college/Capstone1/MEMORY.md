# MEMORY.md — AutoInspect-X

Compact record of the current repository facts. Historical reasoning and old
experiment results remain in the ADRs, archived documents, and Git history.

> **Integrity anchor:** four controlled runs use the two available seeds
> `42` and `1337`; this is not a completed three-seed study. The
> `final100_hybrid_seed42` record is exploratory and
> `PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS`. No architecture superiority,
> statistical significance, or completed final-100 claim is supported.

## Current state — 2026-09-25

- Product scope is photo-first vehicle damage segmentation with an honesty
  contract. Repair cost, repair action, hidden damage, physical cm² area, and
  the questionnaire flow are out of scope under ADR 0011.
- The backend exposes an explicit five-model catalogue through `GET /models`.
  The frontend loads the catalogue and persists the selected model in the
  inspection session.
- `final60_hybrid_seed42` is the current default. `MODEL_PATH` and
  `MODEL_VERSION` remain legacy/custom compatibility settings, not the normal
  catalogue path.
- Session model selection is accepted before analysis and locked once
  inspection evidence exists. Unknown IDs return `MODEL_NOT_FOUND`; locked
  changes return `MODEL_SELECTION_LOCKED`.
- `ml/inference/engine.py` dispatches from checkpoint `model_arch` metadata and
  reports the selected model ID. The API does not import training code.

## Active model evidence

| Model ID | Architecture | Seed | Status | Best val foreground mIoU | Best epoch |
|---|---|---:|---|---:|---:|
| `final60_baseline_seed42` | ResNet34UNet | 42 | CONTROLLED | 0.6676585078 | 44 |
| `final60_baseline_seed1337` | ResNet34UNet | 1337 | CONTROLLED | 0.6681153178 | 50 |
| `final60_hybrid_seed42` | HybridSegmentation | 42 | CONTROLLED | 0.6701672077 | 49 |
| `final60_hybrid_seed1337` | HybridSegmentation | 1337 | CONTROLLED | 0.6731674075 | 47 |
| `final100_hybrid_seed42` | HybridSegmentation | 42 | EXPLORATORY | 0.6715497971 | 58 |

The final-100 record contains a best checkpoint and periodic evidence observed
at epochs 54–84, but no complete history or termination reason. It is not a
matched comparison. The hybrid seed-1337 run retains its resume metadata.

## Evidence and storage

- CarDD-COCO official split counts measured locally: train `2,816`, validation
  `810`, test `374`.
- CarDD segmentation labels are REAL GROUND TRUTH for the dataset; model
  outputs are MODEL PREDICTION; image-relative area ratios are DERIVED
  FEATURES.
- Active experiment directories retain `best_checkpoint.pt` and
  `run_record.json` only. `ml/experiments/` and `archive/experiments/` are
  git-ignored local storage.
- Pilot and legacy experiment provenance is under `archive/experiments/`.
  Generated weights, datasets, `.env`, and storage content must never be
  committed.
- The local `.env` was changed to use `MODEL_ID=final60_hybrid_seed42`; it also
  contains a secret credential and remains ignored.
- The live cinematic scene 4 retains 84 OCR-audited frames. Frames 085–240,
  which contained obsolete repair-action and repair-cost copy, are archived at
  `archive/cinematic/legacy-public-4/` and are not served.

## Product contract

1. Create a session and optionally select a catalogue model.
2. Upload one photo.
3. Run the capture-quality gate.
4. On rejection, return `QUALITY_FAILED` with retake guidance and no mask.
5. On acceptance, run the selected architecture and return predicted classes,
   normalized area ratios, confidence, honesty flags, model metadata, and an
   overlay.
6. Optionally store consent and continue grounded chat.

The assistant is LangChain ChatGroq when configured, otherwise the
`StubAssistant`. It is not the segmentation model and cannot create ground
truth or cost/repair claims.

## Current validation

Verified on 2026-09-25 with the `ai` conda environment (Python 3.12.13) and
Node 22, on commit `931822c` plus the current uncommitted working tree:

- Backend: `ruff check` and `ruff format --check` clean over
  `apps/ ml/ tests/ conftest.py`; `mypy` strict clean over `apps/ ml/ tests/`
  (89 files); full `pytest tests/` green — 147 passed, 10 warnings.
- Frontend: `npm run lint -- --max-warnings=0`, `npm run typecheck`, and
  `npm run build` all pass.
- Browser E2E: full Playwright run green — 34 passed, 8 skipped. The skips are
  the intentional desktop-only engine journeys repeated on tablet and mobile;
  the desktop journeys ran against the real
  `final60_hybrid_seed42` checkpoint.
- Documentation: `docs/research/literature_review.tex` compiles with Tectonic to
  a 10-page PDF with 30 references and no unresolved citations. Remaining
  output is Underfull-box typography plus Tectonic's known `.bbl`-change rerun
  loop, neither of which affects content.
- Deliverables: `Capstone report/` regenerates to 82 A4 pages with a converged
  TOC (49 rows), LOF (22 rows) and 15 code listings whose longest source lines
  survive rendering; `AutoInspect-X_Capstone.pptx` has 17 slides with no
  remaining pilot-era metric, seed-count or cost claim.
- The `public/4/` textual OCR audit is complete; direct visual interpretation
  was unavailable in the current tool environment.

Two environment-driven defects were found and fixed while running the matrix:
the repository `.env` (git-ignored) leaked `MODEL_ID` into API tests that
exercise the legacy configured-checkpoint route, and the header connectivity
chip is intentionally hidden below the `sm` breakpoint, which the shell and
responsive specs asserted as visible on every viewport.

## Open items

- Lock the RQ2 confidence-honesty operational definition.
- Decide whether a third controlled seed and a reproducible `research_summary.md`
  are required before making a comparative claim.
- Recover final-100 history only from an original log or rerun; do not invent
  missing epochs.
- `research_summary.md` and the report/presentation regeneration tooling are not
  in the repository: the report and deck are produced by an out-of-tree
  generator kept outside the worktree. Decide whether that generator should be
  committed so the deliverables are reproducible from the repository alone.

## Invariants

- Keep REAL GROUND TRUTH, WEAK LABEL, SYNTHETIC LABEL, DERIVED FEATURE,
  MODEL PREDICTION, and ASSUMPTION distinct.
- Do not add cost-like output or physical-area claims without a new ADR.
- Do not claim superiority from the current two-seed values.
- Do not commit secrets, checkpoints, datasets, or ignored experiment files.
- Archive superseded material with provenance; do not silently delete it.
