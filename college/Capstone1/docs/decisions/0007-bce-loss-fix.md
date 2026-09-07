# ADR 0007 — Fix BCE objective to class-balanced over all pixels

Status: **Superseded by ADR 0008** (2026-09-08). The class-balanced BCE fix was
correct about the positive-only weighting bug, but BCE-with-argmax is still
structurally incompatible with CarDD's background-as-never-set encoding; see
ADR 0008 for the adopted softmax cross-entropy objective.

## Context

Phase 4's `bce_loss` weighted only positive (damaged) pixels:

```python
loss = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
denom = targets.sum() + 1.0
return loss.mul(targets).sum() / denom
```

Because `loss.mul(targets)` zeroes the per-pixel loss wherever the target is
background, background pixels contributed nothing. The first full-split run
(`cardd_baseline_full`, 2026-09-08) exposed the degenerate optimum: training
BCE collapsed to ~0.0001 within an epoch while the model predicted *no
background at all* (val confusion: predicted class 0 count = 0 over 80 sampled
images), giving val pixel accuracy ~1.7% and never recovering.

## Decision

Replace the positive-only BCE with the standard class-balanced BCE over all
pixels:

```python
return F.binary_cross_entropy_with_logits(
    logits, targets, pos_weight=torch.as_tensor(pos_weight, device=logits.device)
)
```

with `pos_weight = 4.0` by default, recorded verbatim in every run's config
(`TrainingConfig.pos_weight`, train CLI `--pos-weight`).

## Consequences

- Background predictions are now penalized, so the model must actually separate
  damaged and undamaged pixels rather than classifying everything as damage.
- `pos_weight = 4.0` is a mild class-balance, not a tuned hyperparameter; it can
  be revisited by a dedicated tuning ADR.
- The Phase 4 smoke/Phase 4 baseline runs used the old objective; their low
  metrics are not research results and are not comparable to post-fix runs.
  This is recorded in each run's `note` field.