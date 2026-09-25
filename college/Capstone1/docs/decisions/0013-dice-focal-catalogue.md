# ADR 0013 — Use Dice + Focal for the current controlled catalogue

Status: **Accepted** (2026-09-25).

## Context

ADR 0008 records the historical Phase 8 decision to use softmax
cross-entropy. The architecture specification v3 and the current training
entrypoint subsequently use `ml.training.loss.dice_focal_loss`: a deep-
supervised objective with 0.50 foreground soft Dice and 0.50 multiclass Focal
loss. The controlled run records identify code revision `591d7d2`, whose
`ml/training/train.py` imports and calls that objective. The run-record schema
does not contain a separate `objective` field, so the objective is recorded
here as code-revision provenance rather than inferred from a missing JSON key.

Changing the code to CE now would invalidate the relationship between the
existing controlled checkpoints and the code that produced them. The research
report and live architecture specification must instead distinguish the
historical CE path from the current catalogue.

## Decision

1. The four controlled `final60_*` runs use the shared Dice + Focal objective
   for both `ResNet34UNet` and `HybridSegmentation`.
2. The objective uses soft Dice over the six foreground classes, multiclass
   Focal loss with the recorded class weights and background weight, and deep
   supervision weights `0.75`, `0.15`, and `0.10` for the main and two
   auxiliary outputs.
3. Evaluation continues to use the common argmax decode and foreground metrics.
4. Historical CE/BCE run records remain valid for their original experiments
   and are not re-labelled as Dice + Focal runs.
5. A future objective change requires a new ADR and explicit recording in the
   run-record schema before new checkpoints are treated as comparable.

## Consequences

- Current catalogue documentation describes the actual trainer used by the
  controlled run records rather than the superseded CE wording.
- Existing validation metrics are not retroactively reinterpreted, and no
  claim is made that the two loss functions are equivalent.
- Reproducibility remains limited by the existing run-record schema: future
  records should include the objective name and its version explicitly.
