# Implementation ↔ Research Reconciliation

Status of the codebase against `AutoInspect-X_Research_Report_Corrected.md`
(the canonical research document; photo-first rewrite dated 2026-09-21) and the
bootstrap brief `archive/docs/CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md`.

Legend: `IMPLEMENTED` · `PARTIAL` · `NOT STARTED` · `PLANNED` · `REMOVED`

Scope note: this file was reconciled on 2026-09-21 to match **ADR 0011
(photo-first scope)** and **ADR 0010 (CarddHybrid)**. Sections describing a
cost/repair/multimodal research core from the previous version are removed along
with those tasks.

---

## 1. Research requirement (photo-first)

**Research statement (research report §3, §5.7, §9):** the contribution is a
CNN+Transformer hybrid segmentation model (`CarddHybrid`) compared against a
plain U-Net baseline (`CarddUNet`) for damage-segmentation quality and
confidence honesty on CarDD. The system is photo-first: quality gate → mask →
evidence payload → honest explanation, with no cost/repair outputs.

### Current implementation status

- Segmentation core: `IMPLEMENTED`. Research models (spec v3): baseline
  `ResNet34UNet` + proposed `HybridSegmentation`, both implemented **and**
  trained for 15 epochs (seed 0, full official splits): baseline foreground
  mIoU 0.6127 / mDice 0.7440 / pixel accuracy 0.8979; hybrid foreground mIoU
  0.5963 / mDice 0.7320 / pixel accuracy 0.8873 (@ epoch 14, both still
  improving; **preliminary validation only — not a final conclusion, no
  statistical significance claimed**). The legacy `CarddHybrid` demo run
  (`cardd_hybrid_ce`, val mIoU 0.0504, MEASURED) is archived.
- Demo default: `ml/experiments/pilot15_hybrid/best_checkpoint.pt`, loaded via
  `MODEL_PATH` / container default; the baseline pilot is retained as the
  controlled arm.
- Research comparison (RQ1/RQ2): `PARTIAL` — pilots are 15-epoch preliminary
  checks; the 60-epoch / 3-seed comparison and the RQ2 confidence-honesty
  metric are still `PLANNED`.

### Evidence in repository

- Baseline: `ml/models/resnet34_unet.py` (spec v3 §9.1) + `pilot15_baseline`
  run (`ml/experiments/pilot15_baseline/run_record.json`, archived legacy runs
  under `archive/experiments/`).
- Hybrid: `ml/models/hybrid_segmentation.py` (spec v3 §4/§5/§18) +
  `pilot15_hybrid` run; legacy `ml/models/cardd_hybrid.py` (ADR 0010) kept in
  the live tree because the engine/train dispatch still loads `cardd_*`
  checkpoints.
- Experiment harness: `ml/training/train.py` (`--model baseline|hybrid` plus
  legacy `cardd_*` arm), `ml/evaluation/metrics.py`, shared loss
  `ml/training/loss.py`.
- Inference + honesty: `ml/inference/engine.py` (`model_arch` dispatch for
  `resnet34_unet`/`baseline`, `hybrid`/`hybrid_segmentation`, and legacy
  `cardd_*`), `apps/api/container.py` (foreground-mIoU notes from
  `registry.json`).
- Scope: `docs/decisions/0010-cardd-hybrid-model.md`,
  `docs/decisions/0011-photo-first-scope.md`.

### Gap

- The honest A1-vs-A3 head-to-head write-up (`research_summary.md`) is not yet
  written; A2/A4 extended runs are not started.
- The RQ2 confidence-honesty operational metric is not yet locked.

### Recommended next action

Run A2 (U-Net extended) for a fair underfit-vs-architecture separation; lock
RQ2; write `research_summary.md` before any performance statement.

---

## 2. Segmentation framework (research report §8 vs ADR 0006/0010)

### Research requirement

Report §8 recommends a CNN+Transformer hybrid (bottleneck transformer) against
the U-Net baseline; the earlier version's YOLOv8-Seg/SegFormer recommendation is
superseded by the framework decision below.

### Current implementation status

`IMPLEMENTED` — raw PyTorch `CarddUNet` baseline + `CarddHybrid` hybrid.

### Evidence in repository

- `docs/decisions/0006-segmentation-framework.md`: raw PyTorch U-Net over
  ultralytics YOLO; YOLO deferred to a potential later comparison baseline.
- `docs/decisions/0010-cardd-hybrid-model.md`: transform-borne upgrade —
  transformer bottleneck at 32×32, `d_model=base*8`, 4 heads, 2 layers,
  sinusoidal positional encoding; same 7-channel argmax decode and CE loss.
- `ml/models/cardd_unet.py`, `ml/models/cardd_hybrid.py`.

### Gap

- The hybrid is a researched architecture choice (ADR 0010) but has zero
  training evidence yet.

### Resolution (this reconciliation)

Framework is an **engineering decision, not a research contribution**; the
research question is independent of the specific CNN brand. The bottleneck-
transformer design is a standard, GPU-bounded upgrade (see TransUNet et al. in
the research report §5.4). Keeping both models on the same harness makes the
comparison clean.

### Recommended next action

Train both under the locked schedule (see §6) before any architecture comment.

---

## 3. Damage-area feature (ADR 0005/0009 vs the report's surface-area claim)

### Research requirement

Earlier report version proposed a physical surface area in cm². Current version
(§3) defines only `damaged_pixels / total_image_pixels` — a normalized
DERIVED FEATURE, explicitly not cm².

### Current implementation status

`IMPLEMENTED` (image-denominator ratio in `ml/inference/features.py`);
part-normalized form `normalized_damage_area` reserved and unavailable.

### Evidence in repository

- `docs/decisions/0005-cardd-part-mask-gap.md`: CarDD has damage masks, **no
  vehicle-part masks** → `damaged_pixels / part_pixels` not implemented.
- `docs/decisions/0009-part-segmentation-decision.md`: part segmentation not
  adopted this cycle; `damage_area_ratio_image` is the only area feature.
- `ml/datasets/cardd_audit.py` + `ml/datasets/reports/cardd_audit.json`:
  no part annotations in the schema.

### Gap

`A_phys` (cm²) requires part masks + calibration; both absent. Any interface
claiming physical area would violate ADR 0004/0005.

### Recommended next action

None — current contract is already the honest one; keep reserved names unused.

---

## 4. Hidden structural damage head (earlier report §12–§13)

### Research requirement

Earlier version proposed `P(H=1 | F)` with focal loss. Removed with the
photo-first scope.

### Current implementation status

`REMOVED` — correctly out of scope, as it was before.

### Evidence in repository

- `archive/docs/research-scope.md` (Out of scope): hidden-damage risk excluded
  unless real ground-truth labels exist; synthetic labels do not qualify.
- `docs/decisions/0004-ground-truth-labelling-policy.md`: synthetic hidden-damage
  labels are not evidence.
- No code or labels reference hidden damage.

### Recommended next action

Keep marked future/optional. If real teardown-labelled data ever appears, add it
via a new ADR before implementing.

---

## 5. Repair cost and repair action (removed — ADR 0011)

### Research requirement

Earlier version required quantile cost intervals (`P10/P50/P90`) and repair
action. **Removed by ADR 0011** (accepted 2026-09-21): CarDD has no observed
cost or action labels; rule tables are SYNTHETIC LABEL.

### Current implementation status

`REMOVED` — `apps/api/cost/`, `apps/api/repair/` deleted; all cost/quote/amount
fields, `CostPayload`/`RepairPayload`, `ALLOW_SYNTHETIC_ESTIMATE`, and the
`p10/p50/p90` demo structure gone. Enforced by tests
(`_assert_no_forbidden_fields` in `tests/test_e2e_integration.py`).

### Evidence in repository

- `docs/decisions/0011-photo-first-scope.md` (scope cut, contract
  simplification, assistant replacement).
- `tests/test_e2e_integration.py`, `tests/test_agent_assistant.py`,
  `tests/test_agent_graph.py`.

### Gap / recommended next action

None. Do **not** reintroduce cost/repair fields without a new ADR and real
ground-truth data.

---

## 6. Experiment harness and metrics (research report §12–§14)

### Research requirement

Report §12–§14 require: locked baseline config, softmax CE over argmax target,
mIoU/Dice/pixel accuracy/per-class metrics, small-damage slice, and an
RQ2 confidence-honesty evaluation; test split evaluated once.

### Current implementation status

`IMPLEMENTED` for the segmentation metrics and harness (Phase 4/6/7/8);
`PLANNED` for RQ2 honesty evaluation.

### Evidence in repository

- `archive/docs/segmentation-experiment-config.md` (historical Phase 6 locked
  design: official splits, 7 channels, 512×512, batch 2 — 2.85 GB peak VRAM
  measured — Adam 1e-3 wd 1e-5, CosineAnnealingLR, 5 epochs, seed 0, best val
  mIoU checkpoint; superseded by the architecture spec v3 + recorded pilot
  configs).
- `ml/evaluation/metrics.py` (IoU/Dice/precision/recall, background excluded,
  absent classes 0.0); `ml/evaluation/small_damage.py` (train p25 ≈ 3,013.5 px
  @512, measured); `ml/evaluation/evaluate_run.py` (montages, summary).
- `ml/training/loss.py::cross_entropy_loss` (ADR 0008).

### Gap

- RQ2 has **no locked operational metric** yet (`research_summary.md` must not
  report honesty numbers without it).
- mAP (instance-level) remains not implemented — acceptable for the current
  pixel-mask RQ, noted as a limitation in the research report §14.

### Recommended next action

Lock the RQ2 metric (proposed: separation of mean-confidence / low-flag
distributions between agreement and disagreement groups vs CarDD val); evaluate
A2/A3/A4 with the same harness.

---

## 7. Dataset scope (research report §5.2, §7 vs repo)

### Research requirement

Report §7: CarDD is the sole integrated dataset (REAL GROUND TRUTH); other
public sources (VehiDE, CrashCar101) are reviewed as literature, not integrated.

### Current implementation status

`IMPLEMENTED` for CarDD-COCO only; other sources `NOT STARTED` (correctly).

### Evidence in repository

- `ml/datasets/cardd_adapter.py`, `cardd_audit.py`, `cardd_vis.py`.
- `ml/datasets/reports/cardd_audit.json` (train 2816 / 6211, val 810 / 1744,
  test 374 / 785; 6 classes; sums to 4,000 images / 8,740 instances).
- `.gitignore`: raw datasets stay out of Git.

### Gap

- No metadata/cost/part-annotated dataset integrated — and none is needed under
  ADR 0011.
- The report flags "CDD (2025)" and "Insurance-Damage-v2" as UNVERIFIED; they
  are not used as evidence.

### Recommended next action

Keep CarDD as the sole integration. Any new dataset enters with licence + label
mapping + split policy (recording the same reproducibility rules formerly in
`archive/docs/experiment-principles.md` §3) and a new ADR.

---

## 8. Claims the repository cannot yet support

| Claim | Status | Binding constraint |
|---|---|---|
| CarddHybrid improves segmentation quality over the baseline | Weak positive only — `cardd_hybrid_ce` val mIoU 0.0504 > 0.0475, test 0.0586 > 0.0500 (MEASURED); model still underfit, small-damage slice ≈ 0 | Fair-comparison rule: A2/A4 + write-up `research_summary.md` still pending; claim level capped at the measured numbers |
| Confidence-honesty difference between A1–A4 | No evidence — metric not locked | RQ2 operational definition missing |
| Physical damage area in cm² | Not derivable | ADR 0004/0005; no scale reference |
| `normalized_damage_area` (part-normalized) | Not derivable | ADR 0005; no part masks |
| Hidden structural risk probability | Not trainable | No teardown labels |
| Repair-action / repair-cost prediction | Removed | ADR 0011 |
| Cost quantiles with coverage | Removed / no data | ADR 0011 |
| mAP / instance-matched metrics | Not implemented | Not required for the locked pixel RQ; documented limitation |

---

## 9. Explicitly future / optional per the research direction

- RQ2 confidence-honesty experiment — the open portion of the current research
  question.
- MC Dropout / Deep Ensembles as confidence layers — extensions (research report
  §5.6), each via its own ADR.
- External smartphone validation set (300–1,000 images) — domain-shift
  evaluation (§24 blockers).
- Multi-angle / 3-D-aware extension, Grad-CAM / SHAP explainability,
  part segmentation, hidden-damage head — out of scope today (research report
  §15–§16, §6).
  
---

## 10. Citation / data-integrity notes (updated 2026-09-21)

- **CarDD DOI corrected:** the earlier report cited
  `10.1109/TITS.2022.3225828` (a GitHub link); the verified citation is
  **IEEE T-ITS vol. 24, no. 7, pp. 7202–7214, 2023, DOI 10.1109/TITS.2023.3258480**,
  arXiv:2211.00945 — verified against the CarDD project page (material
  correction, recorded in the research report references).
- **VehiDE figures corrected:** verified VehiDE = 13,945 images / 32,000+
  instances / 8 classes (KSE 2023). The previously listed "12,000 / 61 / 26" was
  not verified and matches the ALBERT dataset description instead; it is treated
  as UNVERIFIED in the report.
- **UNVERIFIED, not used as evidence:** "CDD (2025)", "Insurance-Damage-v2",
  and the individual "Top 15 papers" entries (Sharma 2025, Patel 2025, Vignesh
  2025, Zhang 2023, Chen & Schmidt 2024) from the previous report version, which
  could not be independently verified and are dropped/replaced by the verified
  corpus in the research report §5.
- Market figures and commercial-system descriptions remain report content only;
  nothing in the repo validates them and they are not used in any claim.

---

## 11. Material corrections recorded

| # | Correction / clarification | Where recorded |
|---|---|---|
| 1 | CarDD has no part masks → `normalized_damage_area` unavailable; only image-denominator ratio | ADR 0005 |
| 2 | Segmentation framework = raw PyTorch U-Net; YOLO deferred | ADR 0006 |
| 3 | Physical cm² / hidden damage / real costs all out of scope until data supports them | ADRs 0004, 0009, plus this document |
| 4 | Research report + bootstrap docs added to repo root (2026-09-08) | MEMORY |
| 5 | BCE incompatible with argmax decode → softmax CE over argmax target | ADR 0007 (superseded) / ADR 0008 |
| 6 | **CarddHybrid (CNN+transformer) added as the proposed segmentation model;** checkpoints carry `model_arch` | ADR 0010 |
| 7 | **Photo-first scope: cost/repair/questionnaire removed; single assistant; composer chat** | ADR 0011 |
| 8 | **Research report rewritten to photo-first; literature review re-verified; CarDD/VehiDE citations corrected; unverifiable prior citations flagged UNVERIFIED** | research report; this document |

No research direction was silently modified. Where the report and repository
disagree, the divergence is recorded here and in the relevant ADRs.