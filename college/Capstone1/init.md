# init.md — AutoInspect-X Session Bootstrap Protocol

Read this file at the start of every coding session in this repository. It
prevents stale pilot-era assumptions from being reintroduced.

## 0. Required session start

1. Read `init.md`, `CLAUDE.md`, `AGENTS.md`, `MEMORY.md`, `TASKS.md`, and
   `LOGIC.md`.
2. Read `AutoInspect-X_Research_Report_Corrected.md` before research-facing
   changes.
3. Read ADR 0010 (CarddHybrid), ADR 0011 (photo-first scope), ADR 0012
   (five-model catalogue), and ADR 0013 (current Dice + Focal objective).
4. Inspect `git status` and recent history.
5. Inspect the relevant source and test files before editing.

Use the `ai` conda environment for Python/ML commands. Do not install CUDA or
PyTorch into the base environment.

## 1. Project identity

- **Name:** AutoInspect-X
- **Path:** `/home/kisuzoid/Kislay/Repo/Coding/college/Capstone1`
- **Type:** Academic photo-first vehicle damage segmentation capstone.
- **Research title:** *AutoInspect-X: Photo-First Vehicle Damage Segmentation
  with Evidence-Labelled Confidence*.

Current research question: how does `HybridSegmentation` compare with
`ResNet34UNet` for damage-segmentation quality and confidence honesty on
CarDD? The current catalogue has two controlled seeds; it is not a completed
three-seed comparison.

## 2. Research source of truth

The corrected report exists at:

```text
AutoInspect-X_Research_Report_Corrected.md
```

It is authoritative for terminology, literature, datasets, equations,
questions, hypotheses, metrics, and limitations. Preserve the distinction
between source statements and repository inferences. Never fabricate results,
datasets, citations, market figures, or ground truth. Record material changes
as ADRs.

The current report includes a dated 2026-09-25 addendum for the five-model
catalogue. The final-100 record is explicitly partial and must not be described
as a completed run.

## 3. Product and evidence boundary

The implemented flow is:

```text
photo → capture-quality gate → selected segmentation engine
      → predicted mask + normalized ratios + confidence + overlay
      → grounded explanation → optional consent → chat
```

Repair cost, repair action, hidden-damage prediction, physical cm² area, and
questionnaire gating are out of scope under ADR 0011. CarDD masks are REAL
GROUND TRUTH for dataset evaluation; model outputs are MODEL PREDICTION;
image-relative areas are DERIVED FEATURES.

## 4. Current model rule

`apps/api/model_catalog.py` is the explicit five-entry allowlist. The default
is `final60_hybrid_seed42`. The four `final60_*` entries are CONTROLLED;
`final100_hybrid_seed42` is EXPLORATORY and has a
`PARTIAL_RECONSTRUCTED_FROM_CHECKPOINTS` record. Do not use pilot checkpoints
as defaults. `MODEL_PATH` and `MODEL_VERSION` are legacy/custom compatibility
settings only.

## 5. Supabase and external services

No Supabase project belongs to this repository. The connected project
`nykalxhmbupsarhicrtd` belongs to another product and must never be read from
or written to.

Never print, copy, commit, or include the contents of `.env` in output. Read
only the names of required variables from `.env.example`. If a project ref is
needed, inspect the local configuration without exposing credentials and
confirm it against the authoritative account before any database action.

No n8n integration, form automation, scheduled job, or webhook exists. Do not
describe future automation contracts as working software. Workflow logic belongs
in `LOGIC.md`; credentials belong in environment variables only.

## 6. Repository map

```text
apps/api/          FastAPI service, model catalogue, session/state, storage
apps/web/          Next.js photo-first demo
ml/models/         ResNet34UNet, HybridSegmentation, legacy Cardd models
ml/training/       Research-only training pipeline
ml/inference/      Production architecture-aware engine
ml/evaluation/     Metrics and full-split evaluation
ml/experiments/    Git-ignored active records/checkpoints and registry
archive/           Superseded docs, code, and experiment provenance
docs/decisions/    ADRs 0001–0013
docs/research/     Literature review and implementation reconciliation
tests/             API, engine, catalogue, and integration tests
```

## 7. Hard rules

1. Inspect before coding and reuse existing utilities.
2. Make the smallest coherent change; no speculative abstractions.
3. Keep REAL GROUND TRUTH, WEAK LABEL, SYNTHETIC LABEL, DERIVED FEATURE,
   MODEL PREDICTION, and ASSUMPTION distinct.
4. Never commit secrets, datasets, checkpoints, `.env`, `storage/`, or ignored
   experiment artifacts.
5. Never introduce cost/repair output or physical-area claims without a new ADR.
6. Keep model selection allowlisted, checkpoint architecture-tagged, and locked
   after analysis.
7. Run the documented lint, type-check, and relevant tests after changes.
8. Update `TASKS.md` and `MEMORY.md` before finishing a session.
9. Do not commit unless the user explicitly requests it.
