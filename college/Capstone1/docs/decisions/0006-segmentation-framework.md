# ADR 0006 — Segmentation framework: raw PyTorch small U-Net

- **Status:** Accepted
- **Date:** 2026-09-08
- **Supercedes:** nothing (first framework decision)

## Context

Phase 3 requires a segmentation model to run a tiny local smoke training run
on the RTX 3050 Laptop (~4 GB VRAM) before any real experiments. Two candidate
paths were open in [CLAUDE.md](../ml-engineering-guidelines.md) follow-ups:

1. **ultralytics YOLO v8/v11-seg** — off-the-shelf, battle-tested, supports
   instance segmentation, but bundles its own dataset format, its own training
   loop, weights, and heavy dependencies (`torch`,
   base model weights downloads on first use).
2. **Raw PyTorch small U-Net** — the Phase 2 adapter
   (`ml/datasets/cardd_adapter.py`) already produces tensorized, split-scoped
   COCO instance segmentation samples that a U-Net consumes directly.

This decision is deliberately scoped: the smoke run is a machinery test, not a
model comparison. No accuracy claims are being made.

## Decision

Use **raw PyTorch** with a small U-Net (`ml/models/cardd_unet.py`) as the Phase 3
segmentation framework.

1. No `ultralytics`, `pycocotools`, or `albumentations` is installed or required.
   `pycocotools` would add a native C dependency for a feature the adapter
   already implements with `opencv`'s `fillPoly`.
2. The smoke training run (`ml/training/train_smoke.py`) trains the small U-Net
   for a bounded number of steps/epochs on a seeded sample, emits a run record
   (experiment ID, seed, device, loss trajectory, code version) and a checkpoint
   under `ml/experiments/`, and validates one inference pass.
3. This is the **first** framework decision, not a claim that raw PyTorch beats
   YOLO. If a later phase wants a strong IoU benchmark, ultralytics can be
   adopted then, as its own ADR, when the goal is a model comparison rather than
   machinery verification.

## Rationale

- **Smallest coherent change.** The adapter already feeds tensors into a
  `nn.Module`; the phase is a smoke test. Adding a training framework around a
  dataset we already parse directly is extra surface for no required benefit.
- **Dependency discipline.** CLAUDE.md §11.6 requires justifying every
  dependency. `ultralytics` is a large install (model weights, its own trainer)
  that the Phase 3 problem does not need.
- **Reproducibility / record discipline.** A raw PyTorch loop writes exactly the
  fields `docs/research/experiment-principles.md` requires. The loop is small
  and readable; a YOLO run's knobs are scattered across a framework.
- **VRAM.** A small U-Net trains comfortably in ~4 GB; a default YOLO-seg base
  model wants more headroom and would constrain everything to tiny-image runs.
- **Baseline honesty.** The research task compares vision-only and simple-fusion
  baselines *on the same splits and seeds*. Having the model, the fusion, and the
  loss inside one code base makes the comparison tautologically fair. YOLO cannot
  express the metadata fusion head at all, so the comparison would be skewed.

## Consequences

- Phase 3 runs raw-PyTorch only. Yes, a YOLO baseline may come later — but as a
  comparison *victim* run, not as the project's training driver.
- The small U-Net is a place-holder for the actual architecture that a later
  phase chooses; it is small enough to iterate on the 4 GB card.
- `ml/experiments/` holds run records and checkpoints and is git-ignored;
  committed documentation references experiment IDs rather than binaries.