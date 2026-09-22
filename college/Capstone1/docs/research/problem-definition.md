# Problem Definition

Reconciled against `AutoInspect-X_Research_Report_Corrected.md` (photo-first
scope, 2026-09-21) and ADRs 0010–0011.

## Problem

Estimating vehicle damage from a photograph is currently manual, slow, and
inconsistent between assessors. An automated photo-first inspection would
support insurance triage, workshop intake, and used-vehicle assessment —
provided it is presented as decision support and never as a quotation.

With the photo-first scope (ADR 0011) the system answers one question honestly:

1. **Where is the damage, and how sure can we honestly be?** — a pixel-level
   damage mask, its per-class estimated area as a normalized ratio, and an
   explicit low-confidence flag.

The earlier "repair action + repair cost" decisions were removed: CarDD has no
repair-action or observed-cost labels, and a rule-generated cost table is a
SYNTHETIC LABEL, not evidence (ADR 0004, ADR 0011).

## Research question

How does the CNN+Transformer hybrid (`CarddHybrid`, ADR 0010) compare against
the plain U-Net baseline (`CarddUNet`) for damage-segmentation quality (mean
IoU, Dice, pixel accuracy, small-damage slice) and confidence honesty on CarDD,
on identical splits, seed, and training schedule?

## Why segmentation rather than classification

A classifier answers "is this vehicle damaged, and how badly". Segmentation
answers "which class, where, and how much of the image" — producing a structured
damage representation that can be shown to the user as visual evidence and
labelled with honest confidence. Explainability is a project requirement, not a
bonus.

## Inputs

| Input | Type | Source |
|---|---|---|
| Vehicle photograph | image | user upload (attached in the chat composer) |
| Damage evidence context | text (optional) | conversational intake (incident description) |

No vehicle metadata (make/model/year) is required or used; no metadata arm
exists (ADR 0011).

## Outputs

| Output | Form | Ground-truth category |
|---|---|---|
| Damage mask | 7-channel argmax over background + 6 damage classes | MODEL PREDICTION |
| Per-class area | `damaged_pixels / total_image_pixels` ratio | DERIVED FEATURE |
| Confidence | mean pixel confidence + `low_confidence` flag | MODEL PREDICTION |
| Evidence overlay | predicted-mask PNG over the photo | MODEL PREDICTION |
| Explanation | honest narrative from LangChain ChatGroq (or offline stub), grounded in the persisted evidence | MODEL PREDICTION / ASSUMPTION on framing |

Explicitly **not** an output: repair cost, repair action, physical area in cm²,
hidden-damage probability, final workshop quotation.

## Comparison arms to beat

> **Current arms (2026-09-22, architecture spec v3).** The legacy
> `CarddUNet`/`CarddHybrid` pairs below are superseded as *research arms* by
> the spec-v3 models: **baseline** = `ResNet34UNet`
> (`ml/models/resnet34_unet.py`), **proposed** = `HybridSegmentation`
> (`ml/models/hybrid_segmentation.py`). Both were run for 15 epochs (seed 0,
> full official splits): baseline foreground mIoU 0.6127, hybrid 0.5963 —
> **preliminary validation only, both still improving at epoch 14, no
> architecture claimed superior.** The demo default is `pilot15_hybrid`
> (research plan); the controlled comparison remains the planned 60-epoch /
> 3-seed run.

1. **A1 — current baseline:** `CarddUNet`, softmax CE, 5 epochs
   (`cardd_baseline_ce`: val mIoU 0.0475, MEASURED, underfit, SUPERSEDED).
2. **A2 — same harness, more epochs:** separates "underfitting" from
   "architecture" before the hybrid is credited (PLANNED).
3. **A3/A4 — proposed:** `CarddHybrid` on the same schedule (A3) and extended
   (A4). A3 is **done**: `cardd_hybrid_ce` trained 2026-09-21, val mIoU 0.0504 /
   test mIoU 0.0586 (MEASURED), inference verified through the engine + real-
   engine E2E and Playwright journeys.

Evidence so far is a **weak positive** on aggregate only: the hybrid remains
underfit, rare classes sit at IoU 0, and the small-damage slice is ≈0. A
fuller claim requires the RQ2 confidence-honesty metric to be locked in the
experiment config and an honest A1-vs-A3 comparison written.

## Out of scope

- **Repair-cost and repair-action prediction.** Removed (ADR 0011); no labels
  exist. Synthetic price tables are a SYNTHETIC LABEL and are not used.
- **Hidden-damage risk prediction.** Excluded unless real ground-truth labels
  become available; synthetic labels do not qualify.
- **Physical damage area in cm².** An uncontrolled photograph has no scale
  reference. Only the normalized damage-area ratio is defensible (ADR 0005/
  0009).
- **Vehicle-part segmentation.** Not adopted this cycle (ADR 0009); no
  part-mask source.
- **Final workshop quotation.** The system produces an estimate of evidence and
  confidence. The interface must state the difference.

## Open questions

1. What is the operational RQ2 metric ("confidence-honesty")? It must be
   defined and locked in the experiment config before any number is reported.
2. Does the hybrid's bottleneck transformer justify its ~1.7× parameter cost on
   a 4 GB GPU within the training budget? (Empirical — answered by A1/A2/A3/A4.)
3. If a new damage dataset is ever adopted (e.g., VehiDE), it enters only via a
   new ADR with licence, label mapping, and split policy.