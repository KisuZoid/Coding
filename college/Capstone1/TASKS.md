# TASKS.md — AutoInspect-X

Concise task tracker. Current phase and next recommended task are at the top.
This file replaces the append-only 1,900-line task diary (retirement recorded
below); keep it brief and current.

> **Research-integrity note:** the 15-epoch pilot results (`pilot15_baseline`
> foreground mIoU 0.6127, `pilot15_hybrid` 0.5963) are **preliminary validation
> observations and are not the final research conclusion.** No architecture is
> claimed superior until the locked 60-epoch / 3-seed comparison completes.

---

## Current phase

**Phase-I report delivered (Task E) and final revision applied (Task E2).**
Report + PDF delivered under `Capstone report/` and QC-verified (2026-09-23);
2026-09-24 revision pass (see Completed) delivered the 78 pp. report with
manifest-pinned tech stack, expanded Chapter 4, and complete verbatim
Appendix B listings. **Next recommended task:**
in-person dry-run of the viva (defend the pilot numbers as preliminary, the
ADR-0011 scope boundary, and the consent flow), or the locked 60-epoch /
3-seed comparison that upgrades the pilot observations into a conclusion.

## Completed

- **Research + architecture (Task A-era).** Photo-first scope (ADR 0011),
  CarddHybrid design (ADR 0010), arch spec v3, and the research report (source
  of truth) — retained and authoritative.
- **15-epoch pilots (Task B).** `pilot15_hybrid` (ACTIVE) and `pilot15_baseline`
  (retained arm) trained on full official CarDD splits, seed 0, recorded in
  `ml/experiments/registry.json` (git `fb2fb59`).
- **Model integration (Task C1).** Engine `model_arch` dispatch for
  `resnet34_unet`/`baseline` and `hybrid`/`hybrid_segmentation` (+ legacy
  `cardd_*`); container default → `pilot15_hybrid`; registry-backed provenance
  notes (foreground mIoU); `.env.example`, RUNBOOK, e2e specs, and integration
  tests updated.
- **Backend gates (Task C2).** `ruff check` + `ruff format` clean, `mypy` clean
  (86 files), `pytest` 135 passed.
- **Directory cleanup (Task C3).** 10 historical experiments → `archive/experiments/`
  (git-ignored, with logs); periodic checkpoints → `storage/models/pilot15_*`;
  `train_smoke.py` → `archive/legacy-code/ml/training/`; `.gitignore` +
  `archive/README.md` updated (legacy model files stay live by design).
- **Frontend gates (Task C4).** eslint (`--max-warnings=0`), `tsc --noEmit`,
  `next build` all pass.
- **Docs rewrite (Task C5).** README.md, TASKS.md, MEMORY.md re-written concise;
  `docs/research/problem-definition.md` + `implementation-alignment.md`,
  `docs/architecture/overview.md`, research report §10 addendum updated; 6
  historical docs archived to `archive/docs/` with live-doc pointers fixed.
- **Literature review (Task C6).** `docs/research/literature_review.tex` +
  `references.bib` (30 verified references), compiled with tectonic
  (IEEEtran.cls + IEEEtran.bst local) → `literature_review.pdf` **10 pages, 0
  errors**; pilot observations clearly separated from literature findings.
- **Literature review updates (Task C8).** Author block updated to **Capstone
  Group 160 — School of Computing Science Engineering and AI, VIT Bhopal
  University, Sehore**; rebuilt PDF with tectonic. Fixed a latent dangling
  reference: added `\label{sec:hybrid}` so `\ref{sec:hybrid}` resolves instead
  of rendering `??` (single ref, both occurrences verified clean in the output).
- **Model-integration fix (Task D2).** Root cause of the demo "model
  unavailable" error: the local `.env` still pinned `MODEL_PATH` /
  `MODEL_VERSION` to the archived `cardd_hybrid_ce` run; the router hid the
  real reason. Fixed `.env` → `pilot15_hybrid`; `container.py` now resolves
  the checkpoint CWD-/repo-root-independently and logs the resolved path +
  registry metadata; `engine.from_checkpoint` accepts a `model` alias and
  logs arch/base/epoch/device/params + missing/unexpected keys; the router
  distinguishes `ModelLoadError`/`ModelVersionError` from generic build
  failures; a startup lifespan check logs a clear error when the checkpoint
  is absent. Verified: isolated checkpoint load (0 missing/unexpected keys),
  API POST with a real CarDD photo (dent/scratch/glass shatter/lamp broken,
  conf 0.858, overlay), and the real browser UI produced the model overlay.
   New `tests/test_model_integration.py` (9 tests, 144 total green).
- **Phase-I report (Task E — 2026-09-23).** DSN4091 Phase-I report generated
  from the sample-report structure and real project evidence: `Capstone
  report/DSN4091 Capstone Project Phase-I Report - Kislay Anand.docx` +
  `.pdf` (47 pp. A4: cover, bonafide, acknowledgement, abstract, LOF, TOC,
  Chapters 1–7, Appendices A/B, references). 21 figures (project screenshots +
  generated workflow/architecture diagrams), 8 code listings, pilot numbers
  taken verbatim from `run_record.json`; no secrets, no cost/repair claims
  (ADR 0011), no Underbelly content. Verified: every TOC/LOF page number
  matches the rendered page, each chapter starts a fresh page, front-matter
  footers roman / body decimal from 1, no blank/missing-image pages, code
lines ≤78 chars (no wrap). Build scripts live in `/tmp/opencode/`
   (`build_report.py`, `parse_pdf.py`, `verify_pdf.py`) — not part of the repo.
- **Final report revision (Task E2 — 2026-09-24).** Surgical python-docx pass
   over the delivered DOCX (`/tmp/opencode/revise_report.py`, out-of-repo):
   front matter (cover/bonafide/ack/abstract/LOF/TOC) preserved byte-identical
   intent; Chapter 3 tech-stack table rebuilt as precise 5-column
   Layer | Technology | Version | Purpose | Evidence with versions read only
   from repo manifests (requirements-ci.txt pins, package.json+lock,
   pyproject.toml, uv.lock); Chapter 4 expanded to eight sections (4.4 Data
   Flow, 4.5 ML/CV Methodology, 4.7 Novelty inserted; 4.6 UI renamed) incl. the
   real folder tree; Chapter 5 pseudo-code replaced with Appendix B pointers;
   Appendix B = 14 complete verbatim listings (source path + true line range
   per caption, mono size auto-scaled so no line wraps). Result: **78 pp. A4**,
   22 LOF figures, TOC/LOF page numbers converged via two-pass LibreOffice
   render (body offset = physical page 9). Pre-revision backup removed after
   validation. OLD 47 pp. report superseded; the pre-revision docx is recoverable
   only from git history if ever needed.


## In progress

- **Scoped git commits (Task C7).** Multiple reviewable commits under
  `college/Capstone1/...` (never `git add .`).
- **Final verification report (Task D).** Sections A–I with exact paths/counts.

## Next recommended task

1. Commit the cleanup/integration, doc/lit-review, and model-integration-fix
   changes (Task C7).
2. **60-epoch / 3-seed comparison** of `ResNet34UNet` vs `HybridSegmentation`
   on the locked schedule, then lock the RQ2 confidence-honesty operational
   definition and write `research_summary.md`. **This is the blocker for any
   architecture claim.**

## Research experiments (registry)

| Experiment | Model | Status | Foreground mIoU (val, @ep14) | Notes |
|---|---|---|---|---|
| `pilot15_hybrid-20260922-115320` | `hybrid` | ACTIVE | 0.5963 | demo default; ~27.9M params; seed 0 |
| `pilot15_baseline-20260922-110722` | `resnet34_unet` | SUPERSEDED | 0.6127 | retained baseline arm; ~24.6M params; seed 0 |
| `cardd_hybrid_ce-20260921-162128` | `cardd_hybrid` | SUPERSEDED | val mIoU 0.0504 / test 0.0586 | demo-era, archived |
| `cardd_baseline_ce-*` | `cardd_unet` | SUPERSEDED | 0.0475 | 5-epoch underfit, archived |
| `smoke_*`, `phase*` runs | — | SUPERSEDED | — | historical, `archive/experiments/` |

All rows: MEASURED scores from `run_record.json` / `registry.json` (git-ignored).

## Product integration

- **API:** FastAPI; `container.py` resolves checkpoint via `MODEL_PATH` /
  `MODEL_VERSION` and builds provenance notes from the registry; engine emits
  MODEL PREDICTION payload (mask, area ratios, confidence, `low_confidence`).
- **Frontend:** Next.js — photo → overlay → per-class ratios → honesty flags →
  grounded chat (LangChain ChatGroq or offline stub). e2e journeys cover upload,
  analysis, and continued chat.
- **Honesty contract:** enforced by engineered labels + tests
  (`tests/`, engine flags). No cost/severity/physical-area outputs anywhere.

## Documentation (current)

- `README.md` — overview, workflow, architecture, classes, pilots, storage &
  archive policy, limitations (re-written Task C5).
- `RUNBOOK.md` — run commands + troubleshooting (demo default pilot15_hybrid).
- `MEMORY.md` — current state only (re-written Task C5).
- `docs/architecture/cnn-transformer-segmentation.md` — spec v3 (authoritative
  architecture doc).
- `AutoInspect-X_Research_Report_Corrected.md` — research source of truth
  (incl. §10 addendum on the pilots).
- `docs/research/literature_review.tex` + `.pdf` — 10 pp. IEEE review.

## Known issues

- PhD-claimed model quality blocked on the 60-epoch / 3-seed run — the pilots
  are an intermediate check only.
- `cardd_*` legacy checkpoints load with a base-check guard (research checkpoints
  store `base=0`); engine tolerates both, but mixing is intentionally rejected.
  **2026-09-22 resolved:** `.env` previously pointed at the archived
  `cardd_hybrid_ce` checkpoint, causing the demo "model unavailable" error.
  Now points at `pilot15_hybrid`; path resolution is CWD-independent and the
  missing-checkpoint reason is logged (see Task D2).
- Registry entries carry `data_root=/content/data/CarDD_COCO` (training-env
  path); data location is not part of inference resolution.

## Deferred

- MC Dropout / Deep Ensembles for RQ2 (ADR required before use).
- Focal loss as an alternative objective (decision to be recorded if adopted).
- VehiDE cross-dataset check; CrashCar101 pre-training/augmentation
  (licence-review first).
- Expanding the hybrid to heavier attention stages (VRAM- and schedule-bound).
- Multi-view fusion (MVA-CDD direction) — out of single-photo scope.

---

## Retirement record

The previous numbered log (1,900 lines, Tasks 1–N from 2026-09-07 onward) was
replaced on **2026-09-22** by this concise tracker. It was a dated diary whose
content is now stale (calls CarddHybrid/`cardd_hybrid_ce` the current model and
the old experiment layout). Nothing was deleted from the repo; the historical
record lives in `AutoInspect-X_Research_Report_Corrected.md`, `ADRs`,
`AUTOinspectX_PROJECT_STATE.md`, and `git log`, and per-task provenance remains
in the re-written docs above. The 15-epoch pilot numbers above are preliminary;
see the integrity note at the top.