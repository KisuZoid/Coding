# archive/ — Retired AutoInspect-X artifacts

Historical, superseded, or provisional material is moved here so the live
project folders (`docs/`, `ml/`, `apps/`, root `*.md`) speak only about the
implemented, photo-first system. Nothing in `archive/` is live or load-bearing:
no code under `archive/` is imported, no `docs/` link should resolve here, and
no experiment here is a current comparison.

Archival is provenance, never deletion. Every move records the original path.

---

## 1. Moved material (original path → archive path)

| Original path | Archive path | Why it is archived |
|---|---|---|
| `CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md` | `archive/docs/CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md` | Original 2026-09-07 bootstrap brief; historical input to Task 1. |
| `docs/architecture/implementation-gap-report.md` | `archive/docs/implementation-gap-report.md` | Phase A repository audit (2026-09-08); superseded by `docs/architecture/overview.md`. |
| `docs/research/cost-multimodal-data-readiness.md` | `archive/docs/cost-multimodal-data-readiness.md` | Cost/multimodal framing removed from scope by ADR 0011; document is historical evidence for why. |
| `docs/research/research-scope.md` | `archive/docs/research-scope.md` | Provisional scope written before the research report existed; redundant with the report's §1–§4. |
| `docs/research/experiment-principles.md` | `archive/docs/experiment-principles.md` | Superseded by `AGENTS.md` §3/§4 + `docs/ml/ml-engineering-guidelines.md`. |
| `docs/research/segmentation-experiment-config.md` | `archive/docs/segmentation-experiment-config.md` | Phase 6 "locked config" for the first 5-epoch baseline; superseded by `docs/architecture/cnn-transformer-segmentation.md` (spec v3, §10) and the 15-epoch pilots' recorded configs. |
| `ml/training/train_smoke.py` | `archive/legacy-code/ml/training/train_smoke.py` | Phase 3 tiny training smoke; superseded by `ml/training/smoke_test.py` (data/inference check) + `ml/training/train.py` (real runs). Only ADR 0006 referenced it. |
| 10 historical experiment dirs | `archive/experiments/{cardd_baseline_ce, cardd_baseline_full, cardd_hybrid_ce, phase3_smoke, phase4_baseline, phase8_ce_probe, phase8_fixcheck, phase8_midsize_fixcheck, smoke_baseline_512, smoke_hybrid_512}` | Superseded by `ml/experiments/pilot15_{baseline,hybrid}` (the 15-epoch pilots). `run_record.json`, evaluation summaries and the two `cardd_hybrid_ce_*.log` files stay as provenance for the ADR 0007/0008 loss corrections and the legacy hybrid curve. The `.pt` weights move with the dirs (git-ignored, recoverable). |
| pilot `periodic_epoch_*.pt` (4×372 MB + 4×423 MB) | `storage/models/pilot15_{baseline,hybrid}/` (git-ignored external model storage) | Large, non-current experiment weights; the **current** `best_checkpoint.pt` for each pilot stays in `ml/experiments/` where the app loads it. |

## 2. Docs swept in place (decision, not moved)

- `AUTOinspectX_PROJECT_STATE.md` — **kept at repo root.** It is the canonical
  32-section project-state snapshot, actively referenced by `README.md`, ADR
  0011, and the research report. It is not merged into `MEMORY.md`: `MEMORY.md`
  stays a compact running log, and folding a 800-line state snapshot into it
  would make the log unreadable. They are complementary, not duplicates.
- `docs/research/problem-definition.md` and
  `docs/research/implementation-alignment.md` — **kept** (2026-09-21 reconciled
  deliverables, still the live problem statement and repo↔research mapping).
- `docs/decisions/0001–0011` — **kept in full** (ADRs are immutable decision
  records; ADR 0007/0008 pairs and lifecycle provenance matter).
- `AutoInspect-X_Research_Report_Corrected.md` — **kept at repo root** (research
  source of truth per `AGENTS.md` §2; `docs/` must not contradict it).

## 3. Classification summary (2026-09-22 audit)

| Category | Items | Disposition |
|---|---|---|
| **KEEP (live)** | `apps/`, `ml/` (models/training/inference/evaluation/analysis), `tests/`, `.github/`, `docs/architecture` (overview + cnn-transformer spec v3), `docs/decisions/`, `docs/research` (problem-definition, implementation-alignment), root docs (README, RUNBOOK, CLAUDE, AGENTS, init, LOGIC, MEMORY, TASKS, SECURITY, CONTRIBUTING, project state, research report), `public/` (913 cinematic frames), `storage/` (runtime), `conftest.py`, `pyproject.toml`, `.env.example`, `.gitignore` | Untouched except per-deliverable doc edits. |
| **ARCHIVE (moved here)** | `archive/docs/` — 6 docs; `archive/legacy-code/` — `train_smoke.py`; `archive/experiments/` — 10 historical experiment dirs (git-ignored) | `git mv` for tracked files; plain `mv` for git-ignored experiment dirs (see §1). |
| **GENERATED — removed locally** | `apps/web/.next/` (132 MB), `apps/web/test-results/`, `apps/web/playwright-report/`, all `__pycache__/` + `*.pyc`, `.pytest_cache/`, `.ruff_cache/`, `.mypy_cache/`, `*.tsbuildinfo`, `ml/datasets/reports/vis_samples/` | All git-ignored build/test/debug output; deleted from disk (regenerate with the gates). Not a repo change. |
| **GENERATED — retained** | `apps/web/node_modules/` (618 MB), `uv.lock`, `package-lock.json` | Regenerable; retained locally for builds. Lockfiles are committed. |
| **EXTERNAL STORAGE ONLY (git-ignored, never committed)** | `datasets/CarDD_COCO` (working dataset), `datasets/CarDD_SOD` (unused by any code path), `storage/models/pilot15_{baseline,hybrid}/periodic_epoch_*.pt`, pilot `best_checkpoint.pt` (in `ml/experiments/`, loaded by the app), `data/training/`, `.env` | CarDD-COCO is the working dataset. CarDD_SOD is unused — recorded here as external-only; decide its fate on the research machine, never via repo. Pilot `best_checkpoint.pt` stays in `ml/experiments/` because the API default loads it; periodic checkpoints live under `storage/models/`. |
| **CURRENT experiments (kept)** | `ml/experiments/pilot15_baseline/`, `ml/experiments/pilot15_hybrid/`, `ml/experiments/registry.json` | The 15-epoch pilots and the experiment registry (status, metrics, git revisions). Only `best_checkpoint.pt` + `run_record.json` remain per pilot dir. |

**Kept in the live tree (legacy but still imported):** `ml/models/cardd_hybrid.py`
and `ml/models/cardd_unet.py`. The inference engine's legacy `cardd_*` dispatch,
`ml/training/train.py`'s legacy arm, and `tests/test_cardd_hybrid.py` still
import them — they are load-bearing, not dead code, so archiving them would break
loading of the archived `cardd_*` checkpoints.

## 4. Ground rules for future sessions

- Anything moved into `archive/` is final: do not re-wire imports or docs to it.
- Do not add speculative `archive/` categories; move a file only when a live
  document supersedes it.
- Never delete anything under `archive/` without a new audit entry.
- Git-ignored weights/datasets are the team's external responsibility; the repo
  records only experiment IDs and metrics.