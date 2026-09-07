# Implementation ↔ Research Reconciliation

Status of the codebase against `AutoInspect-X_Research_Report_Corrected.md`
(the canonical research document, added to the repo root on 2026-09-08) and the
bootstrap brief `CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md`.

Legend for **Current implementation status**: `IMPLEMENTED` · `PARTIAL` ·
`NOT STARTED` · `BLOCKED BY DATA`.

---

## 1. Research requirement

**Research-formalizable statement (report §12–§13):** the contribution is a
multimodal cross-attention system that fuses pixel-level damage segmentation +
vehicle-part masks + structured metadata, and produces repair action, hidden
structural risk, and uncertainty-calibrated cost intervals (B1 vision-only /
B2 simple fusion / P cross-attention comparison).

### Current implementation status

`BLOCKED BY DATA` for the downstream heads, `PARTIAL` for the segmentation core.

### Evidence in repository

- Segmentation core: `ml/models/cardd_unet.py` (ADR 0006, raw PyTorch small
  U-Net), trained end-to-end on GPU (`ml/experiments/phase3_smoke`,
  `ml/experiments/phase4_baseline`).
- Experiment harness: `ml/training/train.py`, `ml/evaluation/metrics.py`,
  shared loss `ml/training/loss.py`.
- ADRs 0004 (ground-truth policy), 0005 (no part masks), 0006 (framework).

### Gap

- No metadata source, no fusion layer, no repair-action labels, no cost labels,
  no hidden-damage labels. The research question cannot be answered with
  CarDD-only data (see Phase 11 data-readiness).
- The report's proposed *part mask + physical area (cm²)* pipeline cannot be
  built from CarDD (ADR 0005).

### Recommended next action

Finish the segmentation baseline (Phase 8) so that the *vision side* is
measurable; the downstream comparison (B1/B2/P) waits on the data-readiness
verdict. Do not implement the fusion or cost heads before that verdict.

---

## 2. Segmentation framework (report §16 vs ADR 0006)

### Research requirement

Report §16 recommends a vision backbone of **YOLOv8-Seg / SegFormer**; §15 of
the bootstrap brief says to begin with a small Ultralytics YOLO variant if the
local GPU supports it.

### Current implementation status

`IMPLEMENTED` (differently) — **raw PyTorch small U-Net**, not YOLO.

### Evidence in repository

- `docs/decisions/0006-segmentation-framework.md`: chosen raw PyTorch U-Net;
  YOLO explicitly deferred to "comparison baseline later, only if fighting for
  IoU matters".
- `ml/models/cardd_unet.py`: the U-Net used by the smoke and baseline runs.

### Gap

- The research document and bootstrap both *suggest* YOLO-family as the
  practical starting point. ADR 0006 overrides: framework choice is a decision
  recorded as an ADR, and this task's directive keeps the existing U-Net.

### Resolution (this reconciliation)

The segmentation framework is an **engineering decision, not a research
contribution**. The research question (see §1) is independent of the detector
brand: it tests whether segmentation-derived features + metadata + fusion beat
vision-only baselines. Keeping the U-Net is therefore consistent with the
research direction; adopting YOLO would be an ADR, not a research change. No
silent change to the research direction.

### Recommended next action

No action. Re-evaluate YOLO only as a comparison *victim* model in a later
phase, documented by a new ADR, when the goal is an IoU benchmark rather than
the downstream research question.

---

## 3. Part masks and the normalized damage-area feature (report §13.1 vs ADR 0005)

### Research requirement

Report §13.1 defines the physical damage area

```
A_phys = ( sum S_damage / sum S_part ) × A_part_known(model)
```

and the bootstrap's research feature is

```
normalized_damage_area = damaged_mask_pixels / affected_part_pixels
```

### Current implementation status

`BLOCKED BY DATA` for the research feature; the image-denominator variant is
`IMPLEMENTED` as a DERIVED FEATURE.

### Evidence in repository

- `docs/decisions/0005-cardd-part-mask-gap.md`: CarDD provides damage masks only,
  **no vehicle-part masks** → `damaged_pixels / part_pixels` is not implemented
  and not reported from CarDD-only data.
- `ml/datasets/cardd_audit.py` + `ml/datasets/reports/cardd_audit.json`:
  annotation-level audit; no part annotations exist in the schema.
- The adapter exposes mask geometry but never a part-normalized ratio.

### Gap

- `A_phys` (cm²) requires known part surface dimensions and a part mask. Neither
  exists. Any interface claiming physical area would violate ADR 0004/0005.
- `normalized_damage_area` (part-normalized) is reserved and unavailable until a
  part-mask source is adopted via a new ADR.

### Recommended next action

**Decided (ADR 0009, Phase 10): part segmentation is not adopted this cycle.**
The image-denominator `damage_area_ratio_image` (DERIVED FEATURE) is the only
area feature produced. If a part source becomes a requirement in a later cycle,
candidates (e.g. VeHIDE/CDD with part annotations, per report §15) must be
evaluated for licence + label mapping first, and adopted via a new ADR with
full preprocessing/dedup/split policy. Do **not** generate fake part masks.

---

## 4. Hidden structural damage head via Focal Loss (report §13.3.A, §12.2)

### Research requirement

Report proposes `P(H=1 | F)` — a binary hidden-damage head trained with focal
loss, conditioned on impact location, deformation area, and vehicle geometry.

### Current implementation status

`NOT STARTED` — correctly out of scope.

### Evidence in repository

- `docs/research/research-scope.md` (Out of scope): hidden-damage risk excluded
  unless real ground-truth labels exist; synthetic labels do not qualify.
- `docs/decisions/0004-ground-truth-labelling-policy.md`: synthetic hidden-damage
  labels are not evidence.
- `CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md` §3: optional, real labels only.
- No code or labels in the repository reference hidden damage.

### Gap

- CarDD has no teardown/repair records. `P(Hidden)` cannot be trained or
  evaluated honestly.

### Recommended next action

Keep marked as **future/optional**. If real teardown-labelled data ever appears,
add it via a new ADR (source, licence, label definition) before implementing the
head.

---

## 5. Quantile cost interval head (report §13.3.B)

### Research requirement

`[C_low, C_high]` via pinball / quantile loss (τ=0.10 / 0.90), with interval
coverage evaluated as carefully as point error.

### Current implementation status

`NOT STARTED` — blocked pending a real observed-cost data verdict.

### Evidence in repository

- `docs/research/problem-definition.md` (Out of scope / open questions): cost
  ground truth unresolved; rule-based costs are SYNTHETIC LABEL.
- `docs/research/research-scope.md` (Metrics): quantile loss, coverage, width.
- `CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md` §19, §20: cost is a separate
  service; no real-looking prices hard-coded; cost research requires validated
  observed-cost data.
- No cost code exists.

### Gap

- CarDD has no repair cost annotations. No real observed-cost dataset is
  integrated. Synthetic price tables may be used for UI/pipeline development
  only (§19), never presented as ground truth.

### Recommended next action

Phase 11 data-readiness assessment. If observed repair-cost labels are missing,
**stop cost-model implementation**; pattern for the UI is
"Estimate unavailable / insufficient validated data", not a fabricated number.

---

## 6. Segmentation metrics (report §22 vs Phase 4 metric harness)

### Research requirement

Report §22 and bootstrap §25 require for segmentation: **mAP**, IoU, Dice/F1,
precision/recall, per-class AP. Small-damage recall is called out in the
bootstrap §15 comparison list.

### Current implementation status

`PARTIAL`.

### Evidence in repository

- `ml/evaluation/metrics.py`: mean IoU, per-class IoU, mean Dice, per-class
  Dice (confusion-matrix based, background excluded).
- `ml/training/train.py`: per-epoch val mIoU/mDice + pixel accuracy.
- `tests/test_evaluation_metrics.py`: unit tests for those functions.

### Gap

- **Precision / recall per class ‒ not yet computed.**
- **mAP (instance-level) ‒ not implemented.** The current metric harness is
  pixel confusion based (semantic, argmax over class channels). It does not
  evaluate instance-level mask matching (COCO-style AP).
- **Small-damage slice ‒ not yet defined or evaluated.**
- No qualitative prediction export yet.

### Recommended next action

Phase 7: extend the metric harness (precision/recall, per-class), define and
document a small-damage criterion from the audit statistics, export qualitative
montages (original / ground truth / prediction / overlay).

---

## 7. Dataset scope (report §15 vs repo)

### Research requirement

Report §15 lists CarDD, CDD 2025, CrashCar101 as options and proposes a
synthetic metadata DB joined from public pricing data.

### Current implementation status

`IMPLEMENTED` for CarDD-COCO only; other sources `NOT STARTED`.

### Evidence in repository

- `ml/datasets/cardd_adapter.py`, `cardd_audit.py`, `cardd_vis.py`.
- `ml/datasets/reports/cardd_audit.json` (train 2816 / 6211 ann, val 810 / 1744,
  test 374 / 785; 6 classes, counts consistent with the report's "4,000 images /
  ~9,000 instances" when the three splits are summed: 4,000 images, 8,740
  instances).
- `.gitignore`: raw datasets stay out of Git.

### Gap

- No metadata dataset, no repair-cost dataset, no part-annotated dataset
  integrated. The report's other sources (CDD 2025 / CrashCar101) are not
  assessed for licence or label mapping.
- Report's CarDD totals match our audit (4,000 images, ~8,740 instances vs
  report's "9,000 instances") — reported as close, not identical.

### Recommended next action

Keep CarDD as the sole integration until the part/cost/metadata decisions
(Phase 10/11) determine whether a second source is required. Any new dataset
enters with licence + label mapping + split policy (experiment-principles §3).

---

## 8. Claims the repository cannot yet support

These report statements describe future output. Do not present them as current
capability:

| Report claim | Status | Binding constraint |
|---|---|---|
| Physical damage area in cm² | Not derivable | ADR 0004/0005; no scale reference |
| `normalized_damage_area` (part-normalized) | Not derivable | ADR 0005; no part masks |
| Hidden structural risk probability | Not trainable | No teardown labels |
| Repair-action classification | Not trainable | No action labels (Phase 11) |
| Quantile cost intervals with coverage | Not evaluable | No observed cost labels |
| Cross-attention fusion claim | Not implemented | Would require B1/B2/P on same data |
| mAP / instance-matched metrics | Not implemented | Phase 7 gap |

---

## 9. Explicitly future / optional per the research direction

- Hidden-damage head — optional, real labels only (bootstrap §3).
- Part segmentation — only if the research question needs `part_pixels`; adopt
  via ADR with licence/mapping (bootstrap §16; this task's Phase 10).
- External smartphone validation set (300–1,000 images) for domain-shift
  evaluation (bootstrap §23).
- Multi-angle / 3D-aware extension and MCDropout ensembles — publication-stage
  extensions (report §"Ambitious Version"), not required for the core research
  question.
- Grad-CAM / SHAP explainability — product/UX layer, later than the research
  comparison.

---

## 10. Citation / data-integrity notes

- The report's CarDD DOI link points to a GitHub repository rather than the
  paper page; the bibliographic line (Wang / Li, IEEE T-ITS, "CarDD...") is
  recorded as read from the report and has **not been independently verified**
  by the repository. Treat it as report-provided, not confirmed.
- Market figures (§9) and commercial-system descriptions (§8) are report content
  only; nothing in the repo validates them and they are not used in any claim.

---

## 11. Material corrections recorded

| # | Correction / clarification | Where recorded |
|---|---|---|
| 1 | CarDD has no part masks → `normalized_damage_area` unavailable; only image-denominator ratio | ADR 0005 |
| 2 | Segmentation framework = raw PyTorch U-Net; YOLO deferred | ADR 0006 |
| 3 | Physical cm² / hidden damage / real costs all out of scope until data supports them | ADRs 0004, plus this document |
| 4 | Research report + bootstrap docs added to repo root (2026-09-08) | this document / MEMORY |

No research direction was silently modified. Where the report and repository
disagree (framework, part masks), the divergence is recorded here and in the
relevant ADRs, and the research question itself is unaffected.