# AutoInspect-X — Big Pickle / OpenCode Development Instructions

## Purpose

This is the **canonical engineering and implementation brief** for building AutoInspect-X with OpenCode / Big Pickle.

The repository also contains the research document:

```text
AutoInspect-X_Research_Report_Corrected.md
```

That research file must be read before making research-facing decisions. This document translates the research direction into implementation rules.

The goal is a **real, modular, research-grade vehicle-damage inspection system**, not a chatbot demo and not a collection of disconnected AI features.

---

# 0. Big Pickle / OpenCode Operating Rules

Big Pickle is being used as the primary coding agent through OpenCode. OpenCode supports project-level agent prompts and model selection, so keep this file and `AGENTS.md` as the durable project rules rather than relying on conversation memory. The currently available OpenCode Zen catalog includes Big Pickle; model availability and capabilities can change, so do not hard-code assumptions about the model beyond what the current environment reports.

## Use Big Pickle for

- repository exploration
- implementation
- refactoring requested by the team
- test generation
- documentation
- debugging
- local tooling setup
- frontend/backend integration
- controlled ML experiment orchestration

## Do NOT rely on Big Pickle blindly for

- final research novelty claims
- unverified literature facts
- medical/safety claims
- fabricated benchmark results
- deciding that synthetic labels are real ground truth
- destructive Git operations
- large architecture changes without checking the existing docs

## Big Pickle execution discipline

For every non-trivial task:

1. Read the relevant repository files first.
2. Read `AGENTS.md` and this file.
3. Read the relevant research documentation before research-facing code.
4. Search for an existing implementation before creating a new one.
5. State a short implementation plan before large edits.
6. Make small, coherent changes.
7. Run targeted validation after each meaningful change.
8. Review the diff before finishing.
9. Remove temporary/dead code created during the task.
10. Summarize exactly what changed and what remains.

## Context discipline

Use the large context window as an advantage, but do not assume that loading the entire repository is always useful. For a task, read:

```text
project rules
→ relevant architecture docs
→ relevant source files
→ relevant tests
→ relevant research docs
```

Avoid flooding the context with datasets, generated artifacts, binary files, logs, videos, checkpoints, or unrelated source code.

## Git safety

Never run destructive Git commands unless explicitly requested by the user.

Do NOT run without explicit approval:

```text
git reset --hard
git clean -fd
git checkout -- <unrelated files>
git restore --staged/--worktree <unrelated files>
git push --force
```

Never discard unrelated user work.

Before major edits:

```bash
git status --short
```

After major edits:

```bash
git diff --stat
git diff
```

---

# 1. Project Identity

**Project:** AutoInspect-X

**Research title:**

> AutoInspect-X: Multimodal Deep Learning for Vehicle Damage Segmentation and Uncertainty-Aware Repair Cost Estimation

**Core research question:**

> Can segmentation-derived damage representations, combined with vehicle metadata, improve repair-cost estimation and repair-action prediction compared with vision-only and simple-fusion baselines?

---

# 2. FINAL LOCKED RESEARCH FLOW

This is the flow that all implementation must align with:

```text
                         USER
                           │
                           ▼
                 ┌─────────────────┐
                 │ Cinematic Intro │
                 └────────┬────────┘
                          │
                          ▼
                  Conversation / Agent
                          │
            ┌─────────────┼─────────────┐
            ▼             ▼             ▼
        Incident       Vehicle       Repair
        Context        Context       Location
            └─────────────┼─────────────┘
                          ▼
                   Photo Guidance
                          │
                          ▼
                   Photo Upload
                          │
                          ▼
                 Image Quality Check
                     │          │
                  FAIL          PASS
                    │             │
                    ▼             ▼
              New Photo       Segmentation
                                  │
                                  ▼
                           Damage Features
                                  │
                    ┌─────────────┴─────────────┐
                    │                           │
               Vision Data                Vehicle Metadata
                    │                           │
                    └─────────────┬─────────────┘
                                  ▼
                         Multimodal Fusion
                                  │
                       ┌──────────┴──────────┐
                       ▼                     ▼
                 Repair Action          Cost Model
                 Repair/Replace       P10 / P50 / P90
                       │                     │
                       └──────────┬──────────┘
                                  ▼
                           Result Validation
                                  │
                                  ▼
                         LangGraph + Groq
                                  │
                                  ▼
                           Explanation
                                  │
                                  ▼
                            Next Action
```

### Architectural separation

```text
LangGraph + Groq
= conversation + structured information acquisition + orchestration + explanation

Segmentation model
= visible-damage evidence

Feature/fusion model
= research intelligence

Cost model
= structured economic estimation
```

The conversational model is NOT the damage-segmentation model.

The segmentation model is NOT the cost model.

Do not collapse the whole system into one giant model.

---

# 3. RESEARCH BOUNDARIES — NON-NEGOTIABLE

## Core research contribution

The main research comparison is:

```text
B1 — Vision-only
B2 — Vision + metadata with simple fusion
P  — Vision + metadata with advanced multimodal fusion
```

The core downstream tasks are:

1. damage representation from segmentation;
2. repair/replacement action prediction;
3. uncertainty-aware repair-cost estimation.

## Severity

Severity is an **intermediate/derived task or feature**, not the sole research contribution.

Do NOT let the project regress into:

```text
YOLO → Minor / Moderate / Severe
```

as the whole research story.

## Hidden structural damage

Hidden-damage prediction is an **optional extension only**.

It is permitted only if reliable real-world ground-truth labels become available, such as verified teardown/repair records.

Until then:

- do not train a fake hidden-damage model;
- do not report synthetic hidden-damage labels as ground truth;
- do not claim to diagnose internal structural damage.

## Cost estimation

Cost estimation must remain **research-disabled for real accuracy claims** until a validated observed-cost dataset exists.

Synthetic/rule-generated prices may be used for:

- UI development;
- workflow testing;
- architecture smoke tests.

They must NOT be used to claim real-world cost-prediction performance.

If valid cost labels are unavailable, the system must say:

```text
Estimate unavailable / insufficient validated data
```

rather than fabricate a number.

---

# 4. RESEARCH-MD-FIRST RULE

Before changing research-facing architecture or experiments, read:

```text
AutoInspect-X_Research_Report_Corrected.md
```

Use it as the baseline for:

- research terminology;
- literature;
- datasets;
- research questions;
- hypotheses;
- metrics;
- limitations.

If the implementation document and research MD disagree:

1. identify the conflict;
2. do not silently overwrite either document;
3. make the smallest defensible correction;
4. record a material architecture/research decision in `docs/decisions/`.

Never invent:

- citations;
- dataset facts;
- accuracy numbers;
- cost labels;
- hidden-damage labels;
- market statistics;
- experimental results.

---

# 5. PRODUCT VISION

AutoInspect-X should let a user naturally say:

> “I damaged my car.”

The system should:

1. understand what happened;
2. collect useful incident context;
3. identify where the user believes the damage occurred;
4. collect vehicle information;
5. collect repair-market location;
6. guide the user to capture a useful photo;
7. validate the image;
8. analyze visible damage;
9. segment the damaged region;
10. identify damage type and affected part;
11. extract structured damage features;
12. combine visual and vehicle context;
13. predict repair/replacement action where the model is trained to do so;
14. estimate a cost interval where validated cost data allows;
15. explain the result clearly;
16. give the user a sensible next action.

The product is preliminary decision support.

It is NOT:

- a final professional quotation;
- a certified inspection;
- a hidden structural-damage diagnostic tool;
- a replacement for a qualified inspector.

---

# 6. HIGH-LEVEL APPLICATION ARCHITECTURE

```text
                    USER
                      │
                      ▼
              NEXT.JS / REACT
                      │
                      ▼
                   FASTAPI
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      LANGGRAPH      VISION      COST
       + GROQ        SERVICE     SERVICE
          │           │           │
          └───────────┼───────────┘
                      ▼
              STRUCTURED RESULT
                      │
                      ▼
                LANGGRAPH + GROQ
                      │
                      ▼
                 USER RESPONSE
```

LangGraph orchestrates the workflow but does not contain model-training logic.

---

# 7. REPOSITORY ARCHITECTURE

Prefer a modular monorepo/modular application.

```text
AutoInspect-X/
│
├── apps/
│   ├── web/                  # React/Next.js frontend
│   └── api/                  # FastAPI backend
│
├── ml/
│   ├── datasets/             # manifests/documentation; no raw large data in Git
│   ├── models/               # model definitions/registry
│   ├── training/             # training code
│   ├── inference/            # production inference
│   ├── evaluation/           # metrics and benchmarks
│   └── experiments/          # reproducible runs/configs
│
├── packages/
│   └── shared/               # only truly shared contracts/types
│
├── docs/
│   ├── architecture/
│   ├── research/
│   ├── ml/
│   └── decisions/
│
├── scripts/
├── tests/
│   ├── integration/
│   └── e2e/
│
├── .github/
│   └── workflows/
│
├── AGENTS.md
├── CLAUDE.md
├── README.md
├── CONTRIBUTING.md
├── SECURITY.md
├── .env.example
├── .gitignore
└── pyproject.toml / package.json
```

Do not create folders simply because they look impressive. Create them when the implementation needs them.

Dependency direction:

```text
web → API contracts
api → application/domain/infrastructure
ml training → datasets/models/evaluation
api → inference interface, not training internals
web ↛ ML internals
training ↛ frontend
```

Avoid circular imports.

---

# 8. FRONTEND

The frontend should look like a premium automotive-inspection product, not a generic admin dashboard.

Preferred technologies:

- Next.js
- React
- TypeScript
- Tailwind CSS
- GSAP/ScrollTrigger only where cinematic interaction actually benefits the story

Core future experience:

```text
Cinematic intro
→ inspection entry
→ conversational agent
→ context collection
→ photo guidance
→ upload/camera
→ processing
→ damage visualization
→ repair/cost result
→ explanation
→ report
```

The UI must clearly distinguish:

```text
WHAT YOU TOLD US
WHAT THE MODEL FOUND
WHAT WE ESTIMATE
WHAT WE RECOMMEND
```

Avoid:

- excessive gradients;
- glassmorphism everywhere;
- decorative cards with no purpose;
- huge component libraries for simple UI;
- random icon packages;
- excessive animations;
- fake loading states.

Every visible status must correspond to real application state.

---

# 9. BACKEND

Preferred stack:

- Python
- FastAPI
- Pydantic
- uv
- pytest
- Ruff
- mypy or justified equivalent

Conceptual layering:

```text
Router
 ↓
Application Service
 ↓
Domain
 ↓
Infrastructure
```

Route handlers should be thin.

Future logical domains:

```text
inspection
vehicle
conversation/agent
vision
cost
report
models
```

Do not create all of these as empty modules during bootstrap.

---

# 10. AGENT / LANGGRAPH

The conversational agent is a **structured data-acquisition and orchestration system**.

It must collect, where needed:

```text
INCIDENT
DAMAGE LOCATION
VEHICLE
REPAIR LOCATION
PHOTO
```

It must not repeatedly ask for information already known.

Suggested graph:

```text
START
 ↓
understand_request
 ↓
collect_incident
 ↓
collect_damage_location
 ↓
collect_vehicle_context
 ↓
collect_repair_location
 ↓
check_context_readiness
 ↓
guide_photo
 ↓
receive_photo
 ↓
validate_image
 ↓
if invalid → guide_photo
if valid   → damage_analysis
 ↓
feature_extraction
 ↓
vehicle_context_fusion
 ↓
repair_prediction
 ↓
cost_estimation
 ↓
result_validation
 ↓
final_reasoning
 ↓
final_response
 ↓
END
```

Loops are expected.

The agent should ask only questions that materially improve the inspection.

---

# 11. TYPED INSPECTION CONTEXT

Use a typed schema similar to:

```text
InspectionContext

incident
  description
  cause
  event_type

user_damage_report
  suspected_part
  side
  location
  visible_symptoms

vehicle
  make
  model
  year
  variant
  body_type

location
  country
  region
  city
  repair_market

media
  original_image
  processed_image
  image_quality
  image_angle
  image_count

vision_result
  damage_detected
  affected_part
  damage_types
  severity
  damage_area_ratio
  confidence
  mask_reference
  overlay_reference

fusion_result
  repair_action
  confidence

cost_result
  lower
  median
  upper
  currency
  confidence
  source_context

final_result
  recommendation
  explanation
  next_action

provenance
  user
  vision_model
  cost_estimator
  inferred
```

Do not allow untyped arbitrary model objects to leak across API boundaries.

---

# 12. IMAGE-QUALITY STAGE

Before expensive damage inference, validate the image.

Possible states:

```text
VALID
TOO_BLURRY
TOO_DARK
EXCESSIVE_GLARE
WRONG_ANGLE
DAMAGE_NOT_VISIBLE
INSUFFICIENT_CONTEXT
```

If invalid:

```text
image
 ↓
quality feedback
 ↓
agent guidance
 ↓
new photo
```

Do not pass clearly unusable images into the expensive ML stage and then pretend the prediction is trustworthy.

Preserve:

```text
original_image
processed_image
model_output
```

Never destroy the original.

---

# 13. USER REPORT VS MODEL FINDING

Keep these separate:

```text
user_reported_damage
model_detected_damage
```

Possible comparison states:

```text
AGREEMENT
PARTIAL_AGREEMENT
DISAGREEMENT
```

A material disagreement should be surfaced to the user.

The user report is not ground truth for the ML model.

The model prediction is not automatically ground truth either.

---

# 14. CORE ML TASK

The central ML task is:

> **visible vehicle-damage instance segmentation**

Expected output:

- damage instance;
- damage class;
- confidence;
- segmentation mask;
- location/part context where supported.

Do not reduce the scientific core to bounding boxes only.

---

# 15. MODEL STRATEGY

Do not train ten unrelated models.

Use controlled comparison.

## Primary practical baseline

Start with a lightweight segmentation model compatible with the available local GPU.

If the current environment supports it, begin with a small Ultralytics YOLO segmentation variant.

## Research comparison

A transformer segmentation model such as Mask2Former may be evaluated later on a cloud GPU if resources permit.

The model winner must be determined experimentally using:

- mask quality;
- per-class performance;
- small-damage recall;
- robustness;
- inference latency;
- VRAM usage;
- training cost.

Do not assume the larger model is better.

---

# 16. SEGMENTATION-DERIVED DAMAGE FEATURES

Use:

```text
damage type
affected part
mask
normalized area ratio
position
shape
confidence
number of damage instances
```

Research feature:

```text
normalized_damage_area
=
 damaged_mask_pixels / affected_part_pixels
```

Do NOT call this physical cm² unless valid camera calibration/geometry is available.

This rule directly protects the scientific validity of the project.

---

# 17. MULTIMODAL FUSION

## B2 — baseline

```text
vision features
+
vehicle metadata
↓
concatenation
↓
downstream model
```

## P — proposed

```text
vision representation
+
metadata representation
↓
cross-attention / advanced fusion
↓
repair head
+
quantile cost head
```

Do not claim cross-attention exists until it is implemented and experimentally evaluated.

---

# 18. REPAIR ACTION

Downstream classification:

```text
repair
replace
manual_inspection / uncertain
```

Inputs may include:

- damage representation;
- vehicle metadata;
- severity-related features;
- affected part;
- damage type.

Start with interpretable baselines where appropriate, such as gradient boosting or a small MLP.

Do not use a huge neural network without evidence that the extra complexity is useful.

---

# 19. COST ESTIMATION

Cost prediction is a separate service from conversation.

Conceptual inputs:

```text
vehicle make/model/year/variant
affected part
damage type
severity-related features
repair action
repair market/location
```

Outputs:

```text
P10 / lower
P50 / median
P90 / upper
currency
confidence
source context
```

Use quantile regression only when valid observed-cost data supports the experiment.

Never hard-code real-looking prices into production logic.

Never fabricate a price because the UI expects one.

---

# 20. DATASET POLICY

CarDD can be used for the visual damage problem.

A cost dataset is a separate requirement.

The system must distinguish:

```text
image dataset
vs.
cost dataset
```

CarDD answers:

> What does visible damage look like?

A repair-cost dataset answers:

> What did similar damage actually cost?

Do not merge these conceptually and pretend a derived price table is observed ground truth.

---

# 21. DATASET AUDIT FIRST

Before serious training, build the audit.

Audit:

- train/validation/test counts;
- instances;
- classes;
- image dimensions;
- aspect ratios;
- instances per image;
- mask areas;
- class imbalance;
- multiple-damage images;
- invalid annotations;
- duplicates/near-duplicates;
- metadata availability;
- severity availability where applicable.

Generate visualization samples:

```text
original image
+
ground-truth mask
+
class
```

Do not train the final model before the audit is understood.

---

# 22. LEAKAGE PREVENTION

Preserve valid official dataset splits.

Do not split instances from the same image into multiple evaluation sets.

Check for:

- exact duplicates;
- near duplicates;
- repeated photographs;
- annotation leakage.

Keep external smartphone validation images outside the training set until domain-shift evaluation is complete.

---

# 23. REAL-WORLD VALIDATION SET

After the benchmark baseline works, create an AutoInspect-X external validation set.

Target approximately:

```text
300–1,000 smartphone images
```

where realistically obtainable and ethically/licensing appropriate.

Include variation in:

- phone cameras;
- lighting;
- glare;
- angle;
- framing;
- body style;
- vehicle color;
- small vs large damage;
- multiple damages.

Use this initially for **external validation/domain shift**, not immediately for training.

---

# 24. EXPERIMENT PLAN

## B1 — Vision only

```text
image
→ damage representation
→ repair/cost task where labels exist
```

## B2 — Simple multimodal

```text
vision
+
vehicle metadata
↓
concatenation
↓
repair/cost
```

## P — Proposed

```text
vision
+
vehicle metadata
↓
advanced fusion / cross-attention
↓
repair action
+
quantile cost
```

All three must use the same evaluation protocol and data split.

---

# 25. REQUIRED EVALUATION

Segmentation:

- mAP;
- IoU;
- Dice/F1;
- precision/recall;
- per-class AP.

Repair action:

- Macro F1;
- confusion matrix;
- precision/recall where relevant.

Cost:

- MAE;
- MAPE only when zero/near-zero targets are handled appropriately;
- R² where meaningful;
- quantile interval coverage;
- interval width/sharpness.

Calibration:

- reliability diagrams;
- Expected Calibration Error where appropriate;
- calibration method comparisons where justified.

Robustness:

- small damage;
- viewpoint;
- lighting;
- compression;
- real smartphone images;
- model/vehicle variation.

---

# 26. ABLATION STUDY

At minimum:

```text
E1  Vision-only
E2  Vision + normalized damage features
E3  Vision + metadata, simple fusion
E4  Vision + metadata, cross-attention
E5  Full proposed model with quantile cost head
```

The exact experiments may be reduced if data availability makes a comparison invalid.

Do not run an ablation just to create a table; every experiment must answer a research question.

---

# 27. BEFORE VS AFTER — RESEARCH MEASUREMENT

Use measurable comparisons, not invented claims.

Potential process metrics:

```text
inspection time
manual intervention count
cost prediction error
interval coverage
segmentation quality
repair-action F1
user/model disagreement rate
image rejection rate
```

Useful equations include:

```text
MAE = (1/n) Σ |C_i - Ĉ_i|

MAPE = (100/n) Σ |(C_i - Ĉ_i) / C_i|

IoU = |S_pred ∩ S_gt| / |S_pred ∪ S_gt|

TimeReduction =
  ((T_manual - T_auto) / T_manual) × 100
```

Never invent the final values. Measure them.

---

# 28. REPRODUCIBLE EXPERIMENT TRACKING

Track:

- experiment ID;
- Git commit;
- dataset version;
- split;
- seed;
- model/version;
- input resolution;
- batch size;
- accumulation;
- learning rate;
- optimizer;
- scheduler;
- epochs;
- augmentation;
- hardware;
- training time;
- peak VRAM;
- metrics;
- checkpoint.

Use MLflow or Weights & Biases if the team selects one; do not add both merely for completeness.

---

# 29. HARDWARE POLICY

Current local development machine is treated as constrained GPU hardware.

Before training, inspect the actual environment rather than assuming it.

Run:

```bash
nvidia-smi
```

and:

```bash
python -c "import torch; print(torch.__version__); print(torch.version.cuda); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'no cuda'); print(torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else 'no cuda')"
```

The project should support:

- lazy dataset loading;
- DataLoader;
- small batches;
- mixed precision where supported;
- gradient accumulation when useful;
- controlled worker count.

Do not load the entire dataset into VRAM or decoded system memory unnecessarily.

Use cloud GPU only for experiments that genuinely exceed local constraints.

---

# 30. FRONTEND CINEMATIC ASSETS

Existing assets must be inspected before assigning semantic roles:

```text
src/public/
├── 1.mp4
├── 2.mp4
├── 3.mp4
└── 4.mp4
```

Do not assume filename order equals narrative order.

Do not convert them to JPG merely for convenience.

Use them as video assets if they meaningfully support the product story.

The cinematic section is a product/UX layer, not the scientific contribution.

---

# 31. PHOTO GUIDANCE

Guidance should adapt to the reported damage location.

Consider:

- distance;
- lighting;
- glare;
- angle;
- camera height;
- panel visibility;
- surrounding undamaged bodywork;
- body lines as visual reference.

Do not give the same generic instruction for every panel.

---

# 32. API CONTRACTS

Future endpoint groups may include:

```text
POST /chat
POST /inspection/context
POST /inspection/image
POST /inspection/validate-image
POST /inspection/analyze
POST /inspection/cost
GET  /inspection/{id}
```

Do not implement all endpoints during bootstrap.

Use Pydantic request/response models.

Never serialize internal model objects directly to the browser.

---

# 33. SECURITY / PRIVACY

Never expose Groq credentials to the frontend.

Never commit `.env`.

Vehicle images are potentially sensitive.

Do not collect unnecessary exact residential addresses. Repair-city/market context is normally sufficient for pricing research.

Avoid logging raw images or sensitive metadata unnecessarily.

Temporary files should be cleaned when appropriate.

---

# 34. ERROR HANDLING

Handle at least:

- invalid image;
- blur;
- darkness;
- glare;
- wrong angle;
- missing vehicle information;
- low model confidence;
- model failure;
- unavailable cost data;
- Groq failure;
- LangGraph failure;
- user/model disagreement.

Translate technical errors into user-readable guidance.

Never hide a failure behind fake successful output.

---

# 35. TESTING

Agent tests:

- missing information;
- repeated information;
- structured extraction;
- graph transitions;
- photo guidance;
- disagreement handling.

Image tests:

- valid image;
- blur;
- darkness;
- glare;
- incorrect framing.

ML tests:

- inference schema;
- mask format;
- feature extraction;
- confidence propagation.

Cost tests:

- validated cost data path;
- unavailable cost data;
- interval validity;
- currency/schema handling.

E2E:

```text
conversation
→ context
→ image
→ quality check
→ vision
→ fusion
→ cost
→ explanation
```

---

# 36. AI SKILLS / MCP ROUTING

Recommended capabilities:

- Superpowers → planning/TDD/debugging/verification
- everything-claude-code → reusable skills only when directly relevant
- ui-ux-pro-max → frontend/UI design tasks
- Playwright MCP → browser verification/E2E
- GitHub MCP → issues/PR/repository workflows
- Context7 → current framework/library documentation
- Vercel MCP → deployment tasks once Vercel is actually used

Do not activate every skill pack for every task.

The goal is **less unnecessary code**, not more agent activity.

Routing rule:

```text
Task
 ↓
identify smallest required capability
 ↓
use it
 ↓
verify result
```

`AGENTS.md` remains the project authority.

---

# 37. CODE GENERATION GUARDRAILS

Before creating a new file, ask:

> Does this file have a clear, current responsibility?

Before creating a utility/helper:

> Does an existing function already do this?

Before adding a dependency:

> Can the existing stack solve this?

Before adding an abstraction:

> Is it required now rather than anticipated for later?

Before creating an endpoint:

> Is there a real current consumer?

Before creating a database model:

> Is the data model intentionally defined?

Before implementing an ML task:

> Do we have valid labels and a measurable research question?

If the answer is no, do not generate production code for it.

---

# 38. DEAD-CODE PREVENTION

At the end of every implementation task:

1. remove unused imports;
2. remove unused variables;
3. remove abandoned functions/classes;
4. remove temporary debug prints;
5. remove stale TODOs introduced by the task;
6. remove duplicate implementations;
7. remove unused dependencies;
8. inspect the final diff.

Do not keep “just in case” code.

---

# 39. QUALITY GATE

Every meaningful implementation should move through:

```text
Format
 ↓
Lint
 ↓
Type check
 ↓
Targeted tests
 ↓
Integration/E2E where applicable
 ↓
Diff review
```

ML experiment code also needs reproducibility and metric validation.

---

# 40. DOCUMENTATION RULES

Maintain:

```text
docs/architecture/overview.md
docs/research/problem-definition.md
docs/research/research-scope.md
docs/research/experiment-principles.md
docs/ml/ml-engineering-guidelines.md
docs/decisions/
```

Use ADRs for material decisions.

Do not duplicate the full research literature in several documents.

---

# 41. PHASED EXECUTION PLAN

## Phase 0 — Repository / environment audit

Inspect:

- repository;
- research MD;
- AGENTS.md;
- existing frontend/backend;
- dataset;
- videos;
- Python environment;
- CUDA;
- secrets/config.

No heavy coding yet.

## Phase 1 — Dataset audit

Build dataset report and annotation validation.

No final model training yet.

## Phase 2 — Training adapter + smoke test

Validate labels, masks, augmentation, checkpointing, inference.

## Phase 3 — Primary segmentation baseline

Train lightweight local model.

## Phase 4 — Benchmark + external validation

Measure segmentation and domain shift.

## Phase 5 — Damage feature pipeline

Generate structured representations from segmentation.

## Phase 6 — Downstream baseline

Vision-only and simple multimodal models.

## Phase 7 — Proposed multimodal model

Cross-attention/advanced fusion if the data supports it.

## Phase 8 — Cost uncertainty

Only once validated observed-cost labels exist.

## Phase 9 — LangGraph + Groq integration

Structured context acquisition and orchestration.

## Phase 10 — Frontend inspection experience

Chat, upload, processing, visualization, results, explanation, report.

## Phase 11 — Cinematic UX

Integrate the supplied videos after inspecting their content.

## Phase 12 — Final evaluation

Ablations, robustness, calibration, failure analysis, documentation.

---

# 42. FIRST TASK FOR BIG PICKLE

When this file is provided to Big Pickle/OpenCode, do **NOT** immediately generate the full application.

Do this first:

```text
1. Read this file.
2. Read AutoInspect-X_Research_Report_Corrected.md.
3. Read AGENTS.md / CLAUDE.md.
4. Inspect the actual repository tree.
5. Inspect pyproject/package configuration.
6. Inspect the CarDD annotation structure.
7. Inspect the four video assets.
8. Check Python + CUDA environment.
9. Check git status.
10. Identify architecture conflicts.
11. Produce a concise audit report.
12. Propose Phase 0 changes only.
13. Wait for the next task before building product functionality.
```

Do not silently continue into later phases.

---

# 43. DEFINITION OF DONE FOR ANY FUTURE FEATURE

A feature is not done because code was generated.

It is done only when:

- requirements are clear;
- architecture is respected;
- existing code was reused where appropriate;
- implementation is minimal;
- types are correct;
- errors are handled;
- tests exist where appropriate;
- lint/type-check pass;
- no dead code remains;
- research claims remain honest;
- no synthetic data is mislabeled as ground truth;
- the user-facing result reflects actual system state;
- final diff has been reviewed.

---

# 44. FINAL PROJECT PRINCIPLE

The system should feel simple to the user while remaining technically rigorous underneath.

```text
LISTEN
  ↓
UNDERSTAND
  ↓
GUIDE
  ↓
VERIFY
  ↓
INSPECT
  ↓
FUSE
  ↓
ESTIMATE
  ↓
EXPLAIN
```

**Explain the result; do not merely display the result.**

And scientifically:

> **Do not claim more than the data, experiments, and labels can support.**
