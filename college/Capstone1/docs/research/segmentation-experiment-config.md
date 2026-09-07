# Locked Segmentation Experiment — Baseline Design

Phase 6 locks the first research-grade segmentation experiment. One defensible
baseline configuration, not hyperparameter tuning. Reconciles with
`AutoInspect-X_Research_Report_Corrected.md` §22 (metrics) and
`CLAUDE_CODE_AUTOinspectX_BOOTSTRAP_UPDATED.md` §25/§28 (evaluation / tracking),
and with ADR 0006 (raw PyTorch U-Net).

Wrapper: `ml/training/train.py` (Phase 4 harness). Model: `CarddUNet` (ADR 0006).

---

## 1. Dataset and split

| Item | Value | Evidence |
|---|---|---|
| Dataset | CarDD-COCO | `ml/datasets/cardd_adapter.py` |
| Version | files under `datasets/CarDD_COCO` (git-ignored); commit the audit JSON | `ml/datasets/reports/cardd_audit.json` |
| Official splits, preserved | train2017 / val2017 / test2017 | verified disjoint in `ml/training/smoke_test.py` |
| Train split | 2,816 images, 6,211 instances | audit |
| Validation split | 810 images, 1,744 instances | audit |
| Test split | 374 images, 785 instances | audit — **touched once, at the end** (experiment-principles §2) |
| Leakage | no duplicates found by raster hash; official splits kept | audit + `smoke_test.py` |

No custom re-split. Validation is used for model selection; test is used once.

## 2. Classes

CarDD damage classes, indexed by their category id; channel 0 always background:

| Channel | Class |
|---|---|
| 0 | background |
| 1 | dent |
| 2 | scratch |
| 3 | crack |
| 4 | glass shatter |
| 5 | lamp broken |
| 6 | tire flat |

`num_classes = max(category_ids) + 1 = 7`. Per-class binary targets are built by
per-instance mask aggregation (`ml/training/loss.py::aggregate_targets`).
Overlapping damage classes collapse to a single argmax label in metric
computation (documented limitation in `ml/evaluation/metrics.py`).

## 3. Input resolution

Measured on this machine (probe, 2026-09-08):

| Resolution | Peak VRAM (base 64, batch 2) |
|---|---|
| 512 | 2.85 GB |
| 384 | 1.64 GB |

Decision: **512 × 512** (matches the adapter `TARGET_SIZE`, no downscale
compile-resampling). 384 is the fallback if a future model exceeds VRAM.

## 4. Batch, VRAM, and runtime strategy (4 GB RTX 3050)

| Item | Value |
|---|---|
| Batch size | **2** @ 512 (2.85 GB peak, ~1.1 GB headroom under 3.95 GB total) |
| Gradient accumulation | none for baseline; available if a later run needs a larger effective batch |
| Mixed precision | `torch.cuda.amp` not enabled in the harness yet; add only if a run needs it (documented then) |
| Workers | `num_workers=0` (dataset lazy; dataset is small enough) |
| Measured step time | ~0.29 s/step (base 64, batch 2, 512) in probe |
| Est. epoch time (full train) | ~2816/2 = 1408 steps → ~7 min compute + dataloader/validation overhead |

## 5. Augmentation

Train only (`augment=True`, `ml/training/cardd_dataset.py::_augment`):

- random horizontal flip (image + masks together; p=0.5);
- brightness/contrast jitter (±5% brightness, ±5% contrast on image only).

No augmentation on validation/test. No vertical flips or rotations (they are
physically wrong for vehicles).

## 6. Optimizer, LR, scheduler

| Item | Value |
|---|---|
| Optimizer | Adam |
| Learning rate | 1e-3 |
| Weight decay | 1e-5 |
| Loss | softmax cross-entropy over the argmax class target (ADR 0008) |
| Scheduler | CosineAnnealingLR, `T_max = epochs` |

Baseline is not tuned: these follow the Phase 3/4 defaults and are the first
defensible settings.

## 7. Epochs and early stopping

| Item | Value |
|---|---|
| Epochs | **5** (first full-split baseline; a bounded, reportable run on the 4 GB card) |
| Early stopping | none on the baseline — fixed schedule, simple and reproducible. Validation metrics are watched; a full-split run can be extended later |
| Checkpoint rule | save the checkpoint with **best validation mean IoU** across epochs (`best_checkpoint.pt`) |

## 8. Random seed policy

| Item | Value |
|---|---|
| Seed | `0` for the baseline run |
| Vocabulary | seed recorded in `run_record.json` → `config.seed` |
| Determinism | `torch.manual_seed(seed)` + `torch.cuda.manual_seed_all(seed)`; augmentation uses the global torch RNG |
| Variance | a multi-seed variance run is a *later* step; the baseline documents seed 0 explicitly |

Reproducibility requirement (experiment-principles §1) is met by recording:
experiment ID, dataset + version, split strategy, seed, git revision, model,
hyperparameters, full metric set, evaluation outputs, and assumptions — in
`run_record.json` + `registry.json` under `ml/experiments/` (git-ignored).

## 9. Metrics (validation and test)

| Set | Metrics | Where |
|---|---|---|
| Overall | mean IoU, mean Dice, pixel accuracy | `ml/evaluation/metrics.py` |
| Per class | per-class IoU, per-class Dice (channels 1–6) | `ml/evaluation/metrics.py` |
| Per class, additional | **precision, recall per class** | added in Phase 7 |
| Small-damage slice | per-class and overall metrics restricted to small damage instances | Phase 7 — criterion: mask area below the 25th percentile of the **train-split** per-instance mask-area distribution (~3,014 px at 512×512; measured 2026-09-08, n=6,211). Implemented in `ml/evaluation/small_damage.py` |
| Qualitative | original / ground truth / prediction / overlay montages | Phase 7 generator, Phase 9 report |

Background (channel 0) is excluded from mean scores.

## 10. Test protocol

- The test split (374 images) is evaluated **once**, after training + selection,
  with the best checkpoint and the same metric harness as validation.
- Do not fake or extrapolate full-dataset results from the earlier subset runs
  (phase3_smoke / phase4_baseline). Those remain machinery checks.

## 11. Assumptions and limitations

- Sub-sampling: none on the baseline — **full official train split** is used.
- The U-Net is a baseline model, not the final architecture (ADR 0006).
- Loss is softmax cross-entropy over the argmax target (ADR 0008). The
  2026-09-08 pre-ADR-0008 runs (`cardd_baseline_full`, `phase8_fixcheck`,
  `phase8_midsize_fixcheck`) used BCE objectives and are not comparable.
- GPU is the local RTX 3050 Laptop (~4 GB); training time and batch size are
  consequences, not choices.
- Report the run's VRAM, duration, GPU, and git revision in `research_summary.md`.

## 12. Status

`LOCKED` on 2026-09-08. Implements Phase 8 of the research plan mapping: this
corresponds to bootstrap-brief "Phase 3 — Primary segmentation baseline" and the
task numbering here as Phase 8.