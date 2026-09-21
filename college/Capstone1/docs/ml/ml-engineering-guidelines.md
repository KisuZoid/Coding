# ML Engineering Guidelines

## 1. Separation of training and inference

```
Dataset → Preprocessing → Training → Evaluation → Model artefact → Inference API
```

- Training code lives in `ml/training/`, inference code in `ml/inference/`.
- The API imports the inference layer only. It never imports training code, and
  never imports a training dependency at runtime.
- The boundary between them is the **model artefact plus its metadata**: version,
  training run ID, input contract, and output contract.

## 2. Configuration

Never hard-code:

- dataset paths;
- checkpoint paths;
- model versions;
- secrets;
- experiment hyperparameters.

Dataset and experiment settings come from versioned config files under
`ml/experiments/`. Deployment settings come from environment variables
(`MODEL_PATH`, `MODEL_VERSION`). A path written into a source file cannot be
reproduced on another machine and cannot be varied across an experiment sweep.

## 3. Data handling

- Large data never enters Git. `ml/datasets/` holds documentation — source,
  licence, schema, preprocessing, statistics — not the data itself.
- Record how to obtain and prepare each dataset so another person can rebuild it.
- Preprocessing is deterministic and versioned. If preprocessing changes, the
  dataset version changes.
- Deduplicate before splitting, and split by vehicle or incident, not by image.

## 4. Damage representation

Derived from segmentation masks, per damage region:

| Feature | Category | Note |
|---|---|---|
| Damage type | MODEL PREDICTION | Carries model confidence |
| Damage area ratio | DERIVED FEATURE | Damaged pixels ÷ total image pixels. Image-denominator, unitless (ADR 0005, ADR 0009) |
| Location in image | DERIVED FEATURE | Bbox / centroid in image coordinates. CarDD has no part masks, so location is image-relative only |
| Segmentation confidence | MODEL PREDICTION | Propagate downstream; do not discard |
| Geometry descriptors | DERIVED FEATURE | Shape statistics of the mask |

CarDD provides no part masks (ADR 0005, ADR 0009): never report a part-normalized
ratio or part-relative location. Do not convert the area ratio into cm². An
uncontrolled photograph carries no scale reference, and camera distance changes
apparent size. If physical area is ever required, it needs an explicit
calibration method, documented and validated.

## 5. Label integrity

Carry the label category through code, storage, and the interface:

| Category | Example in this project |
|---|---|
| REAL GROUND TRUTH | Human-annotated CarDD segmentation mask |
| WEAK LABEL | None currently; a free-text severity claim would be weak |
| SYNTHETIC LABEL | None currently; synthetic cost labels were removed (ADR 0011) |
| DERIVED FEATURE | Damage area ratio (image-denominator) |
| MODEL PREDICTION | Segmentation mask / per-class damage detection |
| ASSUMPTION | A chosen area-ratio threshold for the "small damage" slice |

No cost or repair field exists in the schema, dataset documentation, or UI; any
future label family must carry its category explicitly (ADR 0004).

## 6. Model artefacts

- Never commit checkpoints. Store them outside Git and reference them by version.
- Every artefact records: training run ID, dataset version, code commit, metric
  summary, and input/output contract.
- Checkpoints carry a `model_arch` key (`cardd_hybrid` / `cardd_unet`); the
  inference engine dispatches on it and a mismatch is a loud `ModelVersionError`
  (ADR 0010). Never guess the architecture of a checkpoint.
- Loading a model from an unverified source is a security risk; see `SECURITY.md`.

## 7. Evaluation

- Evaluation runs as an explicit experiment, never as part of the application
  test suite.
- GPU training never runs in CI.
- The metric implementation is shared between the baselines and the proposed
  model — one code path, so a metric bug affects all arms equally.
- Report the honest-segmentation headline metrics, not point error alone:
  mean IoU, Dice, and pixel accuracy per class, plus a small-damage slice
  (e.g. the train-p25 pixel criterion) where under-segmentation shows first —
  and always alongside the underfit-baseline context when presenting results.
- Confidence honesty is a first-class metric, not a footnote: report the
  low-confidence flag rate and the separation of confidence over agreed vs
  disagreed instances (RQ2) so "low confidence" claims remain falsifiable.
- Metrics must not leak through overlap: keep the argmax decode identical
  between loss and evaluation (ADR 0008) and note the overlap limitation on
  stacked CarDD masks rather than papering over it.
- Every reported evaluation records the reproducibility fields: experiment ID,
  dataset version, split policy, seed, commit hash, hyperparameters, and the
  run record (`registry.json`).

## 8. Inference in production

- Load the model once at startup, not per request.
- Validate input images at the boundary: type, size, dimensions.
- Return the confidence and the low-confidence flag alongside every prediction.
  A point estimate with no confidence signal misrepresents what the system knows
  (RQ2 is a research requirement).
- Fail loudly on a missing, version-mismatched, or arch-ambiguous artefact.
  Never fall back to a hard-coded prediction.

## 9. Reproducibility

- Seed every source of randomness and record the seed.
- Pin dependency versions for any run that appears in the report.
- Run experiments from a clean working tree so the commit hash means something.
