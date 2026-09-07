# ADR 0008 — Use softmax cross-entropy over the argmax class target

Status: **Accepted** (2026-09-08). Supersedes the BCE options in ADR 0007.

## Context

The Phase 8 evaluation exposed that a BCE objective, even class-balanced, is
structurally incompatible with the deployment decode and the metric semantics:

- `aggregate_targets` encodes **background as "channel 0 is never set"** — class
  assignments live in channels 1..6, background is the complement.
- Metrics and inference decode with `argmax` over all 7 channels.
- Under BCE, the background channel is pushed to very negative logits
  everywhere (target = 0 for every pixel), while the six damage channels hover
  near 0 (they only get pulled negative where they are absent). On background
  pixels, argmax therefore almost always prefers some damage channel.

Measured symptom (phase8_midsize_fixcheck, seed 0, base 64, 600 train / 200 val
images, 3 epochs): the model predicted **0% background** on both val and train
despite background being ~76% of pixels; training CE/BCE hovered around 0.34
without improving pixel accuracy (~1.7%).

## Decision

Train with **softmax cross-entropy on the argmax class-index target**:

- `loss.py::cross_entropy_loss(logits, masks, labels, num_classes)` →
  `F.cross_entropy(logits, aggregate_targets(...).argmax(dim=1))`.
- Background becomes a real class (class 0 wins argmax when every damage
  channel is below it). The training objective now matches the evaluation
  decode exactly — argmax classes both in loss and in the confusion matrix.
- `pos_weight` machinery from ADR 0007 is removed (`TrainingConfig.pos_weight`,
  `--pos-weight`, `bce_loss`). No class weighting for the baseline (uniform).

## Consequences

- The single-class per-pixel softmax objective is the standard semantic-
  segmentation loss and matches the current metric harness (argmax, per-class
  IoU/Dice/precision/recall) without a second decoding step.
- Overlapping CarDD damage masks still collapse via argmax in the target
  (documented limitation in `metrics.py`); CE inherits the same caveat.
- `phase3_smoke`, `phase4_baseline`, `phase8_fixcheck`, and
  `phase8_midsize_fixcheck` runs used a BCE objective; their metrics are not
  directly comparable to post-ADR-0008 runs. Their `run_record.json` entries
  are retained but flagged as superseded.
- A weighted-CE variant (class weights from CarDD pixel balance) is possible
  later behind a new ADR if an imbalance study asks for it.

## Corrigendum (same day)

While reporting the ADR-0008 run, the pixel-accuracy metric was found to divide
matched pixels (over the (B, H, W) class-index map) by the *channel* count
`numel(targets)` = (B, 7, H, W), understating pixel accuracy ~7×. Fixed in both
`train.py::evaluate` and `evaluate_run.py::evaluate_split` to normalize by
`numel(target_classes)`. Reported pxAcc for the baseline run below is the
corrected value; earlier phase4-era pxAcc numbers in `run_record.json` used the
self-consistent path and were not affected by this bug (checked: phase4 did not
report pxAcc the same way).